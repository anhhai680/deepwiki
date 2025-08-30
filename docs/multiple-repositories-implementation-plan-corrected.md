# Multiple Repositories Implementation Plan - CORRECTED

## Overview

This document outlines the corrected implementation plan for adding multi-repository support to the DeepWiki Chat UI Interface. The previous plan contained many incorrect file paths and architectural assumptions that don't match the actual project structure.

**CRITICAL CORRECTIONS MADE:**
- ✅ Fixed all incorrect file paths to match actual project structure
- ✅ Corrected architectural assumptions to use existing components
- ✅ Changed approach from replacement to enhancement of existing code
- ✅ Aligned with actual RAG pipeline architecture
- ✅ Implemented single feature flag approach for clean rollout

## Current Project Structure (ACTUAL)

```
backend/
├── api/
│   └── v1/
│       ├── chat.py          # Chat API endpoints
│       ├── wiki.py          # Wiki API endpoints
│       ├── projects.py      # Project management
│       └── config.py        # Configuration endpoints
├── models/
│   ├── chat.py              # Chat models (ChatCompletionRequest, ChatMessage)
│   ├── common.py            # Common models (RepoInfo)
│   └── wiki.py              # Wiki models
├── websocket/
│   └── wiki_handler.py      # WebSocket handler for chat
├── pipelines/
│   └── rag/                 # RAG pipeline implementation
│       ├── __init__.py      # RAG pipeline exports
│       ├── rag_pipeline.py  # Main RAG pipeline class
│       └── compatibility.py # RAG compatibility layer
├── services/
│   └── project_service.py   # Project management service
└── components/               # Core components (embedder, generator, etc.)
```

## Key Corrections from Previous Plan

### 1. **Incorrect File Paths (PREVIOUS PLAN)**
- ❌ `api/models/repository.py` → ✅ `backend/models/chat.py` (extend existing)
- ❌ `api/services/repository_manager.py` → ✅ `backend/services/repository_manager.py` (new)
- ❌ `api/websocket_wiki.py` → ✅ `backend/websocket/wiki_handler.py` (enhance existing)
- ❌ `api/rag.py` → ✅ `backend/pipelines/rag/` (extend existing)

### 2. **Incorrect Architectural Assumptions**
- ❌ Creating new RAG instances → ✅ Extending existing `RAGPipeline` class
- ❌ Replacing existing models → ✅ Extending existing `RepoInfo` and `ChatCompletionRequest`
- ❌ Creating new WebSocket handlers → ✅ Enhancing existing `wiki_handler.py`
- ❌ Building parallel services → ✅ Integrating with existing architecture

### 3. **Implementation Strategy Changes**
- ❌ Major refactoring → ✅ Incremental enhancement
- ❌ Breaking changes → ✅ 100% backward compatibility
- ❌ New architecture → ✅ Extending existing architecture

## Feature Flag Architecture - Single Flag Approach

### Single Feature Flag Configuration
- **File**: `backend/config/feature_flags.py` (new)
- **Purpose**: Single feature flag to control all multi-repository functionality
- **Implementation**: Environment-based configuration with runtime override capability

```python
# backend/config/feature_flags.py
import os
from typing import Optional

class FeatureFlags:
    """Centralized feature flag management with single flag approach"""
    
    # Single feature flag for all multi-repository functionality
    MULTI_REPO_ENABLED = os.getenv("MULTI_REPO_ENABLED", "false").lower() == "true"
    
    @classmethod
    def is_multi_repo_enabled(cls) -> bool:
        """Check if multi-repository is enabled"""
        return cls.MULTI_REPO_ENABLED
```

### Feature Flag Integration Points
- **WebSocket Handler**: Route requests based on single feature flag
- **RAG Pipeline**: Enable/disable all multi-repository processing
- **API Endpoints**: Conditionally expose all new functionality
- **Models**: Conditional validation and processing

## Implementation Phases

### Phase 1: Feature Flag Infrastructure & Model Enhancement (Week 1-2)

#### 1.1 Feature Flag Infrastructure
- **File**: `backend/config/feature_flags.py` (new)
- **Tasks**:
  - Implement single feature flag management system
  - Add environment-based configuration
  - Create feature flag testing framework
  - Document single feature flag usage patterns

#### 1.2 Extend Existing Models
- **File**: `backend/models/chat.py` (extend existing)
- **Tasks**:
  - Extend `ChatCompletionRequest` to support multiple repositories
  - Add backward compatibility for single repository requests
  - Create `RepositoryInfo` model extending existing `RepoInfo`
  - Add `MultiRepositoryRequest` model with feature flag protection

#### 1.3 Repository Model Enhancement
- **File**: `backend/models/common.py` (extend existing)
- **Tasks**:
  - Enhance `RepoInfo` model with additional fields
  - Add `RepositoryConfiguration` for advanced settings
  - Maintain backward compatibility with existing fields

### Phase 2: WebSocket Handler Enhancement (Week 3)

#### 2.1 Multi-Repository Support
- **File**: `backend/websocket/wiki_handler.py` (enhance existing)
- **Tasks**:
  - Add single feature flag routing logic
  - Implement multi-repository request parsing
  - Add repository validation and health checking
  - Add parallel repository processing
  - Maintain backward compatibility with single repository
  - Add fallback mechanisms for disabled feature

### Phase 3: RAG Pipeline Enhancement (Week 4)

#### 3.1 Multi-RAG Support
- **File**: `backend/pipelines/rag/` (extend existing)
- **Tasks**:
  - Add single feature flag protection to RAG pipeline
  - Enhance `RAGPipeline` class for multi-repository support
  - Add repository-aware document retrieval
  - Implement context merging strategies
  - Add performance optimization for multiple repositories
  - Add performance monitoring for feature flag

### Phase 4: Frontend Implementation with Feature Flag Integration (Week 5-6)

#### 4.1 Frontend Feature Flag Infrastructure
- **File**: `src/config/featureFlags.ts` (new)
- **Tasks**:
  - Implement frontend feature flag management system
  - Add environment-based configuration matching backend
  - Create feature flag testing framework for UI components
  - Document frontend feature flag usage patterns
  - Ensure feature flag state synchronization with backend

#### 4.2 Enhanced Type Definitions with Feature Flag Protection
- **File**: `src/types/repoinfo.tsx` (extend existing)
- **Tasks**:
  - Extend `RepoInfo` interface with multi-repository fields (feature flag protected)
  - Add `RepositoryInfo` interface extending `RepoInfo`
  - Add `MultiRepositoryRequest` interface
  - Maintain backward compatibility with existing `RepoInfo`
  - Add feature flag conditional type definitions

#### 4.3 Enhanced WebSocket Client with Feature Flag
- **File**: `src/utils/websocketClient.ts` (enhance existing)
- **Tasks**:
  - Add feature flag check before enabling multi-repository functionality
  - Extend `ChatCompletionRequest` interface conditionally
  - Add multi-repository WebSocket support (feature flag protected)
  - Maintain existing single repository functionality unchanged
  - Add fallback mechanisms for disabled feature

#### 4.4 Enhanced Ask Component with Feature Flag
- **File**: `src/components/Ask.tsx` (enhance existing)
- **Tasks**:
  - Add feature flag check for multi-repository support
  - Extend props interface conditionally based on feature flag
  - Add multi-repository request handling (feature flag protected)
  - Maintain 100% backward compatibility for single repository
  - Add feature flag UI indicators and controls

#### 4.5 Enhanced Configuration Modal with Feature Flag
- **File**: `src/components/ConfigurationModal.tsx` (enhance existing)
- **Tasks**:
  - Add feature flag check for multi-repository configuration
  - Conditionally show multi-repository UI elements
  - Maintain existing single repository configuration unchanged
  - Add repository management interface (feature flag protected)
  - Ensure backward compatibility for all existing functionality

#### 4.6 Enhanced Main Page with Feature Flag
- **File**: `src/app/page.tsx` (enhance existing)
- **Tasks**:
  - Add feature flag check for multi-repository input
  - Conditionally enable multi-repository input mode
  - Maintain existing single repository input unchanged
  - Add repository list management (feature flag protected)
  - Ensure backward compatibility for all existing functionality

#### 4.7 New Multi-Repository Components (Feature Flag Protected)
- **Files**: 
  - `src/components/MultiRepositoryInput.tsx` (new)
  - `src/components/RepositoryList.tsx` (new)
  - `src/components/RepositoryPriority.tsx` (new)
- **Tasks**:
  - Create multi-repository input interface
  - Implement repository list management with drag-and-drop
  - Add repository priority controls
  - All components must check feature flag before rendering
  - Ensure graceful degradation when feature is disabled

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

# Backward compatibility: ChatCompletionRequest remains unchanged
# New requests can use MultiRepositoryRequest for multiple repositories
```

### Enhanced WebSocket Handler

```python
# backend/websocket/wiki_handler.py - ENHANCE EXISTING
from ..config.feature_flags import FeatureFlags
from ..models.chat import MultiRepositoryRequest, RepositoryInfo, ChatCompletionRequest
from ..services.repository_manager import RepositoryManager

async def handle_websocket_chat(websocket: WebSocket):
    """
    Single feature flag-enabled WebSocket handler supporting both single and multiple repositories.
    Maintains 100% backward compatibility through single feature flag.
    """
    await websocket.accept()

    try:
        request_data = await websocket.receive_json()
        
        # Single feature flag: Check if multi-repository is enabled
        if (FeatureFlags.is_multi_repo_enabled() and 
            'repositories' in request_data and 
            isinstance(request_data['repositories'], list)):
            
            # Multi-repository request (feature enabled)
            request = MultiRepositoryRequest(**request_data)
            await handle_multi_repository_chat(websocket, request)
        else:
            # Single repository request (always available for backward compatibility)
            request = ChatCompletionRequest(**request_data)
            await handle_single_repository_chat(websocket, request)
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket handler: {e}")
        await websocket.send_json({
            "type": "error",
            "data": {"message": str(e)}
        })

async def handle_multi_repository_chat(websocket: WebSocket, request: MultiRepositoryRequest):
    """Handle multi-repository chat requests (single feature flag protected)"""
    if not FeatureFlags.is_multi_repo_enabled():
        # Fallback to single repository if feature is disabled
        single_repo_request = ChatCompletionRequest(
            repo=request.repositories[0].repo,
            owner=request.repositories[0].owner,
            messages=request.messages,
            # ... other fields
        )
        await handle_single_repository_chat(websocket, single_repo_request)
        return
    
    # Multi-repository processing logic
    # ... implementation ...
```

## Critical Requirements

### 1. **Backward Compatibility (MANDATORY)**
- Existing single-repository functionality must work 100% unchanged
- All existing API endpoints must continue functioning
- Existing WebSocket connections must remain stable
- No breaking changes to existing models or interfaces

### 2. **Integration Guidelines**
- Extend existing components, don't replace them
- Use inheritance and composition for new functionality
- Maintain existing function signatures where possible
- Add new functionality through optional parameters

### 3. **Testing Requirements**
- All existing tests must continue passing
- New tests must cover multi-repository scenarios
- Performance tests must show acceptable degradation
- Integration tests must verify backward compatibility

## Testing Strategy

### Feature Flag Testing
- **Unit Tests**: Test single feature flag logic in isolation
- **Integration Tests**: Verify feature flag works across all components
- **Environment Tests**: Test feature flag in different configurations

### Backward Compatibility Testing
- **Feature Disabled**: Ensure existing functionality works unchanged
- **Feature Enabled**: Verify all multi-repository functionality works correctly
- **Feature Toggle**: Test switching between enabled/disabled states
- **Rollback Testing**: Verify system stability when toggling feature off

### Rollout Testing
- **Global Toggle**: Test system-wide feature enable/disable
- **Performance Impact**: Monitor system performance during rollout

## Monitoring and Rollback

### Monitoring Requirements
- **Performance Metrics**: Track response times and resource usage
- **Error Rates**: Monitor error rates for both feature states
- **User Experience**: Track user satisfaction and usage patterns
- **System Health**: Monitor overall system stability

### Rollback Procedures
- **Instant Rollback**: Single feature flag can be disabled instantly
- **Environment Rollback**: Different settings per environment

### Feature Flag Lifecycle
1. **Development**: Feature flag disabled by default
2. **Testing**: Feature flag enabled in test environments
3. **Staging**: Feature flag enabled for validation
4. **Production**: Feature flag enabled with monitoring
5. **Full Release**: Feature flag removed after validation

## Risk Mitigation

### 1. **System Breakage Prevention**
- Implement feature flags for gradual rollout
- Extensive testing of both single and multi-repository scenarios
- Rollback plan for any issues
- Monitoring and alerting for performance degradation

### 2. **Incremental Enhancement**
- Start with single-repository enhancement
- Add multi-repository support incrementally
- Test each enhancement thoroughly before proceeding
- Maintain working system throughout development

## Environment Configuration

```bash
# Development (feature disabled)
MULTI_REPO_ENABLED=false

# Testing (feature enabled)
MULTI_REPO_ENABLED=true

# Production (feature enabled)
MULTI_REPO_ENABLED=true
```

## Benefits of Single Feature Flag Approach

1. **Simpler Management**: One flag to control all multi-repository functionality
2. **Easier Testing**: Test one feature state instead of multiple combinations
3. **Cleaner Rollback**: Single toggle to disable all new functionality
4. **Reduced Complexity**: Less configuration and fewer potential failure points
5. **Better Monitoring**: Single metric to track feature adoption and performance

## Frontend Feature Flag Implementation

### Frontend Feature Flag Configuration
- **File**: `src/config/featureFlags.ts` (new)
- **Purpose**: Mirror backend feature flag for frontend components
- **Implementation**: Environment-based configuration with runtime override capability

```typescript
// src/config/featureFlags.ts
export class FeatureFlags {
  /** Centralized feature flag management matching backend implementation */
  
  // Single feature flag for all multi-repository functionality
  static MULTI_REPO_ENABLED = process.env.NEXT_PUBLIC_MULTI_REPO_ENABLED === 'true';
  
  /**
   * Check if multi-repository is enabled
   * This must match the backend feature flag exactly
   */
  static isMultiRepoEnabled(): boolean {
    return this.MULTI_REPO_ENABLED;
  }
  
  /**
   * Get feature flag status for debugging
   */
  static getFeatureFlagStatus() {
    return {
      multiRepoEnabled: this.MULTI_REPO_ENABLED,
      environment: process.env.NODE_ENV,
      configValue: process.env.NEXT_PUBLIC_MULTI_REPO_ENABLED
    };
  }
}
```

### Frontend Feature Flag Integration Points

#### 1. **Type Definitions (Conditional)**
```typescript
// src/types/repoinfo.tsx - Feature flag protected extensions
import { FeatureFlags } from '@/config/featureFlags';

export interface RepoInfo {
  owner: string;
  repo: string;
  type: string;
  token: string | null;
  localPath: string | null;
  repoUrl: string | null;
}

// Only extend if feature flag is enabled
export interface RepositoryInfo extends RepoInfo {
  // New fields for multi-repository support (feature flag protected)
  alias?: string;
  description?: string;
  priority_weight?: number;
  
  // Enhanced filtering (extending existing fields)
  excluded_dirs?: string;
  excluded_files?: string;
  included_dirs?: string;
  included_files?: string;
}

// Only export if feature flag is enabled
export interface MultiRepositoryRequest {
  repositories: RepositoryInfo[];
  messages: ChatMessage[];
  
  // Context configuration
  max_total_context?: number;
  repository_balance?: 'equal' | 'weighted' | 'priority';
  
  // AI configuration (extending existing fields)
  provider?: string;
  model?: string;
  language?: string;
}

// Conditional exports based on feature flag
export const getMultiRepositoryTypes = () => {
  if (FeatureFlags.isMultiRepoEnabled()) {
    return {
      RepositoryInfo,
      MultiRepositoryRequest
    };
  }
  return {};
};

export default RepoInfo;
```

#### 2. **WebSocket Client (Feature Flag Protected)**
```typescript
// src/utils/websocketClient.ts - Feature flag protected extensions
import { FeatureFlags } from '@/config/featureFlags';

export interface ChatCompletionRequest {
  // Always support single repository (backward compatibility)
  repo_url: string;
  messages: ChatMessage[];
  filePath?: string;
  token?: string;
  type?: string;
  provider?: string;
  model?: string;
  language?: string;
  excluded_dirs?: string;
  excluded_files?: string;
}

// Only extend if feature flag is enabled
export interface MultiRepositoryChatRequest {
  repositories: RepositoryInfo[];
  messages: ChatMessage[];
  filePath?: string;
  token?: string;
  type?: string;
  provider?: string;
  model?: string;
  language?: string;
  excluded_dirs?: string;
  excluded_files?: string;
  
  // New multi-repository fields
  max_total_context?: number;
  repository_balance?: string;
}

// Feature flag protected WebSocket creation
export const createMultiRepositoryWebSocket = (
  request: MultiRepositoryChatRequest,
  onMessage: (message: string) => void,
  onError: (error: Event) => void,
  onClose: () => void
): WebSocket | null => {
  // Check feature flag before enabling multi-repository functionality
  if (!FeatureFlags.isMultiRepoEnabled()) {
    console.warn('Multi-repository feature is disabled');
    return null;
  }
  
  // Implementation for multi-repository WebSocket handling
  // ... implementation ...
};
```

#### 3. **Ask Component (Feature Flag Protected)**
```typescript
// src/components/Ask.tsx - Feature flag protected extensions
import { FeatureFlags } from '@/config/featureFlags';

interface AskProps {
  // Always support single repository (backward compatibility)
  repoInfo: RepoInfo;
  provider?: string;
  model?: string;
  isCustomModel?: boolean;
  customModel?: string;
  language?: string;
  onRef?: (ref: { clearConversation: () => void }) => void;
  
  // Only add multi-repository props if feature flag is enabled
  ...(FeatureFlags.isMultiRepoEnabled() ? {
    repositories?: RepositoryInfo[];
    maxTotalContext?: number;
    repositoryBalance?: string;
  } : {});
}

const Ask: React.FC<AskProps> = (props) => {
  // ... existing code ...
  
  // Feature flag protected multi-repository handling
  const handleMultiRepositoryRequest = async () => {
    if (!FeatureFlags.isMultiRepoEnabled()) {
      // Fallback to single repository if feature is disabled
      await handleSingleRepositoryRequest();
      return;
    }
    
    // Multi-repository processing logic
    // ... implementation ...
  };
  
  // Always available single repository handling (backward compatibility)
  const handleSingleRepositoryRequest = async () => {
    // ... existing single repository logic unchanged ...
  };
  
  // ... rest of existing code ...
};
```

#### 4. **Configuration Modal (Feature Flag Protected)**
```typescript
// src/components/ConfigurationModal.tsx - Feature flag protected extensions
import { FeatureFlags } from '@/config/featureFlags';

interface ConfigurationModalProps {
  // ... existing props unchanged ...
  
  // Only add multi-repository props if feature flag is enabled
  ...(FeatureFlags.isMultiRepoEnabled() ? {
    repositories?: RepositoryInfo[];
    onRepositoriesChange?: (repos: RepositoryInfo[]) => void;
    maxTotalContext?: number;
    repositoryBalance?: string;
  } : {});
}

const ConfigurationModal: React.FC<ConfigurationModalProps> = (props) => {
  // ... existing code ...
  
  return (
    <div>
      {/* Always show existing single repository configuration */}
      {/* ... existing UI unchanged ... */}
      
      {/* Only show multi-repository UI if feature flag is enabled */}
      {FeatureFlags.isMultiRepoEnabled() && (
        <div className="multi-repository-section">
          {/* Multi-repository configuration UI */}
          {/* ... implementation ... */}
        </div>
      )}
    </div>
  );
};
```

#### 5. **Main Page (Feature Flag Protected)**
```typescript
// src/app/page.tsx - Feature flag protected extensions
import { FeatureFlags } from '@/config/featureFlags';

export default function Home() {
  // ... existing code ...
  
  // Only add multi-repository state if feature flag is enabled
  const [repositories, setRepositories] = useState<RepositoryInfo[]>(
    FeatureFlags.isMultiRepoEnabled() ? [] : []
  );
  const [isMultiRepositoryMode, setIsMultiRepositoryMode] = useState(
    FeatureFlags.isMultiRepoEnabled() ? false : false
  );
  
  // ... existing code ...
  
  return (
    <div>
      {/* Always show existing single repository input */}
      {/* ... existing UI unchanged ... */}
      
      {/* Only show multi-repository toggle if feature flag is enabled */}
      {FeatureFlags.isMultiRepoEnabled() && (
        <div className="multi-repository-toggle">
          <label>
            <input
              type="checkbox"
              checked={isMultiRepositoryMode}
              onChange={(e) => setIsMultiRepositoryMode(e.target.checked)}
            />
            Enable Multi-Repository Mode
          </label>
        </div>
      )}
      
      {/* Conditionally show multi-repository input */}
      {FeatureFlags.isMultiRepoEnabled() && isMultiRepositoryMode ? (
        <MultiRepositoryInput
          repositories={repositories}
          onRepositoriesChange={setRepositories}
          // ... other props ...
        />
      ) : (
        /* Existing single repository input unchanged */
        /* ... existing UI unchanged ... */
      )}
      
      {/* ... rest of existing UI unchanged ... */}
    </div>
  );
}
```

### Frontend Feature Flag Testing Strategy

#### 1. **Component Testing with Feature Flag**
```typescript
// Test that components work correctly with feature flag disabled
describe('Ask Component - Feature Flag Disabled', () => {
  beforeEach(() => {
    // Mock feature flag as disabled
    jest.spyOn(FeatureFlags, 'isMultiRepoEnabled').mockReturnValue(false);
  });
  
  test('should render single repository interface unchanged', () => {
    // Verify existing functionality works exactly as before
  });
  
  test('should not render multi-repository props', () => {
    // Verify multi-repository props are not accepted
  });
});

// Test that components work correctly with feature flag enabled
describe('Ask Component - Feature Flag Enabled', () => {
  beforeEach(() => {
    // Mock feature flag as enabled
    jest.spyOn(FeatureFlags, 'isMultiRepoEnabled').mockReturnValue(true);
  });
  
  test('should render multi-repository interface', () => {
    // Verify new functionality is available
  });
  
  test('should maintain backward compatibility', () => {
    // Verify existing functionality still works
  });
});
```

#### 2. **Feature Flag Toggle Testing**
```typescript
// Test feature flag state changes
describe('Feature Flag Toggle', () => {
  test('should gracefully handle feature flag changes', () => {
    // Test switching between enabled/disabled states
    // Verify no errors or crashes occur
  });
  
  test('should maintain user data during feature flag changes', () => {
    // Test that user data persists when toggling feature
  });
});
```

### Frontend Environment Configuration

```bash
# Development (feature disabled)
NEXT_PUBLIC_MULTI_REPO_ENABLED=false

# Testing (feature enabled)
NEXT_PUBLIC_MULTI_REPO_ENABLED=true

# Production (feature enabled)
NEXT_PUBLIC_MULTI_REPO_ENABLED=true
```

### Frontend Feature Flag Benefits

1. **Backward Compatibility**: Existing single repository functionality works unchanged
2. **Gradual Rollout**: Feature can be enabled/disabled per environment
3. **Safe Testing**: Test new functionality without affecting production users
4. **Easy Rollback**: Disable feature instantly if issues arise
5. **User Experience**: Users see consistent interface based on feature flag state
6. **Development Safety**: Developers can work on new features without breaking existing code

## Critical Frontend Requirements

### 1. **100% Backward Compatibility (MANDATORY)**
- Existing single-repository functionality must work unchanged
- All existing UI components must render identically when feature flag is disabled
- No breaking changes to existing component interfaces
- Existing user workflows must continue functioning

### 2. **Feature Flag Integration Guidelines**
- All new multi-repository functionality must check feature flag before rendering
- Feature flag state must be synchronized between frontend and backend
- Graceful degradation when feature flag is disabled
- No errors or crashes when feature flag changes

### 3. **Testing Requirements**
- All existing tests must continue passing
- New tests must cover both feature flag states
- Feature flag toggle testing must verify system stability
- Integration tests must verify backward compatibility

### 4. **User Experience Requirements**
- Clear indication when multi-repository mode is available
- Smooth transition between single and multi-repository modes
- Consistent interface regardless of feature flag state
- No confusion about available functionality

## Next Steps

1. **Implement Backend Feature Flag Infrastructure**: Create `backend/config/feature_flags.py`
2. **Extend Backend Models**: Enhance existing models with multi-repository support
3. **Enhance WebSocket Handler**: Add feature flag routing and multi-repository support
4. **Enhance RAG Pipeline**: Add multi-repository processing capabilities
5. **Implement Frontend Feature Flag Infrastructure**: Create `src/config/featureFlags.ts`
6. **Update Frontend Type Definitions**: Extend interfaces with feature flag protection
7. **Enhance Frontend Components**: Add feature flag checks to all new functionality
8. **Test Backward Compatibility**: Verify existing functionality works unchanged
9. **Implement Multi-Repository UI**: Add new components with feature flag protection
10. **Test Feature Flag Toggle**: Verify system stability during feature changes

## Conclusion

The implementation plan now includes comprehensive feature flag integration for both backend and frontend, ensuring:

1. **Complete Backward Compatibility**: Existing functionality works unchanged
2. **Safe Feature Rollout**: Feature can be enabled/disabled safely across all components
3. **System Stability**: No risk of breaking existing functionality
4. **Consistent Architecture**: Frontend and backend use identical feature flag logic
5. **User Experience Protection**: Users see consistent interface regardless of feature state
6. **Full Stack Safety**: Both backend services and frontend UI are protected by feature flags

This approach prevents the DeepWiki system from breaking during new feature implementation while providing a safe path for adding multi-repository support through a unified feature flag strategy.

### 5. **User Experience**
- Clear indication when multi-repository mode is available
- Smooth transition between single and multi-repository modes
- Consistent interface regardless of feature flag state

## Database and Storage Considerations

### 1. **Repository Metadata Storage**
**File**: `backend/data/repositories/` (new directory)
**Purpose**: Store repository metadata, configuration, and processing history

```python
# backend/data/repositories/repository_store.py (new)
from typing import List, Optional, Dict
from ...models.chat import RepositoryInfo
from ...core.exceptions import RepositoryNotFoundError
import json
import os

class RepositoryStore:
    """Persistent storage for repository metadata and configuration"""
    
    def __init__(self, storage_path: str = "data/repositories"):
        self.storage_path = storage_path
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Ensure storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def save_repository(self, repo: RepositoryInfo) -> bool:
        """Save repository metadata to persistent storage"""
        try:
            filename = f"{repo.owner}_{repo.repo}.json"
            filepath = os.path.join(self.storage_path, filename)
            
            with open(filepath, 'w') as f:
                json.dump(repo.dict(), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save repository {repo.repo}: {e}")
            return False
    
    def load_repository(self, owner: str, repo: str) -> Optional[RepositoryInfo]:
        """Load repository metadata from persistent storage"""
        try:
            filename = f"{owner}_{repo}.json"
            filepath = os.path.join(self.storage_path, filename)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r') as f:
                data = json.load(f)
                return RepositoryInfo(**data)
        except Exception as e:
            logger.error(f"Failed to load repository {owner}/{repo}: {e}")
            return None
    
    def list_repositories(self) -> List[RepositoryInfo]:
        """List all stored repositories"""
        repositories = []
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.storage_path, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        repositories.append(RepositoryInfo(**data))
                except Exception as e:
                    logger.warning(f"Failed to load repository from {filename}: {e}")
        return repositories
```

### 2. **Vector Store Integration**
**File**: `backend/data/vector_store.py` (extend existing)
**Purpose**: Enhance vector store to support multi-repository document indexing

```python
# backend/data/vector_store.py - EXTEND EXISTING
class VectorStore:
    """Enhanced vector store with multi-repository support"""
    
    def __init__(self):
        # ... existing initialization ...
        self.repository_store = RepositoryStore()
    
    async def index_multi_repository_documents(self, repositories: List[RepositoryInfo]) -> Dict[str, int]:
        """Index documents from multiple repositories"""
        if not FeatureFlags.is_multi_repo_enabled():
            # Fallback to single repository indexing
            return await self.index_single_repository_documents(repositories[0])
        
        indexing_results = {}
        for repo in repositories:
            try:
                doc_count = await self.index_single_repository_documents(repo)
                indexing_results[f"{repo.owner}/{repo.repo}"] = doc_count
            except Exception as e:
                logger.error(f"Failed to index repository {repo.owner}/{repo.repo}: {e}")
                indexing_results[f"{repo.owner}/{repo.repo}"] = 0
        
        return indexing_results
    
    async def search_across_repositories(self, query: str, repositories: List[RepositoryInfo], 
                                       limit: int = 10) -> List[Document]:
        """Search for documents across multiple repositories"""
        if not FeatureFlags.is_multi_repo_enabled():
            # Fallback to single repository search
            return await self.search_single_repository(query, repositories[0], limit)
        
        # Search each repository in parallel
        search_tasks = [
            self.search_single_repository(query, repo, limit)
            for repo in repositories
        ]
        
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Merge and rank results
        all_documents = []
        for result in results:
            if isinstance(result, list):
                all_documents.extend(result)
            # Handle exceptions gracefully
        
        # Sort by relevance and return top results
        return sorted(all_documents, key=lambda x: x.score, reverse=True)[:limit]
```

## API Endpoint Enhancements

### 1. **Multi-Repository API Endpoints**
**File**: `backend/api/v1/chat.py` (extend existing)
**Purpose**: Add REST API endpoints for multi-repository operations

```python
# backend/api/v1/chat.py - EXTEND EXISTING
from ...config.feature_flags import FeatureFlags
from ...models.chat import MultiRepositoryRequest, RepositoryInfo
from ...services.repository_manager import RepositoryManager

@router.post("/multi-repository/chat")
async def multi_repository_chat(request: MultiRepositoryRequest):
    """Chat endpoint supporting multiple repositories (feature flag protected)"""
    if not FeatureFlags.is_multi_repo_enabled():
        # Fallback to single repository chat
        single_repo_request = ChatCompletionRequest(
            repo=request.repositories[0].repo,
            owner=request.repositories[0].owner,
            messages=request.messages,
            provider=request.provider,
            model=request.model,
            language=request.language
        )
        return await single_repository_chat(single_repo_request)
    
    # Multi-repository processing
    repository_manager = RepositoryManager()
    validated_repos = await repository_manager.validate_repositories(request.repositories)
    
    # Process with RAG pipeline
    rag_pipeline = RAGPipeline()
    result = await rag_pipeline.process_multi_repository_request(request)
    
    return {
        "status": "success",
        "data": result,
        "repositories_processed": len(validated_repos)
    }

@router.get("/repositories")
async def list_repositories():
    """List all available repositories (feature flag protected)"""
    if not FeatureFlags.is_multi_repo_enabled():
        return {"status": "error", "message": "Multi-repository feature is disabled"}
    
    repository_store = RepositoryStore()
    repositories = repository_store.list_repositories()
    
    return {
        "status": "success",
        "data": {
            "repositories": [repo.dict() for repo in repositories],
            "count": len(repositories)
        }
    }

@router.post("/repositories")
async def add_repository(repo: RepositoryInfo):
    """Add a new repository (feature flag protected)"""
    if not FeatureFlags.is_multi_repo_enabled():
        return {"status": "error", "message": "Multi-repository feature is disabled"}
    
    repository_manager = RepositoryManager()
    if await repository_manager._validate_single_repository(repo):
        repository_store = RepositoryStore()
        if repository_store.save_repository(repo):
            return {"status": "success", "message": "Repository added successfully"}
        else:
            return {"status": "error", "message": "Failed to save repository"}
    else:
        return {"status": "error", "message": "Repository validation failed"}
```

### 2. **Repository Management Endpoints**
**File**: `backend/api/v1/projects.py` (extend existing)
**Purpose**: Add repository management functionality to existing project endpoints

```python
# backend/api/v1/projects.py - EXTEND EXISTING
from ...config.feature_flags import FeatureFlags
from ...models.chat import RepositoryInfo
from ...services.repository_manager import RepositoryManager

@router.get("/{project_id}/repositories")
async def get_project_repositories(project_id: str):
    """Get repositories associated with a project (feature flag protected)"""
    if not FeatureFlags.is_multi_repo_enabled():
        return {"status": "error", "message": "Multi-repository feature is disabled"}
    
    # Implementation for retrieving project repositories
    pass

@router.post("/{project_id}/repositories")
async def add_project_repository(project_id: str, repo: RepositoryInfo):
    """Add repository to project (feature flag protected)"""
    if not FeatureFlags.is_multi_repo_enabled():
        return {"status": "error", "message": "Multi-repository feature is disabled"}
    
    # Implementation for adding repository to project
    pass
```

## Performance Optimization Strategies

### 1. **Parallel Processing Configuration**
**File**: `backend/config/performance.py` (new)
**Purpose**: Configure performance parameters for multi-repository processing

```python
# backend/config/performance.py (new)
from pydantic import BaseSettings
from typing import Dict, Any

class PerformanceConfig(BaseSettings):
    """Performance configuration for multi-repository processing"""
    
    # Parallel processing limits
    MAX_CONCURRENT_REPOSITORIES: int = 5
    MAX_CONCURRENT_INDEXING: int = 3
    MAX_CONCURRENT_SEARCHES: int = 10
    
    # Timeout configurations
    REPOSITORY_VALIDATION_TIMEOUT: int = 30
    DOCUMENT_INDEXING_TIMEOUT: int = 300
    SEARCH_TIMEOUT: int = 60
    
    # Memory management
    MAX_MEMORY_USAGE_MB: int = 1024
    DOCUMENT_BATCH_SIZE: int = 100
    
    # Caching configuration
    ENABLE_REPOSITORY_CACHE: bool = True
    CACHE_TTL_SECONDS: int = 3600
    
    class Config:
        env_file = ".env"
```

### 2. **Caching Strategy**
**File**: `backend/services/cache_manager.py` (new)
**Purpose**: Implement caching for repository metadata and search results

```python
# backend/services/cache_manager.py (new)
from typing import Any, Optional, Dict
import asyncio
import time

class CacheManager:
    """Cache manager for multi-repository functionality"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self.cache:
            cache_entry = self.cache[key]
            if time.time() - cache_entry['timestamp'] < self.ttl_seconds:
                return cache_entry['value']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set value in cache with timestamp"""
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def clear_expired(self):
        """Clear expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] >= self.ttl_seconds
        ]
        for key in expired_keys:
            del self.cache[key]
```

## Security and Validation

### 1. **Repository Access Validation**
**File**: `backend/services/security_validator.py` (new)
**Purpose**: Validate repository access permissions and security

```python
# backend/services/security_validator.py (new)
from typing import List, Optional
from ..models.chat import RepositoryInfo
from ..core.exceptions import SecurityValidationError
import re
import os

class SecurityValidator:
    """Security validation for repository access"""
    
    def __init__(self):
        self.allowed_domains = [
            'github.com',
            'gitlab.com',
            'bitbucket.org'
        ]
        self.blocked_patterns = [
            r'\.\./',  # Path traversal
            r'//',     # Protocol confusion
            r'file://' # Local file access
        ]
    
    def validate_repository_url(self, repo_url: str) -> bool:
        """Validate repository URL for security"""
        if not repo_url:
            return False
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, repo_url):
                raise SecurityValidationError(f"Repository URL contains blocked pattern: {pattern}")
        
        # Validate domain
        try:
            from urllib.parse import urlparse
            parsed = urlparse(repo_url)
            if parsed.netloc not in self.allowed_domains:
                raise SecurityValidationError(f"Repository domain not allowed: {parsed.netloc}")
        except Exception as e:
            raise SecurityValidationError(f"Invalid repository URL: {e}")
        
        return True
    
    def validate_local_path(self, local_path: str) -> bool:
        """Validate local file path for security"""
        if not local_path:
            return False
        
        # Check for path traversal
        if '..' in local_path or '//' in local_path:
            raise SecurityValidationError("Local path contains invalid patterns")
        
        # Check if path exists and is accessible
        if not os.path.exists(local_path):
            raise SecurityValidationError(f"Local path does not exist: {local_path}")
        
        return True
    
    def validate_token(self, token: str, repo_type: str) -> bool:
        """Validate repository access token"""
        if not token:
            return True  # No token is valid for public repositories
        
        # Basic token format validation
        if len(token) < 10:
            raise SecurityValidationError("Token too short")
        
        # Repository-specific validation
        if repo_type == 'github':
            return self._validate_github_token(token)
        elif repo_type == 'gitlab':
            return self._validate_gitlab_token(token)
        elif repo_type == 'bitbucket':
            return self._validate_bitbucket_token(token)
        
        return True
    
    def _validate_github_token(self, token: str) -> bool:
        """Validate GitHub personal access token"""
        # Implementation for GitHub token validation
        return True
    
    def _validate_gitlab_token(self, token: str) -> bool:
        """Validate GitLab personal access token"""
        # Implementation for GitLab token validation
        return True
    
    def _validate_bitbucket_token(self, token: str) -> bool:
        """Validate Bitbucket personal access token"""
        # Implementation for Bitbucket token validation
        return True
```

## Monitoring and Observability

### 1. **Performance Metrics Collection**
**File**: `backend/services/metrics_collector.py` (new)
**Purpose**: Collect and track performance metrics for multi-repository functionality

```python
# backend/services/metrics_collector.py (new)
from typing import Dict, List, Any
import time
import asyncio
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProcessingMetrics:
    """Metrics for repository processing"""
    repository_count: int
    total_processing_time: float
    parallel_processing_time: float
    sequential_processing_time: float
    success_count: int
    error_count: int
    memory_usage_mb: float
    timestamp: datetime

class MetricsCollector:
    """Collect performance and usage metrics"""
    
    def __init__(self):
        self.metrics: List[ProcessingMetrics] = []
        self.current_session_start = time.time()
    
    def record_processing_metrics(self, metrics: ProcessingMetrics):
        """Record processing metrics"""
        self.metrics.append(metrics)
        
        # Keep only last 1000 metrics to prevent memory issues
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for monitoring"""
        if not self.metrics:
            return {"status": "no_data"}
        
        total_repos = sum(m.repository_count for m in self.metrics)
        avg_processing_time = sum(m.total_processing_time for m in self.metrics) / len(self.metrics)
        success_rate = sum(m.success_count for m in self.metrics) / total_repos if total_repos > 0 else 0
        
        return {
            "total_requests": len(self.metrics),
            "total_repositories_processed": total_repos,
            "average_processing_time": avg_processing_time,
            "success_rate": success_rate,
            "session_duration": time.time() - self.current_session_start
        }
    
    def get_repository_performance(self, repository_id: str) -> Dict[str, Any]:
        """Get performance metrics for specific repository"""
        repo_metrics = [m for m in self.metrics if repository_id in str(m)]
        
        if not repo_metrics:
            return {"status": "no_data"}
        
        # Calculate repository-specific metrics
        return {
            "repository_id": repository_id,
            "request_count": len(repo_metrics),
            "average_processing_time": sum(m.total_processing_time for m in repo_metrics) / len(repo_metrics)
        }
```

### 2. **Health Check Endpoints**
**File**: `backend/api/v1/health.py` (new)
**Purpose**: Provide health check endpoints for monitoring system status

```python
# backend/api/v1/health.py (new)
from fastapi import APIRouter, Depends
from ...config.feature_flags import FeatureFlags
from ...services.metrics_collector import MetricsCollector
from ...services.repository_manager import RepositoryManager

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/multi-repository")
async def multi_repository_health():
    """Multi-repository feature health check (feature flag protected)"""
    if not FeatureFlags.is_multi_repo_enabled():
        return {
            "status": "disabled",
            "feature": "multi-repository",
            "message": "Feature is disabled"
        }
    
    try:
        # Check repository manager health
        repository_manager = RepositoryManager()
        
        # Check metrics collector health
        metrics_collector = MetricsCollector()
        performance_summary = metrics_collector.get_performance_summary()
        
        return {
            "status": "healthy",
            "feature": "multi-repository",
            "repository_manager": "operational",
            "metrics_collector": "operational",
            "performance_summary": performance_summary
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "feature": "multi-repository",
            "error": str(e)
        }

@router.get("/repositories")
async def repositories_health():
    """Repository health check endpoint"""
    if not FeatureFlags.is_multi_repo_enabled():
        return {
            "status": "disabled",
            "message": "Multi-repository feature is disabled"
        }
    
    try:
        repository_manager = RepositoryManager()
        # Implementation for checking repository health
        return {
            "status": "healthy",
            "repositories": "operational"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

## Deployment and Configuration

### 1. **Docker Configuration Updates**
**File**: `docker-compose.yml` (extend existing)
**Purpose**: Add environment variables and configuration for multi-repository feature

```yaml
# docker-compose.yml - EXTEND EXISTING
version: '3.8'
services:
  backend:
    build: .
    environment:
      # ... existing environment variables ...
      
      # Multi-repository feature flags
      - MULTI_REPO_ENABLED=${MULTI_REPO_ENABLED:-false}
      - MULTI_REPO_MAX_REPOSITORIES=${MULTI_REPO_MAX_REPOSITORIES:-10}
      - MULTI_REPO_MAX_TOTAL_CONTEXT=${MULTI_REPO_MAX_TOTAL_CONTEXT:-8000}
      - MULTI_REPO_DEFAULT_BALANCE_STRATEGY=${MULTI_REPO_DEFAULT_BALANCE_STRATEGY:-equal}
      - MULTI_REPO_PARALLEL_PROCESSING=${MULTI_REPO_PARALLEL_PROCESSING:-true}
      - MULTI_REPO_TIMEOUT_SECONDS=${MULTI_REPO_TIMEOUT_SECONDS:-30}
      
      # Performance configuration
      - MAX_CONCURRENT_REPOSITORIES=${MAX_CONCURRENT_REPOSITORIES:-5}
      - MAX_CONCURRENT_INDEXING=${MAX_CONCURRENT_INDEXING:-3}
      - MAX_CONCURRENT_SEARCHES=${MAX_CONCURRENT_SEARCHES:-10}
      
      # Security configuration
      - ALLOWED_REPOSITORY_DOMAINS=${ALLOWED_REPOSITORY_DOMAINS:-github.com,gitlab.com,bitbucket.org}
    
    volumes:
      # ... existing volumes ...
      - ./data/repositories:/app/data/repositories
      - ./logs:/app/logs
    
    ports:
      - "8000:8000"
  
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    environment:
      # ... existing environment variables ...
      
      # Frontend feature flags (must match backend)
      - NEXT_PUBLIC_MULTI_REPO_ENABLED=${MULTI_REPO_ENABLED:-false}
    
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### 2. **Environment Configuration Files**
**File**: `.env.example` (new)
**Purpose**: Provide example environment configuration

```bash
# .env.example (new)

# Multi-repository feature flags
MULTI_REPO_ENABLED=false
MULTI_REPO_MAX_REPOSITORIES=10
MULTI_REPO_MAX_TOTAL_CONTEXT=8000
MULTI_REPO_DEFAULT_BALANCE_STRATEGY=equal
MULTI_REPO_PARALLEL_PROCESSING=true
MULTI_REPO_TIMEOUT_SECONDS=30

# Performance configuration
MAX_CONCURRENT_REPOSITORIES=5
MAX_CONCURRENT_INDEXING=3
MAX_CONCURRENT_SEARCHES=10
REPOSITORY_VALIDATION_TIMEOUT=30
DOCUMENT_INDEXING_TIMEOUT=300
SEARCH_TIMEOUT=60

# Memory management
MAX_MEMORY_USAGE_MB=1024
DOCUMENT_BATCH_SIZE=100

# Caching configuration
ENABLE_REPOSITORY_CACHE=true
CACHE_TTL_SECONDS=3600

# Security configuration
ALLOWED_REPOSITORY_DOMAINS=github.com,gitlab.com,bitbucket.org

# Frontend feature flags (must match backend)
NEXT_PUBLIC_MULTI_REPO_ENABLED=false
```

## Troubleshooting and Debugging

### 1. **Common Issues and Solutions**
**File**: `docs/troubleshooting.md` (new)
**Purpose**: Document common issues and their solutions

```markdown
# Troubleshooting Multi-Repository Feature

## Common Issues

### 1. Feature Flag Not Working
**Symptoms**: Multi-repository functionality not available
**Solutions**:
- Check environment variables: `MULTI_REPO_ENABLED=true`
- Verify frontend and backend feature flags match
- Restart services after changing environment variables

### 2. Repository Validation Failures
**Symptoms**: Repositories fail to validate
**Solutions**:
- Check repository URLs are accessible
- Verify access tokens are valid
- Check network connectivity to repository hosts

### 3. Performance Issues
**Symptoms**: Slow processing with multiple repositories
**Solutions**:
- Reduce `MAX_CONCURRENT_REPOSITORIES`
- Increase `MULTI_REPO_TIMEOUT_SECONDS`
- Monitor memory usage and adjust `MAX_MEMORY_USAGE_MB`

### 4. WebSocket Connection Issues
**Symptoms**: WebSocket connections fail or timeout
**Solutions**:
- Check WebSocket handler implementation
- Verify feature flag routing logic
- Check for circular import issues

## Debug Commands

### Backend Debug
```bash
# Check feature flag status
curl http://localhost:8000/health/multi-repository

# Check repository health
curl http://localhost:8000/health/repositories

# View logs
tail -f logs/application.log
```

### Frontend Debug
```javascript
// Check feature flag status in browser console
console.log(FeatureFlags.getFeatureFlagStatus());

// Check WebSocket connection
// Add logging to websocketClient.ts
```

## Log Analysis

### Key Log Patterns
- `Feature flag enabled/disabled` - Feature flag status changes
- `Repository validation` - Repository validation attempts
- `Multi-repository processing` - Multi-repository request processing
- `Performance metrics` - Processing time and resource usage
```

### 2. **Debug Mode Configuration**
**File**: `backend/config/debug.py` (new)
**Purpose**: Enable debug mode for development and troubleshooting

```python
# backend/config/debug.py (new)
import os
from typing import Dict, Any

class DebugConfig:
    """Debug configuration for development and troubleshooting"""
    
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Debug flags for specific components
    DEBUG_REPOSITORY_MANAGER = os.getenv("DEBUG_REPOSITORY_MANAGER", "false").lower() == "true"
    DEBUG_RAG_PIPELINE = os.getenv("DEBUG_RAG_PIPELINE", "false").lower() == "true"
    DEBUG_WEBSOCKET = os.getenv("DEBUG_WEBSOCKET", "false").lower() == "true"
    
    @classmethod
    def is_debug_enabled(cls) -> bool:
        """Check if debug mode is enabled"""
        return cls.DEBUG_MODE
    
    @classmethod
    def get_debug_config(cls) -> Dict[str, Any]:
        """Get debug configuration for logging"""
        return {
            "debug_mode": cls.DEBUG_MODE,
            "log_level": cls.LOG_LEVEL,
            "repository_manager_debug": cls.DEBUG_REPOSITORY_MANAGER,
            "rag_pipeline_debug": cls.DEBUG_RAG_PIPELINE,
            "websocket_debug": cls.DEBUG_WEBSOCKET
        }
```

## Final Implementation Checklist

### Pre-Implementation
- [ ] Verify all file paths exist in current project structure
- [ ] Confirm existing model structures match documented assumptions
- [ ] Set up development environment with required dependencies
- [ ] Create feature branch for implementation
- [ ] Set up environment variables for feature flags

### Backend Implementation
- [ ] Create `backend/config/feature_flags.py`
- [ ] Extend `backend/core/exceptions.py`
- [ ] Create `backend/services/repository_manager.py`
- [ ] Extend `backend/models/chat.py` and `backend/models/common.py`
- [ ] Enhance `backend/pipelines/rag/rag_pipeline.py`
- [ ] Update `backend/websocket/wiki_handler.py`
- [ ] Extend `backend/config/settings.py`
- [ ] Create `backend/data/repositories/` directory and files
- [ ] Add new API endpoints in `backend/api/v1/`
- [ ] Create performance and security services

### Frontend Implementation
- [ ] Create `src/config/featureFlags.ts`
- [ ] Extend `src/types/repoinfo.tsx`
- [ ] Enhance `src/utils/websocketClient.ts`
- [ ] Create new components: `MultiRepositoryInput.tsx`, `RepositoryList.tsx`
- [ ] Update existing components: `Ask.tsx`, `ConfigurationModal.tsx`, `page.tsx`
- [ ] Add feature flag checks to all new functionality

### Testing and Validation
- [ ] Create `test/test_multi_repository.py`
- [ ] Test feature flag enabled/disabled states
- [ ] Test backward compatibility
- [ ] Test performance with multiple repositories
- [ ] Test error handling and fallback mechanisms
- [ ] Test WebSocket communication
- [ ] Test API endpoints

### Deployment and Monitoring
- [ ] Update `docker-compose.yml`
- [ ] Create `.env.example`
- [ ] Set up monitoring and metrics collection
- [ ] Test deployment in staging environment
- [ ] Monitor performance and error rates
- [ ] Prepare rollback plan

### Documentation
- [ ] Update API documentation
- [ ] Create user guide for multi-repository functionality
- [ ] Document troubleshooting procedures
- [ ] Update deployment instructions
- [ ] Create feature flag management guide

## Conclusion

This enhanced implementation plan now provides:

1. **Complete Implementation Details**: All missing code examples and implementation specifics
2. **AI Agent Readiness**: Step-by-step implementation sequence with clear prerequisites
3. **Comprehensive Coverage**: Database, security, performance, monitoring, and deployment
4. **Troubleshooting Guide**: Common issues and debugging procedures
5. **Final Checklist**: Complete implementation verification steps

The document is now comprehensive enough for an AI agent to implement the multi-repository feature successfully while maintaining 100% backward compatibility and system stability.
