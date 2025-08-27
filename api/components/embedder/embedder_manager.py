"""
Embedder manager for orchestrating multiple embedding provider embedders.

This module provides a centralized interface for managing different embedding provider
embedders and selecting the appropriate one based on configuration or requirements.
"""

import logging
from typing import Dict, Any, Optional, Type, Union, List
from enum import Enum

from api.components.embedder.base import BaseEmbedder, EmbeddingModelType
from api.components.embedder.providers.openai_embedder import OpenAIEmbedder
from api.components.embedder.providers.ollama_embedder import OllamaEmbedder

log = logging.getLogger(__name__)


class EmbeddingProviderType(Enum):
    """Enumeration of supported embedding providers."""
    OPENAI = "openai"
    OLLAMA = "ollama"


class EmbedderManager:
    """
    Centralized manager for all embedding provider embedders.
    
    This class provides a unified interface for creating, managing, and selecting
    different embedding provider embedders based on configuration or requirements.
    """
    
    def __init__(self):
        """Initialize the embedder manager."""
        self._embedders: Dict[str, BaseEmbedder] = {}
        self._provider_classes: Dict[EmbeddingProviderType, Type[BaseEmbedder]] = {
            EmbeddingProviderType.OPENAI: OpenAIEmbedder,
            EmbeddingProviderType.OLLAMA: OllamaEmbedder,
        }
    
    def register_embedder(self, name: str, embedder: BaseEmbedder) -> None:
        """
        Register an embedder instance with a specific name.
        
        Args:
            name: Unique name for the embedder
            embedder: Embedder instance to register
        """
        if not isinstance(embedder, BaseEmbedder):
            raise ValueError("Embedder must inherit from BaseEmbedder")
        
        self._embedders[name] = embedder
        log.info(f"Registered embedder '{name}' of type {type(embedder).__name__}")
    
    def get_embedder(self, name: str) -> Optional[BaseEmbedder]:
        """
        Get a registered embedder by name.
        
        Args:
            name: Name of the registered embedder
            
        Returns:
            Embedder instance if found, None otherwise
        """
        return self._embedders.get(name)
    
    def create_embedder(
        self,
        provider_type: Union[EmbeddingProviderType, str],
        name: Optional[str] = None,
        **kwargs
    ) -> BaseEmbedder:
        """
        Create a new embedder instance for the specified provider.
        
        Args:
            provider_type: Type of embedding provider (EmbeddingProviderType enum or string)
            name: Optional name to register the embedder with
            **kwargs: Additional arguments to pass to the embedder constructor
            
        Returns:
            New embedder instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        # Convert string to enum if needed
        if isinstance(provider_type, str):
            try:
                provider_type = EmbeddingProviderType(provider_type.lower())
            except ValueError:
                raise ValueError(f"Unsupported provider type: {provider_type}")
        
        if provider_type not in self._provider_classes:
            raise ValueError(f"Provider type {provider_type} is not supported")
        
        # Create the embedder instance
        embedder_class = self._provider_classes[provider_type]
        embedder = embedder_class(**kwargs)
        
        # Register with the provided name if specified
        if name:
            self.register_embedder(name, embedder)
        
        log.info(f"Created embedder of type {provider_type.value}")
        return embedder
    
    def get_all_embedders(self) -> Dict[str, BaseEmbedder]:
        """
        Get all registered embedders.
        
        Returns:
            Dict mapping embedder names to instances
        """
        return self._embedders.copy()
    
    def remove_embedder(self, name: str) -> bool:
        """
        Remove a registered embedder.
        
        Args:
            name: Name of the embedder to remove
            
        Returns:
            True if embedder was removed, False if not found
        """
        if name in self._embedders:
            del self._embedders[name]
            log.info(f"Removed embedder '{name}'")
            return True
        return False
    
    def clear_embedders(self) -> None:
        """Remove all registered embedders."""
        self._embedders.clear()
        log.info("Cleared all registered embedders")
    
    def list_embedders(self) -> List[str]:
        """
        Get a list of all registered embedder names.
        
        Returns:
            List of embedder names
        """
        return list(self._embedders.keys())
    
    def get_embedder_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific embedder.
        
        Args:
            name: Name of the embedder
            
        Returns:
            Dict with embedder information, or None if not found
        """
        embedder = self.get_embedder(name)
        if embedder:
            return {
                "name": name,
                "type": type(embedder).__name__,
                "model_info": embedder.get_model_info()
            }
        return None
    
    def get_all_embedder_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all registered embedders.
        
        Returns:
            Dict mapping embedder names to their information
        """
        return {
            name: self.get_embedder_info(name)
            for name in self.list_embedders()
        }
    
    def embed_text(
        self,
        text: Union[str, List[str]],
        embedder_name: Optional[str] = None,
        provider_type: Optional[Union[EmbeddingProviderType, str]] = None,
        **kwargs
    ) -> Any:
        """
        Generate embeddings using a specific embedder or provider.
        
        Args:
            text: Text or list of texts to embed
            embedder_name: Name of registered embedder to use
            provider_type: Provider type to create new embedder from
            **kwargs: Additional arguments for embedder creation
            
        Returns:
            Embedding result from the embedder
            
        Raises:
            ValueError: If neither embedder_name nor provider_type is specified
        """
        if embedder_name:
            embedder = self.get_embedder(embedder_name)
            if not embedder:
                raise ValueError(f"Embedder '{embedder_name}' not found")
        elif provider_type:
            embedder = self.create_embedder(provider_type, **kwargs)
        else:
            raise ValueError("Must specify either embedder_name or provider_type")
        
        return embedder.embed(text)
    
    async def embed_text_async(
        self,
        text: Union[str, List[str]],
        embedder_name: Optional[str] = None,
        provider_type: Optional[Union[EmbeddingProviderType, str]] = None,
        **kwargs
    ) -> Any:
        """
        Generate embeddings asynchronously using a specific embedder or provider.
        
        Args:
            text: Text or list of texts to embed
            embedder_name: Name of registered embedder to use
            provider_type: Provider type to create new embedder from
            **kwargs: Additional arguments for embedder creation
            
        Returns:
            Async embedding result from the embedder
            
        Raises:
            ValueError: If neither embedder_name nor provider_type is specified
        """
        if embedder_name:
            embedder = self.get_embedder(embedder_name)
            if not embedder:
                raise ValueError(f"Embedder '{embedder_name}' not found")
        elif provider_type:
            embedder = self.create_embedder(provider_type, **kwargs)
        else:
            raise ValueError("Must specify either embedder_name or provider_type")
        
        return await embedder.embed_async(text)
    
    def get_supported_providers(self) -> List[str]:
        """
        Get a list of supported embedding provider types.
        
        Returns:
            List of supported provider type names
        """
        return [provider.value for provider in EmbeddingProviderType]
    
    def validate_provider_type(self, provider_type: str) -> bool:
        """
        Check if a provider type is supported.
        
        Args:
            provider_type: Provider type to validate
            
        Returns:
            True if supported, False otherwise
        """
        try:
            EmbeddingProviderType(provider_type.lower())
            return True
        except ValueError:
            return False
