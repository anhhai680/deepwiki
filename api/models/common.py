"""
Common Pydantic models.

This module contains models that are used across multiple domains
and don't belong to a specific functional area.
"""

from typing import Optional
from pydantic import BaseModel


class RepoInfo(BaseModel):
    """
    Model for repository information.
    """
    owner: str
    repo: str
    type: str
    token: Optional[str] = None
    localPath: Optional[str] = None
    repoUrl: Optional[str] = None


class ProcessedProjectEntry(BaseModel):
    """
    Model for processed project entries.
    """
    id: str  # Filename
    owner: str
    repo: str
    name: str  # owner/repo
    repo_type: str  # Renamed from type to repo_type for clarity with existing models
    submittedAt: int  # Timestamp
    language: str  # Extracted from filename
