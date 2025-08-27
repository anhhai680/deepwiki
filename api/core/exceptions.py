"""
Custom exception classes for the DeepWiki API.

This module will contain custom exception classes extracted
from existing error handling during the restructure.
"""


class DeepWikiException(Exception):
    """Base exception for all DeepWiki API errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ConfigurationError(DeepWikiException):
    """Raised when there's a configuration error."""
    pass


class ProviderError(DeepWikiException):
    """Raised when there's an AI provider error."""
    pass


class ValidationError(DeepWikiException):
    """Raised when input validation fails."""
    pass


class ProcessingError(DeepWikiException):
    """Raised when data processing fails."""
    pass


class RetrievalError(DeepWikiException):
    """Raised when information retrieval fails."""
    pass


class GenerationError(DeepWikiException):
    """Raised when text generation fails."""
    pass


class MemoryError(DeepWikiException):
    """Raised when memory operations fail."""
    pass
