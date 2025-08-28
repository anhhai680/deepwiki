"""
Projects API endpoints.

This module contains all project-related API endpoints extracted from the main api.py file.
"""

import os
import asyncio
import logging
from typing import List
from fastapi import APIRouter, HTTPException

from models import ProcessedProjectEntry
from api.dependencies import WIKI_CACHE_DIR

logger = logging.getLogger(__name__)

# Create router for project endpoints
router = APIRouter()

@router.get("/api/processed_projects", response_model=List[ProcessedProjectEntry])
async def get_processed_projects():
    """
    Lists all processed projects found in the wiki cache directory.
    Projects are identified by files named like: deepwiki_cache_{repo_type}_{owner}_{repo}_{language}.json
    """
    project_entries: List[ProcessedProjectEntry] = []

    try:
        if not os.path.exists(WIKI_CACHE_DIR):
            logger.info(f"Cache directory {WIKI_CACHE_DIR} not found. Returning empty list.")
            return []

        logger.info(f"Scanning for project cache files in: {WIKI_CACHE_DIR}")
        filenames = await asyncio.to_thread(os.listdir, WIKI_CACHE_DIR) # Use asyncio.to_thread for os.listdir

        for filename in filenames:
            if filename.startswith("deepwiki_cache_") and filename.endswith(".json"):
                file_path = os.path.join(WIKI_CACHE_DIR, filename)
                try:
                    stats = await asyncio.to_thread(os.stat, file_path) # Use asyncio.to_thread for os.stat
                    parts = filename.replace("deepwiki_cache_", "").replace(".json", "").split('_')

                    # Expecting repo_type_owner_repo_language
                    # Example: deepwiki_cache_github_AsyncFuncAI_deepwiki-open_en.json
                    # parts = [github, AsyncFuncAI, deepwiki-open, en]
                    if len(parts) >= 4:
                        repo_type = parts[0]
                        owner = parts[1]
                        language = parts[-1] # language is the last part
                        repo = "_".join(parts[2:-1]) # repo can contain underscores

                        project_entries.append(
                            ProcessedProjectEntry(
                                id=filename,
                                owner=owner,
                                repo=repo,
                                name=f"{owner}/{repo}",
                                repo_type=repo_type,
                                submittedAt=int(stats.st_mtime * 1000), # Convert to milliseconds
                                language=language
                            )
                        )
                    else:
                        logger.warning(f"Could not parse project details from filename: {filename}")
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    continue # Skip this file on error

        # Sort by most recent first
        project_entries.sort(key=lambda p: p.submittedAt, reverse=True)
        logger.info(f"Found {len(project_entries)} processed project entries.")
        return project_entries

    except Exception as e:
        logger.error(f"Error listing processed projects from {WIKI_CACHE_DIR}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list processed projects from server cache.")
