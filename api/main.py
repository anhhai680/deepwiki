"""
Main entry point for the DeepWiki API.

This module is the main entry point for the application,
using the new modular app structure.
"""

import os
import argparse
import uvicorn
from .app import create_app

# Create app instance for import compatibility
app = create_app()


def _resolve_port(cli_port: int | None) -> int:
    """Resolve server port from CLI arg or environment, defaulting to 8001.

    Preference order: CLI --port > env PORT > 8001.
    """
    if cli_port is not None:
        return int(cli_port)
    env_port = os.environ.get("PORT")
    if env_port:
        try:
            return int(env_port)
        except ValueError:
            pass
    return 8001


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="Start DeepWiki API server")
    parser.add_argument("--port", type=int, default=None, help="Port to bind the API server")
    parser.add_argument("--host", type=str, default=os.environ.get("HOST", "0.0.0.0"), help="Host to bind")
    args = parser.parse_args()

    app = create_app()

    # Determine runtime settings
    port = _resolve_port(args.port)
    host = args.host
    reload = os.environ.get("RELOAD", "false").lower() in {"1", "true", "yes", "y"}

    # Run the application
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    main()
