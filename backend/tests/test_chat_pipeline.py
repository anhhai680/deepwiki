"""
Tests for the chat pipeline components.

This module tests all aspects of the chat pipeline including
context management, pipeline steps, and streaming responses.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import AsyncGenerator

from backend.pipelines.chat.chat_context import ChatPipelineContext
from backend.pipelines.chat.steps import (
    RequestValidationStep,
    ConversationAnalysisStep,
    SystemPromptGenerationStep,
    ContextPreparationStep,
    PromptAssemblyStep
)
from backend.pipelines.chat.response_generation import ResponseGenerationStep
from backend.pipelines.chat.chat_pipeline import ChatPipeline, create_chat_pipeline
from backend.pipelines.chat.compatibility import ChatCompatibility, get_chat_compatibility


class TestChatPipelineContext:
    """Test the chat pipeline context class."""
    
    def test_context_creation(self):
        """Test creating a chat pipeline context."""
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            language="en"
        )
        
        assert context.repo_url == "https://github.com/test/repo"
        assert context.provider == "google"
        assert context.language == "en"
        assert context.start_time is not None
        assert context.errors == []
        assert context.warnings == []
    
    def test_context_validation_success(self):
        """Test successful context validation."""
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "test"}]
        )
        
        assert context.validate() is True
    
    def test_context_validation_failure(self):
        """Test context validation failure."""
        context = ChatPipelineContext()
        
        assert context.validate() is False
        # The validation stops at the first error, so we only get one error
        assert len(context.errors) == 1  # repo_url is checked first
    
    def test_error_handling(self):
        """Test error handling in context."""
        context = ChatPipelineContext()
        context.add_error("Test error")
        
        assert len(context.errors) == 1
        assert "Test error" in context.errors[0]
    
    def test_warning_handling(self):
        """Test warning handling in context."""
        context = ChatPipelineContext()
        context.add_warning("Test warning")
        
        assert len(context.warnings) == 1
        assert "Test warning" in context.warnings[0]
    
    def test_context_completion(self):
        """Test marking context as completed."""
        context = ChatPipelineContext()
        context.mark_completed()
        
        assert context.end_time is not None
        assert context.processing_time is not None
        assert context.processing_time > 0
    
    def test_status_summary(self):
        """Test getting context status summary."""
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "test"}]
        )
        context.mark_completed()
        
        summary = context.get_status_summary()
        assert summary["status"] == "completed"
        assert summary["errors_count"] == 0
        assert summary["warnings_count"] == 0


class TestRequestValidationStep:
    """Test the request validation step."""
    
    def test_step_creation(self):
        """Test creating the request validation step."""
        step = RequestValidationStep()
        assert step.name == "RequestValidation"
    
    def test_successful_validation(self):
        """Test successful request validation."""
        step = RequestValidationStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "test"}]
        )
        
        with patch('backend.pipelines.chat.steps.get_model_config') as mock_get_config:
            mock_get_config.return_value = {
                "model_kwargs": {"temperature": 0.7, "top_p": 0.8}
            }
            
            result = step.execute(context)
            
            assert result.errors == []
            # Check that the model config contains the expected values
            assert result.model_config["temperature"] == 0.7
            assert result.model_config["top_p"] == 0.8
    
    def test_large_input_detection(self):
        """Test detection of large input."""
        step = RequestValidationStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "x" * 10000}]
        )
        
        with patch('backend.pipelines.chat.steps.count_tokens') as mock_count:
            mock_count.return_value = 9000
            
            with patch('backend.pipelines.chat.steps.get_model_config') as mock_get_config:
                mock_get_config.return_value = {
                    "model_kwargs": {"temperature": 0.7}
                }
                
                result = step.execute(context)
                
                assert result.input_too_large is True
    
    def test_file_filtering_processing(self):
        """Test processing of file filtering parameters."""
        step = RequestValidationStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "test"}],
            excluded_dirs=["dir1", "dir2"],
            excluded_files=["*.log", "*.tmp"]
        )
        
        with patch('backend.core.config.settings.get_model_config') as mock_get_config:
            mock_get_config.return_value = {
                "model_kwargs": {"temperature": 0.7}
            }
            
            result = step.execute(context)
            
            assert result.excluded_dirs == ["dir1", "dir2"]
            assert result.excluded_files == ["*.log", "*.tmp"]


class TestConversationAnalysisStep:
    """Test the conversation analysis step."""
    
    def test_step_creation(self):
        """Test creating the conversation analysis step."""
        step = ConversationAnalysisStep()
        assert step.name == "ConversationAnalysis"
    
    def test_conversation_history_building(self):
        """Test building conversation history."""
        step = ConversationAnalysisStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"},
                {"role": "user", "content": "How are you?"}
            ]
        )
        
        result = step.execute(context)
        
        assert "Hello" in result.conversation_history
        assert "Hi there" in result.conversation_history
        assert result.is_deep_research is False
    
    def test_deep_research_detection(self):
        """Test detection of deep research requests."""
        step = ConversationAnalysisStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[
                {"role": "user", "content": "[DEEP RESEARCH] Tell me about AI"}
            ]
        )
        
        result = step.execute(context)
        
        assert result.is_deep_research is True
        assert result.research_iteration == 1
        assert "[DEEP RESEARCH]" not in result.messages[0]["content"]
    
    def test_research_iteration_counting(self):
        """Test counting of research iterations."""
        step = ConversationAnalysisStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[
                {"role": "user", "content": "[DEEP RESEARCH] Tell me about AI"},
                {"role": "assistant", "content": "AI is..."},
                {"role": "user", "content": "[DEEP RESEARCH] Continue research"}
            ]
        )
        
        result = step.execute(context)
        
        assert result.is_deep_research is True
        assert result.research_iteration == 2


class TestSystemPromptGenerationStep:
    """Test the system prompt generation step."""
    
    def test_step_creation(self):
        """Test creating the system prompt generation step."""
        step = SystemPromptGenerationStep()
        assert step.name == "SystemPromptGeneration"
    
    def test_simple_chat_prompt_generation(self):
        """Test generation of simple chat system prompt."""
        step = SystemPromptGenerationStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            repo_type="github",
            language="en",
            is_deep_research=False
        )
        
        with patch('backend.core.config.settings.configs') as mock_configs:
            mock_configs.return_value = {
                "lang_config": {
                    "supported_languages": {"en": "English"}
                }
            }
            
            result = step.execute(context)
            
            assert result.system_prompt
            assert "github" in result.system_prompt
            assert "test/repo" in result.system_prompt
    
    def test_deep_research_prompt_generation(self):
        """Test generation of deep research system prompt."""
        step = SystemPromptGenerationStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            repo_type="github",
            language="en",
            is_deep_research=True,
            research_iteration=1
        )
        
        with patch('backend.core.config.settings.configs') as mock_configs:
            mock_configs.return_value = {
                "lang_config": {
                    "supported_languages": {"en": "English"}
                }
            }
            
            result = step.execute(context)
            
            assert result.system_prompt
            assert "github" in result.system_prompt
            assert "test/repo" in result.system_prompt


class TestContextPreparationStep:
    """Test the context preparation step."""
    
    def test_step_creation(self):
        """Test creating the context preparation step."""
        step = ContextPreparationStep()
        assert step.name == "ContextPreparation"
    
    def test_context_preparation_with_rag(self):
        """Test context preparation with RAG retrieval."""
        step = ContextPreparationStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "test"}],
            input_too_large=False
        )
        
        # Mock RAG and file content retrieval
        with patch('backend.pipelines.rag.create_rag') as mock_create_rag:
            mock_rag = Mock()
            mock_create_rag.return_value = mock_rag
            
            # Mock documents
            mock_doc = Mock()
            mock_doc.text = "test content"
            mock_doc.meta_data = {"file_path": "test.py"}
            
            mock_rag.call.return_value = [Mock(documents=[mock_doc])]
            
            with patch('backend.utils.file_utils.get_file_content') as mock_get_file:
                mock_get_file.return_value = "file content"
                
                result = step.execute(context)
                
                assert result.context_text
                assert "test.py" in result.context_text
                assert "test content" in result.context_text
    
    def test_context_preparation_without_rag(self):
        """Test context preparation without RAG (input too large)."""
        step = ContextPreparationStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "test"}],
            input_too_large=True
        )
        
        result = step.execute(context)
        
        assert result.context_text == ""
        assert len(result.warnings) == 0  # No RAG attempted


class TestPromptAssemblyStep:
    """Test the prompt assembly step."""
    
    def test_step_creation(self):
        """Test creating the prompt assembly step."""
        step = PromptAssemblyStep()
        assert step.name == "PromptAssembly"
    
    def test_prompt_assembly_with_context(self):
        """Test assembling prompt with context."""
        step = PromptAssemblyStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "test query"}],
            system_prompt="System prompt",
            context_text="Context content",
            conversation_history="<turn>\n<user>Hello</user>\n<assistant>Hi</assistant>\n</turn>",
            file_content="file content",
            file_path="test.py"
        )
        
        result = step.execute(context)
        
        assert result.final_prompt
        assert "System prompt" in result.final_prompt
        assert "Context content" in result.final_prompt
        assert "test query" in result.final_prompt
        assert "Hello" in result.final_prompt
        assert "Hi" in result.final_prompt
        assert "file content" in result.final_prompt
    
    def test_prompt_assembly_without_context(self):
        """Test assembling prompt without context."""
        step = PromptAssemblyStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "test query"}],
            system_prompt="System prompt",
            context_text="",
            conversation_history=""
        )
        
        result = step.execute(context)
        
        assert result.final_prompt
        assert "System prompt" in result.final_prompt
        assert "test query" in result.final_prompt
        assert "Answering without retrieval augmentation" in result.final_prompt
    
    def test_ollama_prompt_modification(self):
        """Test Ollama-specific prompt modification."""
        step = PromptAssemblyStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="ollama",
            messages=[{"role": "user", "content": "test query"}],
            system_prompt="System prompt"
        )
        
        result = step.execute(context)
        
        assert result.final_prompt
        assert " /no_think" in result.final_prompt


class TestResponseGenerationStep:
    """Test the response generation step."""
    
    def test_step_creation(self):
        """Test creating the response generation step."""
        step = ResponseGenerationStep()
        assert step.name == "ResponseGeneration"
    
    def test_step_execution(self):
        """Test step execution."""
        step = ResponseGenerationStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "test"}]
        )
        
        result = step.execute(context)
        
        assert result == context
    
    @pytest.mark.asyncio
    async def test_google_response_generation(self):
        """Test Google Generative AI response generation."""
        step = ResponseGenerationStep()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "test"}],
            final_prompt="Test prompt",
            model_config={"model": "gemini-pro", "temperature": 0.7, "top_p": 0.8, "top_k": 40}
        )
        
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model_class.return_value = mock_model
            
            mock_chunk = Mock()
            mock_chunk.text = "Generated response"
            mock_model.generate_content.return_value = [mock_chunk]
            
            response_generator = step._generate_google_response(context)
            response_chunks = [chunk async for chunk in response_generator]
            
            assert response_chunks == ["Generated response"]
            mock_model.generate_content.assert_called_once_with("Test prompt", stream=True)


class TestChatPipeline:
    """Test the main chat pipeline."""
    
    def test_pipeline_creation(self):
        """Test creating a chat pipeline."""
        pipeline = create_chat_pipeline()
        assert pipeline.name == "ChatPipeline"
        assert len(pipeline.steps) == 6
    
    def test_pipeline_validation(self):
        """Test pipeline validation."""
        pipeline = create_chat_pipeline()
        assert pipeline.validate_pipeline() is True
    
    def test_pipeline_execution(self):
        """Test pipeline execution."""
        pipeline = create_chat_pipeline()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "test"}]
        )
        
        # Mock the steps to avoid actual execution
        with patch.object(pipeline.steps[0], 'execute') as mock_execute:
            mock_execute.return_value = context
            
            result = pipeline.execute(context)
            
            assert result == context
            assert result.end_time is not None
    
    def test_context_creation_from_request(self):
        """Test creating context from request data."""
        pipeline = create_chat_pipeline()
        request_data = {
            "repo_url": "https://github.com/test/repo",
            "provider": "google",
            "messages": [{"role": "user", "content": "test"}]
        }
        
        context = pipeline.create_context_from_request(request_data)
        
        assert context.repo_url == "https://github.com/test/repo"
        assert context.provider == "google"
        assert len(context.messages) == 1
        assert context.messages[0]["role"] == "user"
        assert context.messages[0]["content"] == "test"
    
    def test_pipeline_status(self):
        """Test getting pipeline status."""
        pipeline = create_chat_pipeline()
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "test"}]
        )
        pipeline.set_context(context)
        
        status = pipeline.get_pipeline_status()
        
        assert status["pipeline_name"] == "ChatPipeline"
        assert status["steps_count"] == 6
        assert "context_status" in status


class TestChatCompatibility:
    """Test the chat compatibility layer."""
    
    def test_compatibility_creation(self):
        """Test creating chat compatibility instance."""
        compatibility = ChatCompatibility()
        assert compatibility.pipeline is not None
        assert compatibility.pipeline.name == "ChatPipeline"
    
    def test_get_chat_compatibility_singleton(self):
        """Test that get_chat_compatibility returns a singleton."""
        compatibility1 = get_chat_compatibility()
        compatibility2 = get_chat_compatibility()
        
        assert compatibility1 is compatibility2
    
    def test_pipeline_status_access(self):
        """Test accessing pipeline status through compatibility."""
        compatibility = get_chat_compatibility()
        # Set a context on the pipeline to test status access
        context = ChatPipelineContext(
            repo_url="https://github.com/test/repo",
            provider="google",
            messages=[{"role": "user", "content": "test"}]
        )
        compatibility.pipeline.set_context(context)
        
        status = compatibility.get_pipeline_status()
        
        assert "pipeline_name" in status
        assert status["pipeline_name"] == "ChatPipeline"
    
    def test_pipeline_validation_access(self):
        """Test accessing pipeline validation through compatibility."""
        compatibility = get_chat_compatibility()
        is_valid = compatibility.validate_pipeline()
        
        assert is_valid is True


if __name__ == "__main__":
    pytest.main([__file__])
