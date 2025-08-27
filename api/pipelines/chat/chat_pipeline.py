"""
Chat Pipeline implementation for direct conversational interactions.

This pipeline handles simple chat interactions without document retrieval,
providing a streamlined conversation flow for general queries.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import adalflow as adal

from ..base.base_pipeline import BasePipeline, PipelineStage, PipelineContext
from api.prompts import RAG_SYSTEM_PROMPT as system_prompt
from api.config import get_model_config

logger = logging.getLogger(__name__)


@dataclass
class ChatInput:
    """Input data structure for chat pipeline."""
    query: str
    language: str = "en"
    conversation_history: Optional[List[Dict[str, str]]] = None


@dataclass
class ChatOutput:
    """Output data structure for chat pipeline."""
    response: str
    conversation_history: List[Dict[str, str]]
    execution_metadata: Dict[str, Any]


class ConversationManagementStage(PipelineStage):
    """Stage responsible for managing conversation history."""
    
    def __init__(self):
        super().__init__("conversation_management")
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Manage conversation history."""
        try:
            chat_input: ChatInput = context.input_data
            
            # Initialize or update conversation history
            history = chat_input.conversation_history or []
            
            # Add current query to history
            history.append({
                "role": "user",
                "content": chat_input.query
            })
            
            context.add_stage_result("conversation_history", history)
            context.add_metadata("history_length", len(history))
            
            self.logger.debug(f"Conversation history updated with {len(history)} messages")
            
        except Exception as e:
            context = self._handle_error(context, e)
        
        return context


class ChatResponseGenerationStage(PipelineStage):
    """Stage responsible for generating chat responses."""
    
    def __init__(self, provider: str, model: str):
        super().__init__("chat_response_generation")
        self.provider = provider
        self.model = model
        self._setup_generator()
    
    def _setup_generator(self):
        """Set up the chat response generator."""
        # Simple template for chat responses
        chat_template = """
{{system_prompt}}

{% if conversation_history %}
Previous conversation:
{% for message in conversation_history %}
{{message.role}}: {{message.content}}
{% endfor %}
{% endif %}

Current query: {{query}}
Language: {{language}}

Please provide a helpful response in the specified language.
"""
        
        # Get model configuration
        generator_config = get_model_config(self.provider, self.model)
        
        # Set up the generator
        self.generator = adal.Generator(
            template=chat_template,
            prompt_kwargs={
                "system_prompt": system_prompt,
                "conversation_history": [],
                "query": "",
                "language": "en"
            },
            model_client=generator_config["model_client"](),
            model_kwargs=generator_config["model_kwargs"],
        )
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Generate chat response."""
        try:
            chat_input: ChatInput = context.input_data
            conversation_history = context.get_stage_result("conversation_history")
            
            # Update generator with current context
            self.generator.prompt_kwargs.update({
                "conversation_history": conversation_history[:-1],  # Exclude current query
                "query": chat_input.query,
                "language": chat_input.language
            })
            
            # Generate response
            self.logger.debug("Generating chat response...")
            response = self.generator()
            
            # Extract response text
            if hasattr(response, 'data'):
                response_text = response.data
            elif isinstance(response, str):
                response_text = response
            else:
                response_text = str(response)
            
            context.add_stage_result("chat_response", response_text)
            context.add_metadata("language", chat_input.language)
            
            self.logger.info("Chat response generation completed successfully")
            
        except Exception as e:
            context = self._handle_error(context, e)
            # Create error response
            context.add_stage_result("chat_response", 
                "I apologize, but I encountered an error while processing your message. Please try again.")
        
        return context


class ChatPipeline(BasePipeline):
    """
    Chat Pipeline for direct conversational interactions.
    
    This pipeline provides a streamlined conversation flow without document retrieval,
    suitable for general queries and simple interactions.
    """
    
    def __init__(self, provider: str = "google", model: str = None):
        super().__init__("chat_pipeline")
        
        self.provider = provider
        self.model = model
        
        # Configure pipeline stages
        self._configure_stages()
    
    def _configure_stages(self) -> None:
        """Configure the chat pipeline stages."""
        # Add conversation management stage
        self.add_stage(ConversationManagementStage())
        
        # Add response generation stage
        self.add_stage(ChatResponseGenerationStage(
            provider=self.provider,
            model=self.model
        ))
    
    def chat(self, query: str, language: str = "en", 
             conversation_history: List[Dict[str, str]] = None) -> ChatOutput:
        """
        Process a chat query.
        
        Args:
            query: The user's query
            language: Language for the response
            conversation_history: Previous conversation history
            
        Returns:
            ChatOutput containing the response and updated conversation history
        """
        # Create input for the pipeline
        chat_input = ChatInput(
            query=query,
            language=language,
            conversation_history=conversation_history
        )
        
        # Execute the pipeline
        context = self.execute(chat_input)
        
        if context.success:
            # Extract results
            response = context.get_stage_result("chat_response")
            history = context.get_stage_result("conversation_history")
            
            # Add assistant response to history
            history.append({
                "role": "assistant",
                "content": response
            })
            
            return ChatOutput(
                response=response,
                conversation_history=history,
                execution_metadata=context.metadata
            )
        else:
            # Return error response
            return ChatOutput(
                response="I apologize, but I encountered an error while processing your message.",
                conversation_history=conversation_history or [],
                execution_metadata={"errors": context.errors}
            )
    
    def _post_process(self, context: PipelineContext) -> PipelineContext:
        """Post-process the chat results."""
        if context.success:
            # Create final output structure
            response = context.get_stage_result("chat_response")
            history = context.get_stage_result("conversation_history")
            
            # Add assistant response to history
            if response and history:
                history.append({
                    "role": "assistant",
                    "content": response
                })
            
            output = ChatOutput(
                response=response,
                conversation_history=history or [],
                execution_metadata=context.metadata
            )
            
            context.output_data = output
        
        return context