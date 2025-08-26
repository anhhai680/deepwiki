# Multiple Repositories Implementation Plan

## Overview

This document outlines the comprehensive implementation plan for adding multi-repository support to the DeepWiki Chat UI Interface. The goal is to enable users to query and analyze code across multiple repositories simultaneously while maintaining backward compatibility with existing single-repository functionality.

## Table of Contents

1. [Project Scope](#project-scope)
2. [Architecture Overview](#architecture-overview)
3. [Implementation Phases](#implementation-phases)
4. [Technical Specifications](#technical-specifications)
5. [Testing Strategy](#testing-strategy)
6. [Migration Plan](#migration-plan)
7. [Risk Assessment](#risk-assessment)
8. [Success Criteria](#success-criteria)

## Project Scope

### Objectives
- Enable Chat UI to support multiple repositories in a single conversation
- Maintain backward compatibility with existing single-repository functionality
- Provide per-repository configuration options (filters, tokens, platform types)
- Enhance AI analysis capabilities across multiple codebases
- Improve user experience for cross-repository code analysis

### Out of Scope
- Repository dependency management
- Cross-repository version control
- Repository synchronization or mirroring
- Advanced repository relationship mapping

## Architecture Overview

### Current Architecture

```markdown:docs/multiple-repositories-implementation-plan.md
<code_block_to_apply_changes_from>
Single Repository Flow:
User Input → Single RAG Instance → Single Context → AI Response
```

### Target Architecture
```
Multiple Repositories Flow:
User Input → Multiple RAG Instances → Merged Context → AI Response
```

### Key Components to Modify
1. **Backend**: `websocket_wiki.py` - Core WebSocket handler
2. **Frontend**: Repository input components and configuration modals
3. **Data Models**: Request/response structures and validation
4. **RAG System**: Multi-repository document retrieval and context merging

## Implementation Phases

### Phase 1: Backend Foundation (Week 1-2)

#### 1.1 Update Data Models
- **File**: `api/websocket_wiki.py`
- **Tasks**:
  - Create `RepositoryInfo` Pydantic model
  - Update `ChatCompletionRequest` to support multiple repositories
  - Add backward compatibility validator for single repository URLs
  - Implement field validation and error handling

#### 1.2 Enhance RAG Handling
- **File**: `api/websocket_wiki.py`
- **Tasks**:
  - Modify RAG instance creation to handle multiple repositories
  - Implement multi-repository document retrieval
  - Add repository-aware context merging
  - Update system prompts for multi-repository scenarios

#### 1.3 Context Merging Logic
- **File**: `api/websocket_wiki.py`
- **Tasks**:
  - Implement document grouping by repository and file path
  - Add repository metadata to document context
  - Create structured context formatting for AI consumption
  - Handle repository-specific filtering and inclusion

### Phase 2: Frontend Components (Week 3-4)

#### 2.1 Repository Input Component
- **File**: `src/components/RepositoryInput.tsx`
- **Tasks**:
  - Create dynamic repository list management
  - Implement add/remove repository functionality
  - Add per-repository configuration options
  - Include repository type selection (GitHub, GitLab, Bitbucket)
  - Add per-repository token and filter inputs

#### 2.2 Configuration Modal Updates
- **File**: `src/components/ConfigurationModal.tsx`
- **Tasks**:
  - Integrate RepositoryInput component
  - Update prop interfaces for multi-repository support
  - Maintain existing functionality while adding new features
  - Add validation for repository configurations

#### 2.3 Ask Component Updates
- **File**: `src/components/Ask.tsx`
- **Tasks**:
  - Update component props to accept repository list
  - Modify WebSocket request structure
  - Maintain existing conversation flow
  - Add repository context to user interface

### Phase 3: Integration and State Management (Week 5-6)

#### 3.1 Main Page Updates
- **File**: `src/app/page.tsx`
- **Tasks**:
  - Add repository state management
  - Implement repository CRUD operations
  - Add repository configuration handlers
  - Update component prop passing

#### 3.2 WebSocket Client Updates
- **File**: `src/utils/websocketClient.ts`
- **Tasks**:
  - Update interface definitions
  - Modify request structure for multiple repositories
  - Maintain backward compatibility
  - Add type safety for new structures

#### 3.3 State Persistence
- **Tasks**:
  - Update localStorage caching for multiple repositories
  - Implement repository configuration persistence
  - Add migration logic for existing single-repository configs
  - Handle configuration versioning

### Phase 4: Testing and Validation (Week 7-8)

#### 4.1 Unit Testing
- **Tasks**:
  - Test new data models and validation
  - Verify RAG multi-repository functionality
  - Test context merging algorithms
  - Validate backward compatibility

#### 4.2 Integration Testing
- **Tasks**:
  - Test end-to-end multi-repository flows
  - Verify WebSocket communication
  - Test configuration persistence
  - Validate error handling

#### 4.3 User Experience Testing
- **Tasks**:
  - Test UI responsiveness with multiple repositories
  - Validate configuration workflows
  - Test error scenarios and edge cases
  - Gather user feedback on new features

## Technical Specifications

### Backend Changes

#### Data Models
```python
class RepositoryInfo(BaseModel):
    url: str = Field(..., description="Repository URL")
    type: str = Field("github", description="Repository platform type")
    token: Optional[str] = Field(None, description="Access token")
    excluded_dirs: Optional[str] = Field(None, description="Excluded directories")
    excluded_files: Optional[str] = Field(None, description="Excluded files")
    included_dirs: Optional[str] = Field(None, description="Included directories")
    included_files: Optional[str] = Field(None, description="Included files")

class ChatCompletionRequest(BaseModel):
    repositories: List[RepositoryInfo] = Field(..., description="Repository list")
    messages: List[ChatMessage] = Field(..., description="Chat messages")
    filePath: Optional[str] = Field(None, description="File path context")
    provider: str = Field("google", description="AI model provider")
    model: Optional[str] = Field(None, description="AI model name")
    language: Optional[str] = Field("en", description="Response language")
    
    @field_validator('repositories', mode='before')
    @classmethod
    def validate_repositories(cls, v):
        if isinstance(v, str):
            return [RepositoryInfo(url=v, type="github")]
        return v
```

#### RAG Multi-Repository Handling
```python
# Create RAG instances for all repositories
rag_instances = []
for repo_info in request.repositories:
    repo_rag = RAG(provider=request.provider, model=request.model)
    repo_rag.prepare_retriever(
        repo_info.url, 
        repo_info.type, 
        repo_info.token,
        repo_info.excluded_dirs,
        repo_info.excluded_files,
        repo_info.included_dirs,
        repo_info.included_files
    )
    rag_instances.append(repo_rag)

# Retrieve and merge documents from all repositories
all_documents = []
for i, repo_rag in enumerate(rag_instances):
    retrieved_docs = repo_rag(rag_query, language=request.language)
    if retrieved_docs and retrieved_docs[0].documents:
        for doc in retrieved_docs[0].documents:
            doc.meta_data['repository_index'] = i
            doc.meta_data['repository_url'] = request.repositories[i].url
        all_documents.extend(retrieved_docs[0].documents)
```

### Frontend Changes

#### Repository Input Component
```typescript
interface RepositoryInfo {
  url: string;
  type: 'github' | 'gitlab' | 'bitbucket';
  token?: string;
  excludedDirs?: string;
  excludedFiles?: string;
  includedDirs?: string;
  includedFiles?: string;
}

interface RepositoryInputProps {
  repositories: RepositoryInfo[];
  onRepositoriesChange: (repos: RepositoryInfo[]) => void;
  onRepositoryTypeChange: (index: number, type: 'github' | 'gitlab' | 'bitbucket') => void;
  onRepositoryTokenChange: (index: number, token: string) => void;
  onRepositoryFiltersChange: (index: number, filters: Partial<RepositoryInfo>) => void;
}
```

#### State Management
```typescript
const [repositories, setRepositories] = useState<RepositoryInfo[]>([
  { url: '', type: 'github' }
]);

const addRepository = () => {
  setRepositories([...repositories, { url: '', type: 'github' }]);
};

const removeRepository = (index: number) => {
  const newRepos = repositories.filter((_, i) => i !== index);
  setRepositories(newRepos);
};
```

## Testing Strategy

### Test Categories

#### 1. Unit Tests
- **Data Model Validation**: Test Pydantic models and validators
- **RAG Functionality**: Test multi-repository document retrieval
- **Context Merging**: Test document grouping and formatting
- **Error Handling**: Test validation and error scenarios

#### 2. Integration Tests
- **WebSocket Communication**: Test end-to-end request/response flow
- **Repository Management**: Test CRUD operations and persistence
- **Configuration Handling**: Test multi-repository settings
- **Backward Compatibility**: Test single-repository requests

#### 3. User Experience Tests
- **UI Responsiveness**: Test with various repository counts
- **Configuration Workflows**: Test setup and modification flows
- **Error Scenarios**: Test validation and error messages
- **Performance**: Test with large repository lists

### Test Data
- Single repository scenarios
- Multiple repositories (2-5 repositories)
- Mixed repository types (GitHub, GitLab, Bitbucket)
- Various file filter configurations
- Different token configurations

## Migration Plan

### Phase 1: Backward Compatibility
- Maintain existing single-repository API endpoints
- Add field validators for automatic conversion
- Ensure existing frontend continues to work

### Phase 2: Feature Rollout
- Deploy backend changes with feature flags
- Update frontend components incrementally
- Add user guidance for new features

### Phase 3: Full Migration
- Enable multi-repository features by default
- Deprecate single-repository endpoints (future)
- Update documentation and user guides

## Risk Assessment

### High Risk
- **Performance Impact**: Multiple RAG instances may increase response time
- **Memory Usage**: Large repository lists may consume significant memory
- **Complexity**: Multi-repository logic increases system complexity

### Medium Risk
- **User Experience**: Complex configuration may confuse users
- **Error Handling**: Multiple failure points in repository processing
- **Testing Coverage**: Comprehensive testing required for all scenarios

### Low Risk
- **Backward Compatibility**: Existing functionality should remain intact
- **Data Loss**: No existing data will be affected
- **API Changes**: Changes are additive, not breaking

### Mitigation Strategies
- **Performance**: Implement request batching and caching
- **Memory**: Add repository limits and cleanup mechanisms
- **Complexity**: Comprehensive documentation and user guides
- **Testing**: Extensive automated and manual testing

## Success Criteria

### Functional Requirements
- [ ] Users can add/remove repositories dynamically
- [ ] Each repository supports individual configuration
- [ ] AI responses include context from all repositories
- [ ] Backward compatibility maintained for single repositories
- [ ] Configuration persistence works correctly

### Performance Requirements
- [ ] Response time increase < 50% for 2-3 repositories
- [ ] Memory usage increase < 100% for 2-3 repositories
- [ ] UI remains responsive with up to 5 repositories
- [ ] Error handling graceful for repository failures

### User Experience Requirements
- [ ] Intuitive repository management interface
- [ ] Clear configuration options for each repository
- [ ] Helpful error messages and validation feedback
- [ ] Smooth transition from single to multiple repositories

## Timeline

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1-2  | Backend Foundation | Data models, RAG updates, context merging |
| 3-4  | Frontend Components | RepositoryInput, modal updates, Ask component |
| 5-6  | Integration | State management, WebSocket updates, persistence |
| 7-8  | Testing | Unit tests, integration tests, user testing |
| 9    | Documentation | User guides, API documentation, migration guides |
| 10   | Deployment | Production deployment, monitoring, user feedback |

## Dependencies

### External Dependencies
- Pydantic validation library
- FastAPI WebSocket support
- React state management patterns

### Internal Dependencies
- Existing RAG system architecture
- Current WebSocket client implementation
- Configuration persistence mechanisms

### Team Dependencies
- Backend developer for API changes
- Frontend developer for UI components
- QA engineer for testing and validation
- DevOps engineer for deployment and monitoring

## Conclusion

This implementation plan provides a comprehensive roadmap for adding multi-repository support to the DeepWiki Chat UI Interface. The phased approach ensures minimal disruption to existing functionality while delivering new capabilities incrementally. The focus on backward compatibility and user experience will ensure a smooth transition for existing users while enabling new use cases for cross-repository code analysis.

The plan addresses technical challenges, provides clear success criteria, and includes comprehensive testing strategies to ensure quality delivery. Regular reviews and adjustments should be made throughout the implementation to address any unforeseen challenges or opportunities for improvement.
```

I've recreated the comprehensive implementation plan document at `docs/multiple-repositories-implementation-plan.md`. This document provides a complete roadmap for implementing multi-repository support in the DeepWiki Chat UI Interface.

## Key Features of the Plan:

1. **Structured Implementation**: Organized into 4 main phases with clear deliverables
2. **Technical Specifications**: Detailed code examples and architecture changes
3. **Comprehensive Testing**: Covers unit, integration, and user experience testing
4. **Risk Management**: Identifies potential challenges and mitigation strategies
5. **Timeline**: 10-week implementation schedule with specific milestones
6. **Success Criteria**: Measurable goals for functionality, performance, and user experience

## Implementation Highlights:

- **Phase 1**: Backend foundation with data models and RAG updates
- **Phase 2**: Frontend components for repository management
- **Phase 3**: Integration and state management
- **Phase 4**: Testing and validation

The plan maintains backward compatibility while adding powerful new multi-repository capabilities, ensuring existing users can continue using the system while new features are gradually introduced.
