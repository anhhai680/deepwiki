import { useState } from 'react';
import { RepoInfo } from '@/types/repoinfo';

interface HomePageConfig {
  isComprehensiveView: boolean;
  provider: string;
  model: string;
  isCustomModel: boolean;
  customModel: string;
  selectedPlatform: 'github' | 'gitlab' | 'bitbucket';
  excludedDirs: string;
  excludedFiles: string;
  includedDirs: string;
  includedFiles: string;
}

interface AuthState {
  authRequired: boolean;
  authCode: string;
  isAuthLoading: boolean;
}

export const useHomePageState = () => {
  // Repository input state
  const [repositoryInput, setRepositoryInput] = useState('https://github.com/your-repository');
  
  // Configuration state
  const [config, setConfig] = useState<HomePageConfig>({
    isComprehensiveView: true,
    provider: '',
    model: '',
    isCustomModel: false,
    customModel: '',
    selectedPlatform: 'github',
    excludedDirs: '',
    excludedFiles: '',
    includedDirs: '',
    includedFiles: '',
  });

  // Authentication state
  const [authState, setAuthState] = useState<AuthState>({
    authRequired: false,
    authCode: '',
    isAuthLoading: true,
  });

  // Access token and error states
  const [accessToken, setAccessToken] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Repository selection state
  const [selectedRepository, setSelectedRepository] = useState<string>('');
  const [selectedRepositories, setSelectedRepositories] = useState<string[]>([]);
  const [isMultiRepositoryMode, setIsMultiRepositoryMode] = useState<boolean>(false);
  const [repoInfo, setRepoInfo] = useState<RepoInfo | null>(null);
  const [repoInfos, setRepoInfos] = useState<RepoInfo[]>([]);

  // UI state
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [mobileActiveTab, setMobileActiveTab] = useState<'projects' | 'chat'>('projects');

  return {
    // Repository input
    repositoryInput,
    setRepositoryInput,
    
    // Configuration
    config,
    setConfig,
    
    // Authentication
    authState,
    setAuthState,
    
    // Access and error states
    accessToken,
    setAccessToken,
    error,
    setError,
    isSubmitting,
    setIsSubmitting,
    
    // Repository selection
    selectedRepository,
    setSelectedRepository,
    selectedRepositories,
    setSelectedRepositories,
    isMultiRepositoryMode,
    setIsMultiRepositoryMode,
    repoInfo,
    setRepoInfo,
    repoInfos,
    setRepoInfos,
    
    // UI state
    searchQuery,
    setSearchQuery,
    viewMode,
    setViewMode,
    mobileActiveTab,
    setMobileActiveTab,
  };
};
