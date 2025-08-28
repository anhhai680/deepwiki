"""
Main entry point for the DeepWiki API.

This module is the main entry point for the application,
using the new modular app structure.
"""

import uvicorn
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
