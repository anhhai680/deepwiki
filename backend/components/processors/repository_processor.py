"""
Repository Processor Component

Handles Git repository operations including cloning, file content retrieval, and repository management.
"""

import os
import subprocess
import json
import base64
import logging
import requests
from urllib.parse import urlparse, urlunparse, quote
from requests.exceptions import RequestException
from typing import Optional

logger = logging.getLogger(__name__)

class RepositoryProcessor:
    """
    Handles Git repository operations and file content retrieval.
    """
    
    def __init__(self):
        self.supported_types = ["github", "gitlab", "bitbucket"]
    
    def download_repo(self, repo_url: str, local_path: str, type: str = "github", 
                      access_token: Optional[str] = None) -> str:
        """
        Downloads a Git repository (GitHub, GitLab, or Bitbucket) to a specified local path.

        Args:
            repo_url (str): The URL of the Git repository to clone.
            local_path (str): The local directory where the repository will be cloned.
            type (str): Repository type (github, gitlab, bitbucket)
            access_token (str, optional): Access token for private repositories.

        Returns:
            str: The output message from the `git` command.
        """
        try:
            # Check if Git is installed
            logger.info(f"Preparing to clone repository to {local_path}")
            subprocess.run(
                ["git", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Check if repository already exists
            if os.path.exists(local_path) and os.listdir(local_path):
                # Directory exists and is not empty
                logger.warning(f"Repository already exists at {local_path}. Using existing repository.")
                return f"Using existing repository at {local_path}"

            # Ensure the local path exists
            os.makedirs(local_path, exist_ok=True)

            # Prepare the clone URL with access token if provided
            clone_url = repo_url
            if access_token:
                parsed = urlparse(repo_url)
                # Determine the repository type and format the URL accordingly
                if type == "github":
                    # Format: https://{token}@{domain}/owner/repo.git
                    # Works for both github.com and enterprise GitHub domains
                    clone_url = urlunparse((parsed.scheme, f"{access_token}@{parsed.netloc}", parsed.path, '', '', ''))
                elif type == "gitlab":
                    # Format: https://oauth2:{token}@gitlab.com/owner/repo.git
                    clone_url = urlunparse((parsed.scheme, f"oauth2:{access_token}@{parsed.netloc}", parsed.path, '', '', ''))
                elif type == "bitbucket":
                    # Format: https://x-token-auth:{token}@bitbucket.org/owner/repo.git
                    clone_url = urlunparse((parsed.scheme, f"x-token-auth:{access_token}@{parsed.netloc}", parsed.path, '', '', ''))

                logger.info("Using access token for authentication")

            # Clone the repository
            logger.info(f"Cloning repository from {repo_url} to {local_path}")
            # We use repo_url in the log to avoid exposing the token in logs
            result = subprocess.run(
                ["git", "clone", "--depth=1", "--single-branch", clone_url, local_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            logger.info("Repository cloned successfully")
            return result.stdout.decode("utf-8")

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8')
            # Sanitize error message to remove any tokens
            if access_token and access_token in error_msg:
                error_msg = error_msg.replace(access_token, "***TOKEN***")
            raise ValueError(f"Error during cloning: {error_msg}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred: {str(e)}")
    
    def get_github_file_content(self, repo_url: str, file_path: str, 
                               access_token: Optional[str] = None) -> str:
        """
        Retrieves the content of a file from a GitHub repository using the GitHub API.
        Supports both public GitHub (github.com) and GitHub Enterprise (custom domains).
        
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
            # The API endpoint for getting file content is: /repos/{owner}/{repo}/contents/{path}
            api_url = f"{api_base}/repos/{owner}/{repo}/contents/{file_path}"

            # Fetch file content from GitHub API
            headers = {}
            if access_token:
                headers["Authorization"] = f"token {access_token}"
            logger.info(f"Fetching file content from GitHub API: {api_url}")
            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()
            except RequestException as e:
                raise ValueError(f"Error fetching file content: {e}")
            try:
                content_data = response.json()
            except json.JSONDecodeError:
                raise ValueError("Invalid response from GitHub API")

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
    
    def get_gitlab_file_content(self, repo_url: str, file_path: str, 
                               access_token: Optional[str] = None) -> str:
        """
        Retrieves the content of a file from a GitLab repository (cloud or self-hosted).

        Args:
            repo_url (str): The GitLab repo URL (e.g., "https://gitlab.com/username/repo" or "http://localhost/group/project")
            file_path (str): File path within the repository (e.g., "src/main.py")
            access_token (str, optional): GitLab personal access token

        Returns:
            str: File content

        Raises:
            ValueError: If anything fails
        """
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
                    logger.info(f"Found default branch: {default_branch}")
                else:
                    logger.warning(f"Could not fetch project info, using 'main' as default branch")
                    default_branch = 'main'
            except Exception as e:
                logger.warning(f"Error fetching project info: {e}, using 'main' as default branch")
                default_branch = 'main'

            api_url = f"{gitlab_domain}/api/v4/projects/{encoded_project_path}/repository/files/{encoded_file_path}/raw?ref={default_branch}"
            # Fetch file content from GitLab API
            headers = {}
            if access_token:
                headers["PRIVATE-TOKEN"] = access_token
            logger.info(f"Fetching file content from GitLab API: {api_url}")
            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()
                content = response.text
            except RequestException as e:
                raise ValueError(f"Error fetching file content: {e}")

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
    
    def get_bitbucket_file_content(self, repo_url: str, file_path: str, 
                                  access_token: Optional[str] = None) -> str:
        """
        Retrieves the content of a file from a Bitbucket repository using the Bitbucket API.

        Args:
            repo_url (str): The URL of the Bitbucket repository (e.g., "https://bitbucket.org/username/repo")
            file_path (str): The path to the file within the repository (e.g., "src/main.py")
            access_token (str, optional): Bitbucket personal access token for private repositories

        Returns:
            str: The content of the file as a string
        """
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
                    logger.info(f"Found default branch: {default_branch}")
                else:
                    logger.warning(f"Could not fetch repository info, using 'main' as default branch")
                    default_branch = 'main'
            except Exception as e:
                logger.warning(f"Error fetching repository info: {e}, using 'main' as default branch")
                default_branch = 'main'

            # Use Bitbucket API to get file content
            # The API endpoint for getting file content is: /2.0/repositories/{owner}/{repo}/src/{branch}/{path}
            api_url = f"https://api.bitbucket.org/2.0/repositories/{owner}/{repo}/src/{default_branch}/{file_path}"

            # Fetch file content from Bitbucket API
            headers = {}
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
            logger.info(f"Fetching file content from Bitbucket API: {api_url}")
            try:
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
            except RequestException as e:
                raise ValueError(f"Error fetching file content: {e}")

        except Exception as e:
            raise ValueError(f"Failed to get file content: {str(e)}")
    
    def get_file_content(self, repo_url: str, file_path: str, type: str = "github", 
                        access_token: Optional[str] = None) -> str:
        """
        Retrieves the content of a file from a Git repository (GitHub, GitLab, or Bitbucket).

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
        if type == "github":
            return self.get_github_file_content(repo_url, file_path, access_token)
        elif type == "gitlab":
            return self.get_gitlab_file_content(repo_url, file_path, access_token)
        elif type == "bitbucket":
            return self.get_bitbucket_file_content(repo_url, file_path, access_token)
        else:
            raise ValueError(f"Unsupported repository type: {type}. Supported types: {self.supported_types}")
    
    def extract_repo_name_from_url(self, repo_url_or_path: str, repo_type: str) -> str:
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
