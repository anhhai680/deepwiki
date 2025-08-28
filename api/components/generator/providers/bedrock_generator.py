"""
AWS Bedrock generator implementation.

This module provides AWS Bedrock-specific generator functionality,
extracted from the existing bedrock_client.py implementation.
"""

import os
import json
import logging
import boto3
import botocore
import backoff
from typing import Dict, Any, Optional, List, Generator, Union, AsyncGenerator

from api.components.generator.base import BaseGenerator, ModelType, GeneratorOutput
from api.core.types import CompletionUsage

# Configure logging
from api.logging_config import setup_logging

setup_logging()
log = logging.getLogger(__name__)


class BedrockGenerator(BaseGenerator):
    """
    AWS Bedrock generator implementation.
    
    AWS Bedrock provides a unified API that gives access to various foundation models
    including Amazon's own models and third-party models like Anthropic Claude.
    
    Args:
        aws_access_key_id (Optional[str]): AWS access key ID. If not provided, will use environment variable AWS_ACCESS_KEY_ID.
        aws_secret_access_key (Optional[str]): AWS secret access key. If not provided, will use environment variable AWS_SECRET_ACCESS_KEY.
        aws_region (Optional[str]): AWS region. If not provided, will use environment variable AWS_REGION.
        aws_role_arn (Optional[str]): AWS IAM role ARN for role-based authentication. If not provided, will use environment variable AWS_ROLE_ARN.
    """
    
    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_region: Optional[str] = None,
        aws_role_arn: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        
        # Import config here to avoid circular imports
        from api.core.config.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_ROLE_ARN
        
        self.aws_access_key_id = aws_access_key_id or AWS_ACCESS_KEY_ID
        self.aws_secret_access_key = aws_secret_access_key or AWS_SECRET_ACCESS_KEY
        self.aws_region = aws_region or AWS_REGION or "us-east-1"
        self.aws_role_arn = aws_role_arn or AWS_ROLE_ARN
        
        self.sync_client = self.init_sync_client()
        self.async_client = None  # Initialize async client only when needed
    
    def init_sync_client(self):
        """Initialize the synchronous AWS Bedrock client."""
        try:
            # Create a session with the provided credentials
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
            
            # If a role ARN is provided, assume that role
            if self.aws_role_arn:
                sts_client = session.client('sts')
                assumed_role = sts_client.assume_role(
                    RoleArn=self.aws_role_arn,
                    RoleSessionName="DeepWikiBedrockSession"
                )
                credentials = assumed_role['Credentials']
                
                # Create a new session with the assumed role credentials
                session = boto3.Session(
                    aws_access_key_id=credentials['AccessKeyId'],
                    aws_secret_access_key=credentials['SecretAccessKey'],
                    aws_session_token=credentials['SessionToken'],
                    region_name=self.aws_region
                )
            
            # Create the Bedrock client
            bedrock_runtime = session.client(
                service_name='bedrock-runtime',
                region_name=self.aws_region
            )
            
            return bedrock_runtime
            
        except Exception as e:
            log.error(f"Failed to initialize Bedrock client: {e}")
            raise
    
    def init_async_client(self):
        """Initialize the asynchronous AWS Bedrock client."""
        # For now, we'll use the sync client for async operations
        # In a future implementation, we could use aioboto3
        return self.sync_client
    
    def convert_inputs_to_api_kwargs(
        self,
        input: Any = None,
        model_kwargs: Dict = None,
        model_type: ModelType = ModelType.UNDEFINED
    ) -> Dict:
        """Convert inputs to Bedrock API format."""
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
                raise ValueError(f"Unsupported input format for Bedrock: {type(input)}")
            
            # For debugging
            log.info(f"Messages for Bedrock: {messages}")
            
            api_kwargs = {
                "messages": messages,
                **model_kwargs
            }
            
            # Ensure model is specified
            if "model" not in api_kwargs:
                api_kwargs["model"] = "anthropic.claude-3-sonnet-20240229-v1:0"
                
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
                api_kwargs["model"] = "amazon.titan-embed-text-v1"
                
            return api_kwargs
            
        else:
            raise ValueError(f"Model type {model_type} not supported by Bedrock")
    
    def parse_chat_completion(self, completion: Any) -> GeneratorOutput:
        """Parse Bedrock chat completion response."""
        try:
            # Extract the response content from Bedrock response
            if hasattr(completion, 'body'):
                # Parse the response body
                response_body = json.loads(completion.body.read())
                
                # Extract content based on model type
                if 'completion' in response_body:
                    # Anthropic Claude format
                    content = response_body['completion']
                elif 'generation' in response_body:
                    # Amazon Titan format
                    content = response_body['generation']
                elif 'content' in response_body:
                    # Generic format
                    content = response_body['content']
                else:
                    content = str(response_body)
                    
                # Extract usage if available
                usage = None
                if 'usage' in response_body:
                    usage_data = response_body['usage']
                    usage = CompletionUsage(
                        completion_tokens=usage_data.get('completion_tokens'),
                        prompt_tokens=usage_data.get('prompt_tokens'),
                        total_tokens=usage_data.get('total_tokens')
                    )
                
                return GeneratorOutput(
                    data=content,
                    error=None,
                    raw_response=response_body,
                    usage=usage
                )
            else:
                # Handle direct response
                return GeneratorOutput(
                    data=str(completion),
                    error=None,
                    raw_response=completion
                )
                
        except Exception as e:
            log.error(f"Error parsing Bedrock completion: {e}")
            return GeneratorOutput(
                data=None,
                error=str(e),
                raw_response=completion
            )
    
    def parse_embedding_response(self, response: Any) -> GeneratorOutput:
        """Parse Bedrock embedding response."""
        try:
            if hasattr(response, 'body'):
                # Parse the response body
                response_body = json.loads(response.body.read())
                
                # Extract embeddings
                if 'embedding' in response_body:
                    embeddings = response_body['embedding']
                elif 'embeddings' in response_body:
                    embeddings = [item['embedding'] for item in response_body['embeddings']]
                else:
                    embeddings = []
                
                return GeneratorOutput(
                    data=embeddings,
                    error=None,
                    raw_response=response_body
                )
            else:
                return GeneratorOutput(
                    data=[],
                    error="Invalid response format",
                    raw_response=response
                )
                
        except Exception as e:
            log.error(f"Error parsing Bedrock embedding response: {e}")
            return GeneratorOutput(
                data=[],
                error=str(e),
                raw_response=response
            )
    
    @backoff.on_exception(
        backoff.expo,
        (botocore.exceptions.ClientError, botocore.exceptions.NoCredentialsError),
        max_time=30
    )
    def call(self, api_kwargs: Dict = None, model_type: ModelType = None) -> Any:
        """Execute synchronous call to AWS Bedrock."""
        api_kwargs = api_kwargs or {}
        model_type = model_type or ModelType.LLM
        
        try:
            if model_type == ModelType.LLM:
                # Invoke the model for text generation
                response = self.sync_client.invoke_model(
                    modelId=api_kwargs["model"],
                    body=json.dumps(api_kwargs)
                )
                return response
                
            elif model_type == ModelType.EMBEDDER:
                # Invoke the model for embeddings
                response = self.sync_client.invoke_model(
                    modelId=api_kwargs["model"],
                    body=json.dumps(api_kwargs)
                )
                return response
                
            else:
                raise ValueError(f"Model type {model_type} not supported")
                
        except botocore.exceptions.ClientError as e:
            log.error(f"Bedrock API error: {e}")
            raise
        except Exception as e:
            log.error(f"Unexpected error in Bedrock call: {e}")
            raise
    
    async def acall(
        self, api_kwargs: Dict = None, model_type: ModelType = None
    ) -> Any:
        """Execute asynchronous call to AWS Bedrock."""
        # For now, we'll use the sync client
        # In a future implementation, we could use aioboto3 for true async
        return self.call(api_kwargs, model_type)
    
    def convert_inputs_to_api_kwargs(
        self,
        input: Any = None,
        model_kwargs: Dict = None,
        model_type: ModelType = ModelType.UNDEFINED
    ) -> Dict:
        """Convert inputs to Bedrock API format."""
        return self.convert_inputs_to_api_kwargs(input, model_kwargs, model_type)
    
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
