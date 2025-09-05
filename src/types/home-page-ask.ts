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
  repoInfo: RepoInfo | null;
  showAskSection: boolean;
}

export interface ExistingProjectsPanelProps {
  projects: ProcessedProject[];
  onRepositorySelect: (repo: string) => void;
  selectedRepository: string;
  isLoading: boolean;
  searchQuery: string;
  onSearchQueryChange: (query: string) => void;
  viewMode: 'grid' | 'list';
  onViewModeChange: (mode: 'grid' | 'list') => void;
}

export interface ChatPanelProps {
  repoInfo: RepoInfo | null;
  projects: ProcessedProject[];
  provider?: string;
  model?: string;
  isCustomModel?: boolean;
  customModel?: string;
  language?: string;
  className?: string;
}

// Re-export existing types for convenience
export type { RepoInfo } from '@/types/repoinfo';
