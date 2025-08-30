# TASK023: Phase 1.3: Repository Model Enhancement

## Task Information
- **Task ID**: TASK023
- **Task Name**: Phase 1.3: Repository Model Enhancement
- **Status**: 🔴 Not Started
- **Progress**: 0%
- **Phase**: Week 1-2
- **Priority**: 🟡 Medium
- **Created**: 2024-12-19
- **Estimated Duration**: 3-4 days

## Task Description
Enhance the existing `RepoInfo` model with additional fields for advanced repository configuration while maintaining backward compatibility. This task focuses on extending the repository model to support advanced filtering, configuration, and metadata without breaking existing functionality.

## Original Request
Based on Implementation Phases section in multiple-repositories-implementation-plan-corrected.md document. Each sub-heading in the phases should create as a task instead of a large task.

## Thought Process
The implementation plan emphasizes extending existing models rather than replacing them. This task will enhance the `RepoInfo` model with additional fields for advanced repository configuration, filtering, and metadata. The enhancements will be designed to maintain 100% backward compatibility while adding new capabilities.

## Implementation Plan

### 1. Enhance RepoInfo Model Fields
- **File**: `backend/models/common.py` (extend existing)
- **Purpose**: Add advanced repository configuration fields
- **Approach**: Extend existing fields without breaking changes

### 2. Add RepositoryConfiguration Model
- **File**: `backend/models/common.py` (extend existing)
- **Purpose**: Advanced repository settings and configuration
- **Approach**: Separate model for complex configuration options

### 3. Implement Advanced Filtering
- **File**: `backend/models/common.py` (extend existing)
- **Purpose**: Support for included/excluded directories and files
- **Approach**: String-based filtering with comma-separated values

### 4. Add Metadata and Description Fields
- **File**: `backend/models/common.py` (extend existing)
- **Purpose**: User-friendly repository information and descriptions
- **Approach**: Optional fields that don't affect existing functionality

## Technical Specifications

### Enhanced RepoInfo Model

```python
# backend/models/common.py - EXTEND EXISTING
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator

class RepositoryConfiguration(BaseModel):
    """Advanced repository configuration and settings"""
    
    # Filtering configuration
    excluded_dirs: Optional[str] = Field(None, description="Excluded directories (comma-separated)")
    excluded_files: Optional[str] = Field(None, description="Excluded files (comma-separated)")
    included_dirs: Optional[str] = Field(None, description="Included directories (comma-separated)")
    included_files: Optional[str] = Field(None, description="Included files (comma-separated)")
    
    # Processing configuration
    max_file_size_mb: Optional[int] = Field(None, description="Maximum file size to process (MB)")
    supported_extensions: Optional[str] = Field(None, description="Supported file extensions (comma-separated)")
    ignore_hidden_files: bool = Field(default=True, description="Ignore hidden files and directories")
    
    # Performance configuration
    parallel_processing: bool = Field(default=True, description="Enable parallel processing")
    chunk_size: Optional[int] = Field(None, description="Document chunk size for processing")
    
    @validator('excluded_dirs', 'excluded_files', 'included_dirs', 'included_files')
    @classmethod
    def validate_filter_patterns(cls, v):
        """Validate filter patterns for security and correctness"""
        if v is None:
            return v
        
        # Check for path traversal attempts
        if '..' in v or '//' in v:
            raise ValueError("Invalid filter pattern: path traversal not allowed")
        
        return v

class RepoInfo(BaseModel):
    """Enhanced repository information with advanced configuration"""
    
    # Existing fields (unchanged for backward compatibility)
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    type: str = Field(..., description="Repository type (github, gitlab, bitbucket, local)")
    token: Optional[str] = Field(None, description="Access token for private repositories")
    localPath: Optional[str] = Field(None, description="Local file path for local repositories")
    repoUrl: Optional[str] = Field(None, description="Repository URL")
    
    # New fields for enhanced functionality
    alias: Optional[str] = Field(None, description="User-friendly repository alias")
    description: Optional[str] = Field(None, description="Repository description")
    priority_weight: float = Field(default=1.0, description="Repository priority weight (1.0-10.0)")
    
    # Advanced configuration
    config: Optional[RepositoryConfiguration] = Field(None, description="Advanced repository configuration")
    
    # Metadata fields
    created_at: Optional[str] = Field(None, description="Repository creation timestamp")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    tags: Optional[str] = Field(None, description="Repository tags (comma-separated)")
    
    # Health and status fields
    is_active: bool = Field(default=True, description="Repository is active and accessible")
    last_health_check: Optional[str] = Field(None, description="Last health check timestamp")
    health_status: str = Field(default="unknown", description="Repository health status")
    
    @validator('priority_weight')
    @classmethod
    def validate_priority_weight(cls, v):
        """Validate priority weight is within acceptable range"""
        if v < 0.1 or v > 10.0:
            raise ValueError("Priority weight must be between 0.1 and 10.0")
        return v
    
    @validator('health_status')
    @classmethod
    def validate_health_status(cls, v):
        """Validate health status values"""
        valid_statuses = ['unknown', 'healthy', 'warning', 'error', 'unreachable']
        if v not in valid_statuses:
            raise ValueError(f"Health status must be one of: {', '.join(valid_statuses)}")
        return v
    
    def get_filter_patterns(self) -> Dict[str, str]:
        """Get filter patterns from configuration"""
        if self.config is None:
            return {}
        
        return {
            'excluded_dirs': self.config.excluded_dirs,
            'excluded_files': self.config.excluded_files,
            'included_dirs': self.config.included_dirs,
            'included_files': self.config.included_files
        }
    
    def is_filtered_file(self, file_path: str) -> bool:
        """Check if a file should be filtered based on configuration"""
        if self.config is None:
            return False
        
        # Check excluded patterns
        if self.config.excluded_files:
            excluded_patterns = [p.strip() for p in self.config.excluded_files.split(',')]
            for pattern in excluded_patterns:
                if pattern in file_path:
                    return True
        
        # Check included patterns (if specified, file must match at least one)
        if self.config.included_files:
            included_patterns = [p.strip() for p in self.config.included_files.split(',')]
            if not any(pattern in file_path for pattern in included_patterns):
                return True
        
        return False
```

### Backward Compatibility Requirements
- All existing `RepoInfo` fields must remain unchanged
- New fields must be optional with sensible defaults
- Existing code must continue working without modification
- All existing validation rules must remain functional

## Subtasks

### Subtask 1: Enhance RepoInfo Fields
- [ ] Add new optional fields to RepoInfo model
- [ ] Implement validation for new fields
- [ ] Ensure backward compatibility
- [ ] Add field descriptions and documentation
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 2: Create RepositoryConfiguration Model
- [ ] Design RepositoryConfiguration model structure
- [ ] Implement advanced filtering fields
- [ ] Add processing configuration options
- [ ] Add performance configuration options
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 3: Implement Advanced Filtering
- [ ] Add filtering pattern validation
- [ ] Implement file filtering logic
- [ ] Add security checks for filter patterns
- [ ] Test filtering functionality
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 4: Add Metadata and Health Fields
- [ ] Add metadata fields (created_at, last_updated, tags)
- [ ] Add health and status fields
- [ ] Implement health status validation
- [ ] Add helper methods for data access
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

## Dependencies
- TASK021: Phase 1.1: Feature Flag Infrastructure (for feature flag integration)
- TASK022: Phase 1.2: Extend Existing Models (for model structure alignment)

## Deliverables
1. Enhanced `backend/models/common.py` with extended RepoInfo
2. New `RepositoryConfiguration` model
3. Advanced filtering functionality
4. Metadata and health tracking fields
5. Unit tests for all new functionality
6. Backward compatibility validation tests

## Success Criteria
- [ ] All existing RepoInfo functionality continues working
- [ ] New fields are properly validated and functional
- [ ] Advanced filtering works correctly
- [ ] Configuration model is fully functional
- [ ] All tests pass
- [ ] Backward compatibility is 100% maintained

## Progress Log

### 2024-12-19 - Task Created
- Task created based on Implementation Phases section
- Implementation plan defined
- Subtasks identified and structured
- Dependencies identified

## Notes
- Must maintain 100% backward compatibility
- New fields should enhance existing functionality, not replace it
- Advanced filtering should be secure and performant
- Configuration model should be flexible and extensible
- Health tracking should provide useful status information
