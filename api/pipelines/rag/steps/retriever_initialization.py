"""
Retriever Initialization Step for RAG Pipeline.

This step handles the creation and configuration of the FAISS retriever
with the prepared documents and appropriate embedder.
"""

import logging
import time
from typing import Any, List

from api.pipelines.base import PipelineStep, PipelineContext
from api.pipelines.rag.rag_context import RAGPipelineContext
from api.components.retriever.faiss_retriever import FAISSRetriever
from api.tools.embedder import get_embedder
from api.config import configs

logger = logging.getLogger(__name__)

class RetrieverInitializationStep(PipelineStep[List[Any], FAISSRetriever]):
    """Pipeline step for initializing the FAISS retriever."""
    
    def __init__(self):
        super().__init__("retriever_initialization")
        self.embedder = None
        self.query_embedder = None
    
    def execute(self, input_data: List[Any], context: PipelineContext) -> FAISSRetriever:
        """Execute the retriever initialization step."""
        if not isinstance(context, RAGPipelineContext):
            raise ValueError("Context must be RAGPipelineContext")
        
        rag_context = context
        rag_context.set_step(self.name, 1)
        start_time = time.time()
        
        try:
            self.logger.info("Initializing FAISS retriever")
            
            # Validate that documents are available
            if not rag_context.validate_documents():
                raise ValueError(f"Documents validation failed: {rag_context.get_last_error()}")
            
            # Get embedder configuration
            self._setup_embedders(rag_context)
            
            # Create FAISS retriever
            retriever = self._create_faiss_retriever(rag_context)
            
            # Record timing
            duration = time.time() - start_time
            rag_context.add_step_timing(self.name, duration)
            
            self.logger.info(f"Retriever initialization completed in {duration:.2f}s")
            return retriever
            
        except Exception as e:
            duration = time.time() - start_time
            rag_context.add_step_timing(self.name, duration)
            rag_context.add_error(f"Retriever initialization failed: {str(e)}")
            self.logger.error(f"Retriever initialization failed: {str(e)}")
            raise
    
    def validate_input(self, input_data: List[Any]) -> bool:
        """Validate that input is a list of documents."""
        return isinstance(input_data, list) and len(input_data) > 0
    
    def validate_output(self, output_data: FAISSRetriever) -> bool:
        """Validate that output is a FAISS retriever."""
        return isinstance(output_data, FAISSRetriever)
    
    def _setup_embedders(self, context: RAGPipelineContext) -> None:
        """Set up embedders for the retriever."""
        try:
            # Get the main embedder
            self.embedder = get_embedder()
            
            # Create query embedder based on Ollama compatibility
            if context.is_ollama_embedder:
                self._create_ollama_query_embedder(context)
            else:
                self.query_embedder = self.embedder
            
            context.logger.info("Embedders configured successfully")
            
        except Exception as e:
            context.add_error(f"Failed to setup embedders: {str(e)}")
            raise
    
    def _create_ollama_query_embedder(self, context: RAGPipelineContext) -> None:
        """Create a query embedder compatible with Ollama."""
        def single_string_embedder(query):
            # Accepts either a string or a list, always returns embedding for a single string
            if isinstance(query, list):
                if len(query) != 1:
                    raise ValueError("Ollama embedder only supports a single string")
                query = query[0]
            return self.embedder(input=query)
        
        self.query_embedder = single_string_embedder
        context.logger.info("Created Ollama-compatible query embedder")
    
    def _create_faiss_retriever(self, context: RAGPipelineContext) -> FAISSRetriever:
        """Create the FAISS retriever with proper configuration."""
        try:
            # Use the appropriate embedder for retrieval
            retrieve_embedder = self.query_embedder if context.is_ollama_embedder else self.embedder
            
            # Create FAISS retriever
            retriever = FAISSRetriever(
                **configs["retriever"],
                embedder=retrieve_embedder,
                documents=context.transformed_docs,
                document_map_func=lambda doc: doc.vector,
            )
            
            context.logger.info("FAISS retriever created successfully")
            return retriever
            
        except Exception as e:
            # Provide more specific error information for embedding size issues
            if "All embeddings should be of the same size" in str(e):
                context.add_error("Embedding size validation failed. This suggests there are still inconsistent embedding sizes.")
                self._log_embedding_sizes_for_debugging(context)
            
            context.add_error(f"Failed to create FAISS retriever: {str(e)}")
            raise
    
    def _log_embedding_sizes_for_debugging(self, context: RAGPipelineContext) -> None:
        """Log embedding sizes for debugging purposes."""
        try:
            sizes = []
            for i, doc in enumerate(context.transformed_docs[:10]):  # Check first 10 docs
                if hasattr(doc, 'vector') and doc.vector is not None:
                    try:
                        if isinstance(doc.vector, list):
                            size = len(doc.vector)
                        elif hasattr(doc.vector, 'shape'):
                            size = doc.vector.shape[0] if len(doc.vector.shape) == 1 else doc.vector.shape[-1]
                        elif hasattr(doc.vector, '__len__'):
                            size = len(doc.vector)
                        else:
                            size = "unknown"
                        sizes.append(f"doc_{i}: {size}")
                    except:
                        sizes.append(f"doc_{i}: error")
            
            if sizes:
                context.logger.error(f"Sample embedding sizes: {', '.join(sizes)}")
            
        except Exception as e:
            context.logger.error(f"Failed to log embedding sizes for debugging: {str(e)}")
