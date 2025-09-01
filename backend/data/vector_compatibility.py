"""
Vector Operations Compatibility Layer

This module provides backward compatibility for existing code that uses
vector operations, allowing seamless migration to the new data layer
components while maintaining existing functionality.
"""

import logging
from typing import List, Dict, Any

from adalflow.core.types import Document

from .vector_store import VectorStore

from .vector_operations import VectorOperationsManager
from .faiss_integration import FAISSCompatibilityWrapper

logger = logging.getLogger(__name__)


def create_vector_operations_manager(**kwargs) -> VectorOperationsManager:
    """
    Create a vector operations manager with the specified configuration.
    
    This function provides a factory method for creating vector operations
    managers, maintaining compatibility with existing code patterns.
    
    Args:
        **kwargs: Configuration parameters for the vector operations manager
        
    Returns:
        VectorOperationsManager: Configured vector operations manager instance
    """
    try:
        manager = VectorOperationsManager(**kwargs)
        logger.info("Vector operations manager created successfully")
        return manager
    except Exception as e:
        logger.error(f"Error creating vector operations manager: {str(e)}")
        raise


def create_faiss_compatibility_wrapper(embedder, documents: List[Document] = None, 
                                     **kwargs) -> FAISSCompatibilityWrapper:
    """
    Create a FAISS compatibility wrapper for existing code.
    
    This function provides backward compatibility for code that expects
    the original FAISS retriever interface.
    
    Args:
        embedder: Embedder instance for query processing
        documents: Optional initial list of documents
        **kwargs: Additional configuration parameters
        
    Returns:
        FAISSCompatibilityWrapper: Compatibility wrapper instance
    """
    try:
        # Create vector operations manager
        manager = VectorOperationsManager(
            embedder=embedder,
            **kwargs
        )
        
        # Add documents if provided
        if documents:
            manager.add_documents(documents)
        
        # Create compatibility wrapper
        wrapper = manager.create_faiss_compatibility_wrapper()
        if wrapper:
            logger.info("FAISS compatibility wrapper created successfully")
            return wrapper
        else:
            raise RuntimeError("Failed to create FAISS compatibility wrapper")
            
    except Exception as e:
        logger.error(f"Error creating FAISS compatibility wrapper: {str(e)}")
        raise


def validate_embeddings(documents: List[Document]) -> List[Document]:
    """
    Validate embeddings using the vector operations system.
    
    This function provides a standalone interface for embedding validation,
    maintaining compatibility with existing code.
    
    Args:
        documents: List of documents with embeddings
        
    Returns:
        List[Document]: Documents with valid embeddings
    """
    try:
        # Create a temporary vector store for validation
        from .vector_store import VectorStore
        
        vector_store = VectorStore()
        return vector_store.validate_embeddings(documents)
        
    except Exception as e:
        logger.error(f"Error validating embeddings: {str(e)}")
        return []


def create_vector_store_from_documents(documents: List[Document], 
                                    is_ollama_embedder: bool = False,
                                    db_manager=None) -> VectorStore:
    """
    Create a vector store from a list of documents.
    
    This function provides backward compatibility for existing code
    that creates vector stores directly.
    
    Args:
        documents: List of documents to add to the vector store
        is_ollama_embedder: Whether using Ollama embedder
        db_manager: Optional database manager
        
    Returns:
        VectorStore: Configured vector store instance
    """
    try:
        from .vector_store import VectorStore
        
        vector_store = VectorStore(
            documents=documents,
            is_ollama_embedder=is_ollama_embedder,
            db_manager=db_manager
        )
        
        logger.info(f"Vector store created with {len(documents)} documents")
        return vector_store
        
    except Exception as e:
        logger.error(f"Error creating vector store: {str(e)}")
        raise


def create_faiss_retriever_from_config(config: Dict[str, Any], embedder, 
                                     documents: List[Document], 
                                     document_map_func=None) -> FAISSCompatibilityWrapper:
    """
    Create a FAISS retriever from configuration, maintaining backward compatibility.
    
    This function provides the same interface as the existing compatibility
    functions while using the new vector operations system.
    
    Args:
        config: Configuration dictionary (e.g., configs["retriever"])
        embedder: Embedder instance to use
        documents: List of documents to index
        document_map_func: Function to extract vectors from documents
        
    Returns:
        FAISSCompatibilityWrapper: Configured FAISS retriever compatibility wrapper
    """
    try:
        # Extract configuration parameters
        top_k = config.get("top_k", 20)
        faiss_config = {k: v for k, v in config.items() if k != "top_k"}
        
        # Create vector operations manager
        manager = VectorOperationsManager(
            embedder=embedder,
            top_k=top_k,
            faiss_config=faiss_config
        )
        
        # Add documents
        if documents:
            manager.add_documents(documents)
        
        # Create compatibility wrapper
        wrapper = manager.create_faiss_compatibility_wrapper()
        if wrapper:
            logger.info(f"Created FAISS retriever with top_k={top_k}")
            return wrapper
        else:
            raise RuntimeError("Failed to create FAISS compatibility wrapper")
        
    except Exception as e:
        logger.error(f"Error creating FAISS retriever: {str(e)}")
        raise


# Legacy function names for backward compatibility
def create_faiss_retriever(*args, **kwargs):
    """Legacy function name for backward compatibility."""
    return create_faiss_retriever_from_config(*args, **kwargs)


def create_vector_store(*args, **kwargs):
    """Legacy function name for backward compatibility."""
    return create_vector_store_from_documents(*args, **kwargs)


# Export all compatibility functions
__all__ = [
    'create_vector_operations_manager',
    'create_faiss_compatibility_wrapper',
    'validate_embeddings',
    'create_vector_store_from_documents',
    'create_faiss_retriever_from_config',
    'create_faiss_retriever',  # Legacy alias
    'create_vector_store',      # Legacy alias
]
