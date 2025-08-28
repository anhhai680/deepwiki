"""
Token Counter Component

Handles token counting for different embedding models and provides fallback mechanisms.
"""

import tiktoken
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TokenCounter:
    """
    Handles token counting for different embedding models with fallback mechanisms.
    """
    
    def __init__(self):
        self.max_embedding_tokens = 8192
    
    def count_tokens(self, text: str, is_ollama_embedder: Optional[bool] = None) -> int:
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
                encoding = tiktoken.get_encoding("cl100k_base")
            else:
                encoding = tiktoken.encoding_for_model("text-embedding-3-small")

            return len(encoding.encode(text))
        except Exception as e:
            # Fallback to a simple approximation if tiktoken fails
            logger.warning(f"Error counting tokens with tiktoken: {e}")
            # Rough approximation: 4 characters per token
            return len(text) // 4
    
    def is_text_too_large(self, text: str, is_ollama_embedder: Optional[bool] = None, 
                          multiplier: float = 1.0) -> bool:
        """
        Check if text exceeds token limits.
        
        Args:
            text (str): The text to check
            is_ollama_embedder (bool, optional): Whether using Ollama embeddings
            multiplier (float): Multiplier for the token limit (default: 1.0)
            
        Returns:
            bool: True if text exceeds limit, False otherwise
        """
        token_count = self.count_tokens(text, is_ollama_embedder)
        limit = int(self.max_embedding_tokens * multiplier)
        return token_count > limit
