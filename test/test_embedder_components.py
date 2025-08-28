"""
Test suite for embedder components.

This module tests the functionality of the new embedder component architecture
to ensure it works correctly and maintains compatibility.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the api directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.components.embedder.base import BaseEmbedder, EmbeddingModelType, EmbedderOutput
from api.components.embedder.embedder_manager import EmbedderManager, EmbeddingProviderType
from api.components.embedder.providers.openai_embedder import OpenAIEmbedder
from api.components.embedder.providers.ollama_embedder import OllamaEmbedder
from api.components.embedder.compatibility import get_embedder, get_embedder_manager, create_embedder, embed_text


class TestEmbedderBase(unittest.TestCase):
    """Test the base embedder functionality."""
    
    def test_embedding_model_type_enum(self):
        """Test that embedding model types are properly defined."""
        self.assertEqual(EmbeddingModelType.TEXT.value, "text")
        self.assertEqual(EmbeddingModelType.CODE.value, "code")
        self.assertEqual(EmbeddingModelType.MULTIMODAL.value, "multimodal")
    
    def test_embedder_output_creation(self):
        """Test EmbedderOutput creation and boolean behavior."""
        # Test successful output
        output = EmbedderOutput(data="test_data")
        self.assertTrue(output)
        self.assertEqual(output.data, "test_data")
        self.assertIsNone(output.error)
        
        # Test error output
        error_output = EmbedderOutput(error="test_error")
        self.assertFalse(error_output)
        self.assertEqual(error_output.error, "test_error")
        self.assertIsNone(error_output.data)
    
    def test_embedder_output_string_representation(self):
        """Test EmbedderOutput string representation."""
        output = EmbedderOutput(data="test_data")
        self.assertIn("str", str(output))  # The type name is shown, not the actual data
        
        error_output = EmbedderOutput(error="test_error")
        self.assertIn("test_error", str(error_output))


class TestEmbedderManager(unittest.TestCase):
    """Test the embedder manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = EmbedderManager()
    
    def test_provider_type_enum(self):
        """Test that provider types are properly defined."""
        self.assertEqual(EmbeddingProviderType.OPENAI.value, "openai")
        self.assertEqual(EmbeddingProviderType.OLLAMA.value, "ollama")
    
    def test_manager_initialization(self):
        """Test that the manager initializes correctly."""
        self.assertIsInstance(self.manager, EmbedderManager)
        self.assertEqual(len(self.manager.list_embedders()), 0)
    
    def test_supported_providers(self):
        """Test that supported providers are correctly listed."""
        providers = self.manager.get_supported_providers()
        self.assertIn("openai", providers)
        self.assertIn("ollama", providers)
    
    def test_provider_validation(self):
        """Test provider type validation."""
        self.assertTrue(self.manager.validate_provider_type("openai"))
        self.assertTrue(self.manager.validate_provider_type("OLLAMA"))
        self.assertFalse(self.manager.validate_provider_type("unsupported"))
    
    def test_embedder_creation(self):
        """Test embedder creation for different providers."""
        # Test OpenAI embedder creation
        openai_embedder = self.manager.create_embedder("openai")
        self.assertIsInstance(openai_embedder, OpenAIEmbedder)
        
        # Test Ollama embedder creation
        ollama_embedder = self.manager.create_embedder("ollama")
        self.assertIsInstance(ollama_embedder, OllamaEmbedder)
    
    def test_embedder_registration(self):
        """Test embedder registration and retrieval."""
        embedder = self.manager.create_embedder("openai")
        self.manager.register_embedder("test_embedder", embedder)
        
        retrieved = self.manager.get_embedder("test_embedder")
        self.assertEqual(retrieved, embedder)
        
        # Test listing embedders
        embedders = self.manager.list_embedders()
        self.assertIn("test_embedder", embedders)
    
    def test_embedder_removal(self):
        """Test embedder removal."""
        embedder = self.manager.create_embedder("openai")
        self.manager.register_embedder("test_embedder", embedder)
        
        # Remove the embedder
        result = self.manager.remove_embedder("test_embedder")
        self.assertTrue(result)
        
        # Verify it's gone
        self.assertIsNone(self.manager.get_embedder("test_embedder"))
        
        # Test removing non-existent embedder
        result = self.manager.remove_embedder("non_existent")
        self.assertFalse(result)


class TestOpenAIEmbedder(unittest.TestCase):
    """Test the OpenAI embedder implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('api.components.generator.providers.openai_generator.OpenAIGenerator'):
            self.embedder = OpenAIEmbedder()
    
    def test_embedder_initialization(self):
        """Test that the OpenAI embedder initializes correctly."""
        self.assertIsInstance(self.embedder, OpenAIEmbedder)
        self.assertEqual(self.embedder._model_name, "text-embedding-3-small")
        self.assertEqual(self.embedder._dimensions, 256)
        self.assertEqual(self.embedder._encoding_format, "float")
    
    def test_convert_inputs_to_api_kwargs(self):
        """Test input conversion to API parameters."""
        # Test single text input
        kwargs = self.embedder.convert_inputs_to_api_kwargs("test text")
        self.assertEqual(kwargs["input"], ["test text"])
        self.assertEqual(kwargs["model"], "text-embedding-3-small")
        
        # Test list input
        kwargs = self.embedder.convert_inputs_to_api_kwargs(["text1", "text2"])
        self.assertEqual(kwargs["input"], ["text1", "text2"])
        
        # Test with custom model kwargs
        custom_kwargs = {"dimensions": 512}
        kwargs = self.embedder.convert_inputs_to_api_kwargs("test", custom_kwargs)
        self.assertEqual(kwargs["dimensions"], 512)
    
    def test_model_info(self):
        """Test model information retrieval."""
        info = self.embedder.get_model_info()
        self.assertEqual(info["provider"], "openai")
        self.assertEqual(info["model_name"], "text-embedding-3-small")
        self.assertEqual(info["dimensions"], 256)
    
    def test_model_configuration(self):
        """Test model configuration methods."""
        self.embedder.set_model("text-embedding-3-large", 1024)
        self.assertEqual(self.embedder._model_name, "text-embedding-3-large")
        self.assertEqual(self.embedder._dimensions, 1024)
        
        self.embedder.set_encoding_format("base64")
        self.assertEqual(self.embedder._encoding_format, "base64")
        
        # Test invalid encoding format
        with self.assertRaises(ValueError):
            self.embedder.set_encoding_format("invalid")


class TestOllamaEmbedder(unittest.TestCase):
    """Test the Ollama embedder implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.embedder = OllamaEmbedder()
    
    def test_embedder_initialization(self):
        """Test that the Ollama embedder initializes correctly."""
        self.assertIsInstance(self.embedder, OllamaEmbedder)
        self.assertEqual(self.embedder._model_name, "nomic-embed-text")
        self.assertEqual(self.embedder._base_url, "http://localhost:11434")
    
    def test_convert_inputs_to_api_kwargs(self):
        """Test input conversion to API parameters."""
        # Test single text input
        kwargs = self.embedder.convert_inputs_to_api_kwargs("test text")
        self.assertEqual(kwargs["prompt"], "test text")
        self.assertEqual(kwargs["model"], "nomic-embed-text")
        
        # Test list input (Ollama processes one at a time)
        kwargs = self.embedder.convert_inputs_to_api_kwargs(["text1", "text2"])
        self.assertEqual(kwargs["prompt"], "text1")
    
    def test_model_info(self):
        """Test model information retrieval."""
        info = self.embedder.get_model_info()
        self.assertEqual(info["provider"], "ollama")
        self.assertEqual(info["model_name"], "nomic-embed-text")
        self.assertEqual(info["base_url"], "http://localhost:11434")
    
    def test_model_configuration(self):
        """Test model configuration methods."""
        self.embedder.set_model("new-model")
        self.assertEqual(self.embedder._model_name, "new-model")
        
        self.embedder.set_base_url("http://new-server:11434")
        self.assertEqual(self.embedder._base_url, "http://new-server:11434")


class TestCompatibilityLayer(unittest.TestCase):
    """Test the compatibility layer functionality."""
    
    @patch('api.components.embedder.compatibility.configs')
    def test_get_embedder_manager(self, mock_configs):
        """Test that the embedder manager can be retrieved."""
        manager = get_embedder_manager()
        self.assertIsInstance(manager, EmbedderManager)
    
    @patch('api.components.embedder.compatibility.configs')
    def test_create_embedder_function(self, mock_configs):
        """Test the create_embedder convenience function."""
        embedder = create_embedder("openai")
        self.assertIsInstance(embedder, OpenAIEmbedder)
    
    @patch('api.components.embedder.compatibility.configs')
    def test_embed_text_function(self, mock_configs):
        """Test the embed_text convenience function."""
        with patch.object(EmbedderManager, 'embed_text') as mock_embed:
            mock_embed.return_value = "test_embedding"
            result = embed_text("test text", "openai")
            self.assertEqual(result, "test_embedding")


if __name__ == '__main__':
    unittest.main()
