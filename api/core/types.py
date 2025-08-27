"""
Common type definitions for the DeepWiki API.

This module contains type definitions extracted
from existing code during the restructure.
"""

from typing import Dict, List, Optional, Union, Any, TypedDict, Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict


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


# AI model usage types
class CompletionUsage(BaseModel):
    """Model for completion usage statistics."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    completion_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


# Document processing types
class DocumentChunk(TypedDict, total=False):
    """Document chunk structure."""
    content: str
    metadata: Dict[str, Any]  # Use Dict instead of MetadataDict
    embedding: Optional[EmbeddingVector]
    chunk_id: str


class SearchResult(TypedDict, total=False):
    """Search result structure."""
    content: str
    score: float
    metadata: Dict[str, Any]  # Use Dict instead of MetadataDict
    source: str


# Structured types extracted from existing API models
class WikiPage(BaseModel):
    """Model for a wiki page."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str
    title: str
    content: str
    filePaths: List[str]
    importance: str  # Should ideally be Literal['high', 'medium', 'low']
    relatedPages: List[str]


class ProcessedProjectEntry(BaseModel):
    """Model for processed project entries."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str  # Filename
    owner: str
    repo: str
    name: str  # owner/repo
    repo_type: str  # Renamed from type to repo_type for clarity
    submittedAt: int  # Timestamp
    language: str  # Extracted from filename


class RepoInfo(BaseModel):
    """Model for repository information."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    owner: str
    repo: str
    type: str
    token: Optional[str] = None
    localPath: Optional[str] = None
    repoUrl: Optional[str] = None


class WikiSection(BaseModel):
    """Model for wiki sections."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str
    title: str
    pages: List[str]
    subsections: Optional[List[str]] = None


class WikiStructureModel(BaseModel):
    """Model for the overall wiki structure."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str
    title: str
    description: str
    pages: List[WikiPage]
    sections: Optional[List[WikiSection]] = None
    rootSections: Optional[List[str]] = None


class WikiCacheData(BaseModel):
    """Model for wiki cache data."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    wiki_structure: WikiStructureModel
    generated_pages: Dict[str, WikiPage]
    repo_url: Optional[str] = None  # Compatible for old cache
    repo: Optional[RepoInfo] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class WikiCacheRequest(BaseModel):
    """Model for wiki cache requests."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    repo: RepoInfo
    provider: str
    model: str
    language: str = "en"
    excluded_dirs: Optional[str] = None
    excluded_files: Optional[str] = None
    included_dirs: Optional[str] = None
    included_files: Optional[str] = None


class WikiCacheResponse(BaseModel):
    """Model for wiki cache responses."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool
    data: Optional[WikiCacheData] = None
    error: Optional[str] = None
    message: Optional[str] = None


class WikiGenerationRequest(BaseModel):
    """Model for wiki generation requests."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    repo: RepoInfo
    provider: str
    model: str
    language: str = "en"
    excluded_dirs: Optional[str] = None
    excluded_files: Optional[str] = None
    included_dirs: Optional[str] = None
    included_files: Optional[str] = None


class WikiGenerationResponse(BaseModel):
    """Model for wiki generation responses."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool
    data: Optional[WikiStructureModel] = None
    error: Optional[str] = None
    message: Optional[str] = None


class WikiPageRequest(BaseModel):
    """Model for wiki page requests."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    repo: RepoInfo
    provider: str
    model: str
    filePath: str
    language: str = "en"
    excluded_dirs: Optional[str] = None
    excluded_files: Optional[str] = None
    included_dirs: Optional[str] = None
    included_files: Optional[str] = None


class WikiPageResponse(BaseModel):
    """Model for wiki page responses."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool
    data: Optional[WikiPage] = None
    error: Optional[str] = None
    message: Optional[str] = None


class ChatRequest(BaseModel):
    """Model for chat requests."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    messages: List[Dict[str, str]]
    repo: Optional[RepoInfo] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    language: str = "en"
    excluded_dirs: Optional[str] = None
    excluded_files: Optional[str] = None
    included_dirs: Optional[str] = None
    included_files: Optional[str] = None


class ChatResponse(BaseModel):
    """Model for chat responses."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool
    data: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None


class SearchRequest(BaseModel):
    """Model for search requests."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    query: str
    repo: RepoInfo
    provider: str
    model: str
    language: str = "en"
    excluded_dirs: Optional[str] = None
    excluded_files: Optional[str] = None
    included_dirs: Optional[str] = None
    included_files: Optional[str] = None


class SearchResponse(BaseModel):
    """Model for search responses."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool
    data: Optional[List[SearchResult]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class ConfigurationRequest(BaseModel):
    """Model for configuration requests."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    config_type: str
    config_data: Dict[str, Any]


class ConfigurationResponse(BaseModel):
    """Model for configuration responses."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Model for health check responses."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    status: str
    timestamp: datetime
    version: str
    uptime: float


class ErrorResponse(BaseModel):
    """Model for error responses."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool = False
    error: str
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseModel):
    """Model for success responses."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None


class ProviderConfig(BaseModel):
    """Model for provider configuration."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    type: str
    config: Dict[str, Any]
    enabled: bool = True
    priority: int = 0


class ModelConfig(BaseModel):
    """Model for model configuration."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    provider: str
    type: str
    config: Dict[str, Any]
    enabled: bool = True
    priority: int = 0


class SystemConfig(BaseModel):
    """Model for system configuration."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    providers: List[ProviderConfig]
    models: List[ModelConfig]
    defaultProvider: str


class AuthorizationConfig(BaseModel):
    """Model for authorization configuration."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    code: str


# Chat and conversation types
class ChatMessage(BaseModel):
    """Model for chat messages."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    role: str
    content: str


class ChatRequest(BaseModel):
    """Model for chat requests."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
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


# Provider-specific types
class ProviderResponse(TypedDict, total=False):
    """Provider response structure."""
    content: str
    model: str
    usage: Dict[str, Any]
    metadata: Dict[str, Any]  # Use Dict instead of MetadataDict


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
    metadata: Dict[str, Any]  # Use Dict instead of MetadataDict
