# TASK030: Phase 4.4: Enhanced Ask Component with Feature Flag

## Task Information
- **Task ID**: TASK030
- **Task Name**: Phase 4.4: Enhanced Ask Component with Feature Flag
- **Status**: 🔴 Not Started
- **Progress**: 0%
- **Phase**: Week 5-6
- **Priority**: 🟡 Medium
- **Created**: 2024-12-19
- **Estimated Duration**: 4-5 days

## Task Description
Enhance the existing Ask component to support multiple repositories while maintaining 100% backward compatibility. This task focuses on adding feature flag checks, extending the component interface, and implementing multi-repository request handling with graceful fallback mechanisms.

## Original Request
Based on Implementation Phases section in multiple-repositories-implementation-plan-corrected.md document. Each sub-heading in the phases should create as a task instead of a large task.

## Thought Process
The implementation plan emphasizes enhancing existing components rather than replacing them. This task will extend the existing Ask component to support multi-repository functionality through feature flag protection, while maintaining all existing single-repository functionality unchanged. The approach uses the single feature flag to control component behavior and implements fallback mechanisms.

## Implementation Plan

### 1. Add Feature Flag Check for Multi-Repository Support
- **File**: `src/components/Ask.tsx` (enhance existing)
- **Purpose**: Check feature flag before enabling multi-repository functionality
- **Approach**: Import feature flags and check state before rendering

### 2. Extend Props Interface Conditionally Based on Feature Flag
- **File**: `src/components/Ask.tsx` (enhance existing)
- **Purpose**: Add multi-repository props when feature flag is enabled
- **Approach**: Conditional interface extension with feature flag protection

### 3. Add Multi-Repository Request Handling
- **File**: `src/components/Ask.tsx` (enhance existing)
- **Purpose**: Handle multi-repository requests when feature is enabled
- **Approach**: Feature flag protected with backward compatibility

### 4. Maintain 100% Backward Compatibility for Single Repository
- **File**: `src/components/Ask.tsx` (enhance existing)
- **Purpose**: Ensure existing single repository functionality works unchanged
- **Approach**: Preserve all existing methods and behavior

### 5. Add Feature Flag UI Indicators and Controls
- **File**: `src/components/Ask.tsx` (enhance existing)
- **Purpose**: Visual indicators for feature flag state
- **Approach**: Subtle UI elements showing feature availability

## Technical Specifications

### Enhanced Ask Component (Feature Flag Protected)

```typescript
// src/components/Ask.tsx - Feature flag protected extensions
import { FeatureFlags } from '@/config/featureFlags';
import { EnhancedWebSocketClient } from '@/utils/websocketClient';

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
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Feature flag state
  const isMultiRepoEnabled = FeatureFlags.isMultiRepoEnabled();
  
  // Multi-repository state (only when feature flag is enabled)
  const [repositories, setRepositories] = useState<RepositoryInfo[]>(
    isMultiRepoEnabled ? (props.repositories || []) : []
  );
  const [isMultiRepositoryMode, setIsMultiRepositoryMode] = useState(
    isMultiRepoEnabled ? false : false
  );
  
  // WebSocket client
  const wsClient = useRef<EnhancedWebSocketClient | null>(null);
  
  // Feature flag protected multi-repository handling
  const handleMultiRepositoryRequest = async (userMessage: string) => {
    if (!isMultiRepoEnabled) {
      // Fallback to single repository if feature is disabled
      await handleSingleRepositoryRequest(userMessage);
      return;
    }
    
    if (repositories.length === 0) {
      setError('No repositories configured for multi-repository mode');
      return;
    }
    
    try {
      setIsLoading(true);
      setError(null);
      
      // Create multi-repository request
      const multiRepoRequest: MultiRepositoryChatRequest = {
        repositories: repositories,
        messages: [...messages, { role: 'user', content: userMessage }],
        provider: props.provider || 'google',
        model: props.model,
        language: props.language || 'en',
        max_total_context: props.maxTotalContext || 8000,
        repository_balance: props.repositoryBalance || 'equal'
      };
      
      // Create WebSocket connection
      wsClient.current = new EnhancedWebSocketClient();
      const ws = await wsClient.current.createChatConnection(
        multiRepoRequest,
        handleWebSocketMessage,
        handleWebSocketError,
        handleWebSocketClose
      );
      
      if (!ws) {
        throw new Error('Failed to create WebSocket connection');
      }
      
      // Add user message to chat
      const newMessage: ChatMessage = {
        role: 'user',
        content: userMessage,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, newMessage]);
      
    } catch (error) {
      console.error('Multi-repository request error:', error);
      setError(`Multi-repository error: ${error.message}`);
      setIsLoading(false);
    }
  };
  
  // Always available single repository handling (backward compatibility)
  const handleSingleRepositoryRequest = async (userMessage: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Create single repository request
      const singleRepoRequest: ChatCompletionRequest = {
        repo_url: props.repoInfo.repoUrl || '',
        messages: [...messages, { role: 'user', content: userMessage }],
        provider: props.provider || 'google',
        model: props.model,
        language: props.language || 'en',
        token: props.repoInfo.token,
        type: props.repoInfo.type
      };
      
      // Create WebSocket connection
      wsClient.current = new EnhancedWebSocketClient();
      const ws = await wsClient.current.createChatConnection(
        singleRepoRequest,
        handleWebSocketMessage,
        handleWebSocketError,
        handleWebSocketClose
      );
      
      if (!ws) {
        throw new Error('Failed to create WebSocket connection');
      }
      
      // Add user message to chat
      const newMessage: ChatMessage = {
        role: 'user',
        content: userMessage,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, newMessage]);
      
    } catch (error) {
      console.error('Single repository request error:', error);
      setError(`Request error: ${error.message}`);
      setIsLoading(false);
    }
  };
  
  // Unified request handler
  const handleSubmit = async (userMessage: string) => {
    if (isMultiRepoEnabled && isMultiRepositoryMode && repositories.length > 0) {
      await handleMultiRepositoryRequest(userMessage);
    } else {
      await handleSingleRepositoryRequest(userMessage);
    }
  };
  
  // WebSocket message handlers
  const handleWebSocketMessage = (data: any) => {
    try {
      if (data.type === 'message') {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: data.data.content,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else if (data.type === 'status') {
        // Handle status updates
        console.log('Status update:', data.data);
      } else if (data.type === 'error') {
        setError(data.data.message);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error handling WebSocket message:', error);
    }
  };
  
  const handleWebSocketError = (error: Event) => {
    console.error('WebSocket error:', error);
    setError('WebSocket connection error');
    setIsLoading(false);
  };
  
  const handleWebSocketClose = () => {
    console.log('WebSocket connection closed');
    setIsLoading(false);
  };
  
  // Clear conversation
  const clearConversation = () => {
    setMessages([]);
    setError(null);
    if (wsClient.current) {
      wsClient.current.closeConnection();
    }
  };
  
  // Expose clear function via ref
  useImperativeHandle(props.onRef, () => ({
    clearConversation
  }));
  
  return (
    <div className="ask-component">
      {/* Feature flag indicator (subtle) */}
      {isMultiRepoEnabled && (
        <div className="feature-flag-indicator">
          <span className="text-sm text-gray-500">
            Multi-repository mode available
          </span>
        </div>
      )}
      
      {/* Multi-repository mode toggle (only when feature flag is enabled) */}
      {isMultiRepoEnabled && (
        <div className="multi-repository-toggle mb-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={isMultiRepositoryMode}
              onChange={(e) => setIsMultiRepositoryMode(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm">Enable Multi-Repository Mode</span>
          </label>
        </div>
      )}
      
      {/* Repository list (only when multi-repository mode is enabled) */}
      {isMultiRepoEnabled && isMultiRepositoryMode && (
        <div className="repository-list mb-4">
          <h3 className="text-lg font-medium mb-2">Repositories</h3>
          {repositories.length === 0 ? (
            <p className="text-gray-500">No repositories configured</p>
          ) : (
            <div className="space-y-2">
              {repositories.map((repo, index) => (
                <div key={index} className="flex items-center space-x-2 p-2 bg-gray-50 rounded">
                  <span className="text-sm font-medium">
                    {repo.alias || `${repo.owner}/${repo.repo}`}
                  </span>
                  {repo.priority_weight && (
                    <span className="text-xs text-gray-500">
                      Priority: {repo.priority_weight}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      {/* Chat messages */}
      <div className="chat-messages mb-4">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">{message.content}</div>
            <div className="message-timestamp text-xs text-gray-500">
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>
      
      {/* Error display */}
      {error && (
        <div className="error-message mb-4 p-3 bg-red-100 border border-red-300 rounded text-red-700">
          {error}
        </div>
      )}
      
      {/* Input form */}
      <form onSubmit={(e) => {
        e.preventDefault();
        const input = e.currentTarget.elements.namedItem('message') as HTMLInputElement;
        if (input.value.trim()) {
          handleSubmit(input.value.trim());
          input.value = '';
        }
      }}>
        <div className="flex space-x-2">
          <input
            type="text"
            name="message"
            placeholder="Ask a question..."
            className="flex-1 p-2 border border-gray-300 rounded"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
      
      {/* Loading indicator */}
      {isLoading && (
        <div className="loading-indicator mt-4 text-center text-gray-500">
          Processing request...
        </div>
      )}
    </div>
  );
};

export default Ask;
```

### Backward Compatibility Requirements
- Existing single-repository functionality must work 100% unchanged
- All existing component props must remain functional
- No breaking changes to existing component interface
- Feature flag fallback must work seamlessly

## Subtasks

### Subtask 1: Feature Flag Integration
- [ ] Import and integrate feature flags
- [ ] Add feature flag check logic
- [ ] Implement fallback mechanisms
- [ ] Test feature flag disabled state
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 2: Interface Extension
- [ ] Extend props interface conditionally
- [ ] Add multi-repository props
- [ ] Implement conditional prop handling
- [ ] Test interface compatibility
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 3: Multi-Repository Request Handling
- [ ] Implement multi-repository request logic
- [ ] Add WebSocket integration
- [ ] Implement parallel processing support
- [ ] Test multi-repository functionality
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 4: Backward Compatibility Testing
- [ ] Test existing single repository functionality
- [ ] Verify component behavior unchanged
- [ ] Test feature flag fallback mechanisms
- [ ] Validate error handling unchanged
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

## Dependencies
- TASK027: Phase 4.1: Frontend Feature Flag Infrastructure
- TASK028: Phase 4.2: Enhanced Type Definitions with Feature Flag Protection
- TASK029: Phase 4.3: Enhanced WebSocket Client with Feature Flag
- Existing Ask component implementation

## Deliverables
1. Enhanced `src/components/Ask.tsx` with multi-repository support
2. Feature flag protected component functionality
3. Multi-repository request handling
4. Backward compatibility mechanisms
5. Comprehensive testing for both single and multi-repository scenarios
6. Error handling and fallback mechanisms

## Success Criteria
- [ ] Multi-repository functionality works when feature flag is enabled
- [ ] Single repository functionality works unchanged when feature flag is disabled
- [ ] Feature flag fallback mechanisms work correctly
- [ ] Multi-repository request handling is functional
- [ ] All existing tests continue passing
- [ ] New tests cover multi-repository scenarios
- [ ] Component behavior remains consistent

## Progress Log

### 2024-12-19 - Task Created
- Task created based on Implementation Phases section
- Implementation plan defined
- Subtasks identified and structured
- Dependencies identified

## Notes
- Must maintain 100% backward compatibility
- Feature flag integration is critical for component behavior
- Multi-repository request handling should be robust
- Fallback mechanisms should be seamless
- All existing component functionality must remain intact
- UI should clearly indicate feature availability
