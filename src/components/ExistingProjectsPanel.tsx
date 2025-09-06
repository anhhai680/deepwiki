'use client';

import React, { useRef, useEffect } from 'react';
import { FaTh, FaList, FaCheck } from 'react-icons/fa';
import { useRouter } from 'next/navigation';
import { ExistingProjectsPanelProps, ProcessedProject } from '@/types/home-page-ask';
import { RepositoryType } from '@/constants';

export default function ExistingProjectsPanel({
  projects,
  onRepositorySelect,
  selectedRepository,
  selectedRepositories = [],
  onRepositoriesChange,
  isMultiSelectMode = false,
  onMultiSelectModeChange,
  isLoading,
  searchQuery,
  onSearchQueryChange,
  viewMode,
  onViewModeChange,
}: ExistingProjectsPanelProps) {
  const router = useRouter();
  const clickTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (clickTimeoutRef.current) {
        clearTimeout(clickTimeoutRef.current);
      }
    };
  }, []);

  // Filter projects based on search query
  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.owner.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.repo.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getRepositoryUrl = (project: ProcessedProject): string => {
    let repositoryUrl: string;
    
    // Generate URL based on platform type
    switch (project.repo_type.toLowerCase()) {
      case 'gitlab':
        repositoryUrl = `${RepositoryType.gitlab}/${project.owner}/${project.repo}`;
        break;
      case 'bitbucket':
        repositoryUrl = `${RepositoryType.bitbucket}/${project.owner}/${project.repo}`;
        break;
      case 'github':
      default:
        repositoryUrl = `${RepositoryType.github}/${project.owner}/${project.repo}`;
        break;
    }
    
    return repositoryUrl;
  }

  // Handle repository selection (single click)
  const handleRepositoryClick = (project: ProcessedProject) => {
    const repositoryUrl = getRepositoryUrl(project);
    
    if (isMultiSelectMode) {
      // Multi-select mode: toggle repository in selection
      if (onRepositoriesChange) {
        const isSelected = selectedRepositories.includes(repositoryUrl);
        if (isSelected) {
          onRepositoriesChange(selectedRepositories.filter(url => url !== repositoryUrl));
        } else {
          onRepositoriesChange([...selectedRepositories, repositoryUrl]);
        }
      }
    } else {
      // Single select mode: use existing behavior
      onRepositorySelect(repositoryUrl);
    }
  };

  // Handle repository navigation (double click)
  const handleRepositoryDoubleClick = (project: ProcessedProject) => {
    const repositoryUrl = `/${project.owner}/${project.repo}?type=${project.repo_type}&language=${project.language}`;
    router.push(repositoryUrl);
  };

  // Combined click handler that distinguishes between single and double clicks
  const handleRepositoryInteraction = (project: ProcessedProject) => {
    if (clickTimeoutRef.current) {
      // Double click detected
      clearTimeout(clickTimeoutRef.current);
      clickTimeoutRef.current = null;
      handleRepositoryDoubleClick(project);
    } else {
      // Single click - set timeout to check if it becomes a double click
      clickTimeoutRef.current = setTimeout(() => {
        handleRepositoryClick(project);
        clickTimeoutRef.current = null;
      }, 300); // 300ms delay to detect double click
    }
  };

  // Handle select all / clear all
  const handleSelectAll = () => {
    if (onRepositoriesChange) {
      if (selectedRepositories.length === filteredProjects.length) {
        // Clear all
        onRepositoriesChange([]);
      } else {
        // Select all visible projects
        const allUrls = filteredProjects.map(getRepositoryUrl);
        onRepositoriesChange(allUrls);
      }
    }
  };

  return (
    <div className="h-full flex flex-col bg-[var(--card-bg)]">
      {/* Header with multi-select toggle */}
      <div className="p-4 border-b border-[var(--border-color)]">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold text-[var(--foreground)]">
            Projects
          </h2>
          {onMultiSelectModeChange && (
            <button
              onClick={() => onMultiSelectModeChange(!isMultiSelectMode)}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${
                isMultiSelectMode
                  ? 'bg-[var(--accent-primary)] text-white'
                  : 'bg-[var(--background)] text-[var(--muted)] border border-[var(--border-color)] hover:text-[var(--foreground)]'
              }`}
              title={isMultiSelectMode ? 'Switch to single selection' : 'Enable multi-selection'}
            >
              {isMultiSelectMode ? 'Multi-Select' : 'Single'}
            </button>
          )}
        </div>
        
        <div className="flex items-center justify-between">
          <p className="text-sm text-[var(--muted)]">
            {isMultiSelectMode 
              ? `${selectedRepositories.length} of ${projects.length} selected`
              : `${projects.length} repositories processed`
            }
          </p>
          {isMultiSelectMode && selectedRepositories.length > 0 && onRepositoriesChange && (
            <button
              onClick={handleSelectAll}
              className="text-xs text-[var(--accent-primary)] hover:underline"
            >
              {selectedRepositories.length === filteredProjects.length ? 'Clear All' : 'Select All'}
            </button>
          )}
        </div>

        {/* Search input */}
        <div className="relative mt-3">
          <input
            type="text"
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => onSearchQueryChange(e.target.value)}
            className="w-full px-3 py-2 text-sm bg-[var(--background)] border border-[var(--border-color)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]/50 focus:border-[var(--accent-primary)] transition-colors placeholder-[var(--muted)]"
          />
          <svg className="absolute right-3 top-2.5 h-4 w-4 text-[var(--muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        {/* View toggle */}
        <div className="flex items-center gap-1 mt-3">
          <button
            onClick={() => onViewModeChange('grid')}
            className={`p-2 rounded-md transition-colors ${
              viewMode === 'grid'
                ? 'bg-[var(--accent-primary)] text-white'
                : 'text-[var(--muted)] hover:text-[var(--foreground)] hover:bg-[var(--background)]'
            }`}
          >
            <FaTh className="text-xs" />
          </button>
          <button
            onClick={() => onViewModeChange('list')}
            className={`p-2 rounded-md transition-colors ${
              viewMode === 'list'
                ? 'bg-[var(--accent-primary)] text-white'
                : 'text-[var(--muted)] hover:text-[var(--foreground)] hover:bg-[var(--background)]'
            }`}
          >
            <FaList className="text-xs" />
          </button>
        </div>
      </div>

      {/* Projects list */}
      <div className="flex-1 overflow-y-auto p-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="text-[var(--muted)]">Loading projects...</div>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="flex items-center justify-center h-32">
            <div className="text-center text-[var(--muted)]">
              {searchQuery ? 'No projects match your search.' : 'No projects found.'}
            </div>
          </div>
        ) : (
          <div className={viewMode === 'grid' ? 'grid grid-cols-1 gap-3' : 'space-y-2'}>
            {filteredProjects.map((project) => {
              const repositoryUrl = getRepositoryUrl(project);
              
              const isSelected = isMultiSelectMode 
                ? selectedRepositories.includes(repositoryUrl)
                : selectedRepository === repositoryUrl;
              
              return (
                <div
                  key={project.id}
                  onClick={() => handleRepositoryInteraction(project)}
                  className={`cursor-pointer p-4 rounded-lg border transition-all duration-200 hover:shadow-md ${
                    isSelected
                      ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/10'
                      : 'border-[var(--border-color)] bg-[var(--background)] hover:border-[var(--accent-primary)]/50'
                  }`}
                  title={isMultiSelectMode 
                    ? "Click to toggle selection • Double click to view details"
                    : "Single click to select • Double click to view details"
                  }
                >
                  <div className="flex items-center gap-3">
                    {/* Multi-select checkbox */}
                    {isMultiSelectMode && (
                      <div className="flex-shrink-0">
                        <div className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-colors ${
                          isSelected
                            ? 'bg-[var(--accent-primary)] border-[var(--accent-primary)] text-white'
                            : 'border-[var(--border-color)] bg-[var(--background)]'
                        }`}>
                          {isSelected && <FaCheck className="text-xs" />}
                        </div>
                      </div>
                    )}
                    
                    {/* Repository type indicator */}
                    <div className={`w-3 h-3 rounded-full flex-shrink-0 ${
                      project.repo_type === 'github' ? 'bg-[var(--accent-primary)]' :
                      project.repo_type === 'gitlab' ? 'bg-orange-500' :
                      project.repo_type === 'bitbucket' ? 'bg-blue-500' :
                      'bg-gray-500'
                    }`} />
                    
                    {/* Repository info */}
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-[var(--foreground)] truncate text-base">
                        {project.name}
                      </div>
                      <div className="text-sm text-[var(--muted)] truncate mt-1">
                        {project.owner}/{project.repo}
                      </div>
                      {viewMode === 'list' && (
                        <div className="text-xs text-[var(--muted)] mt-2">
                          {project.language} • {new Date(project.submittedAt * 1000).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
