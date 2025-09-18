"""
Ollama generator implementation.

This module provides Ollama-specific generator functionality,
extracted from the existing ollama_patch.py implementation.
"""

import os
import requests
import logging
import time
from typing import Dict, Any, Optional

from backend.components.generator.base import BaseGenerator, ModelType, GeneratorOutput
from backend.core.types import CompletionUsage

from backend.logging_config import setup_logging

setup_logging()
log = logging.getLogger(__name__)


class OllamaModelNotFoundError(Exception):
    """Custom exception for when Ollama model is not found"""
    pass


class OllamaGenerator(BaseGenerator):
    """
    Ollama generator implementation.
    
    Supports both embedding and chat completion APIs through local Ollama instances.
    
    Args:
        host (Optional[str]): Ollama host URL. If not provided, will use environment variable OLLAMA_HOST.
        env_host_name (str): Environment variable name for host. Defaults to "OLLAMA_HOST".
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        env_host_name: str = "OLLAMA_HOST",
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._env_host_name = env_host_name
        self.host = host or os.getenv(self._env_host_name, "http://localhost:11434")
        self.sync_client = self.init_sync_client()
        self.async_client = None  # Initialize async client only when needed
    
    def init_sync_client(self):
        """Initialize the synchronous Ollama client."""
        # Remove /api prefix if present and add it back
        if self.host.endswith('/api'):
            self.host = self.host[:-4]
        
        # Test connection
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=30)
            if response.status_code != 200:
                log.warning(f"Could not connect to Ollama at {self.host}")
        except requests.exceptions.RequestException as e:
            log.warning(f"Could not connect to Ollama at {self.host}: {e}")
        
        return {
            "host": self.host,
            "base_url": f"{self.host}/api"
        }
    
    def init_async_client(self):
        """Initialize the asynchronous Ollama client."""
        # For now, we'll use the sync client for async operations
        # In a future implementation, we could use aiohttp
        return self.sync_client
    
    def check_model_exists(self, model_name: str) -> bool:
        """
        Check if an Ollama model exists before attempting to use it.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            bool: True if model exists, False otherwise
        """
        try:
            response = requests.get(f"{self.sync_client['base_url']}/tags", timeout=30)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model.get('name', '').split(':')[0] for model in models_data.get('models', [])]
                model_base_name = model_name.split(':')[0]  # Remove tag if present
                
                is_available = model_base_name in available_models
                if is_available:
                    log.info(f"Ollama model '{model_name}' is available")
                else:
                    log.warning(f"Ollama model '{model_name}' is not available. Available models: {available_models}")
                return is_available
            else:
                log.warning(f"Could not check Ollama models, status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            log.warning(f"Could not connect to Ollama to check models: {e}")
            return False
        except Exception as e:
            log.warning(f"Error checking Ollama model availability: {e}")
            return False
    
    def convert_inputs_to_api_kwargs(
        self,
        input: Any = None,
        model_kwargs: Dict = None,
        model_type: ModelType = ModelType.UNDEFINED
    ) -> Dict:
        """Convert inputs to Ollama API format."""
        model_kwargs = model_kwargs or {}
        
        # Default UNDEFINED to LLM for Ollama
        if model_type == ModelType.UNDEFINED:
            model_type = ModelType.LLM
        
        if model_type == ModelType.LLM:
            # Handle LLM generation
            messages = []
            
            # Convert input to messages format if it's a string
            if isinstance(input, str):
                messages = [{"role": "user", "content": input}]
            elif isinstance(input, list) and all(isinstance(msg, dict) for msg in input):
                messages = input
            else:
                raise ValueError(f"Unsupported input format for Ollama: {type(input)}")
            
            # For debugging
            log.info(f"Messages for Ollama: {messages}")
            
            api_kwargs = {
                "messages": messages,
                **model_kwargs
            }
            
            # Ensure model is specified
            if "model" not in api_kwargs:
                api_kwargs["model"] = "llama2"
                
            return api_kwargs
            
        elif model_type == ModelType.EMBEDDER:
            # Handle embedding generation
            if isinstance(input, str):
                input = [input]
            if not isinstance(input, list):
                raise ValueError("Input must be a string or list of strings for embeddings")
                
            api_kwargs = {
                "input": input,
                **model_kwargs
            }
            
            # Ensure model is specified
            if "model" not in api_kwargs:
                api_kwargs["model"] = "llama2"
                
            return api_kwargs
            
        else:
            raise ValueError(f"Model type {model_type} not supported by Ollama")
    
    def parse_chat_completion(self, completion: Any) -> GeneratorOutput:
        """Parse Ollama chat completion response."""
        try:
            # Extract the response content from Ollama response
            if isinstance(completion, dict):
                # Direct response
                if 'message' in completion:
                    content = completion['message']['content']
                elif 'response' in completion:
                    content = completion['response']
                else:
                    content = str(completion)
                    
                # Extract usage if available
                usage = None
                if 'usage' in completion:
                    usage_data = completion['usage']
                    usage = CompletionUsage(
                        completion_tokens=usage_data.get('completion_tokens'),
                        prompt_tokens=usage_data.get('prompt_tokens'),
                        total_tokens=usage_data.get('total_tokens')
                    )
                
                return GeneratorOutput(
                    data=content,
                    error=None,
                    raw_response=completion,
                    usage=usage
                )
            else:
                # Handle other response types
                return GeneratorOutput(
                    data=str(completion),
                    error=None,
                    raw_response=completion
                )
                
        except Exception as e:
            log.error(f"Error parsing Ollama completion: {e}")
            return GeneratorOutput(
                data=None,
                error=str(e),
                raw_response=completion
            )
    
    def parse_embedding_response(self, response: Any) -> GeneratorOutput:
        """Parse Ollama embedding response."""
        try:
            if isinstance(response, dict):
                # Extract embeddings
                if 'embedding' in response:
                    embeddings = [response['embedding']]
                elif 'embeddings' in response:
                    embeddings = response['embeddings']
                else:
                    embeddings = []
                
                return GeneratorOutput(
                    data=embeddings,
                    error=None,
                    raw_response=response
                )
            else:
                return GeneratorOutput(
                    data=[],
                    error="Invalid response format",
                    raw_response=response
                )
                
        except Exception as e:
            log.error(f"Error parsing Ollama embedding response: {e}")
            return GeneratorOutput(
                data=[],
                error=str(e),
                raw_response=response
            )
    
    def _call_with_retry(self, url: str, api_kwargs: Dict, max_retries: int = 3) -> Dict:
        """
        Call Ollama API with retry logic for timeout errors.
        
        Args:
            url: API endpoint URL
            api_kwargs: API request parameters
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict: API response
            
        Raises:
            requests.exceptions.RequestException: If all retries fail
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    wait_time = min(2 ** attempt, 30)  # Exponential backoff, max 30s
                    log.info(f"Retrying Ollama API call (attempt {attempt + 1}/{max_retries + 1}) after {wait_time}s...")
                    time.sleep(wait_time)
                
                response = requests.post(
                    url,
                    json=api_kwargs,
                    timeout=300  # 5 minutes timeout for large models
                )
                response.raise_for_status()
                return response.json()
                
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_exception = e
                if attempt < max_retries:
                    log.warning(f"Ollama API timeout on attempt {attempt + 1}, retrying... Error: {e}")
                    continue
                else:
                    log.error(f"Ollama API failed after {max_retries + 1} attempts. Last error: {e}")
                    raise
            except requests.exceptions.RequestException as e:
                # For non-timeout errors, don't retry
                log.error(f"Ollama API request error (non-retryable): {e}")
                raise
        
        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
    
    def call(self, api_kwargs: Optional[Dict] = None, model_type: Optional[ModelType] = None) -> Any:
        """Execute synchronous call to Ollama API."""
        api_kwargs = api_kwargs or {}
        # Default None or UNDEFINED to LLM for Ollama
        if model_type is None or model_type == ModelType.UNDEFINED:
            model_type = ModelType.LLM
        
        try:
            # Check if model exists
            model_name = api_kwargs.get("model", "llama2")
            if not self.check_model_exists(model_name):
                raise OllamaModelNotFoundError(f"Model {model_name} not found in Ollama")
            
            if model_type == ModelType.LLM:
                # Chat completion endpoint
                url = f"{self.sync_client['base_url']}/chat"
            elif model_type == ModelType.EMBEDDER:
                # Embedding endpoint
                url = f"{self.sync_client['base_url']}/embeddings"
            else:
                raise ValueError(f"Model type {model_type} not supported")
            
            # Use retry logic for API calls
            response_data = self._call_with_retry(url, api_kwargs)
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            log.error(f"Ollama API request error: {e}")
            raise
        except OllamaModelNotFoundError as e:
            log.error(f"Ollama model error: {e}")
            raise
        except Exception as e:
            log.error(f"Unexpected error in Ollama call: {e}")
            raise
    
    async def acall(
        self, api_kwargs: Optional[Dict] = None, model_type: Optional[ModelType] = None
    ) -> Any:
        """Execute asynchronous call to Ollama API."""
        # For now, we'll use the sync client
        # In a future implementation, we could use aiohttp for true async
        return self.call(api_kwargs, model_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the generator to a dictionary representation."""
        exclude = ['sync_client', 'async_client']  # Unserializable objects
        output = {}
        for key, value in self.__dict__.items():
            if key not in exclude:
                output[key] = value
        return output
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create a generator instance from a dictionary."""
        obj = cls()
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj
