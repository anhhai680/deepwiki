"""
Base pipeline framework for DeepWiki.

This module provides the foundational pipeline architecture that all
specific pipeline implementations should inherit from.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Type variable for pipeline input/output
InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')
ContextType = TypeVar('ContextType')

@dataclass
class PipelineContext:
    """Base context class for pipeline execution."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def update(self, **kwargs):
        """Update context with new values."""
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from context with optional default."""
        return getattr(self, key, default)
    
    def has(self, key: str) -> bool:
        """Check if a key exists in context."""
        return hasattr(self, key)

class PipelineStep(ABC, Generic[InputType, OutputType]):
    """Abstract base class for pipeline steps."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def execute(self, input_data: InputType, context: PipelineContext) -> OutputType:
        """Execute this pipeline step."""
        pass
    
    def validate_input(self, input_data: InputType) -> bool:
        """Validate input data for this step. Override if needed."""
        return True
    
    def validate_output(self, output_data: OutputType) -> bool:
        """Validate output data for this step. Override if needed."""
        return True

class BasePipeline(ABC, Generic[InputType, OutputType, ContextType]):
    """Abstract base class for all pipelines."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.steps: list[PipelineStep] = []
        self.context: Optional[ContextType] = None
    
    def add_step(self, step: PipelineStep) -> 'BasePipeline':
        """Add a step to the pipeline."""
        self.steps.append(step)
        self.logger.debug(f"Added step '{step.name}' to pipeline '{self.name}'")
        return self
    
    def add_steps(self, *steps: PipelineStep) -> 'BasePipeline':
        """Add multiple steps to the pipeline."""
        for step in steps:
            self.add_step(step)
        return self
    
    def set_context(self, context: ContextType) -> 'BasePipeline':
        """Set the pipeline context."""
        self.context = context
        return self
    
    def get_context(self) -> Optional[ContextType]:
        """Get the current pipeline context."""
        return self.context
    
    @abstractmethod
    def execute(self, input_data: InputType) -> OutputType:
        """Execute the pipeline with the given input."""
        pass
    
    def validate_pipeline(self) -> bool:
        """Validate that the pipeline is properly configured."""
        if not self.steps:
            self.logger.error(f"Pipeline '{self.name}' has no steps")
            return False
        return True
    
    def get_step_names(self) -> list[str]:
        """Get the names of all steps in the pipeline."""
        return [step.name for step in self.steps]
    
    def get_step_by_name(self, name: str) -> Optional[PipelineStep]:
        """Get a step by name."""
        for step in self.steps:
            if step.name == name:
                return step
        return None

class SequentialPipeline(BasePipeline[InputType, OutputType, ContextType]):
    """Pipeline that executes steps sequentially."""
    
    def execute(self, input_data: InputType) -> OutputType:
        """Execute all pipeline steps sequentially."""
        if not self.validate_pipeline():
            raise ValueError(f"Pipeline '{self.name}' is not properly configured")
        
        self.logger.info(f"Starting execution of pipeline '{self.name}' with {len(self.steps)} steps")
        
        current_input = input_data
        
        for i, step in enumerate(self.steps):
            try:
                self.logger.debug(f"Executing step {i+1}/{len(self.steps)}: '{step.name}'")
                
                # Validate input
                if not step.validate_input(current_input):
                    raise ValueError(f"Input validation failed for step '{step.name}'")
                
                # Execute step
                step_output = step.execute(current_input, self.context)
                
                # Validate output
                if not step.validate_output(step_output):
                    raise ValueError(f"Output validation failed for step '{step.name}'")
                
                # Update input for next step
                current_input = step_output
                
                self.logger.debug(f"Step '{step.name}' completed successfully")
                
            except Exception as e:
                self.logger.error(f"Step '{step.name}' failed: {str(e)}")
                raise
        
        self.logger.info(f"Pipeline '{self.name}' completed successfully")
        return current_input

class ParallelPipeline(BasePipeline[InputType, OutputType, ContextType]):
    """Pipeline that executes steps in parallel where possible."""
    
    def execute(self, input_data: InputType) -> OutputType:
        """Execute pipeline steps in parallel where possible."""
        if not self.validate_pipeline():
            raise ValueError(f"Pipeline '{self.name}' is not properly configured")
        
        self.logger.info(f"Starting parallel execution of pipeline '{self.name}' with {len(self.steps)} steps")
        
        # For now, implement as sequential - parallel execution can be added later
        # when we have steps that can truly run in parallel
        return SequentialPipeline(self.name).add_steps(*self.steps).execute(input_data)
