"""
Custom exception classes for the DeepWiki API.

This module contains custom exception classes extracted
from existing error handling during the restructure.
"""

from typing import Optional, Dict, Any


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


class OllamaModelNotFoundError(Exception):
    """Raised when an Ollama model is not found."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        super().__init__(f"Ollama model '{model_name}' not found. Please run 'ollama pull {model_name}' to install it.")


class EmbeddingError(DeepWikiException):
    """Raised when embedding operations fail."""
    pass


class AuthenticationError(DeepWikiException):
    """Raised when authentication fails."""
    pass


class RepositoryError(DeepWikiException):
    """Raised when repository operations fail."""
    pass


class FileProcessingError(DeepWikiException):
    """Raised when file processing fails."""
    pass


class ModelConfigurationError(DeepWikiException):
    """Raised when model configuration is invalid."""
    pass


class StreamingError(DeepWikiException):
    """Raised when streaming operations fail."""
    pass


class CacheError(DeepWikiException):
    """Raised when cache operations fail."""
    pass


class ExportError(DeepWikiException):
    """Raised when export operations fail."""
    pass


# HTTP-specific exceptions (for API layer)
class HTTPException(DeepWikiException):
    """Base class for HTTP exceptions."""
    
    def __init__(self, status_code: int, detail: str, error_code: str = None, details: dict = None):
        self.status_code = status_code
        super().__init__(detail, error_code, details)


class BadRequestError(HTTPException):
    """400 Bad Request error."""
    
    def __init__(self, detail: str, error_code: str = None, details: dict = None):
        super().__init__(400, detail, error_code, details)


class UnauthorizedError(HTTPException):
    """401 Unauthorized error."""
    
    def __init__(self, detail: str, error_code: str = None, details: dict = None):
        super().__init__(401, detail, error_code, details)


class NotFoundError(HTTPException):
    """404 Not Found error."""
    
    def __init__(self, detail: str, error_code: str = None, details: dict = None):
        super().__init__(404, detail, error_code, details)


class InternalServerError(HTTPException):
    """500 Internal Server Error."""
    
    def __init__(self, detail: str, error_code: str = None, details: dict = None):
        super().__init__(500, detail, error_code, details)


# Utility functions for exception handling
def create_error_response(
    status_code: int, 
    message: str, 
    error_code: str = None, 
    details: dict = None
) -> Dict[str, Any]:
    """Create a standardized error response."""
    response = {
        "status": "error",
        "message": message,
        "status_code": status_code
    }
    
    if error_code:
        response["error_code"] = error_code
    
    if details:
        response["details"] = details
    
    return response


def handle_exception(e: Exception) -> Dict[str, Any]:
    """Handle exceptions and return standardized error responses."""
    if isinstance(e, HTTPException):
        return create_error_response(
            e.status_code, 
            e.message, 
            e.error_code, 
            e.details
        )
    elif isinstance(e, DeepWikiException):
        return create_error_response(
            500, 
            e.message, 
            e.error_code, 
            e.details
        )
    else:
        return create_error_response(
            500, 
            "Internal server error", 
            "internal_error", 
            {"exception_type": type(e).__name__}
        )
