"""
Retriever manager for centralized retriever component management.

This module provides a centralized manager for all retriever components,
enabling easy switching between different retrieval methods and providers.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from enum import Enum

from .base import BaseRetriever, RetrievalMethod, RetrievalResult
from .faiss_retriever import FAISSRetriever
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class RetrieverType(Enum):
    """Enumeration of supported retriever types."""
    UNDEFINED = "undefined"
    FAISS = "faiss"
    VECTOR_STORE = "vector_store"
    HYBRID = "hybrid"


class RetrieverManager:
    """
    Centralized manager for all retriever components.
    
    This class provides a unified interface for managing different
    retriever types and switching between them as needed.
    """
    
    def __init__(self, **kwargs):
        """Initialize the retriever manager."""
        self._retrievers: Dict[str, BaseRetriever] = {}
        self._default_retriever: Optional[str] = None
        self._vector_store: Optional[VectorStore] = None
        
        # Initialize vector store if provided
        if "vector_store" in kwargs:
            self._vector_store = kwargs["vector_store"]
        
        # Initialize default retriever if specified
        default_type = kwargs.get("default_type", RetrieverType.UNDEFINED)
        if default_type != RetrieverType.UNDEFINED:
            self.set_default_retriever(default_type.value)
    
    def create_retriever(
        self,
        retriever_type: Union[str, RetrieverType],
        **kwargs
    ) -> Optional[BaseRetriever]:
        """
        Create a new retriever instance.
        
        Args:
            retriever_type: Type of retriever to create
            **kwargs: Additional arguments for the retriever
            
        Returns:
            BaseRetriever: The created retriever instance, or None if failed
        """
        try:
            if isinstance(retriever_type, RetrieverType):
                retriever_type = retriever_type.value
            
            retriever_type = retriever_type.lower()
            
            if retriever_type == RetrieverType.FAISS.value:
                retriever = FAISSRetriever(**kwargs)
            elif retriever_type == RetrieverType.VECTOR_STORE.value:
                if not self._vector_store:
                    # Create a vector store if none exists
                    self._vector_store = VectorStore(**kwargs)
                retriever = self._vector_store
            else:
                logger.error(f"Unsupported retriever type: {retriever_type}")
                return None
            
            # Store the retriever
            self._retrievers[retriever_type] = retriever
            
            # Set as default if this is the first one
            if not self._default_retriever:
                self._default_retriever = retriever_type
            
            logger.info(f"Successfully created {retriever_type} retriever")
            return retriever
            
        except Exception as e:
            logger.error(f"Error creating {retriever_type} retriever: {str(e)}")
            return None
    
    def get_retriever(self, retriever_type: Optional[str] = None) -> Optional[BaseRetriever]:
        """
        Get a retriever instance.
        
        Args:
            retriever_type: Type of retriever to get (None for default)
            
        Returns:
            BaseRetriever: The retriever instance, or None if not found
        """
        if retriever_type is None:
            retriever_type = self._default_retriever
        
        if not retriever_type:
            logger.error("No default retriever set")
            return None
        
        retriever = self._retrievers.get(retriever_type)
        if not retriever:
            logger.warning(f"Retriever type '{retriever_type}' not found, attempting to create")
            # Try to create the retriever
            retriever = self.create_retriever(retriever_type)
        
        return retriever
    
    def set_default_retriever(self, retriever_type: Union[str, RetrieverType]) -> bool:
        """
        Set the default retriever type.
        
        Args:
            retriever_type: Type of retriever to set as default
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if isinstance(retriever_type, RetrieverType):
                retriever_type = retriever_type.value
            
            retriever_type = retriever_type.lower()
            
            if retriever_type not in self._retrievers:
                logger.warning(f"Retriever type '{retriever_type}' not found, attempting to create")
                if not self.create_retriever(retriever_type):
                    return False
            
            self._default_retriever = retriever_type
            logger.info(f"Set default retriever to {retriever_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting default retriever: {str(e)}")
            return False
    
    def add_documents(
        self,
        documents: List[Any],
        retriever_type: Optional[str] = None
    ) -> bool:
        """
        Add documents to a retriever.
        
        Args:
            documents: List of documents to add
            retriever_type: Type of retriever to use (None for default)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            retriever = self.get_retriever(retriever_type)
            if not retriever:
                return False
            
            return retriever.add_documents(documents)
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return False
    
    def remove_documents(
        self,
        document_ids: List[str],
        retriever_type: Optional[str] = None
    ) -> bool:
        """
        Remove documents from a retriever.
        
        Args:
            document_ids: List of document IDs to remove
            retriever_type: Type of retriever to use (None for default)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            retriever = self.get_retriever(retriever_type)
            if not retriever:
                return False
            
            return retriever.remove_documents(document_ids)
            
        except Exception as e:
            logger.error(f"Error removing documents: {str(e)}")
            return False
    
    def clear_documents(self, retriever_type: Optional[str] = None) -> bool:
        """
        Clear all documents from a retriever.
        
        Args:
            retriever_type: Type of retriever to use (None for default)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            retriever = self.get_retriever(retriever_type)
            if not retriever:
                return False
            
            return retriever.clear_documents()
            
        except Exception as e:
            logger.error(f"Error clearing documents: {str(e)}")
            return False
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        retriever_type: Optional[str] = None
    ) -> RetrievalResult:
        """
        Perform retrieval using the specified retriever.
        
        Args:
            query: The search query
            top_k: Number of top results to return
            retriever_type: Type of retriever to use (None for default)
            
        Returns:
            RetrievalResult: The retrieval results
        """
        try:
            retriever = self.get_retriever(retriever_type)
            if not retriever:
                return RetrievalResult(
                    documents=[],
                    doc_indices=[],
                    error="No retriever available"
                )
            
            return retriever(query, top_k)
            
        except Exception as e:
            logger.error(f"Error during retrieval: {str(e)}")
            return RetrievalResult(
                documents=[],
                doc_indices=[],
                error=f"Retrieval failed: {str(e)}"
            )
    
    def get_available_retrievers(self) -> List[str]:
        """Get list of available retriever types."""
        return list(self._retrievers.keys())
    
    def get_retriever_info(self, retriever_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a retriever.
        
        Args:
            retriever_type: Type of retriever to get info for (None for default)
            
        Returns:
            Dict[str, Any]: Information about the retriever
        """
        try:
            retriever = self.get_retriever(retriever_type)
            if not retriever:
                return {"error": "Retriever not found"}
            
            info = {
                "type": retriever_type or self._default_retriever,
                "document_count": retriever.get_document_count(),
                "available_methods": [method.value for method in RetrievalMethod]
            }
            
            # Add retriever-specific information
            if hasattr(retriever, 'get_embedding_dimension'):
                info["embedding_dimension"] = retriever.get_embedding_dimension()
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting retriever info: {str(e)}")
            return {"error": str(e)}
    
    def validate_embeddings(
        self,
        documents: List[Any],
        retriever_type: Optional[str] = None
    ) -> List[Any]:
        """
        Validate embeddings using the specified retriever.
        
        Args:
            documents: List of documents to validate
            retriever_type: Type of retriever to use (None for default)
            
        Returns:
            List[Any]: Valid documents only
        """
        try:
            retriever = self.get_retriever(retriever_type)
            if not retriever:
                logger.error("No retriever available for validation")
                return []
            
            if hasattr(retriever, 'validate_embeddings'):
                return retriever.validate_embeddings(documents)
            else:
                # Fallback to base validation
                return retriever.validate_documents(documents)
                
        except Exception as e:
            logger.error(f"Error validating embeddings: {str(e)}")
            return []
    
    def get_vector_store(self) -> Optional[VectorStore]:
        """Get the vector store instance."""
        return self._vector_store
    
    def set_vector_store(self, vector_store: VectorStore) -> None:
        """Set the vector store instance."""
        self._vector_store = vector_store
        logger.info("Vector store updated")
    
    def __call__(
        self,
        query: str,
        top_k: Optional[int] = None,
        retriever_type: Optional[str] = None
    ) -> RetrievalResult:
        """
        Convenience method for retrieval.
        
        Args:
            query: The search query
            top_k: Number of top results to return
            retriever_type: Type of retriever to use (None for default)
            
        Returns:
            RetrievalResult: The retrieval results
        """
        return self.retrieve(query, top_k, retriever_type)
