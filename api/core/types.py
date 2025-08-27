"""
Common type definitions for the DeepWiki API.

This module contains type definitions extracted
from existing code during the restructure.
"""

from typing import Dict, List, Optional, Union, Any, TypedDict, Literal
from datetime import datetime
from pydantic import BaseModel


# Basic types that will be populated during restructure
class EmbeddingVector(List[float]):
    """Type alias for embedding vectors."""
    pass


class MetadataDict(Dict[str, Any]):
    """Type alias for metadata dictionaries."""
    pass


class ConversationId(str):
    """Type alias for conversation identifiers."""
    pass


class ProjectId(str):
    """Type alias for project identifiers."""
    pass


class UserId(str):
    """Type alias for user identifiers."""
    pass


# Structured types extracted from existing API models
class WikiPage(BaseModel):
    """Model for a wiki page."""
    id: str
    title: str
    content: str
    filePaths: List[str]
    importance: str  # Should ideally be Literal['high', 'medium', 'low']
    relatedPages: List[str]


class ProcessedProjectEntry(BaseModel):
    """Model for processed project entries."""
    id: str  # Filename
    owner: str
    repo: str
    name: str  # owner/repo
    repo_type: str  # Renamed from type to repo_type for clarity
    submittedAt: int  # Timestamp
    language: str  # Extracted from filename


class RepoInfo(BaseModel):
    """Model for repository information."""
    owner: str
    repo: str
    type: str
    token: Optional[str] = None
    localPath: Optional[str] = None
    repoUrl: Optional[str] = None


class WikiSection(BaseModel):
    """Model for wiki sections."""
    id: str
    title: str
    pages: List[str]
    subsections: Optional[List[str]] = None


class WikiStructureModel(BaseModel):
    """Model for the overall wiki structure."""
    id: str
    title: str
    description: str
    pages: List[WikiPage]
    sections: Optional[List[WikiSection]] = None
    rootSections: Optional[List[str]] = None


class WikiCacheData(BaseModel):
    """Model for wiki cache data."""
    wiki_structure: WikiStructureModel
    generated_pages: Dict[str, WikiPage]
    repo_url: Optional[str] = None  # Compatible for old cache
    repo: Optional[RepoInfo] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class WikiCacheRequest(BaseModel):
    """Model for wiki cache requests."""
    repo: RepoInfo
    language: str
    wiki_structure: WikiStructureModel
    generated_pages: Dict[str, WikiPage]
    provider: str
    model: str


class WikiExportRequest(BaseModel):
    """Model for wiki export requests."""
    repo_url: str
    pages: List[WikiPage]
    format: Literal["markdown", "json"]


class Model(BaseModel):
    """Model for LLM model configuration."""
    id: str
    name: str


class Provider(BaseModel):
    """Model for LLM provider configuration."""
    id: str
    name: str
    models: List[Model]
    supportsCustomModel: Optional[bool] = False


class ModelConfig(BaseModel):
    """Model for the entire model configuration."""
    providers: List[Provider]
    defaultProvider: str


class AuthorizationConfig(BaseModel):
    """Model for authorization configuration."""
    code: str


# Chat and conversation types
class ChatMessage(BaseModel):
    """Model for chat messages."""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Model for chat requests."""
    messages: List[ChatMessage]
    filePath: Optional[str] = None
    token: Optional[str] = None
    type: Optional[str] = "github"
    provider: Optional[str] = None
    model: Optional[str] = None
    language: Optional[str] = "en"
    excluded_dirs: Optional[str] = None
    excluded_files: Optional[str] = None
    included_dirs: Optional[str] = None
    included_files: Optional[str] = None


# Document processing types
class DocumentChunk(TypedDict, total=False):
    """Document chunk structure."""
    content: str
    metadata: MetadataDict
    embedding: Optional[EmbeddingVector]
    chunk_id: str


class SearchResult(TypedDict, total=False):
    """Search result structure."""
    content: str
    score: float
    metadata: MetadataDict
    source: str


# Provider-specific types
class ProviderResponse(TypedDict, total=False):
    """Provider response structure."""
    content: str
    model: str
    usage: Dict[str, Any]
    metadata: MetadataDict


# Configuration types
class GeneratorConfig(TypedDict, total=False):
    """Generator configuration structure."""
    default_provider: str
    providers: Dict[str, Any]


class EmbedderConfig(TypedDict, total=False):
    """Embedder configuration structure."""
    embedder: Dict[str, Any]
    embedder_ollama: Optional[Dict[str, Any]]
    retriever: Optional[Dict[str, Any]]
    text_splitter: Optional[Dict[str, Any]]


class RepoConfig(TypedDict, total=False):
    """Repository configuration structure."""
    file_filters: Optional[Dict[str, Any]]
    repository: Optional[Dict[str, Any]]


class LangConfig(TypedDict, total=False):
    """Language configuration structure."""
    supported_languages: Dict[str, str]
    default: str


# File processing types
class FileInfo(TypedDict, total=False):
    """File information structure."""
    path: str
    content: str
    size: int
    modified: datetime
    language: Optional[str]


class ProcessingResult(TypedDict, total=False):
    """Processing result structure."""
    success: bool
    data: Optional[Any]
    error: Optional[str]
    metadata: MetadataDict
