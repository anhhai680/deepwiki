"""
Document Processor Component

Handles reading and processing various file types including code files and documentation files.
"""

import os
import glob
import logging
from typing import List, Optional
from adalflow.core.types import Document
from .token_counter import TokenCounter

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Handles reading and processing various file types from directories.
    """
    
    def __init__(self):
        self.token_counter = TokenCounter()
        # File extensions to look for, prioritizing code files
        self.code_extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".hpp", ".go", ".rs",
                               ".jsx", ".tsx", ".html", ".css", ".php", ".swift", ".cs"]
        self.doc_extensions = [".md", ".txt", ".rst", ".json", ".yaml", ".yml"]
    
    def read_all_documents(self, path: str, is_ollama_embedder: Optional[bool] = None, 
                          excluded_dirs: Optional[List[str]] = None, 
                          excluded_files: Optional[List[str]] = None,
                          included_dirs: Optional[List[str]] = None, 
                          included_files: Optional[List[str]] = None) -> List[Document]:
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
        from backend.core.config.settings import configs, DEFAULT_EXCLUDED_DIRS, DEFAULT_EXCLUDED_FILES
        
        documents = []
        
        # Determine filtering mode: inclusion or exclusion
        use_inclusion_mode = (included_dirs is not None and len(included_dirs) > 0) or (included_files is not None and len(included_files) > 0)

        if use_inclusion_mode:
            # Inclusion mode: only process specified directories and files
            final_included_dirs = set(included_dirs) if included_dirs else set()
            final_included_files = set(included_files) if included_files else set()

            logger.info(f"Using inclusion mode")
            logger.info(f"Included directories: {list(final_included_dirs)}")
            logger.info(f"Included files: {list(final_included_files)}")

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

            logger.info(f"Using exclusion mode")
            logger.info(f"Excluded directories: {excluded_dirs}")
            logger.info(f"Excluded files: {excluded_files}")

        logger.info(f"Reading documents from {path}")

        # Process code files first
        for ext in self.code_extensions:
            files = glob.glob(f"{path}/**/*{ext}", recursive=True)
            for file_path in files:
                # Check if file should be processed based on inclusion/exclusion rules
                if not self._should_process_file(file_path, use_inclusion_mode, included_dirs, included_files, excluded_dirs, excluded_files):
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
                        token_count = self.token_counter.count_tokens(content, is_ollama_embedder)
                        if self.token_counter.is_text_too_large(content, is_ollama_embedder, multiplier=10):
                            logger.warning(f"Skipping large file {relative_path}: Token count ({token_count}) exceeds limit")
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
                    logger.error(f"Error reading {file_path}: {e}")

        # Then process documentation files
        for ext in self.doc_extensions:
            files = glob.glob(f"{path}/**/*{ext}", recursive=True)
            for file_path in files:
                # Check if file should be processed based on inclusion/exclusion rules
                if not self._should_process_file(file_path, use_inclusion_mode, included_dirs, included_files, excluded_dirs, excluded_files):
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        relative_path = os.path.relpath(file_path, path)

                        # Check token count
                        token_count = self.token_counter.count_tokens(content, is_ollama_embedder)
                        if self.token_counter.is_text_too_large(content, is_ollama_embedder):
                            logger.warning(f"Skipping large file {relative_path}: Token count ({token_count}) exceeds limit")
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
                    logger.error(f"Error reading {file_path}: {e}")

        logger.info(f"Found {len(documents)} documents")
        return documents
    
    def _should_process_file(self, file_path: str, use_inclusion: bool, included_dirs: List[str], 
                           included_files: List[str], excluded_dirs: List[str], 
                           excluded_files: List[str]) -> bool:
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
