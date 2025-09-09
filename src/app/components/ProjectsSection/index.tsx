import React from 'react';
import ExistingProjectsPanel from '@/components/ExistingProjectsPanel';

interface ProcessedProject {
  id: string;
  owner: string;
  repo: string;
  name: string;
  repo_type: string;
  submittedAt: number;
  language: string;
}

interface ProjectsSectionProps {
  projects: ProcessedProject[];
  isLoading: boolean;
  selectedRepository: string;
  selectedRepositories: string[];
  isMultiRepositoryMode: boolean;
  searchQuery: string;
  viewMode: 'grid' | 'list';
  onRepositorySelect: (repoUrl: string) => void;
  onRepositoriesChange: (repoUrls: string[]) => void;
  onMultiRepositoryModeChange: (enabled: boolean) => void;
  onSearchQueryChange: (query: string) => void;
  onViewModeChange: (mode: 'grid' | 'list') => void;
  onMobileTabSwitch?: () => void;
}

const ProjectsSection: React.FC<ProjectsSectionProps> = ({
  projects,
  isLoading,
  selectedRepository,
  selectedRepositories,
  isMultiRepositoryMode,
  searchQuery,
  viewMode,
  onRepositorySelect,
  onRepositoriesChange,
  onMultiRepositoryModeChange,
  onSearchQueryChange,
  onViewModeChange,
  onMobileTabSwitch,
}) => {
  const handleRepositorySelect = (repoUrl: string) => {
    onRepositorySelect(repoUrl);
    // Auto-switch to chat tab on mobile when a repository is selected
    if (onMobileTabSwitch) {
      onMobileTabSwitch();
    }
  };

  return (
    <div className="h-full flex flex-col">
      <ExistingProjectsPanel
        projects={projects}
        onRepositorySelect={handleRepositorySelect}
        selectedRepository={selectedRepository}
        selectedRepositories={selectedRepositories}
        onRepositoriesChange={onRepositoriesChange}
        isMultiSelectMode={isMultiRepositoryMode}
        onMultiSelectModeChange={onMultiRepositoryModeChange}
        isLoading={isLoading}
        searchQuery={searchQuery}
        onSearchQueryChange={onSearchQueryChange}
        viewMode={viewMode}
        onViewModeChange={onViewModeChange}
      />
    </div>
  );
};

export default ProjectsSection;
