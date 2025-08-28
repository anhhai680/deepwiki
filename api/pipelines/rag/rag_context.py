"""
RAG Pipeline Context Management.

This module provides the context management system for the RAG pipeline,
handling data flow and state management between pipeline steps.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from uuid import uuid4

from api.pipelines.base import PipelineContext
from api.components.retriever.base import RetrievalResult
from api.components.memory.conversation_memory import DialogTurn

logger = logging.getLogger(__name__)

@dataclass
class RAGPipelineContext(PipelineContext):
    """Context for RAG pipeline execution."""
    
    # Pipeline state
    pipeline_id: str = field(default_factory=lambda: str(uuid4()))
    step_name: str = ""
    step_index: int = 0
    
    # Repository information
    repo_url_or_path: str = ""
    repo_type: str = "github"
    access_token: Optional[str] = None
    excluded_dirs: List[str] = field(default_factory=list)
    excluded_files: List[str] = field(default_factory=list)
    included_dirs: List[str] = field(default_factory=list)
    included_files: List[str] = field(default_factory=list)
    
    # Document and embedding state
    transformed_docs: List[Any] = field(default_factory=list)
    is_ollama_embedder: bool = False
    
    # Query processing state
    user_query: str = ""
    language: str = "en"
    retrieved_documents: Optional[RetrievalResult] = None
    conversation_history: Dict[str, DialogTurn] = field(default_factory=dict)
    
    # Generation state
    system_prompt: str = ""
    output_format_str: str = ""
    generated_response: Optional[str] = None
    rationale: str = ""
    answer: str = ""
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Performance metrics
    start_time: Optional[float] = None
    step_timings: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the context after creation."""
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}.{self.pipeline_id}")
    
    def add_error(self, error: str) -> None:
        """Add an error to the context."""
        self.errors.append(error)
        self.logger.error(f"Pipeline error: {error}")
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the context."""
        self.warnings.append(warning)
        self.logger.warning(f"Pipeline warning: {warning}")
    
    def has_errors(self) -> bool:
        """Check if the context has any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if the context has any warnings."""
        return len(self.warnings) > 0
    
    def get_last_error(self) -> Optional[str]:
        """Get the last error from the context."""
        return self.errors[-1] if self.errors else None
    
    def get_last_warning(self) -> Optional[str]:
        """Get the last warning from the context."""
        return self.warnings[-1] if self.warnings else None
    
    def clear_errors(self) -> None:
        """Clear all errors from the context."""
        self.errors.clear()
    
    def clear_warnings(self) -> None:
        """Clear all warnings from the context."""
        self.warnings.clear()
    
    def set_step(self, step_name: str, step_index: int) -> None:
        """Set the current pipeline step."""
        self.step_name = step_name
        self.step_index = step_index
        self.logger.debug(f"Pipeline step: {step_name} ({step_index})")
    
    def add_step_timing(self, step_name: str, duration: float) -> None:
        """Add timing information for a pipeline step."""
        self.step_timings[step_name] = duration
    
    def get_total_duration(self) -> float:
        """Get the total pipeline duration."""
        if not self.step_timings:
            return 0.0
        return sum(self.step_timings.values())
    
    def get_step_duration(self, step_name: str) -> float:
        """Get the duration of a specific step."""
        return self.step_timings.get(step_name, 0.0)
    
    def validate_repository_config(self) -> bool:
        """Validate that repository configuration is complete."""
        if not self.repo_url_or_path:
            self.add_error("Repository URL or path is required")
            return False
        
        if self.repo_type not in ["github", "gitlab", "bitbucket", "local"]:
            self.add_error(f"Unsupported repository type: {self.repo_type}")
            return False
        
        return True
    
    def validate_query_config(self) -> bool:
        """Validate that query configuration is complete."""
        if not self.user_query:
            self.add_error("User query is required")
            return False
        
        if not self.language:
            self.add_error("Language is required")
            return False
        
        return True
    
    def validate_documents(self) -> bool:
        """Validate that documents are available."""
        if not self.transformed_docs:
            self.add_error("No transformed documents available")
            return False
        
        return True
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current context state."""
        return {
            "pipeline_id": self.pipeline_id,
            "step": f"{self.step_name} ({self.step_index})",
            "repository": self.repo_url_or_path,
            "query": self.user_query[:100] + "..." if len(self.user_query) > 100 else self.user_query,
            "documents_count": len(self.transformed_docs),
            "conversation_turns": len(self.conversation_history),
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "total_duration": self.get_total_duration()
        }
    
    def log_context_summary(self) -> None:
        """Log a summary of the current context state."""
        summary = self.get_context_summary()
        self.logger.info(f"Context summary: {summary}")
    
    def reset_for_new_query(self) -> None:
        """Reset context for a new query while preserving repository state."""
        # Preserve repository and document state
        repo_state = {
            "repo_url_or_path": self.repo_url_or_path,
            "repo_type": self.repo_type,
            "access_token": self.access_token,
            "excluded_dirs": self.excluded_dirs,
            "excluded_files": self.excluded_files,
            "included_dirs": self.included_dirs,
            "included_files": self.included_files,
            "transformed_docs": self.transformed_docs,
            "is_ollama_embedder": self.is_ollama_embedder
        }
        
        # Reset query-specific state
        self.__init__(**repo_state)
        
        # Restore repository state
        for key, value in repo_state.items():
            setattr(self, key, value)
        
        self.logger.info("Context reset for new query")
    
    def clone(self) -> 'RAGPipelineContext':
        """Create a clone of this context."""
        return RAGPipelineContext(
            pipeline_id=str(uuid4()),
            repo_url_or_path=self.repo_url_or_path,
            repo_type=self.repo_type,
            access_token=self.access_token,
            excluded_dirs=self.excluded_dirs.copy(),
            excluded_files=self.excluded_files.copy(),
            included_dirs=self.included_dirs.copy(),
            included_files=self.included_files.copy(),
            transformed_docs=self.transformed_docs.copy(),
            is_ollama_embedder=self.is_ollama_embedder,
            system_prompt=self.system_prompt,
            output_format_str=self.output_format_str
        )
