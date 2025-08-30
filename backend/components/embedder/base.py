"""
Base embedder interface for all embedding provider implementations.

This module defines the common interface that all embedder components
must implement, ensuring consistent behavior across different embedding providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from enum import Enum


class EmbeddingModelType(Enum):
    """Enumeration of supported embedding model types."""
    UNDEFINED = "undefined"
    TEXT = "text"
    CODE = "code"
    MULTIMODAL = "multimodal"


class EmbedderOutput:
    """Standard output format for all embedder operations."""
    
    def __init__(
        self,
        data: Any = None,
        error: Optional[str] = None,
        raw_response: Any = None,
        model_info: Optional[Dict[str, Any]] = None
    ):
        self.data = data
        self.error = error
        self.raw_response = raw_response
        self.model_info = model_info or {}
    
    def __bool__(self) -> bool:
        """Return True if the operation was successful (no error)."""
        return self.error is None
    
    def __str__(self) -> str:
        """String representation of the embedder output."""
        if self.error:
            return f"EmbedderOutput(error='{self.error}')"
        return f"EmbedderOutput(data={type(self.data).__name__}, model_info={self.model_info})"


class BaseEmbedder(ABC):
    """
    Abstract base class for all embedder implementations.
    
    This class defines the common interface that all embedding provider embedders
    must implement, ensuring consistent behavior and error handling.
    """
    
    def __init__(self, **kwargs):
        """Initialize the base embedder with common configuration."""
        self._api_kwargs = {}
        self._model_type = kwargs.get("model_type", EmbeddingModelType.TEXT)
        self._batch_size = kwargs.get("batch_size", 100)
        self._max_retries = kwargs.get("max_retries", 3)
    
    @abstractmethod
    def init_sync_client(self):
        """Initialize the synchronous client for the provider."""
        pass
    
    @abstractmethod
    def init_async_client(self):
        """Initialize the asynchronous client for the provider."""
        pass
    
    @abstractmethod
    def convert_inputs_to_api_kwargs(
        self,
        input: Union[str, List[str]] = None,
        model_kwargs: Dict = None,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> Dict:
        """
        Convert standardized inputs to provider-specific API format.
        
        Args:
            input: The input text or list of texts to embed
            model_kwargs: Additional model-specific parameters
            model_type: The type of embedding model operation to perform
            
        Returns:
            Dict: Provider-specific API parameters
        """
        pass
    
    @abstractmethod
    def call(
        self,
        api_kwargs: Dict = None,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> Any:
        """
        Execute a synchronous call to the embedding provider.
        
        Args:
            api_kwargs: Provider-specific API parameters
            model_type: The type of embedding model operation to perform
            
        Returns:
            Raw response from the embedding provider
        """
        pass
    
    @abstractmethod
    def call_async(
        self,
        api_kwargs: Dict = None,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> Any:
        """
        Execute an asynchronous call to the embedding provider.
        
        Args:
            api_kwargs: Provider-specific API parameters
            model_type: The type of embedding model operation to perform
            
        Returns:
            Raw async response from the embedding provider
        """
        pass
    
    @abstractmethod
    def parse_response(
        self,
        response: Any,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> EmbedderOutput:
        """
        Parse the provider response into standardized format.
        
        Args:
            response: Raw response from the embedding provider
            model_type: The type of embedding model operation performed
            
        Returns:
            EmbedderOutput: Standardized output with embeddings and metadata
        """
        pass
    
    def embed(
        self,
        input: Union[str, List[str]],
        model_kwargs: Optional[Dict] = None,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> EmbedderOutput:
        """
        Generate embeddings for the given input text(s).
        
        Args:
            input: Text or list of texts to embed
            model_kwargs: Additional model-specific parameters
            model_type: The type of embedding model operation to perform
            
        Returns:
            EmbedderOutput: Standardized output with embeddings and metadata
        """
        try:
            # Convert inputs to provider-specific format
            api_kwargs = self.convert_inputs_to_api_kwargs(
                input=input,
                model_kwargs=model_kwargs,
                model_type=model_type
            )
            
            # Make the API call
            response = self.call(api_kwargs=api_kwargs, model_type=model_type)
            
            # Parse and return the response
            return self.parse_response(response, model_type=model_type)
            
        except Exception as e:
            return EmbedderOutput(
                error=f"Embedding failed: {str(e)}",
                data=None
            )
    
    async def embed_async(
        self,
        input: Union[str, List[str]],
        model_kwargs: Optional[Dict] = None,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> EmbedderOutput:
        """
        Generate embeddings asynchronously for the given input text(s).
        
        Args:
            input: Text or list of texts to embed
            model_kwargs: Additional model-specific parameters
            model_type: The type of embedding model operation to perform
            
        Returns:
            EmbedderOutput: Standardized output with embeddings and metadata
        """
        try:
            # Convert inputs to provider-specific format
            api_kwargs = self.convert_inputs_to_api_kwargs(
                input=input,
                model_kwargs=model_kwargs,
                model_type=model_type
            )
            
            # Make the async API call
            response = await self.call_async(api_kwargs=api_kwargs, model_type=model_type)
            
            # Parse and return the response
            return self.parse_response(response, model_type=model_type)
            
        except Exception as e:
            return EmbedderOutput(
                error=f"Async embedding failed: {str(e)}",
                data=None
            )
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current embedding model.
        
        Returns:
            Dict: Model information including name, dimensions, etc.
        """
        return {
            "model_type": self._model_type.value,
            "batch_size": self._batch_size,
            "max_retries": self._max_retries
        }
    
    def set_batch_size(self, batch_size: int) -> None:
        """
        Set the batch size for processing multiple texts.
        
        Args:
            batch_size: Number of texts to process in a single batch
        """
        if batch_size > 0:
            self._batch_size = batch_size
        else:
            raise ValueError("Batch size must be positive")
    
    def set_max_retries(self, max_retries: int) -> None:
        """
        Set the maximum number of retries for failed requests.
        
        Args:
            max_retries: Maximum number of retry attempts
        """
        if max_retries >= 0:
            self._max_retries = max_retries
        else:
            raise ValueError("Max retries must be non-negative")
