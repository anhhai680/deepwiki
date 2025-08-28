"""
Chat API endpoints.

This module contains all chat-related API endpoints extracted from the main api.py file.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional

# Import the actual chat implementations from the updated modules
from ...services.chat_service import ChatService
from ...models.chat import ChatCompletionRequest, ChatMessage
from ...websocket.wiki_handler import handle_websocket_chat

# Create router for chat endpoints
router = APIRouter()

# Re-export the models for consistency
ChatMessage = ChatMessage
ChatCompletionRequest = ChatCompletionRequest

@router.post("/chat/completions/stream")
async def chat_completions_stream_endpoint(request: ChatCompletionRequest):
    """Stream a chat completion response using the new chat service."""
    chat_service = ChatService()

    # Convert Pydantic models to plain dicts for the service layer
    messages = [
        {"role": m.role, "content": m.content} for m in request.messages
    ]

    stream = chat_service.process_chat_request(
        repo_url=request.repo_url,
        messages=messages,
        file_path=request.filePath,
        token=request.token,
        repo_type=request.type or "github",
        provider=request.provider or "google",
        model=request.model,
        language=request.language or "en",
        excluded_dirs=request.excluded_dirs,
        excluded_files=request.excluded_files,
        included_dirs=request.included_dirs,
        included_files=request.included_files,
    )

    return StreamingResponse(stream, media_type="text/plain; charset=utf-8")

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for chat using the existing websocket implementation."""
    await handle_websocket_chat(websocket)
