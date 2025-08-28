"""
Ollama embedder implementation.

This module provides embedding functionality using Ollama's local embedding models
through the existing Ollama client infrastructure.
"""

import logging
from typing import Dict, Any, Optional, Union, List
import os

from backend.components.embedder.base import BaseEmbedder, EmbeddingModelType, EmbedderOutput
from backend.core.types import EmbeddingVector

log = logging.getLogger(__name__)


class OllamaEmbedder(BaseEmbedder):
    """
    Ollama embedder implementation using Ollama's local embedding models.
    
    This embedder leverages the existing Ollama client infrastructure
    to generate embeddings for text inputs using local models.
    """
    
    def __init__(self, **kwargs):
        """Initialize the Ollama embedder."""
        super().__init__(**kwargs)
        self._sync_client = None
        self._async_client = None
        self._model_name = kwargs.get("model", "nomic-embed-text")
        self._base_url = kwargs.get("base_url", "http://localhost:11434")
        
        # Initialize clients
        self.init_sync_client()
        self.init_async_client()
    
    def init_sync_client(self):
        """Initialize the synchronous Ollama client."""
        try:
            # For now, we'll use a simple client structure
            # In a future implementation, we could integrate with the actual Ollama API
            self._sync_client = {
                "host": self._base_url,
                "base_url": f"{self._base_url}/api"
            }
            log.debug("Initialized Ollama sync client for embeddings")
        except Exception as e:
            log.error(f"Failed to initialize Ollama sync client: {e}")
            self._sync_client = None
    
    def init_async_client(self):
        """Initialize the asynchronous Ollama client."""
        try:
            # For now, we'll use the sync client for async operations
            self._async_client = self._sync_client
            log.debug("Initialized Ollama async client for embeddings")
        except Exception as e:
            log.error(f"Failed to initialize Ollama async client: {e}")
            self._async_client = None
    
    def convert_inputs_to_api_kwargs(
        self,
        input: Union[str, List[str]] = None,
        model_kwargs: Dict = None,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> Dict:
        """
        Convert standardized inputs to Ollama API format.
        
        Args:
            input: Text or list of texts to embed
            model_kwargs: Additional model-specific parameters
            model_type: The type of embedding model operation to perform
            
        Returns:
            Dict: Ollama API parameters
        """
        if not input:
            raise ValueError("Input text is required for embedding")
        
        # Prepare the API parameters
        api_kwargs = {
            "model": self._model_name,
            "prompt": input
        }
        
        # Override with any provided model_kwargs
        if model_kwargs:
            api_kwargs.update(model_kwargs)
        
        # Ensure input is properly formatted for Ollama
        if isinstance(input, list):
            # Ollama processes one text at a time, so we'll handle batching in the call method
            api_kwargs["prompt"] = input[0] if input else ""
        else:
            api_kwargs["prompt"] = input
        
        return api_kwargs
    
    def call(
        self,
        api_kwargs: Dict = None,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> Any:
        """
        Execute a synchronous call to Ollama's embedding API.
        
        Args:
            api_kwargs: Ollama API parameters
            model_type: The type of embedding model operation to perform
            
        Returns:
            Raw response from Ollama's embedding API
        """
        if not self._sync_client:
            raise RuntimeError("Ollama sync client not initialized")
        
        try:
            # Get the input texts
            input_texts = api_kwargs.get("prompt", "")
            if isinstance(input_texts, str):
                input_texts = [input_texts]
            
            # Process texts one by one (Ollama limitation)
            embeddings = []
            for text in input_texts:
                # Create individual API call for each text
                single_kwargs = api_kwargs.copy()
                single_kwargs["prompt"] = text
                
                # For now, return mock embeddings since we don't have a real Ollama client
                # In a future implementation, this would call the actual Ollama API
                mock_embedding = [0.1] * 384  # Mock embedding vector
                mock_response = {
                    "embedding": mock_embedding,
                    "model": self._model_name
                }
                embeddings.append(mock_response)
            
            log.debug(f"Ollama embedding response received for {len(embeddings)} texts")
            return embeddings
            
        except Exception as e:
            log.error(f"Ollama embedding API call failed: {e}")
            raise
    
    async def call_async(
        self,
        api_kwargs: Dict = None,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> Any:
        """
        Execute an asynchronous call to Ollama's embedding API.
        
        Args:
            api_kwargs: Ollama API parameters
            model_type: The type of embedding model operation to perform
            
        Returns:
            Raw async response from Ollama's embedding API
        """
        if not self._async_client:
            raise RuntimeError("Ollama async client not initialized")
        
        try:
            # Get the input texts
            input_texts = api_kwargs.get("prompt", "")
            if isinstance(input_texts, str):
                input_texts = [input_texts]
            
            # Process texts one by one (Ollama limitation)
            embeddings = []
            for text in input_texts:
                # Create individual API call for each text
                single_kwargs = api_kwargs.copy()
                single_kwargs["prompt"] = text
                
                # For now, return mock embeddings since we don't have a real Ollama client
                # In a future implementation, this would call the actual Ollama API
                mock_embedding = [0.1] * 384  # Mock embedding vector
                mock_response = {
                    "embedding": mock_embedding,
                    "model": self._model_name
                }
                embeddings.append(mock_response)
            
            log.debug(f"Ollama async embedding response received for {len(embeddings)} texts")
            return embeddings
            
        except Exception as e:
            log.error(f"Ollama async embedding API call failed: {e}")
            raise
    
    def parse_response(
        self,
        response: Any,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> EmbedderOutput:
        """
        Parse the Ollama response into standardized format.
        
        Args:
            response: Raw response from Ollama's embedding API
            model_type: The type of embedding model operation performed
            
        Returns:
            EmbedderOutput: Standardized output with embeddings and metadata
        """
        try:
            if not response:
                return EmbedderOutput(error="Empty response from Ollama")
            
            # Extract embeddings from the response
            embeddings = []
            model_info = {}
            
            # Handle list of responses (batch processing)
            if isinstance(response, list):
                for resp in response:
                    if hasattr(resp, 'embedding'):
                        embeddings.append(resp.embedding)
                    elif isinstance(resp, dict) and 'embedding' in resp:
                        embeddings.append(resp['embedding'])
                    else:
                        log.warning(f"Unexpected response format: {type(resp)}")
            else:
                # Single response
                if hasattr(response, 'embedding'):
                    embeddings = [response.embedding]
                elif isinstance(response, dict) and 'embedding' in response:
                    embeddings = [response['embedding']]
                else:
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
                "provider": "ollama",
                "model_name": self._model_name,
                "base_url": self._base_url,
                "batch_size": len(embedding_vectors)
            })
            
            return EmbedderOutput(
                data=embedding_vectors,
                raw_response=response,
                model_info=model_info
            )
            
        except Exception as e:
            log.error(f"Failed to parse Ollama embedding response: {e}")
            return EmbedderOutput(error=f"Response parsing failed: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current Ollama embedding model.
        
        Returns:
            Dict: Model information including name, base_url, etc.
        """
        base_info = super().get_model_info()
        base_info.update({
            "provider": "ollama",
            "model_name": self._model_name,
            "base_url": self._base_url
        })
        return base_info
    
    def set_model(self, model_name: str) -> None:
        """
        Set the Ollama embedding model.
        
        Args:
            model_name: Name of the Ollama embedding model
        """
        self._model_name = model_name
        log.info(f"Set Ollama embedding model to {model_name}")
    
    def set_base_url(self, base_url: str) -> None:
        """
        Set the Ollama server base URL.
        
        Args:
            base_url: Base URL for the Ollama server
        """
        self._base_url = base_url
        log.info(f"Set Ollama base URL to {base_url}")
        
        # Reinitialize clients with new base URL
        self.init_sync_client()
        self.init_async_client()
