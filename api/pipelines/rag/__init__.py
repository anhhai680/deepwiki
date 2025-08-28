"""
RAG pipeline package.

This package contains the Retrieval Augmented Generation
workflow orchestration and processing pipelines.
"""

from .rag_pipeline import RAGPipeline
from .rag_context import RAGPipelineContext
from .compatibility import RAGCompatibility, create_rag
from .steps import (
    RepositoryPreparationStep,
    RetrieverInitializationStep,
    DocumentRetrievalStep,
    ResponseGenerationStep,
    MemoryUpdateStep
)

__all__ = [
    "RAGPipeline",
    "RAGPipelineContext",
    "RAGCompatibility",
    "create_rag",
    "RepositoryPreparationStep",
    "RetrieverInitializationStep",
    "DocumentRetrievalStep",
    "ResponseGenerationStep",
    "MemoryUpdateStep"
]
