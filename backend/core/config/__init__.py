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

# Import generator components for provider configuration
try:
    from backend.components.generator.providers.openai_generator import OpenAIGenerator
    from backend.components.generator.providers.openrouter_generator import OpenRouterGenerator
    from backend.components.generator.providers.bedrock_generator import BedrockGenerator
    from backend.components.generator.providers.azure_generator import AzureAIGenerator
    from backend.components.generator.providers.dashscope_generator import DashScopeGenerator
    from backend.components.generator.providers.ollama_generator import OllamaGenerator
    from adalflow import GoogleGenAIClient, OllamaClient, OpenAIClient
except ImportError:
    # Handle import errors gracefully during development
    OpenAIGenerator = None
    OpenRouterGenerator = None
    BedrockGenerator = None
    AzureAIGenerator = None
    DashScopeGenerator = None
    OllamaGenerator = None
    GoogleGenAIClient = None
    OllamaClient = None

# Generator class mapping
GENERATOR_CLASSES = {
    "GoogleGenAIClient": GoogleGenAIClient,
    "OpenAIGenerator": OpenAIGenerator,
    "OpenRouterGenerator": OpenRouterGenerator,
    "OllamaGenerator": OllamaGenerator,
    "BedrockGenerator": BedrockGenerator,
    "AzureAIGenerator": AzureAIGenerator,
    "DashScopeGenerator": DashScopeGenerator
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
    
    # Generator classes
    "GENERATOR_CLASSES",
]
