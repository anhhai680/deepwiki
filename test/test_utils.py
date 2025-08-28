"""
Test utilities for the utils package.

This module provides simple tests to verify that utility functions work correctly.
"""

import sys
import os

# Add the parent directory to the path so we can import the utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    # Text utilities
    count_paragraphs,
    has_markdown_content,
    has_yaml_content,
    has_json_content,
    calculate_readability_metrics,
    
    # File utilities
    get_file_extension,
    get_file_name,
    get_file_name_without_extension,
    create_safe_filename,
    
    # Validation utilities
    validate_language,
    validate_url,
    validate_email,
    
    # Token utilities
    estimate_token_count,
    
    # Configuration utilities
    merge_configs,
    
    # Response utilities
    create_error_response
)


def test_text_utilities():
    """Test text utility functions."""
    print("Testing text utilities...")
    
    # Test count_paragraphs
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    assert count_paragraphs(text) == 3, f"Expected 3 paragraphs, got {count_paragraphs(text)}"
    
    # Test has_markdown_content
    markdown_text = "# Title\n\n**Bold text** and *italic text*"
    assert has_markdown_content(markdown_text, "txt") == True, "Should detect markdown content"
    
    # Test has_yaml_content
    yaml_text = "name: test\nversion: 1.0\n  description: test description"
    assert has_yaml_content(yaml_text, "txt") == True, "Should detect YAML content"
    
    # Test has_json_content
    json_text = '{"name": "test", "version": "1.0"}'
    assert has_json_content(json_text, "txt") == True, "Should detect JSON content"
    
    # Test calculate_readability_metrics
    metrics = calculate_readability_metrics("This is a test sentence. This is another sentence.")
    assert metrics["total_words"] == 9, f"Expected 9 words, got {metrics['total_words']}"
    
    print("✅ Text utilities passed!")


def test_file_utilities():
    """Test file utility functions."""
    print("Testing file utilities...")
    
    # Test get_file_extension
    assert get_file_extension("test.txt") == "txt", "Should extract .txt extension"
    assert get_file_extension("test.file.txt") == "txt", "Should get last extension"
    
    # Test get_file_name
    assert get_file_name("/path/to/test.txt") == "test.txt", "Should get filename with extension"
    
    # Test get_file_name_without_extension
    assert get_file_name_without_extension("/path/to/test.txt") == "test", "Should get filename without extension"
    
    # Test create_safe_filename
    safe_name = create_safe_filename("file<>:\"/\\|?*.txt")
    assert "<>" not in safe_name, "Should remove invalid characters"
    
    print("✅ File utilities passed!")


def test_validation_utilities():
    """Test validation utility functions."""
    print("Testing validation utilities...")
    
    # Test validate_language
    assert validate_language("en") == "en", "Should accept valid language"
    assert validate_language("invalid") == "en", "Should fallback to default for invalid language"
    
    # Test validate_url
    assert validate_url("https://example.com") == True, "Should accept valid HTTPS URL"
    assert validate_url("http://localhost:8000") == True, "Should accept valid HTTP URL"
    assert validate_url("invalid-url") == False, "Should reject invalid URL"
    
    # Test validate_email
    assert validate_email("test@example.com") == True, "Should accept valid email"
    assert validate_email("invalid-email") == False, "Should reject invalid email"
    
    print("✅ Validation utilities passed!")


def test_token_utilities():
    """Test token utility functions."""
    print("Testing token utilities...")
    
    # Test estimate_token_count
    text = "This is a test sentence with multiple words."
    assert estimate_token_count(text) == 8, f"Expected 8 tokens, got {estimate_token_count(text)}"
    
    print("✅ Token utilities passed!")


def test_config_utilities():
    """Test configuration utility functions."""
    print("Testing configuration utilities...")
    
    # Test merge_configs
    base_config = {"a": 1, "b": {"c": 2}}
    override_config = {"b": {"c": 3}, "d": 4}
    merged = merge_configs(base_config, override_config)
    
    assert merged["a"] == 1, "Should preserve base config values"
    assert merged["b"]["c"] == 3, "Should override nested values"
    assert merged["d"] == 4, "Should add new values"
    
    print("✅ Configuration utilities passed!")


def test_response_utilities():
    """Test response utility functions."""
    print("Testing response utilities...")
    
    # Test create_error_response
    error_response = create_error_response("Test error", "test_provider", "test_error")
    
    assert error_response["content"] == "Error: Test error", "Should format error message"
    assert error_response["provider"] == "test_provider", "Should set provider"
    assert error_response["success"] == False, "Should indicate failure"
    
    print("✅ Response utilities passed!")


def run_all_tests():
    """Run all utility tests."""
    print("🧪 Running utility function tests...\n")
    
    try:
        test_text_utilities()
        test_file_utilities()
        test_validation_utilities()
        test_token_utilities()
        test_config_utilities()
        test_response_utilities()
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
