"""
Base generator interface for all AI provider implementations.

This module defines the common interface that all generator components
must implement, ensuring consistent behavior across different AI providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List, Generator, AsyncGenerator
from enum import Enum

from backend.core.types import CompletionUsage


class ModelType(Enum):
    """Enumeration of supported model types."""
    UNDEFINED = "undefined"
    LLM = "llm"
    EMBEDDER = "embedder"
    IMAGE_GENERATION = "image_generation"


class GeneratorOutput:
    """Standard output format for all generator operations."""
    
    def __init__(
        self,
        data: Any = None,
        error: Optional[str] = None,
        raw_response: Any = None,
        usage: Optional[CompletionUsage] = None
    ):
        self.data = data
        self.error = error
        self.raw_response = raw_response
        self.usage = usage
    
    def __bool__(self) -> bool:
        """Return True if the operation was successful (no error)."""
        return self.error is None
    
    def __str__(self) -> str:
        """String representation of the generator output."""
        if self.error:
            return f"GeneratorOutput(error='{self.error}')"
        return f"GeneratorOutput(data={type(self.data).__name__}, usage={self.usage})"


class BaseGenerator(ABC):
    """
    Abstract base class for all generator implementations.
    
    This class defines the common interface that all AI provider generators
    must implement, ensuring consistent behavior and error handling.
    """
    
    def __init__(self, **kwargs):
        """Initialize the base generator with common configuration."""
        self._api_kwargs = {}
        self._input_type = kwargs.get("input_type", "text")
    
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
        input: Any = None,
        model_kwargs: Dict = None,
        model_type: ModelType = ModelType.UNDEFINED
    ) -> Dict:
        """
        Convert standardized inputs to provider-specific API format.
        
        Args:
            input: The input text, messages, or other data to process
            model_kwargs: Additional model-specific parameters
            model_type: The type of model operation to perform
            
        Returns:
            Dict: Provider-specific API parameters
        """
        pass
    
    @abstractmethod
    def call(
        self,
        api_kwargs: Dict = None,
        model_type: ModelType = ModelType.UNDEFINED
    ) -> Any:
        """
        Execute a synchronous call to the AI provider.
        
        Args:
            api_kwargs: Provider-specific API parameters
            model_type: The type of model operation to perform
            
        Returns:
            Any: Raw response from the provider
        """
        pass
    
    @abstractmethod
    async def acall(
        self,
        api_kwargs: Dict = None,
        model_type: ModelType = ModelType.UNDEFINED
    ) -> Any:
        """
        Execute an asynchronous call to the AI provider.
        
        Args:
            api_kwargs: Provider-specific API parameters
            model_type: The type of model operation to perform
            
        Returns:
            Any: Raw response from the provider
        """
        pass
    
    def parse_chat_completion(
        self,
        completion: Union[Any, Generator[Any, None, None]]
    ) -> GeneratorOutput:
        """
        Parse the completion response into a standardized format.
        
        Args:
            completion: Raw completion response from the provider
            
        Returns:
            GeneratorOutput: Standardized output format
        """
        try:
            # Default implementation - subclasses should override
            if hasattr(completion, 'choices') and len(completion.choices) > 0:
                data = completion.choices[0].message.content
            else:
                data = str(completion)
            
            usage = self.track_completion_usage(completion)
            return GeneratorOutput(
                data=data,
                error=None,
                raw_response=completion,
                usage=usage
            )
        except Exception as e:
            return GeneratorOutput(
                data=None,
                error=str(e),
                raw_response=completion
            )
    
    def track_completion_usage(self, completion: Any) -> Optional[CompletionUsage]:
        """
        Extract usage information from the completion response.
        
        Args:
            completion: Raw completion response from the provider
            
        Returns:
            Optional[CompletionUsage]: Usage statistics if available
        """
        try:
            if hasattr(completion, 'usage'):
                usage = completion.usage
                return CompletionUsage(
                    completion_tokens=getattr(usage, 'completion_tokens', None),
                    prompt_tokens=getattr(usage, 'prompt_tokens', None),
                    total_tokens=getattr(usage, 'total_tokens', None)
                )
        except Exception:
            pass
        return None
    
    def parse_embedding_response(self, response: Any) -> GeneratorOutput:
        """
        Parse embedding response into standardized format.
        
        Args:
            response: Raw embedding response from the provider
            
        Returns:
            GeneratorOutput: Standardized output format
        """
        try:
            # Default implementation - subclasses should override
            if hasattr(response, 'data'):
                data = [item.embedding for item in response.data]
            else:
                data = response
            
            return GeneratorOutput(
                data=data,
                error=None,
                raw_response=response
            )
        except Exception as e:
            return GeneratorOutput(
                data=[],
                error=str(e),
                raw_response=response
            )
    
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
