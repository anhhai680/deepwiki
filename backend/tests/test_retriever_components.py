"""
Test suite for retriever components.

This module tests all retriever components to ensure they work correctly
and maintain all RAG functionality.
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock
from typing import List

from backend.components.retriever.base import (
    BaseRetriever,
    RetrievalMethod,
    RetrievalResult
)
from backend.components.retriever.faiss_retriever import FAISSRetriever
from backend.components.retriever.vector_store import VectorStore
from backend.components.retriever.retriever_manager import RetrieverManager, RetrieverType
from backend.components.retriever.compatibility import (
    create_faiss_retriever_from_config,
    create_vector_store_from_documents,
    create_memory_component,
    validate_and_filter_embeddings
)
from backend.components.memory.conversation_memory import (
    ConversationMemory,
    UserQuery,
    AssistantResponse,
    DialogTurn
)


class TestRetrievalMethod:
    """Test the RetrievalMethod enum."""
    
    def test_retrieval_method_values(self):
        """Test that all retrieval method values are correct."""
        assert RetrievalMethod.UNDEFINED.value == "undefined"
        assert RetrievalMethod.VECTOR_SIMILARITY.value == "vector_similarity"
        assert RetrievalMethod.KEYWORD_MATCH.value == "keyword_match"
        assert RetrievalMethod.HYBRID.value == "hybrid"
        assert RetrievalMethod.SEMANTIC.value == "semantic"


class TestRetrievalResult:
    """Test the RetrievalResult dataclass."""
    
    def test_retrieval_result_creation(self):
        """Test creating a RetrievalResult instance."""
        documents = [Mock(), Mock()]
        doc_indices = [0, 1]
        scores = [0.9, 0.8]
        
        result = RetrievalResult(
            documents=documents,
            doc_indices=doc_indices,
            scores=scores
        )
        
        assert result.documents == documents
        assert result.doc_indices == doc_indices
        assert result.scores == scores
        assert result.error is None
    
    def test_retrieval_result_with_error(self):
        """Test creating a RetrievalResult with an error."""
        result = RetrievalResult(
            documents=[],
            doc_indices=[],
            error="Test error"
        )
        
        assert result.error == "Test error"
        assert bool(result) is False
    
    def test_retrieval_result_string_representation(self):
        """Test the string representation of RetrievalResult."""
        # Success case
        result = RetrievalResult(
            documents=[Mock(), Mock()],
            doc_indices=[0, 1],
            scores=[0.9, 0.8]
        )
        assert "RetrievalResult(documents=2, scores=2)" in str(result)
        
        # Error case
        error_result = RetrievalResult(
            documents=[],
            doc_indices=[],
            error="Test error"
        )
        assert "RetrievalResult(error='Test error')" in str(error_result)


class TestBaseRetriever:
    """Test the BaseRetriever abstract class."""
    
    def test_base_retriever_initialization(self):
        """Test BaseRetriever initialization with default values."""
        # Create a concrete implementation for testing
        class TestRetriever(BaseRetriever):
            def add_documents(self, documents):
                return True
            
            def remove_documents(self, document_ids):
                return True
            
            def clear_documents(self):
                return True
            
            def __call__(self, query, top_k=None):
                return RetrievalResult(documents=[], doc_indices=[])
        
        retriever = TestRetriever()
        
        assert retriever._method == RetrievalMethod.VECTOR_SIMILARITY
        assert retriever._top_k == 20
        assert retriever._score_threshold == 0.0
        assert retriever._max_retries == 3
    
    def test_base_retriever_validation(self):
        """Test document validation in BaseRetriever."""
        class TestRetriever(BaseRetriever):
            def add_documents(self, documents):
                return True
            
            def remove_documents(self, document_ids):
                return True
            
            def clear_documents(self):
                return True
            
            def __call__(self, query, top_k=None):
                return RetrievalResult(documents=[], doc_indices=[])
        
        retriever = TestRetriever()
        
        # Test with valid documents
        valid_doc = Mock()
        valid_doc.vector = [1.0, 2.0, 3.0]
        valid_docs = [valid_doc]
        
        result = retriever.validate_documents(valid_docs)
        assert len(result) == 1
        
        # Test with invalid documents
        invalid_doc = Mock()
        invalid_doc.vector = None
        invalid_docs = [invalid_doc]
        
        result = retriever.validate_documents(invalid_docs)
        assert len(result) == 0
    
    def test_base_retriever_configuration(self):
        """Test configuration methods in BaseRetriever."""
        class TestRetriever(BaseRetriever):
            def add_documents(self, documents):
                return True
            
            def remove_documents(self, document_ids):
                return True
            
            def clear_documents(self):
                return True
            
            def __call__(self, query, top_k=None):
                return RetrievalResult(documents=[], doc_indices=[])
        
        retriever = TestRetriever()
        
        # Test setting top_k
        retriever.set_top_k(15)
        assert retriever._top_k == 15
        
        # Test setting score threshold
        retriever.set_score_threshold(0.5)
        assert retriever._score_threshold == 0.5
        
        # Test invalid values
        retriever.set_top_k(-1)
        assert retriever._top_k == 15  # Should not change
        
        retriever.set_score_threshold(1.5)
        assert retriever._score_threshold == 1.0  # Should be capped at 1.0


class TestFAISSRetriever:
    """Test the FAISSRetriever implementation."""
    
    def test_faiss_retriever_initialization(self):
        """Test FAISSRetriever initialization."""
        # Mock the embedder
        mock_embedder = Mock()
        
        retriever = FAISSRetriever(
            embedder=mock_embedder,
            top_k=15
        )
        
        assert retriever._top_k == 15
        assert retriever._embedder == mock_embedder
        assert retriever._faiss_retriever is None
    
    def test_faiss_retriever_add_documents(self):
        """Test adding documents to FAISSRetriever."""
        # Mock the embedder
        mock_embedder = Mock()
        
        retriever = FAISSRetriever(embedder=mock_embedder)
        
        # Mock documents with vectors
        mock_doc1 = Mock()
        mock_doc1.vector = [1.0, 2.0, 3.0]
        mock_doc2 = Mock()
        mock_doc2.vector = [4.0, 5.0, 6.0]
        
        documents = [mock_doc1, mock_doc2]
        
        # Mock the underlying FAISS retriever creation
        with pytest.raises(ValueError):  # Should fail without proper FAISS setup
            retriever.add_documents(documents)
    
    def test_faiss_retriever_validation(self):
        """Test embedding validation in FAISSRetriever."""
        retriever = FAISSRetriever()
        
        # Test with documents of consistent embedding size
        mock_doc1 = Mock()
        mock_doc1.vector = [1.0, 2.0, 3.0]
        mock_doc2 = Mock()
        mock_doc2.vector = [4.0, 5.0, 6.0]
        
        documents = [mock_doc1, mock_doc2]
        result = retriever.validate_embeddings(documents)
        
        assert len(result) == 2
        
        # Test with documents of inconsistent embedding size
        mock_doc3 = Mock()
        mock_doc3.vector = [7.0, 8.0]  # Different size
        
        documents_mixed = [mock_doc1, mock_doc2, mock_doc3]
        result = retriever.validate_embeddings(documents_mixed)
        
        # Should filter out the inconsistent document
        assert len(result) == 2


class TestVectorStore:
    """Test the VectorStore component."""
    
    def test_vector_store_initialization(self):
        """Test VectorStore initialization."""
        vector_store = VectorStore()
        
        assert vector_store._documents == []
        assert vector_store._embedding_dimension is None
        assert vector_store._is_ollama_embedder is False
    
    def test_vector_store_add_documents(self):
        """Test adding documents to VectorStore."""
        vector_store = VectorStore()
        
        # Mock documents with vectors
        mock_doc1 = Mock()
        mock_doc1.vector = [1.0, 2.0, 3.0]
        mock_doc2 = Mock()
        mock_doc2.vector = [4.0, 5.0, 6.0]
        
        documents = [mock_doc1, mock_doc2]
        
        result = vector_store.add_documents(documents)
        assert result is True
        assert len(vector_store._documents) == 2
        assert vector_store._embedding_dimension == 3
    
    def test_vector_store_remove_documents(self):
        """Test removing documents from VectorStore."""
        vector_store = VectorStore()
        
        # Add documents first
        mock_doc1 = Mock()
        mock_doc1.id = "doc1"
        mock_doc1.vector = [1.0, 2.0, 3.0]
        mock_doc2 = Mock()
        mock_doc2.id = "doc2"
        mock_doc2.vector = [4.0, 5.0, 6.0]
        
        documents = [mock_doc1, mock_doc2]
        vector_store.add_documents(documents)
        
        # Remove a document
        result = vector_store.remove_documents(["doc1"])
        assert result is True
        assert len(vector_store._documents) == 1
        assert vector_store._documents[0].id == "doc2"
    
    def test_vector_store_search_by_metadata(self):
        """Test searching documents by metadata in VectorStore."""
        vector_store = VectorStore()
        
        # Add documents with metadata
        mock_doc1 = Mock()
        mock_doc1.vector = [1.0, 2.0, 3.0]
        mock_doc1.meta_data = {"file_path": "/path1", "type": "code"}
        mock_doc2 = Mock()
        mock_doc2.vector = [4.0, 5.0, 6.0]
        mock_doc2.meta_data = {"file_path": "/path2", "type": "doc"}
        
        documents = [mock_doc1, mock_doc2]
        vector_store.add_documents(documents)
        
        # Search by metadata
        result = vector_store.search_by_metadata({"type": "code"})
        assert len(result) == 1
        assert result[0].meta_data["file_path"] == "/path1"


class TestRetrieverManager:
    """Test the RetrieverManager."""
    
    def test_retriever_manager_initialization(self):
        """Test RetrieverManager initialization."""
        manager = RetrieverManager()
        
        assert manager._retrievers == {}
        assert manager._default_retriever is None
        assert manager._vector_store is None
    
    def test_retriever_manager_create_retriever(self):
        """Test creating retrievers through RetrieverManager."""
        manager = RetrieverManager()
        
        # Mock embedder
        mock_embedder = Mock()
        
        # Create FAISS retriever
        retriever = manager.create_retriever(
            RetrieverType.FAISS,
            embedder=mock_embedder
        )
        
        assert retriever is not None
        assert "faiss" in manager._retrievers
        assert manager._default_retriever == "faiss"
    
    def test_retriever_manager_get_retriever(self):
        """Test getting retrievers through RetrieverManager."""
        manager = RetrieverManager()
        
        # Mock embedder
        mock_embedder = Mock()
        
        # Create and get retriever
        manager.create_retriever(RetrieverType.FAISS, embedder=mock_embedder)
        retriever = manager.get_retriever()
        
        assert retriever is not None
        assert retriever == manager._retrievers["faiss"]
    
    def test_retriever_manager_available_retrievers(self):
        """Test getting available retriever types."""
        manager = RetrieverManager()
        
        # Mock embedder
        mock_embedder = Mock()
        
        # Create retrievers
        manager.create_retriever(RetrieverType.FAISS, embedder=mock_embedder)
        manager.create_retriever(RetrieverType.VECTOR_STORE)
        
        available = manager.get_available_retrievers()
        assert "faiss" in available
        assert "vector_store" in available


class TestConversationMemory:
    """Test the ConversationMemory component."""
    
    def test_conversation_memory_initialization(self):
        """Test ConversationMemory initialization."""
        memory = ConversationMemory()
        
        assert memory._max_turns == 100
        assert memory._auto_cleanup is True
        assert hasattr(memory.current_conversation, 'dialog_turns')
    
    def test_conversation_memory_add_dialog_turn(self):
        """Test adding dialog turns to ConversationMemory."""
        memory = ConversationMemory()
        
        result = memory.add_dialog_turn("Hello", "Hi there!")
        assert result is True
        
        # Check that the turn was added
        turns = memory.get_conversation_history()
        assert len(turns) == 1
        assert turns[0].user_query.query_str == "Hello"
        assert turns[0].assistant_response.response_str == "Hi there!"
    
    def test_conversation_memory_get_conversation_history(self):
        """Test getting conversation history from ConversationMemory."""
        memory = ConversationMemory()
        
        # Add some turns
        memory.add_dialog_turn("Q1", "A1")
        memory.add_dialog_turn("Q2", "A2")
        memory.add_dialog_turn("Q3", "A3")
        
        # Get all history
        all_turns = memory.get_conversation_history()
        assert len(all_turns) == 3
        
        # Get limited history
        limited_turns = memory.get_conversation_history(max_turns=2)
        assert len(limited_turns) == 2
        assert limited_turns[-1].user_query.query_str == "Q3"
    
    def test_conversation_memory_cleanup(self):
        """Test automatic cleanup in ConversationMemory."""
        memory = ConversationMemory(max_turns=3, auto_cleanup=True)
        
        # Add more turns than the limit
        memory.add_dialog_turn("Q1", "A1")
        memory.add_dialog_turn("Q2", "A2")
        memory.add_dialog_turn("Q3", "A3")
        memory.add_dialog_turn("Q4", "A4")  # Should trigger cleanup
        
        # Check that only the most recent turns remain
        turns = memory.get_conversation_history()
        assert len(turns) == 3
        assert turns[0].user_query.query_str == "Q2"  # Q1 should be removed


class TestCompatibilityLayer:
    """Test the compatibility layer functions."""
    
    def test_create_faiss_retriever_from_config(self):
        """Test creating FAISS retriever from config."""
        config = {"top_k": 15}
        mock_embedder = Mock()
        mock_docs = [Mock()]
        
        retriever = create_faiss_retriever_from_config(
            config, mock_embedder, mock_docs
        )
        
        assert retriever is not None
        assert retriever._top_k == 15
    
    def test_create_vector_store_from_documents(self):
        """Test creating vector store from documents."""
        mock_docs = [Mock()]
        mock_docs[0].vector = [1.0, 2.0, 3.0]
        
        vector_store = create_vector_store_from_documents(mock_docs)
        
        assert vector_store is not None
        assert len(vector_store._documents) == 1
    
    def test_create_memory_component(self):
        """Test creating memory component."""
        memory = create_memory_component()
        
        assert memory is not None
        assert isinstance(memory, ConversationMemory)
    
    def test_validate_and_filter_embeddings(self):
        """Test embedding validation and filtering."""
        # Mock documents with mixed embedding sizes
        mock_doc1 = Mock()
        mock_doc1.vector = [1.0, 2.0, 3.0]
        mock_doc2 = Mock()
        mock_doc2.vector = [4.0, 5.0, 6.0]
        mock_doc3 = Mock()
        mock_doc3.vector = [7.0, 8.0]  # Different size
        
        documents = [mock_doc1, mock_doc2, mock_doc3]
        
        result = validate_and_filter_embeddings(documents)
        
        # Should filter out the inconsistent document
        assert len(result) == 2


if __name__ == "__main__":
    pytest.main([__file__])
