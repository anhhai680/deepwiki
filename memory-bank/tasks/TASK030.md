# TASK030: Phase 4.5: Enhanced Configuration Modal with Feature Flag

## Task Information
- **Task ID**: TASK030
- **Task Name**: Phase 4.5: Enhanced Configuration Modal with Feature Flag
- **Status**: 🔴 Not Started
- **Progress**: 0%
- **Phase**: Week 5-6
- **Priority**: 🟡 Medium
- **Created**: 2024-12-19
- **Estimated Duration**: 4-5 days

## Task Description
Enhance the existing Configuration Modal component to support multiple repositories while maintaining 100% backward compatibility. This task focuses on adding feature flag checks, conditionally showing multi-repository UI elements, and implementing repository management interface with graceful fallback mechanisms.

## Original Request
Based on Implementation Phases section in multiple-repositories-implementation-plan-corrected.md document. Each sub-heading in the phases should create as a task instead of a large task.

## Thought Process
The implementation plan emphasizes enhancing existing components rather than replacing them. This task will extend the existing Configuration Modal component to support multi-repository functionality through feature flag protection, while maintaining all existing single-repository functionality unchanged. The approach uses the single feature flag to control UI rendering and implements fallback mechanisms.

## Implementation Plan

### 1. Add Feature Flag Check for Multi-Repository Configuration
- **File**: `src/components/ConfigurationModal.tsx` (enhance existing)
- **Purpose**: Check feature flag before showing multi-repository configuration
- **Approach**: Import feature flags and check state before rendering

### 2. Conditionally Show Multi-Repository UI Elements
- **File**: `src/components/ConfigurationModal.tsx` (enhance existing)
- **Purpose**: Show multi-repository UI only when feature flag is enabled
- **Approach**: Conditional rendering with feature flag protection

### 3. Maintain Existing Single Repository Configuration
- **File**: `src/components/ConfigurationModal.tsx` (enhance existing)
- **Purpose**: Ensure existing single repository configuration works unchanged
- **Approach**: Preserve all existing UI elements and functionality

### 4. Add Repository Management Interface
- **File**: `src/components/ConfigurationModal.tsx` (enhance existing)
- **Purpose**: Interface for managing multiple repositories
- **Approach**: Feature flag protected with backward compatibility

### 5. Ensure Backward Compatibility for All Existing Functionality
- **File**: `src/components/ConfigurationModal.tsx` (enhance existing)
- **Purpose**: All existing functionality must continue working
- **Approach**: No breaking changes to existing interface

## Technical Specifications

### Enhanced Configuration Modal (Feature Flag Protected)

```typescript
// src/components/ConfigurationModal.tsx - Feature flag protected extensions
import { FeatureFlags } from '@/config/featureFlags';
import { useState, useEffect } from 'react';

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
  // ... existing state variables ...
  
  // Feature flag state
  const isMultiRepoEnabled = FeatureFlags.isMultiRepoEnabled();
  
  // Multi-repository state (only when feature flag is enabled)
  const [repositories, setRepositories] = useState<RepositoryInfo[]>(
    isMultiRepoEnabled ? (props.repositories || []) : []
  );
  const [maxTotalContext, setMaxTotalContext] = useState(
    isMultiRepoEnabled ? (props.maxTotalContext || 8000) : 8000
  );
  const [repositoryBalance, setRepositoryBalance] = useState(
    isMultiRepoEnabled ? (props.repositoryBalance || 'equal') : 'equal'
  );
  
  // ... existing useEffect hooks ...
  
  // Multi-repository management functions (only when feature flag is enabled)
  const addRepository = (repo: RepositoryInfo) => {
    if (!isMultiRepoEnabled) return;
    
    setRepositories(prev => [...prev, repo]);
    if (props.onRepositoriesChange) {
      props.onRepositoriesChange([...repositories, repo]);
    }
  };
  
  const removeRepository = (index: number) => {
    if (!isMultiRepoEnabled) return;
    
    const newRepositories = repositories.filter((_, i) => i !== index);
    setRepositories(newRepositories);
    if (props.onRepositoriesChange) {
      props.onRepositoriesChange(newRepositories);
    }
  };
  
  const updateRepository = (index: number, updatedRepo: RepositoryInfo) => {
    if (!isMultiRepoEnabled) return;
    
    const newRepositories = repositories.map((repo, i) => 
      i === index ? updatedRepo : repo
    );
    setRepositories(newRepositories);
    if (props.onRepositoriesChange) {
      props.onRepositoriesChange(newRepositories);
    }
  };
  
  const moveRepository = (fromIndex: number, toIndex: number) => {
    if (!isMultiRepoEnabled) return;
    
    const newRepositories = [...repositories];
    const [movedRepo] = newRepositories.splice(fromIndex, 1);
    newRepositories.splice(toIndex, 0, movedRepo);
    setRepositories(newRepositories);
    if (props.onRepositoriesChange) {
      props.onRepositoriesChange(newRepositories);
    }
  };
  
  // ... existing functions unchanged ...
  
  return (
    <div className="configuration-modal">
      {/* Always show existing single repository configuration */}
      <div className="single-repository-section">
        <h2 className="text-xl font-bold mb-4">Repository Configuration</h2>
        
        {/* Existing single repository fields */}
        <div className="form-group mb-4">
          <label className="block text-sm font-medium mb-2">Repository URL</label>
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="https://github.com/owner/repo"
          />
        </div>
        
        <div className="form-group mb-4">
          <label className="block text-sm font-medium mb-2">Access Token (Optional)</label>
          <input
            type="password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="GitHub personal access token"
          />
        </div>
        
        <div className="form-group mb-4">
          <label className="block text-sm font-medium mb-2">Repository Type</label>
          <select
            value={repoType}
            onChange={(e) => setRepoType(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
          >
            <option value="github">GitHub</option>
            <option value="gitlab">GitLab</option>
            <option value="bitbucket">Bitbucket</option>
            <option value="local">Local</option>
          </select>
        </div>
        
        {/* Existing AI configuration fields */}
        <div className="form-group mb-4">
          <label className="block text-sm font-medium mb-2">AI Provider</label>
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
          >
            <option value="google">Google</option>
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
          </select>
        </div>
        
        <div className="form-group mb-4">
          <label className="block text-sm font-medium mb-2">AI Model</label>
          <input
            type="text"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="Model name"
          />
        </div>
        
        <div className="form-group mb-4">
          <label className="block text-sm font-medium mb-2">Language</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="ja">Japanese</option>
            <option value="zh">Chinese</option>
          </select>
        </div>
      </div>
      
      {/* Only show multi-repository UI if feature flag is enabled */}
      {isMultiRepoEnabled && (
        <div className="multi-repository-section border-t pt-6 mt-6">
          <h3 className="text-lg font-semibold mb-4">Multi-Repository Configuration</h3>
          
          {/* Multi-repository toggle */}
          <div className="form-group mb-4">
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
          
          {/* Multi-repository configuration (only when enabled) */}
          {isMultiRepositoryMode && (
            <>
              {/* Repository list management */}
              <div className="form-group mb-4">
                <label className="block text-sm font-medium mb-2">Repositories</label>
                <div className="space-y-2">
                  {repositories.map((repo, index) => (
                    <div key={index} className="flex items-center space-x-2 p-3 bg-gray-50 rounded">
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
                  
                  {repositories.length === 0 && (
                    <p className="text-gray-500 text-sm">No repositories configured</p>
                  )}
                </div>
                
                {/* Add repository button */}
                <button
                  type="button"
                  onClick={() => setShowAddRepositoryModal(true)}
                  className="mt-2 px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  + Add Repository
                </button>
              </div>
              
              {/* Context configuration */}
              <div className="form-group mb-4">
                <label className="block text-sm font-medium mb-2">Maximum Total Context</label>
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
              
              {/* Repository balance strategy */}
              <div className="form-group mb-4">
                <label className="block text-sm font-medium mb-2">Repository Balance Strategy</label>
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
            </>
          )}
        </div>
      )}
      
      {/* Existing action buttons */}
      <div className="modal-actions flex justify-end space-x-3 mt-6">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={handleSave}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Save Configuration
        </button>
      </div>
      
      {/* Add repository modal (only when feature flag is enabled) */}
      {isMultiRepoEnabled && showAddRepositoryModal && (
        <AddRepositoryModal
          onAdd={addRepository}
          onClose={() => setShowAddRepositoryModal(false)}
        />
      )}
    </div>
  );
};

// Add Repository Modal Component (only when feature flag is enabled)
interface AddRepositoryModalProps {
  onAdd: (repo: RepositoryInfo) => void;
  onClose: () => void;
}

const AddRepositoryModal: React.FC<AddRepositoryModalProps> = ({ onAdd, onClose }) => {
  const [newRepo, setNewRepo] = useState<Partial<RepositoryInfo>>({
    owner: '',
    repo: '',
    type: 'github',
    alias: '',
    description: '',
    priority_weight: 1.0
  });
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (newRepo.owner && newRepo.repo) {
      const repo: RepositoryInfo = {
        owner: newRepo.owner!,
        repo: newRepo.repo!,
        type: newRepo.type || 'github',
        token: newRepo.token || null,
        localPath: newRepo.localPath || null,
        repoUrl: newRepo.repoUrl || `https://github.com/${newRepo.owner}/${newRepo.repo}`,
        alias: newRepo.alias || undefined,
        description: newRepo.description || undefined,
        priority_weight: newRepo.priority_weight || 1.0
      };
      
      onAdd(repo);
      onClose();
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">Add Repository</h3>
        
        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Owner</label>
              <input
                type="text"
                value={newRepo.owner}
                onChange={(e) => setNewRepo(prev => ({ ...prev, owner: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded"
                placeholder="username or organization"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Repository</label>
              <input
                type="text"
                value={newRepo.repo}
                onChange={(e) => setNewRepo(prev => ({ ...prev, repo: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded"
                placeholder="repository-name"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Type</label>
              <select
                value={newRepo.type}
                onChange={(e) => setNewRepo(prev => ({ ...prev, type: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded"
              >
                <option value="github">GitHub</option>
                <option value="gitlab">GitLab</option>
                <option value="bitbucket">Bitbucket</option>
                <option value="local">Local</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Alias (Optional)</label>
              <input
                type="text"
                value={newRepo.alias}
                onChange={(e) => setNewRepo(prev => ({ ...prev, alias: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded"
                placeholder="User-friendly name"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Priority Weight</label>
              <input
                type="number"
                value={newRepo.priority_weight}
                onChange={(e) => setNewRepo(prev => ({ ...prev, priority_weight: Number(e.target.value) }))}
                className="w-full p-2 border border-gray-300 rounded"
                min="0.1"
                max="10.0"
                step="0.1"
              />
            </div>
          </div>
          
          <div className="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Add Repository
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ConfigurationModal;
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
- [ ] Implement conditional rendering
- [ ] Test feature flag disabled state
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 2: Multi-Repository UI Elements
- [ ] Add multi-repository configuration section
- [ ] Implement repository list management
- [ ] Add context configuration fields
- [ ] Test multi-repository UI functionality
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 3: Repository Management Interface
- [ ] Implement add repository functionality
- [ ] Add edit repository capability
- [ ] Implement remove repository
- [ ] Add repository priority management
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 4: Backward Compatibility Testing
- [ ] Test existing single repository functionality
- [ ] Verify component behavior unchanged
- [ ] Test feature flag fallback mechanisms
- [ ] Validate all existing functionality
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

## Dependencies
- TASK026: Phase 4.1: Frontend Feature Flag Infrastructure
- TASK027: Phase 4.2: Enhanced Type Definitions with Feature Flag Protection
- Existing Configuration Modal component implementation

## Deliverables
1. Enhanced `src/components/ConfigurationModal.tsx` with multi-repository support
2. Feature flag protected component functionality
3. Multi-repository configuration UI
4. Repository management interface
5. Backward compatibility mechanisms
6. Comprehensive testing for both single and multi-repository scenarios

## Success Criteria
- [ ] Multi-repository functionality works when feature flag is enabled
- [ ] Single repository functionality works unchanged when feature flag is disabled
- [ ] Feature flag fallback mechanisms work correctly
- [ ] Multi-repository configuration UI is functional
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
- Feature flag integration is critical for UI rendering
- Multi-repository configuration should be intuitive
- Repository management should be user-friendly
- All existing component functionality must remain intact
- UI should clearly separate single and multi-repository sections
