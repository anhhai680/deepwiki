"""
Base pipeline framework providing reusable infrastructure for all pipeline implementations.

This module defines the core abstractions for building modular, composable pipelines
that can orchestrate complex workflows while maintaining clean separation of concerns.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypeVar, Generic
from uuid import uuid4

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class PipelineContext:
    """
    Context object that flows through pipeline stages, carrying data and metadata.
    
    This provides a standardized way to pass information between pipeline components
    while maintaining traceability and state management.
    """
    
    # Unique identifier for this pipeline execution
    execution_id: str = field(default_factory=lambda: str(uuid4()))
    
    # Input data for the pipeline
    input_data: Any = None
    
    # Output data from the pipeline
    output_data: Any = None
    
    # Intermediate results from each stage
    stage_results: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata about the execution
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Error information if any stage fails
    errors: List[str] = field(default_factory=list)
    
    # Whether the pipeline execution was successful
    success: bool = True
    
    def add_stage_result(self, stage_name: str, result: Any) -> None:
        """Add result from a pipeline stage."""
        self.stage_results[stage_name] = result
        logger.debug(f"Added stage result for '{stage_name}' in execution {self.execution_id}")
    
    def get_stage_result(self, stage_name: str) -> Any:
        """Get result from a specific pipeline stage."""
        return self.stage_results.get(stage_name)
    
    def add_error(self, error: str, stage_name: str = None) -> None:
        """Add an error to the context."""
        error_msg = f"[{stage_name}] {error}" if stage_name else error
        self.errors.append(error_msg)
        self.success = False
        logger.error(f"Pipeline error in execution {self.execution_id}: {error_msg}")
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the context."""
        self.metadata[key] = value


class PipelineStage(ABC, Generic[T]):
    """
    Abstract base class for pipeline stages.
    
    Each stage represents a discrete unit of work that can process the pipeline context
    and potentially transform its data or add intermediate results.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        """
        Execute this pipeline stage.
        
        Args:
            context: The pipeline context containing input data and intermediate results
            
        Returns:
            Updated pipeline context with results from this stage
        """
        pass
    
    def _validate_input(self, context: PipelineContext) -> bool:
        """
        Validate that the context contains required input for this stage.
        Override in subclasses for stage-specific validation.
        """
        return True
    
    def _handle_error(self, context: PipelineContext, error: Exception) -> PipelineContext:
        """Handle errors that occur during stage execution."""
        error_msg = f"Error in stage '{self.name}': {str(error)}"
        context.add_error(error_msg, self.name)
        self.logger.error(error_msg, exc_info=True)
        return context


class BasePipeline(ABC):
    """
    Base class for all pipeline implementations.
    
    Provides the core orchestration logic for executing a sequence of pipeline stages
    while maintaining proper error handling, logging, and context management.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.stages: List[PipelineStage] = []
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def add_stage(self, stage: PipelineStage) -> None:
        """Add a stage to the pipeline."""
        self.stages.append(stage)
        self.logger.debug(f"Added stage '{stage.name}' to pipeline '{self.name}'")
    
    def execute(self, input_data: Any, **kwargs) -> PipelineContext:
        """
        Execute the complete pipeline with the given input data.
        
        Args:
            input_data: Input data for the pipeline
            **kwargs: Additional parameters to pass to the pipeline context
            
        Returns:
            PipelineContext containing the results and execution metadata
        """
        # Create pipeline context
        context = PipelineContext(
            input_data=input_data,
            metadata=kwargs
        )
        
        self.logger.info(f"Starting pipeline '{self.name}' execution {context.execution_id}")
        
        try:
            # Execute pre-processing
            context = self._pre_process(context)
            
            # Execute each stage in sequence
            for stage in self.stages:
                if not context.success:
                    self.logger.warning(f"Skipping stage '{stage.name}' due to previous errors")
                    break
                
                self.logger.debug(f"Executing stage '{stage.name}'")
                context = stage.execute(context)
            
            # Execute post-processing
            context = self._post_process(context)
            
            if context.success:
                self.logger.info(f"Pipeline '{self.name}' completed successfully")
            else:
                self.logger.error(f"Pipeline '{self.name}' completed with errors: {context.errors}")
        
        except Exception as e:
            error_msg = f"Unexpected error in pipeline '{self.name}': {str(e)}"
            context.add_error(error_msg)
            self.logger.error(error_msg, exc_info=True)
        
        return context
    
    def _pre_process(self, context: PipelineContext) -> PipelineContext:
        """
        Pre-processing hook called before executing stages.
        Override in subclasses for pipeline-specific setup.
        """
        return context
    
    def _post_process(self, context: PipelineContext) -> PipelineContext:
        """
        Post-processing hook called after executing all stages.
        Override in subclasses for pipeline-specific cleanup or result processing.
        """
        return context
    
    @abstractmethod
    def _configure_stages(self) -> None:
        """
        Configure the pipeline stages.
        This method should be implemented by subclasses to define their specific stages.
        """
        pass


class ValidationStage(PipelineStage):
    """A reusable validation stage that can be used in any pipeline."""
    
    def __init__(self, name: str = "validation", validation_func: callable = None):
        super().__init__(name)
        self.validation_func = validation_func or self._default_validation
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute validation."""
        try:
            if not self.validation_func(context):
                context.add_error("Validation failed", self.name)
            else:
                context.add_stage_result(self.name, "validation_passed")
        except Exception as e:
            context = self._handle_error(context, e)
        
        return context
    
    def _default_validation(self, context: PipelineContext) -> bool:
        """Default validation - just check that input_data exists."""
        return context.input_data is not None


class LoggingStage(PipelineStage):
    """A reusable logging stage for debugging and monitoring."""
    
    def __init__(self, name: str = "logging", log_level: str = "INFO"):
        super().__init__(name)
        self.log_level = getattr(logging, log_level.upper())
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Log pipeline state."""
        self.logger.log(
            self.log_level,
            f"Pipeline state - Execution: {context.execution_id}, "
            f"Success: {context.success}, "
            f"Stages completed: {len(context.stage_results)}, "
            f"Errors: {len(context.errors)}"
        )
        return context