"""
Utility functions package.

This package contains common utility functions for
text processing, file operations, validation, token handling,
configuration management, and response processing.
"""

# Import all utility modules
from . import text_utils
from . import file_utils
from . import validation_utils
from . import token_utils
from . import config_utils
from . import response_utils

# Re-export commonly used functions for convenience
from .text_utils import (
    count_paragraphs,
    has_markdown_content,
    has_yaml_content,
    has_json_content,
    calculate_readability_metrics,
    check_encoding_issues,
    extract_text_metadata,
    analyze_text_file,
    filter_text_files,
    filter_by_file_type,
    clean_text_content,
    extract_text_sections
)

from .file_utils import (
    get_adalflow_default_root_path,
    get_wiki_cache_path,
    ensure_directory_exists,
    get_file_extension,
    get_file_name,
    get_file_name_without_extension,
    get_directory_path,
    is_file_readable,
    is_directory_writable,
    get_file_size,
    get_file_modified_time,
    list_files_in_directory,
    list_directories_in_directory,
    find_files_recursively,
    should_process_file,
    extract_repo_name_from_url,
    create_safe_filename,
    get_relative_path,
    normalize_path,
    is_subdirectory
)

from .validation_utils import (
    validate_language,
    validate_auth_code,
    validate_repository_config,
    validate_query_config,
    validate_documents,
    validate_embeddings,
    validate_pipeline_state,
    validate_input_data,
    validate_output_data,
    validate_file_path,
    validate_directory_path,
    validate_url,
    validate_email,
    validate_and_filter_embeddings
)

from .token_utils import (
    count_tokens,
    estimate_token_count,
    is_text_too_large,
    get_token_usage_stats,
    truncate_text_to_tokens,
    split_text_into_chunks,
    get_token_distribution,
    optimize_text_for_tokens
)

from .config_utils import (
    replace_env_placeholders,
    load_json_config,
    load_generator_config,
    load_embedder_config,
    load_repo_config,
    load_lang_config,
    get_config_value,
    set_config_value,
    merge_configs,
    validate_config_structure,
    get_environment_config,
    save_config_to_file,
    reload_config,
    get_config_summary
)

from .response_utils import (
    extract_response_text,
    parse_stream_response,
    handle_streaming_response,
    get_all_messages_content,
    extract_response_metadata,
    validate_response_format,
    normalize_response,
    format_response_for_output,
    create_error_response,
    merge_streaming_responses
)

# Version information
__version__ = "1.0.0"

# Package metadata
__author__ = "DeepWiki Development Team"
__description__ = "Utility functions for DeepWiki API"
__all__ = [
    # Text utilities
    "count_paragraphs",
    "has_markdown_content",
    "has_yaml_content",
    "has_json_content",
    "calculate_readability_metrics",
    "check_encoding_issues",
    "extract_text_metadata",
    "analyze_text_file",
    "filter_text_files",
    "filter_by_file_type",
    "clean_text_content",
    "extract_text_sections",
    
    # File utilities
    "get_adalflow_default_root_path",
    "get_wiki_cache_path",
    "ensure_directory_exists",
    "get_file_extension",
    "get_file_name",
    "get_file_name_without_extension",
    "get_directory_path",
    "is_file_readable",
    "is_directory_writable",
    "get_file_size",
    "get_file_modified_time",
    "list_files_in_directory",
    "list_directories_in_directory",
    "find_files_recursively",
    "should_process_file",
    "extract_repo_name_from_url",
    "create_safe_filename",
    "get_relative_path",
    "normalize_path",
    "is_subdirectory",
    
    # Validation utilities
    "validate_language",
    "validate_auth_code",
    "validate_repository_config",
    "validate_query_config",
    "validate_documents",
    "validate_embeddings",
    "validate_pipeline_state",
    "validate_input_data",
    "validate_output_data",
    "validate_file_path",
    "validate_directory_path",
    "validate_url",
    "validate_email",
    "validate_and_filter_embeddings",
    
    # Token utilities
    "count_tokens",
    "estimate_token_count",
    "is_text_too_large",
    "get_token_usage_stats",
    "truncate_text_to_tokens",
    "split_text_into_chunks",
    "get_token_distribution",
    "optimize_text_for_tokens",
    
    # Configuration utilities
    "replace_env_placeholders",
    "load_json_config",
    "load_generator_config",
    "load_embedder_config",
    "load_repo_config",
    "load_lang_config",
    "get_config_value",
    "set_config_value",
    "merge_configs",
    "validate_config_structure",
    "get_environment_config",
    "save_config_to_file",
    "reload_config",
    "get_config_summary",
    
    # Response utilities
    "extract_response_text",
    "parse_stream_response",
    "handle_streaming_response",
    "get_all_messages_content",
    "extract_response_metadata",
    "validate_response_format",
    "normalize_response",
    "format_response_for_output",
    "create_error_response",
    "merge_streaming_responses"
]
