"""
Embedding components package.

This package contains components responsible for creating and managing
text embeddings for vector search and retrieval.
"""

from .base import BaseEmbedder, EmbeddingModelType, EmbedderOutput
from .embedder_manager import EmbedderManager, EmbeddingProviderType
from .ollama_utils import check_ollama_model_exists, OllamaDocumentProcessor

__all__ = [
    "BaseEmbedder",
    "EmbeddingModelType", 
    "EmbedderOutput",
    "EmbedderManager",
    "EmbeddingProviderType"
]
