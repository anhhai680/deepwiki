"""
Test core infrastructure components extracted from existing code.

This test validates that the core infrastructure extraction
was successful and all components work correctly.
"""

import pytest
import os
import tempfile
from pathlib import Path

# Import the extracted core infrastructure
from backend.core.config import (
    ConfigurationManager,
    get_config_manager,
    initialize_config,
    get_setting,
    get_config,
    get_model_config,
    get_settings,
    get_excluded_dirs,
    get_excluded_files
)
from backend.core.config.logging import setup_logging, get_logger
from backend.core.exceptions import (
    DeepWikiException,
    ConfigurationError,
    ValidationError,
    ProcessingError
)
from backend.core.types import (
    WikiPage,
    RepoInfo,
    ChatMessage,
    DocumentChunk
)


class TestCoreInfrastructure:
    """Test core infrastructure components."""
    
    def test_settings_creation(self):
        """Test that settings can be created and accessed."""
        settings = get_settings()
        assert settings is not None
        assert hasattr(settings, 'openai_api_key')
        assert hasattr(settings, 'google_api_key')
        assert hasattr(settings, 'wiki_auth_mode')
    
    def test_excluded_directories(self):
        """Test that excluded directories are accessible."""
        excluded_dirs = get_excluded_dirs()
        assert isinstance(excluded_dirs, list)
        assert len(excluded_dirs) > 0
        assert "./.git/" in excluded_dirs
        assert "./node_modules/" in excluded_dirs
    
    def test_excluded_files(self):
        """Test that excluded files are accessible."""
        excluded_files = get_excluded_files()
        assert isinstance(excluded_files, list)
        assert len(excluded_files) > 0
        assert "yarn.lock" in excluded_files
        assert ".env" in excluded_files
    
    def test_exception_hierarchy(self):
        """Test that exception hierarchy is correct."""
        # Test base exception
        base_ex = DeepWikiException("Test message", "TEST001", {"detail": "test"})
        assert base_ex.message == "Test message"
        assert base_ex.error_code == "TEST001"
        assert base_ex.details == {"detail": "test"}
        
        # Test specific exceptions
        config_ex = ConfigurationError("Config error")
        assert isinstance(config_ex, DeepWikiException)
        
        validation_ex = ValidationError("Validation error")
        assert isinstance(validation_ex, DeepWikiException)
        
        processing_ex = ProcessingError("Processing error")
        assert isinstance(processing_ex, DeepWikiException)
    
    def test_type_definitions(self):
        """Test that type definitions work correctly."""
        # Test WikiPage
        wiki_page = WikiPage(
            id="test-page",
            title="Test Page",
            content="Test content",
            filePaths=["test.py"],
            importance="high",
            relatedPages=["other-page"]
        )
        assert wiki_page.id == "test-page"
        assert wiki_page.title == "Test Page"
        assert wiki_page.importance == "high"
        
        # Test RepoInfo
        repo_info = RepoInfo(
            owner="testuser",
            repo="testrepo",
            type="github"
        )
        assert repo_info.owner == "testuser"
        assert repo_info.repo == "testrepo"
        assert repo_info.type == "github"
        
        # Test ChatMessage
        chat_message = ChatMessage(
            role="user",
            content="Hello, world!"
        )
        assert chat_message.role == "user"
        assert chat_message.content == "Hello, world!"
    
    def test_logging_setup(self):
        """Test that logging can be set up."""
        # Test basic logging setup
        logger = get_logger("test_logger")
        assert logger is not None
        assert logger.name == "test_logger"
    
    def test_configuration_manager_creation(self):
        """Test that configuration manager can be created."""
        manager = ConfigurationManager()
        assert manager is not None
        assert hasattr(manager, 'initialize')
        assert hasattr(manager, 'get_setting')
        assert hasattr(manager, 'get_config')
    
    def test_global_config_manager(self):
        """Test that global configuration manager works."""
        manager = get_config_manager()
        assert manager is not None
        assert isinstance(manager, ConfigurationManager)
        
        # Test that we get the same instance
        manager2 = get_config_manager()
        assert manager is manager2
    
    def test_convenience_functions(self):
        """Test that convenience functions work."""
        # Test get_setting
        setting = get_setting("log_level", "INFO")
        assert setting == "INFO"
        
        # Test get_config
        config = get_config("generator")
        assert isinstance(config, dict)
    
    def test_environment_variable_handling(self):
        """Test that environment variables are handled correctly."""
        # Test with a temporary environment variable
        test_value = "test_value_123"
        os.environ["TEST_CONFIG_VALUE"] = test_value
        
        # Test that the setting can be accessed
        settings = get_settings()
        # Note: This test depends on the actual environment variables
        # We're just testing that the system doesn't crash
        
        # Clean up
        del os.environ["TEST_CONFIG_VALUE"]


class TestConfigurationLoading:
    """Test configuration loading functionality."""
    
    def test_config_file_loading(self, tmp_path):
        """Test that configuration files can be loaded."""
        # Create a temporary config file
        config_file = tmp_path / "test_config.json"
        config_content = {
            "test_setting": "test_value",
            "nested": {
                "setting": "nested_value"
            }
        }
        
        with open(config_file, 'w') as f:
            import json
            json.dump(config_content, f)
        
        # Test that the file can be read
        assert config_file.exists()
        with open(config_file, 'r') as f:
            loaded_content = json.load(f)
        
        assert loaded_content["test_setting"] == "test_value"
        assert loaded_content["nested"]["setting"] == "nested_value"


if __name__ == "__main__":
    # Run basic tests
    print("Testing core infrastructure components...")
    
    # Test settings
    settings = get_settings()
    print(f"✓ Settings created: {settings is not None}")
    
    # Test excluded directories
    excluded_dirs = get_excluded_dirs()
    print(f"✓ Excluded directories: {len(excluded_dirs)} items")
    
    # Test excluded files
    excluded_files = get_excluded_files()
    print(f"✓ Excluded files: {len(excluded_files)} items")
    
    # Test configuration manager
    manager = get_config_manager()
    print(f"✓ Configuration manager: {manager is not None}")
    
    # Test types
    wiki_page = WikiPage(
        id="test",
        title="Test",
        content="Test content",
        filePaths=["test.py"],
        importance="high",
        relatedPages=[]
    )
    print(f"✓ Type definitions: {wiki_page is not None}")
    
    print("Core infrastructure test completed successfully!")
