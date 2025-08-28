"""
Vector Operations Manager for Data Layer

This module provides a unified interface for all vector operations, integrating
the vector store and FAISS components to provide comprehensive vector management
capabilities.

The manager serves as the main entry point for vector operations, ensuring
clean separation between vector storage and retrieval logic while maintaining
compatibility with existing systems.
"""

import logging
import time
from typing import List, Optional, Dict, Any, Union, Tuple, Callable
import numpy as np

from adalflow.core.types import Document

from .vector_store import VectorStore
from .faiss_integration import FAISSIntegration, FAISSCompatibilityWrapper

logger = logging.getLogger(__name__)


class VectorOperationsManager:
    """
    Unified manager for all vector operations.
    
    This component integrates the vector store and FAISS components to provide
    a comprehensive interface for vector management, storage, and retrieval.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the vector operations manager.
        
        Args:
            db_manager: Optional database manager for persistence
            embedder: Embedder instance for query processing
            top_k: Number of top results to return (default: 20)
            is_ollama_embedder: Whether using Ollama embedder
            faiss_config: Additional FAISS configuration parameters
            validate_on_init: Whether to validate documents on initialization
        """
        self._db_manager = kwargs.get("db_manager")
        self._embedder = kwargs.get("embedder")
        self._top_k = kwargs.get("top_k", 20)
        self._is_ollama_embedder = kwargs.get("is_ollama_embedder", False)
        self._faiss_config = kwargs.get("faiss_config", {})
        self._validate_on_init = kwargs.get("validate_on_init", True)
        
        # Initialize components
        self._vector_store = None
        self._faiss_integration = None
        self._is_initialized = False
        
        # Initialize if embedder is provided
        if self._embedder:
            self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize the vector store and FAISS integration components."""
        try:
            # Create vector store
            self._vector_store = VectorStore(
                db_manager=self._db_manager,
                is_ollama_embedder=self._is_ollama_embedder,
                validate_on_init=self._validate_on_init
            )
            
            # Create FAISS integration
            self._faiss_integration = FAISSIntegration(
                vector_store=self._vector_store,
                top_k=self._top_k,
                embedder=self._embedder,
                faiss_config=self._faiss_config
            )
            
            self._is_initialized = True
            logger.info("Vector operations manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector operations manager: {str(e)}")
            self._is_initialized = False
    
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Add documents to the vector operations system.
        
        Args:
            documents: List of documents to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._is_initialized:
                logger.error("Vector operations manager not initialized")
                return False
            
            # Add documents to vector store
            success = self._vector_store.add_documents(documents)
            if not success:
                return False
            
            # Add documents to FAISS integration
            success = self._faiss_integration.add_documents(documents)
            if not success:
                logger.warning("Documents added to vector store but failed to add to FAISS")
                # Continue as vector store still has the documents
            
            logger.info(f"Successfully added {len(documents)} documents to vector operations system")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector operations system: {str(e)}")
            return False
    
    def remove_documents(self, document_ids: List[str]) -> bool:
        """
        Remove documents from the vector operations system.
        
        Args:
            document_ids: List of document IDs to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._is_initialized:
                logger.error("Vector operations manager not initialized")
                return False
            
            # Remove documents from both components
            vector_success = self._vector_store.remove_documents(document_ids)
            faiss_success = self._faiss_integration.remove_documents(document_ids)
            
            if vector_success and faiss_success:
                logger.info(f"Successfully removed {len(document_ids)} documents from vector operations system")
                return True
            else:
                logger.warning("Documents removed from some components but not all")
                return False
            
        except Exception as e:
            logger.error(f"Error removing documents from vector operations system: {str(e)}")
            return False
    
    def clear_documents(self) -> bool:
        """
        Clear all documents from the vector operations system.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._is_initialized:
                logger.error("Vector operations manager not initialized")
                return False
            
            # Clear documents from both components
            vector_success = self._vector_store.clear_documents()
            faiss_success = self._faiss_integration.clear_documents()
            
            if vector_success and faiss_success:
                logger.info("Successfully cleared all documents from vector operations system")
                return True
            else:
                logger.warning("Documents cleared from some components but not all")
                return False
            
        except Exception as e:
            logger.error(f"Error clearing documents from vector operations system: {str(e)}")
            return False
    
    def search_documents(self, query: str, top_k: Optional[int] = None) -> List[Document]:
        """
        Search for documents using vector similarity.
        
        Args:
            query: Query string to search for
            top_k: Number of top results to return (overrides default)
            
        Returns:
            List[Document]: List of similar documents
        """
        try:
            if not self._is_initialized:
                logger.error("Vector operations manager not initialized")
                return []
            
            if not self._faiss_integration.is_ready():
                logger.error("FAISS integration not ready for search")
                return []
            
            # Perform search using FAISS integration
            results = self._faiss_integration.search(query, top_k)
            
            logger.info(f"Vector search returned {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error performing vector search: {str(e)}")
            return []
    
    def search_by_vector(self, query_vector: Union[List[float], np.ndarray], 
                        top_k: Optional[int] = None) -> List[Document]:
        """
        Search for documents using a query vector.
        
        Args:
            query_vector: Query vector to search for
            top_k: Number of top results to return (overrides default)
            
        Returns:
            List[Document]: List of similar documents
        """
        try:
            if not self._is_initialized:
                logger.error("Vector operations manager not initialized")
                return []
            
            if not self._faiss_integration.is_ready():
                logger.error("FAISS integration not ready for vector search")
                return []
            
            # Perform vector search using FAISS integration
            results = self._faiss_integration.search_by_vector(query_vector, top_k)
            
            logger.info(f"Vector search returned {len(results)} results for {len(query_vector)}-dimensional vector")
            return results
            
        except Exception as e:
            logger.error(f"Error performing vector search: {str(e)}")
            return []
    
    def validate_embeddings(self, documents: List[Document]) -> List[Document]:
        """
        Validate embeddings using the vector store validation.
        
        Args:
            documents: List of documents to validate
            
        Returns:
            List[Document]: Documents with valid embeddings
        """
        try:
            if not self._is_initialized:
                logger.error("Vector operations manager not initialized")
                return []
            
            return self._vector_store.validate_embeddings(documents)
            
        except Exception as e:
            logger.error(f"Error validating embeddings: {str(e)}")
            return []
    
    def get_documents(self, **kwargs) -> List[Document]:
        """
        Get documents from the vector store with optional filtering.
        
        Args:
            **kwargs: Filtering options (file_path, file_extension, directory_path, metadata_filter)
            
        Returns:
            List[Document]: Filtered documents
        """
        try:
            if not self._is_initialized:
                logger.error("Vector operations manager not initialized")
                return []
            
            # Apply filters based on kwargs
            if 'file_path' in kwargs:
                return self._vector_store.get_documents_by_file_path(kwargs['file_path'])
            elif 'file_extension' in kwargs:
                return self._vector_store.get_documents_by_extension(kwargs['file_extension'])
            elif 'directory_path' in kwargs:
                return self._vector_store.get_documents_by_directory(kwargs['directory_path'])
            elif 'metadata_filter' in kwargs:
                return self._vector_store.search_by_metadata(kwargs['metadata_filter'])
            else:
                return self._vector_store.get_documents()
                
        except Exception as e:
            logger.error(f"Error getting documents: {str(e)}")
            return []
    
    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """
        Get a document by its ID.
        
        Args:
            document_id: The document ID to search for
            
        Returns:
            Document: The document if found, None otherwise
        """
        try:
            if not self._is_initialized:
                logger.error("Vector operations manager not initialized")
                return None
            
            return self._vector_store.get_document_by_id(document_id)
            
        except Exception as e:
            logger.error(f"Error getting document by ID: {str(e)}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the vector operations system.
        
        Returns:
            Dict[str, Any]: Dictionary containing system statistics
        """
        try:
            if not self._is_initialized:
                return {
                    "is_initialized": False,
                    "error": "Vector operations manager not initialized"
                }
            
            # Get statistics from both components
            vector_stats = self._vector_store.get_embedding_statistics()
            faiss_stats = self._faiss_integration.get_faiss_statistics()
            
            # Combine statistics
            combined_stats = {
                "is_initialized": self._is_initialized,
                "vector_store": vector_stats,
                "faiss_integration": faiss_stats,
                "total_documents": vector_stats.get("total_documents", 0),
                "embedding_dimension": vector_stats.get("embedding_dimension"),
                "faiss_ready": self._faiss_integration.is_ready()
            }
            
            return combined_stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {
                "is_initialized": self._is_initialized,
                "error": str(e)
            }
    
    def export_vectors(self, output_format: str = "numpy") -> Union[np.ndarray, List[List[float]]]:
        """
        Export all vectors in the specified format.
        
        Args:
            output_format: Output format ('numpy' or 'list')
            
        Returns:
            Union[np.ndarray, List[List[float]]: Exported vectors
        """
        try:
            if not self._is_initialized:
                logger.error("Vector operations manager not initialized")
                return np.array([]) if output_format == "numpy" else []
            
            return self._vector_store.export_vectors(output_format)
            
        except Exception as e:
            logger.error(f"Error exporting vectors: {str(e)}")
            return np.array([]) if output_format == "numpy" else []
    
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
            if not self._is_initialized:
                logger.error("Vector operations manager not initialized")
                return False
            
            # Import vectors to vector store
            success = self._vector_store.import_vectors(vectors, document_ids)
            if not success:
                return False
            
            # Reinitialize FAISS integration with updated vectors
            if self._faiss_integration:
                self._faiss_integration._initialize_faiss()
            
            logger.info(f"Successfully imported {len(vectors)} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Error importing vectors: {str(e)}")
            return False
    
    def update_configuration(self, new_config: Dict[str, Any]) -> bool:
        """
        Update the configuration of the vector operations system.
        
        Args:
            new_config: New configuration parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update FAISS configuration
            if 'faiss_config' in new_config and self._faiss_integration:
                success = self._faiss_integration.update_faiss_config(new_config['faiss_config'])
                if not success:
                    logger.warning("Failed to update FAISS configuration")
            
            # Update other configuration parameters
            if 'top_k' in new_config:
                self._top_k = new_config['top_k']
                if self._faiss_integration:
                    self._faiss_integration._top_k = self._top_k
            
            logger.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {str(e)}")
            return False
    
    def create_faiss_compatibility_wrapper(self) -> FAISSCompatibilityWrapper:
        """
        Create a FAISS compatibility wrapper for existing code.
        
        Returns:
            FAISSCompatibilityWrapper: Compatibility wrapper instance
        """
        try:
            if not self._is_initialized or not self._faiss_integration:
                logger.error("Cannot create compatibility wrapper: system not initialized")
                return None
            
            return self._faiss_integration.create_compatibility_wrapper()
            
        except Exception as e:
            logger.error(f"Error creating compatibility wrapper: {str(e)}")
            return None
    
    def is_ready(self) -> bool:
        """
        Check if the vector operations system is ready for use.
        
        Returns:
            bool: True if ready, False otherwise
        """
        return (self._is_initialized and 
                self._vector_store is not None and 
                self._faiss_integration is not None and
                self._faiss_integration.is_ready())
    
    def get_vector_store(self) -> Optional[VectorStore]:
        """
        Get the underlying vector store component.
        
        Returns:
            VectorStore: The vector store component or None
        """
        return self._vector_store
    
    def get_faiss_integration(self) -> Optional[FAISSIntegration]:
        """
        Get the underlying FAISS integration component.
        
        Returns:
            FAISSIntegration: The FAISS integration component or None
        """
        return self._faiss_integration
    
    def save_to_database(self, database_path: Optional[str] = None) -> bool:
        """
        Save the vector operations system to a database.
        
        Args:
            database_path: Optional path to save the database
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._is_initialized:
                logger.error("Vector operations manager not initialized")
                return False
            
            # Save vector store
            vector_success = self._vector_store.save_to_database(database_path)
            
            # Note: FAISS index would need to be saved separately
            # This is a placeholder for future implementation
            logger.info("Vector operations save functionality would be implemented here")
            
            return vector_success
            
        except Exception as e:
            logger.error(f"Error saving vector operations system: {str(e)}")
            return False
    
    def load_from_database(self, database_path: Optional[str] = None) -> bool:
        """
        Load the vector operations system from a database.
        
        Args:
            database_path: Optional path to load the database from
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self._is_initialized:
                logger.error("Vector operations manager not initialized")
                return False
            
            # Load vector store
            vector_success = self._vector_store.load_from_database(database_path)
            
            # Reinitialize FAISS integration with loaded data
            if vector_success and self._faiss_integration:
                self._faiss_integration._initialize_faiss()
            
            # Note: FAISS index would need to be loaded separately
            # This is a placeholder for future implementation
            logger.info("Vector operations load functionality would be implemented here")
            
            return vector_success
            
        except Exception as e:
            logger.error(f"Error loading vector operations system: {str(e)}")
            return False
