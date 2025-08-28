"""
Chat-related data models.

This module contains Pydantic models for chat functionality
extracted from the websocket handler during restructure.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ChatMessage(BaseModel):
    """Model for a chat message."""
    role: str = Field(..., description="Role of the message sender ('user' or 'assistant')")
    content: str = Field(..., description="Content of the message")


class ChatCompletionRequest(BaseModel):
    """Model for requesting a chat completion."""
    repo_url: str = Field(..., description="URL of the repository to query")
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    filePath: Optional[str] = Field(None, description="Optional path to a file in the repository to include in the prompt")
    token: Optional[str] = Field(None, description="Personal access token for private repositories")
    type: Optional[str] = Field("github", description="Type of repository (e.g., 'github', 'gitlab', 'bitbucket')")

    # Model parameters
    provider: str = Field("google", description="Model provider (google, openai, openrouter, ollama, azure)")
    model: Optional[str] = Field(None, description="Model name for the specified provider")

    # Language and filtering
    language: Optional[str] = Field("en", description="Language for content generation (e.g., 'en', 'ja', 'zh', 'es', 'kr', 'vi')")
    excluded_dirs: Optional[str] = Field(None, description="Comma-separated list of directories to exclude from processing")
    excluded_files: Optional[str] = Field(None, description="Comma-separated list of file patterns to exclude from processing")
    included_dirs: Optional[str] = Field(None, description="Comma-separated list of directories to include exclusively")
    included_files: Optional[str] = Field(None, description="Comma-separated list of file patterns to include exclusively")


class ChatResponse(BaseModel):
    """Model for chat response."""
    content: str = Field(..., description="Generated response content")
    provider: str = Field(..., description="Provider used for generation")
    model: str = Field(..., description="Model used for generation")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used in generation")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")
