"""
Base pipeline framework package.

This package contains the foundational pipeline components
including base classes and interfaces.
"""

from .base_pipeline import (
    BasePipeline,
    PipelineStep,
    PipelineContext,
    SequentialPipeline,
    ParallelPipeline,
    InputType,
    OutputType,
    ContextType
)

__all__ = [
    "BasePipeline",
    "PipelineStep", 
    "PipelineContext",
    "SequentialPipeline",
    "ParallelPipeline",
    "InputType",
    "OutputType",
    "ContextType"
]
