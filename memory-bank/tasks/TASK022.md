# TASK022: Phase 1.2: Extend Existing Models

## Task Information
- **Task ID**: TASK022
- **Task Name**: Phase 1.2: Extend Existing Models
- **Status**: 🔴 Not Started
- **Progress**: 0%
- **Phase**: Week 1-2
- **Priority**: 🟡 Medium
- **Created**: 2024-12-19
- **Estimated Duration**: 4-6 days

## Task Description
Extend existing models to support multiple repositories while maintaining 100% backward compatibility. This task focuses on enhancing the existing `ChatCompletionRequest` and `RepoInfo` models to support multi-repository functionality through inheritance and composition.

## Original Request
Based on Implementation Phases section in multiple-repositories-implementation-plan-corrected.md document. Each sub-heading in the phases should create as a task instead of a large task.

## Thought Process
The implementation plan emphasizes extending existing models rather than replacing them. This approach ensures backward compatibility while adding new functionality. The models will use inheritance and composition to add multi-repository support without breaking existing single-repository functionality.

## Implementation Plan

### 1. Extend ChatCompletionRequest Model
- **File**: `backend/models/chat.py` (extend existing)
- **Purpose**: Support multiple repositories while maintaining backward compatibility
- **Approach**: Create new models that extend existing ones

### 2. Create RepositoryInfo Model
- **File**: `backend/models/chat.py` (extend existing)
- **Purpose**: Enhanced repository information extending existing RepoInfo
- **Approach**: Inherit from existing RepoInfo and add new fields

### 3. Create MultiRepositoryRequest Model
- **File**: `backend/models/chat.py` (extend existing)
- **Purpose**: New request model supporting multiple repositories
- **Approach**: Feature flag protected with backward compatibility

### 4. Enhance RepoInfo Model
- **File**: `backend/models/common.py` (extend existing)
- **Purpose**: Add additional fields for advanced repository configuration
- **Approach**: Extend existing fields without breaking changes

## Technical Specifications

### Enhanced Data Models (Extending Existing)

```python
# backend/models/chat.py - EXTEND EXISTING
from typing import Optional, List, Union
from pydantic import BaseModel, Field, validator
from .common import RepoInfo

class RepositoryInfo(RepoInfo):
    """Enhanced repository information extending existing RepoInfo"""
    # Inherit existing fields: owner, repo, type, token, localPath, repoUrl
    
    # New fields for multi-repository support
    alias: Optional[str] = Field(None, description="User-friendly repository alias")
    description: Optional[str] = Field(None, description="Repository description")
    priority_weight: float = Field(default=1.0, description="Repository priority weight")
    
    # Enhanced filtering (extending existing fields)
    excluded_dirs: Optional[str] = Field(None, description="Excluded directories (comma-separated)")
    excluded_files: Optional[str] = Field(None, description="Excluded files (comma-separated)")
    included_dirs: Optional[str] = Field(None, description="Included directories (comma-separated)")
    included_files: Optional[str] = Field(None, description="Included files (comma-separated)")

class MultiRepositoryRequest(BaseModel):
    """Enhanced request model supporting multiple repositories"""
    repositories: List[RepositoryInfo] = Field(..., description="Repository list")
    messages: List[ChatMessage] = Field(..., description="Chat messages")
    
    # Context configuration
    max_total_context: int = Field(default=8000, description="Maximum total context tokens")
    repository_balance: str = Field(default="equal", description="Repository context balancing strategy")
    
    # AI configuration (extending existing fields)
    provider: str = Field("google", description="AI model provider")
    model: Optional[str] = Field(None, description="AI model name")
    language: str = Field("en", description="Response language")
    
    @validator('repositories', mode='before')
    @classmethod
    def validate_repositories(cls, v):
        """Backward compatibility validator"""
        if isinstance(v, str):
            # Single repository URL - convert to RepositoryInfo
            return [RepositoryInfo.from_url(v)]
        elif isinstance(v, dict):
            # Single repository dict - convert to RepositoryInfo
            return [RepositoryInfo(**v)]
        return v
```

### Backward Compatibility Requirements
- Existing `ChatCompletionRequest` must remain unchanged
- New requests can use `MultiRepositoryRequest` for multiple repositories
- Single repository requests must continue working exactly as before
- All existing API endpoints must continue functioning

## Subtasks

### Subtask 1: Extend ChatCompletionRequest
- [ ] Analyze existing ChatCompletionRequest structure
- [ ] Create RepositoryInfo model extending RepoInfo
- [ ] Add new fields for multi-repository support
- [ ] Ensure backward compatibility
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 2: Create MultiRepositoryRequest
- [ ] Design MultiRepositoryRequest model structure
- [ ] Implement backward compatibility validator
- [ ] Add context configuration fields
- [ ] Add AI configuration fields
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 3: Enhance RepoInfo Model
- [ ] Extend existing RepoInfo fields
- [ ] Add RepositoryConfiguration for advanced settings
- [ ] Maintain backward compatibility with existing fields
- [ ] Add validation for new fields
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 4: Model Testing and Validation
- [ ] Test backward compatibility with existing requests
- [ ] Test new multi-repository functionality
- [ ] Validate model serialization/deserialization
- [ ] Test validation rules and error handling
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

## Dependencies
- TASK021: Phase 1.1: Feature Flag Infrastructure (for feature flag integration)

## Deliverables
1. Enhanced `backend/models/chat.py` with new models
2. Enhanced `backend/models/common.py` with extended RepoInfo
3. Unit tests for all new models
4. Backward compatibility validation tests
5. Model documentation and usage examples

## Success Criteria
- [ ] All existing models continue working unchanged
- [ ] New multi-repository models are fully functional
- [ ] Backward compatibility is 100% maintained
- [ ] All validation rules work correctly
- [ ] All tests pass
- [ ] Documentation is complete and clear

## Progress Log

### 2024-12-19 - Task Created
- Task created based on Implementation Phases section
- Implementation plan defined
- Subtasks identified and structured
- Dependencies identified

## Notes
- Must maintain 100% backward compatibility
- New models should extend existing ones, not replace them
- Feature flag integration will be added in later tasks
- All existing API endpoints must continue functioning
- Testing should focus on both new functionality and backward compatibility
