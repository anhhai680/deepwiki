"""
Chat pipeline steps for DeepWiki.

This module contains the individual steps that make up the chat pipeline,
each handling a specific aspect of the chat workflow.
"""

import logging
from typing import Any, Dict, List
from urllib.parse import unquote

from ..base.base_pipeline import PipelineStep, PipelineContext
from .chat_context import ChatPipelineContext
from api.data_pipeline import count_tokens
from api.config import get_model_config


class RequestValidationStep(PipelineStep[ChatPipelineContext, ChatPipelineContext]):
    """Step to validate and prepare the chat request."""
    
    def __init__(self):
        super().__init__("RequestValidation")
    
    def execute(self, context: ChatPipelineContext) -> ChatPipelineContext:
        """Validate the chat request and prepare context."""
        self.logger.info("Validating chat request")
        
        # Check if request contains very large input
        if context.messages and len(context.messages) > 0:
            last_message = context.messages[-1]
            if last_message.get('content'):
                tokens = count_tokens(last_message.get('content'), context.provider == "ollama")
                self.logger.info(f"Request size: {tokens} tokens")
                if tokens > 8000:
                    self.logger.warning(f"Request exceeds recommended token limit ({tokens} > 7500)")
                    context.input_too_large = True
        
        # Validate request structure
        if not context.messages or len(context.messages) == 0:
            context.add_error("No messages provided")
            return context
        
        last_message = context.messages[-1]
        if last_message.get('role') != "user":
            context.add_error("Last message must be from the user")
            return context
        
        # Process file filtering parameters
        if context.excluded_dirs:
            context.excluded_dirs = [unquote(dir_path) for dir_path in context.excluded_dirs.split('\n') if dir_path.strip()]
            self.logger.info(f"Using custom excluded directories: {context.excluded_dirs}")
        
        if context.excluded_files:
            context.excluded_files = [unquote(file_pattern) for file_pattern in context.excluded_files.split('\n') if file_pattern.strip()]
            self.logger.info(f"Using custom excluded files: {context.excluded_files}")
        
        if context.included_dirs:
            context.included_dirs = [unquote(dir_path) for dir_path in context.included_dirs.split('\n') if dir_path.strip()]
            self.logger.info(f"Using custom included directories: {context.included_dirs}")
        
        if context.included_files:
            context.included_files = [unquote(file_pattern) for file_pattern in context.included_files.split('\n') if file_pattern.strip()]
            self.logger.info(f"Using custom included files: {context.included_files}")
        
        # Get model configuration
        try:
            model_config = get_model_config(context.provider, context.model)
            context.model_config = model_config["model_kwargs"]
            self.logger.info(f"Model configuration loaded for {context.provider}")
        except Exception as e:
            context.add_error(f"Failed to load model configuration: {str(e)}")
            return context
        
        self.logger.info("Request validation completed successfully")
        return context


class ConversationAnalysisStep(PipelineStep[ChatPipelineContext, ChatPipelineContext]):
    """Step to analyze conversation and detect special features like Deep Research."""
    
    def __init__(self):
        super().__init__("ConversationAnalysis")
    
    def execute(self, context: ChatPipelineContext) -> ChatPipelineContext:
        """Analyze conversation for special features and prepare conversation history."""
        self.logger.info("Analyzing conversation")
        
        # Process previous messages to build conversation history
        for i in range(0, len(context.messages) - 1, 2):
            if i + 1 < len(context.messages):
                user_msg = context.messages[i]
                assistant_msg = context.messages[i + 1]
                
                if user_msg.get('role') == "user" and assistant_msg.get('role') == "assistant":
                    # Note: This would need to be integrated with the memory system
                    # For now, we'll build a simple conversation history string
                    context.conversation_history += f"<turn>\n<user>{user_msg.get('content', '')}</user>\n<assistant>{assistant_msg.get('content', '')}</assistant>\n</turn>\n"
        
        # Check if this is a Deep Research request
        for msg in context.messages:
            if msg.get('content') and "[DEEP RESEARCH]" in msg.get('content', ''):
                context.is_deep_research = True
                # Only remove the tag from the last message
                if msg == context.messages[-1]:
                    # Remove the Deep Research tag
                    msg['content'] = msg['content'].replace("[DEEP RESEARCH]", "").strip()
        
        # Count research iterations if this is a Deep Research request
        if context.is_deep_research:
            context.research_iteration = sum(1 for msg in context.messages if msg.get('role') == 'assistant') + 1
            self.logger.info(f"Deep Research request detected - iteration {context.research_iteration}")
            
            # Check if this is a continuation request
            last_message = context.messages[-1]
            if "continue" in last_message.get('content', '').lower() and "research" in last_message.get('content', '').lower():
                # Find the original topic from the first user message
                original_topic = None
                for msg in context.messages:
                    if msg.get('role') == "user" and "continue" not in msg.get('content', '').lower():
                        original_topic = msg.get('content', '').replace("[DEEP RESEARCH]", "").strip()
                        self.logger.info(f"Found original research topic: {original_topic}")
                        break
                
                if original_topic:
                    # Replace the continuation message with the original topic
                    last_message['content'] = original_topic
                    self.logger.info(f"Using original topic for research: {original_topic}")
        
        self.logger.info("Conversation analysis completed")
        return context


class SystemPromptGenerationStep(PipelineStep[ChatPipelineContext, ChatPipelineContext]):
    """Step to generate appropriate system prompts based on context."""
    
    def __init__(self):
        super().__init__("SystemPromptGeneration")
    
    def execute(self, context: ChatPipelineContext) -> ChatPipelineContext:
        """Generate system prompt based on conversation context."""
        self.logger.info("Generating system prompt")
        
        from api.prompts import (
            DEEP_RESEARCH_FIRST_ITERATION_PROMPT,
            DEEP_RESEARCH_FINAL_ITERATION_PROMPT,
            DEEP_RESEARCH_INTERMEDIATE_ITERATION_PROMPT,
            SIMPLE_CHAT_SYSTEM_PROMPT
        )
        
        # Get repository information
        repo_name = context.repo_url.split("/")[-1] if "/" in context.repo_url else context.repo_url
        
        # Get language information
        from api.config import configs
        supported_langs = configs["lang_config"]["supported_languages"]
        language_name = supported_langs.get(context.language, "English")
        
        # Create system prompt based on type
        if context.is_deep_research:
            # Check if this is the first iteration
            is_first_iteration = context.research_iteration == 1
            
            # Check if this is the final iteration
            is_final_iteration = context.research_iteration >= 5
            
            if is_first_iteration:
                context.system_prompt = DEEP_RESEARCH_FIRST_ITERATION_PROMPT.format(
                    repo_type=context.repo_type,
                    repo_url=context.repo_url,
                    repo_name=repo_name,
                    language_name=language_name
                )
            elif is_final_iteration:
                context.system_prompt = DEEP_RESEARCH_FINAL_ITERATION_PROMPT.format(
                    repo_type=context.repo_type,
                    repo_url=context.repo_url,
                    repo_name=repo_name,
                    research_iteration=context.research_iteration,
                    language_name=language_name
                )
            else:
                context.system_prompt = DEEP_RESEARCH_INTERMEDIATE_ITERATION_PROMPT.format(
                    repo_type=context.repo_type,
                    repo_url=context.repo_url,
                    repo_name=repo_name,
                    research_iteration=context.research_iteration,
                    language_name=language_name
                )
        else:
            context.system_prompt = SIMPLE_CHAT_SYSTEM_PROMPT.format(
                repo_type=context.repo_type,
                repo_url=context.repo_url,
                repo_name=repo_name,
                language_name=language_name
            )
        
        self.logger.info("System prompt generated successfully")
        return context


class ContextPreparationStep(PipelineStep[ChatPipelineContext, ChatPipelineContext]):
    """Step to prepare context from RAG and file content."""
    
    def __init__(self):
        super().__init__("ContextPreparation")
    
    def execute(self, context: ChatPipelineContext) -> ChatPipelineContext:
        """Prepare context from RAG retrieval and file content."""
        self.logger.info("Preparing context")
        
        # Only retrieve documents if input is not too large
        if not context.input_too_large:
            try:
                from api.rag import RAG
                
                # Create a new RAG instance for this request
                request_rag = RAG(provider=context.provider, model=context.model)
                
                # Prepare retriever
                request_rag.prepare_retriever(
                    context.repo_url, 
                    context.repo_type, 
                    context.token, 
                    context.excluded_dirs, 
                    context.excluded_files, 
                    context.included_dirs, 
                    context.included_files
                )
                
                # Get the query from the last message
                query = context.messages[-1].get('content', '')
                
                # If filePath exists, modify the query for RAG to focus on the file
                rag_query = query
                if context.file_path:
                    rag_query = f"Contexts related to {context.file_path}"
                    self.logger.info(f"Modified RAG query to focus on file: {context.file_path}")
                
                # Perform RAG retrieval
                retrieved_documents = request_rag(rag_query, language=context.language)
                
                if retrieved_documents and retrieved_documents[0].documents:
                    # Format context for the prompt in a structured way
                    documents = retrieved_documents[0].documents
                    self.logger.info(f"Retrieved {len(documents)} documents")
                    
                    # Group documents by file path
                    docs_by_file = {}
                    for doc in documents:
                        file_path = doc.meta_data.get('file_path', 'unknown')
                        if file_path not in docs_by_file:
                            docs_by_file[file_path] = []
                        docs_by_file[file_path].append(doc)
                    
                    # Format context text with file path grouping
                    context_parts = []
                    for file_path, docs in docs_by_file.items():
                        # Add file header with metadata
                        header = f"## File Path: {file_path}\n\n"
                        # Add document content
                        content = "\n\n".join([doc.text for doc in docs])
                        context_parts.append(f"{header}{content}")
                    
                    # Join all parts with clear separation
                    context.context_text = "\n\n" + "-" * 10 + "\n\n".join(context_parts)
                else:
                    self.logger.warning("No documents retrieved from RAG")
                    
            except Exception as e:
                context.add_warning(f"Error in RAG retrieval: {str(e)}")
                # Continue without RAG if there's an error
        
        # Fetch file content if provided
        if context.file_path:
            try:
                from api.data_pipeline import get_file_content
                context.file_content = get_file_content(
                    context.repo_url, 
                    context.file_path, 
                    context.repo_type, 
                    context.token
                )
                self.logger.info(f"Successfully retrieved content for file: {context.file_path}")
            except Exception as e:
                context.add_warning(f"Error retrieving file content: {str(e)}")
                # Continue without file content if there's an error
        
        self.logger.info("Context preparation completed")
        return context


class PromptAssemblyStep(PipelineStep[ChatPipelineContext, ChatPipelineContext]):
    """Step to assemble the final prompt for the AI model."""
    
    def __init__(self):
        super().__init__("PromptAssembly")
    
    def execute(self, context: ChatPipelineContext) -> ChatPipelineContext:
        """Assemble the final prompt for the AI model."""
        self.logger.info("Assembling final prompt")
        
        # Create the prompt with context
        prompt = f"/no_think {context.system_prompt}\n\n"
        
        if context.conversation_history:
            prompt += f"<conversation_history>\n{context.conversation_history}</conversation_history>\n\n"
        
        # Check if filePath is provided and fetch file content if it exists
        if context.file_content:
            # Add file content to the prompt after conversation history
            prompt += f"<currentFileContent path=\"{context.file_path}\">\n{context.file_content}\n</currentFileContent>\n\n"
        
        # Only include context if it's not empty
        CONTEXT_START = "<START_OF_CONTEXT>"
        CONTEXT_END = "<END_OF_CONTEXT>"
        if context.context_text.strip():
            prompt += f"{CONTEXT_START}\n{context.context_text}\n{CONTEXT_END}\n\n"
        else:
            # Add a note that we're skipping RAG due to size constraints
            self.logger.info("No context available from RAG")
            prompt += "<note>Answering without retrieval augmentation.</note>\n\n"
        
        # Get the query from the last message
        query = context.messages[-1].get('content', '')
        prompt += f"<query>\n{query}\n</query>\n\nAssistant: "
        
        # Add provider-specific prompt modifications
        if context.provider == "ollama":
            prompt += " /no_think"
        
        context.final_prompt = prompt
        self.logger.info("Final prompt assembled successfully")
        return context
