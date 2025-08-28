"""
Main RAG Pipeline Implementation.

This module provides the main RAG pipeline that orchestrates all the
individual steps including repository preparation, retrieval, generation,
and memory management.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from backend.pipelines.base import SequentialPipeline
from backend.pipelines.rag.rag_context import RAGPipelineContext
from backend.pipelines.rag.steps import (
    RepositoryPreparationStep,
    RetrieverInitializationStep,
    DocumentRetrievalStep,
    ResponseGenerationStep,
    MemoryUpdateStep
)

logger = logging.getLogger(__name__)

class RAGPipeline(SequentialPipeline[str, Dict[str, str], RAGPipelineContext]):
    """
    Main RAG Pipeline for DeepWiki.
    
    This pipeline orchestrates the complete RAG workflow:
    1. Repository preparation and document loading
    2. Retriever initialization with FAISS
    3. Document retrieval based on user query
    4. AI response generation using retrieved documents
    5. Memory update for conversation history
    """
    
    def __init__(self, provider: str = "google", model: str = None):
        """Initialize the RAG pipeline with the specified AI provider and model."""
        super().__init__("rag_pipeline")
        
        self.provider = provider
        self.model = model
        
        # Initialize pipeline steps
        self._setup_pipeline_steps()
        
        # Initialize context
        self.context = RAGPipelineContext()
        
        logger.info(f"RAG Pipeline initialized with provider '{provider}' and model '{model}'")
    
    def _setup_pipeline_steps(self) -> None:
        """Setup the pipeline steps in the correct order."""
        # Step 1: Repository preparation
        self.add_step(RepositoryPreparationStep())
        
        # Step 2: Retriever initialization
        self.add_step(RetrieverInitializationStep())
        
        # Step 3: Document retrieval
        self.add_step(DocumentRetrievalStep())
        
        # Step 4: Response generation
        self.add_step(ResponseGenerationStep(self.provider, self.model))
        
        # Step 5: Memory update
        self.add_step(MemoryUpdateStep())
        
        logger.info(f"Pipeline configured with {len(self.steps)} steps: {self.get_step_names()}")
    
    def prepare_repository(self, repo_url_or_path: str, repo_type: str = "github", 
                          access_token: str = None, excluded_dirs: List[str] = None,
                          excluded_files: List[str] = None, included_dirs: List[str] = None,
                          included_files: List[str] = None) -> 'RAGPipeline':
        """
        Prepare the repository for RAG processing.
        
        Args:
            repo_url_or_path: URL or local path to the repository
            repo_type: Type of repository (github, gitlab, bitbucket, local)
            access_token: Optional access token for private repositories
            excluded_dirs: Optional list of directories to exclude
            excluded_files: Optional list of file patterns to exclude
            included_dirs: Optional list of directories to include exclusively
            included_files: Optional list of file patterns to include exclusively
            
        Returns:
            Self for method chaining
        """
        # Update context with repository information
        self.context.update(
            repo_url_or_path=repo_url_or_path,
            repo_type=repo_type,
            access_token=access_token,
            excluded_dirs=excluded_dirs or [],
            excluded_files=excluded_files or [],
            included_dirs=included_dirs or [],
            included_files=included_files or []
        )
        
        # Execute repository preparation step
        try:
            logger.info(f"Preparing repository: {repo_url_or_path}")
            documents = self.steps[0].execute(repo_url_or_path, self.context)
            
            # Update context with documents
            self.context.transformed_docs = documents
            
            logger.info(f"Repository prepared successfully with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Repository preparation failed: {str(e)}")
            raise
        
        return self
    
    def query(self, query: str, language: str = "en") -> Dict[str, str]:
        """
        Process a query using the RAG pipeline.
        
        Args:
            query: The user's query
            language: Language for the response (default: "en")
            
        Returns:
            Dictionary containing the generated answer and rationale
        """
        try:
            # Update context with query information
            self.context.update(
                user_query=query,
                language=language
            )
            
            logger.info(f"Processing query: {query[:100]}...")
            
            # Execute the pipeline
            start_time = time.time()
            result = self.execute(query)
            total_duration = time.time() - start_time
            
            # Log completion
            self.context.log_context_summary()
            logger.info(f"Query processing completed in {total_duration:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            
            # Return error response
            error_response = {
                "rationale": "Error occurred while processing the query.",
                "answer": f"I apologize, but I encountered an error while processing your question. Please try again or rephrase your question. Error: {str(e)}"
            }
            
            return error_response
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current pipeline context."""
        return self.context.get_context_summary()
    
    def reset_for_new_query(self) -> None:
        """Reset the pipeline context for a new query while preserving repository state."""
        self.context.reset_for_new_query()
        logger.info("Pipeline reset for new query")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get the current status of the pipeline."""
        return {
            "name": self.name,
            "provider": self.provider,
            "model": self.model,
            "steps": self.get_step_names(),
            "context": self.get_context_summary(),
            "has_errors": self.context.has_errors(),
            "has_warnings": self.context.has_warnings()
        }
    
    def clear_errors(self) -> None:
        """Clear all errors from the pipeline context."""
        self.context.clear_errors()
        logger.info("Pipeline errors cleared")
    
    def clear_warnings(self) -> None:
        """Clear all warnings from the pipeline context."""
        self.context.clear_warnings()
        logger.info("Pipeline warnings cleared")
    
    def validate_pipeline_state(self) -> bool:
        """Validate that the pipeline is in a valid state for processing."""
        # Check if repository is prepared
        if not self.context.transformed_docs:
            logger.error("Pipeline not ready: repository not prepared")
            return False
        
        # Check if pipeline has steps
        if not self.validate_pipeline():
            logger.error("Pipeline not ready: no steps configured")
            return False
        
        # Check for critical errors
        if self.context.has_errors():
            logger.error(f"Pipeline has errors: {self.context.get_last_error()}")
            return False
        
        logger.info("Pipeline state validation passed")
        return True
