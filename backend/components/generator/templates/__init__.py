"""
Prompt template management package.

This package contains prompt templates and template management
for different types of AI interactions.
"""

from .templates import (
    RAG_SYSTEM_PROMPT,
    RAG_TEMPLATE,
    DEEP_RESEARCH_FIRST_ITERATION_PROMPT,
    DEEP_RESEARCH_FINAL_ITERATION_PROMPT,
    DEEP_RESEARCH_INTERMEDIATE_ITERATION_PROMPT,
    SIMPLE_CHAT_SYSTEM_PROMPT,
)

__all__ = [
    "RAG_SYSTEM_PROMPT",
    "RAG_TEMPLATE",
    "DEEP_RESEARCH_FIRST_ITERATION_PROMPT",
    "DEEP_RESEARCH_FINAL_ITERATION_PROMPT",
    "DEEP_RESEARCH_INTERMEDIATE_ITERATION_PROMPT",
    "SIMPLE_CHAT_SYSTEM_PROMPT",
]
