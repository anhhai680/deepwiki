"""
File Operations Utilities

This module contains utility functions for file operations, path handling, and file system operations
extracted from various components throughout the codebase.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def get_adalflow_default_root_path() -> str:
    """
    Get the default root path for adalflow configuration.
    
    Returns:
        str: Path to the adalflow configuration directory
    """
    return os.path.expanduser(os.path.join("~", ".adalflow"))


def get_wiki_cache_path(owner: str, repo: str, repo_type: str, language: str) -> str:
    """
    Generate the file path for a given wiki cache.
    
    Args:
        owner (str): Repository owner
        repo (str): Repository name
        repo_type (str): Repository type (e.g., github, gitlab)
        language (str): Language of the wiki content
        
    Returns:
        str: Full path to the wiki cache file
    """
    wiki_cache_dir = os.path.join(get_adalflow_default_root_path(), "wikicache")
    os.makedirs(wiki_cache_dir, exist_ok=True)
    
    filename = f"deepwiki_cache_{repo_type}_{owner}_{repo}_{language}.json"
    return os.path.join(wiki_cache_dir, filename)


def ensure_directory_exists(path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path (str): Directory path to ensure exists
    """
    os.makedirs(path, exist_ok=True)


def get_file_extension(file_path: str) -> str:
    """
    Extract the file extension from a file path.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File extension (without the dot)
    """
    return Path(file_path).suffix.lstrip('.')


def get_file_name(file_path: str) -> str:
    """
    Extract the file name from a file path.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File name with extension
    """
    return Path(file_path).name


def get_file_name_without_extension(file_path: str) -> str:
    """
    Extract the file name without extension from a file path.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File name without extension
    """
    return Path(file_path).stem


def get_directory_path(file_path: str) -> str:
    """
    Extract the directory path from a file path.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Directory path
    """
    return str(Path(file_path).parent)


def is_file_readable(file_path: str) -> bool:
    """
    Check if a file is readable.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file is readable, False otherwise
    """
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)


def is_directory_writable(dir_path: str) -> bool:
    """
    Check if a directory is writable.
    
    Args:
        dir_path (str): Path to the directory
        
    Returns:
        bool: True if directory is writable, False otherwise
    """
    return os.path.isdir(dir_path) and os.access(dir_path, os.W_OK)


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        int: File size in bytes, -1 if file doesn't exist or can't be accessed
    """
    try:
        return os.path.getsize(file_path)
    except (OSError, IOError):
        return -1


def get_file_modified_time(file_path: str) -> float:
    """
    Get the last modified time of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        float: Last modified time as timestamp, -1 if file doesn't exist or can't be accessed
    """
    try:
        return os.path.getmtime(file_path)
    except (OSError, IOError):
        return -1


def list_files_in_directory(dir_path: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    List all files in a directory, optionally filtered by extension.
    
    Args:
        dir_path (str): Path to the directory
        extensions (List[str], optional): List of file extensions to include
        
    Returns:
        List[str]: List of file paths
    """
    if not os.path.isdir(dir_path):
        return []
    
    files = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            if extensions is None or get_file_extension(item_path) in extensions:
                files.append(item_path)
    
    return files


def list_directories_in_directory(dir_path: str) -> List[str]:
    """
    List all subdirectories in a directory.
    
    Args:
        dir_path (str): Path to the directory
        
    Returns:
        List[str]: List of directory paths
    """
    if not os.path.isdir(dir_path):
        return []
    
    directories = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path):
            directories.append(item_path)
    
    return directories


def find_files_recursively(root_path: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    Recursively find all files in a directory tree, optionally filtered by extension.
    
    Args:
        root_path (str): Root directory to search
        extensions (List[str], optional): List of file extensions to include
        
    Returns:
        List[str]: List of file paths
    """
    if not os.path.isdir(root_path):
        return []
    
    files = []
    for root, dirs, filenames in os.walk(root_path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            if extensions is None or get_file_extension(file_path) in extensions:
                files.append(file_path)
    
    return files


def should_process_file(file_path: str, excluded_dirs: List[str], excluded_files: List[str],
                       included_dirs: Optional[List[str]] = None, 
                       included_files: Optional[List[str]] = None) -> bool:
    """
    Determine if a file should be processed based on inclusion/exclusion rules.
    
    Args:
        file_path (str): Path to the file
        excluded_dirs (List[str]): List of directory patterns to exclude
        excluded_files (List[str]): List of file patterns to exclude
        included_dirs (List[str], optional): List of directory patterns to include exclusively
        included_files (List[str], optional): List of file patterns to include exclusively
        
    Returns:
        bool: True if file should be processed, False otherwise
    """
    file_path_normalized = file_path.replace('\\', '/')
    
    # Check inclusion rules first (if specified, only process included items)
    if included_dirs or included_files:
        use_inclusion = True
    else:
        use_inclusion = False
    
    if use_inclusion:
        # Check if file is in any included directory
        if included_dirs:
            in_included_dir = any(
                any(pattern in file_path_normalized for pattern in dir_patterns)
                for dir_patterns in included_dirs
            )
            if not in_included_dir:
                return False
        
        # Check if file matches any included file pattern
        if included_files:
            matches_included_file = any(
                any(pattern in file_path_normalized for pattern in file_patterns)
                for file_patterns in included_files
            )
            if not matches_included_file:
                return False
    
    # Check exclusion rules
    # Exclude if file is in any excluded directory
    for dir_patterns in excluded_dirs:
        if any(pattern in file_path_normalized for pattern in dir_patterns):
            return False
    
    # Exclude if file matches any excluded file pattern
    for file_patterns in excluded_files:
        if any(pattern in file_path_normalized for pattern in file_patterns):
            return False
    
    return True


def extract_repo_name_from_url(repo_url_or_path: str, repo_type: str = "github") -> str:
    """
    Extract repository name from a repository URL or path.
    
    Args:
        repo_url_or_path (str): Repository URL or local path
        repo_type (str): Repository type (github, gitlab, bitbucket, local)
        
    Returns:
        str: Repository name
    """
    if repo_type == "local":
        # For local paths, extract the last directory name
        return os.path.basename(os.path.normpath(repo_url_or_path))
    
    try:
        # Parse the URL
        parsed = urlparse(repo_url_or_path)
        
        # Extract path components
        path_parts = [part for part in parsed.path.split('/') if part]
        
        if len(path_parts) >= 2:
            # Format: /owner/repo or /owner/repo.git
            repo_name = path_parts[1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            return repo_name
        elif len(path_parts) == 1:
            # Format: /repo or /repo.git
            repo_name = path_parts[0]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            return repo_name
        else:
            # Fallback: use the last part of the path
            return os.path.basename(repo_url_or_path)
    
    except Exception as e:
        logger.warning(f"Error parsing repository URL {repo_url_or_path}: {e}")
        # Fallback: use the last part of the path
        return os.path.basename(repo_url_or_path)


def create_safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing or replacing invalid characters.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Safe filename
    """
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    safe_filename = filename
    for char in invalid_chars:
        safe_filename = safe_filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    safe_filename = safe_filename.strip(' .')
    
    # Ensure filename is not empty
    if not safe_filename:
        safe_filename = "unnamed_file"
    
    return safe_filename


def get_relative_path(file_path: str, base_path: str) -> str:
    """
    Get the relative path of a file from a base directory.
    
    Args:
        file_path (str): Path to the file
        base_path (str): Base directory path
        
    Returns:
        str: Relative path from base directory
    """
    try:
        return os.path.relpath(file_path, base_path)
    except ValueError:
        # If paths are on different drives (Windows), return the absolute path
        return file_path


def normalize_path(path: str) -> str:
    """
    Normalize a file path by resolving relative components and normalizing separators.
    
    Args:
        path (str): Path to normalize
        
    Returns:
        str: Normalized path
    """
    return os.path.normpath(path.replace('\\', '/'))


def is_subdirectory(path: str, parent_path: str) -> bool:
    """
    Check if a path is a subdirectory of a parent path.
    
    Args:
        path (str): Path to check
        parent_path (str): Parent directory path
        
    Returns:
        bool: True if path is a subdirectory of parent_path
    """
    try:
        path = os.path.realpath(path)
        parent_path = os.path.realpath(parent_path)
        return path.startswith(parent_path + os.sep)
    except (OSError, ValueError):
        return False
