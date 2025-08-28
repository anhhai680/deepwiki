"""
RAG Pipeline Compatibility Layer.

This module provides backward compatibility with the existing rag.py interface,
allowing existing code to work with the new pipeline architecture without changes.
"""

import logging
from typing import Any, List, Tuple, Optional

from api.pipelines.rag.rag_pipeline import RAGPipeline
from api.pipelines.rag.rag_context import RAGPipelineContext

logger = logging.getLogger(__name__)

class RAGCompatibility:
    """
    Compatibility wrapper for the RAG pipeline.
    
    This class provides the same interface as the original RAG class
    from rag.py, ensuring backward compatibility.
    """
    
    def __init__(self, provider: str = "google", model: str = None, use_s3: bool = False):
        """
        Initialize the RAG compatibility wrapper.
        
        Args:
            provider: Model provider to use (google, openai, openrouter, ollama)
            model: Model name to use with the provider
            use_s3: Whether to use S3 for database storage (kept for compatibility)
        """
        self.provider = provider
        self.model = model
        self.use_s3 = use_s3  # Kept for compatibility, not used in pipeline
        
        # Initialize the underlying pipeline
        self.pipeline = RAGPipeline(provider=provider, model=model)
        
        # Initialize state variables for compatibility
        self.repo_url_or_path = None
        self.transformed_docs = []
        self.retriever = None
        self.memory = self.pipeline.context
        
        logger.info(f"RAG Compatibility wrapper initialized with provider '{provider}' and model '{model}'")
    
    def prepare_retriever(self, repo_url_or_path: str, type: str = "github", access_token: str = None,
                          excluded_dirs: List[str] = None, excluded_files: List[str] = None,
                          included_dirs: List[str] = None, included_files: List[str] = None):
        """
        Prepare the retriever for a repository.
        
        This method maintains the same interface as the original rag.py
        while using the new pipeline architecture.
        
        Args:
            repo_url_or_path: URL or local path to the repository
            type: Type of repository (github, gitlab, bitbucket, local)
            access_token: Optional access token for private repositories
            excluded_dirs: Optional list of directories to exclude
            excluded_files: Optional list of file patterns to exclude
            included_dirs: Optional list of directories to include exclusively
            included_files: Optional list of file patterns to include exclusively
        """
        try:
            # Store repository information for compatibility
            self.repo_url_or_path = repo_url_or_path
            
            # Use the pipeline to prepare the repository
            self.pipeline.prepare_repository(
                repo_url_or_path=repo_url_or_path,
                repo_type=type,
                access_token=access_token,
                excluded_dirs=excluded_dirs,
                excluded_files=excluded_files,
                included_dirs=included_dirs,
                included_files=included_files
            )
            
            # Update compatibility variables
            self.transformed_docs = self.pipeline.context.transformed_docs
            
            # Get the retriever from the pipeline context
            # Note: In the pipeline, the retriever is created during execution
            # For compatibility, we'll create a reference that can be accessed
            self.retriever = self._get_retriever_reference()
            
            logger.info(f"Retriever prepared successfully for repository: {repo_url_or_path}")
            
        except Exception as e:
            logger.error(f"Failed to prepare retriever: {str(e)}")
            raise
    
    def call(self, query: str, language: str = "en") -> Tuple[Any, List]:
        """
        Process a query using RAG.
        
        This method maintains the same interface as the original rag.py
        while using the new pipeline architecture.
        
        Args:
            query: The user's query
            language: Language for the response (default: "en")
            
        Returns:
            Tuple of (RAGAnswer, retrieved_documents) for compatibility
        """
        try:
            # Use the pipeline to process the query
            result = self.pipeline.query(query, language)
            
            # Create a compatibility response object
            rag_answer = self._create_rag_answer(result)
            
            # Get retrieved documents from context
            retrieved_documents = self._get_retrieved_documents()
            
            return rag_answer, retrieved_documents
            
        except Exception as e:
            logger.error(f"Error in RAG call: {str(e)}")
            
            # Create error response for compatibility
            error_answer = self._create_error_answer(str(e))
            return error_answer, []
    
    def _get_retriever_reference(self):
        """Get a reference to the retriever for compatibility."""
        # This is a placeholder - in the actual pipeline, the retriever
        # is created during execution. For compatibility, we return
        # a reference that can be used by existing code.
        return self.pipeline.context
    
    def _create_rag_answer(self, result: dict) -> Any:
        """Create a RAGAnswer object for compatibility."""
        # Create a simple object that mimics the original RAGAnswer structure
        class RAGAnswer:
            def __init__(self, rationale: str, answer: str):
                self.rationale = rationale
                self.answer = answer
        
        return RAGAnswer(
            rationale=result.get("rationale", ""),
            answer=result.get("answer", "")
        )
    
    def _create_error_answer(self, error_message: str) -> Any:
        """Create an error RAGAnswer object for compatibility."""
        class RAGAnswer:
            def __init__(self, rationale: str, answer: str):
                self.rationale = rationale
                self.answer = answer
        
        return RAGAnswer(
            rationale="Error occurred while processing the query.",
            answer=f"I apologize, but I encountered an error while processing your question. Please try again or rephrase your question. Error: {error_message}"
        )
    
    def _get_retrieved_documents(self) -> List:
        """Get retrieved documents for compatibility."""
        # Return the documents from the pipeline context
        if hasattr(self.pipeline.context, 'retrieved_documents') and self.pipeline.context.retrieved_documents:
            return self.pipeline.context.retrieved_documents.documents
        return []

# Create a compatibility function that mimics the original RAG class
def create_rag(provider: str = "google", model: str = None, use_s3: bool = False) -> RAGCompatibility:
    """
    Create a RAG instance for compatibility.
    
    This function provides the same interface as the original RAG class
    constructor, ensuring backward compatibility.
    
    Args:
        provider: Model provider to use
        model: Model name to use
        use_s3: Whether to use S3 (kept for compatibility)
        
    Returns:
        RAGCompatibility instance that mimics the original RAG class
    """
    return RAGCompatibility(provider=provider, model=model, use_s3=use_s3)

# Export the compatibility class and function
__all__ = ["RAGCompatibility", "create_rag"]
