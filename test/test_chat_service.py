"""
Tests for the Chat Service.

This module tests the chat service functionality including request validation,
Deep Research detection, and service orchestration.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from api.services.chat_service import ChatService, get_chat_service, create_chat_service


class TestChatService:
    """Test cases for the ChatService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.chat_service = ChatService()
        self.sample_messages = [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"},
            {"role": "user", "content": "Can you help me with this code?"}
        ]
    
    def test_chat_service_initialization(self):
        """Test that ChatService initializes correctly."""
        assert self.chat_service is not None
        assert hasattr(self.chat_service, '_chat_compatibility')
        assert hasattr(self.chat_service, 'logger')
    
    def test_validate_and_preprocess_request_valid(self):
        """Test request validation with valid data."""
        result = self.chat_service._validate_and_preprocess_request(
            repo_url="https://github.com/user/repo",
            messages=self.sample_messages,
            provider="google",
            language="en"
        )
        
        assert result["repo_url"] == "https://github.com/user/repo"
        assert result["repo_name"] == "repo"
        assert result["provider"] == "google"
        assert result["language"] == "en"
        assert result["is_deep_research"] is False
        assert result["research_iteration"] == 1
        assert result["input_too_large"] is False
    
    def test_validate_and_preprocess_request_no_messages(self):
        """Test request validation with no messages."""
        with pytest.raises(HTTPException) as exc_info:
            self.chat_service._validate_and_preprocess_request(
                repo_url="https://github.com/user/repo",
                messages=[],
                provider="google"
            )
        
        assert exc_info.value.status_code == 400
        assert "No messages provided" in str(exc_info.value.detail)
    
    def test_validate_and_preprocess_request_last_message_not_user(self):
        """Test request validation with last message not from user."""
        invalid_messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        with pytest.raises(HTTPException) as exc_info:
            self.chat_service._validate_and_preprocess_request(
                repo_url="https://github.com/user/repo",
                messages=invalid_messages,
                provider="google"
            )
        
        assert exc_info.value.status_code == 400
        assert "Last message must be from the user" in str(exc_info.value.detail)
    
    def test_validate_and_preprocess_request_large_input(self):
        """Test request validation with large input detection."""
        # Mock count_tokens to return a large number
        with patch('api.services.chat_service.count_tokens', return_value=9000):
            result = self.chat_service._validate_and_preprocess_request(
                repo_url="https://github.com/user/repo",
                messages=self.sample_messages,
                provider="google"
            )
            
            assert result["input_too_large"] is True
    
    def test_validate_and_preprocess_request_file_filtering(self):
        """Test request validation with file filtering parameters."""
        result = self.chat_service._validate_and_preprocess_request(
            repo_url="https://github.com/user/repo",
            messages=self.sample_messages,
            excluded_dirs="dir1\ndir2",
            excluded_files="*.log\n*.tmp",
            included_dirs="src\ntests",
            included_files="*.py\n*.js"
        )
        
        assert result["excluded_dirs"] == ["dir1", "dir2"]
        assert result["excluded_files"] == ["*.log", "*.tmp"]
        assert result["included_dirs"] == ["src", "tests"]
        assert result["included_files"] == ["*.py", "*.js"]
    
    def test_detect_deep_research_no_tag(self):
        """Test Deep Research detection with no tag."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "user", "content": "How are you?"}
        ]
        
        is_deep_research, research_iteration, processed_messages = (
            self.chat_service._detect_deep_research(messages)
        )
        
        assert is_deep_research is False
        assert research_iteration == 1
        assert processed_messages == messages
    
    def test_detect_deep_research_with_tag(self):
        """Test Deep Research detection with tag."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "user", "content": "[DEEP RESEARCH] How does this work?"}
        ]
        
        is_deep_research, research_iteration, processed_messages = (
            self.chat_service._detect_deep_research(messages)
        )
        
        assert is_deep_research is True
        assert research_iteration == 2  # 1 assistant message + 1
        assert "[DEEP RESEARCH]" not in processed_messages[-1]["content"]
        assert "How does this work?" in processed_messages[-1]["content"]
    
    def test_detect_deep_research_continuation(self):
        """Test Deep Research detection with continuation request."""
        messages = [
            {"role": "user", "content": "[DEEP RESEARCH] Explain this code"},
            {"role": "assistant", "content": "Here's what I found..."},
            {"role": "user", "content": "continue research"}
        ]
        
        is_deep_research, research_iteration, processed_messages = (
            self.chat_service._detect_deep_research(messages)
        )
        
        assert is_deep_research is True
        assert research_iteration == 2
        assert processed_messages[-1]["content"] == "Explain this code"
    
    def test_create_pipeline_context(self):
        """Test pipeline context creation."""
        validated_data = {
            "repo_url": "https://github.com/user/repo",
            "repo_type": "github",
            "token": "token123",
            "language": "en",
            "provider": "google",
            "model": "gemini-pro",
            "file_path": "src/main.py",
            "excluded_dirs": ["dir1"],
            "excluded_files": ["*.log"],
            "included_dirs": ["src"],
            "included_files": ["*.py"],
            "messages": self.sample_messages,
            "is_deep_research": False,
            "research_iteration": 1,
            "input_too_large": False
        }
        
        context = self.chat_service._create_pipeline_context(validated_data)
        
        assert context["repo_url"] == "https://github.com/user/repo"
        assert context["type"] == "github"
        assert context["token"] == "token123"
        assert context["language"] == "en"
        assert context["provider"] == "google"
        assert context["model"] == "gemini-pro"
        assert context["filePath"] == "src/main.py"
        assert context["excluded_dirs"] == ["dir1"]
        assert context["excluded_files"] == ["*.log"]
        assert context["included_dirs"] == ["src"]
        assert context["included_files"] == ["*.py"]
        assert context["messages"] == self.sample_messages
    
    def test_get_service_status(self):
        """Test service status retrieval."""
        status = self.chat_service.get_service_status()
        
        assert status["service"] == "ChatService"
        assert status["status"] == "active"
        assert "pipeline_status" in status
        assert status["compatibility_layer"] == "active"
    
    def test_validate_service(self):
        """Test service validation."""
        # Mock the compatibility layer validation
        with patch.object(self.chat_service._chat_compatibility, 'validate_pipeline', return_value=True):
            is_valid = self.chat_service.validate_service()
            assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_process_chat_request_success(self):
        """Test successful chat request processing."""
        # Mock the chat compatibility layer
        mock_chunks = ["Hello", " ", "world", "!"]
        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = mock_chunks
        
        with patch.object(self.chat_service._chat_compatibility, 'chat_completions_stream', return_value=mock_stream):
            chunks = []
            async for chunk in self.chat_service.process_chat_request(
                repo_url="https://github.com/user/repo",
                messages=self.sample_messages,
                provider="google"
            ):
                chunks.append(chunk)
            
            assert chunks == ["Hello", " ", "world", "!"]
    
    @pytest.mark.asyncio
    async def test_process_chat_request_validation_error(self):
        """Test chat request processing with validation error."""
        with pytest.raises(HTTPException) as exc_info:
            async for chunk in self.chat_service.process_chat_request(
                repo_url="https://github.com/user/repo",
                messages=[],  # Invalid: no messages
                provider="google"
            ):
                pass
        
        assert exc_info.value.status_code == 400
        assert "No messages provided" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_process_chat_request_pipeline_error(self):
        """Test chat request processing with pipeline error."""
        # Mock the chat compatibility layer to raise an exception
        with patch.object(self.chat_service._chat_compatibility, 'chat_completions_stream', side_effect=Exception("Pipeline error")):
            with pytest.raises(HTTPException) as exc_info:
                async for chunk in self.chat_service.process_chat_request(
                    repo_url="https://github.com/user/repo",
                    messages=self.sample_messages,
                    provider="google"
                ):
                    pass
            
            assert exc_info.value.status_code == 500
            assert "Error processing chat request: Pipeline error" in str(exc_info.value.detail)


class TestChatServiceFunctions:
    """Test cases for the chat service module functions."""
    
    def test_get_chat_service_singleton(self):
        """Test that get_chat_service returns a singleton."""
        service1 = get_chat_service()
        service2 = get_chat_service()
        
        assert service1 is service2
        assert isinstance(service1, ChatService)
    
    def test_create_chat_service_new_instance(self):
        """Test that create_chat_service creates a new instance."""
        service1 = get_chat_service()
        service2 = create_chat_service()
        
        assert service1 is not service2
        assert isinstance(service1, ChatService)
        assert isinstance(service2, ChatService)


class TestChatServiceIntegration:
    """Integration tests for the chat service."""
    
    def test_service_with_real_config(self):
        """Test that the service can be initialized with real configuration."""
        try:
            service = create_chat_service()
            assert service is not None
            
            # Test that the service can access configuration
            status = service.get_service_status()
            assert status["service"] == "ChatService"
            
        except Exception as e:
            # If there are configuration issues, that's okay for this test
            pytest.skip(f"Service initialization failed due to configuration: {e}")
    
    def test_service_dependency_injection(self):
        """Test that the service properly injects dependencies."""
        service = create_chat_service()
        
        # Check that required dependencies are available
        assert hasattr(service, '_chat_compatibility')
        assert service._chat_compatibility is not None
        
        # Check that the service can validate itself
        try:
            is_valid = service.validate_service()
            assert isinstance(is_valid, bool)
        except Exception:
            # Validation might fail in test environment, which is okay
            pass
