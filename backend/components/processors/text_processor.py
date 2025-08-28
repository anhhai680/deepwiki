"""
Text Processor Component

Handles text-specific processing logic and analysis.
"""

import logging
from typing import Dict, Any, List
from adalflow.core.types import Document

logger = logging.getLogger(__name__)

class TextProcessor:
    """
    Handles text-specific processing logic and analysis.
    """
    
    def __init__(self):
        self.document_extensions = [".md", ".txt", ".rst", ".json", ".yaml", ".yml"]
    
    def analyze_text_file(self, content: str, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Analyze a text file and extract relevant metadata.
        
        Args:
            content (str): The file content
            file_path (str): The file path
            file_type (str): The file type/extension
            
        Returns:
            Dict[str, Any]: Analysis results and metadata
        """
        analysis = {
            "file_path": file_path,
            "type": file_type,
            "is_code": False,
            "is_implementation": False,
            "title": file_path,
            "lines_of_text": len(content.splitlines()),
            "character_count": len(content),
            "word_count": len(content.split()),
            "paragraph_count": self._count_paragraphs(content),
            "has_markdown": self._has_markdown_content(content, file_type),
            "has_yaml": self._has_yaml_content(content, file_type),
            "has_json": self._has_json_content(content, file_type),
            "readability_metrics": self._calculate_readability(content)
        }
        
        return analysis
    
    def _count_paragraphs(self, content: str) -> int:
        """
        Count the number of paragraphs in the text.
        
        Args:
            content (str): The text content
            
        Returns:
            int: Number of paragraphs
        """
        # Split by double newlines to count paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        return len(paragraphs)
    
    def _has_markdown_content(self, content: str, file_type: str) -> bool:
        """
        Check if the file contains Markdown content.
        
        Args:
            content (str): The file content
            file_type (str): The file type/extension
            
        Returns:
            bool: True if Markdown content is detected, False otherwise
        """
        if file_type in ["md", "markdown"]:
            return True
        
        # Check for Markdown patterns in content
        markdown_patterns = [
            "# ", "## ", "### ", "**", "*", "`", "```", "[", "](", 
            "> ", "- ", "1. ", "|", "---", "![", "<!--"
        ]
        
        for pattern in markdown_patterns:
            if pattern in content:
                return True
        
        return False
    
    def _has_yaml_content(self, content: str, file_type: str) -> bool:
        """
        Check if the file contains YAML content.
        
        Args:
            content (str): The file content
            file_type (str): The file type/extension
            
        Returns:
            bool: True if YAML content is detected, False otherwise
        """
        if file_type in ["yaml", "yml"]:
            return True
        
        # Check for YAML patterns in content
        yaml_patterns = [
            ":", "  ", "- ", "---", "...", "&", "*", "!", "|", ">", "<"
        ]
        
        # Simple heuristic: if file has many colons and indentation, likely YAML
        colon_count = content.count(":")
        indented_lines = len([line for line in content.splitlines() if line.startswith("  ")])
        
        return colon_count > 5 and indented_lines > 3
    
    def _has_json_content(self, content: str, file_type: str) -> bool:
        """
        Check if the file contains JSON content.
        
        Args:
            content (str): The file content
            file_type (str): The file type/extension
            
        Returns:
            bool: True if JSON content is detected, False otherwise
        """
        if file_type == "json":
            return True
        
        # Check for JSON patterns in content
        content_stripped = content.strip()
        return (content_stripped.startswith("{") and content_stripped.endswith("}")) or \
               (content_stripped.startswith("[") and content_stripped.endswith("]"))
    
    def _calculate_readability(self, content: str) -> Dict[str, Any]:
        """
        Calculate basic readability metrics for the text.
        
        Args:
            content (str): The text content
            
        Returns:
            Dict[str, Any]: Readability metrics
        """
        lines = content.splitlines()
        words = content.split()
        sentences = content.replace('\n', ' ').split('. ')
        
        # Filter out empty elements
        lines = [line for line in lines if line.strip()]
        words = [word for word in words if word.strip()]
        sentences = [sentence for sentence in sentences if sentence.strip()]
        
        metrics = {
            "total_lines": len(lines),
            "total_words": len(words),
            "total_sentences": len(sentences),
            "average_words_per_line": len(words) / len(lines) if lines else 0,
            "average_words_per_sentence": len(words) / len(sentences) if sentences else 0,
            "average_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0
        }
        
        return metrics
    
    def create_text_document(self, content: str, file_path: str, file_type: str, 
                           token_count: int) -> Document:
        """
        Create a Document object for a text file with comprehensive metadata.
        
        Args:
            content (str): The file content
            file_path (str): The file path
            file_type (str): The file type/extension
            token_count (int): The token count for the content
            
        Returns:
            Document: A Document object with text-specific metadata
        """
        analysis = self.analyze_text_file(content, file_path, file_type)
        
        # Add token count to metadata
        analysis["token_count"] = token_count
        
        return Document(
            text=content,
            meta_data=analysis
        )
    
    def filter_text_files(self, documents: List[Document]) -> List[Document]:
        """
        Filter documents to only include text files.
        
        Args:
            documents (List[Document]): List of documents to filter
            
        Returns:
            List[Document]: Filtered list containing only text files
        """
        return [doc for doc in documents if not doc.meta_data.get("is_code", False)]
    
    def filter_by_file_type(self, documents: List[Document], file_types: List[str]) -> List[Document]:
        """
        Filter documents by specific file types.
        
        Args:
            documents (List[Document]): List of documents to filter
            file_types (List[str]): List of file types to include
            
        Returns:
            List[Document]: Filtered list containing only specified file types
        """
        return [doc for doc in documents if doc.meta_data.get("type") in file_types]
    
    def extract_text_metadata(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata specifically for text processing.
        
        Args:
            content (str): The file content
            file_path (str): The file path
            
        Returns:
            Dict[str, Any]: Text-specific metadata
        """
        return {
            "file_path": file_path,
            "content_length": len(content),
            "line_count": len(content.splitlines()),
            "word_count": len(content.split()),
            "has_content": bool(content.strip()),
            "encoding_issues": self._check_encoding_issues(content)
        }
    
    def _check_encoding_issues(self, content: str) -> List[str]:
        """
        Check for potential encoding issues in the text.
        
        Args:
            content (str): The text content
            
        Returns:
            List[str]: List of detected encoding issues
        """
        issues = []
        
        # Check for common encoding problems
        if '\x00' in content:
            issues.append("null_bytes_detected")
        
        if '\ufffd' in content:
            issues.append("replacement_characters_detected")
        
        # Check for mixed encodings
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            issues.append("unicode_encoding_error")
        
        return issues
