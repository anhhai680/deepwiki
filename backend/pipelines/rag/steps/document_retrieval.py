"""
Document Retrieval Step for RAG Pipeline.

This step handles querying the retriever and processing the retrieved
documents for the RAG pipeline.
"""

import logging
import time
from typing import Any, List

from backend.pipelines.base import PipelineStep, PipelineContext
from backend.pipelines.rag.rag_context import RAGPipelineContext
from backend.components.retriever.faiss_retriever import FAISSRetriever
from backend.components.retriever.base import RetrievalResult

logger = logging.getLogger(__name__)

class DocumentRetrievalStep(PipelineStep[FAISSRetriever, List[Any]]):
    """Pipeline step for retrieving relevant documents."""
    
    def __init__(self):
        super().__init__("document_retrieval")
    
    def execute(self, input_data: FAISSRetriever, context: PipelineContext) -> List[Any]:
        """Execute the document retrieval step."""
        if not isinstance(context, RAGPipelineContext):
            raise ValueError("Context must be RAGPipelineContext")
        
        rag_context = context
        rag_context.set_step(self.name, 2)
        start_time = time.time()
        
        try:
            retriever = input_data
            query = rag_context.user_query
            self.logger.info(f"Retrieving documents for query: {query[:100]}...")
            
            # Validate query
            if not rag_context.validate_query_config():
                raise ValueError(f"Query validation failed: {rag_context.get_last_error()}")
            
            # Execute retrieval
            retrieved_documents = retriever(query)
            
            # Process retrieved documents
            processed_docs = self._process_retrieved_documents(retrieved_documents, rag_context)
            
            # Update context with retrieved documents
            rag_context.retrieved_documents = retrieved_documents
            
            # Record timing
            duration = time.time() - start_time
            rag_context.add_step_timing(self.name, duration)
            
            self.logger.info(f"Document retrieval completed in {duration:.2f}s, found {len(processed_docs)} documents")
            return processed_docs
            
        except Exception as e:
            duration = time.time() - start_time
            rag_context.add_step_timing(self.name, duration)
            rag_context.add_error(f"Document retrieval failed: {str(e)}")
            self.logger.error(f"Document retrieval failed: {str(e)}")
            raise
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate that input is a FAISS retriever."""
        return isinstance(input_data, FAISSRetriever)
    
    def validate_output(self, output_data: Any) -> bool:
        """Validate that output is a list of documents."""
        return isinstance(output_data, list)
    
    def _process_retrieved_documents(self, retrieved_documents: RetrievalResult, context: RAGPipelineContext) -> List[Any]:
        """
        Process the retrieved documents and fill in the document content.
        
        Args:
            retrieved_documents: Retrieval result from the retriever
            context: RAG pipeline context
            
        Returns:
            List of processed documents with content
        """
        if not retrieved_documents:
            context.add_warning("No documents retrieved from retriever")
            return []
        
        try:
            # Fill in the document content from the transformed docs
            if hasattr(retrieved_documents, 'doc_indices') and hasattr(retrieved_documents, 'documents'):
                retrieved_documents.documents = [
                    context.transformed_docs[doc_index]
                    for doc_index in retrieved_documents.doc_indices
                ]
                
                context.logger.info(f"Processed {len(retrieved_documents.documents)} retrieved documents")
                return retrieved_documents.documents
            else:
                context.add_warning("Retrieval result missing doc_indices or documents attribute")
                return []
                
        except Exception as e:
            context.add_error(f"Failed to process retrieved documents: {str(e)}")
            raise
