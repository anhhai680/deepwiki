// TypeScript interfaces for two-column layout components
import { RepoInfo } from '@/types/repoinfo';

export interface ProcessedProject {
  id: string;
  owner: string;
  repo: string;
  name: string;
  repo_type: string;
  submittedAt: number;
  language: string;
}

export interface HomePageAskState {
  selectedRepository: string;
  selectedRepositories: string[]; // For multi-repository mode
  repoInfo: RepoInfo | null;
  repoInfos: RepoInfo[]; // For multi-repository mode
  showAskSection: boolean;
  isMultiRepositoryMode: boolean; // Toggle for multi-repository mode
}

export interface ExistingProjectsPanelProps {
  projects: ProcessedProject[];
  onRepositorySelect: (repo: string) => void;
  selectedRepository: string;
  // Multi-repository support
  selectedRepositories?: string[];
  onRepositoriesChange?: (repos: string[]) => void;
  isMultiSelectMode?: boolean;
  onMultiSelectModeChange?: (enabled: boolean) => void;
  // Existing props
  isLoading: boolean;
  searchQuery: string;
  onSearchQueryChange: (query: string) => void;
  viewMode: 'grid' | 'list';
  onViewModeChange: (mode: 'grid' | 'list') => void;
}

export interface ChatPanelProps {
  repoInfo: RepoInfo | null;
  repoInfos?: RepoInfo[]; // For multi-repository mode
  projects: ProcessedProject[];
  provider?: string;
  model?: string;
  isCustomModel?: boolean;
  customModel?: string;
  language?: string;
  className?: string;
  isMultiRepositoryMode?: boolean; // Indicate if in multi-repository mode
}

// Re-export existing types for convenience
export type { RepoInfo } from '@/types/repoinfo';
