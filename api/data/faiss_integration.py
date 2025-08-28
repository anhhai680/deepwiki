"""
FAISS Integration Component for Data Layer

This module provides FAISS integration for the vector store, maintaining the existing
FAISS functionality while providing a clean interface for vector similarity search.

The component handles FAISS index creation, management, and search operations,
ensuring compatibility with the existing retrieval system.
"""

import logging
import time
from typing import List, Optional, Dict, Any, Union, Tuple, Callable
import numpy as np

from adalflow.core.types import Document
from adalflow.components.retriever.faiss_retriever import FAISSRetriever as AdalflowFAISSRetriever

from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class FAISSIntegration:
    """
    FAISS integration component for vector similarity search.
    
    This component provides FAISS functionality while maintaining compatibility
    with the existing retrieval system and integrating with the new vector store.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the FAISS integration component.
        
        Args:
            vector_store: VectorStore instance to integrate with
            top_k: Number of top results to return (default: 20)
            embedder: Embedder instance for query processing
            document_map_func: Function to extract vectors from documents
            faiss_config: Additional FAISS configuration parameters
        """
        self._vector_store = kwargs.get("vector_store")
        self._top_k = kwargs.get("top_k", 20)
        self._embedder = kwargs.get("embedder")
        self._document_map_func = kwargs.get("document_map_func", lambda doc: doc.vector)
        self._faiss_config = kwargs.get("faiss_config", {})
        
        # Initialize the underlying FAISS retriever
        self._faiss_retriever: Optional[AdalflowFAISSRetriever] = None
        self._is_initialized = False
        
        # Initialize if vector store is provided
        if self._vector_store:
            self._initialize_faiss()
    
    def _initialize_faiss(self) -> None:
        """Initialize the FAISS retriever with the vector store documents."""
        try:
            if not self._vector_store:
                logger.warning("No vector store available for FAISS initialization")
                return
            
            documents = self._vector_store.get_documents()
            if not documents:
                logger.info("No documents available for FAISS initialization")
                return
            
            # Create FAISS retriever
            self._faiss_retriever = AdalflowFAISSRetriever(
                top_k=self._top_k,
                embedder=self._embedder,
                documents=documents,
                document_map_func=self._document_map_func,
                **self._faiss_config
            )
            
            self._is_initialized = True
            logger.info(f"FAISS retriever initialized with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error initializing FAISS retriever: {str(e)}")
            self._faiss_retriever = None
            self._is_initialized = False
    
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Add documents to the FAISS integration.
        
        Args:
            documents: List of documents to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._vector_store:
                logger.error("No vector store available")
                return False
            
            # Add documents to vector store first
            success = self._vector_store.add_documents(documents)
            if not success:
                return False
            
            # Reinitialize FAISS with updated documents
            self._initialize_faiss()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to FAISS integration: {str(e)}")
            return False
    
    def remove_documents(self, document_ids: List[str]) -> bool:
        """
        Remove documents from the FAISS integration.
        
        Args:
            document_ids: List of document IDs to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._vector_store:
                logger.error("No vector store available")
                return False
            
            # Remove documents from vector store first
            success = self._vector_store.remove_documents(document_ids)
            if not success:
                return False
            
            # Reinitialize FAISS with updated documents
            self._initialize_faiss()
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing documents from FAISS integration: {str(e)}")
            return False
    
    def clear_documents(self) -> bool:
        """
        Clear all documents from the FAISS integration.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._vector_store:
                logger.error("No vector store available")
                return False
            
            # Clear documents from vector store first
            success = self._vector_store.clear_documents()
            if not success:
                return False
            
            # Reset FAISS retriever
            self._faiss_retriever = None
            self._is_initialized = False
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing documents from FAISS integration: {str(e)}")
            return False
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Document]:
        """
        Search for similar documents using FAISS.
        
        Args:
            query: Query string to search for
            top_k: Number of top results to return (overrides default)
            
        Returns:
            List[Document]: List of similar documents
        """
        try:
            if not self._is_initialized or not self._faiss_retriever:
                logger.error("FAISS retriever not initialized")
                return []
            
            # Use provided top_k or default
            search_top_k = top_k if top_k is not None else self._top_k
            
            # Perform search using FAISS retriever
            results = self._faiss_retriever.retrieve(query, top_k=search_top_k)
            
            # Extract documents from results
            documents = []
            for result in results:
                if hasattr(result, 'document') and result.document:
                    documents.append(result.document)
                elif hasattr(result, 'content') and result.content:
                    # Handle different result formats
                    documents.append(result.content)
            
            logger.info(f"FAISS search returned {len(documents)} results for query: {query[:50]}...")
            return documents
            
        except Exception as e:
            logger.error(f"Error performing FAISS search: {str(e)}")
            return []
    
    def search_by_vector(self, query_vector: Union[List[float], np.ndarray], 
                        top_k: Optional[int] = None) -> List[Document]:
        """
        Search for similar documents using a query vector.
        
        Args:
            query_vector: Query vector to search for
            top_k: Number of top results to return (overrides default)
            
        Returns:
            List[Document]: List of similar documents
        """
        try:
            if not self._is_initialized or not self._faiss_retriever:
                logger.error("FAISS retriever not initialized")
                return []
            
            # Use provided top_k or default
            search_top_k = top_k if top_k is not None else self._top_k
            
            # Convert query vector to appropriate format
            if isinstance(query_vector, list):
                query_vector = np.array(query_vector)
            
            # Perform vector search using FAISS
            # Note: This would need to be implemented based on the specific FAISS retriever interface
            logger.info(f"Vector search requested for {len(query_vector)}-dimensional vector")
            
            # For now, return empty list as this would need specific FAISS implementation
            # This method can be extended based on the actual FAISS retriever capabilities
            return []
            
        except Exception as e:
            logger.error(f"Error performing vector search: {str(e)}")
            return []
    
    def get_similarity_scores(self, query: str, documents: List[Document]) -> List[float]:
        """
        Get similarity scores between a query and a list of documents.
        
        Args:
            query: Query string
            documents: List of documents to compare against
            
        Returns:
            List[float]: List of similarity scores
        """
        try:
            if not self._is_initialized or not self._faiss_retriever:
                logger.error("FAISS retriever not initialized")
                return []
            
            # This would need to be implemented based on the specific FAISS retriever interface
            # For now, return placeholder scores
            logger.info(f"Similarity score calculation requested for {len(documents)} documents")
            
            # Placeholder implementation
            scores = [0.0] * len(documents)
            return scores
            
        except Exception as e:
            logger.error(f"Error calculating similarity scores: {str(e)}")
            return []
    
    def update_faiss_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Update FAISS configuration parameters.
        
        Args:
            new_config: New configuration parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update configuration
            self._faiss_config.update(new_config)
            
            # Reinitialize FAISS with new configuration
            if self._vector_store and self._vector_store.get_document_count() > 0:
                self._initialize_faiss()
            
            logger.info("FAISS configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating FAISS configuration: {str(e)}")
            return False
    
    def get_faiss_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the FAISS integration.
        
        Returns:
            Dict[str, Any]: Dictionary containing FAISS statistics
        """
        stats = {
            "is_initialized": self._is_initialized,
            "top_k": self._top_k,
            "has_embedder": self._embedder is not None,
            "faiss_config": self._faiss_config.copy(),
            "vector_store_available": self._vector_store is not None
        }
        
        if self._vector_store:
            vector_stats = self._vector_store.get_embedding_statistics()
            stats.update({
                "vector_store_stats": vector_stats,
                "total_documents": vector_stats.get("total_documents", 0),
                "embedding_dimension": vector_stats.get("embedding_dimension")
            })
        
        return stats
    
    def validate_embeddings(self, documents: List[Document]) -> List[Document]:
        """
        Validate embeddings using the vector store validation.
        
        Args:
            documents: List of documents to validate
            
        Returns:
            List[Document]: Documents with valid embeddings
        """
        if not self._vector_store:
            logger.error("No vector store available for validation")
            return []
        
        return self._vector_store.validate_embeddings(documents)
    
    def is_ready(self) -> bool:
        """
        Check if the FAISS integration is ready for use.
        
        Returns:
            bool: True if ready, False otherwise
        """
        return (self._is_initialized and 
                self._faiss_retriever is not None and 
                self._vector_store is not None and
                self._vector_store.get_document_count() > 0)
    
    def get_underlying_retriever(self) -> Optional[AdalflowFAISSRetriever]:
        """
        Get the underlying FAISS retriever for advanced operations.
        
        Returns:
            AdalflowFAISSRetriever: The underlying FAISS retriever or None
        """
        return self._faiss_retriever
    
    def create_compatibility_wrapper(self) -> 'FAISSCompatibilityWrapper':
        """
        Create a compatibility wrapper for existing code.
        
        Returns:
            FAISSCompatibilityWrapper: Compatibility wrapper instance
        """
        return FAISSCompatibilityWrapper(self)


class FAISSCompatibilityWrapper:
    """
    Compatibility wrapper for existing FAISS retriever usage.
    
    This wrapper provides the same interface as the original FAISS retriever
    while using the new FAISS integration component.
    """
    
    def __init__(self, faiss_integration: FAISSIntegration):
        """
        Initialize the compatibility wrapper.
        
        Args:
            faiss_integration: FAISS integration component to wrap
        """
        self._faiss_integration = faiss_integration
        self._underlying_retriever = faiss_integration.get_underlying_retriever()
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to the retriever."""
        return self._faiss_integration.add_documents(documents)
    
    def remove_documents(self, document_ids: List[str]) -> bool:
        """Remove documents from the retriever."""
        return self._faiss_integration.remove_documents(document_ids)
    
    def clear_documents(self) -> bool:
        """Clear all documents from the retriever."""
        return self._faiss_integration.clear_documents()
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Any]:
        """Retrieve documents for a query."""
        documents = self._faiss_integration.search(query, top_k)
        
        # Convert to expected format (this may need adjustment based on actual usage)
        results = []
        for doc in documents:
            # Create a result object that matches expected interface
            result = type('RetrievalResult', (), {
                'document': doc,
                'content': doc,
                'score': 1.0,  # Placeholder score
                'metadata': getattr(doc, 'meta_data', {})
            })()
            results.append(result)
        
        return results
    
    def validate_documents(self, documents: List[Document]) -> List[Document]:
        """Validate documents using the integration."""
        return self._faiss_integration.validate_embeddings(documents)
    
    def is_ready(self) -> bool:
        """Check if the retriever is ready."""
        return self._faiss_integration.is_ready()
