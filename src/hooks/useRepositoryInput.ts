import { useCallback } from 'react';
import { RepoInfo } from '@/types/repoinfo';

const REPO_CONFIG_CACHE_KEY = 'deepwikiRepoConfigCache';

interface RepoConfig {
  isComprehensiveView?: boolean;
  provider?: string;
  model?: string;
  isCustomModel?: boolean;
  customModel?: string;
  selectedPlatform?: 'github' | 'gitlab' | 'bitbucket';
  excludedDirs?: string;
  excludedFiles?: string;
  includedDirs?: string;
  includedFiles?: string;
}

interface ParsedRepository {
  owner: string;
  repo: string;
  type: 'github' | 'gitlab' | 'bitbucket' | 'local';
  localPath?: string;
}

export const useRepositoryInput = () => {
  // Parse repository input to extract owner, repo, and type
  const parseRepositoryInput = useCallback((input: string): ParsedRepository | null => {
    if (!input.trim()) return null;

    // Handle local paths
    if (input.startsWith('/') || input.startsWith('./') || input.startsWith('../')) {
      return {
        owner: '',
        repo: input.split('/').pop() || 'unknown',
        type: 'local',
        localPath: input,
      };
    }

    // Handle URLs
    const urlPatterns = [
      // GitHub patterns
      { pattern: /github\.com\/([^\/]+)\/([^\/\?#]+)/, type: 'github' as const },
      // GitLab patterns
      { pattern: /gitlab\.com\/([^\/]+)\/([^\/\?#]+)/, type: 'gitlab' as const },
      // Bitbucket patterns
      { pattern: /bitbucket\.org\/([^\/]+)\/([^\/\?#]+)/, type: 'bitbucket' as const },
    ];

    for (const { pattern, type } of urlPatterns) {
      const match = input.match(pattern);
      if (match) {
        return {
          owner: match[1],
          repo: match[2].replace(/\.git$/, ''), // Remove .git suffix
          type,
        };
      }
    }

    return null;
  }, []);

  // Load configuration from cache
  const loadConfigFromCache = useCallback((repoUrl: string): RepoConfig | null => {
    if (!repoUrl) return null;
    
    try {
      const cachedConfigs = localStorage.getItem(REPO_CONFIG_CACHE_KEY);
      if (cachedConfigs) {
        const configs = JSON.parse(cachedConfigs);
        return configs[repoUrl.trim()] || null;
      }
    } catch (error) {
      console.error('Error loading config from localStorage:', error);
    }
    
    return null;
  }, []);

  // Save configuration to cache
  const saveConfigToCache = useCallback((repoUrl: string, config: RepoConfig) => {
    if (!repoUrl) return;
    
    try {
      const cachedConfigs = localStorage.getItem(REPO_CONFIG_CACHE_KEY);
      const configs = cachedConfigs ? JSON.parse(cachedConfigs) : {};
      configs[repoUrl.trim()] = config;
      localStorage.setItem(REPO_CONFIG_CACHE_KEY, JSON.stringify(configs));
    } catch (error) {
      console.error('Error saving config to localStorage:', error);
    }
  }, []);

  // Create RepoInfo from repository URL
  const createRepoInfo = useCallback((repoUrl: string, accessToken?: string): RepoInfo | null => {
    const parsed = parseRepositoryInput(repoUrl);
    if (!parsed) return null;

    return {
      owner: parsed.owner,
      repo: parsed.repo,
      type: parsed.type,
      token: accessToken || null,
      localPath: parsed.localPath || null,
      repoUrl: repoUrl,
    };
  }, [parseRepositoryInput]);

  // Validate repository URL format
  const validateRepositoryUrl = useCallback((url: string): { isValid: boolean; error?: string } => {
    if (!url.trim()) {
      return { isValid: false, error: 'Repository URL is required' };
    }

    const parsed = parseRepositoryInput(url);
    if (!parsed) {
      return { isValid: false, error: 'Invalid repository URL format' };
    }

    return { isValid: true };
  }, [parseRepositoryInput]);

  return {
    parseRepositoryInput,
    loadConfigFromCache,
    saveConfigToCache,
    createRepoInfo,
    validateRepositoryUrl,
  };
};
