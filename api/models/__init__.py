"""
Data models package.

This package contains Pydantic models for API requests,
responses, and internal data structures.
"""

# Import all models for easy access
from .wiki import (
    WikiPage,
    WikiSection,
    WikiStructureModel,
    WikiCacheData,
    WikiCacheRequest,
    WikiExportRequest
)

from .common import (
    ProcessedProjectEntry,
    RepoInfo
)

from .config import (
    Model,
    Provider,
    ModelConfig,
    AuthorizationConfig
)

from .chat import (
    ChatMessage,
    ChatCompletionRequest,
    ChatResponse
)

# Rebuild models to resolve forward references
# This is required for Pydantic v2 when using forward references
WikiCacheData.model_rebuild()
WikiCacheRequest.model_rebuild()

__all__ = [
    # Wiki models
    "WikiPage",
    "WikiSection", 
    "WikiStructureModel",
    "WikiCacheData",
    "WikiCacheRequest",
    "WikiExportRequest",
    
    # Common models
    "ProcessedProjectEntry",
    "RepoInfo",
    
    # Configuration models
    "Model",
    "Provider", 
    "ModelConfig",
    "AuthorizationConfig",
    
    # Chat models
    "ChatMessage",
    "ChatCompletionRequest",
    "ChatResponse"
]
