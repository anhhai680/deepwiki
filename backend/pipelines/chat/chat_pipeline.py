"""
Main chat pipeline for DeepWiki.

This module provides the main chat pipeline that orchestrates all chat steps
and provides a streaming interface for chat completions.
"""

import logging
from typing import AsyncGenerator, Dict, Any, List

from ..base.base_pipeline import BasePipeline, PipelineContext
from .chat_context import ChatPipelineContext
from .steps import (
    RequestValidationStep,
    ConversationAnalysisStep,
    SystemPromptGenerationStep,
    ContextPreparationStep,
    PromptAssemblyStep
)
from .response_generation import ResponseGenerationStep


class ChatPipeline(BasePipeline[ChatPipelineContext, ChatPipelineContext, ChatPipelineContext]):
    """Main chat pipeline that orchestrates all chat operations."""
    
    def __init__(self):
        super().__init__("ChatPipeline")
        self._setup_pipeline()
    
    def _setup_pipeline(self):
        """Set up the pipeline with all required steps."""
        self.add_steps(
            RequestValidationStep(),
            ConversationAnalysisStep(),
            SystemPromptGenerationStep(),
            ContextPreparationStep(),
            PromptAssemblyStep(),
            ResponseGenerationStep()
        )
        self.logger.info("Chat pipeline steps configured")
    
    def execute(self, input_data: ChatPipelineContext) -> ChatPipelineContext:
        """Execute the chat pipeline with the given input."""
        self.logger.info("Starting chat pipeline execution")
        
        # Set the context
        self.set_context(input_data)
        
        # Validate the context
        if not input_data.validate():
            self.logger.error("Context validation failed")
            return input_data
        
        # Execute all steps sequentially
        current_context = input_data
        for step in self.steps:
            try:
                self.logger.debug(f"Executing step: {step.name}")
                current_context = step.execute(current_context)
                
                # Check for errors after each step
                if current_context.errors:
                    self.logger.error(f"Step {step.name} encountered errors: {current_context.errors}")
                    break
                    
            except Exception as e:
                error_msg = f"Error executing step {step.name}: {str(e)}"
                current_context.add_error(error_msg)
                self.logger.error(error_msg)
                break
        
        # Mark pipeline as completed
        current_context.mark_completed()
        
        self.logger.info("Chat pipeline execution completed")
        return current_context
    
    async def execute_streaming(self, input_data: ChatPipelineContext) -> AsyncGenerator[str, None]:
        """Execute the chat pipeline and return a streaming response."""
        self.logger.info("Starting streaming chat pipeline execution")
        
        # Execute the pipeline to prepare context
        context = self.execute(input_data)
        
        # Check for errors
        if context.errors:
            error_message = f"Pipeline execution failed: {'; '.join(context.errors)}"
            self.logger.error(error_message)
            yield f"\nError: {error_message}"
            return
        
        # Get the response generation step
        response_step = None
        for step in self.steps:
            if isinstance(step, ResponseGenerationStep):
                response_step = step
                break
        
        if not response_step:
            error_message = "Response generation step not found"
            self.logger.error(error_message)
            yield f"\nError: {error_message}"
            return
        
        # Generate streaming response
        try:
            async for chunk in response_step.generate_streaming_response(context):
                yield chunk
        except Exception as e:
            error_message = f"Error in streaming response: {str(e)}"
            self.logger.error(error_message)
            yield f"\nError: {error_message}"
    
    def create_context_from_request(self, request_data: Dict[str, Any]) -> ChatPipelineContext:
        """Create a chat pipeline context from request data."""
        self.logger.info("Creating chat pipeline context from request")
        
        # Extract basic request data
        context = ChatPipelineContext(
            repo_url=request_data.get("repo_url", ""),
            repo_type=request_data.get("type", "github"),
            token=request_data.get("token"),
            language=request_data.get("language", "en"),
            provider=request_data.get("provider", "google"),
            model=request_data.get("model"),
            file_path=request_data.get("filePath"),
            excluded_dirs=request_data.get("excluded_dirs"),
            excluded_files=request_data.get("excluded_files"),
            included_dirs=request_data.get("included_dirs"),
            included_files=request_data.get("included_files")
        )
        
        # Convert messages to the expected format
        messages = request_data.get("messages", [])
        if messages:
            # Convert Pydantic models to dictionaries if needed
            converted_messages = []
            for msg in messages:
                if hasattr(msg, 'dict'):
                    converted_messages.append(msg.dict())
                elif hasattr(msg, '__dict__'):
                    converted_messages.append(msg.__dict__)
                else:
                    converted_messages.append(msg)
            context.messages = converted_messages
        
        self.logger.info("Chat pipeline context created successfully")
        return context
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get the current status of the pipeline."""
        if not self.context:
            return {"status": "not_initialized"}
        
        return {
            "pipeline_name": self.name,
            "steps_count": len(self.steps),
            "context_status": self.context.get_status_summary()
        }
    
    def validate_pipeline(self) -> bool:
        """Validate that the pipeline is properly configured."""
        if not super().validate_pipeline():
            return False
        
        # Check that we have the required steps
        required_step_types = [
            RequestValidationStep,
            ConversationAnalysisStep,
            SystemPromptGenerationStep,
            ContextPreparationStep,
            PromptAssemblyStep,
            ResponseGenerationStep
        ]
        
        step_types = [type(step) for step in self.steps]
        for required_type in required_step_types:
            if required_type not in step_types:
                self.logger.error(f"Missing required step type: {required_type.__name__}")
                return False
        
        self.logger.info("Chat pipeline validation passed")
        return True


# Factory function for creating chat pipeline instances
def create_chat_pipeline() -> ChatPipeline:
    """Create and return a new chat pipeline instance."""
    pipeline = ChatPipeline()
    if pipeline.validate_pipeline():
        return pipeline
    else:
        raise ValueError("Chat pipeline validation failed")
