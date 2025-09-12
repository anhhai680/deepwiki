"""
Configuration Utilities

This module contains utility functions for configuration loading, processing, and management
extracted from various components throughout the codebase.
"""

import os
import json
import re
import logging
from pathlib import Path
from typing import Dict, Any, Union, List, Optional

logger = logging.getLogger(__name__)


def replace_env_placeholders(config: Union[Dict[str, Any], List[Any], str, Any]) -> Union[Dict[str, Any], List[Any], str, Any]:
    """
    Recursively replace placeholders like "${ENV_VAR}" in string values
    within a nested configuration structure with environment variable values.
    
    Args:
        config: Configuration data (dict, list, string, or other types)
        
    Returns:
        Configuration with environment variable placeholders replaced
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


def load_json_config(filename: str, config_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Load JSON configuration file with environment variable substitution.
    
    Args:
        filename (str): Name of the configuration file
        config_dir (str, optional): Directory containing configuration files
        
    Returns:
        Dict[str, Any]: Loaded configuration
    """
    try:
        # If environment variable is set, use the directory specified by it
        if config_dir:
            config_path = Path(config_dir) / filename
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
    
    Args:
        client_classes (Dict[str, Any]): Dictionary of available client classes
        
    Returns:
        Dict[str, Any]: Generator configuration with client classes
    """
    generator_config = load_json_config("generator.json")

    # Add client classes to each provider
    if "providers" in generator_config:
        for provider_id, provider_config in generator_config["providers"].items():
            # Try to set client class from client_class
            if provider_config.get("client_class") in client_classes:
                provider_config["model_client"] = client_classes[provider_config["client_class"]]
            # Fall back to default mapping based on provider_id
            elif provider_id in ["google", "openai", "openrouter", "ollama", "bedrock", "azure", "dashscope", "privatemodel"]:
                default_map = {
                    "google": client_classes.get("GoogleGenAIClient"),
                    "openai": client_classes.get("OpenAIGenerator"),
                    "openrouter": client_classes.get("OpenRouterGenerator"),
                    "ollama": client_classes.get("OllamaGenerator"),
                    "bedrock": client_classes.get("BedrockGenerator"),
                    "azure": client_classes.get("AzureAIGenerator"),
                    "dashscope": client_classes.get("DashScopeGenerator"),
                    "privatemodel": client_classes.get("PrivateModelGenerator")
                }
                provider_config["model_client"] = default_map[provider_id]
            else:
                logger.warning(f"Unknown provider or client class: {provider_id}")

    return generator_config


def load_embedder_config(client_classes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load embedder configuration.
    
    Args:
        client_classes (Dict[str, Any]): Dictionary of available client classes
        
    Returns:
        Dict[str, Any]: Embedder configuration with client classes
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
    
    Returns:
        Dict[str, Any]: Repository configuration
    """
    return load_json_config("repo.json")


def load_lang_config() -> Dict[str, Any]:
    """
    Load language configuration.
    
    Returns:
        Dict[str, Any]: Language configuration
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


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get a configuration value using dot notation path.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        key_path (str): Dot-separated path to the configuration value
        default (Any): Default value if key is not found
        
    Returns:
        Any: Configuration value or default
    """
    keys = key_path.split('.')
    current = config
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def set_config_value(config: Dict[str, Any], key_path: str, value: Any) -> bool:
    """
    Set a configuration value using dot notation path.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary to modify
        key_path (str): Dot-separated path to the configuration value
        value (Any): Value to set
        
    Returns:
        bool: True if value was set successfully
    """
    keys = key_path.split('.')
    current = config
    
    # Navigate to the parent of the target key
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # Set the value
    current[keys[-1]] = value
    return True


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries, with override_config taking precedence.
    
    Args:
        base_config (Dict[str, Any]): Base configuration
        override_config (Dict[str, Any]): Configuration to override with
        
    Returns:
        Dict[str, Any]: Merged configuration
    """
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


def validate_config_structure(config: Dict[str, Any], required_keys: List[str]) -> bool:
    """
    Validate that a configuration has all required keys.
    
    Args:
        config (Dict[str, Any]): Configuration to validate
        required_keys (List[str]): List of required keys
        
    Returns:
        bool: True if all required keys are present
    """
    for key in required_keys:
        if key not in config:
            logger.error(f"Configuration missing required key: {key}")
            return False
    
    return True


def get_environment_config() -> Dict[str, Any]:
    """
    Get configuration from environment variables.
    
    Returns:
        Dict[str, Any]: Environment-based configuration
    """
    config = {}
    
    # Common configuration keys
    env_mappings = {
        "OPENAI_API_KEY": "openai.api_key",
        "GOOGLE_API_KEY": "google.api_key",
        "AZURE_OPENAI_API_KEY": "azure.api_key",
        "AZURE_OPENAI_ENDPOINT": "azure.endpoint",
        "OLLAMA_BASE_URL": "ollama.base_url",
        "LOG_LEVEL": "logging.level",
        "LOG_FILE_PATH": "logging.file_path"
    }
    
    for env_var, config_path in env_mappings.items():
        value = os.environ.get(env_var)
        if value:
            set_config_value(config, config_path, value)
    
    return config


def save_config_to_file(config: Dict[str, Any], filepath: str) -> bool:
    """
    Save configuration to a JSON file.
    
    Args:
        config (Dict[str, Any]): Configuration to save
        filepath (str): Path to the file to save to
        
    Returns:
        bool: True if configuration was saved successfully
    """
    try:
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Configuration saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration to {filepath}: {e}")
        return False


def reload_config(config_file: str, config_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Reload configuration from file, clearing any cached values.
    
    Args:
        config_file (str): Name of the configuration file
        config_dir (str, optional): Directory containing configuration files
        
    Returns:
        Dict[str, Any]: Reloaded configuration
    """
    logger.info(f"Reloading configuration from {config_file}")
    
    # Clear any cached configuration
    if hasattr(reload_config, '_cache'):
        reload_config._cache.clear()
    
    return load_json_config(config_file, config_dir)


def get_config_summary(config: Dict[str, Any], max_depth: int = 3) -> Dict[str, Any]:
    """
    Get a summary of configuration structure and values.
    
    Args:
        config (Dict[str, Any]): Configuration to summarize
        max_depth (int): Maximum depth to traverse
        
    Returns:
        Dict[str, Any]: Configuration summary
    """
    def summarize_dict(d: Dict[str, Any], depth: int = 0) -> Dict[str, Any]:
        if depth >= max_depth:
            return {"type": "dict", "keys": list(d.keys()), "depth_limit_reached": True}
        
        summary = {"type": "dict", "keys": {}}
        for key, value in d.items():
            if isinstance(value, dict):
                summary["keys"][key] = summarize_dict(value, depth + 1)
            elif isinstance(value, list):
                summary["keys"][key] = {"type": "list", "length": len(value)}
            else:
                summary["keys"][key] = {"type": type(value).__name__, "value": str(value)[:100]}
        
        return summary
    
    return summarize_dict(config)
