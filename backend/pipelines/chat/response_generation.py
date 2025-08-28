"""
Response generation step for the chat pipeline.

This module handles the AI model interactions and streaming responses
for different AI providers in the chat pipeline.
"""

import logging
import google.generativeai as genai
from typing import AsyncGenerator, Any, Dict

from ..base.base_pipeline import PipelineStep, PipelineContext
from .chat_context import ChatPipelineContext
from adalflow.components.model_client.ollama_client import OllamaClient
from adalflow.core.types import ModelType


class ResponseGenerationStep(PipelineStep[ChatPipelineContext, ChatPipelineContext]):
    """Step to generate streaming responses from AI models."""
    
    def __init__(self):
        super().__init__("ResponseGeneration")
    
    def _clean_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove keys with None values recursively from a dict."""
        if not isinstance(data, dict):
            return data
        cleaned: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, dict):
                nested = self._clean_dict(value)
                if len(nested) > 0:
                    cleaned[key] = nested
            elif value is not None:
                cleaned[key] = value
        return cleaned
    
    def execute(self, context: ChatPipelineContext) -> ChatPipelineContext:
        """Generate streaming response from the AI model."""
        self.logger.info("Generating AI response")
        
        # This step prepares the context for response generation
        # The actual streaming is handled by the pipeline's execute method
        # which returns an async generator
        
        self.logger.info("Response generation context prepared")
        return context
    
    async def generate_streaming_response(self, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate streaming response from the AI model."""
        self.logger.info(f"Starting streaming response generation for {context.provider}")
        
        # Ensure model_config is always a dictionary
        if context.model_config is None:
            context.model_config = {}
        
        try:
            if context.provider == "ollama":
                async for chunk in self._generate_ollama_response(context):
                    yield chunk
            elif context.provider == "openrouter":
                async for chunk in self._generate_openrouter_response(context):
                    yield chunk
            elif context.provider == "openai":
                async for chunk in self._generate_openai_response(context):
                    yield chunk
            elif context.provider == "bedrock":
                async for chunk in self._generate_bedrock_response(context):
                    yield chunk
            elif context.provider == "azure":
                async for chunk in self._generate_azure_response(context):
                    yield chunk
            else:
                # Default to Google Generative AI
                async for chunk in self._generate_google_response(context):
                    yield chunk
                
        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Error in streaming response: {error_message}")
            
            # Check for token limit errors and try fallback
            if any(phrase in error_message.lower() for phrase in ["maximum context length", "token limit", "too many tokens"]):
                self.logger.warning("Token limit exceeded, retrying without context")
                async for chunk in self._generate_fallback_response(context):
                    yield chunk
            else:
                yield f"\nError: {error_message}"
    
    async def _generate_ollama_response(self, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate streaming response from Ollama."""
        model = OllamaClient()
        model_name = context.model or context.model_config.get("model")
        model_kwargs = self._clean_dict({
            "model": model_name,
            "stream": True,
            "options": {
                "temperature": context.model_config.get("temperature"),
                "top_p": context.model_config.get("top_p"),
                "num_ctx": context.model_config.get("num_ctx")
            }
        })
        
        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=context.final_prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
        
        response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
        
        async for chunk in response:
            text = getattr(chunk, 'response', None) or getattr(chunk, 'text', None) or str(chunk)
            if text and not text.startswith('model=') and not text.startswith('created_at='):
                text = text.replace('<think>', '').replace('</think>', '')
                yield text
    
    async def _generate_openrouter_response(self, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate streaming response from OpenRouter."""
        from backend.components.generator.providers.openrouter_generator import OpenRouterGenerator
        
        model = OpenRouterGenerator()
        model_kwargs = {
            "model": context.model,
            "stream": True,
            "temperature": context.model_config.get("temperature")
        }
        
        top_p = context.model_config.get("top_p")
        if top_p is not None:
            model_kwargs["top_p"] = top_p
        model_kwargs = self._clean_dict(model_kwargs)
        
        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=context.final_prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
        
        try:
            response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
            async for chunk in response:
                yield chunk
        except Exception as e:
            yield f"\nError with OpenRouter API: {str(e)}\n\nPlease check that you have set the OPENROUTER_API_KEY environment variable with a valid API key."
    
    async def _generate_openai_response(self, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate streaming response from OpenAI."""
        from backend.components.generator.providers.openai_generator import OpenAIGenerator
        
        model = OpenAIGenerator()
        model_kwargs = {
            "model": context.model,
            "stream": True,
            "temperature": context.model_config.get("temperature")
        }
        
        top_p = context.model_config.get("top_p")
        if top_p is not None:
            model_kwargs["top_p"] = top_p
        model_kwargs = self._clean_dict(model_kwargs)
        
        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=context.final_prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
        
        try:
            response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
            async for chunk in response:
                choices = getattr(chunk, "choices", [])
                if len(choices) > 0:
                    delta = getattr(choices[0], "delta", None)
                    if delta is not None:
                        text = getattr(delta, "content", None)
                        if text is not None:
                            yield text
        except Exception as e:
            yield f"\nError with OpenAI API: {str(e)}\n\nPlease check that you have set the OPENAI_API_KEY environment variable with a valid API key."
    
    async def _generate_bedrock_response(self, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate streaming response from AWS Bedrock."""
        from backend.components.generator.providers.bedrock_generator import BedrockGenerator
        
        model = BedrockGenerator()
        model_kwargs = self._clean_dict({
            "model": context.model,
            "temperature": context.model_config.get("temperature"),
            "top_p": context.model_config.get("top_p")
        })
        
        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=context.final_prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
        
        try:
            response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
            if isinstance(response, str):
                yield response
            else:
                yield str(response)
        except Exception as e:
            yield f"\nError with AWS Bedrock API: {str(e)}\n\nPlease check that you have set the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables with valid credentials."
    
    async def _generate_azure_response(self, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate streaming response from Azure AI."""
        from backend.components.generator.providers.azure_generator import AzureAIGenerator
        
        model = AzureAIGenerator()
        model_kwargs = {
            "model": context.model,
            "stream": True,
            "temperature": context.model_config.get("temperature"),
            "top_p": context.model_config.get("top_p")
        }
        model_kwargs = self._clean_dict(model_kwargs)
        
        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=context.final_prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
        
        try:
            response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
            async for chunk in response:
                choices = getattr(chunk, "choices", [])
                if len(choices) > 0:
                    delta = getattr(choices[0], "delta", None)
                    if delta is not None:
                        text = getattr(delta, "content", None)
                        if text is not None:
                            yield text
        except Exception as e:
            yield f"\nError with Azure AI API: {str(e)}\n\nPlease check that you have set the AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_VERSION environment variables with valid values."
    
    async def _generate_google_response(self, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate streaming response from Google Generative AI."""
        model_name = context.model or context.model_config.get("model")
        generation_config = self._clean_dict({
            "temperature": context.model_config.get("temperature"),
            "top_p": context.model_config.get("top_p"),
            "top_k": context.model_config.get("top_k")
        })
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        
        response = model.generate_content(context.final_prompt, stream=True)
        for chunk in response:
            if hasattr(chunk, 'text'):
                yield chunk.text
    
    async def _generate_fallback_response(self, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate fallback response without context when token limits are exceeded."""
        self.logger.info("Generating fallback response without context")
        
        # Create a simplified prompt without context
        simplified_prompt = f"/no_think {context.system_prompt}\n\n"
        if context.conversation_history:
            simplified_prompt += f"<conversation_history>\n{context.conversation_history}</conversation_history>\n\n"
        
        # Include file content in the fallback prompt if it was retrieved
        if context.file_path and context.file_content:
            simplified_prompt += f"<currentFileContent path=\"{context.file_path}\">\n{context.file_content}\n</currentFileContent>\n\n"
        
        simplified_prompt += "<note>Answering without retrieval augmentation due to input size constraints.</note>\n\n"
        
        query = context.messages[-1].get('content', '')
        simplified_prompt += f"<query>\n{query}\n</query>\n\nAssistant: "
        
        # Generate fallback response based on provider
        try:
            if context.provider == "ollama":
                simplified_prompt += " /no_think"
                async for chunk in self._generate_ollama_fallback(simplified_prompt, context):
                    yield chunk
            elif context.provider == "openrouter":
                async for chunk in self._generate_openrouter_fallback(simplified_prompt, context):
                    yield chunk
            elif context.provider == "openai":
                async for chunk in self._generate_openai_fallback(simplified_prompt, context):
                    yield chunk
            elif context.provider == "bedrock":
                async for chunk in self._generate_bedrock_fallback(simplified_prompt, context):
                    yield chunk
            elif context.provider == "azure":
                async for chunk in self._generate_azure_fallback(simplified_prompt, context):
                    yield chunk
            else:
                async for chunk in self._generate_google_fallback(simplified_prompt, context):
                    yield chunk
        except Exception as e:
            self.logger.error(f"Error in fallback response: {str(e)}")
            yield f"\nI apologize, but your request is too large for me to process. Please try a shorter query or break it into smaller parts."
    
    async def _generate_ollama_fallback(self, simplified_prompt: str, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate Ollama fallback response."""
        model = OllamaClient()
        model_name = context.model or context.model_config.get("model")
        model_kwargs = self._clean_dict({
            "model": model_name,
            "stream": True,
            "options": {
                "temperature": context.model_config.get("temperature"),
                "top_p": context.model_config.get("top_p"),
                "num_ctx": context.model_config.get("num_ctx")
            }
        })
        
        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=simplified_prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
        
        response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
        async for chunk in response:
            text = getattr(chunk, 'response', None) or getattr(chunk, 'text', None) or str(chunk)
            if text and not text.startswith('model=') and not text.startswith('created_at='):
                text = text.replace('<think>', '').replace('</think>', '')
                yield text
    
    async def _generate_openrouter_fallback(self, simplified_prompt: str, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate OpenRouter fallback response."""
        from api.components.generator.providers.openrouter_generator import OpenRouterGenerator
        
        model = OpenRouterGenerator()
        model_kwargs = {
            "model": context.model,
            "stream": True,
            "temperature": context.model_config.get("temperature")
        }
        
        top_p = context.model_config.get("top_p")
        if top_p is not None:
            model_kwargs["top_p"] = top_p
        model_kwargs = self._clean_dict(model_kwargs)
        
        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=simplified_prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
        
        try:
            response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
            async for chunk in response:
                yield chunk
        except Exception as e:
            yield f"\nError with OpenRouter API fallback: {str(e)}\n\nPlease check that you have set the OPENROUTER_API_KEY environment variable with a valid API key."
    
    async def _generate_openai_fallback(self, simplified_prompt: str, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate OpenAI fallback response."""
        from backend.components.generator.providers.openai_generator import OpenAIGenerator
        
        model = OpenAIGenerator()
        model_kwargs = {
            "model": context.model,
            "stream": True,
            "temperature": context.model_config.get("temperature")
        }
        
        top_p = context.model_config.get("top_p")
        if top_p is not None:
            model_kwargs["top_p"] = top_p
        model_kwargs = self._clean_dict(model_kwargs)
        
        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=simplified_prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
        
        try:
            response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
            async for chunk in response:
                text = chunk if isinstance(chunk, str) else getattr(chunk, 'text', str(chunk))
                yield text
        except Exception as e:
            yield f"\nError with OpenAI API fallback: {str(e)}\n\nPlease check that you have set the OPENAI_API_KEY environment variable with a valid API key."
    
    async def _generate_bedrock_fallback(self, simplified_prompt: str, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate Bedrock fallback response."""
        from backend.components.generator.providers.bedrock_generator import BedrockGenerator
        
        model = BedrockGenerator()
        model_kwargs = self._clean_dict({
            "model": context.model,
            "temperature": context.model_config.get("temperature"),
            "top_p": context.model_config.get("top_p")
        })
        
        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=simplified_prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
        
        try:
            response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
            if isinstance(response, str):
                yield response
            else:
                yield str(response)
        except Exception as e:
            yield f"\nError with AWS Bedrock API fallback: {str(e)}\n\nPlease check that you have set the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables with valid credentials."
    
    async def _generate_azure_fallback(self, simplified_prompt: str, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate Azure AI fallback response."""
        from backend.components.generator.providers.azure_generator import AzureAIGenerator
        
        model = AzureAIGenerator()
        model_kwargs = {
            "model": context.model,
            "stream": True,
            "temperature": context.model_config.get("temperature"),
            "top_p": context.model_config.get("top_p")
        }
        model_kwargs = self._clean_dict(model_kwargs)
        
        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=simplified_prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
        
        try:
            response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
            async for chunk in response:
                choices = getattr(chunk, "choices", [])
                if len(choices) > 0:
                    delta = getattr(choices[0], "delta", None)
                    if delta is not None:
                        text = getattr(delta, "content", None)
                        if text is not None:
                            yield text
        except Exception as e:
            yield f"\nError with Azure AI API fallback: {str(e)}\n\nPlease check that you have set the AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_VERSION environment variables with valid values."
    
    async def _generate_google_fallback(self, simplified_prompt: str, context: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Generate Google Generative AI fallback response."""
        model_name = context.model or context.model_config.get("model")
        generation_config = self._clean_dict({
            "temperature": context.model_config.get("temperature", 0.7),
            "top_p": context.model_config.get("top_p", 0.8),
            "top_k": context.model_config.get("top_k", 40)
        })
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        
        response = model.generate_content(simplified_prompt, stream=True)
        for chunk in response:
            if hasattr(chunk, 'text'):
                yield chunk.text
