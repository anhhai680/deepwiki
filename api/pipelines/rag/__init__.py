"""
RAG (Retrieval-Augmented Generation) pipeline implementation.

This module provides the RAG pipeline that orchestrates document retrieval,
memory management, and response generation for code repository Q&A.
"""

from .rag_pipeline import RAGPipeline

__all__ = ["RAGPipeline"]