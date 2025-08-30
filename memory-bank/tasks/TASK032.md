# TASK032: Phase 4.7: New Multi-Repository Components (Feature Flag Protected)

## Task Information
- **Task ID**: TASK032
- **Task Name**: Phase 4.7: New Multi-Repository Components (Feature Flag Protected)
- **Status**: 🔴 Not Started
- **Progress**: 0%
- **Phase**: Week 5-6
- **Priority**: 🟡 Medium
- **Created**: 2024-12-19
- **Estimated Duration**: 5-6 days

## Task Description
Create new multi-repository components that are feature flag protected and provide enhanced functionality for managing multiple repositories. This task focuses on creating specialized components for multi-repository input, repository list management, and repository priority controls while ensuring graceful degradation when the feature is disabled.

## Original Request
Based on Implementation Phases section in multiple-repositories-implementation-plan-corrected.md document. Each sub-heading in the phases should create as a task instead of a large task.

## Thought Process
The implementation plan emphasizes creating new components rather than modifying existing ones extensively. This task will create specialized multi-repository components that are feature flag protected, providing enhanced functionality for managing multiple repositories while ensuring the system remains stable and backward compatible. The approach uses feature flag checks to control component rendering and implements graceful degradation.

## Implementation Plan

### 1. Create MultiRepositoryInput Component
- **File**: `src/components/MultiRepositoryInput.tsx` (new)
- **Purpose**: Specialized input interface for multiple repositories
- **Approach**: Feature flag protected with graceful degradation

### 2. Create RepositoryList Component
- **File**: `src/components/RepositoryList.tsx` (new)
- **Purpose**: Drag-and-drop repository list management
- **Approach**: Feature flag protected with backward compatibility

### 3. Create RepositoryPriority Component
- **File**: `src/components/RepositoryPriority.tsx` (new)
- **Purpose**: Repository priority controls and management
- **Approach**: Feature flag protected with graceful degradation

### 4. Implement Feature Flag Protection
- **Files**: All new components
- **Purpose**: Check feature flag before rendering
- **Approach**: Conditional rendering with fallback mechanisms

### 5. Ensure Graceful Degradation
- **Files**: All new components
- **Purpose**: Handle disabled feature gracefully
- **Approach**: Fallback to single repository mode or hidden rendering

## Technical Specifications

### MultiRepositoryInput Component

```typescript
// src/components/MultiRepositoryInput.tsx (new)
import { useState, useEffect } from 'react';
import { FeatureFlags } from '@/config/featureFlags';
import { RepositoryInfo } from '@/types/repoinfo';

interface MultiRepositoryInputProps {
  repositories: RepositoryInfo[];
  onRepositoriesChange: (repos: RepositoryInfo[]) => void;
  maxTotalContext?: number;
  repositoryBalance?: string;
  onMaxTotalContextChange?: (value: number) => void;
  onRepositoryBalanceChange?: (value: string) => void;
}

const MultiRepositoryInput: React.FC<MultiRepositoryInputProps> = (props) => {
  // Check feature flag before rendering
  if (!FeatureFlags.isMultiRepoEnabled()) {
    // Graceful degradation: return null when feature is disabled
    return null;
  }
  
  const [newRepo, setNewRepo] = useState<Partial<RepositoryInfo>>({
    owner: '',
    repo: '',
    type: 'github',
    alias: '',
    description: '',
    priority_weight: 1.0
  });
  
  const [showAddForm, setShowAddForm] = useState(false);
  
  const addRepository = () => {
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
      
      props.onRepositoriesChange([...props.repositories, repo]);
      setNewRepo({ owner: '', repo: '', type: 'github', alias: '', description: '', priority_weight: 1.0 });
      setShowAddForm(false);
    }
  };
  
  const removeRepository = (index: number) => {
    const newRepositories = props.repositories.filter((_, i) => i !== index);
    props.onRepositoriesChange(newRepositories);
  };
  
  const updateRepository = (index: number, updatedRepo: RepositoryInfo) => {
    const newRepositories = props.repositories.map((repo, i) => 
      i === index ? updatedRepo : repo
    );
    props.onRepositoriesChange(newRepositories);
  };
  
  return (
    <div className="multi-repository-input bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Multi-Repository Configuration
      </h3>
      
      {/* Repository list */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium text-gray-700">
            Repositories ({props.repositories.length})
          </h4>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            {showAddForm ? 'Cancel' : '+ Add Repository'}
          </button>
        </div>
        
        {/* Repository list */}
        <div className="space-y-2">
          {props.repositories.map((repo, index) => (
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
          
          {props.repositories.length === 0 && (
            <p className="text-gray-500 text-sm text-center py-4">
              No repositories configured. Add your first repository to get started.
            </p>
          )}
        </div>
      </div>
      
      {/* Add repository form */}
      {showAddForm && (
        <div className="border-t pt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Add New Repository</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Owner</label>
              <input
                type="text"
                value={newRepo.owner}
                onChange={(e) => setNewRepo(prev => ({ ...prev, owner: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded"
                placeholder="username or organization"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Repository</label>
              <input
                type="text"
                value={newRepo.repo}
                onChange={(e) => setNewRepo(prev => ({ ...prev, repo: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded"
                placeholder="repository-name"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
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
              <label className="block text-sm font-medium text-gray-700 mb-1">Alias (Optional)</label>
              <input
                type="text"
                value={newRepo.alias}
                onChange={(e) => setNewRepo(prev => ({ ...prev, alias: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded"
                placeholder="User-friendly name"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority Weight</label>
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
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description (Optional)</label>
              <input
                type="text"
                value={newRepo.description}
                onChange={(e) => setNewRepo(prev => ({ ...prev, description: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded"
                placeholder="Repository description"
              />
            </div>
          </div>
          
          <div className="flex justify-end space-x-3 mt-4">
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={addRepository}
              disabled={!newRepo.owner || !newRepo.repo}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            >
              Add Repository
            </button>
          </div>
        </div>
      )}
      
      {/* Context configuration */}
      <div className="border-t pt-4">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Context Configuration</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Maximum Total Context
            </label>
            <input
              type="number"
              value={props.maxTotalContext || 8000}
              onChange={(e) => props.onMaxTotalContextChange?.(Number(e.target.value))}
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
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Repository Balance Strategy
            </label>
            <select
              value={props.repositoryBalance || 'equal'}
              onChange={(e) => props.onRepositoryBalanceChange?.(e.target.value)}
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
    </div>
  );
};

export default MultiRepositoryInput;
```

### RepositoryList Component

```typescript
// src/components/RepositoryList.tsx (new)
import { useState, useEffect } from 'react';
import { FeatureFlags } from '@/config/featureFlags';
import { RepositoryInfo } from '@/types/repoinfo';

interface RepositoryListProps {
  repositories: RepositoryInfo[];
  onRepositoriesChange: (repos: RepositoryInfo[]) => void;
  onRepositorySelect?: (repo: RepositoryInfo) => void;
  selectable?: boolean;
  showPriority?: boolean;
  showActions?: boolean;
}

const RepositoryList: React.FC<RepositoryListProps> = (props) => {
  // Check feature flag before rendering
  if (!FeatureFlags.isMultiRepoEnabled()) {
    // Graceful degradation: return null when feature is disabled
    return null;
  }
  
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
  
  const handleDragStart = (e: React.DragEvent, index: number) => {
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = 'move';
  };
  
  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    setDragOverIndex(index);
  };
  
  const handleDragLeave = () => {
    setDragOverIndex(null);
  };
  
  const handleDrop = (e: React.DragEvent, dropIndex: number) => {
    e.preventDefault();
    
    if (draggedIndex !== null && draggedIndex !== dropIndex) {
      const newRepositories = [...props.repositories];
      const [draggedRepo] = newRepositories.splice(draggedIndex, 1);
      newRepositories.splice(dropIndex, 0, draggedRepo);
      props.onRepositoriesChange(newRepositories);
    }
    
    setDraggedIndex(null);
    setDragOverIndex(null);
  };
  
  const removeRepository = (index: number) => {
    const newRepositories = props.repositories.filter((_, i) => i !== index);
    props.onRepositoriesChange(newRepositories);
  };
  
  const updateRepository = (index: number, updatedRepo: RepositoryInfo) => {
    const newRepositories = props.repositories.map((repo, i) => 
      i === index ? updatedRepo : repo
    );
    props.onRepositoriesChange(newRepositories);
  };
  
  return (
    <div className="repository-list">
      <h3 className="text-lg font-medium text-gray-900 mb-3">
        Repository List ({props.repositories.length})
      </h3>
      
      <div className="space-y-2">
        {props.repositories.map((repo, index) => (
          <div
            key={index}
            draggable
            onDragStart={(e) => handleDragStart(e, index)}
            onDragOver={(e) => handleDragOver(e, index)}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, index)}
            className={`
              p-3 bg-gray-50 rounded border-2 cursor-move
              ${draggedIndex === index ? 'opacity-50' : ''}
              ${dragOverIndex === index ? 'border-blue-300 bg-blue-50' : 'border-transparent'}
              ${props.selectable ? 'hover:bg-gray-100' : ''}
            `}
            onClick={() => props.onRepositorySelect?.(repo)}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium">
                    {repo.alias || `${repo.owner}/${repo.repo}`}
                  </span>
                  {props.showPriority && repo.priority_weight && (
                    <span className="text-xs text-gray-500">
                      Priority: {repo.priority_weight}
                    </span>
                  )}
                </div>
                <div className="text-xs text-gray-500">
                  {repo.repoUrl || `${repo.owner}/${repo.repo}`}
                </div>
                {repo.description && (
                  <div className="text-xs text-gray-600 mt-1">
                    {repo.description}
                  </div>
                )}
              </div>
              
              {props.showActions && (
                <div className="flex items-center space-x-1 ml-3">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      updateRepository(index, repo);
                    }}
                    className="p-1 text-blue-600 hover:text-blue-800"
                    title="Edit repository"
                  >
                    ✏️
                  </button>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeRepository(index);
                    }}
                    className="p-1 text-red-600 hover:text-red-800"
                    title="Remove repository"
                  >
                    🗑️
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {props.repositories.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p className="text-sm">No repositories configured</p>
            <p className="text-xs mt-1">Drag and drop repositories here or add them manually</p>
          </div>
        )}
      </div>
      
      {/* Drag and drop instructions */}
      {props.repositories.length > 1 && (
        <div className="mt-4 p-3 bg-blue-50 rounded text-sm text-blue-700">
          <p className="text-xs">
            💡 Drag and drop repositories to reorder them. The order affects context balancing and priority.
          </p>
        </div>
      )}
    </div>
  );
};

export default RepositoryList;
```

### RepositoryPriority Component

```typescript
// src/components/RepositoryPriority.tsx (new)
import { useState, useEffect } from 'react';
import { FeatureFlags } from '@/config/featureFlags';
import { RepositoryInfo } from '@/types/repoinfo';

interface RepositoryPriorityProps {
  repositories: RepositoryInfo[];
  onRepositoriesChange: (repos: RepositoryInfo[]) => void;
  showAdvanced?: boolean;
}

const RepositoryPriority: React.FC<RepositoryPriorityProps> = (props) => {
  // Check feature flag before rendering
  if (!FeatureFlags.isMultiRepoEnabled()) {
    // Graceful degradation: return null when feature is disabled
    return null;
  }
  
  const [showAdvanced, setShowAdvanced] = useState(props.showAdvanced || false);
  
  const updatePriority = (index: number, priority: number) => {
    const newRepositories = props.repositories.map((repo, i) => 
      i === index ? { ...repo, priority_weight: priority } : repo
    );
    props.onRepositoriesChange(newRepositories);
  };
  
  const setEqualPriority = () => {
    const newRepositories = props.repositories.map(repo => ({
      ...repo,
      priority_weight: 1.0
    }));
    props.onRepositoriesChange(newRepositories);
  };
  
  const setLinearPriority = () => {
    const newRepositories = props.repositories.map((repo, index) => ({
      ...repo,
      priority_weight: Math.max(0.1, 10.0 - (index * 0.5))
    }));
    props.onRepositoriesChange(newRepositories);
  };
  
  const setExponentialPriority = () => {
    const newRepositories = props.repositories.map((repo, index) => ({
      ...repo,
      priority_weight: Math.max(0.1, Math.pow(2, 10 - index))
    }));
    props.onRepositoriesChange(newRepositories);
  };
  
  const sortedRepositories = [...props.repositories].sort(
    (a, b) => (b.priority_weight || 1.0) - (a.priority_weight || 1.0)
  );
  
  return (
    <div className="repository-priority bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Repository Priority Management
      </h3>
      
      {/* Priority presets */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Priority Presets</h4>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={setEqualPriority}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            Equal Priority
          </button>
          <button
            onClick={setLinearPriority}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            Linear Priority
          </button>
          <button
            onClick={setExponentialPriority}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            Exponential Priority
          </button>
        </div>
      </div>
      
      {/* Priority sliders */}
      <div className="space-y-4">
        {sortedRepositories.map((repo, index) => (
          <div key={`${repo.owner}-${repo.repo}`} className="flex items-center space-x-4">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">
                  {repo.alias || `${repo.owner}/${repo.repo}`}
                </span>
                <span className="text-sm text-gray-500">
                  Priority: {repo.priority_weight?.toFixed(1) || '1.0'}
                </span>
              </div>
              <input
                type="range"
                min="0.1"
                max="10.0"
                step="0.1"
                value={repo.priority_weight || 1.0}
                onChange={(e) => {
                  const repoIndex = props.repositories.findIndex(
                    r => r.owner === repo.owner && r.repo === repo.repo
                  );
                  if (repoIndex !== -1) {
                    updatePriority(repoIndex, Number(e.target.value));
                  }
                }}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          </div>
        ))}
      </div>
      
      {/* Advanced options */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          {showAdvanced ? 'Hide' : 'Show'} Advanced Options
        </button>
        
        {showAdvanced && (
          <div className="mt-3 space-y-3">
            <div className="text-xs text-gray-500">
              <p><strong>Equal Priority:</strong> All repositories have the same weight (1.0)</p>
              <p><strong>Linear Priority:</strong> Priority decreases linearly from first to last</p>
              <p><strong>Exponential Priority:</strong> Priority decreases exponentially from first to last</p>
              <p><strong>Custom Priority:</strong> Manually adjust each repository's priority weight</p>
            </div>
            
            <div className="text-xs text-gray-500">
              <p><strong>Priority Weight Range:</strong> 0.1 (lowest) to 10.0 (highest)</p>
              <p><strong>Context Balancing:</strong> Higher priority repositories get more context allocation</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RepositoryPriority;
```

### Feature Flag Protection Requirements
- All components must check feature flag before rendering
- Graceful degradation when feature is disabled
- No errors or crashes when feature flag changes
- Consistent behavior across all components

## Subtasks

### Subtask 1: MultiRepositoryInput Component
- [ ] Create component structure and interface
- [ ] Implement repository management functionality
- [ ] Add context configuration fields
- [ ] Test component functionality
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 2: RepositoryList Component
- [ ] Create component structure and interface
- [ ] Implement drag-and-drop functionality
- [ ] Add repository management actions
- [ ] Test component functionality
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 3: RepositoryPriority Component
- [ ] Create component structure and interface
- [ ] Implement priority management functionality
- [ ] Add priority preset options
- [ ] Test component functionality
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

### Subtask 4: Feature Flag Integration
- [ ] Add feature flag checks to all components
- [ ] Implement graceful degradation
- [ ] Test feature flag disabled state
- [ ] Validate fallback mechanisms
- [ ] **Status**: 🔴 Not Started
- [ ] **Progress**: 0%

## Dependencies
- TASK026: Phase 4.1: Frontend Feature Flag Infrastructure
- TASK027: Phase 4.2: Enhanced Type Definitions with Feature Flag Protection
- Existing component infrastructure

## Deliverables
1. `src/components/MultiRepositoryInput.tsx` - Multi-repository input interface
2. `src/components/RepositoryList.tsx` - Drag-and-drop repository list management
3. `src/components/RepositoryPriority.tsx` - Repository priority controls
4. Feature flag protection for all components
5. Graceful degradation mechanisms
6. Comprehensive testing for all component scenarios

## Success Criteria
- [ ] All components are fully functional when feature flag is enabled
- [ ] Components gracefully degrade when feature flag is disabled
- [ ] Feature flag protection works correctly across all components
- [ ] All component functionality is properly tested
- [ ] Components integrate seamlessly with existing system
- [ ] No errors or crashes occur during feature flag changes
- [ ] All components maintain consistent behavior

## Progress Log

### 2024-12-19 - Task Created
- Task created based on Implementation Phases section
- Implementation plan defined
- Subtasks identified and structured
- Dependencies identified

## Notes
- All components must be feature flag protected
- Graceful degradation is critical for system stability
- Components should be reusable and modular
- Feature flag checks should be consistent across all components
- Testing should cover both enabled and disabled states
- Components should integrate well with existing architecture
