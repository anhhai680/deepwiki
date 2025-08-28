"""
Test generator components functionality.

This test file verifies that all generator components can be imported
and basic functionality works correctly.
"""

import pytest
import os
import sys

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_import_generator_base():
    """Test that the base generator module can be imported."""
    try:
        from backend.components.generator.base import BaseGenerator, ModelType, GeneratorOutput
        assert BaseGenerator is not None
        assert ModelType is not None
        assert GeneratorOutput is not None
        print("✅ Successfully imported generator base classes")
    except ImportError as e:
        pytest.fail(f"Failed to import generator base classes: {e}")


def test_import_generator_providers():
    """Test that all generator providers can be imported."""
    try:
        from backend.components.generator.providers.openai_generator import OpenAIGenerator
        from backend.components.generator.providers.azure_generator import AzureAIGenerator
        from backend.components.generator.providers.bedrock_generator import BedrockGenerator
        from backend.components.generator.providers.dashscope_generator import DashScopeGenerator
        from backend.components.generator.providers.openrouter_generator import OpenRouterGenerator
        from backend.components.generator.providers.ollama_generator import OllamaGenerator
        
        assert OpenAIGenerator is not None
        assert AzureAIGenerator is not None
        assert BedrockGenerator is not None
        assert DashScopeGenerator is not None
        assert OpenRouterGenerator is not None
        assert OllamaGenerator is not None
        
        print("✅ Successfully imported all generator providers")
    except ImportError as e:
        pytest.fail(f"Failed to import generator providers: {e}")


def test_import_generator_manager():
    """Test that the generator manager can be imported."""
    try:
        from backend.components.generator.generator_manager import (
            GeneratorManager, 
            ProviderType,
            get_generator_manager,
            create_generator,
            get_generator
        )
        assert GeneratorManager is not None
        assert ProviderType is not None
        assert get_generator_manager is not None
        assert create_generator is not None
        assert get_generator is not None
        print("✅ Successfully imported generator manager")
    except ImportError as e:
        pytest.fail(f"Failed to import generator manager: {e}")


def test_import_generator_module():
    """Test that the main generator module can be imported."""
    try:
        from backend.components.generator import (
            BaseGenerator,
            ModelType,
            GeneratorOutput,
            GeneratorManager,
            ProviderType,
            OpenAIGenerator,
            AzureAIGenerator,
            BedrockGenerator,
            DashScopeGenerator,
            OpenRouterGenerator,
            OllamaGenerator
        )
        print("✅ Successfully imported main generator module")
    except ImportError as e:
        pytest.fail(f"Failed to import main generator module: {e}")


def test_model_type_enum():
    """Test that ModelType enum has expected values."""
    try:
        from backend.components.generator.base import ModelType
        
        assert ModelType.UNDEFINED.value == "undefined"
        assert ModelType.LLM.value == "llm"
        assert ModelType.EMBEDDER.value == "embedder"
        assert ModelType.IMAGE_GENERATION.value == "image_generation"
        
        print("✅ ModelType enum values are correct")
    except Exception as e:
        pytest.fail(f"ModelType enum test failed: {e}")


def test_provider_type_enum():
    """Test that ProviderType enum has expected values."""
    try:
        from backend.components.generator.generator_manager import ProviderType
        
        assert ProviderType.OPENAI.value == "openai"
        assert ProviderType.AZURE.value == "azure"
        assert ProviderType.BEDROCK.value == "bedrock"
        assert ProviderType.DASHSCOPE.value == "dashscope"
        assert ProviderType.OPENROUTER.value == "openrouter"
        assert ProviderType.OLLAMA.value == "ollama"
        
        print("✅ ProviderType enum values are correct")
    except Exception as e:
        pytest.fail(f"ProviderType enum test failed: {e}")


def test_generator_output_creation():
    """Test that GeneratorOutput can be created correctly."""
    try:
        from backend.components.generator.base import GeneratorOutput
        
        # Test basic creation
        output = GeneratorOutput(data="test", error=None)
        assert output.data == "test"
        assert output.error is None
        assert bool(output) is True
        
        # Test error case
        error_output = GeneratorOutput(data=None, error="test error")
        assert error_output.data is None
        assert error_output.error == "test error"
        assert bool(error_output) is False
        
        print("✅ GeneratorOutput creation and boolean behavior works correctly")
    except Exception as e:
        pytest.fail(f"GeneratorOutput test failed: {e}")


def test_generator_manager_creation():
    """Test that GeneratorManager can be created."""
    try:
        from backend.components.generator.generator_manager import GeneratorManager
        
        manager = GeneratorManager()
        assert manager is not None
        assert len(manager) == 0
        
        # Test provider listing
        providers = manager.list_providers()
        assert len(providers) == 6  # Should have 6 provider types
        
        print("✅ GeneratorManager creation and basic functionality works")
    except Exception as e:
        pytest.fail(f"GeneratorManager test failed: {e}")


if __name__ == "__main__":
    # Run tests
    print("🧪 Running generator components tests...")
    
    test_import_generator_base()
    test_import_generator_providers()
    test_import_generator_manager()
    test_import_generator_module()
    test_model_type_enum()
    test_provider_type_enum()
    test_generator_output_creation()
    test_generator_manager_creation()
    
    print("🎉 All generator component tests passed!")
