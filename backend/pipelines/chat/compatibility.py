"""
Compatibility layer for the chat pipeline.

This module provides backward compatibility with the existing simple_chat.py
interface while using the new chat pipeline internally.
"""

import logging
from typing import AsyncGenerator, Dict, Any
from fastapi import HTTPException

from .chat_pipeline import ChatPipeline, create_chat_pipeline
from .chat_context import ChatPipelineContext

logger = logging.getLogger(__name__)


class ChatCompatibility:
    """Compatibility layer for the existing simple_chat.py interface."""
    
    def __init__(self):
        self.pipeline = create_chat_pipeline()
        self.logger = logging.getLogger(__name__)
    
    async def chat_completions_stream(self, request_data: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Stream a chat completion response using the new chat pipeline."""
        try:
            self.logger.info("Starting chat completion stream with new pipeline")
            
            # Create pipeline context from request
            context = self.pipeline.create_context_from_request(request_data)
            
            # Execute the streaming pipeline
            async for chunk in self.pipeline.execute_streaming(context):
                yield chunk
                
        except HTTPException:
            raise
        except Exception as e:
            error_msg = f"Error in streaming chat completion: {str(e)}"
            self.logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get the status of the underlying chat pipeline."""
        return self.pipeline.get_pipeline_status()
    
    def validate_pipeline(self) -> bool:
        """Validate the underlying chat pipeline."""
        return self.pipeline.validate_pipeline()


# Global compatibility instance
_chat_compatibility = None


def get_chat_compatibility() -> ChatCompatibility:
    """Get the global chat compatibility instance."""
    global _chat_compatibility
    if _chat_compatibility is None:
        _chat_compatibility = ChatCompatibility()
    return _chat_compatibility


def create_chat_completion_stream(request_data: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """Create a chat completion stream using the compatibility layer."""
    compatibility = get_chat_compatibility()
    return compatibility.chat_completions_stream(request_data)


# Convenience function for direct pipeline access
def create_chat_pipeline_instance() -> ChatPipeline:
    """Create a new chat pipeline instance for direct use."""
    return create_chat_pipeline()
