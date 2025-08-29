"""
Compatibility layer for existing rag.py usage.

This module provides backward compatibility for the existing rag.py file,
allowing it to use the new retriever components without breaking changes.
"""

import logging
from typing import List, Dict, Any

from .faiss_retriever import FAISSRetriever
from .vector_store import VectorStore
from ..memory.conversation_memory import ConversationMemory

logger = logging.getLogger(__name__)


def create_faiss_retriever_from_config(
    config: Dict[str, Any],
    embedder,
    documents: List[Any],
    document_map_func=None
) -> FAISSRetriever:
    """
    Create a FAISS retriever from configuration, maintaining backward compatibility.
    
    Args:
        config: Configuration dictionary (e.g., configs["retriever"])
        embedder: Embedder instance to use
        documents: List of documents to index
        document_map_func: Function to extract vectors from documents
        
    Returns:
        FAISSRetriever: Configured FAISS retriever instance
    """
    try:
        # Extract configuration parameters
        top_k = config.get("top_k", 20)
        
        # Create retriever with extracted configuration
        retriever = FAISSRetriever(
            top_k=top_k,
            embedder=embedder,
            documents=documents,
            document_map_func=document_map_func or (lambda doc: doc.vector),
            allow_mock_embedder=True
        )
        
        logger.info(f"Created FAISS retriever with top_k={top_k}")
        return retriever
        
    except Exception as e:
        logger.error(f"Error creating FAISS retriever: {str(e)}")
        raise


def create_vector_store_from_documents(
    documents: List[Any],
    is_ollama_embedder: bool = False,
    db_manager=None
) -> VectorStore:
    """
    Create a vector store from documents, maintaining backward compatibility.
    
    Args:
        documents: List of documents to store
        is_ollama_embedder: Whether using Ollama embedder
        db_manager: Database manager instance
        
    Returns:
        VectorStore: Configured vector store instance
    """
    try:
        # Create vector store with extracted configuration
        vector_store = VectorStore(
            documents=documents,
            is_ollama_embedder=is_ollama_embedder,
            db_manager=db_manager
        )
        
        logger.info(f"Created vector store with {len(documents)} documents")
        return vector_store
        
    except Exception as e:
        logger.error(f"Error creating vector store: {str(e)}")
        raise


def create_memory_component() -> ConversationMemory:
    """
    Create a memory component, maintaining backward compatibility.
    
    Returns:
        ConversationMemory: Configured memory component instance
    """
    try:
        # Create memory component with default configuration
        memory = ConversationMemory()
        
        logger.info("Created conversation memory component")
        return memory
        
    except Exception as e:
        logger.error(f"Error creating memory component: {str(e)}")
        raise


def validate_and_filter_embeddings(documents: List[Any]) -> List[Any]:
    """
    Validate embeddings and filter out documents with invalid or mismatched sizes.
    This function maintains backward compatibility with the existing rag.py logic.
    
    Args:
        documents: List of documents with embeddings
        
    Returns:
        List[Any]: Documents with valid embeddings of consistent size
    """
    try:
        # Create a temporary vector store to use its validation logic
        vector_store = VectorStore()
        return vector_store.validate_embeddings(documents)
        
    except Exception as e:
        logger.error(f"Error validating embeddings: {str(e)}")
        # Fallback to basic validation
        valid_documents = []
        for doc in documents:
            if doc and hasattr(doc, 'vector') and doc.vector is not None:
                valid_documents.append(doc)
        return valid_documents


# Legacy function names for backward compatibility
def get_faiss_retriever(config, embedder, documents, document_map_func=None):
    """Legacy function name for backward compatibility."""
    return create_faiss_retriever_from_config(config, embedder, documents, document_map_func)


def get_vector_store(documents, is_ollama_embedder=False, db_manager=None):
    """Legacy function name for backward compatibility."""
    return create_vector_store_from_documents(documents, is_ollama_embedder, db_manager)


def get_memory():
    """Legacy function name for backward compatibility."""
    return create_memory_component()
