"""
Pipeline framework package.

This package contains the pipeline architecture and implementations
for orchestrating complex workflows in the DeepWiki system.
"""

from .base import (
    BasePipeline,
    PipelineStep,
    PipelineContext,
    SequentialPipeline,
    ParallelPipeline,
    InputType,
    OutputType,
    ContextType
)

from .rag import (
    RAGPipeline,
    RAGPipelineContext,
    RAGCompatibility,
    create_rag
)

__all__ = [
    # Base pipeline framework
    "BasePipeline",
    "PipelineStep",
    "PipelineContext",
    "SequentialPipeline",
    "ParallelPipeline",
    "InputType",
    "OutputType",
    "ContextType",
    
    # RAG pipeline
    "RAGPipeline",
    "RAGPipelineContext",
    "RAGCompatibility",
    "create_rag"
]
