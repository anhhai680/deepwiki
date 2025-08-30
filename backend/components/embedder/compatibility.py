"""
Compatibility layer for existing embedder interface.

This module provides backward compatibility with the existing tools/embedder.py
interface while using the new component-based architecture.
"""

import logging

from backend.components.embedder import EmbedderManager, EmbeddingProviderType
from backend.core.config.settings import configs

log = logging.getLogger(__name__)


def get_embedder():
    """
    Get an embedder instance using the new component architecture.
    
    This function maintains backward compatibility with the existing
    tools/embedder.py interface while leveraging the new embedder components.
    
    Returns:
        Embedder instance configured according to the embedder configuration
    """
    try:
        embedder_config = configs.get("embedder", {})
        
        # Determine the provider type from configuration
        client_class = embedder_config.get("client_class", "OpenAIGenerator")
        
        # Map client class names to provider types
        provider_mapping = {
            "OpenAIGenerator": EmbeddingProviderType.OPENAI,
            "OllamaGenerator": EmbeddingProviderType.OLLAMA,
        }
        
        provider_type = provider_mapping.get(client_class, EmbeddingProviderType.OPENAI)
        
        # Create embedder manager
        manager = EmbedderManager()
        
        # Extract configuration parameters
        model_kwargs = embedder_config.get("model_kwargs", {})
        initialize_kwargs = embedder_config.get("initialize_kwargs", {})
        
        # Create embedder with configuration
        embedder = manager.create_embedder(
            provider_type=provider_type,
            **model_kwargs,
            **initialize_kwargs
        )
        
        log.info(f"Created embedder using {provider_type.value} provider")
        return embedder
        
    except Exception as e:
        log.error(f"Failed to create embedder: {e}")
        # Fallback to original implementation if available
        try:
            import adalflow as adal
            model_client_class = embedder_config["model_client"]
            if "initialize_kwargs" in embedder_config:
                model_client = model_client_class(**embedder_config["initialize_kwargs"])
            else:
                model_client = model_client_class()
            embedder = adal.Embedder(
                model_client=model_client,
                model_kwargs=embedder_config["model_kwargs"],
            )
            log.warning("Using fallback embedder implementation")
            return embedder
        except Exception as fallback_error:
            log.error(f"Fallback embedder creation also failed: {fallback_error}")
            raise RuntimeError(f"Failed to create embedder: {e}")


def get_embedder_manager():
    """
    Get the embedder manager instance for advanced usage.
    
    Returns:
        EmbedderManager instance for managing multiple embedders
    """
    return EmbedderManager()


def create_embedder(provider_type: str, **kwargs):
    """
    Create a new embedder instance for the specified provider.
    
    Args:
        provider_type: Type of embedding provider ('openai', 'ollama')
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured embedder instance
    """
    manager = EmbedderManager()
    return manager.create_embedder(provider_type=provider_type, **kwargs)


def embed_text(text, provider_type: str = "openai", **kwargs):
    """
    Generate embeddings for text using the specified provider.
    
    Args:
        text: Text or list of texts to embed
        provider_type: Type of embedding provider ('openai', 'ollama')
        **kwargs: Additional configuration parameters
        
    Returns:
        Embedding result
    """
    manager = EmbedderManager()
    return manager.embed_text(text, provider_type=provider_type, **kwargs)


async def embed_text_async(text, provider_type: str = "openai", **kwargs):
    """
    Generate embeddings asynchronously for text using the specified provider.
    
    Args:
        text: Text or list of texts to embed
        provider_type: Type of embedding provider ('openai', 'ollama')
        **kwargs: Additional configuration parameters
        
    Returns:
        Async embedding result
    """
    manager = EmbedderManager()
    return await manager.embed_text_async(text, provider_type=provider_type, **kwargs)
