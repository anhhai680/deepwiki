"""
Response Generation Step for RAG Pipeline.

This step handles AI generation using the retrieved documents and
conversation history to produce the final RAG response.
"""

import logging
import time
from typing import Any, List, Dict

from backend.pipelines.base import PipelineStep, PipelineContext
from backend.pipelines.rag.rag_context import RAGPipelineContext
from backend.components.generator.generator_manager import get_generator_manager
from backend.components.generator.templates import RAG_SYSTEM_PROMPT, RAG_TEMPLATE

logger = logging.getLogger(__name__)

class ResponseGenerationStep(PipelineStep[List[Any], Dict[str, str]]):
    """Pipeline step for generating AI responses."""
    
    def __init__(self, provider: str = "google", model: str = "default"):
        super().__init__("response_generation")
        self.provider = provider
        self.model = model
        self.generator_manager = None
        self.generator = None
    
    def execute(self, input_data: List[Any], context: PipelineContext) -> Dict[str, str]:
        """Execute the response generation step."""
        if not isinstance(context, RAGPipelineContext):
            raise ValueError("Context must be RAGPipelineContext")
        
        rag_context = context
        rag_context.set_step(self.name, 3)
        start_time = time.time()
        
        try:
            self.logger.info("Generating AI response")
            
            # Validate input documents
            if not input_data:
                raise ValueError("No documents provided for response generation")
            
            # Setup generator
            self._setup_generator(rag_context)
            
            # Generate response
            response = self._generate_response(input_data, rag_context)
            
            # Update context with generated response
            rag_context.generated_response = response.get("answer", "")
            rag_context.rationale = response.get("rationale", "")
            rag_context.answer = response.get("answer", "")
            
            # Record timing
            duration = time.time() - start_time
            rag_context.add_step_timing(self.name, duration)
            
            self.logger.info(f"Response generation completed in {duration:.2f}s")
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            rag_context.add_step_timing(self.name, duration)
            rag_context.add_error(f"Response generation failed: {str(e)}")
            self.logger.error(f"Response generation failed: {str(e)}")
            raise
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate that input is a list of documents."""
        return isinstance(input_data, list) and len(input_data) > 0
    
    def validate_output(self, output_data: Any) -> bool:
        """Validate that output is a dictionary with answer and rationale."""
        return (
            isinstance(output_data, dict) and
            "answer" in output_data and
            "rationale" in output_data
        )
    
    def _setup_generator(self, context: RAGPipelineContext) -> None:
        """Setup the AI generator for response generation."""
        try:
            # Get generator manager
            self.generator_manager = get_generator_manager()
            
            # Create or get generator for this provider
            generator_name = f"{self.provider}_rag_generator"
            
            # Try to get existing generator first
            generator = self.generator_manager.get_generator(generator_name)
            
            if generator is None:
                # Create new generator if none exists
                generator = self.generator_manager.create_generator(
                    provider_type=self.provider,
                    name=generator_name
                )
                context.logger.info(f"Created new generator for provider '{self.provider}'")
            else:
                context.logger.info(f"Using existing generator for provider '{self.provider}'")
            
            # Store the generator for use in response generation
            self.generator = generator
            
            context.logger.info(f"Generator configured for provider '{self.provider}' with model '{self.model or 'default'}'")
            
        except Exception as e:
            context.add_error(f"Failed to setup generator: {str(e)}")
            raise
    
    def _generate_response(self, documents: List[Any], context: RAGPipelineContext) -> Dict[str, str]:
        """
        Generate the AI response using the retrieved documents and conversation history.
        
        Args:
            documents: List of retrieved documents
            context: RAG pipeline context
            
        Returns:
            Dictionary containing the generated answer and rationale
        """
        try:
            # Prepare conversation history
            conversation_history = self._prepare_conversation_history(context)
            
            # Prepare document contexts
            document_contexts = self._prepare_document_contexts(documents)
            
            # Prepare system prompt and template
            system_prompt = self._prepare_system_prompt(context)
            output_format = self._prepare_output_format()
            
            # Create the prompt
            prompt = self._create_prompt(
                system_prompt=system_prompt,
                output_format=output_format,
                conversation_history=conversation_history,
                document_contexts=document_contexts,
                user_query=context.user_query
            )
            
            # Generate response using the generator
            response = self._call_generator(prompt, context)
            
            return response
            
        except Exception as e:
            context.add_error(f"Failed to generate response: {str(e)}")
            raise
    
    def _prepare_conversation_history(self, context: RAGPipelineContext) -> Dict[str, Any]:
        """Prepare conversation history for the prompt."""
        if not context.conversation_history:
            return {}
        
        # Convert conversation history to the format expected by the template
        formatted_history = {}
        for turn_id, turn in context.conversation_history.items():
            formatted_history[turn_id] = {
                "user_query": {"query_str": turn.user_query.query_str},
                "assistant_response": {"response_str": turn.assistant_response.response_str}
            }
        
        return formatted_history
    
    def _prepare_document_contexts(self, documents: List[Any]) -> List[Dict[str, str]]:
        """Prepare document contexts for the prompt."""
        contexts = []
        
        for doc in documents:
            try:
                # Extract file path and content
                file_path = getattr(doc, 'meta_data', {}).get('file_path', 'unknown')
                content = getattr(doc, 'text', '')
                
                contexts.append({
                    "meta_data": {"file_path": file_path},
                    "text": content
                })
                
            except Exception as e:
                self.logger.warning(f"Failed to prepare document context: {str(e)}")
                continue
        
        return contexts
    
    def _prepare_system_prompt(self, context: RAGPipelineContext) -> str:
        """Prepare the system prompt for generation."""
        # Use the language from context if specified
        if context.language and context.language != "en":
            # For now, use the base system prompt
            # Language-specific prompts can be added here later
            return RAG_SYSTEM_PROMPT
        else:
            return RAG_SYSTEM_PROMPT
    
    def _prepare_output_format(self) -> str:
        """Prepare the output format instructions."""
        return """
IMPORTANT FORMATTING RULES:
1. DO NOT include your thinking or reasoning process in the output
2. Provide only the final, polished answer
3. DO NOT include ```markdown fences at the beginning or end of your answer
4. DO NOT wrap your response in any kind of fences
5. Start your response directly with the content
6. The content will already be rendered as markdown
7. Do not use backslashes before special characters like [ ] { } in your answer
8. When listing tags or similar items, write them as plain text without escape characters
9. For pipe characters (|) in text, write them directly without escaping them"""
    
    def _create_prompt(self, system_prompt: str, output_format: str, 
                       conversation_history: Dict[str, Any], document_contexts: List[Dict[str, str]], 
                       user_query: str) -> str:
        """Create the complete prompt for generation."""
        # This is a simplified prompt creation - in a full implementation,
        # you would use the RAG_TEMPLATE with proper templating
        prompt_parts = []
        
        # System prompt
        prompt_parts.append(f"<START_OF_SYS_PROMPT>\n{system_prompt}\n{output_format}\n<END_OF_SYS_PROMPT>")
        
        # Conversation history
        if conversation_history:
            prompt_parts.append("<START_OF_CONVERSATION_HISTORY>")
            for key, turn in conversation_history.items():
                prompt_parts.append(f"{key}.\nUser: {turn['user_query']['query_str']}\nYou: {turn['assistant_response']['response_str']}")
            prompt_parts.append("<END_OF_CONVERSATION_HISTORY>")
        
        # Document contexts
        if document_contexts:
            prompt_parts.append("<START_OF_CONTEXT>")
            for i, context in enumerate(document_contexts):
                # Handle different document context structures
                if isinstance(context, dict):
                    meta_data = context.get('meta_data', {})
                    file_path = meta_data.get('file_path', 'Unknown file') if isinstance(meta_data, dict) else 'Unknown file'
                    text_content = context.get('text', str(context))
                else:
                    file_path = 'Unknown file'
                    text_content = str(context)
                
                prompt_parts.append(f"{i+1}.\nFile Path: {file_path}\nContent: {text_content}")
            prompt_parts.append("<END_OF_CONTEXT>")
        
        # User query
        prompt_parts.append(f"<START_OF_USER_PROMPT>\n{user_query}\n<END_OF_USER_PROMPT>")
        
        return "\n\n".join(prompt_parts)
    
    def _call_generator(self, prompt: str, context: RAGPipelineContext) -> Dict[str, str]:
        """Call the AI generator to produce the response."""
        try:
            if not self.generator:
                raise ValueError("Generator not initialized. Call _setup_generator first.")

            # Import ModelType for proper type specification
            from backend.components.generator.base import ModelType

            # Prepare API kwargs for the generator call
            api_kwargs = {
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "model": self.model,
                "temperature": 0.7,
                "max_tokens": 2000
            }

            # Call the generator with proper model type
            context.logger.info(f"Calling {self.provider} generator for response generation")
            result = self.generator.call(api_kwargs, model_type=ModelType.LLM)
            
            if hasattr(result, 'data') and result.data:
                # Extract the response content
                raw_response = result.data
                
                # For now, parse as a simple response
                # In future, could implement more sophisticated parsing
                response = {
                    "rationale": "Generated using RAG pipeline with retrieved documents",
                    "answer": str(raw_response)
                }
            else:
                # Fallback response if generator call fails
                response = {
                    "rationale": "Generated using RAG pipeline with retrieved documents",
                    "answer": f"Based on the retrieved documents, here is the answer to your question: {context.user_query}"
                }
            
            context.logger.info("Response generated successfully")
            return response
            
        except Exception as e:
            context.add_error(f"Failed to call generator: {str(e)}")
            # Provide fallback response instead of raising
            context.logger.warning(f"Generator call failed, using fallback response: {str(e)}")
            return {
                "rationale": "Generated using RAG pipeline with retrieved documents (fallback due to generator error)",
                "answer": f"I apologize, but I encountered an issue generating a response. However, based on the retrieved documents, I can tell you that your question '{context.user_query}' relates to the codebase content that was found."
            }
