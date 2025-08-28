"""
Chat pipeline package.

This package contains the chat workflow orchestration
and conversation management pipelines.
"""

from .chat_pipeline import ChatPipeline, create_chat_pipeline
from .chat_context import ChatPipelineContext
from .compatibility import ChatCompatibility, get_chat_compatibility, create_chat_completion_stream, create_chat_pipeline_instance
from .steps import (
    RequestValidationStep,
    ConversationAnalysisStep,
    SystemPromptGenerationStep,
    ContextPreparationStep,
    PromptAssemblyStep
)
from .response_generation import ResponseGenerationStep

__all__ = [
    "ChatPipeline",
    "create_chat_pipeline",
    "ChatPipelineContext",
    "ChatCompatibility",
    "get_chat_compatibility",
    "create_chat_completion_stream",
    "create_chat_pipeline_instance",
    "RequestValidationStep",
    "ConversationAnalysisStep",
    "SystemPromptGenerationStep",
    "ContextPreparationStep",
    "PromptAssemblyStep",
    "ResponseGenerationStep"
]
