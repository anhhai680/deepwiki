"""
Configuration manager for the DeepWiki API.

This module provides a centralized interface for managing
all application configuration, extracted from existing code.
"""

from typing import Dict, Any, Optional

from .settings import get_settings, update_settings, get_excluded_dirs, get_excluded_files
from .logging import setup_logging_from_env, get_logger
from .utils import (
    load_generator_config, 
    load_embedder_config, 
    load_repo_config, 
    load_lang_config
)

logger = get_logger(__name__)


class ConfigurationManager:
    """
    Centralized configuration manager for the DeepWiki API.
    
    This class consolidates all configuration functionality
    extracted from the existing config.py file.
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        self._settings = get_settings()
        self._configs = {}
        self._initialized = False
        self._client_classes = {}
    
    def _load_client_classes(self):
        """Load generator classes for provider configuration."""
        try:
            from backend.components.generator.providers.openai_generator import OpenAIGenerator
            from backend.components.generator.providers.openrouter_generator import OpenRouterGenerator
            from backend.components.generator.providers.bedrock_generator import BedrockGenerator
            from backend.components.generator.providers.azure_generator import AzureAIGenerator
            from backend.components.generator.providers.dashscope_generator import DashScopeGenerator
            from backend.components.generator.providers.ollama_generator import OllamaGenerator
            from backend.components.generator.providers.private_model_generator import PrivateModelGenerator
            from adalflow import GoogleGenAIClient, OllamaClient, OpenAIClient
            
            self._client_classes = {
                "GoogleGenAIClient": GoogleGenAIClient,
                "OllamaClient": OllamaClient,
                "OpenAIClient": OpenAIClient,
                "OpenAIGenerator": OpenAIGenerator,
                "OpenRouterGenerator": OpenRouterGenerator,
                "OllamaGenerator": OllamaGenerator,
                "BedrockGenerator": BedrockGenerator,
                "AzureAIGenerator": AzureAIGenerator,
                "DashScopeGenerator": DashScopeGenerator,
                "PrivateModelGenerator": PrivateModelGenerator
            }
        except ImportError:
            # Handle import errors gracefully during development
            logger.warning("Some client classes could not be imported")
            self._client_classes = {}
    
    def initialize(self) -> None:
        """Initialize the configuration system."""
        if self._initialized:
            logger.debug("Configuration already initialized")
            return
        
        try:
            # Set up logging from environment
            setup_logging_from_env()
            
            # Load client classes
            self._load_client_classes()
            
            # Load all configurations
            self._configs["generator"] = load_generator_config(self._client_classes)
            self._configs["embedder"] = load_embedder_config(self._client_classes)
            self._configs["repo"] = load_repo_config()
            self._configs["lang"] = load_lang_config()
            
            # Update global settings with loaded configurations
            configs_to_update = {}
            
            if self._configs["generator"]:
                configs_to_update["default_provider"] = self._configs["generator"].get("default_provider", "google")
                configs_to_update["providers"] = self._configs["generator"].get("providers", {})
            
            if self._configs["embedder"]:
                for key in ["embedder", "embedder_ollama", "retriever", "text_splitter"]:
                    if key in self._configs["embedder"]:
                        configs_to_update[key] = self._configs["embedder"][key]
            
            if self._configs["repo"]:
                for key in ["file_filters", "repository"]:
                    if key in self._configs["repo"]:
                        configs_to_update[key] = self._configs["repo"][key]
            
            if self._configs["lang"]:
                configs_to_update["lang_config"] = self._configs["lang"]
            
            # Update settings with loaded configurations
            update_settings(configs_to_update)
            
            self._initialized = True
            logger.info("Configuration system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize configuration: {e}")
            raise
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return getattr(self._settings, key, default)
    
    def get_config(self, config_type: str) -> Dict[str, Any]:
        """Get configuration of a specific type."""
        if not self._initialized:
            self.initialize()
        return self._configs.get(config_type, {})
    
    def get_generator_config(self) -> Dict[str, Any]:
        """Get generator configuration."""
        return self.get_config("generator")
    
    def get_embedder_config(self) -> Dict[str, Any]:
        """Get embedder configuration."""
        return self.get_config("embedder")
    
    def get_repo_config(self) -> Dict[str, Any]:
        """Get repository configuration."""
        return self.get_config("repo")
    
    def get_lang_config(self) -> Dict[str, Any]:
        """Get language configuration."""
        return self.get_config("lang")
    
    def get_provider_config(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific provider."""
        generator_config = self.get_generator_config()
        providers = generator_config.get("providers", {})
        return providers.get(provider)
    
    def get_model_config(self, provider: str = "google", model: str = None) -> Dict[str, Any]:
        """Get configuration for the specified provider and model."""
        if not self._initialized:
            self.initialize()
        
        # Get provider configuration
        provider_config = self.get_provider_config(provider)
        if not provider_config:
            raise ValueError(f"Configuration for provider '{provider}' not found")
        
        model_client = provider_config.get("model_client")
        if not model_client:
            raise ValueError(f"Model client not specified for provider '{provider}'")
        
        # If model not provided, use default model for the provider
        if not model:
            model = provider_config.get("default_model")
            if not model:
                raise ValueError(f"No default model specified for provider '{provider}'")
        
        # Get model parameters (if present)
        model_params = {}
        if model in provider_config.get("models", {}):
            model_params = provider_config["models"][model]
        else:
            default_model = provider_config.get("default_model")
            if default_model and default_model in provider_config.get("models", {}):
                model_params = provider_config["models"][default_model]
        
        # Prepare base configuration
        result = {
            "model_client": model_client,
        }
        
        # Provider-specific adjustments
        if provider == "ollama":
            # Ollama uses a slightly different parameter structure
            if "options" in model_params:
                result["model_kwargs"] = {"model": model, **model_params["options"]}
            else:
                result["model_kwargs"] = {"model": model}
        else:
            # Standard structure for other providers
            result["model_kwargs"] = {"model": model, **model_params}
        
        return result
    
    def get_excluded_dirs(self) -> list:
        """Get the list of excluded directories."""
        return get_excluded_dirs()
    
    def get_excluded_files(self) -> list:
        """Get the list of excluded files."""
        return get_excluded_files()
    
    def is_ollama_embedder(self) -> bool:
        """Check if the current embedder configuration uses OllamaClient."""
        embedder_config = self.get_embedder_config()
        if not embedder_config:
            return False
        
        # Check if model_client is OllamaClient
        model_client = embedder_config.get("model_client")
        if model_client:
            return model_client.__name__ == "OllamaClient"
        
        # Fallback: check client_class string
        client_class = embedder_config.get("client_class", "")
        return client_class == "OllamaClient"
    
    def get_default_provider(self) -> str:
        """Get the default provider."""
        generator_config = self.get_generator_config()
        return generator_config.get("default_provider", "google")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages."""
        lang_config = self.get_lang_config()
        return lang_config.get("supported_languages", {"en": "English"})
    
    def get_default_language(self) -> str:
        """Get the default language."""
        lang_config = self.get_lang_config()
        return lang_config.get("default", "en")
    
    def reload_config(self) -> None:
        """Reload all configuration files."""
        logger.info("Reloading configuration files")
        self._initialized = False
        self.initialize()
    
    def validate_config(self) -> bool:
        """Validate the current configuration."""
        try:
            # Check if required configurations are present
            generator_config = self.get_generator_config()
            if not generator_config:
                logger.warning("Generator configuration not found")
                return False
            
            # Check if at least one provider is configured
            providers = generator_config.get("providers", {})
            if not providers:
                logger.warning("No providers configured")
                return False
            
            # Check if default provider exists
            default_provider = generator_config.get("default_provider")
            if default_provider and default_provider not in providers:
                logger.warning(f"Default provider '{default_provider}' not found in configured providers")
                return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def get_client_classes(self) -> Dict[str, Any]:
        """Get the client classes mapping."""
        if not self._initialized:
            self.initialize()
        return self._client_classes.copy()


# Global configuration manager instance
_config_manager = None


def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
        _config_manager.initialize()
    return _config_manager


def initialize_config() -> None:
    """Initialize the global configuration system."""
    get_config_manager().initialize()


# Convenience functions for backward compatibility
def get_setting(key: str, default: Any = None) -> Any:
    """Get a setting value."""
    return get_config_manager().get_setting(key, default)


def get_config(config_type: str) -> Dict[str, Any]:
    """Get configuration of a specific type."""
    return get_config_manager().get_config(config_type)


def get_model_config(provider: str = "google", model: str = None) -> Dict[str, Any]:
    """Get configuration for the specified provider and model."""
    return get_config_manager().get_model_config(provider, model)

