"""
Ollama embedder implementation.

This module provides embedding functionality using Ollama's local embedding models
through the existing Ollama client infrastructure.
"""

import logging
import requests
import asyncio
import aiohttp
from typing import Dict, Any, Union, List, Optional
import concurrent.futures
from threading import Semaphore

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
        
        # Concurrency control settings
        self._max_concurrent_requests = kwargs.get("max_concurrent_requests", 4)  # Limit concurrent requests
        self._semaphore = Semaphore(self._max_concurrent_requests)
        
        # Initialize clients
        self.init_sync_client()
        self.init_async_client()
    
    def init_sync_client(self):
        """Initialize the synchronous Ollama client."""
        try:
            # Normalize the base URL (remove /api suffix if present)
            if self._base_url.endswith('/api'):
                self._base_url = self._base_url[:-4]
                
            # Test connection to ensure Ollama is running
            try:
                response = requests.get(f"{self._base_url}/api/tags", timeout=10)
                if response.status_code == 200:
                    log.info(f"Successfully connected to Ollama at {self._base_url}")
                else:
                    log.warning(f"Could not connect to Ollama at {self._base_url}, status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                log.warning(f"Could not connect to Ollama at {self._base_url}: {e}")
            
            # Store client configuration
            self._sync_client = {
                "host": self._base_url,
                "base_url": f"{self._base_url}/api",
                "embeddings_url": f"{self._base_url}/api/embeddings"
            }
            log.debug("Initialized Ollama sync client for embeddings")
            
        except Exception as e:
            log.error(f"Failed to initialize Ollama sync client: {e}")
            self._sync_client = None
    
    def init_async_client(self):
        """Initialize the asynchronous Ollama client."""
        # Store configuration for async operations
        if self._sync_client:
            self._async_client = {
                "host": self._sync_client["host"],
                "base_url": self._sync_client["base_url"],
                "embeddings_url": self._sync_client["embeddings_url"]
            }
            log.debug("Initialized Ollama async client for embeddings")
        else:
            log.error("Cannot initialize async client: sync client not available")
    
    def __call__(self, input=None, input_data=None, **kwargs):
        """
        Make the embedder callable for compatibility with adalflow FAISS retriever.
        
        Args:
            input: Text or list of texts to embed (keyword argument from single_string_embedder)
            input_data: Text or list of texts to embed (positional argument for direct calls)
            **kwargs: Additional arguments
            
        Returns:
            Object with .data attribute containing embeddings
        """
        try:
            # Handle both keyword and positional arguments
            text_input = input if input is not None else input_data
            
            # Handle both single string and list of strings
            if isinstance(text_input, str):
                queries = [text_input]
            elif isinstance(text_input, list):
                queries = text_input
            else:
                raise ValueError(f"Unsupported input type: {type(text_input)}")
            
            embeddings = []
            for query in queries:
                # Call the embedding API
                api_kwargs = {"prompt": query}
                result = self.call(api_kwargs)
                
                # Extract the embedding vector from the response
                if result and len(result) > 0 and "embedding" in result[0]:
                    embedding = result[0]["embedding"]
                    embeddings.append(embedding)
                    log.info(f"Embedding for '{query[:50]}...': dimension={len(embedding)}")
                else:
                    log.error(f"Invalid embedding response format: {result}")
                    raise RuntimeError("Invalid embedding response format")
            
            # Create a compatible object with .data attribute
            # Each item in .data needs to have an .embedding attribute
            class EmbeddingData:
                def __init__(self, embedding):
                    self.embedding = embedding
            
            class EmbedderOutput:
                def __init__(self, embeddings):
                    # Create EmbeddingData objects with .embedding attribute
                    self.data = [EmbeddingData(emb) for emb in embeddings]
            
            return EmbedderOutput(embeddings)
            
        except Exception as e:
            log.error(f"Error in __call__ method: {e}")
            raise
            self._async_client = None
    
    def convert_inputs_to_api_kwargs(
        self,
        input: Optional[Union[str, List[str]]] = None,
        model_kwargs: Optional[Dict] = None,
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
    
    def _single_embed_request(self, text: str) -> Dict[str, Any]:
        """
        Make a single embedding request to Ollama.
        
        Args:
            text: Text to embed
            
        Returns:
            Dict with embedding and model info
        """
        with self._semaphore:  # Limit concurrent requests
            payload = {
                "model": self._model_name,
                "prompt": text
            }
            
            response = requests.post(
                self._sync_client["embeddings_url"],
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                log.error(f"Ollama API error: {response.status_code} - {response.text}")
                raise RuntimeError(f"Ollama API error: {response.status_code}")
            
            response_data = response.json()
            if "embedding" not in response_data:
                log.error(f"Invalid Ollama response format: {response_data}")
                raise RuntimeError("Invalid response format from Ollama API")
            
            return {
                "embedding": response_data["embedding"],
                "model": self._model_name
            }

    def call(
        self,
        api_kwargs: Optional[Dict] = None,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> Any:
        """
        Execute concurrent calls to Ollama's embedding API.
        
        Args:
            api_kwargs: Ollama API parameters
            model_type: The type of embedding model operation to perform
            
        Returns:
            Raw response from Ollama's embedding API
        """
        if not self._sync_client:
            raise RuntimeError("Ollama sync client not initialized")
        
        if api_kwargs is None:
            api_kwargs = {}

        try:
            # Get the input texts
            input_texts = api_kwargs.get("prompt", "")
            if isinstance(input_texts, str):
                input_texts = [input_texts]
            
            # Filter out empty texts
            valid_texts = [text for text in input_texts if text.strip()]
            
            if not valid_texts:
                return []
            
            # Use concurrent processing for better performance
            embeddings = []
            
            if len(valid_texts) == 1:
                # Single text - no need for threading
                embeddings.append(self._single_embed_request(valid_texts[0]))
            else:
                # Multiple texts - use ThreadPoolExecutor for concurrent requests
                with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_concurrent_requests) as executor:
                    # Submit all embedding requests concurrently
                    future_to_text = {
                        executor.submit(self._single_embed_request, text): text 
                        for text in valid_texts
                    }
                    
                    # Collect results as they complete
                    for future in concurrent.futures.as_completed(future_to_text):
                        text = future_to_text[future]
                        try:
                            result = future.result()
                            embeddings.append(result)
                        except Exception as e:
                            log.error(f"Failed to get embedding for text: {e}")
                            # Continue with other embeddings rather than failing completely
                            continue
            
            log.debug(f"Ollama embedding response received for {len(embeddings)} texts")
            return embeddings
            
        except requests.exceptions.RequestException as e:
            log.error(f"Ollama embedding API connection failed: {e}")
            raise RuntimeError(f"Failed to connect to Ollama API: {e}")
        except Exception as e:
            log.error(f"Ollama embedding API call failed: {e}")
            raise
    
    async def _single_embed_request_async(self, session: aiohttp.ClientSession, text: str) -> Dict[str, Any]:
        """
        Make a single async embedding request to Ollama.
        
        Args:
            session: aiohttp session
            text: Text to embed
            
        Returns:
            Dict with embedding and model info
        """
        payload = {
            "model": self._model_name,
            "prompt": text
        }
        
        async with session.post(
            self._async_client["embeddings_url"],
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"Content-Type": "application/json"}
        ) as response:
            
            if response.status != 200:
                error_text = await response.text()
                log.error(f"Ollama async API error: {response.status} - {error_text}")
                raise RuntimeError(f"Ollama async API error: {response.status}")
            
            response_data = await response.json()
            if "embedding" not in response_data:
                log.error(f"Invalid Ollama async response format: {response_data}")
                raise RuntimeError("Invalid response format from Ollama async API")
            
            return {
                "embedding": response_data["embedding"],
                "model": self._model_name
            }

    async def call_async(
        self,
        api_kwargs: Optional[Dict] = None,
        model_type: EmbeddingModelType = EmbeddingModelType.TEXT
    ) -> Any:
        """
        Execute concurrent asynchronous calls to Ollama's embedding API.
        
        Args:
            api_kwargs: Ollama API parameters
            model_type: The type of embedding model operation to perform
            
        Returns:
            Raw async response from Ollama's embedding API
        """
        if not self._async_client:
            raise RuntimeError("Ollama async client not initialized")
        
        if api_kwargs is None:
            api_kwargs = {}

        try:
            # Get the input texts
            input_texts = api_kwargs.get("prompt", "")
            if isinstance(input_texts, str):
                input_texts = [input_texts]
            
            # Filter out empty texts
            valid_texts = [text for text in input_texts if text.strip()]
            
            if not valid_texts:
                return []
            
            # Use async concurrency with semaphore for rate limiting
            semaphore = asyncio.Semaphore(self._max_concurrent_requests)
            
            async def limited_request(session, text):
                async with semaphore:
                    return await self._single_embed_request_async(session, text)
            
            embeddings = []
            
            async with aiohttp.ClientSession() as session:
                if len(valid_texts) == 1:
                    # Single text - no need for concurrency
                    result = await self._single_embed_request_async(session, valid_texts[0])
                    embeddings.append(result)
                else:
                    # Multiple texts - use asyncio.gather for concurrent requests
                    tasks = [
                        limited_request(session, text) 
                        for text in valid_texts
                    ]
                    
                    # Wait for all tasks to complete
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Process results, filtering out exceptions
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            log.error(f"Failed to get embedding for text {i}: {result}")
                            continue
                        embeddings.append(result)
            
            log.debug(f"Ollama async embedding response received for {len(embeddings)} texts")
            return embeddings
            
        except aiohttp.ClientError as e:
            log.error(f"Ollama async embedding API connection failed: {e}")
            raise RuntimeError(f"Failed to connect to Ollama async API: {e}")
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
                    if isinstance(resp, dict) and 'embedding' in resp:
                        embeddings.append(resp['embedding'])
                    else:
                        log.warning(f"Unexpected response format: {type(resp)}")
            else:
                # Single response
                if isinstance(response, dict) and 'embedding' in response:
                    embeddings = [response['embedding']]
                else:
                    log.warning("Unexpected response format, attempting to extract embeddings")
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
    
    def validate_connection(self) -> bool:
        """
        Validate that Ollama is running and accessible.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            if not self._sync_client:
                log.error("Sync client not initialized")
                return False
                
            response = requests.get(f"{self._base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                log.info(f"Ollama connection validated at {self._base_url}")
                return True
            else:
                log.error(f"Ollama connection failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            log.error(f"Ollama connection validation failed: {e}")
            return False
    
    def validate_model(self) -> bool:
        """
        Validate that the specified model is available in Ollama.
        
        Returns:
            bool: True if model is available, False otherwise
        """
        try:
            if not self._sync_client:
                log.error("Sync client not initialized")
                return False
                
            response = requests.get(f"{self._base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model.get("name", "") for model in models_data.get("models", [])]
                
                if self._model_name in available_models:
                    log.info(f"Model {self._model_name} is available in Ollama")
                    return True
                else:
                    log.error(f"Model {self._model_name} not found. Available models: {available_models}")
                    return False
            else:
                log.error(f"Failed to get model list: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            log.error(f"Model validation failed: {e}")
            return False
        except Exception as e:
            log.error(f"Error validating model: {e}")
            return False
