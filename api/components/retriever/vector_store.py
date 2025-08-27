"""
Vector store component for managing document vectors and embeddings.

This module provides a vector store component that handles vector database
operations and document management for retrieval systems.
"""

import logging
from typing import List, Optional, Dict, Any, Union
import numpy as np

from adalflow.core.types import Document
from adalflow.core.db import LocalDB

from .base import BaseRetriever

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector store for managing document vectors and embeddings.
    
    This component handles the storage and retrieval of document vectors,
    providing a unified interface for vector database operations.
    """
    
    def __init__(self, **kwargs):
        """Initialize the vector store."""
        self._db_manager = kwargs.get("db_manager")
        self._documents: List[Document] = []
        self._embedding_dimension: Optional[int] = None
        self._is_ollama_embedder = kwargs.get("is_ollama_embedder", False)
        
        # Initialize if documents are provided
        if "documents" in kwargs:
            self.add_documents(kwargs["documents"])
    
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not documents:
                return True
            
            # Validate documents
            valid_documents = self._validate_documents(documents)
            if not valid_documents:
                logger.warning("No valid documents provided to vector store")
                return False
            
            # Check embedding dimension consistency
            if not self._check_embedding_dimension(valid_documents):
                logger.error("Documents have inconsistent embedding dimensions")
                return False
            
            # Add documents
            self._documents.extend(valid_documents)
            
            logger.info(f"Successfully added {len(valid_documents)} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            return False
    
    def remove_documents(self, document_ids: List[str]) -> bool:
        """
        Remove documents from the vector store.
        
        Args:
            document_ids: List of document IDs to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._documents:
                return True
            
            # Filter out documents to remove
            remaining_docs = [doc for doc in self._documents if doc.id not in document_ids]
            
            if len(remaining_docs) != len(self._documents):
                self._documents = remaining_docs
                logger.info(f"Removed {len(document_ids)} documents from vector store")
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing documents from vector store: {str(e)}")
            return False
    
    def clear_documents(self) -> bool:
        """
        Clear all documents from the vector store.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._documents = []
            self._embedding_dimension = None
            logger.info("Cleared all documents from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing documents from vector store: {str(e)}")
            return False
    
    def get_documents(self) -> List[Document]:
        """Get all documents in the vector store."""
        return self._documents.copy()
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the vector store."""
        return len(self._documents)
    
    def get_embedding_dimension(self) -> Optional[int]:
        """Get the embedding dimension of stored vectors."""
        return self._embedding_dimension
    
    def validate_embeddings(self, documents: List[Document]) -> List[Document]:
        """
        Validate embeddings and filter out documents with invalid or mismatched sizes.
        
        Args:
            documents: List of documents with embeddings
            
        Returns:
            List[Document]: Documents with valid embeddings of consistent size
        """
        if not documents:
            logger.warning("No documents provided for embedding validation")
            return []
        
        valid_documents = []
        embedding_sizes = {}
        
        # First pass: collect all embedding sizes and count occurrences
        for i, doc in enumerate(documents):
            if not hasattr(doc, 'vector') or doc.vector is None:
                logger.warning(f"Document {i} has no embedding vector, skipping")
                continue
            
            try:
                if isinstance(doc.vector, list):
                    embedding_size = len(doc.vector)
                elif hasattr(doc.vector, 'shape'):
                    embedding_size = doc.vector.shape[0] if len(doc.vector.shape) == 1 else doc.vector.shape[-1]
                elif hasattr(doc.vector, '__len__'):
                    embedding_size = len(doc.vector)
                else:
                    logger.warning(f"Document {i} has invalid embedding vector type: {type(doc.vector)}, skipping")
                    continue
                
                if embedding_size == 0:
                    logger.warning(f"Document {i} has empty embedding vector, skipping")
                    continue
                
                embedding_sizes[embedding_size] = embedding_sizes.get(embedding_size, 0) + 1
                
            except Exception as e:
                logger.warning(f"Error checking embedding size for document {i}: {str(e)}, skipping")
                continue
        
        if not embedding_sizes:
            logger.error("No valid embeddings found in any documents")
            return []
        
        # Find the most common embedding size (this should be the correct one)
        target_size = max(embedding_sizes.keys(), key=lambda k: embedding_sizes[k])
        logger.info(f"Target embedding size: {target_size} (found in {embedding_sizes[target_size]} documents)")
        
        # Log all embedding sizes found
        for size, count in embedding_sizes.items():
            if size != target_size:
                logger.warning(f"Found {count} documents with incorrect embedding size {size}, will be filtered out")
        
        # Second pass: filter documents with the target embedding size
        for i, doc in enumerate(documents):
            if not hasattr(doc, 'vector') or doc.vector is None:
                continue
            
            try:
                if isinstance(doc.vector, list):
                    embedding_size = len(doc.vector)
                elif hasattr(doc.vector, 'shape'):
                    embedding_size = doc.vector.shape[0] if len(doc.vector.shape) == 1 else doc.vector.shape[-1]
                elif hasattr(doc.vector, '__len__'):
                    embedding_size = len(doc.vector)
                else:
                    continue
                
                if embedding_size == target_size:
                    valid_documents.append(doc)
                else:
                    # Log which document is being filtered out
                    file_path = getattr(doc, 'meta_data', {}).get('file_path', f'document_{i}')
                    logger.warning(f"Filtering out document '{file_path}' due to embedding size mismatch: {embedding_size} != {target_size}")
                    
            except Exception as e:
                file_path = getattr(doc, 'meta_data', {}).get('file_path', f'document_{i}')
                logger.warning(f"Error validating embedding for document '{file_path}': {str(e)}, skipping")
                continue
        
        logger.info(f"Embedding validation complete: {len(valid_documents)}/{len(documents)} documents have valid embeddings")
        
        if len(valid_documents) == 0:
            logger.error("No documents with valid embeddings remain after filtering")
        elif len(valid_documents) < len(documents):
            filtered_count = len(documents) - len(valid_documents)
            logger.warning(f"Filtered out {filtered_count} documents due to embedding issues")
        
        return valid_documents
    
    def _validate_documents(self, documents: List[Document]) -> List[Document]:
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
    
    def _check_embedding_dimension(self, documents: List[Document]) -> bool:
        """
        Check if all documents have consistent embedding dimensions.
        
        Args:
            documents: List of documents to check
            
        Returns:
            bool: True if dimensions are consistent, False otherwise
        """
        if not documents:
            return True
        
        dimensions = set()
        for doc in documents:
            if hasattr(doc, 'vector') and doc.vector is not None:
                try:
                    if isinstance(doc.vector, list):
                        dim = len(doc.vector)
                    elif hasattr(doc.vector, 'shape'):
                        dim = doc.vector.shape[0] if len(doc.vector.shape) == 1 else doc.vector.shape[-1]
                    elif hasattr(doc.vector, '__len__'):
                        dim = len(doc.vector)
                    else:
                        continue
                    
                    dimensions.add(dim)
                    
                except Exception:
                    continue
        
        if len(dimensions) > 1:
            logger.error(f"Multiple embedding dimensions found: {dimensions}")
            return False
        
        if dimensions:
            self._embedding_dimension = list(dimensions)[0]
        
        return True
    
    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """
        Get a document by its ID.
        
        Args:
            document_id: The document ID to search for
            
        Returns:
            Document: The document if found, None otherwise
        """
        for doc in self._documents:
            if doc.id == document_id:
                return doc
        return None
    
    def search_by_metadata(self, metadata_filter: Dict[str, Any]) -> List[Document]:
        """
        Search for documents by metadata criteria.
        
        Args:
            metadata_filter: Dictionary of metadata key-value pairs to filter by
            
        Returns:
            List[Document]: Documents matching the metadata filter
        """
        matching_docs = []
        
        for doc in self._documents:
            if hasattr(doc, 'meta_data') and doc.meta_data:
                matches = True
                for key, value in metadata_filter.items():
                    if key not in doc.meta_data or doc.meta_data[key] != value:
                        matches = False
                        break
                
                if matches:
                    matching_docs.append(doc)
        
        return matching_docs
    
    def get_documents_by_file_path(self, file_path: str) -> List[Document]:
        """
        Get documents by file path.
        
        Args:
            file_path: The file path to search for
            
        Returns:
            List[Document]: Documents with matching file path
        """
        matching_docs = []
        
        for doc in self._documents:
            if hasattr(doc, 'meta_data') and doc.meta_data:
                doc_file_path = doc.meta_data.get('file_path', '')
                if doc_file_path == file_path:
                    matching_docs.append(doc)
        
        return matching_docs
