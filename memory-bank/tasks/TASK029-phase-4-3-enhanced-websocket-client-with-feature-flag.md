# TASK029: Phase 4.3: Enhanced WebSocket Client with Feature Flag

## Task Information
- **Task ID**: TASK029
- **Task Name**: Phase 4.3: Enhanced WebSocket Client with Feature Flag
- **Status**: 🔴 Not Started
- **Progress**: 0%
- **Phase**: Week 5-6
- **Priority**: 🟡 Medium
- **Created**: 2024-12-19
- **Estimated Duration**: 4-5 days

## Task Description
Enhance the existing WebSocket client to support multiple repositories while maintaining 100% backward compatibility. This task focuses on adding feature flag checks, extending the WebSocket client interface, and implementing multi-repository WebSocket support with graceful fallback mechanisms.

## Original Request
Based on Implementation Phases section in multiple-repositories-implementation-plan-corrected.md document. Each sub-heading in the phases should create as a task instead of a large task.

## Thought Process
The implementation plan emphasizes enhancing existing components rather than replacing them. This task will extend the existing WebSocket client to support multi-repository functionality through feature flag protection, while maintaining all existing single-repository functionality unchanged. The approach uses the single feature flag to control WebSocket client behavior and implements fallback mechanisms.

## Implementation Plan

### 1. Add Feature Flag Check Before Enabling Multi-Repository
- **File**: `src/utils/websocketClient.ts` (enhance existing)
- **Purpose**: Check feature flag before enabling multi-repository functionality
- **Approach**: Import feature flags and check state before processing

### 2. Extend ChatCompletionRequest Interface Conditionally
- **File**: `src/utils/websocketClient.ts` (enhance existing)
- **Purpose**: Extend existing interface with multi-repository support
- **Approach**: Conditional interface extension based on feature flag

### 3. Add Multi-Repository WebSocket Support
- **File**: `src/utils/websocketClient.ts` (enhance existing)
- **Purpose**: Support for multi-repository WebSocket connections
- **Approach**: Feature flag protected with backward compatibility

### 4. Maintain Existing Single Repository Functionality
- **File**: `src/utils/websocketClient.ts` (enhance existing)
- **Purpose**: Ensure existing functionality works unchanged
- **Approach**: Preserve all existing methods and behavior

### 5. Add Fallback Mechanisms for Disabled Feature
- **File**: `src/utils/websocketClient.ts` (enhance existing)
- **Purpose**: Graceful degradation when feature is disabled
- **Approach**: Automatic fallback to single repository mode

## Technical Specifications

### Enhanced WebSocket Client (Feature Flag Protected)

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
  
  try {
    // Create WebSocket connection for multi-repository request
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8000/ws');
    
    ws.onopen = () => {
      // Send multi-repository request
      ws.send(JSON.stringify({
        type: 'multi_repository_chat',
        data: request
      }));
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        onError(new Error('Failed to parse WebSocket message'));
      }
    };
    
    ws.onerror = onError;
    ws.onclose = onClose;
    
    return ws;
  } catch (error) {
    console.error('Failed to create multi-repository WebSocket:', error);
    return null;
  }
};

// Enhanced WebSocket client with feature flag support
export class EnhancedWebSocketClient {
  private ws: WebSocket | null = null;
  private isMultiRepositoryMode: boolean = false;
  
  constructor() {
    this.isMultiRepositoryMode = FeatureFlags.isMultiRepoEnabled();
  }
  
  /**
   * Create WebSocket connection for chat requests
   * Automatically handles single vs multi-repository based on feature flag
   */
  async createChatConnection(
    request: ChatCompletionRequest | MultiRepositoryChatRequest,
    onMessage: (message: string) => void,
    onError: (error: Event) => void,
    onClose: () => void
  ): Promise<WebSocket | null> {
    
    // Check if this is a multi-repository request
    if (this.isMultiRepositoryMode && 'repositories' in request) {
      // Multi-repository request
      return createMultiRepositoryWebSocket(
        request as MultiRepositoryChatRequest,
        onMessage,
        onError,
        onClose
      );
    } else {
      // Single repository request (always supported for backward compatibility)
      return this.createSingleRepositoryConnection(
        request as ChatCompletionRequest,
        onMessage,
        onError,
        onClose
      );
    }
  }
  
  /**
   * Create single repository WebSocket connection (existing functionality)
   */
  private createSingleRepositoryConnection(
    request: ChatCompletionRequest,
    onMessage: (message: string) => void,
    onError: (error: Event) => void,
    onClose: () => void
  ): WebSocket {
    
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8000/ws');
    
    ws.onopen = () => {
      // Send single repository request
      ws.send(JSON.stringify({
        type: 'chat',
        data: request
      }));
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        onError(new Error('Failed to parse WebSocket message'));
      }
    };
    
    ws.onerror = onError;
    ws.onclose = onClose;
    
    return ws;
  }
  
  /**
   * Check if multi-repository mode is available
   */
  isMultiRepositoryAvailable(): boolean {
    return this.isMultiRepositoryMode;
  }
  
  /**
   * Get current feature flag status
   */
  getFeatureFlagStatus() {
    return FeatureFlags.getFeatureFlagStatus();
  }
  
  /**
   * Close current WebSocket connection
   */
  closeConnection() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
  
  /**
   * Send message through current WebSocket connection
   */
  sendMessage(message: any): boolean {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
      return true;
    }
    return false;
  }
  
  /**
   * Get connection status
   */
  getConnectionStatus(): 'connecting' | 'open' | 'closing' | 'closed' | 'none' {
    if (!this.ws) return 'none';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting';
      case WebSocket.OPEN: return 'open';
      case WebSocket.CLOSING: return 'closing';
      case WebSocket.CLOSED: return 'closed';
      default: return 'none';
    }
  }
}

// Utility functions for feature flag checking
export const canUseMultiRepository = (): boolean => {
  return FeatureFlags.isMultiRepoEnabled();
};

export const getWebSocketRequestType = (request: any): 'single' | 'multi' => {
  if (FeatureFlags.isMultiRepoEnabled() && 'repositories' in request) {
    return 'multi';
  }
  return 'single';
};

// Default export for backward compatibility
export default EnhancedWebSocketClient;
```

### Backward Compatibility Requirements
- Existing single-repository functionality must work 100% unchanged
- All existing WebSocket connections must remain stable
- No breaking changes to existing method signatures
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
- [ ] Extend ChatCompletionRequest interface
- [ ] Add MultiRepositoryChatRequest interface
- [ ] Implement conditional interface support
- [ ] Test interface compatibility
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 3: Multi-Repository WebSocket Support
- [ ] Implement multi-repository WebSocket creation
- [ ] Add multi-repository message handling
- [ ] Implement parallel processing support
- [ ] Test multi-repository functionality
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 4: Backward Compatibility Testing
- [ ] Test existing single repository functionality
- [ ] Verify WebSocket message formats unchanged
- [ ] Test feature flag fallback mechanisms
- [ ] Validate error handling unchanged
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

## Dependencies
- TASK027: Phase 4.1: Frontend Feature Flag Infrastructure
- TASK028: Phase 4.2: Enhanced Type Definitions with Feature Flag Protection
- Existing WebSocket client implementation

## Deliverables
1. Enhanced `src/utils/websocketClient.ts` with multi-repository support
2. Feature flag protected WebSocket functionality
3. Multi-repository WebSocket support
4. Backward compatibility mechanisms
5. Comprehensive testing for both single and multi-repository scenarios
6. Error handling and fallback mechanisms

## Success Criteria
- [ ] Multi-repository functionality works when feature flag is enabled
- [ ] Single repository functionality works unchanged when feature flag is disabled
- [ ] Feature flag fallback mechanisms work correctly
- [ ] Multi-repository WebSocket support is functional
- [ ] All existing tests continue passing
- [ ] New tests cover multi-repository scenarios
- [ ] WebSocket connections remain stable

## Progress Log

### 2024-12-19 - Task Created
- Task created based on Implementation Phases section
- Implementation plan defined
- Subtasks identified and structured
- Dependencies identified

## Notes
- Must maintain 100% backward compatibility
- Feature flag integration is critical for WebSocket behavior
- Multi-repository WebSocket should be robust and error-resistant
- Fallback mechanisms should be seamless
- All existing WebSocket functionality must remain intact
- Error handling should be comprehensive for multi-repository scenarios
