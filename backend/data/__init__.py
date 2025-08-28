"""
Data management package.

This package contains data access, storage, and
management components including vector stores.
"""

from .database import DatabaseManager
from .vector_store import VectorStore
from .faiss_integration import FAISSIntegration, FAISSCompatibilityWrapper
from .vector_operations import VectorOperationsManager
from .vector_compatibility import (
    create_vector_operations_manager,
    create_faiss_compatibility_wrapper,
    validate_embeddings,
    create_vector_store_from_documents,
    create_faiss_retriever_from_config,
    create_faiss_retriever,
    create_vector_store
)

__all__ = [
    'DatabaseManager',
    'VectorStore',
    'FAISSIntegration',
    'FAISSCompatibilityWrapper',
    'VectorOperationsManager',
    # Compatibility functions
    'create_vector_operations_manager',
    'create_faiss_compatibility_wrapper',
    'validate_embeddings',
    'create_vector_store_from_documents',
    'create_faiss_retriever_from_config',
    'create_faiss_retriever',
    'create_vector_store',
]
