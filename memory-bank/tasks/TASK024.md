# TASK024: Phase 2.1: Multi-Repository Support

## Task Information
- **Task ID**: TASK024
- **Task Name**: Phase 2.1: Multi-Repository Support
- **Status**: 🔴 Not Started
- **Progress**: 0%
- **Phase**: Week 3
- **Priority**: 🟡 Medium
- **Created**: 2024-12-19
- **Estimated Duration**: 5-7 days

## Task Description
Enhance the existing WebSocket handler to support multiple repositories while maintaining 100% backward compatibility. This task focuses on adding single feature flag routing logic, multi-repository request parsing, and parallel repository processing to the existing `wiki_handler.py`.

## Original Request
Based on Implementation Phases section in multiple-repositories-implementation-plan-corrected.md document. Each sub-heading in the phases should create as a task instead of a large task.

## Thought Process
The implementation plan emphasizes enhancing existing components rather than replacing them. This task will extend the existing WebSocket handler to support multi-repository functionality through feature flag routing, while maintaining all existing single-repository functionality unchanged. The approach uses the single feature flag to control routing and fallback mechanisms.

## Implementation Plan

### 1. Add Single Feature Flag Routing Logic
- **File**: `backend/websocket/wiki_handler.py` (enhance existing)
- **Purpose**: Route requests based on single feature flag
- **Approach**: Check feature flag before enabling multi-repository functionality

### 2. Implement Multi-Repository Request Parsing
- **File**: `backend/websocket/wiki_handler.py` (enhance existing)
- **Purpose**: Parse and validate multi-repository requests
- **Approach**: Use new models from Phase 1 with validation

### 3. Add Repository Validation and Health Checking
- **File**: `backend/websocket/wiki_handler.py` (enhance existing)
- **Purpose**: Validate repositories and check their health
- **Approach**: Integrate with repository manager service

### 4. Implement Parallel Repository Processing
- **File**: `backend/websocket/wiki_handler.py` (enhance existing)
- **Purpose**: Process multiple repositories in parallel
- **Approach**: Async processing with proper error handling

### 5. Maintain Backward Compatibility
- **File**: `backend/websocket/wiki_handler.py` (enhance existing)
- **Purpose**: Ensure existing single repository functionality works unchanged
- **Approach**: Feature flag fallback mechanisms

## Technical Specifications

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
            provider=request.provider,
            model=request.model,
            language=request.language
        )
        await handle_single_repository_chat(websocket, single_repo_request)
        return
    
    try:
        # Validate all repositories
        repository_manager = RepositoryManager()
        validated_repos = await repository_manager.validate_repositories(request.repositories)
        
        if not validated_repos:
            await websocket.send_json({
                "type": "error",
                "data": {"message": "No valid repositories found"}
            })
            return
        
        # Process repositories in parallel
        await process_multi_repository_request(websocket, request, validated_repos)
        
    except Exception as e:
        logger.error(f"Error in multi-repository chat: {e}")
        await websocket.send_json({
            "type": "error",
            "data": {"message": f"Multi-repository processing error: {str(e)}"}
        })

async def process_multi_repository_request(websocket: WebSocket, request: MultiRepositoryRequest, repositories: List[RepositoryInfo]):
    """Process multi-repository request with parallel processing"""
    
    # Send initial status
    await websocket.send_json({
        "type": "status",
        "data": {
            "message": f"Processing {len(repositories)} repositories",
            "repository_count": len(repositories)
        }
    })
    
    try:
        # Process repositories in parallel
        processing_tasks = [
            process_single_repository_for_multi(websocket, repo, request.messages, request.provider, request.model)
            for repo in repositories
        ]
        
        # Wait for all repositories to complete processing
        results = await asyncio.gather(*processing_tasks, return_exceptions=True)
        
        # Merge results and send final response
        await merge_and_send_results(websocket, results, repositories)
        
    except Exception as e:
        logger.error(f"Error in parallel processing: {e}")
        await websocket.send_json({
            "type": "error",
            "data": {"message": f"Parallel processing error: {str(e)}"}
        })

async def process_single_repository_for_multi(websocket: WebSocket, repo: RepositoryInfo, messages: List[ChatMessage], 
                                           provider: str, model: Optional[str]) -> Dict[str, Any]:
    """Process a single repository as part of multi-repository request"""
    
    try:
        # Create single repository request for processing
        single_request = ChatCompletionRequest(
            repo=repo.repo,
            owner=repo.owner,
            messages=messages,
            provider=provider,
            model=model,
            language="en"
        )
        
        # Process with existing single repository logic
        result = await process_single_repository_request(single_request)
        
        return {
            "repository": f"{repo.owner}/{repo.repo}",
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error processing repository {repo.owner}/{repo.repo}: {e}")
        return {
            "repository": f"{repo.owner}/{repo.repo}",
            "status": "error",
            "error": str(e)
        }

async def merge_and_send_results(websocket: WebSocket, results: List[Dict[str, Any]], repositories: List[RepositoryInfo]):
    """Merge results from multiple repositories and send final response"""
    
    successful_results = [r for r in results if r.get("status") == "success"]
    failed_results = [r for r in results if r.get("status") == "error"]
    
    # Send summary
    await websocket.send_json({
        "type": "summary",
        "data": {
            "total_repositories": len(repositories),
            "successful": len(successful_results),
            "failed": len(failed_results),
            "repositories": [r["repository"] for r in results]
        }
    })
    
    # Send individual results
    for result in results:
        await websocket.send_json({
            "type": "repository_result",
            "data": result
        })
    
    # Send final completion message
    await websocket.send_json({
        "type": "completion",
        "data": {
            "message": "Multi-repository processing completed",
            "total_processed": len(results)
        }
    })
```

### Backward Compatibility Requirements
- Existing single-repository functionality must work 100% unchanged
- All existing WebSocket connections must remain stable
- No breaking changes to existing message formats
- Feature flag fallback must work seamlessly

## Subtasks

### Subtask 1: Feature Flag Integration
- [ ] Import and integrate feature flags
- [ ] Add feature flag routing logic
- [ ] Implement fallback mechanisms
- [ ] Test feature flag disabled state
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 2: Multi-Repository Request Handling
- [ ] Add multi-repository request parsing
- [ ] Implement request validation
- [ ] Add repository validation logic
- [ ] Test request parsing functionality
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 3: Parallel Processing Implementation
- [ ] Implement parallel repository processing
- [ ] Add async task management
- [ ] Implement result aggregation
- [ ] Test parallel processing performance
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
- TASK021: Phase 1.1: Feature Flag Infrastructure
- TASK022: Phase 1.2: Extend Existing Models
- TASK023: Phase 1.3: Repository Model Enhancement
- Repository Manager Service (to be created)

## Deliverables
1. Enhanced `backend/websocket/wiki_handler.py` with multi-repository support
2. Feature flag routing logic
3. Parallel repository processing
4. Backward compatibility mechanisms
5. Comprehensive testing for both single and multi-repository scenarios
6. Error handling and fallback mechanisms

## Success Criteria
- [ ] Multi-repository functionality works when feature flag is enabled
- [ ] Single repository functionality works unchanged when feature flag is disabled
- [ ] Feature flag fallback mechanisms work correctly
- [ ] Parallel processing is functional and performant
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
- Feature flag routing is critical for system stability
- Parallel processing should be configurable and monitored
- Error handling must be robust for multi-repository scenarios
- WebSocket message formats should remain consistent
