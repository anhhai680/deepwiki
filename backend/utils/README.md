# DeepWiki Utilities Package

This package contains comprehensive utility functions extracted from various components throughout the DeepWiki codebase. The utilities are organized into logical modules for easy discovery and reuse.

## Overview

The utilities package provides common functionality for:
- **Text Processing**: Text analysis, content detection, and metadata extraction
- **File Operations**: Path handling, file system operations, and repository utilities
- **Validation**: Input validation, data validation, and format checking
- **Token Management**: Token counting, estimation, and optimization
- **Configuration**: Configuration loading, processing, and management
- **Response Processing**: AI provider response handling and normalization

## Module Structure

```
backend/utils/
├── __init__.py          # Main package exports
├── text_utils.py        # Text processing utilities
├── file_utils.py        # File operations utilities
├── validation_utils.py  # Validation utilities
├── token_utils.py       # Token management utilities
├── config_utils.py      # Configuration utilities
├── response_utils.py    # Response processing utilities
├── test_utils.py        # Test suite for utilities
└── README.md            # This documentation
```

## Quick Start

```python
from backend.utils import (
    # Text utilities
    count_paragraphs,
    has_markdown_content,
    analyze_text_file,
    
    # File utilities
    get_file_extension,
    extract_repo_name_from_url,
    
    # Validation utilities
    validate_language,
    validate_url,
    
    # Token utilities
    count_tokens,
    is_text_too_large,
    
    # Configuration utilities
    load_json_config,
    merge_configs,
    
    # Response utilities
    extract_response_text,
    normalize_response
)

# Example usage
text = "This is a test paragraph.\n\nThis is another paragraph."
paragraph_count = count_paragraphs(text)  # Returns 2

file_ext = get_file_extension("document.txt")  # Returns "txt"
is_valid = validate_url("https://example.com")  # Returns True
```

## Text Utilities (`text_utils.py`)

### Content Analysis
- `analyze_text_file()` - Comprehensive text file analysis
- `count_paragraphs()` - Count paragraphs in text
- `calculate_readability_metrics()` - Calculate readability statistics

### Content Detection
- `has_markdown_content()` - Detect Markdown formatting
- `has_yaml_content()` - Detect YAML content
- `has_json_content()` - Detect JSON content

### Text Processing
- `clean_text_content()` - Clean and normalize text
- `extract_text_sections()` - Extract sections based on markers
- `extract_text_metadata()` - Extract text-specific metadata

### Filtering
- `filter_text_files()` - Filter documents by text type
- `filter_by_file_type()` - Filter by specific file types

## File Utilities (`file_utils.py`)

### Path Operations
- `get_file_extension()` - Extract file extension
- `get_file_name()` - Get filename with extension
- `get_file_name_without_extension()` - Get filename without extension
- `get_directory_path()` - Extract directory path
- `normalize_path()` - Normalize file paths

### File System Operations
- `ensure_directory_exists()` - Create directories if needed
- `list_files_in_directory()` - List files with optional filtering
- `find_files_recursively()` - Recursive file search
- `should_process_file()` - Check file inclusion/exclusion rules

### Repository Utilities
- `extract_repo_name_from_url()` - Extract repository name from URL
- `get_adalflow_default_root_path()` - Get configuration root path
- `get_wiki_cache_path()` - Generate wiki cache file paths

### File Validation
- `is_file_readable()` - Check file readability
- `is_directory_writable()` - Check directory writability
- `get_file_size()` - Get file size in bytes
- `get_file_modified_time()` - Get last modified time

## Validation Utilities (`validation_utils.py`)

### Data Validation
- `validate_input_data()` - Validate input against expected types
- `validate_output_data()` - Validate output data
- `validate_documents()` - Validate document lists
- `validate_embeddings()` - Validate and filter embeddings

### Format Validation
- `validate_file_path()` - Validate file paths
- `validate_directory_path()` - Validate directory paths
- `validate_url()` - Validate URL format and scheme
- `validate_email()` - Validate email addresses

### Configuration Validation
- `validate_repository_config()` - Validate repository settings
- `validate_query_config()` - Validate query parameters
- `validate_pipeline_state()` - Validate pipeline state
- `validate_language()` - Validate language codes

### Specialized Validation
- `validate_auth_code()` - Validate authorization codes
- `validate_and_filter_embeddings()` - Validate embedding consistency

## Token Utilities (`token_utils.py`)

### Token Counting
- `count_tokens()` - Accurate token counting with tiktoken
- `estimate_token_count()` - Simple token estimation fallback
- `is_text_too_large()` - Check if text exceeds token limits

### Token Analysis
- `get_token_usage_stats()` - Comprehensive token statistics
- `get_token_distribution()` - Token distribution across text segments

### Text Optimization
- `truncate_text_to_tokens()` - Truncate text to fit token limit
- `split_text_into_chunks()` - Split text into token-limited chunks
- `optimize_text_for_tokens()` - Optimize text using various strategies

## Configuration Utilities (`config_utils.py`)

### Configuration Loading
- `load_json_config()` - Load JSON configuration files
- `load_generator_config()` - Load AI generator configuration
- `load_embedder_config()` - Load embedding configuration
- `load_repo_config()` - Load repository configuration
- `load_lang_config()` - Load language configuration

### Environment Processing
- `replace_env_placeholders()` - Replace ${ENV_VAR} placeholders
- `get_environment_config()` - Extract configuration from environment

### Configuration Management
- `get_config_value()` - Get values using dot notation paths
- `set_config_value()` - Set values using dot notation paths
- `merge_configs()` - Merge configuration dictionaries
- `validate_config_structure()` - Validate required configuration keys

### Advanced Features
- `save_config_to_file()` - Save configuration to JSON files
- `reload_config()` - Reload configuration with cache clearing
- `get_config_summary()` - Get configuration structure summary

## Response Utilities (`response_utils.py`)

### Response Extraction
- `extract_response_text()` - Extract text from AI provider responses
- `extract_response_metadata()` - Extract metadata from responses
- `parse_stream_response()` - Parse streaming response chunks

### Response Processing
- `handle_streaming_response()` - Handle complete streaming responses
- `get_all_messages_content()` - Extract content from multi-choice responses
- `merge_streaming_responses()` - Merge multiple response chunks

### Response Validation
- `validate_response_format()` - Validate response format
- `normalize_response()` - Normalize responses to common format
- `format_response_for_output()` - Format responses for different outputs

### Error Handling
- `create_error_response()` - Create standardized error responses

## Testing

The utilities package includes a comprehensive test suite in `test_utils.py`. Run the tests to verify functionality:

```bash
cd backend
python3 -c "import utils.test_utils; utils.test_utils.run_all_tests()"
```

## Usage Examples

### Text Processing
```python
from backend.utils import analyze_text_file, has_markdown_content

# Analyze a text file
content = "# Title\n\nThis is content with **bold** text."
analysis = analyze_text_file(content, "document.txt", "txt")
print(f"Has markdown: {analysis['has_markdown']}")
print(f"Word count: {analysis['word_count']}")

# Check for markdown content
is_markdown = has_markdown_content(content, "txt")
print(f"Is markdown: {is_markdown}")
```

### File Operations
```python
from backend.utils import (
    get_file_extension, 
    extract_repo_name_from_url,
    should_process_file
)

# Extract file information
ext = get_file_extension("config.yaml")  # "yaml"
repo_name = extract_repo_name_from_url("https://github.com/user/repo")  # "repo"

# Check file processing rules
should_process = should_process_file(
    "src/main.py",
    excluded_dirs=[["node_modules", "venv"]],
    excluded_files=[["*.log", "*.tmp"]]
)
```

### Validation
```python
from backend.utils import validate_url, validate_email, validate_repository_config

# Validate inputs
is_valid_url = validate_url("https://example.com")  # True
is_valid_email = validate_email("user@example.com")  # True

# Validate repository configuration
is_valid_repo = validate_repository_config(
    "https://github.com/user/repo",
    "github",
    "access_token_123"
)
```

### Token Management
```python
from backend.utils import count_tokens, is_text_too_large, truncate_text_to_tokens

# Count tokens
token_count = count_tokens("This is a test sentence.")

# Check size limits
is_too_large = is_text_too_large(text, max_tokens=100)

# Truncate if needed
truncated = truncate_text_to_tokens(long_text, max_tokens=1000)
```

### Configuration
```python
from backend.utils import load_json_config, get_config_value, merge_configs

# Load configuration
config = load_json_config("config.json")

# Get nested values
api_key = get_config_value(config, "api.keys.openai")

# Merge configurations
merged = merge_configs(base_config, override_config)
```

### Response Processing
```python
from backend.utils import extract_response_text, normalize_response

# Extract text from AI response
response = {"choices": [{"message": {"content": "Hello world"}}]}
text = extract_response_text("openai", response)  # "Hello world"

# Normalize response
normalized = normalize_response(response, "openai")
print(f"Content: {normalized['content']}")
print(f"Provider: {normalized['provider']}")
```

## Best Practices

1. **Import Specific Functions**: Import only the functions you need to avoid unnecessary dependencies
2. **Error Handling**: Always handle potential errors when using file operations
3. **Configuration**: Use environment variables for sensitive configuration
4. **Validation**: Validate inputs early in your processing pipeline
5. **Token Limits**: Check token limits before sending text to AI models
6. **Response Processing**: Use normalized responses for consistent handling

## Dependencies

The utilities package has minimal dependencies:
- `tiktoken` - For accurate token counting
- `pathlib` - For path operations (Python 3.4+)
- Standard library modules: `os`, `json`, `re`, `logging`, `typing`

## Contributing

When adding new utilities:
1. Place them in the appropriate module based on functionality
2. Add comprehensive docstrings with examples
3. Include type hints for all functions
4. Add tests to `test_utils.py`
5. Update the `__init__.py` exports
6. Update this README with usage examples

## License

This utilities package is part of the DeepWiki project and follows the same license terms.
