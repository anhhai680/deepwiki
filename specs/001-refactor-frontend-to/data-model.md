# Data Model: Quick Access Ask UI from Home Page

## Core Entities

### HomePageAskState
**Purpose**: Manages the state for Ask UI integration on home page
**Fields**:
- `selectedRepositories: string[]` - Array of selected repository URLs
- `isMultiRepositoryMode: boolean` - Toggle between single/multi repository modes
- `askVisible: boolean` - Controls visibility of Ask UI section
- `isLoading: boolean` - Loading state for Ask operations

**Relationships**:
- Contains repository context passed to Ask component
- Integrates with existing home page state

**Validation Rules**:
- At least one repository must be selected before asking questions
- Repository URLs must be valid GitHub/GitLab/BitBucket format
- Multi-repository mode requires selectedRepositories.length >= 1

**State Transitions**:
```
Initial → Repository Selected → Ask Ready → Asking → Response Received
   ↓           ↓                 ↓          ↓           ↓
Empty      Single/Multi      Enabled    Loading    Complete
```

### RepositoryContext (From existing codebase)
**Purpose**: Repository information passed to Ask component (defined in `src/types/repoinfo.tsx`)
**Fields**:
- `owner: string` - Repository owner/organization
- `repo: string` - Repository name  
- `type: 'github' | 'gitlab' | 'bitbucket' | 'local'` - Platform type
- `token?: string | null` - Access token if required
- `localPath?: string | null` - Local path for local repositories
- `repoUrl?: string | null` - Full repository URL

**Relationships**:
- Created from selected repository URLs via RepositorySelector
- Passed to Ask.tsx component as `repoInfo` prop
- Sourced from processed projects via useProcessedProjects hook

### ProcessedProject (From existing codebase)
**Purpose**: Repository data from processed projects (used in RepositorySelector)
**Fields**:
- `id: string` - Unique project identifier
- `owner: string` - Repository owner
- `repo: string` - Repository name
- `name: string` - Display name
- `repo_type: string` - Platform type
- `submittedAt: number` - Timestamp
- `language: string` - Programming language

### AskRequest (Reused from existing)
**Purpose**: Request structure for Ask API calls
**Fields**:
- `repo_url: string | string[]` - Single or multiple repository URLs
- `messages: ChatMessage[]` - Conversation history
- `provider: string` - AI provider selection
- `model: string` - AI model selection
- `language: string` - Response language
- Additional existing Ask.tsx fields

## Component Props Interfaces

### HomePageAskProps (New component)
```typescript
interface HomePageAskProps {
  projects: ProcessedProject[]; // From useProcessedProjects hook
  className?: string;
}
```

### Ask Component Props (Existing from src/components/Ask.tsx)
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

## State Flow

### Repository Selection Flow
1. User interacts with RepositorySelector
2. RepositorySelector calls onRepositoryChange
3. HomePageAsk updates selectedRepositories state
4. Ask component receives new repository context
5. Ask component is ready for user questions

### Multi-Repository Toggle Flow
1. User toggles multi-repository mode
2. Component switches between RepositorySelector and MultiRepositorySelector
3. Selected repositories are preserved where possible
4. Ask component receives updated repository array

### Ask Interaction Flow
1. User types question in Ask input
2. Ask component validates repository selection
3. Ask component sends request with repository context
4. Response is displayed in Ask component
5. Conversation history is maintained

## Error Handling

### Repository Selection Errors
- Invalid repository URL format
- Repository not accessible/not found
- Authentication required but not provided
- Network errors during repository validation

### Ask Request Errors
- No repository selected
- API rate limiting
- Authentication failures
- Network connectivity issues
- Invalid AI provider/model configuration

## Performance Considerations

### State Management
- Minimize re-renders by using appropriate React hooks
- Memoize expensive operations (repository URL validation)
- Debounce repository selection changes

### Component Loading
- Lazy load Ask component until needed
- Progressive enhancement - show repository selector first
- Graceful degradation for API failures

## Integration Points

### Home Page Integration
- HomePageAsk component added to existing page.tsx
- Positioned after repository input form
- Uses existing page styling and theme context

### Ask Component Integration
- Reuse existing Ask.tsx without modifications
- Pass repository context via props
- Maintain existing Ask functionality and APIs

### Repository Selector Integration
- Reuse RepositorySelector.tsx and MultiRepositorySelector.tsx
- Maintain existing repository selection patterns
- Integrate with processed projects data
