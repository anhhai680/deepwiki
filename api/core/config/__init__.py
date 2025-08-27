"""
Core configuration module for the DeepWiki API.

This module provides configuration management, logging setup,
and provider configuration extracted from existing code.
"""

# Import the configuration manager as the main interface
from .manager import (
    ConfigurationManager,
    get_config_manager,
    initialize_config,
    get_setting,
    get_config,
    get_model_config
)

# Import core configuration functions
from .settings import get_settings, update_settings, get_excluded_dirs, get_excluded_files
from .logging import setup_logging_from_env, get_logger

# Import configuration loading functions from utilities
from .utils import (
    load_generator_config, 
    load_embedder_config, 
    load_repo_config, 
    load_lang_config
)

# Import client classes for provider configuration
try:
    from api.openai_client import OpenAIClient
    from api.openrouter_client import OpenRouterClient
    from api.bedrock_client import BedrockClient
    from api.azureai_client import AzureAIClient
    from api.dashscope_client import DashscopeClient
    from adalflow import GoogleGenAIClient, OllamaClient
except ImportError:
    # Handle import errors gracefully during development
    OpenAIClient = None
    OpenRouterClient = None
    BedrockClient = None
    AzureAIClient = None
    DashscopeClient = None
    GoogleGenAIClient = None
    OllamaClient = None

# Client class mapping
CLIENT_CLASSES = {
    "GoogleGenAIClient": GoogleGenAIClient,
    "OpenAIClient": OpenAIClient,
    "OpenRouterClient": OpenRouterClient,
    "OllamaClient": OllamaClient,
    "BedrockClient": BedrockClient,
    "AzureAIClient": AzureAIClient,
    "DashscopeClient": DashscopeClient
}

# Export the main configuration interface
__all__ = [
    # Configuration manager
    "ConfigurationManager",
    "get_config_manager", 
    "initialize_config",
    
    # Core functions
    "get_settings",
    "update_settings",
    "get_excluded_dirs",
    "get_excluded_files",
    
    # Logging
    "setup_logging_from_env",
    "get_logger",
    
    # Configuration loading
    "load_generator_config",
    "load_embedder_config", 
    "load_repo_config",
    "load_lang_config",
    
    # Convenience functions
    "get_setting",
    "get_config",
    "get_model_config",
    
    # Client classes
    "CLIENT_CLASSES",
]
