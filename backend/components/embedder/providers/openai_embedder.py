"""
OpenAI embedder implementation.

This module provides embedding functionality using OpenAI's embedding models
through the existing OpenAI client infrastructure.
"""

import logging
from typing import Dict, Any, Optional, Union, List
import os

from backend.components.embedder.base import BaseEmbedder, EmbeddingModelType, EmbedderOutput
from backend.core.types import EmbeddingVector
from backend.components.generator.providers.openai_generator import OpenAIGenerator

log = logging.getLogger(__name__)


class OpenAIEmbedder(BaseEmbedder):
    """
    OpenAI embedder implementation using OpenAI's embedding models.
    
    This embedder leverages the existing OpenAI client infrastructure
    to generate embeddings for text inputs.
    """
    
    def __init__(self, **kwargs):
        """Initialize the OpenAI embedder."""
        super().__init__(**kwargs)
        self._sync_client = None
        self._async_client = None
        self._model_name = kwargs.get("model", "text-embedding-3-small")
        self._dimensions = kwargs.get("dimensions", 256)
        self._encoding_format = kwargs.get("encoding_format", "float")
        
        # Initialize clients
        self.init_sync_client()
        self.init_async_client()
    
    def init_sync_client(self):
        """Initialize the synchronous OpenAI client."""
        try:
            self._sync_client = OpenAIGenerator()
            log.debug("Initialized OpenAI sync client for embeddings")
        except Exception as e:
            log.error(f"Failed to initialize OpenAI sync client: {e}")
            self._sync_client = None
    
    def init_async_client(self):
        """Initialize the asynchronous OpenAI client."""
        try:
            self._async_client = OpenAIGenerator()
            log.debug("Initialized OpenAI async client for embeddings")
        except Exception as e:
            log.error(f"Failed to initialize OpenAI async client: {e}")
            self._async_client = None
    
    def convert_inputs_to_api_kwargs(
        self,
        input: Union[str, List[str]] = None,
        model_kwargs: Dict = None,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> Dict:
        """
        Convert standardized inputs to OpenAI API format.
        
        Args:
            input: Text or list of texts to embed
            model_kwargs: Additional model-specific parameters
            model_type: The type of embedding model operation to perform
            
        Returns:
            Dict: OpenAI API parameters
        """
        if not input:
            raise ValueError("Input text is required for embedding")
        
        # Prepare the API parameters
        api_kwargs = {
            "input": input,
            "model": self._model_name,
            "encoding_format": self._encoding_format
        }
        
        # Add dimensions if specified and supported by the model
        if self._dimensions and "text-embedding-3" in self._model_name:
            api_kwargs["dimensions"] = self._dimensions
        
        # Override with any provided model_kwargs
        if model_kwargs:
            api_kwargs.update(model_kwargs)
        
        # Ensure input is properly formatted
        if isinstance(input, str):
            api_kwargs["input"] = [input]
        
        return api_kwargs
    
    def call(
        self,
        api_kwargs: Dict = None,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> Any:
        """
        Execute a synchronous call to OpenAI's embedding API.
        
        Args:
            api_kwargs: OpenAI API parameters
            model_type: The type of embedding model operation to perform
            
        Returns:
            Raw response from OpenAI's embedding API
        """
        if not self._sync_client:
            raise RuntimeError("OpenAI sync client not initialized")
        
        try:
            # Use the existing OpenAI client's embedding functionality
            response = self._sync_client.call(api_kwargs=api_kwargs, model_type=EmbeddingModelType.TEXT)
            log.debug(f"OpenAI embedding response received: {type(response)}")
            return response
        except Exception as e:
            log.error(f"OpenAI embedding API call failed: {e}")
            raise
    
    async def call_async(
        self,
        api_kwargs: Dict = None,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> Any:
        """
        Execute an asynchronous call to OpenAI's embedding API.
        
        Args:
            api_kwargs: OpenAI API parameters
            model_type: The type of embedding model operation to perform
            
        Returns:
            Raw async response from OpenAI's embedding API
        """
        if not self._async_client:
            raise RuntimeError("OpenAI async client not initialized")
        
        try:
            # Use the existing OpenAI client's async embedding functionality
            response = await self._async_client.acall(api_kwargs=api_kwargs, model_type=EmbeddingModelType.TEXT)
            log.debug(f"OpenAI async embedding response received: {type(response)}")
            return response
        except Exception as e:
            log.error(f"OpenAI async embedding API call failed: {e}")
            raise
    
    def parse_response(
        self,
        response: Any,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> EmbedderOutput:
        """
        Parse the OpenAI response into standardized format.
        
        Args:
            response: Raw response from OpenAI's embedding API
            model_type: The type of embedding model operation performed
            
        Returns:
            EmbedderOutput: Standardized output with embeddings and metadata
        """
        try:
            if not response:
                return EmbedderOutput(error="Empty response from OpenAI")
            
            # Extract embeddings from the response
            embeddings = []
            model_info = {}
            
            # Handle different response formats
            if hasattr(response, 'data') and hasattr(response.data[0], 'embedding'):
                # Standard OpenAI response format
                embeddings = [item.embedding for item in response.data]
                if hasattr(response, 'model'):
                    model_info["model"] = response.model
                if hasattr(response, 'usage'):
                    model_info["usage"] = response.usage
            elif isinstance(response, dict) and 'data' in response:
                # Dict response format
                embeddings = [item['embedding'] for item in response['data']]
                if 'model' in response:
                    model_info["model"] = response['model']
                if 'usage' in response:
                    model_info["usage"] = response['usage']
            else:
                # Fallback: try to extract embeddings directly
                log.warning("Unexpected response format, attempting to extract embeddings")
                if hasattr(response, 'embedding'):
                    embeddings = [response.embedding]
                else:
                    return EmbedderOutput(error="Could not extract embeddings from response")
            
            # Validate embeddings
            if not embeddings:
                return EmbedderOutput(error="No embeddings found in response")
            
            # Convert to EmbeddingVector format
            embedding_vectors = []
            for emb in embeddings:
                if isinstance(emb, list):
                    embedding_vectors.append(EmbeddingVector(emb))
                else:
                    embedding_vectors.append(EmbeddingVector(list(emb)))
            
            # Add model information
            model_info.update({
                "provider": "openai",
                "model_name": self._model_name,
                "dimensions": self._dimensions,
                "encoding_format": self._encoding_format,
                "batch_size": len(embedding_vectors)
            })
            
            return EmbedderOutput(
                data=embedding_vectors,
                raw_response=response,
                model_info=model_info
            )
            
        except Exception as e:
            log.error(f"Failed to parse OpenAI embedding response: {e}")
            return EmbedderOutput(error=f"Response parsing failed: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current OpenAI embedding model.
        
        Returns:
            Dict: Model information including name, dimensions, etc.
        """
        base_info = super().get_model_info()
        base_info.update({
            "provider": "openai",
            "model_name": self._model_name,
            "dimensions": self._dimensions,
            "encoding_format": self._encoding_format
        })
        return base_info
    
    def set_model(self, model_name: str, dimensions: Optional[int] = None) -> None:
        """
        Set the OpenAI embedding model and optionally dimensions.
        
        Args:
            model_name: Name of the OpenAI embedding model
            dimensions: Optional dimensions for the model
        """
        self._model_name = model_name
        if dimensions and "text-embedding-3" in model_name:
            self._dimensions = dimensions
        log.info(f"Set OpenAI embedding model to {model_name}")
    
    def set_encoding_format(self, encoding_format: str) -> None:
        """
        Set the encoding format for embeddings.
        
        Args:
            encoding_format: Encoding format ('float' or 'base64')
        """
        if encoding_format in ['float', 'base64']:
            self._encoding_format = encoding_format
            log.info(f"Set encoding format to {encoding_format}")
        else:
            raise ValueError("Encoding format must be 'float' or 'base64'")
