"""
Base pipeline framework providing reusable infrastructure for all pipeline implementations.
"""

from .base_pipeline import BasePipeline, PipelineContext

__all__ = ["BasePipeline", "PipelineContext"]