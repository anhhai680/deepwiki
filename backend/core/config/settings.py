"""
Application settings and configuration management.

This module contains the configuration settings extracted from
the existing config.py file.
"""

import os
from typing import Dict, Any, Optional, List

# Try to import from pydantic-settings, fallback to simple class
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, ConfigDict
    PYDANTIC_AVAILABLE = True
except ImportError:
    try:
        from pydantic import BaseSettings, Field, ConfigDict
        PYDANTIC_AVAILABLE = True
    except ImportError:
        PYDANTIC_AVAILABLE = False


if PYDANTIC_AVAILABLE:
    class Settings(BaseSettings):
        """
        Application configuration settings.
        
        Extracted from the existing config.py file during restructure.
        """
        
        # API Keys
        openai_api_key: Optional[str] = Field(default=None, json_schema_extra={"env": "OPENAI_API_KEY"})
        google_api_key: Optional[str] = Field(default=None, json_schema_extra={"env": "GOOGLE_API_KEY"})
        openrouter_api_key: Optional[str] = Field(default=None, json_schema_extra={"env": "OPENROUTER_API_KEY"})
        aws_access_key_id: Optional[str] = Field(default=None, json_schema_extra={"env": "AWS_ACCESS_KEY_ID"})
        aws_secret_access_key: Optional[str] = Field(default=None, json_schema_extra={"env": "AWS_SECRET_ACCESS_KEY"})
        aws_region: Optional[str] = Field(default=None, json_schema_extra={"env": "AWS_REGION"})
        aws_role_arn: Optional[str] = Field(default=None, json_schema_extra={"env": "AWS_ROLE_ARN"})
        
        # Wiki authentication settings
        wiki_auth_mode: bool = Field(default=False, json_schema_extra={"env": "DEEPWIKI_AUTH_MODE"})
        wiki_auth_code: str = Field(default="", json_schema_extra={"env": "DEEPWIKI_AUTH_CODE"})
        
        # Configuration directory
        config_dir: Optional[str] = Field(default=None, json_schema_extra={"env": "DEEPWIKI_CONFIG_DIR"})
        
        # Logging configuration
        log_level: str = Field(default="INFO", json_schema_extra={"env": "LOG_LEVEL"})
        log_file_path: Optional[str] = Field(default=None, json_schema_extra={"env": "LOG_FILE_PATH"})
        log_max_size: int = Field(default=10, json_schema_extra={"env": "LOG_MAX_SIZE"})  # MB
        log_backup_count: int = Field(default=5, json_schema_extra={"env": "LOG_BACKUP_COUNT"})
        
        # Use ConfigDict for Pydantic 2.x
        model_config = ConfigDict(
            env_file=".env",
            case_sensitive=False,
            extra="ignore"  # Allow extra fields from environment
        )
else:
    # Fallback to simple class without Pydantic
    class Settings:
        """
        Application configuration settings (fallback without Pydantic).
        
        Extracted from the existing config.py file during restructure.
        """
        
        def __init__(self):
            # API Keys
            self.openai_api_key = os.environ.get('OPENAI_API_KEY')
            self.google_api_key = os.environ.get('GOOGLE_API_KEY')
            self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
            self.aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
            self.aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
            self.aws_region = os.environ.get('AWS_REGION')
            self.aws_role_arn = os.environ.get('AWS_ROLE_ARN')
            
            # Wiki authentication settings
            raw_auth_mode = os.environ.get('DEEPWIKI_AUTH_MODE', 'False')
            self.wiki_auth_mode = raw_auth_mode.lower() in ['true', '1', 't']
            self.wiki_auth_code = os.environ.get('DEEPWIKI_AUTH_CODE', '')
            
            # Configuration directory
            self.config_dir = os.environ.get('DEEPWIKI_CONFIG_DIR')
            
            # Logging configuration
            self.log_level = os.environ.get('LOG_LEVEL', 'INFO')
            self.log_file_path = os.environ.get('LOG_FILE_PATH')
            self.log_max_size = int(os.environ.get('LOG_MAX_SIZE', 10))
            self.log_backup_count = int(os.environ.get('LOG_BACKUP_COUNT', 5))


# Default excluded directories and files
DEFAULT_EXCLUDED_DIRS: List[str] = [
    # Virtual environments and package managers
    "./.venv/", "./venv/", "./env/", "./virtualenv/",
    "./node_modules/", "./bower_components/", "./jspm_packages/",
    # Version control
    "./.git/", "./.svn/", "./.hg/", "./.bzr/",
    # Cache and compiled files
    "./__pycache__/", "./.pytest_cache/", "./.mypy_cache/", "./.ruff_cache/", "./.coverage/",
    # Build and distribution
    "./dist/", "./build/", "./out/", "./target/", "./bin/", "./obj/",
    # Documentation
    "./docs/", "./_docs/", "./site-docs/", "./_site/",
    # IDE specific
    "./.idea/", "./.vscode/", "./.vs/", "./.eclipse/", "./.settings/",
    # Logs and temporary files
    "./logs/", "./log/", "./tmp/", "./temp/",
]

DEFAULT_EXCLUDED_FILES: List[str] = [
    "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json", "poetry.lock",
    "Pipfile.lock", "requirements.txt.lock", "Cargo.lock", "composer.lock",
    ".lock", ".DS_Store", "Thumbs.db", "desktop.ini", "*.lnk", ".env",
    ".env.*", "*.env", "*.cfg", "*.ini", ".flaskenv", ".gitignore",
    ".gitattributes", ".gitmodules", ".github", ".gitlab-ci.yml",
    ".prettierrc", ".eslintrc", ".eslintignore", ".stylelintrc",
    ".editorconfig", ".jshintrc", ".pylintrc", ".flake8", "mypy.ini",
    "pyproject.toml", "tsconfig.json", "webpack.config.js", "babel.config.js",
    "rollup.config.js", "jest.config.js", "karma.conf.js", "vite.config.js",
    "next.config.js", "*.min.js", "*.min.css", "*.bundle.js", "*.bundle.css",
    "*.map", "*.gz", "*.zip", "*.tar", "*.tgz", "*.rar", "*.7z", "*.iso",
    "*.dmg", "*.img", "*.msix", "*.appx", "*.appxbundle", "*.xap", "*.ipa",
    "*.deb", "*.rpm", "*.msi", "*.exe", "*.dll", "*.so", "*.dylib", "*.o",
    "*.obj", "*.jar", "*.war", "*.ear", "*.jsm", "*.class", "*.pyc", "*.pyd",
    "*.pyo", "__pycache__", "*.a", "*.lib", "*.lo", "*.la", "*.slo", "*.dSYM",
    "*.egg", "*.egg-info", "*.dist-info", "*.eggs", "node_modules",
    "bower_components", "jspm_packages", "lib-cov", "coverage", "htmlcov",
    ".nyc_output", ".tox", "dist", "build", "bld", "out", "bin", "target",
    "packages/*/dist", "packages/*/build", ".output"
]


# Global settings instance
settings = Settings()

# Global configs dictionary for backward compatibility
configs = {
    "lang_config": {
        "default": "en",
        "supported_languages": {
            "en": "English"
        }
    },
    "file_filters": {
        "excluded_dirs": DEFAULT_EXCLUDED_DIRS,
        "excluded_files": DEFAULT_EXCLUDED_FILES
    },
    "embedder": {},
    "retriever": {},
    "text_splitter": {},
    "generator": {}
}

# Environment variable access for backward compatibility
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')
AWS_ROLE_ARN = os.environ.get('AWS_ROLE_ARN')

def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def update_settings(config_dict: Dict[str, Any]) -> None:
    """Update settings with new configuration."""
    for key, value in config_dict.items():
        if hasattr(settings, key):
            setattr(settings, key, value)


def get_excluded_dirs() -> List[str]:
    """Get the list of excluded directories."""
    return DEFAULT_EXCLUDED_DIRS.copy()


def get_excluded_files() -> List[str]:
    """Get the list of excluded files."""
    return DEFAULT_EXCLUDED_FILES.copy()


def get_model_config(provider: str = "google", model: str = None) -> Dict[str, Any]:
    """
    Get model configuration for the specified provider.
    
    Args:
        provider: The AI provider (e.g., 'openai', 'google', 'azure')
        model: The specific model name (optional)
        
    Returns:
        Dictionary containing model configuration
    """
    # Default configuration
    default_config = {
        "model_kwargs": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_tokens": 4000
        }
    }
    
    # Provider-specific configurations
    provider_configs = {
        "openai": {
            "model": "gpt-4.1-mini",
            "model_kwargs": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 4000
            }
        },
        "google": {
            "model": "gemini-2.5-flash",
            "model_kwargs": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_tokens": 4000
            }
        },
        "azure": {
            "model": "gpt-4.1-mini",
            "model_kwargs": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 4000
            }
        },
        "openrouter": {
            "model": "openai/gpt-4.1-mini",
            "model_kwargs": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 4000
            }
        },
        "bedrock": {
            "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "model_kwargs": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 4000
            }
        },
        "dashscope": {
            "model": "qwen-plus",
            "model_kwargs": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 4000
            }
        },
        "ollama": {
            "model": "qwen3:4b",
            "model_kwargs": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 4000
            }
        }
    }
    
    # Get provider config or use default
    provider_config = provider_configs.get(provider, default_config)
    
    # If model is specified, try to get model-specific config
    if model and provider in configs.get("generator", {}).get("providers", {}):
        model_config = configs["generator"]["providers"][provider].get("models", {}).get(model, {})
        if model_config:
            # Merge provider config with model-specific config
            merged_config = provider_config.copy()
            if "model_kwargs" in model_config:
                merged_config["model_kwargs"].update(model_config["model_kwargs"])
            if "model" in model_config:
                merged_config["model"] = model_config["model"]
            return merged_config
    
    return provider_config


def get_embedder_config() -> Dict[str, Any]:
    """
    Get embedder configuration.
    
    Returns:
        Dictionary containing embedder configuration
    """
    return configs.get("embedder", {})


def is_ollama_embedder() -> bool:
    """
    Check if Ollama is being used as the embedder.
    
    Returns:
        True if Ollama embedder is configured, False otherwise
    """
    embedder_config = get_embedder_config()
    return embedder_config.get("embedder", {}).get("provider", "").lower() == "ollama"
