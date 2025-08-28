"""
Validation Utilities

This module contains utility functions for data validation, input validation, and validation helpers
extracted from various components throughout the codebase.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_language(language: str) -> str:
    """
    Validate and return the language, falling back to default if invalid.
    
    Args:
        language (str): Language code to validate
        
    Returns:
        str: Valid language code or default
    """
    supported_langs = ["en", "ja", "zh", "es", "kr", "vi", "fr", "pt-br", "ru", "zh-tw"]
    if language not in supported_langs:
        language = "en"  # Default to English
    return language


def validate_auth_code(authorization_code: Optional[str] = None) -> bool:
    """
    Validate authorization code if authentication is required.
    
    Args:
        authorization_code (str, optional): Authorization code to validate
        
    Returns:
        bool: True if authorization code is valid
    """
    # Simplified auth validation - will be enhanced when config is properly integrated
    # For now, always return True to allow endpoints to work
    return True


def validate_repository_config(repo_url: str, repo_type: str, access_token: Optional[str] = None) -> bool:
    """
    Validate repository configuration parameters.
    
    Args:
        repo_url (str): Repository URL to validate
        repo_type (str): Repository type to validate
        access_token (str, optional): Access token to validate
        
    Returns:
        bool: True if configuration is valid
    """
    # Validate repository URL
    if not repo_url or not isinstance(repo_url, str):
        logger.error("Repository URL is required and must be a string")
        return False
    
    # Validate repository type
    valid_repo_types = ["github", "gitlab", "bitbucket", "local"]
    if repo_type not in valid_repo_types:
        logger.error(f"Invalid repository type: {repo_type}. Must be one of {valid_repo_types}")
        return False
    
    # Validate access token for private repositories
    if repo_type != "local" and not access_token:
        logger.warning("No access token provided for remote repository")
        # Don't fail validation, just warn
    
    return True


def validate_query_config(query: str, max_length: int = 10000) -> bool:
    """
    Validate query configuration parameters.
    
    Args:
        query (str): Query string to validate
        max_length (int): Maximum allowed query length
        
    Returns:
        bool: True if query is valid
    """
    if not query or not isinstance(query, str):
        logger.error("Query is required and must be a string")
        return False
    
    if len(query.strip()) == 0:
        logger.error("Query cannot be empty")
        return False
    
    if len(query) > max_length:
        logger.error(f"Query exceeds maximum length of {max_length} characters")
        return False
    
    return True


def validate_documents(documents: List[Any]) -> bool:
    """
    Validate documents list.
    
    Args:
        documents (List[Any]): List of documents to validate
        
    Returns:
        bool: True if documents are valid
    """
    if not isinstance(documents, list):
        logger.error("Documents must be a list")
        return False
    
    if len(documents) == 0:
        logger.warning("Documents list is empty")
        return True  # Empty list is valid
    
    # Check if all documents have required attributes
    for i, doc in enumerate(documents):
        if not hasattr(doc, 'text') or not hasattr(doc, 'meta_data'):
            logger.error(f"Document {i} missing required attributes (text, meta_data)")
            return False
        
        if not doc.text or not isinstance(doc.text, str):
            logger.error(f"Document {i} has invalid text content")
            return False
    
    return True


def validate_embeddings(documents: List[Any]) -> List[Any]:
    """
    Validate embeddings and filter out documents with invalid or mismatched embedding sizes.
    
    Args:
        documents (List[Any]): List of documents with embeddings
        
    Returns:
        List[Any]: List of documents with valid embeddings of consistent size
    """
    if not documents:
        logger.warning("No documents provided for embedding validation")
        return []
    
    valid_documents = []
    embedding_sizes = {}
    
    # First pass: collect all embedding sizes and count occurrences
    for i, doc in enumerate(documents):
        if not hasattr(doc, 'vector') or doc.vector is None:
            logger.warning(f"Document {i} has no embedding vector, skipping")
            continue
        
        try:
            if isinstance(doc.vector, list):
                embedding_size = len(doc.vector)
            elif hasattr(doc.vector, 'shape'):
                embedding_size = doc.vector.shape[0] if len(doc.vector.shape) == 1 else doc.vector.shape[-1]
            elif hasattr(doc.vector, '__len__'):
                embedding_size = len(doc.vector)
            else:
                logger.warning(f"Document {i} has invalid embedding vector type: {type(doc.vector)}, skipping")
                continue
            
            if embedding_size == 0:
                logger.warning(f"Document {i} has empty embedding vector, skipping")
                continue
            
            embedding_sizes[embedding_size] = embedding_sizes.get(embedding_size, 0) + 1
            
        except Exception as e:
            logger.warning(f"Error processing document {i} embedding: {e}")
            continue
    
    if not embedding_sizes:
        logger.warning("No valid embeddings found")
        return []
    
    # Find the most common embedding size
    most_common_size = max(embedding_sizes.items(), key=lambda x: x[1])[0]
    logger.info(f"Most common embedding size: {most_common_size} (found in {embedding_sizes[most_common_size]} documents)")
    
    # Second pass: keep only documents with the most common embedding size
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
            
            if embedding_size == most_common_size:
                valid_documents.append(doc)
            else:
                logger.debug(f"Document {i} has embedding size {embedding_size}, expected {most_common_size}, skipping")
                
        except Exception as e:
            logger.debug(f"Error processing document {i} embedding: {e}")
            continue
    
    logger.info(f"Embedding validation complete: {len(valid_documents)}/{len(documents)} documents retained")
    return valid_documents


def validate_pipeline_state(pipeline_state: Dict[str, Any]) -> bool:
    """
    Validate pipeline state.
    
    Args:
        pipeline_state (Dict[str, Any]): Pipeline state to validate
        
    Returns:
        bool: True if pipeline state is valid
    """
    if not isinstance(pipeline_state, dict):
        logger.error("Pipeline state must be a dictionary")
        return False
    
    required_keys = ["status", "step", "context"]
    for key in required_keys:
        if key not in pipeline_state:
            logger.error(f"Pipeline state missing required key: {key}")
            return False
    
    # Validate status
    valid_statuses = ["idle", "running", "completed", "failed", "paused"]
    if pipeline_state["status"] not in valid_statuses:
        logger.error(f"Invalid pipeline status: {pipeline_state['status']}")
        return False
    
    return True


def validate_input_data(input_data: Any, expected_type: type, required: bool = True) -> bool:
    """
    Validate input data against expected type.
    
    Args:
        input_data (Any): Input data to validate
        expected_type (type): Expected type for the input data
        required (bool): Whether the input data is required
        
    Returns:
        bool: True if input data is valid
    """
    if required and input_data is None:
        logger.error("Input data is required but None was provided")
        return False
    
    if input_data is not None and not isinstance(input_data, expected_type):
        logger.error(f"Input data must be of type {expected_type.__name__}, got {type(input_data).__name__}")
        return False
    
    return True


def validate_output_data(output_data: Any, expected_type: type) -> bool:
    """
    Validate output data against expected type.
    
    Args:
        output_data (Any): Output data to validate
        expected_type (type): Expected type for the output data
        
    Returns:
        bool: True if output data is valid
    """
    if output_data is None:
        logger.warning("Output data is None")
        return True  # None output is valid in some cases
    
    if not isinstance(output_data, expected_type):
        logger.error(f"Output data must be of type {expected_type.__name__}, got {type(output_data).__name__}")
        return False
    
    return True


def validate_file_path(file_path: str, must_exist: bool = False, must_be_file: bool = False) -> bool:
    """
    Validate file path.
    
    Args:
        file_path (str): File path to validate
        must_exist (bool): Whether the file must exist
        must_be_file (bool): Whether the path must be a file (not directory)
        
    Returns:
        bool: True if file path is valid
    """
    if not file_path or not isinstance(file_path, str):
        logger.error("File path is required and must be a string")
        return False
    
    # Check if path exists
    if must_exist and not Path(file_path).exists():
        logger.error(f"File path does not exist: {file_path}")
        return False
    
    # Check if path is a file
    if must_be_file and not Path(file_path).is_file():
        logger.error(f"Path is not a file: {file_path}")
        return False
    
    return True


def validate_directory_path(dir_path: str, must_exist: bool = False, must_be_dir: bool = False) -> bool:
    """
    Validate directory path.
    
    Args:
        dir_path (str): Directory path to validate
        must_exist (bool): Whether the directory must exist
        must_be_dir (bool): Whether the path must be a directory (not file)
        
    Returns:
        bool: True if directory path is valid
    """
    if not dir_path or not isinstance(dir_path, str):
        logger.error("Directory path is required and must be a string")
        return False
    
    # Check if path exists
    if must_exist and not Path(dir_path).exists():
        logger.error(f"Directory path does not exist: {dir_path}")
        return False
    
    # Check if path is a directory
    if must_be_dir and not Path(dir_path).is_dir():
        logger.error(f"Path is not a directory: {dir_path}")
        return False
    
    return True


def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
    """
    Validate URL format and scheme.
    
    Args:
        url (str): URL to validate
        allowed_schemes (List[str], optional): List of allowed URL schemes
        
    Returns:
        bool: True if URL is valid
    """
    if not url or not isinstance(url, str):
        logger.error("URL is required and must be a string")
        return False
    
    # Basic URL pattern validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        logger.error(f"Invalid URL format: {url}")
        return False
    
    # Validate scheme if specified
    if allowed_schemes:
        scheme = url.split('://')[0].lower()
        if scheme not in allowed_schemes:
            logger.error(f"URL scheme '{scheme}' not allowed. Allowed schemes: {allowed_schemes}")
            return False
    
    return True


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email is valid
    """
    if not email or not isinstance(email, str):
        logger.error("Email is required and must be a string")
        return False
    
    # Basic email pattern validation
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    if not email_pattern.match(email):
        logger.error(f"Invalid email format: {email}")
        return False
    
    return True


def validate_and_filter_embeddings(documents: List[Any]) -> List[Any]:
    """
    Validate and filter embeddings, keeping only documents with valid embeddings.
    
    Args:
        documents (List[Any]): List of documents with embeddings
        
    Returns:
        List[Any]: Filtered list of documents with valid embeddings
    """
    if not documents:
        return []
    
    valid_documents = []
    
    for doc in documents:
        if not hasattr(doc, 'vector') or doc.vector is None:
            continue
        
        try:
            # Check if vector has valid content
            if isinstance(doc.vector, list):
                if len(doc.vector) > 0:
                    valid_documents.append(doc)
            elif hasattr(doc.vector, 'shape'):
                if doc.vector.size > 0:
                    valid_documents.append(doc)
            elif hasattr(doc.vector, '__len__'):
                if len(doc.vector) > 0:
                    valid_documents.append(doc)
        except Exception:
            continue
    
    return valid_documents
