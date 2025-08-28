"""
DashScope (Alibaba Cloud) generator implementation.

This module provides DashScope-specific generator functionality,
extracted from the existing dashscope_client.py implementation.
"""

import os
import pickle
import logging
from typing import Dict, Optional, Any, Callable, Generator, Union, Literal, List, Sequence

import backoff
from copy import deepcopy
from tqdm import tqdm

# Optional import
from adalflow.utils.lazy_import import safe_import, OptionalPackages

openai = safe_import(OptionalPackages.OPENAI.value[0], OptionalPackages.OPENAI.value[1])

from openai import OpenAI, AsyncOpenAI, Stream
from openai import (
    APITimeoutError,
    InternalServerError,
    RateLimitError,
    UnprocessableEntityError,
    BadRequestError,
)
from openai.types import (
    Completion,
    CreateEmbeddingResponse,
)
from openai.types.chat import ChatCompletionChunk, ChatCompletion

from backend.components.generator.base import BaseGenerator, ModelType, GeneratorOutput
from backend.core.types import CompletionUsage

from backend.logging_config import setup_logging

setup_logging()
log = logging.getLogger(__name__)


def get_first_message_content(completion: ChatCompletion) -> str:
    """When we only need the content of the first message."""
    log.info(f"🔍 get_first_message_content called with: {type(completion)}")
    log.debug(f"raw completion: {completion}")
    
    try:
        if hasattr(completion, 'choices') and len(completion.choices) > 0:
            choice = completion.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                content = choice.message.content
                log.info(f"✅ Successfully extracted content: {type(content)}, length: {len(content) if content else 0}")
                return content
            else:
                log.error("❌ Choice doesn't have message.content")
                return str(completion)
        else:
            log.error("❌ Completion doesn't have choices")
            return str(completion)
    except Exception as e:
        log.error(f"❌ Error in get_first_message_content: {e}")
        return str(completion)


def parse_stream_response(completion: ChatCompletionChunk) -> str:
    """Parse the response of the stream API."""
    return completion.choices[0].delta.content


def handle_streaming_response(generator: Stream[ChatCompletionChunk]):
    """Handle the streaming response."""
    for completion in generator:
        log.debug(f"Raw chunk completion: {completion}")
        parsed_content = parse_stream_response(completion)
        yield parsed_content


def get_all_messages_content(completion: ChatCompletion) -> List[str]:
    """When the n > 1, get all the messages content."""
    return [c.message.content for c in completion.choices]


class DashScopeGenerator(BaseGenerator):
    """
    DashScope generator implementation.
    
    Supports both embedding and chat completion APIs through Alibaba Cloud.
    
    Args:
        api_key (Optional[str]): DashScope API key. If not provided, will use environment variable DASHSCOPE_API_KEY.
        chat_completion_parser (Callable[[Completion], Any]): Function to parse chat completion. Defaults to get_first_message_content.
        input_type (Literal["text", "messages"]): Input type for processing. Defaults to "text".
        base_url (str): The API base URL to use. Defaults to "https://dashscope.aliyuncs.com/api/v1".
        env_api_key_name (str): Environment variable name for API key. Defaults to "DASHSCOPE_API_KEY".
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        chat_completion_parser: Callable[[Completion], Any] = None,
        input_type: Literal["text", "messages"] = "text",
        base_url: Optional[str] = None,
        env_api_key_name: str = "DASHSCOPE_API_KEY",
    ):
        super().__init__(input_type=input_type)
        self._api_key = api_key
        self._env_api_key_name = env_api_key_name
        self.base_url = base_url or os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
        self.sync_client = self.init_sync_client()
        self.async_client = None  # Only initialize if the async call is called
        self.chat_completion_parser = chat_completion_parser or get_first_message_content
        self._api_kwargs = {}
    
    def init_sync_client(self):
        """Initialize the synchronous DashScope client."""
        api_key = self._api_key or os.getenv(self._env_api_key_name)
        if not api_key:
            raise ValueError(f"Environment variable {self._env_api_key_name} must be set")
        
        return OpenAI(
            api_key=api_key,
            base_url=self.base_url
        )
    
    def init_async_client(self):
        """Initialize the asynchronous DashScope client."""
        api_key = self._api_key or os.getenv(self._env_api_key_name)
        if not api_key:
            raise ValueError(f"Environment variable {self._env_api_key_name} must be set")
        
        return AsyncOpenAI(
            api_key=api_key,
            base_url=self.base_url
        )
    
    def parse_chat_completion(
        self,
        completion: Union[ChatCompletion, Generator[ChatCompletionChunk, None, None]],
    ) -> GeneratorOutput:
        """Parse the completion, and put it into the raw_response."""
        log.debug(f"completion: {completion}, parser: {self.chat_completion_parser}")
        
        # If the completion is already a GeneratorOutput, return it directly (prevent recursion)
        if isinstance(completion, GeneratorOutput):
            return completion
        
        try:
            data = self.chat_completion_parser(completion)
        except Exception as e:
            log.error(f"Error parsing the completion: {e}")
            return GeneratorOutput(data=None, error=str(e), raw_response=completion)
        
        try:
            usage = self.track_completion_usage(completion)
            return GeneratorOutput(
                data=None, error=None, raw_response=data, usage=usage
            )
        except Exception as e:
            log.error(f"Error tracking the completion usage: {e}")
            return GeneratorOutput(data=None, error=str(e), raw_response=data)
    
    def track_completion_usage(
        self,
        completion: Union[ChatCompletion, Generator[ChatCompletionChunk, None, None]],
    ) -> CompletionUsage:
        """Track completion usage statistics."""
        try:
            usage: CompletionUsage = CompletionUsage(
                completion_tokens=completion.usage.completion_tokens,
                prompt_tokens=completion.usage.prompt_tokens,
                total_tokens=completion.usage.total_tokens,
            )
            return usage
        except Exception as e:
            log.error(f"Error tracking the completion usage: {e}")
            return CompletionUsage(
                completion_tokens=None, prompt_tokens=None, total_tokens=None
            )
    
    def parse_embedding_response(
        self, response: CreateEmbeddingResponse
    ) -> GeneratorOutput:
        """Parse the embedding response to a structure components can understand."""
        try:
            # Extract embeddings from the response
            embeddings = []
            for item in response.data:
                embeddings.append(item.embedding)
            return GeneratorOutput(data=embeddings, error=None, raw_response=response)
        except Exception as e:
            log.error(f"Error parsing the embedding response: {e}")
            return GeneratorOutput(data=[], error=str(e), raw_response=response)
    
    def convert_inputs_to_api_kwargs(
        self,
        input: Optional[Any] = None,
        model_kwargs: Dict = {},
        model_type: ModelType = ModelType.UNDEFINED,
    ) -> Dict:
        """
        Convert the Component's standard input, and system_input(chat model) and model_kwargs into API-specific format.
        
        Args:
            input: The input text or messages to process
            model_kwargs: Additional parameters including:
                - images: Optional image source(s) as path, URL, or list of them
                - detail: Image detail level ('auto', 'low', or 'high'), defaults to 'auto'
                - model: The model to use (must support multimodal inputs if images are provided)
            model_type: The type of model (EMBEDDER or LLM)
            
        Returns:
            Dict: API-specific kwargs for the model call
        """
        final_model_kwargs = model_kwargs.copy()
        
        if model_type == ModelType.EMBEDDER:
            if isinstance(input, str):
                input = [input]
            if not isinstance(input, Sequence):
                raise TypeError("input must be a sequence of text")
            final_model_kwargs["input"] = input
            
        elif model_type == ModelType.LLM:
            # Convert input to messages
            messages: List[Dict[str, str]] = []
            images = final_model_kwargs.pop("images", None)
            detail = final_model_kwargs.pop("detail", "auto")
            
            if self._input_type == "messages":
                system_start_tag = "<START_OF_SYSTEM_PROMPT>"
                system_end_tag = "<END_OF_SYSTEM_PROMPT>"
                user_start_tag = "<START_OF_USER_PROMPT>"
                user_end_tag = "<END_OF_USER_PROMPT>"
                
                # New regex pattern to ignore special characters such as \n
                pattern = (
                    rf"{system_start_tag}\s*(.*?)\s*{system_end_tag}\s*"
                    rf"{user_start_tag}\s*(.*?)\s*{user_end_tag}"
                )
                
                regex = re.compile(pattern, re.DOTALL)
                match = regex.match(input)
                system_prompt, input_str = None, None
                
                if match:
                    system_prompt = match.group(1)
                    input_str = match.group(2)
                else:
                    print("No match found.")
                    
                if system_prompt and input_str:
                    messages.append({"role": "system", "content": system_prompt})
                    if images:
                        content = [{"type": "text", "text": input_str}]
                        if isinstance(images, (str, dict)):
                            images = [images]
                        for img in images:
                            content.append(self._prepare_image_content(img, detail))
                        messages.append({"role": "user", "content": content})
                    else:
                        messages.append({"role": "user", "content": input_str})
                        
            if len(messages) == 0:
                if images:
                    content = [{"type": "text", "text": input}]
                    if isinstance(images, (str, dict)):
                        images = [images]
                    for img in images:
                        content.append(self._prepare_image_content(img, detail))
                    messages.append({"role": "user", "content": content})
                else:
                    messages.append({"role": "user", "content": input})
                    
            final_model_kwargs["messages"] = messages
            
        else:
            raise ValueError(f"model_type {model_type} is not supported")
            
        return final_model_kwargs
    
    @backoff.on_exception(
        backoff.expo,
        (
            APITimeoutError,
            InternalServerError,
            RateLimitError,
            UnprocessableEntityError,
            BadRequestError,
        ),
        max_time=5,
    )
    def call(self, api_kwargs: Dict = {}, model_type: ModelType = ModelType.UNDEFINED):
        """Execute synchronous call to DashScope API."""
        log.info(f"api_kwargs: {api_kwargs}")
        self._api_kwargs = api_kwargs
        
        if model_type == ModelType.EMBEDDER:
            return self.sync_client.embeddings.create(**api_kwargs)
        elif model_type == ModelType.LLM:
            if "stream" in api_kwargs and api_kwargs.get("stream", False):
                log.debug("streaming call")
                self.chat_completion_parser = handle_streaming_response
                return self.sync_client.chat.completions.create(**api_kwargs)
            else:
                log.debug("non-streaming call")
                return self.sync_client.chat.completions.create(**api_kwargs)
        else:
            raise ValueError(f"model_type {model_type} is not supported")
    
    @backoff.on_exception(
        backoff.expo,
        (
            APITimeoutError,
            InternalServerError,
            RateLimitError,
            UnprocessableEntityError,
            BadRequestError,
        ),
        max_time=5,
    )
    async def acall(
        self, api_kwargs: Dict = {}, model_type: ModelType = ModelType.UNDEFINED
    ):
        """Execute asynchronous call to DashScope API."""
        # Store the api kwargs in the client
        self._api_kwargs = api_kwargs
        if self.async_client is None:
            self.async_client = self.init_async_client()
            
        if model_type == ModelType.EMBEDDER:
            return await self.async_client.embeddings.create(**api_kwargs)
        elif model_type == ModelType.LLM:
            return await self.async_client.chat.completions.create(**api_kwargs)
        else:
            raise ValueError(f"model_type {model_type} is not supported")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from dictionary."""
        obj = super().from_dict(data)
        # Recreate the existing clients
        obj.sync_client = obj.init_sync_client()
        obj.async_client = obj.init_async_client()
        return obj
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the component to a dictionary."""
        exclude = ["sync_client", "async_client"]  # Unserializable object
        output = {}
        for key, value in self.__dict__.items():
            if key not in exclude:
                output[key] = value
        return output
    
    def _prepare_image_content(
        self, image_source: Union[str, Dict[str, Any]], detail: str = "auto"
    ) -> Dict[str, Any]:
        """Prepare image content for API request."""
        if isinstance(image_source, str):
            if image_source.startswith(("http://", "https://")):
                return {
                    "type": "image_url",
                    "image_url": {"url": image_source, "detail": detail},
                }
            else:
                # For local files, we would need to encode them
                # This is a simplified version - in practice, you might want to handle file encoding
                return {
                    "type": "image_url",
                    "image_url": {"url": image_source, "detail": detail},
                }
        return image_source
