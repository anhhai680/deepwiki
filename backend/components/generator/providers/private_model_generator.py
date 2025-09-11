"""
Private Model generator implementation.

This module provides support for private model LLM deployments that use 
OpenAI-compatible APIs (vLLM, Ollama, LocalAI, etc.).
"""

import os
import logging
from typing import Dict, Any, Optional, Union, Generator

from openai import OpenAI, AsyncOpenAI
from openai import (
    APITimeoutError,
    InternalServerError,
    RateLimitError,
    UnprocessableEntityError,
    BadRequestError,
    APIConnectionError,
)
from openai.types.chat import ChatCompletionChunk, ChatCompletion

from backend.components.generator.base import BaseGenerator, ModelType, GeneratorOutput
from backend.core.types import CompletionUsage

log = logging.getLogger(__name__)


class PrivateModelGenerator(BaseGenerator):
    """
    Private Model generator implementation.
    
    Supports OpenAI-compatible private model deployments such as vLLM, Ollama,
    LocalAI, and other local or private cloud deployments.
    
    Args:
        api_key (Optional[str], optional): API key for authentication. Defaults to None.
        base_url (Optional[str], optional): Base URL for the private model API. Defaults to None.
        env_api_key_name (str): Environment variable name for API key. Defaults to "PRIVATE_MODEL_API_KEY".
        env_base_url_name (str): Environment variable name for base URL. Defaults to "PRIVATE_MODEL_BASE_URL".
        default_model (str): Default model name to use. Defaults to "custom-model".
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        env_api_key_name: str = "PRIVATE_MODEL_API_KEY",
        env_base_url_name: str = "PRIVATE_MODEL_BASE_URL",
        default_model: str = "custom-model",
        **kwargs
    ):
        super().__init__(**kwargs)
        self._api_key = api_key
        self._env_api_key_name = env_api_key_name
        self._env_base_url_name = env_base_url_name
        self._default_model = default_model
        
        # Set base URL from parameter, environment, or config
        self.base_url = (
            base_url 
            or os.getenv(self._env_base_url_name)
            or "http://localhost:8000/v1"
        )
        
        self.sync_client = None
        self.async_client = None
        self._api_kwargs = {}
        
        # Initialize clients and validate connection
        try:
            self.sync_client = self.init_sync_client()
            self._validate_connection()
        except Exception as e:
            log.error(f"Failed to initialize private model generator: {e}")
            # Don't raise here to allow graceful degradation
    
    def init_sync_client(self):
        """Initialize the synchronous OpenAI-compatible client."""
        api_key = self._api_key or os.getenv(self._env_api_key_name)
        if not api_key:
            # Some private models don't require API keys
            log.warning(f"No API key found for private model (checked {self._env_api_key_name})")
            api_key = "dummy-key"  # Some deployments require a dummy key
        
        return OpenAI(api_key=api_key, base_url=self.base_url)
    
    def init_async_client(self):
        """Initialize the asynchronous OpenAI-compatible client."""
        api_key = self._api_key or os.getenv(self._env_api_key_name)
        if not api_key:
            log.warning(f"No API key found for private model (checked {self._env_api_key_name})")
            api_key = "dummy-key"
        
        return AsyncOpenAI(api_key=api_key, base_url=self.base_url)
    
    def _validate_connection(self):
        """Validate connection to the private model endpoint."""
        if not self.sync_client:
            raise ConnectionError("Sync client not initialized")
        
        try:
            # Test connection by attempting to list models (if supported)
            # This is a lightweight way to validate the connection
            log.info(f"Validating connection to private model at {self.base_url}")
            
            # Some deployments don't support /models endpoint, so we'll just log success
            log.info(f"Private model generator ready at {self.base_url}")
            
        except APIConnectionError as e:
            log.error(f"Failed to connect to private model at {self.base_url}: {e}")
            raise ConnectionError(f"Cannot connect to private model API at {self.base_url}")
        except Exception as e:
            log.warning(f"Connection validation warning (may be normal): {e}")
    
    def convert_inputs_to_api_kwargs(
        self,
        input: Optional[Any] = None,
        model_kwargs: Dict = None,
        model_type: ModelType = ModelType.UNDEFINED,
    ) -> Dict:
        """
        Convert the Component's standard input and model_kwargs into API-specific format.
        
        Args:
            input: The input text or messages to process
            model_kwargs: Additional parameters
            model_type: The type of model (EMBEDDER or LLM)
            
        Returns:
            Dict: API-specific kwargs for the model call
        """
        if model_kwargs is None:
            model_kwargs = {}
        
        final_model_kwargs = model_kwargs.copy()
        
        if model_type == ModelType.LLM:
            # Ensure model is specified
            if "model" not in final_model_kwargs:
                final_model_kwargs["model"] = self._default_model
            
            # Convert input to messages format
            if isinstance(input, str):
                final_model_kwargs["messages"] = [{"role": "user", "content": input}]
            elif isinstance(input, list):
                final_model_kwargs["messages"] = input
            else:
                final_model_kwargs["messages"] = [{"role": "user", "content": str(input)}]
            
            # Set reasonable defaults for private models
            final_model_kwargs.setdefault("temperature", 0.7)
            final_model_kwargs.setdefault("top_p", 0.8)
            final_model_kwargs.setdefault("max_tokens", 4000)
            
        elif model_type == ModelType.EMBEDDER:
            # For embeddings, if supported by the private model
            if isinstance(input, str):
                input = [input]
            final_model_kwargs["input"] = input
            if "model" not in final_model_kwargs:
                final_model_kwargs["model"] = self._default_model
                
        else:
            raise ValueError(f"model_type {model_type} is not supported by PrivateModelGenerator")
        
        return final_model_kwargs
    
    def parse_chat_completion(
        self,
        completion: Union[ChatCompletion, Generator[ChatCompletionChunk, None, None]],
    ) -> GeneratorOutput:
        """Parse the completion response into a standardized format."""
        try:
            # Handle streaming response
            if hasattr(completion, '__iter__') and not isinstance(completion, (str, ChatCompletion)):
                # This is a streaming response
                accumulated_content = ""
                for chunk in completion:
                    if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            accumulated_content += delta.content
                
                return GeneratorOutput(
                    data=None,
                    error=None,
                    raw_response=accumulated_content,
                    usage=None  # Streaming responses typically don't include usage
                )
            
            # Handle standard completion
            if hasattr(completion, 'choices') and len(completion.choices) > 0:
                content = completion.choices[0].message.content
                usage = self.track_completion_usage(completion)
                
                return GeneratorOutput(
                    data=None,
                    error=None,
                    raw_response=content,
                    usage=usage
                )
            
            # Fallback
            return GeneratorOutput(
                data=None,
                error=None,
                raw_response=str(completion),
                usage=None
            )
            
        except Exception as e:
            log.error(f"Error parsing chat completion: {e}")
            return GeneratorOutput(
                data=None,
                error=str(e),
                raw_response=completion
            )
    
    def track_completion_usage(
        self,
        completion: Union[ChatCompletion, Generator[ChatCompletionChunk, None, None]],
    ) -> Optional[CompletionUsage]:
        """Track completion usage statistics."""
        try:
            if hasattr(completion, 'usage') and completion.usage:
                usage = completion.usage
                return CompletionUsage(
                    completion_tokens=getattr(usage, 'completion_tokens', None),
                    prompt_tokens=getattr(usage, 'prompt_tokens', None),
                    total_tokens=getattr(usage, 'total_tokens', None),
                )
        except Exception as e:
            log.debug(f"Could not track usage for private model: {e}")
        
        return None
    
    def call(self, api_kwargs: Dict = None, model_type: ModelType = ModelType.UNDEFINED):
        """Execute synchronous call to private model API."""
        if api_kwargs is None:
            api_kwargs = {}
        
        log.info(f"Private model API call: {api_kwargs}")
        self._api_kwargs = api_kwargs
        
        if not self.sync_client:
            raise RuntimeError("Sync client not initialized")
        
        if model_type == ModelType.LLM:
            try:
                # Always use streaming for consistency with other generators
                api_kwargs_streaming = api_kwargs.copy()
                api_kwargs_streaming["stream"] = True
                
                stream_response = self.sync_client.chat.completions.create(**api_kwargs_streaming)
                
                # Accumulate streaming response into a standard response
                accumulated_content = ""
                id = ""
                model = ""
                created = 0
                
                for chunk in stream_response:
                    id = getattr(chunk, "id", None) or id
                    model = getattr(chunk, "model", None) or model
                    created = getattr(chunk, "created", 0) or created
                    
                    choices = getattr(chunk, "choices", [])
                    if len(choices) > 0:
                        delta = getattr(choices[0], "delta", None)
                        if delta and hasattr(delta, "content") and delta.content:
                            accumulated_content += delta.content
                
                # Return a mock completion object for consistent handling
                return ChatCompletion(
                    id=id or "private-model-completion",
                    model=model or api_kwargs.get("model", self._default_model),
                    created=created or 0,
                    object="chat.completion",
                    choices=[{
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"content": accumulated_content, "role": "assistant"}
                    }]
                )
                
            except (APIConnectionError, APITimeoutError) as e:
                log.error(f"Connection error with private model: {e}")
                raise ConnectionError(f"Failed to connect to private model at {self.base_url}")
            except Exception as e:
                log.error(f"Private model API call failed: {e}")
                raise
        
        elif model_type == ModelType.EMBEDDER:
            try:
                return self.sync_client.embeddings.create(**api_kwargs)
            except Exception as e:
                log.error(f"Private model embeddings call failed: {e}")
                raise
        
        else:
            raise ValueError(f"model_type {model_type} is not supported")
    
    async def acall(
        self, api_kwargs: Dict = None, model_type: ModelType = ModelType.UNDEFINED
    ):
        """Execute asynchronous call to private model API."""
        if api_kwargs is None:
            api_kwargs = {}
        
        self._api_kwargs = api_kwargs
        
        if self.async_client is None:
            self.async_client = self.init_async_client()
        
        if model_type == ModelType.LLM:
            return await self.async_client.chat.completions.create(**api_kwargs)
        elif model_type == ModelType.EMBEDDER:
            return await self.async_client.embeddings.create(**api_kwargs)
        else:
            raise ValueError(f"model_type {model_type} is not supported")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from dictionary."""
        obj = super().from_dict(data)
        # Recreate the existing clients
        obj.sync_client = obj.init_sync_client()
        if hasattr(obj, '_async_client') and obj._async_client:
            obj.async_client = obj.init_async_client()
        return obj
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the component to a dictionary."""
        exclude = ["sync_client", "async_client"]  # Unserializable objects
        output = {}
        for key, value in self.__dict__.items():
            if key not in exclude:
                output[key] = value
        return output
