import { useCallback } from 'react';
import { RepoInfo } from '@/types/repoinfo';
import { useRepositoryInput } from './useRepositoryInput';

export const useProjectManagement = () => {
  const { createRepoInfo, parseRepositoryInput } = useRepositoryInput();

  // Handle single repository selection for Ask UI
  const handleAskRepositorySelect = useCallback((
    repoUrl: string,
    accessToken: string | null,
    setSelectedRepository: (repo: string) => void,
    setRepoInfo: (info: RepoInfo | null) => void
  ) => {
    setSelectedRepository(repoUrl);
    
    const newRepoInfo = createRepoInfo(repoUrl, accessToken || undefined);
    setRepoInfo(newRepoInfo);
  }, [createRepoInfo]);

  // Handle multiple repository selection for multi-repository mode
  const handleRepositoriesChange = useCallback((
    repoUrls: string[],
    accessToken: string | null,
    setSelectedRepositories: (repos: string[]) => void,
    setRepoInfos: (infos: RepoInfo[]) => void
  ) => {
    setSelectedRepositories(repoUrls);
    
    // Parse repository URLs to create RepoInfo array
    const newRepoInfos: RepoInfo[] = repoUrls.map(repoUrl => {
      const parsed = parseRepositoryInput(repoUrl);
      if (parsed) {
        return {
          owner: parsed.owner,
          repo: parsed.repo,
          type: parsed.type,
          token: accessToken,
          localPath: parsed.localPath || null,
          repoUrl: repoUrl,
        } as RepoInfo;
      }
      return null;
    }).filter((info): info is RepoInfo => info !== null);
    
    setRepoInfos(newRepoInfos);
  }, [parseRepositoryInput]);

  // Handle multi-repository mode toggle
  const handleMultiRepositoryModeChange = useCallback((
    enabled: boolean,
    setIsMultiRepositoryMode: (mode: boolean) => void,
    setSelectedRepositories: (repos: string[]) => void,
    setRepoInfos: (infos: RepoInfo[]) => void,
    setSelectedRepository: (repo: string) => void,
    setRepoInfo: (info: RepoInfo | null) => void
  ) => {
    setIsMultiRepositoryMode(enabled);
    if (!enabled) {
      // When switching to single mode, clear multi-selections
      setSelectedRepositories([]);
      setRepoInfos([]);
    } else {
      // When switching to multi mode, clear single selection
      setSelectedRepository('');
      setRepoInfo(null);
    }
  }, []);

  return {
    handleAskRepositorySelect,
    handleRepositoriesChange,
    handleMultiRepositoryModeChange,
  };
};
