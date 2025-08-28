"""
Repository Preparation Step for RAG Pipeline.

This step handles loading and preparing the repository for RAG processing,
including document transformation and embedding validation.
"""

import logging
import time
from typing import Any, List

from api.pipelines.base import PipelineStep, PipelineContext
from api.pipelines.rag.rag_context import RAGPipelineContext
from api.data_pipeline import DatabaseManager

logger = logging.getLogger(__name__)

class RepositoryPreparationStep(PipelineStep[str, List[Any]]):
    """Pipeline step for preparing repository data."""
    
    def __init__(self):
        super().__init__("repository_preparation")
        self.db_manager = DatabaseManager()
    
    def execute(self, input_data: str, context: PipelineContext) -> List[Any]:
        """Execute the repository preparation step."""
        if not isinstance(context, RAGPipelineContext):
            raise ValueError("Context must be RAGPipelineContext")
        
        rag_context = context
        rag_context.set_step(self.name, 0)
        start_time = time.time()
        
        try:
            self.logger.info(f"Preparing repository: {rag_context.repo_url_or_path}")
            
            # Validate repository configuration
            if not rag_context.validate_repository_config():
                raise ValueError(f"Invalid repository configuration: {rag_context.get_last_error()}")
            
            # Prepare database and load documents
            transformed_docs = self.db_manager.prepare_database(
                rag_context.repo_url_or_path,
                rag_context.repo_type,
                rag_context.access_token,
                is_ollama_embedder=rag_context.is_ollama_embedder,
                excluded_dirs=rag_context.excluded_dirs,
                excluded_files=rag_context.excluded_files,
                included_dirs=rag_context.included_dirs,
                included_files=rag_context.included_files
            )
            
            self.logger.info(f"Loaded {len(transformed_docs)} documents for retrieval")
            
            # Validate and filter embeddings
            valid_docs = self._validate_and_filter_embeddings(transformed_docs, rag_context)
            
            if not valid_docs:
                raise ValueError("No valid documents with embeddings found. Cannot create retriever.")
            
            # Update context with transformed documents
            rag_context.transformed_docs = valid_docs
            rag_context.logger.info(f"Using {len(valid_docs)} documents with valid embeddings for retrieval")
            
            # Record timing
            duration = time.time() - start_time
            rag_context.add_step_timing(self.name, duration)
            
            self.logger.info(f"Repository preparation completed in {duration:.2f}s")
            return valid_docs
            
        except Exception as e:
            duration = time.time() - start_time
            rag_context.add_step_timing(self.name, duration)
            rag_context.add_error(f"Repository preparation failed: {str(e)}")
            self.logger.error(f"Repository preparation failed: {str(e)}")
            raise
    
    def validate_input(self, input_data: str) -> bool:
        """Validate that input is a repository URL or path."""
        return isinstance(input_data, str) and len(input_data.strip()) > 0
    
    def validate_output(self, output_data: List[Any]) -> bool:
        """Validate that output is a list of documents."""
        return isinstance(output_data, list) and len(output_data) > 0
    
    def _validate_and_filter_embeddings(self, documents: List[Any], context: RAGPipelineContext) -> List[Any]:
        """
        Validate embeddings and filter out documents with invalid or mismatched embedding sizes.
        
        Args:
            documents: List of documents with embeddings
            context: RAG pipeline context for logging
            
        Returns:
            List of documents with valid embeddings of consistent size
        """
        if not documents:
            context.add_warning("No documents provided for embedding validation")
            return []
        
        valid_documents = []
        embedding_sizes = {}
        
        # First pass: collect all embedding sizes and count occurrences
        for i, doc in enumerate(documents):
            if not hasattr(doc, 'vector') or doc.vector is None:
                context.add_warning(f"Document {i} has no embedding vector, skipping")
                continue
            
            try:
                if isinstance(doc.vector, list):
                    embedding_size = len(doc.vector)
                elif hasattr(doc.vector, 'shape'):
                    embedding_size = doc.vector.shape[0] if len(doc.vector.shape) == 1 else doc.vector.shape[-1]
                elif hasattr(doc.vector, '__len__'):
                    embedding_size = len(doc.vector)
                else:
                    context.add_warning(f"Document {i} has invalid embedding vector type: {type(doc.vector)}, skipping")
                    continue
                
                if embedding_size == 0:
                    context.add_warning(f"Document {i} has empty embedding vector, skipping")
                    continue
                
                embedding_sizes[embedding_size] = embedding_sizes.get(embedding_size, 0) + 1
                
            except Exception as e:
                context.add_warning(f"Error checking embedding size for document {i}: {str(e)}, skipping")
                continue
        
        if not embedding_sizes:
            context.add_error("No valid embeddings found in any documents")
            return []
        
        # Find the most common embedding size (this should be the correct one)
        target_size = max(embedding_sizes.keys(), key=lambda k: embedding_sizes[k])
        context.logger.info(f"Target embedding size: {target_size} (found in {embedding_sizes[target_size]} documents)")
        
        # Log all embedding sizes found
        for size, count in embedding_sizes.items():
            if size != target_size:
                context.add_warning(f"Found {count} documents with incorrect embedding size {size}, will be filtered out")
        
        # Second pass: filter documents with the target embedding size
        for i, doc in enumerate(documents):
            if not hasattr(doc, 'vector') or doc.vector is None:
                continue
            
            try:
                if isinstance(doc.vector, list):
                    embedding_size = len(doc.vector)
                elif hasattr(doc.vector, 'shape'):
                    embedding_size = doc.vector.shape[0] if len(doc.vector.shape) == 1 else doc.vector.shape[-1]
                elif hasattr(doc.vector, '__len__'):
                    embedding_size = len(doc.vector)
                else:
                    continue
                
                if embedding_size == target_size:
                    valid_documents.append(doc)
                else:
                    # Log which document is being filtered out
                    file_path = getattr(doc, 'meta_data', {}).get('file_path', f'document_{i}')
                    context.add_warning(f"Filtering out document '{file_path}' due to embedding size mismatch: {embedding_size} != {target_size}")
                
            except Exception as e:
                file_path = getattr(doc, 'meta_data', {}).get('file_path', f'document_{i}')
                context.add_warning(f"Error validating embedding for document '{file_path}': {str(e)}, skipping")
                continue
        
        context.logger.info(f"Embedding validation complete: {len(valid_documents)}/{len(documents)} documents have valid embeddings")
        
        if len(valid_documents) == 0:
            context.add_error("No documents with valid embeddings remain after filtering")
        elif len(valid_documents) < len(documents):
            filtered_count = len(documents) - len(valid_documents)
            context.add_warning(f"Filtered out {filtered_count} documents due to embedding issues")
        
        return valid_documents
