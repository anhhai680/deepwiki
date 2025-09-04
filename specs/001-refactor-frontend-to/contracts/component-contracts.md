# Component Contracts: Quick Access Ask UI from Home Page

## HomePageAsk Component Contract

### Component Interface
```typescript
interface HomePageAskProps {
  projects: ProcessedProject[]; // From useProcessedProjects hook
  className?: string;
}

interface HomePageAskState {
  selectedRepository: string;
  repoInfo: RepoInfo | null;
  showAskSection: boolean;
}
```

### Expected Behavior
- **Input**: Receives projects list from useProcessedProjects hook
- **Output**: Renders repository selection + Ask UI section
- **State**: Manages repository selection and Ask visibility
- **Integration**: Uses existing RepositorySelector and Ask components

### Component Lifecycle
1. Mount: Initialize with no repository selected
2. Repository Selection: Convert selected repo to RepoInfo format
3. Ask Integration: Pass RepoInfo to existing Ask component
4. Unmount: Clean up state

## Ask Component Integration Contract (Existing)

### Props Interface (From src/components/Ask.tsx)
```typescript
interface AskProps {
  repoInfo: RepoInfo | RepoInfo[];
  projects?: ProcessedProject[];
  provider?: string;
  model?: string;
  isCustomModel?: boolean;
  customModel?: string;
  language?: string;
  onRef?: (ref: { clearConversation: () => void }) => void;
}
```

### Expected Behavior
- **Compatibility**: 100% compatibility with existing Ask.tsx implementation
- **Repository Context**: Handle single or multiple repositories via repoInfo prop
- **State**: Maintain conversation state independently
- **Features**: Multi-repository mode, deep research, model selection (all existing features)

## RepositorySelector Integration Contract

### Props Interface
```typescript
interface RepositorySelectorIntegrationProps {
  projects: ProcessedProject[];
  selectedRepository: string;
  onRepositorySelect: (repo: string) => void;
  multiMode: boolean;
  selectedRepositories?: string[];
  onRepositoriesChange?: (repos: string[]) => void;
}
```

### Expected Behavior
- **Single Mode**: Use RepositorySelector.tsx as-is
- **Multi Mode**: Use MultiRepositorySelector.tsx
- **Fallback**: Support manual URL input
- **Validation**: Validate repository URL format

## Ask Component Integration Contract

### Props Pass-through
```typescript
interface AskIntegrationProps {
  repoInfo: RepoInfo | RepoInfo[];
  projects: ProcessedProject[];
  provider: string;
  model: string;
  language: string;
  // All existing Ask.tsx props maintained
}
```

### Expected Behavior
- **Compatibility**: 100% compatibility with existing Ask.tsx
- **Repository Context**: Handle single or multiple repositories
- **State**: Maintain conversation state independently
- **Events**: Handle Ask-specific user interactions

## Event Contracts

### Repository Selection Events
```typescript
type RepositorySelectionEvent = {
  type: 'single' | 'multi';
  repositories: string[];
  timestamp: number;
};

type RepositoryValidationEvent = {
  type: 'validation';
  repository: string;
  isValid: boolean;
  error?: string;
};
```

### Ask Interaction Events
```typescript
type AskRequestEvent = {
  type: 'ask_request';
  repositories: string[];
  question: string;
  provider: string;
  model: string;
};

type AskResponseEvent = {
  type: 'ask_response';
  success: boolean;
  response?: string;
  error?: string;
};
```

## Error Handling Contracts

### Repository Selection Errors
```typescript
interface RepositorySelectionError {
  type: 'repository_error';
  code: 'invalid_url' | 'not_found' | 'auth_required' | 'network_error';
  message: string;
  repository: string;
}
```

### Ask Request Errors
```typescript
interface AskRequestError {
  type: 'ask_error';
  code: 'no_repository' | 'auth_failed' | 'rate_limit' | 'network_error' | 'api_error';
  message: string;
  context?: any;
}
```

## Performance Contracts

### Component Performance
- **Mount Time**: < 100ms for initial render
- **Repository Selection**: < 50ms response to user input
- **State Updates**: Debounced to prevent excessive re-renders
- **Memory Usage**: No memory leaks from event listeners

### Ask Component Performance
- **Integration Overhead**: < 10ms additional latency
- **Repository Context**: Efficient conversion from URLs to RepoInfo
- **State Synchronization**: Minimal impact on existing Ask performance

## Testing Contracts

### Unit Test Requirements
- Component renders without errors
- Repository selection updates state correctly
- Multi-repository toggle works as expected
- Error states are handled gracefully

### Integration Test Requirements
- HomePageAsk integrates with home page layout
- Repository selection flows work end-to-end
- Ask component receives correct repository context
- Authentication state is passed through correctly

### End-to-End Test Requirements
- User can select repositories and ask questions
- Multi-repository mode functions correctly
- Error messages are displayed appropriately
- Performance requirements are met
