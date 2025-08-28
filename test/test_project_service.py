"""
Test file for ProjectService.

This module tests the project service functionality to ensure it works correctly
after extraction from data_pipeline.py.
"""

import pytest
from api.services.project_service import ProjectService, get_project_service, create_project_service


class TestProjectService:
    """Test cases for ProjectService."""
    
    def test_project_service_initialization(self):
        """Test that ProjectService initializes correctly."""
        service = ProjectService()
        assert service.logger is not None
        assert service._adalflow_root is not None
    
    def test_singleton_pattern(self):
        """Test that get_project_service returns the same instance."""
        service1 = get_project_service()
        service2 = get_project_service()
        assert service1 is service2
    
    def test_create_project_service(self):
        """Test that create_project_service creates new instances."""
        service1 = create_project_service()
        service2 = create_project_service()
        assert service1 is not service2
    
    def test_extract_repo_name_from_url_github(self):
        """Test GitHub repository name extraction."""
        service = ProjectService()
        repo_url = "https://github.com/owner/repo"
        result = service.extract_repo_name_from_url(repo_url, "github")
        assert result == "owner_repo"
    
    def test_extract_repo_name_from_url_local(self):
        """Test local path repository name extraction."""
        service = ProjectService()
        local_path = "/path/to/local/repo"
        result = service.extract_repo_name_from_url(local_path, "local")
        assert result == "repo"
    
    def test_get_file_content_unsupported_type(self):
        """Test that unsupported repository types raise ValueError."""
        service = ProjectService()
        with pytest.raises(ValueError, match="Unsupported repository URL"):
            service.get_file_content("https://unsupported.com/owner/repo", "file.txt", "unsupported")


if __name__ == "__main__":
    pytest.main([__file__])
