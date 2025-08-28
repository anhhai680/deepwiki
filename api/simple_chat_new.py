"""
Simple Chat API using the new chat pipeline.

This module provides the same interface as simple_chat.py but uses the new
chat pipeline architecture internally for better maintainability and testing.
"""

import logging
from typing import List, Optional
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api.config import get_model_config, configs, OPENROUTER_API_KEY, OPENAI_API_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from api.data_pipeline import count_tokens, get_file_content
from api.pipelines.chat import get_chat_compatibility

# Configure logging
from api.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(
    title="Simple Chat API",
    description="Simplified API for streaming chat completions using new pipeline architecture"
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
    """Stream a chat completion response using the new chat pipeline"""
    try:
        # Convert request to dictionary format for the pipeline
        request_data = {
            "repo_url": request.repo_url,
            "type": request.type,
            "token": request.token,
            "language": request.language,
            "provider": request.provider,
            "model": request.model,
            "filePath": request.filePath,
            "excluded_dirs": request.excluded_dirs,
            "excluded_files": request.excluded_files,
            "included_dirs": request.included_dirs,
            "included_files": request.included_files,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages]
        }
        
        # Get the chat compatibility layer
        chat_compatibility = get_chat_compatibility()
        
        # Create streaming response using the new pipeline
        async def response_stream():
            async for chunk in chat_compatibility.chat_completions_stream(request_data):
                yield chunk
        
        # Return streaming response
        return StreamingResponse(response_stream(), media_type="text/event-stream")

    except HTTPException:
        raise
    except Exception as e_handler:
        error_msg = f"Error in streaming chat completion: {str(e_handler)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/")
async def root():
    """Root endpoint to check if the API is running"""
    return {"status": "API is running", "message": "Navigate to /docs for API documentation"}

@app.get("/pipeline/status")
async def get_pipeline_status():
    """Get the status of the underlying chat pipeline"""
    try:
        chat_compatibility = get_chat_compatibility()
        return chat_compatibility.get_pipeline_status()
    except Exception as e:
        return {"error": str(e)}

@app.get("/pipeline/validate")
async def validate_pipeline():
    """Validate the underlying chat pipeline"""
    try:
        chat_compatibility = get_chat_compatibility()
        is_valid = chat_compatibility.validate_pipeline()
        return {"valid": is_valid}
    except Exception as e:
        return {"valid": False, "error": str(e)}
