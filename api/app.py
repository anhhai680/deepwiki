"""
FastAPI application configuration.

This module contains the FastAPI app configuration
extracted from the existing api.py file during the restructure.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all routers
from api.v1 import chat, wiki, projects, config, core


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
    
    # TODO: Add dependency injection container when properly configured
    # container = get_container()
    # container.wire(modules=[...])
    
    # Include all domain-specific routers
    app.include_router(core.router, tags=["core"])
    app.include_router(config.router, tags=["configuration"])
    app.include_router(chat.router, tags=["chat"])
    app.include_router(wiki.router, tags=["wiki"])
    app.include_router(projects.router, tags=["projects"])
    
    return app
