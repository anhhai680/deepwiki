"""
Configuration API endpoints.

This module contains all configuration-related API endpoints extracted from the main api.py file.
"""

import logging
from fastapi import APIRouter

from ...models import ModelConfig, Provider, Model
from ...core.config.manager import get_config_manager

logger = logging.getLogger(__name__)

# Create router for configuration endpoints
router = APIRouter()

@router.get("/lang/config")
async def get_lang_config():
    """Get language configuration."""
    # Simplified language config - will be enhanced when full config is integrated
    return {
        "supported_languages": ["en", "vi"],
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
        # Load dynamic generator configuration
        cfg_manager = get_config_manager()
        generator_cfg = cfg_manager.get_generator_config()

        providers_cfg = generator_cfg.get("providers", {}) or {}
        default_provider = generator_cfg.get("default_provider", "openai")

        # Friendly names for known providers; fallback to capitalized id
        provider_names = {
            "google": "Google",
            "openai": "OpenAI",
            "openrouter": "OpenRouter",
            "ollama": "Ollama",
            "bedrock": "Bedrock",
            "azure": "Azure AI",
            "dashscope": "DashScope",
            "privatemodel": "Private Model",
        }

        providers: list[Provider] = []
        for pid, pcfg in providers_cfg.items():
            models_cfg = (pcfg.get("models") or {})
            model_list = [
                Model(id=mid, name=mid) for mid in models_cfg.keys()
            ]
            
            # Get the default model for this provider
            default_model = pcfg.get("default_model")

            providers.append(
                Provider(
                    id=pid,
                    name=provider_names.get(pid, pid.capitalize()),
                    supportsCustomModel=bool(pcfg.get("supportsCustomModel", False)),
                    models=model_list,
                    defaultModel=default_model,
                )
            )

        return ModelConfig(providers=providers, defaultProvider=default_provider)

    except Exception as e:
        logger.error(f"Error creating model configuration: {str(e)}")
        # Return some default configuration in case of error
        return ModelConfig(
            providers=[
                Provider(
                    id="google",
                    name="Google",
                    supportsCustomModel=True,
                    defaultModel="gemini-2.5-flash",
                    models=[
                        Model(id="gemini-2.5-flash", name="Gemini 2.5 Flash")
                    ]
                )
            ],
            defaultProvider="google"
        )
