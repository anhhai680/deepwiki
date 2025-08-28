"""
Simple Chat API using the Chat Service.

This module provides the same interface as simple_chat.py but uses the new
chat service architecture internally for better maintainability and testing.
"""

import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api.services import get_chat_service

# Configure logging
from api.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(
    title="Simple Chat API",
    description="Simplified API for streaming chat completions using chat service architecture"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Models for the API
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatCompletionRequest(BaseModel):
    """
    Model for requesting a chat completion.
    """
    repo_url: str = Field(..., description="URL of the repository to query")
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    filePath: Optional[str] = Field(None, description="Optional path to a file in the repository to include in the prompt")
    token: Optional[str] = Field(None, description="Personal access token for private repositories")
    type: Optional[str] = Field("github", description="Type of repository (e.g., 'github', 'gitlab', 'bitbucket')")

    # model parameters
    provider: str = Field("google", description="Model provider (google, openai, openrouter, ollama, bedrock, azure)")
    model: Optional[str] = Field(None, description="Model name for the specified provider")

    language: Optional[str] = Field("en", description="Language for content generation (e.g., 'en', 'ja', 'zh', 'es', 'kr', 'vi')")
    excluded_dirs: Optional[str] = Field(None, description="Comma-separated list of directories to exclude from processing")
    excluded_files: Optional[str] = Field(None, description="Comma-separated list of file patterns to exclude from processing")
    included_dirs: Optional[str] = Field(None, description="Comma-separated list of directories to include exclusively")
    included_files: Optional[str] = Field(None, description="Comma-separated list of file patterns to include exclusively")

@app.post("/chat/completions/stream")
async def chat_completions_stream(request: ChatCompletionRequest):
    """Stream a chat completion response using the chat service"""
    try:
        # Convert request to service format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Get the chat service
        chat_service = get_chat_service()
        
        # Create streaming response using the service
        async def response_stream():
            async for chunk in chat_service.process_chat_request(
                repo_url=request.repo_url,
                messages=messages,
                file_path=request.filePath,
                token=request.token,
                repo_type=request.type,
                provider=request.provider,
                model=request.model,
                language=request.language,
                excluded_dirs=request.excluded_dirs,
                excluded_files=request.excluded_files,
                included_dirs=request.included_dirs,
                included_files=request.included_files
            ):
                yield chunk
        
        # Return streaming response
        return StreamingResponse(response_stream(), media_type="text/event-stream")

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error in streaming chat completion: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/")
async def root():
    """Root endpoint to check if the API is running"""
    return {"status": "API is running", "message": "Navigate to /docs for API documentation"}

@app.get("/status")
async def status():
    """Get the status of the chat service"""
    try:
        chat_service = get_chat_service()
        return chat_service.get_service_status()
    except Exception as e:
        logger.error(f"Error getting service status: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        chat_service = get_chat_service()
        is_valid = chat_service.validate_service()
        return {
            "status": "healthy" if is_valid else "unhealthy",
            "service": "ChatService",
            "timestamp": "2025-08-27T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}
