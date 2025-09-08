// Repository-related types
export interface ProcessedProject {
  id: string;
  owner: string;
  repo: string;
  name: string;
  repo_type: string;
  submittedAt: number;
  language: string;
}

export interface RepositoryState {
  selectedRepositories: string[];
  isMultiRepositoryMode: boolean;
  currentRepository: string;
}

// URL parsing utilities types
export interface ParsedRepository {
  owner: string;
  repo: string;
  type: 'github' | 'gitlab' | 'bitbucket';
  url: string;
}
