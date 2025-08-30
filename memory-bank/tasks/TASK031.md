# TASK031: Phase 4.6: Enhanced Main Page with Feature Flag

## Task Information
- **Task ID**: TASK031
- **Task Name**: Phase 4.6: Enhanced Main Page with Feature Flag
- **Status**: 🔴 Not Started
- **Progress**: 0%
- **Phase**: Week 5-6
- **Priority**: 🟡 Medium
- **Created**: 2024-12-19
- **Estimated Duration**: 4-5 days

## Task Description
Enhance the existing Main Page component to support multiple repositories while maintaining 100% backward compatibility. This task focuses on adding feature flag checks, conditionally enabling multi-repository input mode, and implementing repository list management with graceful fallback mechanisms.

## Original Request
Based on Implementation Phases section in multiple-repositories-implementation-plan-corrected.md document. Each sub-heading in the phases should create as a task instead of a large task.

## Thought Process
The implementation plan emphasizes enhancing existing components rather than replacing them. This task will extend the existing Main Page component to support multi-repository functionality through feature flag protection, while maintaining all existing single-repository functionality unchanged. The approach uses the single feature flag to control page behavior and implements fallback mechanisms.

## Implementation Plan

### 1. Add Feature Flag Check for Multi-Repository Input
- **File**: `src/app/page.tsx` (enhance existing)
- **Purpose**: Check feature flag before enabling multi-repository input mode
- **Approach**: Import feature flags and check state before rendering

### 2. Conditionally Enable Multi-Repository Input Mode
- **File**: `src/app/page.tsx` (enhance existing)
- **Purpose**: Enable multi-repository input only when feature flag is enabled
- **Approach**: Conditional state management with feature flag protection

### 3. Maintain Existing Single Repository Input
- **File**: `src/app/page.tsx` (enhance existing)
- **Purpose**: Ensure existing single repository input works unchanged
- **Approach**: Preserve all existing UI elements and functionality

### 4. Add Repository List Management
- **File**: `src/app/page.tsx` (enhance existing)
- **Purpose**: Interface for managing multiple repositories
- **Approach**: Feature flag protected with backward compatibility

### 5. Ensure Backward Compatibility for All Existing Functionality
- **File**: `src/app/page.tsx` (enhance existing)
- **Purpose**: All existing functionality must continue working
- **Approach**: No breaking changes to existing interface

## Technical Specifications

### Enhanced Main Page (Feature Flag Protected)

```typescript
// src/app/page.tsx - Feature flag protected extensions
'use client';

import { useState, useEffect } from 'react';
import { FeatureFlags } from '@/config/featureFlags';
import Ask from '@/components/Ask';
import ConfigurationModal from '@/components/ConfigurationModal';

export default function Home() {
  // ... existing state variables ...
  
  // Feature flag state
  const isMultiRepoEnabled = FeatureFlags.isMultiRepoEnabled();
  
  // Multi-repository state (only when feature flag is enabled)
  const [repositories, setRepositories] = useState<RepositoryInfo[]>(
    isMultiRepoEnabled ? [] : []
  );
  const [isMultiRepositoryMode, setIsMultiRepositoryMode] = useState(
    isMultiRepoEnabled ? false : false
  );
  const [maxTotalContext, setMaxTotalContext] = useState(
    isMultiRepoEnabled ? 8000 : 8000
  );
  const [repositoryBalance, setRepositoryBalance] = useState(
    isMultiRepoEnabled ? 'equal' : 'equal'
  );
  
  // ... existing useEffect hooks ...
  
  // Multi-repository management functions (only when feature flag is enabled)
  const addRepository = (repo: RepositoryInfo) => {
    if (!isMultiRepoEnabled) return;
    
    setRepositories(prev => [...prev, repo]);
  };
  
  const removeRepository = (index: number) => {
    if (!isMultiRepoEnabled) return;
    
    setRepositories(prev => prev.filter((_, i) => i !== index));
  };
  
  const updateRepository = (index: number, updatedRepo: RepositoryInfo) => {
    if (!isMultiRepoEnabled) return;
    
    setRepositories(prev => prev.map((repo, i) => 
      i === index ? updatedRepo : repo
    ));
  };
  
  const moveRepository = (fromIndex: number, toIndex: number) => {
    if (!isMultiRepoEnabled) return;
    
    const newRepositories = [...repositories];
    const [movedRepo] = newRepositories.splice(fromIndex, 1);
    newRepositories.splice(toIndex, 0, movedRepo);
    setRepositories(newRepositories);
  };
  
  // ... existing functions unchanged ...
  
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            DeepWiki Chat
          </h1>
          <p className="text-lg text-gray-600">
            AI-powered chat interface for your repositories
          </p>
          
          {/* Feature flag indicator (subtle) */}
          {isMultiRepoEnabled && (
            <div className="mt-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                Multi-Repository Mode Available
              </span>
            </div>
          )}
        </div>
        
        {/* Main content */}
        <div className="max-w-4xl mx-auto">
          {/* Configuration section */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Configuration
              </h2>
              <button
                onClick={() => setShowConfigModal(true)}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Configure
              </button>
            </div>
            
            {/* Current configuration display */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  Repository
                </h3>
                <p className="text-sm text-gray-900">
                  {repoInfo.repoUrl || 'Not configured'}
                </p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  AI Provider
                </h3>
                <p className="text-sm text-gray-900">
                  {provider || 'Google'}
                </p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  AI Model
                </h3>
                <p className="text-sm text-gray-900">
                  {model || 'Default'}
                </p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  Language
                </h3>
                <p className="text-sm text-gray-900">
                  {language || 'English'}
                </p>
              </div>
            </div>
            
            {/* Multi-repository configuration (only when feature flag is enabled) */}
            {isMultiRepoEnabled && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Multi-Repository Configuration
                  </h3>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={isMultiRepositoryMode}
                      onChange={(e) => setIsMultiRepositoryMode(e.target.checked)}
                      className="rounded"
                    />
                    <span className="text-sm font-medium">Enable Multi-Repository Mode</span>
                  </label>
                </div>
                
                {isMultiRepositoryMode && (
                  <div className="space-y-4">
                    {/* Repository list */}
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">
                        Repositories ({repositories.length})
                      </h4>
                      
                      {repositories.length === 0 ? (
                        <p className="text-gray-500 text-sm">
                          No repositories configured. Add repositories in the configuration modal.
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {repositories.map((repo, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                              <div className="flex-1">
                                <div className="flex items-center space-x-2">
                                  <span className="text-sm font-medium">
                                    {repo.alias || `${repo.owner}/${repo.repo}`}
                                  </span>
                                  {repo.priority_weight && (
                                    <span className="text-xs text-gray-500">
                                      Priority: {repo.priority_weight}
                                    </span>
                                  )}
                                </div>
                                <div className="text-xs text-gray-500">
                                  {repo.repoUrl || `${repo.owner}/${repo.repo}`}
                                </div>
                              </div>
                              
                              <div className="flex items-center space-x-1">
                                <button
                                  type="button"
                                  onClick={() => updateRepository(index, repo)}
                                  className="p-1 text-blue-600 hover:text-blue-800"
                                  title="Edit repository"
                                >
                                  ✏️
                                </button>
                                <button
                                  type="button"
                                  onClick={() => removeRepository(index)}
                                  className="p-1 text-red-600 hover:text-red-800"
                                  title="Remove repository"
                                >
                                  🗑️
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    {/* Context configuration */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Maximum Total Context
                        </label>
                        <input
                          type="number"
                          value={maxTotalContext}
                          onChange={(e) => setMaxTotalContext(Number(e.target.value))}
                          className="w-full p-2 border border-gray-300 rounded"
                          min="1000"
                          max="16000"
                          step="1000"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Maximum total context tokens across all repositories
                        </p>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Repository Balance Strategy
                        </label>
                        <select
                          value={repositoryBalance}
                          onChange={(e) => setRepositoryBalance(e.target.value)}
                          className="w-full p-2 border border-gray-300 rounded"
                        >
                          <option value="equal">Equal Balance</option>
                          <option value="weighted">Weighted by Priority</option>
                          <option value="priority">Priority-Based</option>
                        </select>
                        <p className="text-xs text-gray-500 mt-1">
                          How to balance context across multiple repositories
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Chat interface */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Chat Interface
            </h2>
            
            {/* Ask component with conditional props */}
            <Ask
              repoInfo={repoInfo}
              provider={provider}
              model={model}
              isCustomModel={isCustomModel}
              customModel={customModel}
              language={language}
              onRef={setAskRef}
              // Only pass multi-repository props if feature flag is enabled
              {...(isMultiRepoEnabled ? {
                repositories: isMultiRepositoryMode ? repositories : undefined,
                maxTotalContext: isMultiRepositoryMode ? maxTotalContext : undefined,
                repositoryBalance: isMultiRepositoryMode ? repositoryBalance : undefined,
              } : {})}
            />
          </div>
        </div>
      </div>
      
      {/* Configuration Modal */}
      {showConfigModal && (
        <ConfigurationModal
          repoInfo={repoInfo}
          provider={provider}
          model={model}
          isCustomModel={isCustomModel}
          customModel={customModel}
          language={language}
          onClose={() => setShowConfigModal(false)}
          onSave={handleConfigSave}
          // Only pass multi-repository props if feature flag is enabled
          {...(isMultiRepoEnabled ? {
            repositories: repositories,
            onRepositoriesChange: setRepositories,
            maxTotalContext: maxTotalContext,
            repositoryBalance: repositoryBalance,
          } : {})}
        />
      )}
    </div>
  );
}
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
- [ ] Implement conditional state management
- [ ] Test feature flag disabled state
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 2: Multi-Repository Input Mode
- [ ] Add multi-repository mode toggle
- [ ] Implement conditional input mode
- [ ] Add repository list management
- [ ] Test multi-repository mode functionality
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 3: Repository List Management
- [ ] Implement add repository functionality
- [ ] Add edit repository capability
- [ ] Implement remove repository
- [ ] Add repository priority management
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 4: Backward Compatibility Testing
- [ ] Test existing single repository functionality
- [ ] Verify page behavior unchanged
- [ ] Test feature flag fallback mechanisms
- [ ] Validate all existing functionality
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

## Dependencies
- TASK026: Phase 4.1: Frontend Feature Flag Infrastructure
- TASK027: Phase 4.2: Enhanced Type Definitions with Feature Flag Protection
- TASK029: Phase 4.4: Enhanced Ask Component with Feature Flag
- TASK030: Phase 4.5: Enhanced Configuration Modal with Feature Flag
- Existing Main Page component implementation

## Deliverables
1. Enhanced `src/app/page.tsx` with multi-repository support
2. Feature flag protected page functionality
3. Multi-repository input mode
4. Repository list management interface
5. Backward compatibility mechanisms
6. Comprehensive testing for both single and multi-repository scenarios

## Success Criteria
- [ ] Multi-repository functionality works when feature flag is enabled
- [ ] Single repository functionality works unchanged when feature flag is disabled
- [ ] Feature flag fallback mechanisms work correctly
- [ ] Multi-repository input mode is functional
- [ ] All existing tests continue passing
- [ ] New tests cover multi-repository scenarios
- [ ] Page behavior remains consistent

## Progress Log

### 2024-12-19 - Task Created
- Task created based on Implementation Phases section
- Implementation plan defined
- Subtasks identified and structured
- Dependencies identified

## Notes
- Must maintain 100% backward compatibility
- Feature flag integration is critical for page behavior
- Multi-repository input mode should be intuitive
- Repository management should be user-friendly
- All existing page functionality must remain intact
- UI should clearly separate single and multi-repository sections
