"""
Common type definitions for the DeepWiki API.

This module will contain type definitions extracted
from existing code during the restructure.
"""

from typing import Dict, List, Optional, Union, Any, TypedDict
from datetime import datetime


# Basic types that will be populated during restructure
class EmbeddingVector(List[float]):
    """Type alias for embedding vectors."""
    pass


class MetadataDict(Dict[str, Any]):
    """Type alias for metadata dictionaries."""
    pass


class ConversationId(str):
    """Type alias for conversation identifiers."""
    pass


class ProjectId(str):
    """Type alias for project identifiers."""
    pass


class UserId(str):
    """Type alias for user identifiers."""
    pass


# Structured types that will be populated during restructure
class DocumentChunk(TypedDict, total=False):
    """Document chunk structure."""
    content: str
    metadata: MetadataDict
    embedding: Optional[EmbeddingVector]
    chunk_id: str


class ConversationMessage(TypedDict, total=False):
    """Conversation message structure."""
    role: str
    content: str
    timestamp: datetime
    metadata: MetadataDict


class SearchResult(TypedDict, total=False):
    """Search result structure."""
    content: str
    score: float
    metadata: MetadataDict
    source: str


# Provider-specific types that will be populated during restructure
class ModelConfig(TypedDict, total=False):
    """Model configuration structure."""
    name: str
    provider: str
    parameters: Dict[str, Any]
    capabilities: List[str]


class ProviderResponse(TypedDict, total=False):
    """Provider response structure."""
    content: str
    model: str
    usage: Dict[str, Any]
    metadata: MetadataDict
