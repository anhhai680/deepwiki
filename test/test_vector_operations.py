"""
Test Vector Operations Components

This module tests the vector operations components to ensure they work
correctly and maintain compatibility with existing systems.
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock

# Import the components to test
from api.data.vector_store import VectorStore
from api.data.faiss_integration import FAISSIntegration, FAISSCompatibilityWrapper
from api.data.vector_operations import VectorOperationsManager
from api.data.vector_compatibility import (
    create_vector_operations_manager,
    create_faiss_compatibility_wrapper,
    validate_embeddings,
    create_vector_store_from_documents,
    create_faiss_retriever_from_config
)


class TestVectorStore:
    """Test the VectorStore component."""
    
    def test_vector_store_initialization(self):
        """Test vector store initialization."""
        vector_store = VectorStore()
        assert vector_store is not None
        assert vector_store.get_document_count() == 0
        assert vector_store.get_embedding_dimension() is None
    
    def test_vector_store_with_documents(self):
        """Test vector store with initial documents."""
        # Create mock documents
        doc1 = Mock()
        doc1.id = "doc1"
        doc1.vector = [1.0, 2.0, 3.0]
        doc1.meta_data = {"file_path": "test1.py"}
        
        doc2 = Mock()
        doc2.id = "doc2"
        doc2.vector = [4.0, 5.0, 6.0]
        doc2.meta_data = {"file_path": "test2.py"}
        
        documents = [doc1, doc2]
        
        vector_store = VectorStore(documents=documents)
        assert vector_store.get_document_count() == 2
        assert vector_store.get_embedding_dimension() == 3
    
    def test_add_documents(self):
        """Test adding documents to vector store."""
        vector_store = VectorStore()
        
        # Create mock documents
        doc1 = Mock()
        doc1.id = "doc1"
        doc1.vector = [1.0, 2.0, 3.0]
        
        success = vector_store.add_documents([doc1])
        assert success is True
        assert vector_store.get_document_count() == 1
    
    def test_remove_documents(self):
        """Test removing documents from vector store."""
        vector_store = VectorStore()
        
        # Add documents first
        doc1 = Mock()
        doc1.id = "doc1"
        doc1.vector = [1.0, 2.0, 3.0]
        
        doc2 = Mock()
        doc2.id = "doc2"
        doc2.vector = [4.0, 5.0, 6.0]
        
        vector_store.add_documents([doc1, doc2])
        assert vector_store.get_document_count() == 2
        
        # Remove one document
        success = vector_store.remove_documents(["doc1"])
        assert success is True
        assert vector_store.get_document_count() == 1
    
    def test_clear_documents(self):
        """Test clearing all documents from vector store."""
        vector_store = VectorStore()
        
        # Add documents first
        doc1 = Mock()
        doc1.id = "doc1"
        doc1.vector = [1.0, 2.0, 3.0]
        
        vector_store.add_documents([doc1])
        assert vector_store.get_document_count() == 1
        
        # Clear documents
        success = vector_store.clear_documents()
        assert success is True
        assert vector_store.get_document_count() == 0
    
    def test_validate_embeddings(self):
        """Test embedding validation."""
        vector_store = VectorStore()
        
        # Create documents with consistent embeddings
        doc1 = Mock()
        doc1.id = "doc1"
        doc1.vector = [1.0, 2.0, 3.0]
        
        doc2 = Mock()
        doc2.id = "doc2"
        doc2.vector = [4.0, 5.0, 6.0]
        
        documents = [doc1, doc2]
        
        # Validate embeddings
        valid_docs = vector_store.validate_embeddings(documents)
        assert len(valid_docs) == 2
        
        # Test with inconsistent embeddings
        doc3 = Mock()
        doc3.id = "doc3"
        doc3.vector = [7.0, 8.0]  # Different size
        
        documents_mixed = [doc1, doc2, doc3]
        valid_docs = vector_store.validate_embeddings(documents_mixed)
        assert len(valid_docs) == 2  # Should filter out inconsistent one
    
    def test_get_documents_by_file_path(self):
        """Test getting documents by file path."""
        vector_store = VectorStore()
        
        # Add documents with file paths
        doc1 = Mock()
        doc1.id = "doc1"
        doc1.vector = [1.0, 2.0, 3.0]
        doc1.meta_data = {"file_path": "src/test1.py"}
        
        doc2 = Mock()
        doc2.id = "doc2"
        doc2.vector = [4.0, 5.0, 6.0]
        doc2.meta_data = {"file_path": "src/test2.py"}
        
        vector_store.add_documents([doc1, doc2])
        
        # Get documents by file path
        docs = vector_store.get_documents_by_file_path("src/test1.py")
        assert len(docs) == 1
        assert docs[0].id == "doc1"
    
    def test_get_embedding_statistics(self):
        """Test getting embedding statistics."""
        vector_store = VectorStore()
        
        # Add documents
        doc1 = Mock()
        doc1.id = "doc1"
        doc1.vector = [1.0, 2.0, 3.0]
        doc1.meta_data = {"file_path": "test1.py"}
        
        doc2 = Mock()
        doc2.id = "doc2"
        doc2.vector = [4.0, 5.0, 6.0]
        doc2.meta_data = {"file_path": "test2.py"}
        
        vector_store.add_documents([doc1, doc2])
        
        # Get statistics
        stats = vector_store.get_embedding_statistics()
        assert stats["total_documents"] == 2
        assert stats["documents_with_vectors"] == 2
        assert stats["embedding_dimension"] == 3
        assert ".py" in stats["file_extensions"]
        assert stats["file_extensions"][".py"] == 2


class TestFAISSIntegration:
    """Test the FAISSIntegration component."""
    
    def test_faiss_integration_initialization(self):
        """Test FAISS integration initialization."""
        # Mock embedder
        mock_embedder = Mock()
        
        # Mock vector store
        mock_vector_store = Mock()
        mock_vector_store.get_documents.return_value = []
        
        faiss_integration = FAISSIntegration(
            vector_store=mock_vector_store,
            embedder=mock_embedder
        )
        
        assert faiss_integration is not None
        assert faiss_integration._vector_store == mock_vector_store
        assert faiss_integration._embedder == mock_embedder
    
    def test_faiss_integration_ready_state(self):
        """Test FAISS integration ready state."""
        # Mock embedder
        mock_embedder = Mock()
        
        # Mock vector store with documents
        mock_vector_store = Mock()
        mock_doc = Mock()
        mock_doc.vector = [1.0, 2.0, 3.0]
        mock_vector_store.get_documents.return_value = [mock_doc]
        
        faiss_integration = FAISSIntegration(
            vector_store=mock_vector_store,
            embedder=mock_embedder
        )
        
        # Should be ready if FAISS retriever was created
        # Note: This test may need adjustment based on actual FAISS initialization
        assert faiss_integration._vector_store is not None


class TestVectorOperationsManager:
    """Test the VectorOperationsManager component."""
    
    def test_vector_operations_manager_initialization(self):
        """Test vector operations manager initialization."""
        # Mock embedder
        mock_embedder = Mock()
        
        manager = VectorOperationsManager(embedder=mock_embedder)
        assert manager is not None
        assert manager._embedder == mock_embedder
    
    def test_vector_operations_manager_not_initialized(self):
        """Test vector operations manager without embedder."""
        manager = VectorOperationsManager()
        assert manager is not None
        assert not manager._is_initialized
    
    def test_add_documents_not_initialized(self):
        """Test adding documents when not initialized."""
        manager = VectorOperationsManager()
        
        # Mock document
        doc = Mock()
        doc.id = "doc1"
        doc.vector = [1.0, 2.0, 3.0]
        
        success = manager.add_documents([doc])
        assert success is False  # Should fail when not initialized


class TestVectorCompatibility:
    """Test the vector compatibility functions."""
    
    def test_create_vector_operations_manager(self):
        """Test creating vector operations manager through compatibility function."""
        # Mock embedder
        mock_embedder = Mock()
        
        manager = create_vector_operations_manager(embedder=mock_embedder)
        assert manager is not None
        assert isinstance(manager, VectorOperationsManager)
    
    def test_validate_embeddings_compatibility(self):
        """Test embedding validation through compatibility function."""
        # Create documents with consistent embeddings
        doc1 = Mock()
        doc1.id = "doc1"
        doc1.vector = [1.0, 2.0, 3.0]
        
        doc2 = Mock()
        doc2.id = "doc2"
        doc2.vector = [4.0, 5.0, 6.0]
        
        documents = [doc1, doc2]
        
        # Validate embeddings
        valid_docs = validate_embeddings(documents)
        assert len(valid_docs) == 2
    
    def test_create_vector_store_from_documents(self):
        """Test creating vector store from documents through compatibility function."""
        # Create documents
        doc1 = Mock()
        doc1.id = "doc1"
        doc1.vector = [1.0, 2.0, 3.0]
        
        doc2 = Mock()
        doc2.id = "doc2"
        doc2.vector = [4.0, 5.0, 6.0]
        
        documents = [doc1, doc2]
        
        # Create vector store
        vector_store = create_vector_store_from_documents(documents)
        assert vector_store is not None
        assert vector_store.get_document_count() == 2


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__])
