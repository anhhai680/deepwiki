"""
Chat pipeline context for DeepWiki.

This module provides the context management system for chat operations,
including conversation state, user preferences, and processing metadata.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..base.base_pipeline import PipelineContext

logger = logging.getLogger(__name__)


@dataclass
class ChatPipelineContext(PipelineContext):
    """Context class for chat pipeline execution."""
    
    # Request data
    repo_url: str = ""
    repo_type: str = "github"
    token: Optional[str] = None
    language: str = "en"
    
    # File filtering
    excluded_dirs: Optional[List[str]] = None
    excluded_files: Optional[List[str]] = None
    included_dirs: Optional[List[str]] = None
    included_files: Optional[List[str]] = None
    file_path: Optional[str] = None
    
    # Model configuration
    provider: str = "ollama"  # Will be overridden by configuration
    model: Optional[str] = None
    model_config: Dict[str, Any] = field(default_factory=dict)
    
    # Conversation data
    messages: List[Dict[str, str]] = field(default_factory=list)
    conversation_history: str = ""
    is_deep_research: bool = False
    research_iteration: int = 1
    
    # Processing state
    input_too_large: bool = False
    context_text: str = ""
    retrieved_documents: Optional[Any] = None
    file_content: str = ""
    
    # System prompts
    system_prompt: str = ""
    final_prompt: str = ""
    
    # Performance tracking
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    processing_time: Optional[float] = None
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize context after creation."""
        self.start_time = datetime.now()
        self.logger = logging.getLogger(f"{__name__}.ChatPipelineContext")
    
    def add_error(self, error: str):
        """Add an error to the context."""
        self.errors.append(f"{datetime.now()}: {error}")
        self.logger.error(f"Chat pipeline error: {error}")
    
    def add_warning(self, warning: str):
        """Add a warning to the context."""
        self.warnings.append(f"{datetime.now()}: {warning}")
        self.logger.warning(f"Chat pipeline warning: {warning}")
    
    def mark_completed(self):
        """Mark the pipeline as completed and calculate processing time."""
        self.end_time = datetime.now()
        if self.start_time:
            self.processing_time = (self.end_time - self.start_time).total_seconds()
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of the pipeline status."""
        return {
            "status": "completed" if self.end_time else "running",
            "processing_time": self.processing_time,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "has_context": bool(self.context_text.strip()),
            "has_file_content": bool(self.file_content.strip()),
            "is_deep_research": self.is_deep_research,
            "research_iteration": self.research_iteration
        }
    
    def validate(self) -> bool:
        """Validate the context for pipeline execution."""
        if not self.repo_url or self.repo_url == "":
            self.add_error("Repository URL is required")
            return False
        
        if not self.messages or len(self.messages) == 0:
            self.add_error("At least one message is required")
            return False
        
        if not self.provider or self.provider == "":
            self.add_error("AI provider is required")
            return False
        
        return True
