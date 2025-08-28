"""
OpenRouter generator implementation.

This module provides OpenRouter-specific generator functionality,
extracted from the existing openrouter_client.py implementation.
"""

import logging
import json
import aiohttp
import requests
from requests.exceptions import RequestException, Timeout
from typing import Dict, Sequence, Optional, Any, List

from backend.components.generator.base import BaseGenerator, ModelType, GeneratorOutput
from backend.core.types import CompletionUsage

log = logging.getLogger(__name__)


class OpenRouterGenerator(BaseGenerator):
    """
    OpenRouter generator implementation.
    
    OpenRouter provides a unified API that gives access to hundreds of AI models through a single endpoint.
    The API is compatible with OpenAI's API format with a few small differences.
    
    Args:
        api_key (Optional[str]): OpenRouter API key. If not provided, will use environment variable OPENROUTER_API_KEY.
        base_url (str): The API base URL to use. Defaults to "https://openrouter.ai/api/v1".
        env_api_key_name (str): Environment variable name for API key. Defaults to "OPENROUTER_API_KEY".
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        env_api_key_name: str = "OPENROUTER_API_KEY",
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._env_api_key_name = env_api_key_name
        self.base_url = base_url or "https://openrouter.ai/api/v1"
        self.sync_client = self.init_sync_client()
        self.async_client = None  # Initialize async client only when needed
    
    def init_sync_client(self):
        """Initialize the synchronous OpenRouter client."""
        from backend.core.config.settings import OPENROUTER_API_KEY
        api_key = OPENROUTER_API_KEY
        if not api_key:
            log.warning("OPENROUTER_API_KEY not configured")
        
        # OpenRouter doesn't have a dedicated client library, so we'll use requests directly
        return {
            "api_key": api_key,
            "base_url": self.base_url
        }
    
    def init_async_client(self):
        """Initialize the asynchronous OpenRouter client."""
        from backend.core.config.settings import OPENROUTER_API_KEY
        api_key = OPENROUTER_API_KEY
        if not api_key:
            log.warning("OPENROUTER_API_KEY not configured")
        
        # For async, we'll use aiohttp
        return {
            "api_key": api_key,
            "base_url": self.base_url
        }
    
    def convert_inputs_to_api_kwargs(
        self, input: Any, model_kwargs: Dict = None, model_type: ModelType = None
    ) -> Dict:
        """Convert AdalFlow inputs to OpenRouter API format."""
        model_kwargs = model_kwargs or {}
        
        if model_type == ModelType.LLM:
            # Handle LLM generation
            messages = []
            
            # Convert input to messages format if it's a string
            if isinstance(input, str):
                messages = [{"role": "user", "content": input}]
            elif isinstance(input, list) and all(isinstance(msg, dict) for msg in input):
                messages = input
            else:
                raise ValueError(f"Unsupported input format for OpenRouter: {type(input)}")
            
            # For debugging
            log.info(f"Messages for OpenRouter: {messages}")
            
            api_kwargs = {
                "messages": messages,
                **model_kwargs
            }
            
            # Ensure model is specified
            if "model" not in api_kwargs:
                api_kwargs["model"] = "openai/gpt-3.5-turbo"
                
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
                api_kwargs["model"] = "openai/text-embedding-ada-002"
                
            return api_kwargs
            
        else:
            raise ValueError(f"Model type {model_type} not supported by OpenRouter")
    
    def parse_chat_completion(self, completion: Any) -> GeneratorOutput:
        """Parse OpenRouter chat completion response."""
        try:
            # Extract the response content from OpenRouter response
            if isinstance(completion, dict):
                # Direct response
                if 'choices' in completion and len(completion['choices']) > 0:
                    content = completion['choices'][0]['message']['content']
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
            log.error(f"Error parsing OpenRouter completion: {e}")
            return GeneratorOutput(
                data=None,
                error=str(e),
                raw_response=completion
            )
    
    def parse_embedding_response(self, response: Any) -> GeneratorOutput:
        """Parse OpenRouter embedding response."""
        try:
            if isinstance(response, dict):
                # Extract embeddings
                if 'data' in response:
                    embeddings = [item['embedding'] for item in response['data']]
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
            log.error(f"Error parsing OpenRouter embedding response: {e}")
            return GeneratorOutput(
                data=[],
                error=str(e),
                raw_response=response
            )
    
    def call(self, api_kwargs: Dict = None, model_type: ModelType = None) -> Any:
        """Execute synchronous call to OpenRouter API."""
        api_kwargs = api_kwargs or {}
        model_type = model_type or ModelType.LLM
        
        try:
            headers = {
                "Authorization": f"Bearer {self.sync_client['api_key']}",
                "Content-Type": "application/json"
            }
            
            if model_type == ModelType.LLM:
                # Chat completion endpoint
                url = f"{self.sync_client['base_url']}/chat/completions"
            elif model_type == ModelType.EMBEDDER:
                # Embedding endpoint
                url = f"{self.sync_client['base_url']}/embeddings"
            else:
                raise ValueError(f"Model type {model_type} not supported")
            
            response = requests.post(
                url,
                headers=headers,
                json=api_kwargs,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
            
        except RequestException as e:
            log.error(f"OpenRouter API request error: {e}")
            raise
        except Exception as e:
            log.error(f"Unexpected error in OpenRouter call: {e}")
            raise
    
    async def acall(
        self, api_kwargs: Dict = None, model_type: ModelType = None
    ) -> Any:
        """Execute asynchronous call to OpenRouter API."""
        api_kwargs = api_kwargs or {}
        model_type = model_type or ModelType.LLM
        
        try:
            headers = {
                "Authorization": f"Bearer {self.async_client['api_key']}",
                "Content-Type": "application/json"
            }
            
            if model_type == ModelType.LLM:
                # Chat completion endpoint
                url = f"{self.async_client['base_url']}/chat/completions"
            elif model_type == ModelType.EMBEDDER:
                # Embedding endpoint
                url = f"{self.async_client['base_url']}/embeddings"
            else:
                raise ValueError(f"Model type {model_type} not supported")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    json=api_kwargs,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    return await response.json()
                    
        except aiohttp.ClientError as e:
            log.error(f"OpenRouter API async request error: {e}")
            raise
        except Exception as e:
            log.error(f"Unexpected error in OpenRouter async call: {e}")
            raise
    
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
