"""
Chat API endpoints.

This module contains all chat-related API endpoints extracted from the main api.py file.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional

# Import the actual chat implementations from the existing modules
from ..simple_chat import chat_completions_stream, ChatCompletionRequest, ChatMessage
from ..websocket import handle_websocket_chat

# Create router for chat endpoints
router = APIRouter()

# Re-export the models for consistency
ChatMessage = ChatMessage
ChatCompletionRequest = ChatCompletionRequest

@router.post("/chat/completions/stream")
async def chat_completions_stream_endpoint(request: ChatCompletionRequest):
    """Stream a chat completion response using the existing chat implementation."""
    return await chat_completions_stream(request)

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for chat using the existing websocket implementation."""
    await handle_websocket_chat(websocket)
