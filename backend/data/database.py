"""
Database Operations Module

Handles database operations including LocalDB management, document transformation, and persistence.
"""

import os
import logging
from typing import List, Optional, Union
from adalflow.core.types import Document
from adalflow.core.db import LocalDB
from adalflow.components.data_process import TextSplitter, ToEmbeddings
from backend.core.config.settings import configs
from backend.tools.embedder import get_embedder
from backend.components.embedder import OllamaDocumentProcessor

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages the creation, loading, transformation, and persistence of LocalDB instances.
    """

    def __init__(self):
        self.db = None
        self.repo_url_or_path = None
        self.repo_paths = None

    def prepare_database(self, repo_url_or_path: Union[str, List[str]], type: str = "github", 
                        access_token: Optional[str] = None, is_ollama_embedder: Optional[bool] = None,
                        excluded_dirs: Optional[List[str]] = None, excluded_files: Optional[List[str]] = None,
                        included_dirs: Optional[List[str]] = None, included_files: Optional[List[str]] = None) -> List[Document]:
        """
        Prepare the database for a repository.

        Args:
            repo_url_or_path (Union[str, List[str]]): The URL or local path of the repository, or list of URLs
            type (str): Repository type (github, gitlab, bitbucket)
            access_token (str, optional): Access token for private repositories
            is_ollama_embedder (bool, optional): Whether to use Ollama for embedding.
                                               If None, will be determined from configuration.
            excluded_dirs (List[str], optional): List of directories to exclude from processing
            excluded_files (List[str], optional): List of file patterns to exclude from processing
            included_dirs (List[str], optional): List of directories to include exclusively
            included_files (List[str], optional): List of file patterns to include exclusively

        Returns:
            List[Document]: List of Document objects
        """
        self.reset_database()
        self._create_repo(repo_url_or_path, type, access_token)
        return self.prepare_db_index(is_ollama_embedder=is_ollama_embedder, 
                                   excluded_dirs=excluded_dirs, excluded_files=excluded_files,
                                   included_dirs=included_dirs, included_files=included_files)

    def reset_database(self):
        """
        Reset the database to its initial state.
        """
        self.db = None
        self.repo_url_or_path = None
        self.repo_paths = None

    def _extract_repo_name_from_url(self, repo_url_or_path: str, repo_type: str) -> str:
        """
        Extract owner and repo name to create unique identifier.
        
        Args:
            repo_url_or_path (str): Repository URL or path
            repo_type (str): Type of repository
            
        Returns:
            str: Repository name identifier
        """
        url_parts = repo_url_or_path.rstrip('/').split('/')

        if repo_type in ["github", "gitlab", "bitbucket"] and len(url_parts) >= 5:
            # GitHub URL format: https://github.com/owner/repo
            # GitLab URL format: https://gitlab.com/owner/repo or https://gitlab.com/group/subgroup/repo
            # Bitbucket URL format: https://bitbucket.org/owner/repo
            owner = url_parts[-2]
            repo = url_parts[-1].replace(".git", "")
            repo_name = f"{owner}_{repo}"
        else:
            repo_name = url_parts[-1].replace(".git", "")
        return repo_name

    def _create_repo(self, repo_url_or_path: Union[str, List[str]], repo_type: str = "github", 
                     access_token: Optional[str] = None) -> None:
        """
        Download and prepare all paths.
        Paths:
        ~/.adalflow/repos/{owner}_{repo_name} (for url, local path will be the same)
        ~/.adalflow/databases/{owner}_{repo_name}.pkl

        Args:
            repo_url_or_path (Union[str, List[str]]): The URL or local path of the repository, or list of URLs
            repo_type (str): Repository type
            access_token (str, optional): Access token for private repositories
        """
        # Handle list input - for now, we'll use the first repository
        # TODO: Implement multi-repository support
        if isinstance(repo_url_or_path, list):
            if not repo_url_or_path:
                raise ValueError("Repository URL list cannot be empty")
            if len(repo_url_or_path) > 1:
                logger.warning(f"Multiple repositories provided: {repo_url_or_path}. Using first repository: {repo_url_or_path[0]}")
            repo_url_or_path = repo_url_or_path[0]
        
        # Validate that we now have a string
        if not isinstance(repo_url_or_path, str):
            raise ValueError(f"Invalid repository URL type: {type(repo_url_or_path)}. Expected string or list of strings.")
        
        logger.info(f"Preparing repo storage for {repo_url_or_path}...")

        try:
            from adalflow.utils import get_adalflow_default_root_path
            root_path = get_adalflow_default_root_path()

            os.makedirs(root_path, exist_ok=True)
            
            # url
            if repo_url_or_path.startswith("https://") or repo_url_or_path.startswith("http://"):
                # Extract the repository name from the URL
                repo_name = self._extract_repo_name_from_url(repo_url_or_path, repo_type)
                logger.info(f"Extracted repo name: {repo_name}")

                save_repo_dir = os.path.join(root_path, "repos", repo_name)

                # Check if the repository directory already exists and is not empty
                if not (os.path.exists(save_repo_dir) and os.listdir(save_repo_dir)):
                    # Only download if the repository doesn't exist or is empty
                    from backend.components.processors.repository_processor import RepositoryProcessor
                    repo_processor = RepositoryProcessor()
                    repo_processor.download_repo(repo_url_or_path, save_repo_dir, repo_type, access_token)
                else:
                    logger.info(f"Repository already exists at {save_repo_dir}. Using existing repository.")
            else:  # local path
                repo_name = os.path.basename(repo_url_or_path)
                save_repo_dir = repo_url_or_path

            save_db_file = os.path.join(root_path, "databases", f"{repo_name}.pkl")
            os.makedirs(save_repo_dir, exist_ok=True)
            os.makedirs(os.path.dirname(save_db_file), exist_ok=True)

            self.repo_paths = {
                "save_repo_dir": save_repo_dir,
                "save_db_file": save_db_file,
            }
            self.repo_url_or_path = repo_url_or_path
            logger.info(f"Repo paths: {self.repo_paths}")

        except Exception as e:
            logger.error(f"Failed to create repository structure: {e}")
            raise

    def prepare_db_index(self, is_ollama_embedder: Optional[bool] = None, 
                        excluded_dirs: Optional[List[str]] = None, 
                        excluded_files: Optional[List[str]] = None,
                        included_dirs: Optional[List[str]] = None, 
                        included_files: Optional[List[str]] = None) -> List[Document]:
        """
        Prepare the indexed database for the repository.

        Args:
            is_ollama_embedder (bool, optional): Whether to use Ollama for embedding.
                                               If None, will be determined from configuration.
            excluded_dirs (List[str], optional): List of directories to exclude from processing
            excluded_files (List[str], optional): List of file patterns to exclude from processing
            included_dirs (List[str], optional): List of directories to include exclusively
            included_files (List[str], optional): List of file patterns to include exclusively

        Returns:
            List[Document]: List of Document objects
        """
        # check the database
        if self.repo_paths and os.path.exists(self.repo_paths["save_db_file"]):
            logger.info("Loading existing database...")
            try:
                self.db = LocalDB.load_state(self.repo_paths["save_db_file"])
                documents = self.db.get_transformed_data(key="split_and_embed")
                if documents:
                    logger.info(f"Loaded {len(documents)} documents from existing database")
                    return documents
            except Exception as e:
                logger.error(f"Error loading existing database: {e}")
                # Continue to create a new database

        # prepare the database
        logger.info("Creating new database...")
        from backend.components.processors.document_processor import DocumentProcessor
        doc_processor = DocumentProcessor()
        
        documents = doc_processor.read_all_documents(
            self.repo_paths["save_repo_dir"],
            is_ollama_embedder=is_ollama_embedder,
            excluded_dirs=excluded_dirs, excluded_files=excluded_files,
            included_dirs=included_dirs, included_files=included_files
        )
        
        self.db = self._transform_documents_and_save_to_db(
            documents, self.repo_paths["save_db_file"], is_ollama_embedder=is_ollama_embedder
        )
        logger.info(f"Total documents: {len(documents)}")
        transformed_docs = self.db.get_transformed_data(key="split_and_embed")
        logger.info(f"Total transformed documents: {len(transformed_docs)}")
        return transformed_docs

    def prepare_retriever(self, repo_url_or_path: Union[str, List[str]], type: str = "github", 
                         access_token: Optional[str] = None):
        """
        Prepare the retriever for a repository.
        This is a compatibility method for the isolated API.

        Args:
            repo_url_or_path (Union[str, List[str]]): The URL or local path of the repository, or list of URLs
            type (str): Repository type
            access_token (str, optional): Access token for private repositories

        Returns:
            List[Document]: List of Document objects
        """
        return self.prepare_database(repo_url_or_path, type, access_token)

    def _transform_documents_and_save_to_db(self, documents: List[Document], 
                                          db_path: str, 
                                          is_ollama_embedder: Optional[bool] = None) -> LocalDB:
        """
        Transforms a list of documents and saves them to a local database.

        Args:
            documents (list): A list of `Document` objects.
            db_path (str): The path to the local database file.
            is_ollama_embedder (bool, optional): Whether to use Ollama for embedding.
                                               If None, will be determined from configuration.
        """
        # Get the data transformer
        data_transformer = self._prepare_data_pipeline(is_ollama_embedder)

        # Save the documents to a local database
        db = LocalDB()
        db.register_transformer(transformer=data_transformer, key="split_and_embed")
        db.load(documents)
        db.transform(key="split_and_embed")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db.save_state(filepath=db_path)
        return db

    def _prepare_data_pipeline(self, is_ollama_embedder: Optional[bool] = None):
        """
        Creates and returns the data transformation pipeline.

        Args:
            is_ollama_embedder (bool, optional): Whether to use Ollama for embedding.
                                               If None, will be determined from configuration.

        Returns:
            adal.Sequential: The data transformation pipeline
        """
        from backend.core.config.settings import get_embedder_config, is_ollama_embedder as check_ollama

        # Determine if using Ollama embedder if not specified
        if is_ollama_embedder is None:
            is_ollama_embedder = check_ollama()

        splitter = TextSplitter(**configs["text_splitter"])
        embedder_config = get_embedder_config()

        embedder = get_embedder()

        if is_ollama_embedder:
            # Use Ollama document processor with batch processing for better performance
            batch_size = embedder_config.get("batch_size", 8)  # Smaller batch size for Ollama due to local processing
            embedder_transformer = OllamaDocumentProcessor(embedder=embedder, batch_size=batch_size)
        else:
            # Use batch processing for other embedders
            batch_size = embedder_config.get("batch_size", 500)
            embedder_transformer = ToEmbeddings(
                embedder=embedder, batch_size=batch_size
            )

        import adalflow as adal
        data_transformer = adal.Sequential(
            splitter, embedder_transformer
        )  # sequential will chain together splitter and embedder
        return data_transformer

    def get_database(self) -> Optional[LocalDB]:
        """
        Get the current database instance.
        
        Returns:
            Optional[LocalDB]: The current database instance or None if not initialized
        """
        return self.db

    def get_repo_paths(self) -> Optional[dict]:
        """
        Get the repository paths.
        
        Returns:
            Optional[dict]: Repository paths or None if not initialized
        """
        return self.repo_paths

    def is_database_loaded(self) -> bool:
        """
        Check if a database is currently loaded.
        
        Returns:
            bool: True if database is loaded, False otherwise
        """
        return self.db is not None

    def get_document_count(self) -> int:
        """
        Get the number of documents in the current database.
        
        Returns:
            int: Number of documents, 0 if no database is loaded
        """
        if self.db is None:
            return 0
        
        try:
            documents = self.db.get_transformed_data(key="split_and_embed")
            return len(documents) if documents else 0
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
