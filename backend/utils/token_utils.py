"""
Token Utilities

This module contains utility functions for token counting, estimation, and token-related operations
extracted from various components throughout the codebase.
"""

import tiktoken
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


def count_tokens(text: str, is_ollama_embedder: Optional[bool] = None) -> int:
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
            try:
                from backend.core.config.settings import is_ollama_embedder as check_ollama
                is_ollama_embedder = check_ollama()
            except ImportError:
                # Fallback to default if config is not available
                is_ollama_embedder = False

        if is_ollama_embedder:
            encoding = tiktoken.get_encoding("cl100k_base")
        else:
            encoding = tiktoken.encoding_for_model("text-embedding-3-small")

        return len(encoding.encode(text))
    except Exception as e:
        # Fallback to a simple approximation if tiktoken fails
        logger.warning(f"Error counting tokens with tiktoken: {e}")
        # Rough approximation: 4 characters per token
        return len(text) // 4


def estimate_token_count(text: str) -> int:
    """
    Estimate the token count of a given text using a simple heuristic.
    
    This is a fallback method when tiktoken is not available or fails.
    
    Args:
        text (str): The text to estimate token count for.

    Returns:
        int: Estimated token count.
    """
    # Split the text into tokens using spaces as a simple heuristic
    tokens = text.split()
    return len(tokens)


def is_text_too_large(text: str, is_ollama_embedder: Optional[bool] = None, 
                      multiplier: float = 1.0, max_tokens: int = 8192) -> bool:
    """
    Check if text exceeds token limits.
    
    Args:
        text (str): The text to check
        is_ollama_embedder (bool, optional): Whether using Ollama embeddings
        multiplier (float): Multiplier for the token limit (default: 1.0)
        max_tokens (int): Maximum token limit (default: 8192)
        
    Returns:
        bool: True if text exceeds limit, False otherwise
    """
    token_count = count_tokens(text, is_ollama_embedder)
    limit = int(max_tokens * multiplier)
    return token_count > limit


def get_token_usage_stats(text: str, is_ollama_embedder: Optional[bool] = None) -> Dict[str, Any]:
    """
    Get comprehensive token usage statistics for text.
    
    Args:
        text (str): The text to analyze
        is_ollama_embedder (bool, optional): Whether using Ollama embeddings
        
    Returns:
        Dict[str, Any]: Token usage statistics
    """
    token_count = count_tokens(text, is_ollama_embedder)
    char_count = len(text)
    word_count = len(text.split())
    line_count = len(text.splitlines())
    
    # Calculate token efficiency
    chars_per_token = char_count / token_count if token_count > 0 else 0
    words_per_token = word_count / token_count if token_count > 0 else 0
    
    return {
        "token_count": token_count,
        "character_count": char_count,
        "word_count": word_count,
        "line_count": line_count,
        "characters_per_token": round(chars_per_token, 2),
        "words_per_token": round(words_per_token, 2),
        "is_ollama_embedder": is_ollama_embedder
    }


def truncate_text_to_tokens(text: str, max_tokens: int, is_ollama_embedder: Optional[bool] = None) -> str:
    """
    Truncate text to fit within token limit while preserving word boundaries.
    
    Args:
        text (str): The text to truncate
        max_tokens (int): Maximum number of tokens allowed
        is_ollama_embedder (bool, optional): Whether using Ollama embeddings
        
    Returns:
        str: Truncated text that fits within token limit
    """
    if count_tokens(text, is_ollama_embedder) <= max_tokens:
        return text
    
    # Start with a conservative estimate and work backwards
    words = text.split()
    truncated_words = []
    current_tokens = 0
    
    for word in words:
        # Add space if not first word
        test_text = " ".join(truncated_words + [word])
        test_tokens = count_tokens(test_text, is_ollama_embedder)
        
        if test_tokens <= max_tokens:
            truncated_words.append(word)
            current_tokens = test_tokens
        else:
            break
    
    return " ".join(truncated_words)


def split_text_into_chunks(text: str, max_tokens_per_chunk: int, 
                          is_ollama_embedder: Optional[bool] = None,
                          overlap_tokens: int = 0) -> List[str]:
    """
    Split text into chunks that fit within token limits.
    
    Args:
        text (str): The text to split
        max_tokens_per_chunk (int): Maximum tokens per chunk
        is_ollama_embedder (bool, optional): Whether using Ollama embeddings
        overlap_tokens (int): Number of overlapping tokens between chunks
        
    Returns:
        List[str]: List of text chunks
    """
    if count_tokens(text, is_ollama_embedder) <= max_tokens_per_chunk:
        return [text]
    
    chunks = []
    words = text.split()
    current_chunk = []
    current_tokens = 0
    
    for word in words:
        # Test adding the word to current chunk
        test_text = " ".join(current_chunk + [word])
        test_tokens = count_tokens(test_text, is_ollama_embedder)
        
        if test_tokens <= max_tokens_per_chunk:
            current_chunk.append(word)
            current_tokens = test_tokens
        else:
            # Current chunk is full, save it
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            
            # Start new chunk with overlap
            if overlap_tokens > 0 and current_chunk:
                # Add some words from the end of previous chunk for overlap
                overlap_words = current_chunk[-overlap_tokens:] if overlap_tokens <= len(current_chunk) else current_chunk
                current_chunk = overlap_words + [word]
                current_tokens = count_tokens(" ".join(current_chunk), is_ollama_embedder)
            else:
                current_chunk = [word]
                current_tokens = count_tokens(word, is_ollama_embedder)
    
    # Add the last chunk if it has content
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


def get_token_distribution(text: str, is_ollama_embedder: Optional[bool] = None) -> Dict[str, Any]:
    """
    Analyze token distribution across different text segments.
    
    Args:
        text (str): The text to analyze
        is_ollama_embedder (bool, optional): Whether using Ollama embeddings
        
    Returns:
        Dict[str, Any]: Token distribution analysis
    """
    lines = text.splitlines()
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    sentences = [s.strip() for s in text.replace('\n', ' ').split('. ') if s.strip()]
    
    # Count tokens for each segment
    line_tokens = [count_tokens(line, is_ollama_embedder) for line in lines if line.strip()]
    paragraph_tokens = [count_tokens(para, is_ollama_embedder) for para in paragraphs]
    sentence_tokens = [count_tokens(sent, is_ollama_embedder) for sent in sentences]
    
    # Calculate statistics
    def safe_stats(token_list):
        if not token_list:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "total": 0}
        return {
            "count": len(token_list),
            "min": min(token_list),
            "max": max(token_list),
            "avg": round(sum(token_list) / len(token_list), 2),
            "total": sum(token_list)
        }
    
    return {
        "total_tokens": count_tokens(text, is_ollama_embedder),
        "lines": safe_stats(line_tokens),
        "paragraphs": safe_stats(paragraph_tokens),
        "sentences": safe_stats(sentence_tokens)
    }


def optimize_text_for_tokens(text: str, target_tokens: int, 
                           is_ollama_embedder: Optional[bool] = None,
                           strategy: str = "truncate") -> str:
    """
    Optimize text to match target token count using various strategies.
    
    Args:
        text (str): The text to optimize
        target_tokens (int): Target number of tokens
        is_ollama_embedder (bool, optional): Whether using Ollama embeddings
        strategy (str): Optimization strategy ("truncate", "chunk", "compress")
        
    Returns:
        str: Optimized text
    """
    current_tokens = count_tokens(text, is_ollama_embedder)
    
    if current_tokens <= target_tokens:
        return text
    
    if strategy == "truncate":
        return truncate_text_to_tokens(text, target_tokens, is_ollama_embedder)
    elif strategy == "chunk":
        chunks = split_text_into_chunks(text, target_tokens, is_ollama_embedder)
        return chunks[0] if chunks else text
    elif strategy == "compress":
        # Simple compression: remove extra whitespace and short words
        compressed = " ".join(word for word in text.split() if len(word) > 2)
        if count_tokens(compressed, is_ollama_embedder) <= target_tokens:
            return compressed
        else:
            return truncate_text_to_tokens(compressed, target_tokens, is_ollama_embedder)
    else:
        # Default to truncation
        return truncate_text_to_tokens(text, target_tokens, is_ollama_embedder)
