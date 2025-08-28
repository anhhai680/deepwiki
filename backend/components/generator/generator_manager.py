"""
Generator manager for orchestrating multiple AI provider generators.

This module provides a centralized interface for managing different AI provider
generators and selecting the appropriate one based on configuration or requirements.
"""

import logging
from typing import Dict, Any, Optional, Type, Union, List
from enum import Enum

from backend.components.generator.base import BaseGenerator, ModelType
from backend.components.generator.providers.openai_generator import OpenAIGenerator
from backend.components.generator.providers.azure_generator import AzureAIGenerator
from backend.components.generator.providers.bedrock_generator import BedrockGenerator
from backend.components.generator.providers.dashscope_generator import DashScopeGenerator
from backend.components.generator.providers.openrouter_generator import OpenRouterGenerator
from backend.components.generator.providers.ollama_generator import OllamaGenerator

log = logging.getLogger(__name__)


class ProviderType(Enum):
    """Enumeration of supported AI providers."""
    OPENAI = "openai"
    AZURE = "azure"
    BEDROCK = "bedrock"
    DASHSCOPE = "dashscope"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"


class GeneratorManager:
    """
    Centralized manager for all AI provider generators.
    
    This class provides a unified interface for creating, managing, and selecting
    different AI provider generators based on configuration or requirements.
    """
    
    def __init__(self):
        """Initialize the generator manager."""
        self._generators: Dict[str, BaseGenerator] = {}
        self._provider_classes: Dict[ProviderType, Type[BaseGenerator]] = {
            ProviderType.OPENAI: OpenAIGenerator,
            ProviderType.AZURE: AzureAIGenerator,
            ProviderType.BEDROCK: BedrockGenerator,
            ProviderType.DASHSCOPE: DashScopeGenerator,
            ProviderType.OPENROUTER: OpenRouterGenerator,
            ProviderType.OLLAMA: OllamaGenerator,
        }
    
    def register_generator(self, name: str, generator: BaseGenerator) -> None:
        """
        Register a generator instance with a specific name.
        
        Args:
            name: Unique name for the generator
            generator: Generator instance to register
        """
        if not isinstance(generator, BaseGenerator):
            raise ValueError("Generator must inherit from BaseGenerator")
        
        self._generators[name] = generator
        log.info(f"Registered generator '{name}' of type {type(generator).__name__}")
    
    def get_generator(self, name: str) -> Optional[BaseGenerator]:
        """
        Get a registered generator by name.
        
        Args:
            name: Name of the registered generator
            
        Returns:
            Generator instance if found, None otherwise
        """
        return self._generators.get(name)
    
    def create_generator(
        self,
        provider_type: Union[ProviderType, str],
        name: Optional[str] = None,
        **kwargs
    ) -> BaseGenerator:
        """
        Create a new generator instance for the specified provider.
        
        Args:
            provider_type: Type of AI provider (ProviderType enum or string)
            name: Optional name to register the generator with
            **kwargs: Additional arguments to pass to the generator constructor
            
        Returns:
            New generator instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        # Convert string to enum if needed
        if isinstance(provider_type, str):
            try:
                provider_type = ProviderType(provider_type.lower())
            except ValueError:
                raise ValueError(f"Unsupported provider type: {provider_type}")
        
        if provider_type not in self._provider_classes:
            raise ValueError(f"Provider type {provider_type} not supported")
        
        # Create the generator instance
        generator_class = self._provider_classes[provider_type]
        generator = generator_class(**kwargs)
        
        # Register with a default name if none provided
        if name is None:
            name = f"{provider_type.value}_generator"
        
        self.register_generator(name, generator)
        return generator
    
    def list_generators(self) -> Dict[str, str]:
        """
        List all registered generators.
        
        Returns:
            Dictionary mapping generator names to their types
        """
        return {name: type(gen).__name__ for name, gen in self._generators.items()}
    
    def list_providers(self) -> List[ProviderType]:
        """
        List all supported provider types.
        
        Returns:
            List of supported provider types
        """
        return list(self._provider_classes.keys())
    
    def remove_generator(self, name: str) -> bool:
        """
        Remove a registered generator.
        
        Args:
            name: Name of the generator to remove
            
        Returns:
            True if generator was removed, False if not found
        """
        if name in self._generators:
            del self._generators[name]
            log.info(f"Removed generator '{name}'")
            return True
        return False
    
    def clear_generators(self) -> None:
        """Remove all registered generators."""
        self._generators.clear()
        log.info("Cleared all registered generators")
    
    def get_generator_by_provider(self, provider_type: Union[ProviderType, str]) -> Optional[BaseGenerator]:
        """
        Get the first generator of a specific provider type.
        
        Args:
            provider_type: Type of AI provider to search for
            
        Returns:
            First generator of the specified type, or None if not found
        """
        # Convert string to enum if needed
        if isinstance(provider_type, str):
            try:
                provider_type = ProviderType(provider_type.lower())
            except ValueError:
                return None
        
        for generator in self._generators.values():
            if type(generator) == self._provider_classes[provider_type]:
                return generator
        
        return None
    
    def get_generators_by_provider(self, provider_type: Union[ProviderType, str]) -> List[BaseGenerator]:
        """
        Get all generators of a specific provider type.
        
        Args:
            provider_type: Type of AI provider to search for
            
        Returns:
            List of generators of the specified type
        """
        # Convert string to enum if needed
        if isinstance(provider_type, str):
            try:
                provider_type = ProviderType(provider_type.lower())
            except ValueError:
                return []
        
        generators = []
        for generator in self._generators.values():
            if type(generator) == self._provider_classes[provider_type]:
                generators.append(generator)
        
        return generators
    
    def create_default_generators(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, BaseGenerator]:
        """
        Create default generators for all supported providers.
        
        Args:
            config: Optional configuration dictionary for generators
            
        Returns:
            Dictionary mapping provider names to generator instances
        """
        config = config or {}
        created_generators = {}
        
        for provider_type in self._provider_classes.keys():
            try:
                # Get provider-specific configuration
                provider_config = config.get(provider_type.value, {})
                
                # Create generator with provider-specific config
                generator = self.create_generator(provider_type, **provider_config)
                created_generators[provider_type.value] = generator
                
                log.info(f"Created default generator for {provider_type.value}")
                
            except Exception as e:
                log.warning(f"Failed to create default generator for {provider_type.value}: {e}")
                continue
        
        return created_generators
    
    def validate_generator(self, generator: BaseGenerator) -> bool:
        """
        Validate that a generator is properly configured and can be used.
        
        Args:
            generator: Generator instance to validate
            
        Returns:
            True if generator is valid, False otherwise
        """
        try:
            # Check if generator has required methods
            required_methods = ['init_sync_client', 'call', 'acall']
            for method in required_methods:
                if not hasattr(generator, method):
                    log.error(f"Generator missing required method: {method}")
                    return False
            
            # Try to initialize sync client
            generator.init_sync_client()
            
            return True
            
        except Exception as e:
            log.error(f"Generator validation failed: {e}")
            return False
    
    def get_generator_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a registered generator.
        
        Args:
            name: Name of the registered generator
            
        Returns:
            Dictionary with generator information, or None if not found
        """
        generator = self._generators.get(name)
        if not generator:
            return None
        
        info = {
            "name": name,
            "type": type(generator).__name__,
            "provider": self._get_provider_type(generator),
            "valid": self.validate_generator(generator),
            "config": generator.to_dict() if hasattr(generator, 'to_dict') else {}
        }
        
        return info
    
    def _get_provider_type(self, generator: BaseGenerator) -> Optional[ProviderType]:
        """Get the provider type for a generator instance."""
        for provider_type, generator_class in self._provider_classes.items():
            if isinstance(generator, generator_class):
                return provider_type
        return None
    
    def __len__(self) -> int:
        """Return the number of registered generators."""
        return len(self._generators)
    
    def __contains__(self, name: str) -> bool:
        """Check if a generator name is registered."""
        return name in self._generators
    
    def __getitem__(self, name: str) -> BaseGenerator:
        """Get a generator by name using dictionary-style access."""
        if name not in self._generators:
            raise KeyError(f"Generator '{name}' not found")
        return self._generators[name]
    
    def __iter__(self):
        """Iterate over generator names."""
        return iter(self._generators.keys())


# Global generator manager instance
_generator_manager: Optional[GeneratorManager] = None


def get_generator_manager() -> GeneratorManager:
    """
    Get the global generator manager instance.
    
    Returns:
        Global generator manager instance
    """
    global _generator_manager
    if _generator_manager is None:
        _generator_manager = GeneratorManager()
    return _generator_manager


def create_generator(
    provider_type: Union[ProviderType, str],
    name: Optional[str] = None,
    **kwargs
) -> BaseGenerator:
    """
    Create a generator using the global manager.
    
    Args:
        provider_type: Type of AI provider
        name: Optional name to register the generator with
        **kwargs: Additional arguments for the generator
        
    Returns:
        New generator instance
    """
    manager = get_generator_manager()
    return manager.create_generator(provider_type, name, **kwargs)


def get_generator(name: str) -> Optional[BaseGenerator]:
    """
    Get a generator by name using the global manager.
    
    Args:
        name: Name of the registered generator
        
    Returns:
        Generator instance if found, None otherwise
    """
    manager = get_generator_manager()
    return manager.get_generator(name)
