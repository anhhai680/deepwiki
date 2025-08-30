# TASK026: Phase 3.1: Multi-RAG Support

## Task Information
- **Task ID**: TASK026
- **Task Name**: Phase 3.1: Multi-RAG Support
- **Status**: 🔴 Not Started
- **Progress**: 0%
- **Phase**: Week 4
- **Priority**: 🟡 Medium
- **Created**: 2024-12-19
- **Estimated Duration**: 6-8 days

## Task Description
Enhance the existing RAG pipeline to support multiple repositories while maintaining 100% backward compatibility. This task focuses on adding single feature flag protection, multi-repository document retrieval, context merging strategies, and performance optimization to the existing `RAGPipeline` class.

## Original Request
Based on Implementation Phases section in multiple-repositories-implementation-plan-corrected.md document. Each sub-heading in the phases should create as a task instead of a large task.

## Thought Process
The implementation plan emphasizes extending existing components rather than replacing them. This task will enhance the existing RAG pipeline to support multi-repository functionality through feature flag protection, while maintaining all existing single-repository functionality unchanged. The approach uses the single feature flag to control RAG pipeline behavior and implements context merging strategies for multiple repositories.

## Implementation Plan

### 1. Add Single Feature Flag Protection
- **File**: `backend/pipelines/rag/rag_pipeline.py` (extend existing)
- **Purpose**: Protect RAG pipeline with single feature flag
- **Approach**: Check feature flag before enabling multi-repository processing

### 2. Enhance RAGPipeline Class for Multi-Repository
- **File**: `backend/pipelines/rag/rag_pipeline.py` (extend existing)
- **Purpose**: Add multi-repository support to existing RAG pipeline
- **Approach**: Extend existing methods and add new multi-repository methods

### 3. Implement Repository-Aware Document Retrieval
- **File**: `backend/pipelines/rag/rag_pipeline.py` (extend existing)
- **Purpose**: Retrieve documents from multiple repositories
- **Approach**: Parallel document retrieval with repository context

### 4. Add Context Merging Strategies
- **File**: `backend/pipelines/rag/rag_pipeline.py` (extend existing)
- **Purpose**: Merge context from multiple repositories
- **Approach**: Configurable merging strategies (equal, weighted, priority)

### 5. Implement Performance Optimization
- **File**: `backend/pipelines/rag/rag_pipeline.py` (extend existing)
- **Purpose**: Optimize performance for multiple repositories
- **Approach**: Parallel processing, caching, and resource management

## Technical Specifications

### Enhanced RAG Pipeline

```python
# backend/pipelines/rag/rag_pipeline.py - EXTEND EXISTING
from ...config.feature_flags import FeatureFlags
from ...models.chat import MultiRepositoryRequest, RepositoryInfo
from ...services.repository_manager import RepositoryManager
import asyncio
from typing import List, Dict, Any, Optional

class RAGPipeline:
    """Enhanced RAG pipeline with multi-repository support"""
    
    def __init__(self):
        # ... existing initialization ...
        self.repository_manager = RepositoryManager()
        self.context_merger = ContextMerger()
    
    async def process_multi_repository_request(self, request: MultiRepositoryRequest) -> Dict[str, Any]:
        """Process multi-repository request (feature flag protected)"""
        if not FeatureFlags.is_multi_repo_enabled():
            # Fallback to single repository processing
            return await self.process_single_repository_request(request.repositories[0], request.messages)
        
        try:
            # Validate repositories
            validated_repos = await self.repository_manager.validate_repositories(request.repositories)
            
            if not validated_repos:
                raise ValueError("No valid repositories found")
            
            # Process repositories in parallel
            results = await self._process_repositories_parallel(validated_repos, request)
            
            # Merge context and generate response
            merged_context = await self._merge_repository_contexts(results, request.repository_balance)
            
            # Generate final response
            final_response = await self._generate_multi_repository_response(merged_context, request)
            
            return {
                "status": "success",
                "response": final_response,
                "repositories_processed": len(validated_repos),
                "context_merged": len(merged_context),
                "processing_time": results.get("total_time", 0)
            }
            
        except Exception as e:
            logger.error(f"Error in multi-repository RAG processing: {e}")
            return {
                "status": "error",
                "message": str(e),
                "repositories_processed": 0
            }
    
    async def _process_repositories_parallel(self, repositories: List[RepositoryInfo], 
                                           request: MultiRepositoryRequest) -> Dict[str, Any]:
        """Process multiple repositories in parallel"""
        
        start_time = time.time()
        
        # Create processing tasks for each repository
        processing_tasks = [
            self._process_single_repository_for_multi(repo, request.messages, request.provider, request.model)
            for repo in repositories
        ]
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*processing_tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing repository {repositories[i].owner}/{repositories[i].repo}: {result}")
                processed_results.append({
                    "repository": f"{repositories[i].owner}/{repositories[i].repo}",
                    "status": "error",
                    "error": str(result)
                })
            else:
                processed_results.append({
                    "repository": f"{repositories[i].owner}/{repositories[i].repo}",
                    "status": "success",
                    "documents": result.get("documents", []),
                    "context": result.get("context", ""),
                    "processing_time": result.get("processing_time", 0)
                })
        
        return {
            "results": processed_results,
            "total_time": time.time() - start_time,
            "successful": len([r for r in processed_results if r["status"] == "success"]),
            "failed": len([r for r in processed_results if r["status"] == "error"])
        }
    
    async def _process_single_repository_for_multi(self, repo: RepositoryInfo, messages: List[ChatMessage], 
                                                 provider: str, model: Optional[str]) -> Dict[str, Any]:
        """Process a single repository as part of multi-repository request"""
        
        start_time = time.time()
        
        try:
            # Use existing single repository processing logic
            result = await self.process_single_repository_request(repo, messages)
            
            return {
                "documents": result.get("documents", []),
                "context": result.get("context", ""),
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Error processing repository {repo.owner}/{repo.repo}: {e}")
            raise e
    
    async def _merge_repository_contexts(self, results: Dict[str, Any], 
                                       balance_strategy: str) -> List[Dict[str, Any]]:
        """Merge context from multiple repositories based on strategy"""
        
        successful_results = [r for r in results["results"] if r["status"] == "success"]
        
        if not successful_results:
            return []
        
        if balance_strategy == "equal":
            return self._merge_equal_balance(successful_results)
        elif balance_strategy == "weighted":
            return self._merge_weighted_balance(successful_results)
        elif balance_strategy == "priority":
            return self._merge_priority_balance(successful_results)
        else:
            # Default to equal balance
            return self._merge_equal_balance(successful_results)
    
    def _merge_equal_balance(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge context with equal balance across repositories"""
        merged_context = []
        
        for result in results:
            if "documents" in result:
                merged_context.extend(result["documents"])
        
        # Sort by relevance score and limit total context
        merged_context.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return merged_context
    
    def _merge_weighted_balance(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge context with weighted balance based on repository priority"""
        merged_context = []
        
        for result in results:
            if "documents" in result:
                # Apply repository weight to document scores
                repo_weight = result.get("repository_weight", 1.0)
                weighted_documents = []
                
                for doc in result["documents"]:
                    weighted_doc = doc.copy()
                    weighted_doc["score"] = doc.get("score", 0) * repo_weight
                    weighted_documents.append(weighted_doc)
                
                merged_context.extend(weighted_documents)
        
        # Sort by weighted score and limit total context
        merged_context.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return merged_context
    
    def _merge_priority_balance(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge context with priority-based balance"""
        merged_context = []
        
        # Sort results by repository priority
        sorted_results = sorted(results, key=lambda x: x.get("repository_priority", 0), reverse=True)
        
        for result in sorted_results:
            if "documents" in result:
                merged_context.extend(result["documents"])
        
        return merged_context
    
    async def _generate_multi_repository_response(self, merged_context: List[Dict[str, Any]], 
                                               request: MultiRepositoryRequest) -> str:
        """Generate final response from merged context"""
        
        # Prepare context for generation
        context_text = self._prepare_context_for_generation(merged_context)
        
        # Use existing generation logic with merged context
        response = await self._generate_response_with_context(
            context_text, 
            request.messages, 
            request.provider, 
            request.model
        )
        
        return response
    
    def _prepare_context_for_generation(self, merged_context: List[Dict[str, Any]]) -> str:
        """Prepare merged context for response generation"""
        
        if not merged_context:
            return ""
        
        # Extract text content from documents
        context_parts = []
        for doc in merged_context:
            if "content" in doc:
                context_parts.append(doc["content"])
            elif "text" in doc:
                context_parts.append(doc["text"])
        
        # Join context parts with separators
        return "\n\n---\n\n".join(context_parts)
    
    async def _generate_response_with_context(self, context: str, messages: List[ChatMessage], 
                                           provider: str, model: Optional[str]) -> str:
        """Generate response using existing generation logic"""
        
        # Use existing single repository generation method
        # This ensures consistency with existing functionality
        return await self.generate_response(context, messages, provider, model)
```

### Backward Compatibility Requirements
- Existing single-repository functionality must work 100% unchanged
- All existing RAG pipeline methods must remain functional
- No breaking changes to existing method signatures
- Feature flag fallback must work seamlessly

## Subtasks

### Subtask 1: Feature Flag Integration
- [ ] Import and integrate feature flags
- [ ] Add feature flag protection to RAG pipeline
- [ ] Implement fallback mechanisms
- [ ] Test feature flag disabled state
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 2: Multi-Repository Processing
- [ ] Add multi-repository request processing
- [ ] Implement parallel repository processing
- [ ] Add repository validation integration
- [ ] Test multi-repository functionality
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 3: Context Merging Implementation
- [ ] Implement equal balance merging
- [ ] Implement weighted balance merging
- [ ] Implement priority balance merging
- [ ] Test all merging strategies
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 4: Performance Optimization
- [ ] Add parallel processing optimization
- [ ] Implement context caching
- [ ] Add resource management
- [ ] Test performance improvements
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

## Dependencies
- TASK022: Phase 1.1: Feature Flag Infrastructure
- TASK023: Phase 1.2: Extend Existing Models
- TASK024: Phase 1.3: Repository Model Enhancement
- TASK025: Phase 2.1: Multi-Repository Support (WebSocket)
- Repository Manager Service (to be created)

## Deliverables
1. Enhanced `backend/pipelines/rag/rag_pipeline.py` with multi-repository support
2. Feature flag protection for RAG pipeline
3. Multi-repository document retrieval
4. Context merging strategies
5. Performance optimization features
6. Comprehensive testing for both single and multi-repository scenarios

## Success Criteria
- [ ] Multi-repository functionality works when feature flag is enabled
- [ ] Single repository functionality works unchanged when feature flag is disabled
- [ ] Feature flag fallback mechanisms work correctly
- [ ] Context merging strategies are functional
- [ ] Performance optimization is effective
- [ ] All existing tests continue passing
- [ ] New tests cover multi-repository scenarios

## Progress Log

### 2024-12-19 - Task Created
- Task created based on Implementation Phases section
- Implementation plan defined
- Subtasks identified and structured
- Dependencies identified

## Notes
- Must maintain 100% backward compatibility
- Feature flag protection is critical for system stability
- Context merging should be configurable and efficient
- Performance optimization should handle multiple repositories gracefully
- All existing RAG pipeline functionality must remain intact
