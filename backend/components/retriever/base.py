"""
Base retriever interface for all retriever implementations.

This module defines the common interface that all retriever components
must implement, ensuring consistent behavior across different retrieval methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List, Tuple
from dataclasses import dataclass
from enum import Enum

from adalflow.core.types import Document


class RetrievalMethod(Enum):
    """Enumeration of supported retrieval methods."""
    UNDEFINED = "undefined"
    VECTOR_SIMILARITY = "vector_similarity"
    KEYWORD_MATCH = "keyword_match"
    HYBRID = "hybrid"
    SEMANTIC = "semantic"


@dataclass
class RetrievalResult:
    """Standard output format for all retriever operations."""
    
    documents: List[Document]
    doc_indices: List[int]
    scores: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __bool__(self) -> bool:
        """Return True if the operation was successful (no error)."""
        return self.error is None
    
    def __str__(self) -> str:
        """String representation of the retrieval result."""
        if self.error:
            return f"RetrievalResult(error='{self.error}')"
        return f"RetrievalResult(documents={len(self.documents)}, scores={len(self.scores) if self.scores else 0})"


class BaseRetriever(ABC):
    """
    Abstract base class for all retriever implementations.
    
    This class defines the common interface that all retrieval methods
    must implement, ensuring consistent behavior and error handling.
    """
    
    def __init__(self, **kwargs):
        """Initialize the base retriever with common configuration."""
        self._method = kwargs.get("method", RetrievalMethod.VECTOR_SIMILARITY)
        self._top_k = kwargs.get("top_k", 20)
        self._score_threshold = kwargs.get("score_threshold", 0.0)
        self._max_retries = kwargs.get("max_retries", 3)
        self._documents: List[Document] = []
        self._embedder = kwargs.get("embedder")
        self._document_map_func = kwargs.get("document_map_func")
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Add documents to the retriever's document store.
        
        Args:
            documents: List of documents to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def remove_documents(self, document_ids: List[str]) -> bool:
        """
        Remove documents from the retriever's document store.
        
        Args:
            document_ids: List of document IDs to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def clear_documents(self) -> bool:
        """
        Clear all documents from the retriever's document store.
        
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def __call__(self, query: str, top_k: Optional[int] = None) -> RetrievalResult:
        """
        Retrieve relevant documents for a given query.
        
        Args:
            query: The search query
            top_k: Number of top results to return (overrides default)
            
        Returns:
            RetrievalResult: The retrieval results
        """
        pass
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the retriever."""
        return len(self._documents)
    
    def get_documents(self) -> List[Document]:
        """Get all documents in the retriever."""
        return self._documents.copy()
    
    def set_top_k(self, top_k: int) -> None:
        """Set the default number of top results to return."""
        if top_k > 0:
            self._top_k = top_k
    
    def set_score_threshold(self, threshold: float) -> None:
        """Set the minimum score threshold for results."""
        self._score_threshold = max(0.0, min(1.0, threshold))
    
    def validate_documents(self, documents: List[Document]) -> List[Document]:
        """
        Validate documents and filter out invalid ones.
        
        Args:
            documents: List of documents to validate
            
        Returns:
            List[Document]: Valid documents only
        """
        if not documents:
            return []
        
        valid_documents = []
        for doc in documents:
            if doc and hasattr(doc, 'vector') and doc.vector is not None:
                valid_documents.append(doc)
        
        return valid_documents
