"""
Configuration API endpoints.

This module contains all configuration-related API endpoints extracted from the main api.py file.
"""

import logging
from fastapi import APIRouter

from models import ModelConfig, Provider, Model

logger = logging.getLogger(__name__)

# Create router for configuration endpoints
router = APIRouter()

@router.get("/lang/config")
async def get_lang_config():
    """Get language configuration."""
    # Simplified language config - will be enhanced when full config is integrated
    return {
        "supported_languages": ["en", "ja", "zh", "es", "kr", "vi", "fr", "pt-br", "ru", "zh-tw"],
        "default": "en"
    }

@router.get("/auth/status")
async def get_auth_status():
    """
    Check if authentication is required for the wiki.
    """
    # Simplified auth status - will be enhanced when full config is integrated
    return {"auth_required": False}

@router.post("/auth/validate")
async def validate_auth_code(request):
    """
    Check authorization code.
    """
    # Simplified auth validation - will be enhanced when full config is integrated
    return {"success": True}

@router.get("/models/config", response_model=ModelConfig)
async def get_model_config():
    """
    Get available model providers and their models.

    This endpoint returns the configuration of available model providers and their
    respective models that can be used throughout the application.

    Returns:
        ModelConfig: A configuration object containing providers and their models
    """
    try:
        logger.info("Fetching model configurations")

        # Simplified model config - will be enhanced when full config is integrated
        providers = [
            Provider(
                id="google",
                name="Google",
                supportsCustomModel=True,
                models=[
                    Model(id="gemini-2.5-flash", name="Gemini 2.5 Flash")
                ]
            ),
            Provider(
                id="openai",
                name="OpenAI",
                supportsCustomModel=False,
                models=[
                    Model(id="gpt-4", name="GPT-4"),
                    Model(id="gpt-3.5-turbo", name="GPT-3.5 Turbo")
                ]
            ),
            Provider(
                id="ollama",
                name="Ollama",
                supportsCustomModel=True,
                models=[
                    Model(id="llama3", name="Llama 3"),
                    Model(id="mistral", name="Mistral")
                ]
            )
        ]

        # Create and return the configuration
        config = ModelConfig(
            providers=providers,
            defaultProvider="google"
        )
        return config

    except Exception as e:
        logger.error(f"Error creating model configuration: {str(e)}")
        # Return some default configuration in case of error
        return ModelConfig(
            providers=[
                Provider(
                    id="google",
                    name="Google",
                    supportsCustomModel=True,
                    models=[
                        Model(id="gemini-2.5-flash", name="Gemini 2.5 Flash")
                    ]
                )
            ],
            defaultProvider="google"
        )
