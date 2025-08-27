"""
Main entry point for the DeepWiki API.

This module will be the main entry point for the application,
replacing the current main.py functionality.
"""

import uvicorn
from fastapi import FastAPI
from .app import create_app


def main():
    """Main application entry point."""
    app = create_app()
    
    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()
