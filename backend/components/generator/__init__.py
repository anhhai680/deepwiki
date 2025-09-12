"""
Generator components for AI provider integration.

This module provides a unified interface for different AI providers including
OpenAI, Azure AI, AWS Bedrock, DashScope, OpenRouter, and Ollama.
"""

from .base import BaseGenerator, ModelType, GeneratorOutput
from .generator_manager import (
    GeneratorManager,
    ProviderType,
    get_generator_manager,
    create_generator,
    get_generator
)

# Provider-specific generators
from .providers.openai_generator import OpenAIGenerator
from .providers.azure_generator import AzureAIGenerator
from .providers.bedrock_generator import BedrockGenerator
from .providers.dashscope_generator import DashScopeGenerator
from .providers.openrouter_generator import OpenRouterGenerator
from .providers.ollama_generator import OllamaGenerator
from .providers.private_model_generator import PrivateModelGenerator

__all__ = [
    # Base classes and types
    "BaseGenerator",
    "ModelType", 
    "GeneratorOutput",
    
    # Generator manager
    "GeneratorManager",
    "ProviderType",
    "get_generator_manager",
    "create_generator",
    "get_generator",
    
    # Provider-specific generators
    "OpenAIGenerator",
    "AzureAIGenerator", 
    "BedrockGenerator",
    "DashScopeGenerator",
    "OpenRouterGenerator",
    "OllamaGenerator",
    "PrivateModelGenerator",
]
