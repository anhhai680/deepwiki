"""
API v1 endpoints package.

This package contains all v1 API endpoints organized by domain.
"""

from . import chat, wiki, projects, config, core

__all__ = ["chat", "wiki", "projects", "config", "core"]
