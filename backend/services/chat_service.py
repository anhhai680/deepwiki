"""
Chat Service for DeepWiki.

This module provides a service layer for chat operations, extracting business logic
from simple_chat.py and providing a clean interface for chat orchestration and
state management.
"""

import logging
from typing import List, Optional, Dict, Any, AsyncGenerator
from urllib.parse import unquote

from fastapi import HTTPException

from backend.core.config.settings import get_model_config, configs
from backend.utils.token_utils import count_tokens
from backend.utils.file_utils import get_file_content
from backend.pipelines.chat import get_chat_compatibility
from backend.pipelines.chat.chat_context import ChatPipelineContext

logger = logging.getLogger(__name__)


class ChatService:
    """Service layer for chat operations and orchestration."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._chat_compatibility = get_chat_compatibility()
    
    async def process_chat_request(
        self,
        repo_url: str,
        messages: List[Dict[str, str]],
        file_path: Optional[str] = None,
        token: Optional[str] = None,
        repo_type: str = "github",
        provider: str = "google",
        model: Optional[str] = None,
        language: str = "en",
        excluded_dirs: Optional[str] = None,
        excluded_files: Optional[str] = None,
        included_dirs: Optional[str] = None,
        included_files: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Process a chat request and return a streaming response.
        
        This method orchestrates the complete chat workflow including:
        - Request validation and preprocessing
        - Deep Research detection and iteration tracking
        - Context preparation and RAG integration
        - Response generation with streaming
        """
        try:
            self.logger.info(f"Processing chat request for {repo_url}")
            
            # Validate and preprocess the request
            validated_data = self._validate_and_preprocess_request(
                repo_url=repo_url,
                messages=messages,
                file_path=file_path,
                token=token,
                repo_type=repo_type,
                provider=provider,
                model=model,
                language=language,
                excluded_dirs=excluded_dirs,
                excluded_files=excluded_files,
                included_dirs=included_dirs,
                included_files=included_files
            )
            
            # Create pipeline context
            context = self._create_pipeline_context(validated_data)
            
            # Execute the streaming pipeline
            async for chunk in self._chat_compatibility.chat_completions_stream(context):
                yield chunk
                
        except HTTPException:
            raise
        except Exception as e:
            error_msg = f"Error processing chat request: {str(e)}"
            self.logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
    
    def _validate_and_preprocess_request(
        self,
        repo_url: str,
        messages: List[Dict[str, str]],
        file_path: Optional[str] = None,
        token: Optional[str] = None,
        repo_type: str = "github",
        provider: str = "google",
        model: Optional[str] = None,
        language: str = "en",
        excluded_dirs: Optional[str] = None,
        excluded_files: Optional[str] = None,
        included_dirs: Optional[str] = None,
        included_files: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate and preprocess the chat request."""
        # Validate messages
        if not messages or len(messages) == 0:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        last_message = messages[-1]
        if last_message.get("role") != "user":
            raise HTTPException(status_code=400, detail="Last message must be from the user")
        
        # Check for large input
        input_too_large = False
        if messages and len(messages) > 0:
            last_message = messages[-1]
            if last_message.get("content"):
                tokens = count_tokens(last_message["content"], provider == "ollama")
                self.logger.info(f"Request size: {tokens} tokens")
                if tokens > 8000:
                    self.logger.warning(f"Request exceeds recommended token limit ({tokens} > 7500)")
                    input_too_large = True
        
        # Process file filtering parameters
        processed_excluded_dirs = None
        processed_excluded_files = None
        processed_included_dirs = None
        processed_included_files = None
        
        if excluded_dirs:
            processed_excluded_dirs = [unquote(dir_path) for dir_path in excluded_dirs.split('\n') if dir_path.strip()]
            self.logger.info(f"Using custom excluded directories: {processed_excluded_dirs}")
        if excluded_files:
            processed_excluded_files = [unquote(file_pattern) for file_pattern in excluded_files.split('\n') if file_pattern.strip()]
            self.logger.info(f"Using custom excluded files: {processed_excluded_files}")
        if included_dirs:
            processed_included_dirs = [unquote(dir_path) for dir_path in included_dirs.split('\n') if dir_path.strip()]
            self.logger.info(f"Using custom included directories: {processed_included_dirs}")
        if included_files:
            processed_included_files = [unquote(file_pattern) for file_pattern in included_files.split('\n') if file_pattern.strip()]
            self.logger.info(f"Using custom included files: {processed_included_files}")
        
        # Detect Deep Research requests
        is_deep_research, research_iteration, processed_messages = self._detect_deep_research(messages)
        
        # Get language information
        language_code = language or configs["lang_config"]["default"]
        supported_langs = configs["lang_config"]["supported_languages"]
        language_name = supported_langs.get(language_code, "English")
        
        # Get repository information
        repo_name = repo_url.split("/")[-1] if "/" in repo_url else repo_url
        
        return {
            "repo_url": repo_url,
            "repo_type": repo_type,
            "repo_name": repo_name,
            "token": token,
            "language": language,
            "language_name": language_name,
            "provider": provider,
            "model": model,
            "file_path": file_path,
            "excluded_dirs": processed_excluded_dirs,
            "excluded_files": processed_excluded_files,
            "included_dirs": processed_included_dirs,
            "included_files": processed_included_files,
            "messages": processed_messages,
            "is_deep_research": is_deep_research,
            "research_iteration": research_iteration,
            "input_too_large": input_too_large
        }
    
    def _detect_deep_research(self, messages: List[Dict[str, str]]) -> tuple[bool, int, List[Dict[str, str]]]:
        """Detect Deep Research requests and process messages accordingly."""
        is_deep_research = False
        research_iteration = 1
        processed_messages = messages.copy()
        
        # Process messages to detect Deep Research requests
        for msg in processed_messages:
            if msg.get("content") and "[DEEP RESEARCH]" in msg["content"]:
                is_deep_research = True
                # Only remove the tag from the last message
                if msg == processed_messages[-1]:
                    # Remove the Deep Research tag
                    msg["content"] = msg["content"].replace("[DEEP RESEARCH]", "").strip()
        
        # Count research iterations if this is a Deep Research request
        if is_deep_research:
            research_iteration = sum(1 for msg in processed_messages if msg.get("role") == "assistant") + 1
            self.logger.info(f"Deep Research request detected - iteration {research_iteration}")
            
            # Check if this is a continuation request
            last_message = processed_messages[-1]
            if "continue" in last_message.get("content", "").lower() and "research" in last_message.get("content", "").lower():
                # Find the original topic from the first user message
                original_topic = None
                for msg in processed_messages:
                    if msg.get("role") == "user" and "continue" not in msg.get("content", "").lower():
                        original_topic = msg["content"].replace("[DEEP RESEARCH]", "").strip()
                        self.logger.info(f"Found original research topic: {original_topic}")
                        break
                
                if original_topic:
                    # Replace the continuation message with the original topic
                    last_message["content"] = original_topic
                    self.logger.info(f"Using original topic for research: {original_topic}")
        
        return is_deep_research, research_iteration, processed_messages
    
    def _create_pipeline_context(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create pipeline context from validated data."""
        return {
            "repo_url": validated_data["repo_url"],
            "type": validated_data["repo_type"],
            "token": validated_data["token"],
            "language": validated_data["language"],
            "provider": validated_data["provider"],
            "model": validated_data["model"],
            "filePath": validated_data["file_path"],
            "excluded_dirs": validated_data["excluded_dirs"],
            "excluded_files": validated_data["excluded_files"],
            "included_dirs": validated_data["included_dirs"],
            "included_files": validated_data["included_files"],
            "messages": validated_data["messages"]
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of the chat service."""
        return {
            "service": "ChatService",
            "status": "active",
            "pipeline_status": self._chat_compatibility.get_pipeline_status(),
            "compatibility_layer": "active"
        }
    
    def validate_service(self) -> bool:
        """Validate the chat service and its dependencies."""
        return self._chat_compatibility.validate_pipeline()


# Global chat service instance
_chat_service = None


def get_chat_service() -> ChatService:
    """Get the global chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service


def create_chat_service() -> ChatService:
    """Create a new chat service instance."""
    return ChatService()
