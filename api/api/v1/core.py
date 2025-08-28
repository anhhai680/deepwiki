"""
Core API endpoints.

This module contains core API endpoints like root and health check extracted from the main api.py file.
"""

import logging
from datetime import datetime
from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Create router for core endpoints
router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "deepwiki-api"
    }

@router.get("/")
async def root():
    """Root endpoint to check if the API is running and list available endpoints dynamically."""
    # This endpoint will be populated with dynamic endpoint listing
    # when the app is fully configured with all routers
    return {
        "message": "Welcome to DeepWiki API",
        "version": "2.0.0",
        "status": "restructuring",
        "note": "Endpoints are being organized into domain-specific modules"
    }
