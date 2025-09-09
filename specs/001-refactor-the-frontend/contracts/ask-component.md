# Ask Component Contract

**File**: `src/components/Ask.tsx` (1,062 lines → target: <500 lines)  
**Purpose**: Chat/Q&A interface for repository analysis

## Public API Contract

### Props Interface
```typescript
interface AskProps {
  repoInfo: RepoInfo | RepoInfo[];
  projects?: ProcessedProject[];
}
```

**Requirements**:
- MUST accept both single RepoInfo and array of RepoInfo
- MUST handle optional projects parameter
- MUST maintain backward compatibility with existing usage

### Component Behavior

#### Chat Functionality
- MUST provide text input for user questions
- MUST display conversation history with user/assistant messages
- MUST support markdown rendering in responses
- MUST handle streaming responses via WebSocket connection
- MUST maintain message order and threading

#### Model Selection
- MUST allow selection of AI model provider
- MUST support custom model input when provider supports it
- MUST persist model selection across sessions
- MUST validate model availability before use

#### Multi-Repository Support
- MUST handle single and multiple repository contexts
- MUST display repository selector when multiple repos provided
- MUST maintain context across repository switches
- MUST indicate active repository in conversation

#### Export Functionality
- MUST provide export conversation to markdown
- MUST include timestamp and repository context in exports
- MUST handle large conversations without performance issues

## State Management Contract

### Internal State Requirements
- Chat message history (Message[])
- Current model selection (provider + model)
- Repository context (active repo from props)
- UI state (loading, error states)
- WebSocket connection status

### State Persistence
- Model selection persists via localStorage
- Chat history maintained during session
- Repository context follows prop changes

## Integration Points

### WebSocket Communication
- MUST use existing websocketClient utility
- MUST handle connection failures gracefully
- MUST support message streaming and parsing
- MUST maintain connection lifecycle management

### Model Configuration
- MUST integrate with ModelSelectionModal component
- MUST respect global model configuration
- MUST validate model availability via API

### Repository Integration
- MUST work with MultiRepositorySelector component
- MUST extract repository metadata for context
- MUST handle repository URL validation

## Performance Requirements

### Response Time
- Initial render: <100ms
- Message submission: <50ms response time
- Model switching: <200ms

### Memory Management
- Chat history limited to reasonable size (configurable)
- Efficient re-rendering with React optimizations
- Proper cleanup on unmount

## Error Handling

### Required Error States
- WebSocket connection failures
- Model unavailability
- Invalid repository information
- Network timeouts
- Malformed responses

### Error Recovery
- Automatic reconnection attempts for WebSocket
- Fallback model selection
- Graceful degradation when features unavailable
- User feedback for all error conditions

## Accessibility Requirements

- Keyboard navigation support
- Screen reader compatibility
- Focus management for modal interactions
- Color contrast compliance
- ARIA labels for interactive elements

## Test Scenarios

### Critical Path Tests
1. **Basic Chat Flow**
   - User enters question → receives response
   - Message history maintained correctly
   - Markdown rendering works properly

2. **Model Selection**
   - Can change provider and model
   - Custom model input functions
   - Selection persists across reloads

3. **Multi-Repository Handling**
   - Switches between repositories correctly
   - Maintains separate contexts
   - Repository selector functions properly

4. **Export Functionality**
   - Exports complete conversation
   - Includes proper metadata
   - Handles empty/large conversations

### Edge Case Tests
- Empty repository list handling
- Network disconnection recovery
- Invalid model selection recovery
- Large message handling
- Concurrent message handling

## Refactoring Constraints

### What CAN Be Changed
- Internal component structure and organization
- State management implementation details
- Styling and layout (preserving visual consistency)
- Performance optimizations
- Code organization and file splitting

### What MUST NOT Change
- Public props interface (AskProps)
- Component export name and location
- Core user interaction flows
- Integration with parent components
- WebSocket message protocols
- Export file format

## Migration Strategy

1. **Phase 1**: Extract utilities and hooks while preserving main component
2. **Phase 2**: Split UI components while maintaining container structure  
3. **Phase 3**: Optimize internal organization without changing external interface
4. **Phase 4**: Remove legacy code after thorough testing
