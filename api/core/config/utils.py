"""
Configuration utilities for the DeepWiki API.

This module contains utility functions for loading and processing
configuration files, extracted from existing code.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, Any, Union, List

from .settings import get_settings
from .logging import get_logger

logger = get_logger(__name__)


def replace_env_placeholders(config: Union[Dict[str, Any], List[Any], str, Any]) -> Union[Dict[str, Any], List[Any], str, Any]:
    """
    Recursively replace placeholders like "${ENV_VAR}" in string values
    within a nested configuration structure with environment variable values.
    
    Extracted from existing config.py during restructure.
    """
    pattern = re.compile(r"\$\{([A-Z0-9_]+)\}")

    def replacer(match: re.Match[str]) -> str:
        env_var_name = match.group(1)
        original_placeholder = match.group(0)
        env_var_value = os.environ.get(env_var_name)
        if env_var_value is None:
            logger.warning(
                f"Environment variable placeholder '{original_placeholder}' was not found in the environment. "
                f"The placeholder string will be used as is."
            )
            return original_placeholder
        return env_var_value

    if isinstance(config, dict):
        return {k: replace_env_placeholders(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [replace_env_placeholders(item) for item in config]
    elif isinstance(config, str):
        return pattern.sub(replacer, config)
    else:
        # Handles numbers, booleans, None, etc.
        return config


def load_json_config(filename: str) -> Dict[str, Any]:
    """
    Load JSON configuration file with environment variable substitution.
    
    Extracted from existing config.py during restructure.
    """
    try:
        settings = get_settings()
        
        # If environment variable is set, use the directory specified by it
        if settings.config_dir:
            config_path = Path(settings.config_dir) / filename
        else:
            # Otherwise use default directory
            config_path = Path(__file__).parent.parent.parent / "config" / filename

        logger.info(f"Loading configuration from {config_path}")

        if not config_path.exists():
            logger.warning(f"Configuration file {config_path} does not exist")
            return {}

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            config = replace_env_placeholders(config)
            return config
    except Exception as e:
        logger.error(f"Error loading configuration file {filename}: {str(e)}")
        return {}


def load_generator_config(client_classes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load generator model configuration.
    
    Extracted from existing config.py during restructure.
    """
    generator_config = load_json_config("generator.json")

    # Add client classes to each provider
    if "providers" in generator_config:
        for provider_id, provider_config in generator_config["providers"].items():
            # Try to set client class from client_class
            if provider_config.get("client_class") in client_classes:
                provider_config["model_client"] = client_classes[provider_config["client_class"]]
            # Fall back to default mapping based on provider_id
            elif provider_id in ["google", "openai", "openrouter", "ollama", "bedrock", "azure", "dashscope"]:
                default_map = {
                    "google": client_classes.get("GoogleGenAIClient"),
                    "openai": client_classes.get("OpenAIClient"),
                    "openrouter": client_classes.get("OpenRouterClient"),
                    "ollama": client_classes.get("OllamaClient"),
                    "bedrock": client_classes.get("BedrockClient"),
                    "azure": client_classes.get("AzureAIClient"),
                    "dashscope": client_classes.get("DashscopeClient")
                }
                provider_config["model_client"] = default_map[provider_id]
            else:
                logger.warning(f"Unknown provider or client class: {provider_id}")

    return generator_config


def load_embedder_config(client_classes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load embedder configuration.
    
    Extracted from existing config.py during restructure.
    """
    embedder_config = load_json_config("embedder.json")

    # Process client classes
    for key in ["embedder", "embedder_ollama"]:
        if key in embedder_config and "client_class" in embedder_config[key]:
            class_name = embedder_config[key]["client_class"]
            if class_name in client_classes:
                embedder_config[key]["model_client"] = client_classes[class_name]

    return embedder_config


def load_repo_config() -> Dict[str, Any]:
    """
    Load repository and file filters configuration.
    
    Extracted from existing config.py during restructure.
    """
    return load_json_config("repo.json")


def load_lang_config() -> Dict[str, Any]:
    """
    Load language configuration.
    
    Extracted from existing config.py during restructure.
    """
    default_config = {
        "supported_languages": {
            "en": "English"
        },
        "default": "en"
    }

    loaded_config = load_json_config("lang.json")

    if not loaded_config:
        return default_config

    if "supported_languages" not in loaded_config or "default" not in loaded_config:
        logger.warning("Language configuration file 'lang.json' is malformed. Using default language configuration.")
        return default_config

    return loaded_config
