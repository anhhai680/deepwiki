"""
FastAPI application configuration.

This module contains the FastAPI app configuration
extracted from the existing api.py file during the restructure.
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime

# Configure logging
from backend.logging_config import setup_logging

# Setup logging first
setup_logging()
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


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    This function configures the FastAPI app with all domain-specific routers
    and middleware extracted from the existing api.py file during the restructure.
    """
    
    # Create FastAPI app instance
    app = FastAPI(
        title="DeepWiki API",
        description="AI-powered documentation generator API with RAG optimization",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configured from original api.py
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add dedicated health endpoint for Docker and external health checks
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "deepwiki-api"
        }
    
    # Include domain-specific routers
    try:
        from backend.api.v1 import core, config as config_router, chat, wiki, projects
        logger.info("Including core router...")
        app.include_router(core.router, prefix="/api", tags=["core"])
        logger.info("Including config router...")
        app.include_router(config_router.router, prefix="/api", tags=["configuration"])
        logger.info("Including chat router...")
        app.include_router(chat.router, prefix="/api", tags=["chat"])
        logger.info("Including wiki router...")
        app.include_router(wiki.router, prefix="/api", tags=["wiki"])
        logger.info("Including projects router...")
        app.include_router(projects.router, prefix="/api", tags=["projects"])
        logger.info("All routers included successfully")
        
        # Log all registered routes for debugging
        logger.info("Registered routes:")
        for route in app.routes:
            if hasattr(route, 'path'):
                logger.info(f"  {route.path}")
            elif hasattr(route, 'routes'):
                for subroute in route.routes:
                    if hasattr(subroute, 'path'):
                        logger.info(f"  {subroute.path}")
    except Exception as import_error:
        logger.error(f"Error including routers: {import_error}")
        # Fallback minimal endpoints to keep app responsive
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "deepwiki-api"
            }

        @app.get("/")
        async def root():
            return {
                "message": "Welcome to DeepWiki API",
                "version": "2.0.0",
                "status": "degraded",
                "note": "Routers failed to load; running fallback endpoints",
                "docs_url": "/docs",
                "redoc_url": "/redoc"
            }
    
    return app
