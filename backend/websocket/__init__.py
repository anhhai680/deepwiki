"""
WebSocket handling package.

This package contains WebSocket connection management
and real-time communication components.
"""

from .wiki_handler import handle_websocket_chat, ChatMessage, ChatCompletionRequest

__all__ = [
    "handle_websocket_chat",
    "ChatMessage", 
    "ChatCompletionRequest"
]
