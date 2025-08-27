"""
FastAPI application configuration.

This module will contain the FastAPI app configuration
extracted from the existing api.py file during the restructure.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .container import get_container


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    This function will be populated with app configuration
    extracted from the existing api.py file during the restructure.
    """
    
    # Create FastAPI app instance
    app = FastAPI(
        title="DeepWiki API",
        description="AI-powered documentation generator API with RAG optimization",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware (placeholder - will be configured during restructure)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Will be configured properly during restructure
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Get dependency injection container
    container = get_container()
    
    # Wire container to app (will be implemented during restructure)
    # container.wire(modules=[...])
    
    # Include routers (will be added during restructure)
    # from .api.v1 import chat, wiki, projects
    # app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
    # app.include_router(wiki.router, prefix="/api/v1", tags=["wiki"])
    # app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {"message": "DeepWiki API v2.0.0", "status": "restructuring"}
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": "2.0.0"}
    
    return app
