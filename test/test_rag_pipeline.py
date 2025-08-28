"""
Test suite for RAG Pipeline implementation.

This module tests the complete RAG pipeline including all steps,
context management, and compatibility layer.
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from backend.pipelines.rag.rag_pipeline import RAGPipeline
from backend.pipelines.rag.rag_context import RAGPipelineContext
from backend.pipelines.rag.steps import (
    RepositoryPreparationStep,
    RetrieverInitializationStep,
    DocumentRetrievalStep,
    ResponseGenerationStep,
    MemoryUpdateStep
)
from backend.pipelines.rag.compatibility import RAGCompatibility, create_rag
from backend.pipelines.base import PipelineStep, PipelineContext

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)

class TestRAGPipelineContext:
    """Test RAG pipeline context management."""
    
    def test_context_initialization(self):
        """Test that context initializes correctly."""
        context = RAGPipelineContext()
        
        assert context.pipeline_id is not None
        assert context.step_name == ""
        assert context.step_index == 0
        assert context.repo_url_or_path == ""
        assert context.repo_type == "github"
        assert context.transformed_docs == []
        assert context.user_query == ""
        assert context.language == "en"
        assert context.errors == []
        assert context.warnings == []
    
    def test_context_update(self):
        """Test context update functionality."""
        context = RAGPipelineContext()
        
        context.update(
            repo_url_or_path="https://github.com/test/repo",
            user_query="test query",
            language="es"
        )
        
        assert context.repo_url_or_path == "https://github.com/test/repo"
        assert context.user_query == "test query"
        assert context.language == "es"
    
    def test_context_error_handling(self):
        """Test context error and warning handling."""
        context = RAGPipelineContext()
        
        context.add_error("Test error")
        context.add_warning("Test warning")
        
        assert context.has_errors()
        assert context.has_warnings()
        assert context.get_last_error() == "Test error"
        assert context.get_last_warning() == "Test warning"
        assert len(context.errors) == 1
        assert len(context.warnings) == 1
    
    def test_context_validation(self):
        """Test context validation methods."""
        context = RAGPipelineContext()
        
        # Test repository validation
        assert not context.validate_repository_config()
        context.repo_url_or_path = "https://github.com/test/repo"
        assert context.validate_repository_config()
        
        # Test query validation
        assert not context.validate_query_config()
        context.user_query = "test query"
        context.language = "en"
        assert context.validate_query_config()
        
        # Test document validation
        assert not context.validate_documents()
        context.transformed_docs = [Mock()]
        assert context.validate_documents()
    
    def test_context_step_management(self):
        """Test context step management."""
        context = RAGPipelineContext()
        
        context.set_step("test_step", 1)
        assert context.step_name == "test_step"
        assert context.step_index == 1
    
    def test_context_timing(self):
        """Test context timing functionality."""
        context = RAGPipelineContext()
        
        context.add_step_timing("step1", 1.5)
        context.add_step_timing("step2", 2.0)
        
        assert context.get_step_duration("step1") == 1.5
        assert context.get_step_duration("step2") == 2.0
        assert context.get_total_duration() == 3.5
    
    def test_context_summary(self):
        """Test context summary generation."""
        context = RAGPipelineContext()
        context.repo_url_or_path = "https://github.com/test/repo"
        context.user_query = "test query"
        context.transformed_docs = [Mock(), Mock()]
        
        summary = context.get_context_summary()
        
        assert "pipeline_id" in summary
        assert "repository" in summary
        assert "query" in summary
        assert "documents_count" in summary
        assert summary["documents_count"] == 2
    
    def test_context_reset(self):
        """Test context reset functionality."""
        context = RAGPipelineContext()
        context.repo_url_or_path = "https://github.com/test/repo"
        context.user_query = "test query"
        mock_doc = Mock()
        context.transformed_docs = [mock_doc]
        
        context.reset_for_new_query()
        
        # Repository state should be preserved
        assert context.repo_url_or_path == "https://github.com/test/repo"
        assert len(context.transformed_docs) == 1  # Check length instead of exact object
        
        # Query state should be reset
        assert context.user_query == ""
        assert context.language == "en"
    
    def test_context_clone(self):
        """Test context cloning functionality."""
        context = RAGPipelineContext()
        context.repo_url_or_path = "https://github.com/test/repo"
        context.transformed_docs = [Mock()]
        
        cloned = context.clone()
        
        assert cloned.repo_url_or_path == context.repo_url_or_path
        assert cloned.transformed_docs == context.transformed_docs
        assert cloned.pipeline_id != context.pipeline_id  # Should have new ID

class TestRAGPipelineSteps:
    """Test individual RAG pipeline steps."""
    
    def test_repository_preparation_step(self):
        """Test repository preparation step."""
        step = RepositoryPreparationStep()
        
        # Test validation
        assert step.validate_input("https://github.com/test/repo")
        assert not step.validate_input("")
        assert not step.validate_input(None)
        
        # Test output validation
        mock_docs = [Mock(), Mock()]
        assert step.validate_output(mock_docs)
        assert not step.validate_output([])
        assert not step.validate_output(None)
    
    def test_retriever_initialization_step(self):
        """Test retriever initialization step."""
        step = RetrieverInitializationStep()
        
        # Test validation
        mock_docs = [Mock(), Mock()]
        assert step.validate_input(mock_docs)
        assert not step.validate_input([])
        assert not step.validate_input(None)
        
        # Test output validation - mock a FAISS retriever
        from backend.components.retriever.faiss_retriever import FAISSRetriever
        mock_retriever = Mock(spec=FAISSRetriever)
        assert step.validate_output(mock_retriever)
        assert not step.validate_output(None)
    
    def test_document_retrieval_step(self):
        """Test document retrieval step."""
        step = DocumentRetrievalStep()
        
        # Test validation
        from backend.components.retriever.faiss_retriever import FAISSRetriever
        mock_retriever = Mock(spec=FAISSRetriever)
        valid_input = ("test query", mock_retriever)
        assert step.validate_input(valid_input)
        assert not step.validate_input(("", mock_retriever))
        assert not step.validate_input(("query", None))
        assert not step.validate_input("invalid")
        
        # Test output validation
        mock_docs = [Mock(), Mock()]
        assert step.validate_output(mock_docs)
        assert step.validate_output([])
        assert not step.validate_output(None)
    
    def test_response_generation_step(self):
        """Test response generation step."""
        step = ResponseGenerationStep()
        
        # Test validation
        mock_docs = [Mock(), Mock()]
        assert step.validate_input(mock_docs)
        assert not step.validate_input([])
        assert not step.validate_input(None)
        
        # Test output validation
        valid_output = {"answer": "test answer", "rationale": "test rationale"}
        assert step.validate_output(valid_output)
        assert not step.validate_output({"answer": "test"})  # Missing rationale
        assert not step.validate_output({"rationale": "test"})  # Missing answer
        assert not step.validate_output(None)
    
    def test_memory_update_step(self):
        """Test memory update step."""
        step = MemoryUpdateStep()
        
        # Test validation
        valid_input = {"answer": "test answer", "rationale": "test rationale"}
        assert step.validate_input(valid_input)
        assert not step.validate_input({"answer": "test"})  # Missing rationale
        assert not step.validate_input({"rationale": "test"})  # Missing answer
        assert not step.validate_input(None)
        
        # Test output validation
        assert step.validate_output(valid_input)
        assert not step.validate_output({"answer": "test"})  # Missing rationale
        assert not step.validate_output({"rationale": "test"})  # Missing answer
        assert not step.validate_output(None)

class TestRAGPipeline:
    """Test the main RAG pipeline."""
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        pipeline = RAGPipeline(provider="google", model="gemini-pro")
        
        assert pipeline.name == "rag_pipeline"
        assert pipeline.provider == "google"
        assert pipeline.model == "gemini-pro"
        assert len(pipeline.steps) == 5
        assert isinstance(pipeline.context, RAGPipelineContext)
    
    def test_pipeline_step_setup(self):
        """Test that pipeline steps are set up correctly."""
        pipeline = RAGPipeline()
        
        step_names = pipeline.get_step_names()
        expected_steps = [
            "repository_preparation",
            "retriever_initialization",
            "document_retrieval",
            "response_generation",
            "memory_update"
        ]
        
        assert step_names == expected_steps
    
    def test_pipeline_validation(self):
        """Test pipeline validation."""
        pipeline = RAGPipeline()
        
        # Pipeline should be valid with steps
        assert pipeline.validate_pipeline()
        
        # Pipeline should not be ready without repository
        assert not pipeline.validate_pipeline_state()
        
        # Add repository and check again
        pipeline.context.repo_url_or_path = "https://github.com/test/repo"
        pipeline.context.transformed_docs = [Mock()]
        assert pipeline.validate_pipeline_state()
    
    def test_pipeline_status(self):
        """Test pipeline status reporting."""
        pipeline = RAGPipeline(provider="openai", model="gpt-4")
        
        status = pipeline.get_pipeline_status()
        
        assert status["name"] == "rag_pipeline"
        assert status["provider"] == "openai"
        assert status["model"] == "gpt-4"
        assert "steps" in status
        assert "context" in status
        assert "has_errors" in status
        assert "has_warnings" in status
    
    def test_pipeline_error_handling(self):
        """Test pipeline error handling."""
        pipeline = RAGPipeline()
        
        # Add some errors and warnings
        pipeline.context.add_error("Test error")
        pipeline.context.add_warning("Test warning")
        
        assert pipeline.context.has_errors()
        assert pipeline.context.has_warnings()
        
        # Clear errors and warnings
        pipeline.clear_errors()
        pipeline.clear_warnings()
        
        assert not pipeline.context.has_errors()
        assert not pipeline.context.has_warnings()

class TestRAGCompatibility:
    """Test the RAG compatibility layer."""
    
    def test_compatibility_initialization(self):
        """Test compatibility wrapper initialization."""
        rag = RAGCompatibility(provider="ollama", model="llama2")
        
        assert rag.provider == "ollama"
        assert rag.model == "llama2"
        assert rag.use_s3 is False
        assert isinstance(rag.pipeline, RAGPipeline)
        assert rag.repo_url_or_path is None
        assert rag.transformed_docs == []
    
    def test_compatibility_interface(self):
        """Test that compatibility wrapper provides the expected interface."""
        rag = RAGCompatibility()
        
        # Check that required methods exist
        assert hasattr(rag, 'prepare_retriever')
        assert hasattr(rag, 'call')
        assert hasattr(rag, 'repo_url_or_path')
        assert hasattr(rag, 'transformed_docs')
        assert hasattr(rag, 'retriever')
        assert hasattr(rag, 'memory')
    
    def test_create_rag_function(self):
        """Test the create_rag convenience function."""
        rag = create_rag(provider="openai", model="gpt-4", use_s3=True)
        
        assert isinstance(rag, RAGCompatibility)
        assert rag.provider == "openai"
        assert rag.model == "gpt-4"
        assert rag.use_s3 is True

class TestPipelineIntegration:
    """Test pipeline integration and workflow."""
    
    @patch('backend.pipelines.rag.steps.repository_preparation.DatabaseManager')
    def test_pipeline_workflow(self, mock_db_manager):
        """Test the complete pipeline workflow."""
        # Mock the database manager
        mock_db = Mock()
        
        # Create mock documents with proper structure
        mock_doc1 = Mock()
        mock_doc1.vector = [0.1, 0.2, 0.3]  # Mock embedding vector
        mock_doc1.meta_data = {"file_path": "test1.py"}
        mock_doc1.text = "test content 1"
        
        mock_doc2 = Mock()
        mock_doc2.vector = [0.1, 0.2, 0.3]  # Same embedding size
        mock_doc2.meta_data = {"file_path": "test2.py"}
        mock_doc2.text = "test content 2"
        
        mock_db.prepare_database.return_value = [mock_doc1, mock_doc2]
        mock_db_manager.return_value = mock_db
        
        # Create pipeline
        pipeline = RAGPipeline(provider="google", model="gemini-pro")
        
        # Test repository preparation
        pipeline.prepare_repository("https://github.com/test/repo")
        
        assert pipeline.context.repo_url_or_path == "https://github.com/test/repo"
        assert len(pipeline.context.transformed_docs) == 2
        
        # Test pipeline state validation
        assert pipeline.validate_pipeline_state()
    
    def test_pipeline_context_flow(self):
        """Test that context flows correctly through pipeline steps."""
        context = RAGPipelineContext()
        context.repo_url_or_path = "https://github.com/test/repo"
        context.user_query = "test query"
        context.language = "en"
        
        # Simulate step execution
        context.set_step("repository_preparation", 0)
        context.add_step_timing("repository_preparation", 1.0)
        
        context.set_step("retriever_initialization", 1)
        context.add_step_timing("retriever_initialization", 0.5)
        
        # Check context state
        assert context.step_name == "retriever_initialization"
        assert context.step_index == 1
        assert context.get_total_duration() == 1.5
        assert context.get_step_duration("repository_preparation") == 1.0

if __name__ == "__main__":
    pytest.main([__file__])
