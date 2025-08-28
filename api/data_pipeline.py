"""
Data Pipeline Module

This module provides a simplified interface to the data processing components.
It maintains backward compatibility while using the extracted processor components.
"""

import logging
from typing import List, Optional
from adalflow.core.types import Document

# Import the extracted components
from api.components.processors.token_counter import TokenCounter
from api.components.processors.repository_processor import RepositoryProcessor
from api.components.processors.document_processor import DocumentProcessor
from api.data.database import DatabaseManager

logger = logging.getLogger(__name__)

# Backward compatibility functions
def count_tokens(text: str, is_ollama_embedder: Optional[bool] = None) -> int:
    """
    Count the number of tokens in a text string using tiktoken.
    
    This function is maintained for backward compatibility.
    For new code, use TokenCounter class directly.
    
    Args:
        text (str): The text to count tokens for.
        is_ollama_embedder (bool, optional): Whether using Ollama embeddings.
                                           If None, will be determined from configuration.

    Returns:
        int: The number of tokens in the text.
    """
    token_counter = TokenCounter()
    return token_counter.count_tokens(text, is_ollama_embedder)

def download_repo(repo_url: str, local_path: str, type: str = "github", access_token: Optional[str] = None) -> str:
    """
    Downloads a Git repository (GitHub, GitLab, or Bitbucket) to a specified local path.
    
    This function is maintained for backward compatibility.
    For new code, use RepositoryProcessor class directly.
    
    Args:
        repo_url (str): The URL of the Git repository to clone.
        local_path (str): The local directory where the repository will be cloned.
        type (str): Repository type (github, gitlab, bitbucket)
        access_token (str, optional): Access token for private repositories.

    Returns:
        str: The output message from the `git` command.
    """
    repo_processor = RepositoryProcessor()
    return repo_processor.download_repo(repo_url, local_path, type, access_token)

# Alias for backward compatibility
download_github_repo = download_repo

def read_all_documents(path: str, is_ollama_embedder: Optional[bool] = None, 
                      excluded_dirs: Optional[List[str]] = None, 
                      excluded_files: Optional[List[str]] = None,
                      included_dirs: Optional[List[str]] = None, 
                      included_files: Optional[List[str]] = None) -> List[Document]:
    """
    Recursively reads all documents in a directory and its subdirectories.
    
    This function is maintained for backward compatibility.
    For new code, use DocumentProcessor class directly.
    
    Args:
        path (str): The root directory path.
        is_ollama_embedder (bool, optional): Whether using Ollama embeddings for token counting.
                                           If None, will be determined from configuration.
        excluded_dirs (List[str], optional): List of directories to exclude from processing.
            Overrides the default configuration if provided.
        excluded_files (List[str], optional): List of file patterns to exclude from processing.
            Overrides the default configuration if provided.
        included_dirs (List[str], optional): List of directories to include exclusively.
            When provided, only files in these directories will be processed.
        included_files (List[str], optional): List of file patterns to include exclusively.
            When provided, only files matching these patterns will be processed.

    Returns:
        list: A list of Document objects with metadata.
    """
    doc_processor = DocumentProcessor()
    return doc_processor.read_all_documents(
        path, is_ollama_embedder, excluded_dirs, excluded_files, 
        included_dirs, included_files
    )

def prepare_data_pipeline(is_ollama_embedder: Optional[bool] = None):
    """
    Creates and returns the data transformation pipeline.
    
    This function is maintained for backward compatibility.
    For new code, use DatabaseManager class directly.
    
    Args:
        is_ollama_embedder (bool, optional): Whether to use Ollama for embedding.
                                           If None, will be determined from configuration.

    Returns:
        adal.Sequential: The data transformation pipeline
    """
    db_manager = DatabaseManager()
    return db_manager._prepare_data_pipeline(is_ollama_embedder)

def transform_documents_and_save_to_db(documents: List[Document], db_path: str, 
                                     is_ollama_embedder: Optional[bool] = None) -> 'LocalDB':
    """
    Transforms a list of documents and saves them to a local database.
    
    This function is maintained for backward compatibility.
    For new code, use DatabaseManager class directly.
    
    Args:
        documents (list): A list of `Document` objects.
        db_path (str): The path to the local database file.
        is_ollama_embedder (bool, optional): Whether to use Ollama for embedding.
                                           If None, will be determined from configuration.
    """
    db_manager = DatabaseManager()
    return db_manager._transform_documents_and_save_to_db(documents, db_path, is_ollama_embedder)

def get_github_file_content(repo_url: str, file_path: str, access_token: Optional[str] = None) -> str:
    """
    Retrieves the content of a file from a GitHub repository using the GitHub API.
    
    This function is maintained for backward compatibility.
    For new code, use RepositoryProcessor class directly.
    
    Args:
        repo_url (str): The URL of the GitHub repository 
                       (e.g., "https://github.com/username/repo" or "https://github.company.com/username/repo")
        file_path (str): The path to the file within the repository (e.g., "src/main.py")
        access_token (str, optional): GitHub personal access token for private repositories

    Returns:
        str: The content of the file as a string

    Raises:
        ValueError: If the file cannot be fetched or if the URL is not a valid GitHub URL
    """
    repo_processor = RepositoryProcessor()
    return repo_processor.get_github_file_content(repo_url, file_path, access_token)

def get_gitlab_file_content(repo_url: str, file_path: str, access_token: Optional[str] = None) -> str:
    """
    Retrieves the content of a file from a GitLab repository (cloud or self-hosted).
    
    This function is maintained for backward compatibility.
    For new code, use RepositoryProcessor class directly.
    
    Args:
        repo_url (str): The GitLab repo URL (e.g., "https://gitlab.com/username/repo" or "http://localhost/group/project")
        file_path (str): File path within the repository (e.g., "src/main.py")
        access_token (str, optional): GitLab personal access token

    Returns:
        str: File content

    Raises:
        ValueError: If anything fails
    """
    repo_processor = RepositoryProcessor()
    return repo_processor.get_gitlab_file_content(repo_url, file_path, access_token)

def get_bitbucket_file_content(repo_url: str, file_path: str, access_token: Optional[str] = None) -> str:
    """
    Retrieves the content of a file from a Bitbucket repository using the Bitbucket API.
    
    This function is maintained for backward compatibility.
    For new code, use RepositoryProcessor class directly.
    
    Args:
        repo_url (str): The URL of the Bitbucket repository (e.g., "https://bitbucket.org/username/repo")
        file_path (str): The path to the file within the repository (e.g., "src/main.py")
        access_token (str, optional): Bitbucket personal access token for private repositories

    Returns:
        str: The content of the file as a string
    """
    repo_processor = RepositoryProcessor()
    return repo_processor.get_bitbucket_file_content(repo_url, file_path, access_token)

def get_file_content(repo_url: str, file_path: str, type: str = "github", access_token: Optional[str] = None) -> str:
    """
    Retrieves the content of a file from a Git repository (GitHub, GitLab, or Bitbucket).
    
    This function is maintained for backward compatibility.
    For new code, use RepositoryProcessor class directly.
    
    Args:
        repo_url (str): The URL of the repository
        file_path (str): The path to the file within the repository
        type (str): Repository type (github, gitlab, bitbucket)
        access_token (str, optional): Access token for private repositories

    Returns:
        str: The content of the file as a string

    Raises:
        ValueError: If the file cannot be fetched or if the URL is not valid
    """
    repo_processor = RepositoryProcessor()
    return repo_processor.get_file_content(repo_url, file_path, type, access_token)

# The DatabaseManager class is now imported from api.data.database
# This maintains backward compatibility while using the extracted components
DatabaseManager = DatabaseManager
