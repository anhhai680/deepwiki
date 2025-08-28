"""
Pytest configuration and shared fixtures.

Provides common fixtures for FastAPI app, HTTP client, repo_url/query
defaults, and environment isolation.
"""

import os
import asyncio
import contextlib
from typing import AsyncIterator, Iterator

import pytest


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture(scope="session")
def fastapi_app():
    """Provide the FastAPI app without starting a server."""
    from api.app import create_app

    return create_app()


@pytest.fixture()
async def http_client(fastapi_app) -> AsyncIterator["httpx.AsyncClient"]:
    """ASGI test client for the FastAPI app (no network)."""
    import httpx

    async with httpx.AsyncClient(app=fastapi_app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session")
def repo_url() -> str:
    """Default repository URL used by tests that accept a repo_url fixture."""
    return os.environ.get("TEST_REPO_URL", "https://github.com/deepwikis/sample-repo")


@pytest.fixture(scope="session")
def query() -> str:
    """Default query used by tests that accept a query fixture."""
    return os.environ.get("TEST_QUERY", "Explain the purpose of this repository.")


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch):
    """Isolate environment-dependent settings for each test.

    Ensures tests do not depend on real API keys or user-specific paths.
    """
    # Avoid accidental calls to external providers by default
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("DEEPWIKI_ENV", "test")

    # Ensure adalflow cache directory uses a temp-like home if needed
    monkeypatch.setenv("HOME", os.environ.get("HOME", "/tmp"))

    yield


