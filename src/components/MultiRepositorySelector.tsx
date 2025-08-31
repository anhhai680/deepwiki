'use client';

import React, { useState, useMemo } from 'react';
import { FaChevronDown, FaSearch, FaGithub, FaGitlab, FaBitbucket, FaTimes } from 'react-icons/fa';
import { useLanguage } from '@/contexts/LanguageContext';

interface ProcessedProject {
  id: string;
  owner: string;
  repo: string;
  name: string;
  repo_type: string;
  submittedAt: number;
  language: string;
}

interface MultiRepositorySelectorProps {
  projects: ProcessedProject[];
  selectedRepositories: string[];
  onRepositoriesChange: (repositories: string[]) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export default function MultiRepositorySelector({
  projects,
  selectedRepositories,
  onRepositoriesChange,
  placeholder = "Select repositories...",
  className = "",
  disabled = false
}: MultiRepositorySelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const { messages } = useLanguage();

  // Create translation function
  const t = (key: string): string => {
    const keys = key.split('.');
    let value: unknown = messages;
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = (value as Record<string, unknown>)[k];
      } else {
        return key;
      }
    }
    
    return typeof value === 'string' ? value : key;
  };

  // Filter projects based on search term and exclude already selected ones
  const availableProjects = useMemo(() => {
    if (!searchTerm.trim()) {
      return projects.filter(project => 
        !selectedRepositories.includes(`https://${project.repo_type}.com/${project.owner}/${project.repo}`)
      );
    }
    
    const search = searchTerm.toLowerCase();
    return projects.filter(project => {
      const isMatch = project.name.toLowerCase().includes(search) ||
                     project.owner.toLowerCase().includes(search) ||
                     project.repo.toLowerCase().includes(search);
      const isNotSelected = !selectedRepositories.includes(`https://${project.repo_type}.com/${project.owner}/${project.repo}`);
      return isMatch && isNotSelected;
    });
  }, [projects, searchTerm, selectedRepositories]);

  // Get platform icon
  const getPlatformIcon = (repoType: string) => {
    switch (repoType.toLowerCase()) {
      case 'github':
        return <FaGithub className="text-sm" />;
      case 'gitlab':
        return <FaGitlab className="text-sm" />;
      case 'bitbucket':
        return <FaBitbucket className="text-sm" />;
      default:
        return <FaGithub className="text-sm" />;
    }
  };

  // Format repository display name
  const formatRepoName = (project: ProcessedProject) => {
    return `${project.owner}/${project.repo}`;
  };

  // Handle repository selection
  const handleSelect = (project: ProcessedProject) => {
    let repoUrl: string;
    
    // Generate URL based on platform type
    switch (project.repo_type.toLowerCase()) {
      case 'gitlab':
        repoUrl = `https://gitlab.com/${project.owner}/${project.repo}`;
        break;
      case 'bitbucket':
        repoUrl = `https://bitbucket.org/${project.owner}/${project.repo}`;
        break;
      case 'github':
      default:
        repoUrl = `https://github.com/${project.owner}/${project.repo}`;
        break;
    }
    
    onRepositoriesChange([...selectedRepositories, repoUrl]);
    setSearchTerm('');
  };

  // Handle repository removal
  const handleRemove = (repoUrl: string) => {
    onRepositoriesChange(selectedRepositories.filter(url => url !== repoUrl));
  };

  // Handle manual URL input
  const handleManualInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const urls = e.target.value.split('\n').filter(url => url.trim());
    onRepositoriesChange(urls);
  };

  return (
    <div className={`relative ${className}`}>
      {/* Selected repositories display */}
      {selectedRepositories.length > 0 && (
        <div className="mb-3 space-y-2">
          <div className="text-xs text-[var(--muted)]">Selected Repositories:</div>
          {selectedRepositories.map((repoUrl, index) => (
            <div key={index} className="flex items-center gap-2 p-2 bg-[var(--background)] border border-[var(--border-color)] rounded-md">
              <div className="flex-1 text-sm text-[var(--foreground)] truncate">
                {repoUrl}
              </div>
              <button
                type="button"
                onClick={() => handleRemove(repoUrl)}
                className="text-[var(--muted)] hover:text-[var(--highlight)] transition-colors"
                disabled={disabled}
              >
                <FaTimes className="text-xs" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Repository selector */}
      <div className="relative">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={placeholder}
          className="input-japanese block w-full pl-10 pr-10 py-2.5 border-[var(--border-color)] rounded-lg bg-transparent text-[var(--foreground)] focus:outline-none focus:border-[var(--accent-primary)] disabled:opacity-50"
          disabled={disabled}
        />
        
        {/* Search icon */}
        <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--muted)]">
          <FaSearch className="text-sm" />
        </div>
        
        {/* Dropdown toggle button */}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          disabled={disabled}
          className="absolute right-2 top-1/2 transform -translate-y-1/2 text-[var(--muted)] hover:text-[var(--foreground)] transition-colors disabled:opacity-50"
        >
          <FaChevronDown className={`text-sm transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </button>
      </div>

      {/* Dropdown menu */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg shadow-lg z-50 max-h-64 overflow-hidden">
          {/* Search input in dropdown */}
          <div className="p-3 border-b border-[var(--border-color)]">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={t('form.searchRepositories') || "Search repositories..."}
              className="w-full px-3 py-2 text-sm bg-[var(--background)] border border-[var(--border-color)] rounded-md text-[var(--foreground)] focus:outline-none focus:border-[var(--accent-primary)]"
            />
          </div>

          {/* Repository list */}
          <div className="max-h-48 overflow-y-auto">
            {availableProjects.length > 0 ? (
              availableProjects.map((project) => (
                <button
                  key={project.id}
                  type="button"
                  onClick={() => handleSelect(project)}
                  className="w-full px-3 py-2 text-left hover:bg-[var(--background)] transition-colors border-b border-[var(--border-color)]/30 last:border-b-0"
                >
                  <div className="flex items-center gap-2">
                    {getPlatformIcon(project.repo_type)}
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-[var(--foreground)] truncate">
                        {formatRepoName(project)}
                      </div>
                      <div className="text-xs text-[var(--muted)] truncate">
                        {project.name}
                      </div>
                    </div>
                    <div className="text-xs text-[var(--muted)]">
                      {new Date(project.submittedAt).toLocaleDateString()}
                    </div>
                  </div>
                </button>
              ))
            ) : (
              <div className="px-3 py-4 text-center text-[var(--muted)] text-sm">
                {searchTerm ? 'No repositories found' : 'No repositories available'}
              </div>
            )}
          </div>

          {/* Manual input option */}
          <div className="p-3 border-t border-[var(--border-color)] bg-[var(--background)]/50">
            <div className="text-xs text-[var(--muted)] mb-2">
              {t('form.orEnterManually') || "Or enter repository URLs manually below (one per line)"}
            </div>
            <textarea
              value={selectedRepositories.join('\n')}
              onChange={handleManualInput}
              placeholder="https://github.com/owner/repo1&#10;https://github.com/owner/repo2&#10;https://gitlab.com/owner/repo3"
              className="w-full px-3 py-2 text-sm bg-[var(--background)] border border-[var(--border-color)] rounded-md text-[var(--foreground)] focus:outline-none focus:border-[var(--accent-primary)] resize-none"
              rows={3}
              disabled={disabled}
            />
            <div className="text-xs text-[var(--muted)] mt-2">
              {availableProjects.length} of {projects.length} repositories available
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
