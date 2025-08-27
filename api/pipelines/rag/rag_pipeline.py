"""
RAG Pipeline implementation that orchestrates retrieval-augmented generation workflow.

This module extracts and refactors the RAG orchestration logic from the original rag.py
into a proper pipeline architecture with clear separation of concerns.
"""

import logging
import weakref
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Optional

import adalflow as adal
from adalflow.components.retriever.faiss_retriever import FAISSRetriever

from ..base.base_pipeline import BasePipeline, PipelineStage, PipelineContext
from api.tools.embedder import get_embedder
from api.prompts import RAG_SYSTEM_PROMPT as system_prompt, RAG_TEMPLATE
from api.config import configs, get_model_config
from api.data_pipeline import DatabaseManager

logger = logging.getLogger(__name__)

# Maximum token limit for embedding models
MAX_INPUT_TOKENS = 7500  # Safe threshold below 8192 token limit


@dataclass
class RAGAnswer(adal.DataClass):
    """RAG response data structure."""
    rationale: str = field(default="", metadata={"desc": "Chain of thoughts for the answer."})
    answer: str = field(default="", metadata={"desc": "Answer to the user query, formatted in markdown for beautiful rendering with react-markdown. DO NOT include ``` triple backticks fences at the beginning or end of your answer."})

    __output_fields__ = ["rationale", "answer"]


@dataclass
class RAGInput:
    """Input data structure for RAG pipeline."""
    query: str
    language: str = "en"
    repo_url_or_path: Optional[str] = None
    access_token: Optional[str] = None
    excluded_dirs: Optional[List[str]] = None
    excluded_files: Optional[List[str]] = None
    included_dirs: Optional[List[str]] = None
    included_files: Optional[List[str]] = None


@dataclass 
class RAGOutput:
    """Output data structure for RAG pipeline."""
    answer: RAGAnswer
    retrieved_documents: List[Any]
    execution_metadata: Dict[str, Any]


class RepositoryPreparationStage(PipelineStage):
    """Stage responsible for preparing repository data and retriever."""
    
    def __init__(self, embedder, is_ollama_embedder: bool = False):
        super().__init__("repository_preparation")
        self.embedder = embedder
        self.is_ollama_embedder = is_ollama_embedder
        self.db_manager = DatabaseManager()
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Prepare repository data and create retriever."""
        try:
            rag_input: RAGInput = context.input_data
            
            # Check if retriever already exists
            if context.get_stage_result("retriever"):
                self.logger.debug("Retriever already exists, skipping preparation")
                return context
            
            if not rag_input.repo_url_or_path:
                context.add_error("Repository URL or path is required", self.name)
                return context
            
            # Prepare repository database
            self.logger.info(f"Preparing repository: {rag_input.repo_url_or_path}")
            transformed_docs = self.db_manager.prepare_database(
                rag_input.repo_url_or_path,
                "github",
                rag_input.access_token,
                is_ollama_embedder=self.is_ollama_embedder,
                excluded_dirs=rag_input.excluded_dirs,
                excluded_files=rag_input.excluded_files,
                included_dirs=rag_input.included_dirs,
                included_files=rag_input.included_files
            )
            
            # Validate and filter embeddings
            transformed_docs = self._validate_and_filter_embeddings(transformed_docs)
            
            if not transformed_docs:
                context.add_error("No valid documents with embeddings found", self.name)
                return context
            
            # Create retriever
            query_embedder = self._get_query_embedder()
            retriever = FAISSRetriever(
                **configs["retriever"],
                embedder=query_embedder,
                documents=transformed_docs,
                document_map_func=lambda doc: doc.vector,
            )
            
            # Store results
            context.add_stage_result("transformed_docs", transformed_docs)
            context.add_stage_result("retriever", retriever)
            context.add_metadata("repository_url", rag_input.repo_url_or_path)
            context.add_metadata("document_count", len(transformed_docs))
            
            self.logger.info(f"Repository preparation completed with {len(transformed_docs)} documents")
            
        except Exception as e:
            context = self._handle_error(context, e)
        
        return context
    
    def _get_query_embedder(self):
        """Get the appropriate query embedder based on configuration."""
        if self.is_ollama_embedder:
            # Create single string embedder for Ollama
            def single_string_embedder(query):
                if isinstance(query, list):
                    if len(query) != 1:
                        raise ValueError("Ollama embedder only supports a single string")
                    query = query[0]
                return self.embedder(input=query)
            return single_string_embedder
        else:
            return self.embedder
    
    def _validate_and_filter_embeddings(self, documents: List) -> List:
        """Validate embeddings and filter out documents with invalid or mismatched embedding sizes."""
        if not documents:
            self.logger.warning("No documents provided for embedding validation")
            return []

        valid_documents = []
        embedding_sizes = {}

        # First pass: collect all embedding sizes and count occurrences
        for i, doc in enumerate(documents):
            if not hasattr(doc, 'vector') or doc.vector is None:
                self.logger.warning(f"Document {i} has no embedding vector, skipping")
                continue

            try:
                if isinstance(doc.vector, list):
                    embedding_size = len(doc.vector)
                elif hasattr(doc.vector, 'shape'):
                    embedding_size = doc.vector.shape[0] if len(doc.vector.shape) == 1 else doc.vector.shape[-1]
                elif hasattr(doc.vector, '__len__'):
                    embedding_size = len(doc.vector)
                else:
                    self.logger.warning(f"Document {i} has invalid embedding vector type: {type(doc.vector)}, skipping")
                    continue

                if embedding_size == 0:
                    self.logger.warning(f"Document {i} has empty embedding vector, skipping")
                    continue

                embedding_sizes[embedding_size] = embedding_sizes.get(embedding_size, 0) + 1

            except Exception as e:
                self.logger.warning(f"Error checking embedding size for document {i}: {str(e)}, skipping")
                continue

        if not embedding_sizes:
            self.logger.error("No valid embeddings found in any documents")
            return []

        # Find the most common embedding size (this should be the correct one)
        target_size = max(embedding_sizes.keys(), key=lambda k: embedding_sizes[k])
        self.logger.info(f"Target embedding size: {target_size} (found in {embedding_sizes[target_size]} documents)")

        # Log all embedding sizes found
        for size, count in embedding_sizes.items():
            if size != target_size:
                self.logger.warning(f"Found {count} documents with incorrect embedding size {size}, will be filtered out")

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
                    self.logger.warning(f"Filtering out document '{file_path}' due to embedding size mismatch: {embedding_size} != {target_size}")

            except Exception as e:
                file_path = getattr(doc, 'meta_data', {}).get('file_path', f'document_{i}')
                self.logger.warning(f"Error validating embedding for document '{file_path}': {str(e)}, skipping")
                continue

        self.logger.info(f"Embedding validation complete: {len(valid_documents)}/{len(documents)} documents have valid embeddings")
        return valid_documents


class DocumentRetrievalStage(PipelineStage):
    """Stage responsible for retrieving relevant documents based on the query."""
    
    def __init__(self):
        super().__init__("document_retrieval")
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Retrieve relevant documents for the query."""
        try:
            rag_input: RAGInput = context.input_data
            retriever = context.get_stage_result("retriever")
            transformed_docs = context.get_stage_result("transformed_docs")
            
            if not retriever:
                context.add_error("Retriever not available", self.name)
                return context
            
            if not transformed_docs:
                context.add_error("Transformed documents not available", self.name)
                return context
            
            # Retrieve relevant documents
            self.logger.debug(f"Retrieving documents for query: {rag_input.query[:100]}...")
            retrieved_documents = retriever(rag_input.query)
            
            # Fill in the actual document content
            if retrieved_documents and len(retrieved_documents) > 0:
                retrieved_documents[0].documents = [
                    transformed_docs[doc_index]
                    for doc_index in retrieved_documents[0].doc_indices
                ]
            
            context.add_stage_result("retrieved_documents", retrieved_documents)
            context.add_metadata("retrieval_count", len(retrieved_documents[0].documents) if retrieved_documents else 0)
            
            self.logger.info(f"Retrieved {len(retrieved_documents[0].documents) if retrieved_documents else 0} relevant documents")
            
        except Exception as e:
            context = self._handle_error(context, e)
        
        return context


class ResponseGenerationStage(PipelineStage):
    """Stage responsible for generating the final response using the retrieved documents."""
    
    def __init__(self, provider: str, model: str, memory):
        super().__init__("response_generation")
        self.provider = provider
        self.model = model
        self.memory = memory
        self._setup_generator()
    
    def _setup_generator(self):
        """Set up the response generator."""
        # Set up the output parser
        data_parser = adal.DataClassParser(data_class=RAGAnswer, return_data_class=True)

        # Format instructions to ensure proper output structure
        format_instructions = data_parser.get_output_format_str() + """

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

        # Get model configuration based on provider and model
        generator_config = get_model_config(self.provider, self.model)

        # Set up the main generator
        self.generator = adal.Generator(
            template=RAG_TEMPLATE,
            prompt_kwargs={
                "output_format_str": format_instructions,
                "conversation_history": self.memory(),
                "system_prompt": system_prompt,
                "contexts": None,
            },
            model_client=generator_config["model_client"](),
            model_kwargs=generator_config["model_kwargs"],
            output_processors=data_parser,
        )
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Generate response using retrieved documents."""
        try:
            rag_input: RAGInput = context.input_data
            retrieved_documents = context.get_stage_result("retrieved_documents")
            
            if not retrieved_documents:
                context.add_error("Retrieved documents not available", self.name)
                return context
            
            # Prepare contexts from retrieved documents
            contexts = []
            if retrieved_documents and len(retrieved_documents) > 0:
                for doc in retrieved_documents[0].documents:
                    if hasattr(doc, 'text'):
                        contexts.append(doc.text)
                    elif hasattr(doc, 'content'):
                        contexts.append(doc.content)
            
            # Update generator with current context
            self.generator.prompt_kwargs.update({
                "contexts": contexts,
                "conversation_history": self.memory(),
            })
            
            # Generate response
            self.logger.debug("Generating response...")
            response = self.generator(query=rag_input.query, language=rag_input.language)
            
            # Add to memory if successful
            if hasattr(response, 'answer') and response.answer:
                self.memory.add_dialog_turn(rag_input.query, response.answer)
            
            context.add_stage_result("rag_answer", response)
            context.add_metadata("context_count", len(contexts))
            context.add_metadata("language", rag_input.language)
            
            self.logger.info("Response generation completed successfully")
            
        except Exception as e:
            context = self._handle_error(context, e)
            # Create error response
            error_response = RAGAnswer(
                rationale="Error occurred while processing the query.",
                answer="I apologize, but I encountered an error while processing your question. Please try again or rephrase your question."
            )
            context.add_stage_result("rag_answer", error_response)
        
        return context


class RAGPipeline(BasePipeline):
    """
    RAG Pipeline that orchestrates the complete retrieval-augmented generation workflow.
    
    This pipeline extracts and refactors the RAG orchestration logic from the original rag.py
    into a modular, testable pipeline architecture.
    """
    
    def __init__(self, provider: str = "google", model: str = None, use_s3: bool = False):
        super().__init__("rag_pipeline")
        
        self.provider = provider
        self.model = model
        
        # Import helper functions
        from api.config import is_ollama_embedder
        
        # Determine if we're using Ollama embedder based on configuration
        self.is_ollama_embedder = is_ollama_embedder()
        
        # Check if Ollama model exists before proceeding
        if self.is_ollama_embedder:
            self._validate_ollama_model()
        
        # Initialize components
        from api.rag import Memory  # Import the existing Memory class
        self.memory = Memory()
        self.embedder = get_embedder()
        
        # Configure pipeline stages
        self._configure_stages()
    
    def _validate_ollama_model(self):
        """Validate that required Ollama model exists."""
        from api.ollama_patch import check_ollama_model_exists
        from api.config import get_embedder_config
        
        embedder_config = get_embedder_config()
        if embedder_config and embedder_config.get("model_kwargs", {}).get("model"):
            model_name = embedder_config["model_kwargs"]["model"]
            if not check_ollama_model_exists(model_name):
                raise Exception(f"Ollama model '{model_name}' not found. Please run 'ollama pull {model_name}' to install it.")
    
    def _configure_stages(self) -> None:
        """Configure the RAG pipeline stages."""
        # Add repository preparation stage
        self.add_stage(RepositoryPreparationStage(
            embedder=self.embedder,
            is_ollama_embedder=self.is_ollama_embedder
        ))
        
        # Add document retrieval stage
        self.add_stage(DocumentRetrievalStage())
        
        # Add response generation stage
        self.add_stage(ResponseGenerationStage(
            provider=self.provider,
            model=self.model,
            memory=self.memory
        ))
    
    def prepare_retriever(self, repo_url_or_path: str, type: str = "github", access_token: str = None,
                         excluded_dirs: List[str] = None, excluded_files: List[str] = None,
                         included_dirs: List[str] = None, included_files: List[str] = None):
        """
        Prepare the retriever for a repository.
        This method provides compatibility with the original RAG API.
        """
        rag_input = RAGInput(
            query="",  # Empty query for preparation
            repo_url_or_path=repo_url_or_path,
            access_token=access_token,
            excluded_dirs=excluded_dirs,
            excluded_files=excluded_files,
            included_dirs=included_dirs,
            included_files=included_files
        )
        
        # Execute only the repository preparation stage
        context = PipelineContext(input_data=rag_input)
        prep_stage = RepositoryPreparationStage(
            embedder=self.embedder,
            is_ollama_embedder=self.is_ollama_embedder
        )
        
        context = prep_stage.execute(context)
        
        if not context.success:
            raise ValueError(f"Repository preparation failed: {'; '.join(context.errors)}")
        
        # Store the prepared components for future queries
        self._prepared_retriever = context.get_stage_result("retriever")
        self._prepared_docs = context.get_stage_result("transformed_docs")
        
        self.logger.info(f"Repository prepared successfully with {context.metadata.get('document_count', 0)} documents")
    
    def call(self, query: str, language: str = "en") -> Tuple[RAGAnswer, List]:
        """
        Process a query using RAG.
        This method provides compatibility with the original RAG API.
        
        Args:
            query: The user's query
            language: Language for the response
            
        Returns:
            Tuple of (RAGAnswer, retrieved_documents)
        """
        # Create input for the pipeline
        rag_input = RAGInput(query=query, language=language)
        
        # Create context and inject prepared components if available
        context = PipelineContext(input_data=rag_input)
        if hasattr(self, '_prepared_retriever'):
            context.add_stage_result("retriever", self._prepared_retriever)
            context.add_stage_result("transformed_docs", self._prepared_docs)
        
        # Execute pipeline stages
        try:
            # Skip repository preparation if already prepared
            start_stage = 1 if hasattr(self, '_prepared_retriever') else 0
            
            for stage in self.stages[start_stage:]:
                if not context.success:
                    break
                context = stage.execute(context)
            
            # Extract results
            rag_answer = context.get_stage_result("rag_answer")
            retrieved_documents = context.get_stage_result("retrieved_documents")
            
            if not rag_answer:
                # Create error response if no answer was generated
                rag_answer = RAGAnswer(
                    rationale="No answer was generated.",
                    answer="I apologize, but I couldn't generate an answer. Please try again."
                )
            
            return rag_answer, retrieved_documents or []
            
        except Exception as e:
            self.logger.error(f"Error in RAG pipeline: {str(e)}")
            error_response = RAGAnswer(
                rationale="Error occurred while processing the query.",
                answer="I apologize, but I encountered an error while processing your question. Please try again or rephrase your question."
            )
            return error_response, []
    
    def _post_process(self, context: PipelineContext) -> PipelineContext:
        """Post-process the pipeline results."""
        if context.success:
            # Create final output structure
            rag_answer = context.get_stage_result("rag_answer")
            retrieved_documents = context.get_stage_result("retrieved_documents")
            
            output = RAGOutput(
                answer=rag_answer,
                retrieved_documents=retrieved_documents or [],
                execution_metadata=context.metadata
            )
            
            context.output_data = output
        
        return context