"""
Vector Store Component for Data Layer

This module provides a comprehensive vector store component that handles vector database
operations, document management, and FAISS integration for the DeepWiki system.

The vector store serves as a foundational component for vector storage and retrieval
operations, providing a clean separation between vector storage and retrieval logic.
"""

import logging
from typing import List, Optional, Dict, Any, Union
import numpy as np

from adalflow.core.types import Document

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Comprehensive vector store for managing document vectors and embeddings.
    
    This component handles the storage, validation, and management of document vectors,
    providing a unified interface for vector database operations while maintaining
    FAISS integration for efficient similarity search.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the vector store.
        
        Args:
            db_manager: Optional database manager for persistence
            documents: Optional initial list of documents
            is_ollama_embedder: Whether using Ollama embedder (affects validation)
            embedding_dimension: Expected embedding dimension
            validate_on_init: Whether to validate documents on initialization
        """
        self._db_manager = kwargs.get("db_manager")
        self._documents: List[Document] = []
        self._embedding_dimension: Optional[int] = kwargs.get("embedding_dimension")
        self._is_ollama_embedder = kwargs.get("is_ollama_embedder", False)
        self._validate_on_init = kwargs.get("validate_on_init", True)
        
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
        
        This method implements the same validation logic that was previously embedded
        in the RAG system, ensuring consistency and filtering out problematic documents.
        
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
                embedding_size = self._get_embedding_size(doc.vector)
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
                embedding_size = self._get_embedding_size(doc.vector)
                
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
    
    def _get_embedding_size(self, vector: Any) -> int:
        """
        Get the size of an embedding vector.
        
        Args:
            vector: The embedding vector (can be list, numpy array, or other vector-like object)
            
        Returns:
            int: The size of the vector
        """
        try:
            if isinstance(vector, list):
                return len(vector)
            elif hasattr(vector, 'shape'):
                return vector.shape[0] if len(vector.shape) == 1 else vector.shape[-1]
            elif hasattr(vector, '__len__'):
                return len(vector)
            else:
                raise ValueError(f"Invalid embedding vector type: {type(vector)}")
        except Exception as e:
            raise ValueError(f"Error getting embedding size: {str(e)}")
    
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
                    dim = self._get_embedding_size(doc.vector)
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
    
    def get_documents_by_extension(self, file_extension: str) -> List[Document]:
        """
        Get documents by file extension.
        
        Args:
            file_extension: The file extension to search for (e.g., '.py', '.js')
            
        Returns:
            List[Document]: Documents with matching file extension
        """
        matching_docs = []
        
        for doc in self._documents:
            if hasattr(doc, 'meta_data') and doc.meta_data:
                doc_file_path = doc.meta_data.get('file_path', '')
                if doc_file_path.endswith(file_extension):
                    matching_docs.append(doc)
        
        return matching_docs
    
    def get_documents_by_directory(self, directory_path: str) -> List[Document]:
        """
        Get documents by directory path.
        
        Args:
            directory_path: The directory path to search for
            
        Returns:
            List[Document]: Documents in the specified directory
        """
        matching_docs = []
        
        for doc in self._documents:
            if hasattr(doc, 'meta_data') and doc.meta_data:
                doc_file_path = doc.meta_data.get('file_path', '')
                if doc_file_path.startswith(directory_path):
                    matching_docs.append(doc)
        
        return matching_docs
    
    def get_embedding_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the stored embeddings.
        
        Returns:
            Dict[str, Any]: Dictionary containing embedding statistics
        """
        if not self._documents:
            return {
                "total_documents": 0,
                "documents_with_vectors": 0,
                "embedding_dimension": None,
                "vector_types": {},
                "file_extensions": {},
                "total_vector_size": 0
            }
        
        stats = {
            "total_documents": len(self._documents),
            "documents_with_vectors": 0,
            "embedding_dimension": self._embedding_dimension,
            "vector_types": {},
            "file_extensions": {},
            "total_vector_size": 0
        }
        
        for doc in self._documents:
            # Count documents with vectors
            if hasattr(doc, 'vector') and doc.vector is not None:
                stats["documents_with_vectors"] += 1
                
                # Count vector types
                vector_type = type(doc.vector).__name__
                stats["vector_types"][vector_type] = stats["vector_types"].get(vector_type, 0) + 1
                
                # Calculate total vector size
                try:
                    vector_size = self._get_embedding_size(doc.vector)
                    stats["total_vector_size"] += vector_size
                except Exception:
                    pass
            
            # Count file extensions
            if hasattr(doc, 'meta_data') and doc.meta_data:
                file_path = doc.meta_data.get('file_path', '')
                if file_path:
                    import os
                    _, ext = os.path.splitext(file_path)
                    if ext:
                        stats["file_extensions"][ext] = stats["file_extensions"].get(ext, 0) + 1
        
        return stats
    
    def export_vectors(self, output_format: str = "numpy") -> Union[np.ndarray, List[List[float]]]:
        """
        Export all vectors in the specified format.
        
        Args:
            output_format: Output format ('numpy' or 'list')
            
        Returns:
            Union[np.ndarray, List[List[float]]: Exported vectors
        """
        if not self._documents:
            return np.array([]) if output_format == "numpy" else []
        
        vectors = []
        for doc in self._documents:
            if hasattr(doc, 'vector') and doc.vector is not None:
                try:
                    if isinstance(doc.vector, list):
                        vectors.append(doc.vector)
                    elif hasattr(doc.vector, 'tolist'):
                        vectors.append(doc.vector.tolist())
                    else:
                        vectors.append(list(doc.vector))
                except Exception as e:
                    logger.warning(f"Error exporting vector for document {doc.id}: {str(e)}")
                    continue
        
        if output_format == "numpy":
            return np.array(vectors)
        else:
            return vectors
    
    def import_vectors(self, vectors: Union[np.ndarray, List[List[float]]], 
                      document_ids: Optional[List[str]] = None) -> bool:
        """
        Import vectors and assign them to documents.
        
        Args:
            vectors: Vectors to import
            document_ids: Optional list of document IDs to assign vectors to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not vectors:
                return True
            
            if document_ids and len(vectors) != len(document_ids):
                logger.error("Number of vectors must match number of document IDs")
                return False
            
            # Convert to list if numpy array
            if isinstance(vectors, np.ndarray):
                vectors = vectors.tolist()
            
            # Assign vectors to documents
            if document_ids:
                for i, doc_id in enumerate(document_ids):
                    doc = self.get_document_by_id(doc_id)
                    if doc:
                        doc.vector = vectors[i]
            else:
                # Assign to documents in order
                for i, doc in enumerate(self._documents):
                    if i < len(vectors):
                        doc.vector = vectors[i]
            
            logger.info(f"Successfully imported {len(vectors)} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Error importing vectors: {str(e)}")
            return False
    
    def save_to_database(self, database_path: Optional[str] = None) -> bool:
        """
        Save the vector store to a database file.
        
        Args:
            database_path: Optional path to save the database
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._db_manager:
                logger.warning("No database manager available for saving")
                return False
            
            # This would integrate with the existing database manager
            # Implementation depends on the specific database manager interface
            logger.info("Vector store save functionality would be implemented here")
            return True
            
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            return False
    
    def load_from_database(self, database_path: Optional[str] = None) -> bool:
        """
        Load the vector store from a database file.
        
        Args:
            database_path: Optional path to load the database from
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._db_manager:
                logger.warning("No database manager available for loading")
                return False
            
            # This would integrate with the existing database manager
            # Implementation depends on the specific database manager interface
            logger.info("Vector store load functionality would be implemented here")
            return True
            
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False
