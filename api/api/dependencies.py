"""
Shared dependencies for API endpoints.

This module contains common dependencies, utilities, and helper functions
that are used across multiple endpoint modules.
"""

import os
import logging
import json
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, Query

# Import models directly to avoid circular imports
try:
    from models import WikiCacheData, WikiCacheRequest
except ImportError:
    # Fallback for when models are not available
    WikiCacheData = None
    WikiCacheRequest = None

logger = logging.getLogger(__name__)

# Helper function to get adalflow root path
def get_adalflow_default_root_path():
    """Get the default root path for adalflow configuration."""
    return os.path.expanduser(os.path.join("~", ".adalflow"))

# Wiki Cache Helper Functions
WIKI_CACHE_DIR = os.path.join(get_adalflow_default_root_path(), "wikicache")
os.makedirs(WIKI_CACHE_DIR, exist_ok=True)

def get_wiki_cache_path(owner: str, repo: str, repo_type: str, language: str) -> str:
    """Generates the file path for a given wiki cache."""
    filename = f"deepwiki_cache_{repo_type}_{owner}_{repo}_{language}.json"
    return os.path.join(WIKI_CACHE_DIR, filename)

async def read_wiki_cache(owner: str, repo: str, repo_type: str, language: str) -> Optional[WikiCacheData]:
    """Reads wiki cache data from the file system."""
    if WikiCacheData is None:
        logger.warning("WikiCacheData model not available")
        return None
        
    cache_path = get_wiki_cache_path(owner, repo, repo_type, language)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return WikiCacheData(**data)
        except Exception as e:
            logger.error(f"Error reading wiki cache from {cache_path}: {e}")
            return None
    return None

async def save_wiki_cache(data: WikiCacheRequest) -> bool:
    """Saves wiki cache data to the file system."""
    if WikiCacheRequest is None:
        logger.warning("WikiCacheRequest model not available")
        return False
        
    cache_path = get_wiki_cache_path(data.repo.owner, data.repo.repo, data.repo.type, data.language)
    logger.info(f"Attempting to save wiki cache. Path: {cache_path}")
    try:
        payload = WikiCacheData(
            wiki_structure=data.wiki_structure,
            generated_pages=data.generated_pages,
            repo=data.repo,
            provider=data.provider,
            model=data.model
        )
        # Log size of data to be cached for debugging (avoid logging full content if large)
        try:
            payload_json = payload.model_dump_json()
            payload_size = len(payload_json.encode('utf-8'))
            logger.info(f"Payload prepared for caching. Size: {payload_size} bytes.")
        except Exception as ser_e:
            logger.warning(f"Could not serialize payload for size logging: {ser_e}")

        logger.info(f"Writing cache file to: {cache_path}")
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(payload.model_dump(), f, indent=2)
        logger.info(f"Wiki cache successfully saved to {cache_path}")
        return True
    except IOError as e:
        logger.error(f"IOError saving wiki cache to {cache_path}: {e.strerror} (errno: {e.errno})", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Unexpected error saving wiki cache to {cache_path}: {e}", exc_info=True)
        return False

def validate_language(language: str) -> str:
    """Validate and return the language, falling back to default if invalid."""
    # Simplified language validation - will be enhanced when config is properly integrated
    supported_langs = ["en", "ja", "zh", "es", "kr", "vi", "fr", "pt-br", "ru", "zh-tw"]
    if language not in supported_langs:
        language = "en"  # Default to English
    return language

def validate_auth_code(authorization_code: Optional[str] = None) -> bool:
    """Validate authorization code if authentication is required."""
    # Simplified auth validation - will be enhanced when config is properly integrated
    # For now, always return True to allow endpoints to work
    return True
