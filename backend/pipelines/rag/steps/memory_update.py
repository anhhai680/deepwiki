"""
Memory Update Step for RAG Pipeline.

This step handles updating the conversation memory with the new
query and response for future context.
"""

import logging
import time
from typing import Any, Dict

from backend.pipelines.base import PipelineStep, PipelineContext
from backend.pipelines.rag.rag_context import RAGPipelineContext
from backend.components.memory.conversation_memory import ConversationMemory

logger = logging.getLogger(__name__)

class MemoryUpdateStep(PipelineStep[Dict[str, str], Dict[str, str]]):
    """Pipeline step for updating conversation memory."""
    
    def __init__(self):
        super().__init__("memory_update")
        self.memory = ConversationMemory()
    
    def execute(self, input_data: Dict[str, str], context: PipelineContext) -> Dict[str, str]:
        """Execute the memory update step."""
        if not isinstance(context, RAGPipelineContext):
            raise ValueError("Context must be RAGPipelineContext")
        
        rag_context = context
        rag_context.set_step(self.name, 4)
        start_time = time.time()
        
        try:
            self.logger.info("Updating conversation memory")
            
            # Validate input data
            if not self._validate_response_data(input_data):
                raise ValueError("Invalid response data for memory update")
            
            # Update conversation memory
            self._update_memory(input_data, rag_context)
            
            # Update context with conversation history
            self._update_context_history(rag_context)
            
            # Record timing
            duration = time.time() - start_time
            rag_context.add_step_timing(self.name, duration)
            
            self.logger.info(f"Memory update completed in {duration:.2f}s")
            return input_data
            
        except Exception as e:
            duration = time.time() - start_time
            rag_context.add_step_timing(self.name, duration)
            rag_context.add_error(f"Memory update failed: {str(e)}")
            self.logger.error(f"Memory update failed: {str(e)}")
            raise
    
    def validate_input(self, input_data: Dict[str, str]) -> bool:
        """Validate that input is a dictionary with answer and rationale."""
        return (
            isinstance(input_data, dict) and
            "answer" in input_data and
            "rationale" in input_data
        )
    
    def validate_output(self, output_data: Dict[str, str]) -> bool:
        """Validate that output is a dictionary with answer and rationale."""
        return (
            isinstance(output_data, dict) and
            "answer" in output_data and
            "rationale" in output_data
        )
    
    def _validate_response_data(self, response_data: Dict[str, str]) -> bool:
        """Validate the response data structure."""
        required_fields = ["answer", "rationale"]
        
        for field in required_fields:
            if field not in response_data:
                self.logger.error(f"Missing required field: {field}")
                return False
            
            if not isinstance(response_data[field], str):
                self.logger.error(f"Field {field} must be a string")
                return False
            
            if not response_data[field].strip():
                self.logger.error(f"Field {field} cannot be empty")
                return False
        
        return True
    
    def _update_memory(self, response_data: Dict[str, str], context: RAGPipelineContext) -> None:
        """
        Update the conversation memory with the new query and response.
        
        Args:
            response_data: Dictionary containing the generated answer and rationale
            context: RAG pipeline context
        """
        try:
            # Add the dialog turn to memory
            success = self.memory.add_dialog_turn(
                user_query=context.user_query,
                assistant_response=response_data["answer"]
            )
            
            if success:
                context.logger.info("Successfully added dialog turn to memory")
            else:
                context.add_warning("Failed to add dialog turn to memory")
                
        except Exception as e:
            context.add_error(f"Failed to update memory: {str(e)}")
            raise
    
    def _update_context_history(self, context: RAGPipelineContext) -> None:
        """
        Update the context with the current conversation history.
        
        Args:
            context: RAG pipeline context
        """
        try:
            # Get the current conversation history from memory
            conversation_history = self.memory.call()
            
            # Update the context
            context.conversation_history = conversation_history
            
            context.logger.info(f"Updated context with {len(conversation_history)} conversation turns")
            
        except Exception as e:
            context.add_error(f"Failed to update context history: {str(e)}")
            raise
