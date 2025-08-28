"""
Code Processor Component

Handles code-specific processing logic and analysis.
"""

import logging
from typing import Dict, Any, List
from adalflow.core.types import Document

logger = logging.getLogger(__name__)

class CodeProcessor:
    """
    Handles code-specific processing logic and analysis.
    """
    
    def __init__(self):
        self.test_file_patterns = ["test_", "app_", "test"]
    
    def analyze_code_file(self, content: str, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Analyze a code file and extract relevant metadata.
        
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
            "is_code": True,
            "is_implementation": self._is_implementation_file(file_path),
            "title": file_path,
            "lines_of_code": len(content.splitlines()),
            "character_count": len(content),
            "has_tests": self._has_test_content(content, file_path),
            "complexity_indicators": self._analyze_complexity(content)
        }
        
        return analysis
    
    def _is_implementation_file(self, file_path: str) -> bool:
        """
        Determine if a file is an implementation file (not a test file).
        
        Args:
            file_path (str): The file path to check
            
        Returns:
            bool: True if it's an implementation file, False otherwise
        """
        file_name = file_path.lower()
        
        # Check for test file patterns
        for pattern in self.test_file_patterns:
            if pattern in file_name:
                return False
        
        return True
    
    def _has_test_content(self, content: str, file_path: str) -> bool:
        """
        Check if the file contains test-related content.
        
        Args:
            content (str): The file content
            file_path (str): The file path
            
        Returns:
            bool: True if test content is detected, False otherwise
        """
        content_lower = content.lower()
        file_name_lower = file_path.lower()
        
        # Check file name patterns
        test_patterns = ["test", "spec", "specs", "specification"]
        for pattern in test_patterns:
            if pattern in file_name_lower:
                return True
        
        # Check content patterns
        test_content_patterns = [
            "def test_", "class test", "test(", "assert", "expect(", 
            "describe(", "it(", "should", "given(", "when(", "then("
        ]
        
        for pattern in test_content_patterns:
            if pattern in content_lower:
                return True
        
        return False
    
    def _analyze_complexity(self, content: str) -> Dict[str, Any]:
        """
        Analyze code complexity indicators.
        
        Args:
            content (str): The file content
            
        Returns:
            Dict[str, Any]: Complexity analysis results
        """
        lines = content.splitlines()
        
        # Count various complexity indicators
        complexity = {
            "total_lines": len(lines),
            "empty_lines": len([line for line in lines if not line.strip()]),
            "comment_lines": len([line for line in lines if line.strip().startswith(('#', '//', '/*', '*'))]),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith(('#', '//', '/*', '*'))]),
            "function_count": content.count("def "),
            "class_count": content.count("class "),
            "import_count": content.count("import ") + content.count("from "),
            "nested_levels": self._count_max_nesting(content)
        }
        
        # Calculate ratios
        if complexity["total_lines"] > 0:
            complexity["code_ratio"] = complexity["code_lines"] / complexity["total_lines"]
            complexity["comment_ratio"] = complexity["comment_lines"] / complexity["total_lines"]
        else:
            complexity["code_ratio"] = 0
            complexity["comment_ratio"] = 0
        
        return complexity
    
    def _count_max_nesting(self, content: str) -> int:
        """
        Count the maximum nesting level in the code.
        
        Args:
            content (str): The file content
            
        Returns:
            int: Maximum nesting level
        """
        max_nesting = 0
        current_nesting = 0
        
        for char in content:
            if char in '({[':
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif char in ')}]':
                current_nesting = max(0, current_nesting - 1)
        
        return max_nesting
    
    def create_code_document(self, content: str, file_path: str, file_type: str, 
                           token_count: int) -> Document:
        """
        Create a Document object for a code file with comprehensive metadata.
        
        Args:
            content (str): The file content
            file_path (str): The file path
            file_type (str): The file type/extension
            token_count (int): The token count for the content
            
        Returns:
            Document: A Document object with code-specific metadata
        """
        analysis = self.analyze_code_file(content, file_path, file_type)
        
        # Add token count to metadata
        analysis["token_count"] = token_count
        
        return Document(
            text=content,
            meta_data=analysis
        )
    
    def filter_code_files(self, documents: List[Document]) -> List[Document]:
        """
        Filter documents to only include code files.
        
        Args:
            documents (List[Document]): List of documents to filter
            
        Returns:
            List[Document]: Filtered list containing only code files
        """
        return [doc for doc in documents if doc.meta_data.get("is_code", False)]
    
    def filter_implementation_files(self, documents: List[Document]) -> List[Document]:
        """
        Filter documents to only include implementation files (exclude test files).
        
        Args:
            documents (List[Document]): List of documents to filter
            
        Returns:
            List[Document]: Filtered list containing only implementation files
        """
        return [doc for doc in documents if doc.meta_data.get("is_implementation", False)]
