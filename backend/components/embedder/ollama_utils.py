from typing import Sequence, Callable, Optional
from copy import deepcopy
import logging
import os
import requests
from tqdm import tqdm

import adalflow as adal
from adalflow.core.types import Document

# Configure logging
from backend.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class OllamaModelNotFoundError(Exception):
    """Custom exception for when Ollama model is not found"""
    pass


def check_ollama_model_exists(model_name: str, ollama_host: Optional[str] = None) -> bool:
    """
    Check if an Ollama model exists before attempting to use it.
    """
    if ollama_host is None:
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    try:
        if ollama_host.endswith('/api'):
            ollama_host = ollama_host[:-4]

        response = requests.get(f"{ollama_host}/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            available_models = [model.get('name', '').split(':')[0] for model in models_data.get('models', [])]
            model_base_name = model_name.split(':')[0]

            is_available = model_base_name in available_models
            if is_available:
                logger.info(f"Ollama model '{model_name}' is available")
            else:
                logger.warning(f"Ollama model '{model_name}' is not available. Available models: {available_models}")
            return is_available
        else:
            logger.warning(f"Could not check Ollama models, status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.warning(f"Could not connect to Ollama to check models: {e}")
        return False
    except Exception as e:
        logger.warning(f"Error checking Ollama model availability: {e}")
        return False


class OllamaDocumentProcessor(adal.Component):
    """
    Process documents for Ollama embeddings using batch processing for better performance.
    Uses concurrent requests to reduce total processing time and avoid frontend timeouts.
    """
    def __init__(self, embedder: adal.Embedder, batch_size: int = 8) -> None:
        super().__init__()
        self.embedder = embedder
        self.batch_size = batch_size  # Process documents in batches

    def call(self, documents: Sequence[Document]) -> Sequence[Document]:
        output = deepcopy(documents)
        logger.info(f"Processing {len(output)} documents in batches of {self.batch_size} for Ollama embeddings")

        successful_docs = []
        expected_embedding_size = None

        # Process documents in batches for better performance
        for batch_start in tqdm(range(0, len(output), self.batch_size), desc="Processing document batches"):
            batch_end = min(batch_start + self.batch_size, len(output))
            batch_docs = output[batch_start:batch_end]
            
            # Extract texts from batch
            batch_texts = [doc.text for doc in batch_docs]
            
            try:
                # Process entire batch at once (uses concurrent requests internally)
                result = self.embedder(input=batch_texts)
                
                if result.data and len(result.data) > 0:
                    # Process each embedding result
                    for i, embedding_result in enumerate(result.data):
                        if i >= len(batch_docs):  # Safety check
                            break
                            
                        doc_index = batch_start + i
                        embedding = embedding_result.embedding

                        if expected_embedding_size is None:
                            expected_embedding_size = len(embedding)
                            logger.info(f"Expected embedding size set to: {expected_embedding_size}")
                        elif len(embedding) != expected_embedding_size:
                            file_path = getattr(batch_docs[i], 'meta_data', {}).get('file_path', f'document_{doc_index}')
                            logger.warning(f"Document '{file_path}' has inconsistent embedding size {len(embedding)} != {expected_embedding_size}, skipping")
                            continue

                        output[doc_index].vector = embedding
                        successful_docs.append(output[doc_index])
                else:
                    # If batch processing failed, try individual documents in this batch
                    logger.warning(f"Batch processing failed for batch {batch_start}-{batch_end}, trying individual documents")
                    for i, doc in enumerate(batch_docs):
                        doc_index = batch_start + i
                        try:
                            individual_result = self.embedder(input=doc.text)
                            if individual_result.data and len(individual_result.data) > 0:
                                embedding = individual_result.data[0].embedding

                                if expected_embedding_size is None:
                                    expected_embedding_size = len(embedding)
                                    logger.info(f"Expected embedding size set to: {expected_embedding_size}")
                                elif len(embedding) != expected_embedding_size:
                                    file_path = getattr(doc, 'meta_data', {}).get('file_path', f'document_{doc_index}')
                                    logger.warning(f"Document '{file_path}' has inconsistent embedding size {len(embedding)} != {expected_embedding_size}, skipping")
                                    continue

                                output[doc_index].vector = embedding
                                successful_docs.append(output[doc_index])
                            else:
                                file_path = getattr(doc, 'meta_data', {}).get('file_path', f'document_{doc_index}')
                                logger.warning(f"Failed to get embedding for document '{file_path}', skipping")
                        except Exception as e:
                            file_path = getattr(doc, 'meta_data', {}).get('file_path', f'document_{doc_index}')
                            logger.error(f"Error processing individual document '{file_path}': {e}, skipping")
                            
            except Exception as e:
                logger.error(f"Error processing batch {batch_start}-{batch_end}: {e}, trying individual documents")
                # Fallback to individual processing for this batch
                for i, doc in enumerate(batch_docs):
                    doc_index = batch_start + i
                    try:
                        individual_result = self.embedder(input=doc.text)
                        if individual_result.data and len(individual_result.data) > 0:
                            embedding = individual_result.data[0].embedding

                            if expected_embedding_size is None:
                                expected_embedding_size = len(embedding)
                                logger.info(f"Expected embedding size set to: {expected_embedding_size}")
                            elif len(embedding) != expected_embedding_size:
                                file_path = getattr(doc, 'meta_data', {}).get('file_path', f'document_{doc_index}')
                                logger.warning(f"Document '{file_path}' has inconsistent embedding size {len(embedding)} != {expected_embedding_size}, skipping")
                                continue

                            output[doc_index].vector = embedding
                            successful_docs.append(output[doc_index])
                        else:
                            file_path = getattr(doc, 'meta_data', {}).get('file_path', f'document_{doc_index}')
                            logger.warning(f"Failed to get embedding for document '{file_path}', skipping")
                    except Exception as individual_e:
                        file_path = getattr(doc, 'meta_data', {}).get('file_path', f'document_{doc_index}')
                        logger.error(f"Error processing individual document '{file_path}': {individual_e}, skipping")

        logger.info(f"Successfully processed {len(successful_docs)}/{len(output)} documents with consistent embeddings")
        return successful_docs


__all__ = [
    "OllamaModelNotFoundError",
    "check_ollama_model_exists",
    "OllamaDocumentProcessor",
]


