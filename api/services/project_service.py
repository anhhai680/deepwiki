"""
Project Service for DeepWiki.

This module provides a service layer for project operations, extracting business logic
from data_pipeline.py and providing a clean interface for project processing, indexing,
and management.
"""

import os
import subprocess
import json
import logging
import base64
import re
import glob
from typing import List, Optional, Dict, Any, Tuple
from urllib.parse import urlparse, urlunparse, quote
import requests
from requests.exceptions import RequestException

from adalflow.core.types import Document
from adalflow.core.db import LocalDB
from adalflow.utils import get_adalflow_default_root_path

from api.config import configs, DEFAULT_EXCLUDED_DIRS, DEFAULT_EXCLUDED_FILES

logger = logging.getLogger(__name__)

# Maximum token limit for OpenAI embedding models
MAX_EMBEDDING_TOKENS = 8192


class ProjectService:
    """Service layer for project operations and management."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._adalflow_root = get_adalflow_default_root_path()
    
    def count_tokens(self, text: str, is_ollama_embedder: bool = None) -> int:
        """
        Count the number of tokens in a text string using tiktoken.

        Args:
            text (str): The text to count tokens for.
            is_ollama_embedder (bool, optional): Whether using Ollama embeddings.
                                               If None, will be determined from configuration.

        Returns:
            int: The number of tokens in the text.
        """
        try:
            # Determine if using Ollama embedder if not specified
            if is_ollama_embedder is None:
                from api.config import is_ollama_embedder as check_ollama
                is_ollama_embedder = check_ollama()

            if is_ollama_embedder:
                import tiktoken
                encoding = tiktoken.get_encoding("cl100k_base")
            else:
                import tiktoken
                encoding = tiktoken.encoding_for_model("text-embedding-3-small")

            return len(encoding.encode(text))
        except Exception as e:
            # Fallback to a simple approximation if tiktoken fails
            self.logger.warning(f"Error counting tokens with tiktoken: {e}")
            # Rough approximation: 4 characters per token
            return len(text) // 4
    
    def download_repository(
        self, 
        repo_url: str, 
        local_path: str, 
        repo_type: str = "github", 
        access_token: str = None
    ) -> str:
        """
        Downloads a Git repository (GitHub, GitLab, or Bitbucket) to a specified local path.

        Args:
            repo_url (str): The URL of the Git repository to clone.
            local_path (str): The local directory where the repository will be cloned.
            repo_type (str): The type of repository (github, gitlab, bitbucket).
            access_token (str, optional): Access token for private repositories.

        Returns:
            str: The output message from the `git` command.
        """
        try:
            # Check if Git is installed
            self.logger.info(f"Preparing to clone repository to {local_path}")
            subprocess.run(
                ["git", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Check if repository already exists
            if os.path.exists(local_path) and os.listdir(local_path):
                # Directory exists and is not empty
                self.logger.warning(f"Repository already exists at {local_path}. Using existing repository.")
                return f"Using existing repository at {local_path}"

            # Ensure the local path exists
            os.makedirs(local_path, exist_ok=True)

            # Prepare the clone URL with access token if provided
            clone_url = repo_url
            if access_token:
                parsed = urlparse(repo_url)
                # Determine the repository type and format the URL accordingly
                if repo_type == "github":
                    # Format: https://{token}@{domain}/owner/repo.git
                    # Works for both github.com and enterprise GitHub domains
                    clone_url = urlunparse((parsed.scheme, f"{access_token}@{parsed.netloc}", parsed.path, '', '', ''))
                elif repo_type == "gitlab":
                    # Format: https://oauth2:{token}@gitlab.com/owner/repo.git
                    clone_url = urlunparse((parsed.scheme, f"oauth2:{access_token}@{parsed.netloc}", parsed.path, '', '', ''))
                elif repo_type == "bitbucket":
                    # Format: https://x-token-auth:{token}@bitbucket.org/owner/repo.git
                    clone_url = urlunparse((parsed.scheme, f"x-token-auth:{access_token}@{parsed.netloc}", parsed.path, '', '', ''))

                self.logger.info("Using access token for authentication")

            # Clone the repository
            self.logger.info(f"Cloning repository from {repo_url} to {local_path}")
            # We use repo_url in the log to avoid exposing the token in logs
            result = subprocess.run(
                ["git", "clone", "--depth=1", "--single-branch", clone_url, local_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.logger.info("Repository cloned successfully")
            return result.stdout.decode("utf-8")

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8')
            # Sanitize error message to remove any tokens
            if access_token and access_token in error_msg:
                error_msg = error_msg.replace(access_token, "***TOKEN***")
            raise ValueError(f"Error during cloning: {error_msg}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred: {str(e)}")
    
    def read_all_documents(
        self, 
        path: str, 
        is_ollama_embedder: bool = None, 
        excluded_dirs: List[str] = None, 
        excluded_files: List[str] = None,
        included_dirs: List[str] = None, 
        included_files: List[str] = None
    ) -> List[Document]:
        """
        Recursively reads all documents in a directory and its subdirectories.

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
        documents = []
        # File extensions to look for, prioritizing code files
        code_extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".hpp", ".go", ".rs",
                           ".jsx", ".tsx", ".html", ".css", ".php", ".swift", ".cs"]
        doc_extensions = [".md", ".txt", ".rst", ".json", ".yaml", ".yml"]

        # Determine filtering mode: inclusion or exclusion
        use_inclusion_mode = (included_dirs is not None and len(included_dirs) > 0) or (included_files is not None and len(included_files) > 0)

        if use_inclusion_mode:
            # Inclusion mode: only process specified directories and files
            final_included_dirs = set(included_dirs) if included_dirs else set()
            final_included_files = set(included_files) if included_files else set()

            self.logger.info(f"Using inclusion mode")
            self.logger.info(f"Included directories: {list(final_included_dirs)}")
            self.logger.info(f"Included files: {list(final_included_files)}")

            # Convert to lists for processing
            included_dirs = list(final_included_dirs)
            included_files = list(final_included_files)
            excluded_dirs = []
            excluded_files = []
        else:
            # Exclusion mode: use default exclusions plus any additional ones
            final_excluded_dirs = set(DEFAULT_EXCLUDED_DIRS)
            final_excluded_files = set(DEFAULT_EXCLUDED_FILES)

            # Add any additional excluded directories from config
            if "file_filters" in configs and "excluded_dirs" in configs["file_filters"]:
                final_excluded_dirs.update(configs["file_filters"]["excluded_dirs"])

            # Add any additional excluded files from config
            if "file_filters" in configs and "excluded_files" in configs["file_filters"]:
                final_excluded_files.update(configs["file_filters"]["excluded_files"])

            # Add any explicitly provided excluded directories and files
            if excluded_dirs is not None:
                final_excluded_dirs.update(excluded_dirs)

            if excluded_files is not None:
                final_excluded_files.update(excluded_files)

            # Convert back to lists for compatibility
            excluded_dirs = list(final_excluded_dirs)
            excluded_files = list(final_excluded_files)
            included_dirs = []
            included_files = []

            self.logger.info(f"Using exclusion mode")
            self.logger.info(f"Excluded directories: {excluded_dirs}")
            self.logger.info(f"Excluded files: {excluded_files}")

        self.logger.info(f"Reading documents from {path}")

        def should_process_file(file_path: str, use_inclusion: bool, included_dirs: List[str], included_files: List[str],
                               excluded_dirs: List[str], excluded_files: List[str]) -> bool:
            """
            Determine if a file should be processed based on inclusion/exclusion rules.

            Args:
                file_path (str): The file path to check
                use_inclusion (bool): Whether to use inclusion mode
                included_dirs (List[str]): List of directories to include
                included_files (List[str]): List of files to include
                excluded_dirs (List[str]): List of directories to exclude
                excluded_files (List[str]): List of files to exclude

            Returns:
                bool: True if the file should be processed, False otherwise
            """
            file_path_parts = os.path.normpath(file_path).split(os.sep)
            file_name = os.path.basename(file_path)

            if use_inclusion:
                # Inclusion mode: file must be in included directories or match included files
                is_included = False

                # Check if file is in an included directory
                if included_dirs:
                    for included in included_dirs:
                        clean_included = included.strip("./").rstrip("/")
                        if clean_included in file_path_parts:
                            is_included = True
                            break

                # Check if file matches included file patterns
                if not is_included and included_files:
                    for included_file in included_files:
                        if file_name == included_file or file_name.endswith(included_file):
                            is_included = True
                            break

                # If no inclusion rules are specified for a category, allow all files from that category
                if not included_dirs and not included_files:
                    is_included = True
                elif not included_dirs and included_files:
                    # Only file patterns specified, allow all directories
                    pass  # is_included is already set based on file patterns
                elif included_dirs and not included_files:
                    # Only directory patterns specified, allow all files in included directories
                    pass  # is_included is already set based on directory patterns

                return is_included
            else:
                # Exclusion mode: file must not be in excluded directories or match excluded files
                is_excluded = False

                # Check if file is in an excluded directory
                for excluded in excluded_dirs:
                    clean_excluded = excluded.strip("./").rstrip("/")
                    if clean_excluded in file_path_parts:
                        is_excluded = True
                        break

                # Check if file matches excluded file patterns
                if not is_excluded:
                    for excluded_file in excluded_files:
                        if file_name == excluded_file:
                            is_excluded = True
                            break

                return not is_excluded

        # Process code files first
        for ext in code_extensions:
            files = glob.glob(f"{path}/**/*{ext}", recursive=True)
            for file_path in files:
                # Check if file should be processed based on inclusion/exclusion rules
                if not should_process_file(file_path, use_inclusion_mode, included_dirs, included_files, excluded_dirs, excluded_files):
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        relative_path = os.path.relpath(file_path, path)

                        # Determine if this is an implementation file
                        is_implementation = (
                            not relative_path.startswith("test_")
                            and not relative_path.startswith("app_")
                            and "test" not in relative_path.lower()
                        )

                        # Check token count
                        token_count = self.count_tokens(content, is_ollama_embedder)
                        if token_count > MAX_EMBEDDING_TOKENS * 10:
                            self.logger.warning(f"Skipping large file {relative_path}: Token count ({token_count}) exceeds limit")
                            continue

                        doc = Document(
                            text=content,
                            meta_data={
                                "file_path": relative_path,
                                "type": ext[1:],
                                "is_code": True,
                                "is_implementation": is_implementation,
                                "title": relative_path,
                                "token_count": token_count,
                            },
                        )
                        documents.append(doc)
                except Exception as e:
                    self.logger.error(f"Error reading {file_path}: {e}")

        # Then process documentation files
        for ext in doc_extensions:
            files = glob.glob(f"{path}/**/*{ext}", recursive=True)
            for file_path in files:
                # Check if file should be processed based on inclusion/exclusion rules
                if not should_process_file(file_path, use_inclusion_mode, included_dirs, included_files, excluded_dirs, excluded_files):
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        relative_path = os.path.relpath(file_path, path)

                        # Check token count
                        token_count = self.count_tokens(content, is_ollama_embedder)
                        if token_count > MAX_EMBEDDING_TOKENS:
                            self.logger.warning(f"Skipping large file {relative_path}: Token count ({token_count}) exceeds limit")
                            continue

                        doc = Document(
                            text=content,
                            meta_data={
                                "file_path": relative_path,
                                "type": ext[1:],
                                "is_code": False,
                                "is_implementation": False,
                                "title": relative_path,
                                "token_count": token_count,
                            },
                        )
                        documents.append(doc)
                except Exception as e:
                    self.logger.error(f"Error reading {file_path}: {e}")

        self.logger.info(f"Found {len(documents)} documents")
        return documents
    
    def get_file_content(self, repo_url: str, file_path: str, repo_type: str = "github", access_token: str = None) -> str:
        """
        Retrieves the content of a file from a Git repository (GitHub, GitLab, or Bitbucket).

        Args:
            repo_url (str): The URL of the repository
            file_path (str): The path to the file within the repository
            repo_type (str): The type of repository (github, gitlab, bitbucket)
            access_token (str, optional): Access token for private repositories

        Returns:
            str: The content of the file as a string

        Raises:
            ValueError: If the file cannot be fetched or if the URL is not valid
        """
        if repo_type == "github":
            return self._get_github_file_content(repo_url, file_path, access_token)
        elif repo_type == "gitlab":
            return self._get_gitlab_file_content(repo_url, file_path, access_token)
        elif repo_type == "bitbucket":
            return self._get_bitbucket_file_content(repo_url, file_path, access_token)
        else:
            raise ValueError("Unsupported repository URL. Only GitHub, GitLab, and Bitbucket are supported.")
    
    def _get_github_file_content(self, repo_url: str, file_path: str, access_token: str = None) -> str:
        """Internal method to get GitHub file content."""
        try:
            # Parse the repository URL to support both github.com and enterprise GitHub
            parsed_url = urlparse(repo_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Not a valid GitHub repository URL")

            # Check if it's a GitHub-like URL structure
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) < 2:
                raise ValueError("Invalid GitHub URL format - expected format: https://domain/owner/repo")

            owner = path_parts[-2]
            repo = path_parts[-1].replace(".git", "")

            # Determine the API base URL
            if parsed_url.netloc == "github.com":
                # Public GitHub
                api_base = "https://api.github.com"
            else:
                # GitHub Enterprise - API is typically at https://domain/api/v3/
                api_base = f"{parsed_url.scheme}://{parsed_url.netloc}/api/v3"
            
            # Use GitHub API to get file content
            api_url = f"{api_base}/repos/{owner}/{repo}/contents/{file_path}"

            # Fetch file content from GitHub API
            headers = {}
            if access_token:
                headers["Authorization"] = f"token {access_token}"
            self.logger.info(f"Fetching file content from GitHub API: {api_url}")
            
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            
            content_data = response.json()

            # Check if we got an error response
            if "message" in content_data and "documentation_url" in content_data:
                raise ValueError(f"GitHub API error: {content_data['message']}")

            # GitHub API returns file content as base64 encoded string
            if "content" in content_data and "encoding" in content_data:
                if content_data["encoding"] == "base64":
                    # The content might be split into lines, so join them first
                    content_base64 = content_data["content"].replace("\n", "")
                    content = base64.b64decode(content_base64).decode("utf-8")
                    return content
                else:
                    raise ValueError(f"Unexpected encoding: {content_data['encoding']}")
            else:
                raise ValueError("File content not found in GitHub API response")

        except Exception as e:
            raise ValueError(f"Failed to get file content: {str(e)}")
    
    def _get_gitlab_file_content(self, repo_url: str, file_path: str, access_token: str = None) -> str:
        """Internal method to get GitLab file content."""
        try:
            # Parse and validate the URL
            parsed_url = urlparse(repo_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Not a valid GitLab repository URL")

            gitlab_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            if parsed_url.port not in (None, 80, 443):
                gitlab_domain += f":{parsed_url.port}"
            path_parts = parsed_url.path.strip("/").split("/")
            if len(path_parts) < 2:
                raise ValueError("Invalid GitLab URL format — expected something like https://gitlab.domain.com/group/project")

            # Build project path and encode for API
            project_path = "/".join(path_parts).replace(".git", "")
            encoded_project_path = quote(project_path, safe='')

            # Encode file path
            encoded_file_path = quote(file_path, safe='')

            # Try to get the default branch from the project info
            default_branch = None
            try:
                project_info_url = f"{gitlab_domain}/api/v4/projects/{encoded_project_path}"
                project_headers = {}
                if access_token:
                    project_headers["PRIVATE-TOKEN"] = access_token
                
                project_response = requests.get(project_info_url, headers=project_headers)
                if project_response.status_code == 200:
                    project_data = project_response.json()
                    default_branch = project_data.get('default_branch', 'main')
                    self.logger.info(f"Found default branch: {default_branch}")
                else:
                    self.logger.warning(f"Could not fetch project info, using 'main' as default branch")
                    default_branch = 'main'
            except Exception as e:
                self.logger.warning(f"Error fetching project info: {e}, using 'main' as default branch")
                default_branch = 'main'

            api_url = f"{gitlab_domain}/api/v4/projects/{encoded_project_path}/repository/files/{encoded_file_path}/raw?ref={default_branch}"
            # Fetch file content from GitLab API
            headers = {}
            if access_token:
                headers["PRIVATE-TOKEN"] = access_token
            self.logger.info(f"Fetching file content from GitLab API: {api_url}")
            
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            content = response.text

            # Check for GitLab error response (JSON instead of raw file)
            if content.startswith("{") and '"message":' in content:
                try:
                    error_data = json.loads(content)
                    if "message" in error_data:
                        raise ValueError(f"GitLab API error: {error_data['message']}")
                except json.JSONDecodeError:
                    pass

            return content

        except Exception as e:
            raise ValueError(f"Failed to get file content: {str(e)}")
    
    def _get_bitbucket_file_content(self, repo_url: str, file_path: str, access_token: str = None) -> str:
        """Internal method to get Bitbucket file content."""
        try:
            # Extract owner and repo name from Bitbucket URL
            if not (repo_url.startswith("https://bitbucket.org/") or repo_url.startswith("http://bitbucket.org/")):
                raise ValueError("Not a valid Bitbucket repository URL")

            parts = repo_url.rstrip('/').split('/')
            if len(parts) < 5:
                raise ValueError("Invalid Bitbucket URL format")

            owner = parts[-2]
            repo = parts[-1].replace(".git", "")

            # Try to get the default branch from the repository info
            default_branch = None
            try:
                repo_info_url = f"https://api.bitbucket.org/2.0/repositories/{owner}/{repo}"
                repo_headers = {}
                if access_token:
                    repo_headers["Authorization"] = f"Bearer {access_token}"
                
                repo_response = requests.get(repo_info_url, headers=repo_headers)
                if repo_response.status_code == 200:
                    repo_data = repo_response.json()
                    default_branch = repo_data.get('mainbranch', {}).get('name', 'main')
                    self.logger.info(f"Found default branch: {default_branch}")
                else:
                    self.logger.warning(f"Could not fetch repository info, using 'main' as default branch")
                    default_branch = 'main'
            except Exception as e:
                self.logger.warning(f"Error fetching repository info: {e}, using 'main' as default branch")
                default_branch = 'main'

            # Use Bitbucket API to get file content
            api_url = f"https://api.bitbucket.org/2.0/repositories/{owner}/{repo}/src/{default_branch}/{file_path}"

            # Fetch file content from Bitbucket API
            headers = {}
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
            self.logger.info(f"Fetching file content from Bitbucket API: {api_url}")
            
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                content = response.text
            elif response.status_code == 404:
                raise ValueError("File not found on Bitbucket. Please check the file path and repository.")
            elif response.status_code == 401:
                raise ValueError("Unauthorized access to Bitbucket. Please check your access token.")
            elif response.status_code == 403:
                raise ValueError("Forbidden access to Bitbucket. You might not have permission to access this file.")
            elif response.status_code == 500:
                raise ValueError("Internal server error on Bitbucket. Please try again later.")
            else:
                response.raise_for_status()
                content = response.text
            return content

        except Exception as e:
            raise ValueError(f"Failed to get file content: {str(e)}")
    
    def extract_repo_name_from_url(self, repo_url_or_path: str, repo_type: str) -> str:
        """
        Extract owner and repo name to create unique identifier.

        Args:
            repo_url_or_path (str): The repository URL or path
            repo_type (str): The type of repository

        Returns:
            str: The extracted repository name
        """
        # Extract owner and repo name to create unique identifier
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
    
    def create_repository_structure(
        self, 
        repo_url_or_path: str, 
        repo_type: str = "github", 
        access_token: str = None
    ) -> Dict[str, str]:
        """
        Download and prepare all paths.
        Paths:
        ~/.adalflow/repos/{owner}_{repo_name} (for url, local path will be the same)
        ~/.adalflow/databases/{owner}_{repo_name}.pkl

        Args:
            repo_url_or_path (str): The URL or local path of the repository
            repo_type (str): The type of repository
            access_token (str, optional): Access token for private repositories

        Returns:
            Dict[str, str]: Dictionary containing repository paths
        """
        self.logger.info(f"Preparing repo storage for {repo_url_or_path}...")

        try:
            root_path = self._adalflow_root

            os.makedirs(root_path, exist_ok=True)
            # url
            if repo_url_or_path.startswith("https://") or repo_url_or_path.startswith("http://"):
                # Extract the repository name from the URL
                repo_name = self.extract_repo_name_from_url(repo_url_or_path, repo_type)
                self.logger.info(f"Extracted repo name: {repo_name}")

                save_repo_dir = os.path.join(root_path, "repos", repo_name)

                # Check if the repository directory already exists and is not empty
                if not (os.path.exists(save_repo_dir) and os.listdir(save_repo_dir)):
                    # Only download if the repository doesn't exist or is empty
                    self.download_repository(repo_url_or_path, save_repo_dir, repo_type, access_token)
                else:
                    self.logger.info(f"Repository already exists at {save_repo_dir}. Using existing repository.")
            else:  # local path
                repo_name = os.path.basename(repo_url_or_path)
                save_repo_dir = repo_url_or_path

            save_db_file = os.path.join(root_path, "databases", f"{repo_name}.pkl")
            os.makedirs(save_repo_dir, exist_ok=True)
            os.makedirs(os.path.dirname(save_db_file), exist_ok=True)

            repo_paths = {
                "save_repo_dir": save_repo_dir,
                "save_db_file": save_db_file,
            }
            self.logger.info(f"Repo paths: {repo_paths}")
            return repo_paths

        except Exception as e:
            self.logger.error(f"Failed to create repository structure: {e}")
            raise


# Factory functions for service creation
def get_project_service() -> ProjectService:
    """Get the singleton project service instance."""
    if not hasattr(get_project_service, '_instance'):
        get_project_service._instance = ProjectService()
    return get_project_service._instance


def create_project_service() -> ProjectService:
    """Create a new project service instance."""
    return ProjectService()
