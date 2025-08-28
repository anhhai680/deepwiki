"""
Wiki-related Pydantic models.

This module contains all models related to wiki functionality including
pages, sections, structure, and cache operations.
"""

from typing import List, Optional, Dict, Literal, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .common import RepoInfo


class WikiPage(BaseModel):
    """
    Model for a wiki page.
    """
    id: str
    title: str
    content: str
    filePaths: List[str]
    importance: str  # Should ideally be Literal['high', 'medium', 'low']
    relatedPages: List[str]


class WikiSection(BaseModel):
    """
    Model for the wiki sections.
    """
    id: str
    title: str
    pages: List[str]
    subsections: Optional[List[str]] = None


class WikiStructureModel(BaseModel):
    """
    Model for the overall wiki structure.
    """
    id: str
    title: str
    description: str
    pages: List[WikiPage]
    sections: Optional[List[WikiSection]] = None
    rootSections: Optional[List[str]] = None


class WikiCacheData(BaseModel):
    """
    Model for the data to be stored in the wiki cache.
    """
    wiki_structure: WikiStructureModel
    generated_pages: Dict[str, WikiPage]
    repo_url: Optional[str] = None  # compatible for old cache
    repo: Optional["RepoInfo"] = None
    provider: Optional[str] = None
    model: Optional[str] = None

    class Config:
        # Enable arbitrary types for forward references
        arbitrary_types_allowed = True


class WikiCacheRequest(BaseModel):
    """
    Model for the request body when saving wiki cache.
    """
    repo: "RepoInfo"
    language: str
    wiki_structure: WikiStructureModel
    generated_pages: Dict[str, WikiPage]
    provider: str
    model: str

    class Config:
        # Enable arbitrary types for forward references
        arbitrary_types_allowed = True


class WikiExportRequest(BaseModel):
    """
    Model for requesting a wiki export.
    """
    repo_url: str = Field(..., description="URL of the repository")
    pages: List[WikiPage] = Field(..., description="List of wiki pages to export")
    format: Literal["markdown", "json"] = Field(..., description="Export format (markdown or json)")



