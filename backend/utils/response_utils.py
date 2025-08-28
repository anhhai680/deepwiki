"""
Response Processing Utilities

This module contains utility functions for processing and extracting responses from various AI providers
extracted from various components throughout the codebase.
"""

import logging
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)


def extract_response_text(provider: str, response: Dict[str, Any]) -> str:
    """
    Extract the generated text from the response based on provider.
    
    Args:
        provider (str): The provider name, e.g., "anthropic", "openai", "google"
        response (Dict[str, Any]): The response from the AI provider
        
    Returns:
        str: The extracted text content
    """
    try:
        if provider == "anthropic":
            return response.get("content", [{}])[0].get("text", "")
        elif provider == "amazon":
            return response.get("results", [{}])[0].get("outputText", "")
        elif provider == "cohere":
            return response.get("generations", [{}])[0].get("text", "")
        elif provider == "ai21":
            return response.get("completions", [{}])[0].get("data", {}).get("text", "")
        elif provider == "openai":
            return response.get("choices", [{}])[0].get("message", {}).get("content", "")
        elif provider == "google":
            return response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        elif provider == "ollama":
            return response.get("response", "")
        elif provider == "dashscope":
            return response.get("output", {}).get("text", "")
        else:
            # Try to extract text from common response patterns
            if isinstance(response, dict):
                for key in ["text", "content", "output", "completion", "response", "message"]:
                    if key in response:
                        value = response[key]
                        if isinstance(value, str):
                            return value
                        elif isinstance(value, dict) and "content" in value:
                            return value["content"]
                        elif isinstance(value, list) and len(value) > 0:
                            if isinstance(value[0], str):
                                return value[0]
                            elif isinstance(value[0], dict) and "text" in value[0]:
                                return value[0]["text"]
            
            # Fallback: return string representation
            return str(response)
            
    except Exception as e:
        logger.error(f"Error extracting response text from {provider}: {e}")
        return str(response)


def parse_stream_response(completion: Any) -> str:
    """
    Parse the response from a streaming completion.
    
    Args:
        completion: Streaming completion chunk
        
    Returns:
        str: Parsed content from the chunk
    """
    try:
        # Handle different provider formats
        if hasattr(completion, 'choices') and len(completion.choices) > 0:
            # OpenAI format
            return completion.choices[0].delta.content or ""
        elif hasattr(completion, 'candidates') and len(completion.candidates) > 0:
            # Google format
            return completion.candidates[0].content.parts[0].text or ""
        elif hasattr(completion, 'response'):
            # Ollama format
            return completion.response or ""
        elif hasattr(completion, 'content') and len(completion.content) > 0:
            # Anthropic format
            return completion.content[0].text or ""
        else:
            # Generic format
            return str(completion)
    except Exception as e:
        logger.error(f"Error parsing stream response: {e}")
        return str(completion)


def handle_streaming_response(generator: Any) -> str:
    """
    Handle streaming response and collect all content.
    
    Args:
        generator: Streaming response generator
        
    Returns:
        str: Complete response content
    """
    try:
        content_parts = []
        for chunk in generator:
            parsed_content = parse_stream_response(chunk)
            if parsed_content:
                content_parts.append(parsed_content)
        
        return "".join(content_parts)
    except Exception as e:
        logger.error(f"Error handling streaming response: {e}")
        return ""


def get_all_messages_content(completion: Any) -> List[str]:
    """
    Get all message content when n > 1.
    
    Args:
        completion: Completion response with multiple choices
        
    Returns:
        List[str]: List of message contents
    """
    try:
        if hasattr(completion, 'choices'):
            return [choice.message.content for choice in completion.choices if hasattr(choice, 'message')]
        else:
            return [str(completion)]
    except Exception as e:
        logger.error(f"Error getting all messages content: {e}")
        return [str(completion)]


def extract_response_metadata(response: Dict[str, Any], provider: str) -> Dict[str, Any]:
    """
    Extract metadata from AI provider response.
    
    Args:
        response (Dict[str, Any]): Response from AI provider
        provider (str): Provider name
        
    Returns:
        Dict[str, Any]: Extracted metadata
    """
    metadata = {
        "provider": provider,
        "model": None,
        "usage": None,
        "finish_reason": None,
        "response_time": None
    }
    
    try:
        if provider == "openai":
            metadata["model"] = response.get("model")
            metadata["usage"] = response.get("usage")
            if response.get("choices"):
                metadata["finish_reason"] = response["choices"][0].get("finish_reason")
        elif provider == "google":
            metadata["model"] = response.get("model")
            metadata["usage"] = response.get("usageMetadata")
            if response.get("candidates"):
                metadata["finish_reason"] = response["candidates"][0].get("finishReason")
        elif provider == "anthropic":
            metadata["model"] = response.get("model")
            metadata["usage"] = response.get("usage")
            metadata["finish_reason"] = response.get("stop_reason")
        elif provider == "ollama":
            metadata["model"] = response.get("model")
            metadata["usage"] = response.get("usage")
        elif provider == "dashscope":
            metadata["model"] = response.get("model")
            metadata["usage"] = response.get("usage")
        
        # Extract common fields
        if not metadata["model"]:
            metadata["model"] = response.get("model")
        if not metadata["usage"]:
            metadata["usage"] = response.get("usage")
        if not metadata["finish_reason"]:
            metadata["finish_reason"] = response.get("finish_reason", response.get("stop_reason"))
            
    except Exception as e:
        logger.error(f"Error extracting response metadata: {e}")
    
    return metadata


def validate_response_format(response: Dict[str, Any], expected_format: str = "text") -> bool:
    """
    Validate that response has the expected format.
    
    Args:
        response (Dict[str, Any]): Response to validate
        expected_format (str): Expected format ("text", "json", "structured")
        
    Returns:
        bool: True if response has expected format
    """
    try:
        if expected_format == "text":
            # Check if response contains text content
            text_content = extract_response_text("generic", response)
            return bool(text_content and text_content.strip())
        
        elif expected_format == "json":
            # Check if response is valid JSON
            import json
            if isinstance(response, str):
                json.loads(response)
                return True
            elif isinstance(response, dict):
                return True
            return False
        
        elif expected_format == "structured":
            # Check if response has structured format
            required_keys = ["content", "metadata"]
            return all(key in response for key in required_keys)
        
        return False
        
    except Exception as e:
        logger.error(f"Error validating response format: {e}")
        return False


def normalize_response(response: Any, provider: str) -> Dict[str, Any]:
    """
    Normalize response from different providers to a common format.
    
    Args:
        response (Any): Raw response from provider
        provider (str): Provider name
        
    Returns:
        Dict[str, Any]: Normalized response
    """
    try:
        # Extract text content
        text_content = extract_response_text(provider, response)
        
        # Extract metadata
        metadata = extract_response_metadata(response, provider)
        
        # Create normalized format
        normalized = {
            "content": text_content,
            "metadata": metadata,
            "provider": provider,
            "raw_response": response
        }
        
        return normalized
        
    except Exception as e:
        logger.error(f"Error normalizing response: {e}")
        return {
            "content": str(response),
            "metadata": {"provider": provider, "error": str(e)},
            "provider": provider,
            "raw_response": response
        }


def format_response_for_output(response: Dict[str, Any], output_format: str = "text") -> Union[str, Dict[str, Any]]:
    """
    Format response for different output formats.
    
    Args:
        response (Dict[str, Any]): Normalized response
        output_format (str): Desired output format
        
    Returns:
        Union[str, Dict[str, Any]]: Formatted response
    """
    try:
        if output_format == "text":
            return response.get("content", "")
        elif output_format == "json":
            return response
        elif output_format == "minimal":
            return {
                "content": response.get("content", ""),
                "provider": response.get("provider"),
                "model": response.get("metadata", {}).get("model")
            }
        else:
            return response
            
    except Exception as e:
        logger.error(f"Error formatting response: {e}")
        return response


def create_error_response(error_message: str, provider: str, error_type: str = "processing_error") -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        error_message (str): Error message
        provider (str): Provider name
        error_type (str): Type of error
        
    Returns:
        Dict[str, Any]: Standardized error response
    """
    return {
        "content": f"Error: {error_message}",
        "metadata": {
            "provider": provider,
            "error": True,
            "error_type": error_type,
            "error_message": error_message
        },
        "provider": provider,
        "success": False
    }


def merge_streaming_responses(responses: List[str]) -> str:
    """
    Merge multiple streaming response chunks into a single response.
    
    Args:
        responses (List[str]): List of response chunks
        
    Returns:
        str: Merged response
    """
    try:
        # Remove empty responses and join
        valid_responses = [r for r in responses if r and r.strip()]
        return "".join(valid_responses)
    except Exception as e:
        logger.error(f"Error merging streaming responses: {e}")
        return "".join(str(r) for r in responses)
