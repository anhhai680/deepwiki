'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { FaWikipediaW, FaGithub, FaCoffee, FaTwitter } from 'react-icons/fa';
import ThemeToggle from '@/components/theme-toggle';
import ConfigurationModal from '@/components/ConfigurationModal';
import RepositorySelector from '@/components/RepositorySelector';
import ExistingProjectsPanel from '@/components/ExistingProjectsPanel';
import ChatPanel from '@/components/ChatPanel';
import { extractUrlPath, extractUrlDomain } from '@/utils/urlDecoder';
import { useProcessedProjects } from '@/hooks/useProcessedProjects';
import { RepoInfo } from '@/types/repoinfo';

import { useLanguage } from '@/contexts/LanguageContext';

export default function Home() {
  const router = useRouter();
  const { language, setLanguage, messages, supportedLanguages } = useLanguage();
  const { projects, isLoading: projectsLoading } = useProcessedProjects();

  // Create a simple translation function
  const t = (key: string, params: Record<string, string | number> = {}): string => {
    // Split the key by dots to access nested properties
    const keys = key.split('.');
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let value: any = messages;

    // Navigate through the nested properties
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // Return the key if the translation is not found
        return key;
      }
    }

    // If the value is a string, replace parameters
    if (typeof value === 'string') {
      return Object.entries(params).reduce((acc: string, [paramKey, paramValue]) => {
        return acc.replace(`{${paramKey}}`, String(paramValue));
      }, value);
    }

    // Return the key if the value is not a string
    return key;
  };

  const [repositoryInput, setRepositoryInput] = useState('https://github.com/your-repository');

  const REPO_CONFIG_CACHE_KEY = 'deepwikiRepoConfigCache';

  const loadConfigFromCache = useCallback((repoUrl: string) => {
    if (!repoUrl) return;
    try {
      const cachedConfigs = localStorage.getItem(REPO_CONFIG_CACHE_KEY);
      if (cachedConfigs) {
        const configs = JSON.parse(cachedConfigs);
        const config = configs[repoUrl.trim()];
        if (config) {
          setSelectedLanguage(config.selectedLanguage || language);
          setIsComprehensiveView(config.isComprehensiveView === undefined ? true : config.isComprehensiveView);
          setProvider(config.provider || '');
          setModel(config.model || '');
          setIsCustomModel(config.isCustomModel || false);
          setCustomModel(config.customModel || '');
          setSelectedPlatform(config.selectedPlatform || 'github');
          setExcludedDirs(config.excludedDirs || '');
          setExcludedFiles(config.excludedFiles || '');
          setIncludedDirs(config.includedDirs || '');
          setIncludedFiles(config.includedFiles || '');
        }
      }
    } catch (error) {
      console.error('Error loading config from localStorage:', error);
    }
  }, [language]);

  // Handle repository selection changes
  const handleRepositorySelect = (newRepoUrl: string) => {
    setRepositoryInput(newRepoUrl);
    if (newRepoUrl.trim() !== "") {
      loadConfigFromCache(newRepoUrl);
    }
  };

  useEffect(() => {
    if (repositoryInput) {
      loadConfigFromCache(repositoryInput);
    }
  }, [repositoryInput, loadConfigFromCache]);

  // Handle repository selection for Ask UI
  const handleAskRepositorySelect = (repoUrl: string) => {
    setSelectedRepository(repoUrl);
    
    // Parse the repository URL to create RepoInfo
    const parsed = parseRepositoryInput(repoUrl);
    if (parsed) {
      const newRepoInfo: RepoInfo = {
        owner: parsed.owner,
        repo: parsed.repo,
        type: parsed.type,
        token: accessToken || null,
        localPath: parsed.localPath || null,
        repoUrl: repoUrl,
      };
      setRepoInfo(newRepoInfo);
    } else {
      setRepoInfo(null);
    }
  };

  // Provider-based model selection state
  const [provider, setProvider] = useState<string>('');
  const [model, setModel] = useState<string>('');
  const [isCustomModel, setIsCustomModel] = useState<boolean>(false);
  const [customModel, setCustomModel] = useState<string>('');

  // Wiki type state - default to comprehensive view
  const [isComprehensiveView, setIsComprehensiveView] = useState<boolean>(true);

  const [excludedDirs, setExcludedDirs] = useState('');
  const [excludedFiles, setExcludedFiles] = useState('');
  const [includedDirs, setIncludedDirs] = useState('');
  const [includedFiles, setIncludedFiles] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState<'github' | 'gitlab' | 'bitbucket'>('github');
  const [accessToken, setAccessToken] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState<string>(language);

  // Authentication state
  const [authRequired, setAuthRequired] = useState<boolean>(false);
  const [authCode, setAuthCode] = useState<string>('');
  const [isAuthLoading, setIsAuthLoading] = useState<boolean>(true);

  // Home page state for two-column layout
  const [selectedRepository, setSelectedRepository] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [repoInfo, setRepoInfo] = useState<RepoInfo | null>(null);
  const [mobileActiveTab, setMobileActiveTab] = useState<'projects' | 'chat'>('projects');

  // Sync the language context with the selectedLanguage state
  useEffect(() => {
    setLanguage(selectedLanguage);
  }, [selectedLanguage, setLanguage]);

  // Fetch authentication status on component mount
  useEffect(() => {
    const fetchAuthStatus = async () => {
      try {
        setIsAuthLoading(true);
        const response = await fetch('/api/auth/status');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setAuthRequired(data.auth_required);
      } catch (err) {
        console.error("Failed to fetch auth status:", err);
        // Assuming auth is required if fetch fails to avoid blocking UI for safety
        setAuthRequired(true);
      } finally {
        setIsAuthLoading(false);
      }
    };

    fetchAuthStatus();
  }, []);

  // Parse repository URL/input and extract owner and repo
  const parseRepositoryInput = (input: string): {
    owner: string,
    repo: string,
    type: string,
    fullPath?: string,
    localPath?: string
  } | null => {
    input = input.trim();

    let owner = '', repo = '', type = 'github', fullPath;
    let localPath: string | undefined;

    // Handle Windows absolute paths (e.g., C:\path\to\folder)
    const windowsPathRegex = /^[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*$/;
    const customGitRegex = /^(?:https?:\/\/)?([^\/]+)\/(.+?)\/([^\/]+)(?:\.git)?\/?$/;

    if (windowsPathRegex.test(input)) {
      type = 'local';
      localPath = input;
      repo = input.split('\\').pop() || 'local-repo';
      owner = 'local';
    }
    // Handle Unix/Linux absolute paths (e.g., /path/to/folder)
    else if (input.startsWith('/')) {
      type = 'local';
      localPath = input;
      repo = input.split('/').filter(Boolean).pop() || 'local-repo';
      owner = 'local';
    }
    else if (customGitRegex.test(input)) {
      // Detect repository type based on domain
      const domain = extractUrlDomain(input);
      if (domain?.includes('github.com')) {
        type = 'github';
      } else if (domain?.includes('gitlab.com') || domain?.includes('gitlab.')) {
        type = 'gitlab';
      } else if (domain?.includes('bitbucket.org') || domain?.includes('bitbucket.')) {
        type = 'bitbucket';
      } else {
        type = 'web'; // fallback for other git hosting services
      }

      fullPath = extractUrlPath(input)?.replace(/\.git$/, '');
      const parts = fullPath?.split('/') ?? [];
      if (parts.length >= 2) {
        repo = parts[parts.length - 1] || '';
        owner = parts[parts.length - 2] || '';
      }
    }
    // Unsupported URL formats
    else {
      console.error('Unsupported URL format:', input);
      return null;
    }

    if (!owner || !repo) {
      return null;
    }

    // Clean values
    owner = owner.trim();
    repo = repo.trim();

    // Remove .git suffix if present
    if (repo.endsWith('.git')) {
      repo = repo.slice(0, -4);
    }

    return { owner, repo, type, fullPath, localPath };
  };

  // State for configuration modal
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Parse repository input to validate
    const parsedRepo = parseRepositoryInput(repositoryInput);

    if (!parsedRepo) {
      setError('Invalid repository format. Use "owner/repo", GitHub/GitLab/BitBucket URL, or a local folder path like "/path/to/folder" or "C:\\path\\to\\folder".');
      return;
    }

    // If valid, open the configuration modal
    setError(null);
    setIsConfigModalOpen(true);
  };

  const validateAuthCode = async () => {
    try {
      if(authRequired) {
        if(!authCode) {
          return false;
        }
        const response = await fetch('/api/auth/validate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({'code': authCode})
        });
        if (!response.ok) {
          return false;
        }
        const data = await response.json();
        return data.success || false;
      }
    } catch {
      return false;
    }
    return true;
  };

  const handleGenerateWiki = async () => {

    // Check authorization code
    const validation = await validateAuthCode();
    if(!validation) {
      setError(`Failed to validate the authorization code`);
      console.error(`Failed to validate the authorization code`);
      setIsConfigModalOpen(false);
      return;
    }

    // Prevent multiple submissions
    if (isSubmitting) {
      console.log('Form submission already in progress, ignoring duplicate click');
      return;
    }

    try {
      const currentRepoUrl = repositoryInput.trim();
      if (currentRepoUrl) {
        const existingConfigs = JSON.parse(localStorage.getItem(REPO_CONFIG_CACHE_KEY) || '{}');
        const configToSave = {
          selectedLanguage,
          isComprehensiveView,
          provider,
          model,
          isCustomModel,
          customModel,
          selectedPlatform,
          excludedDirs,
          excludedFiles,
          includedDirs,
          includedFiles,
        };
        existingConfigs[currentRepoUrl] = configToSave;
        localStorage.setItem(REPO_CONFIG_CACHE_KEY, JSON.stringify(existingConfigs));
      }
    } catch (error) {
      console.error('Error saving config to localStorage:', error);
    }

    setIsSubmitting(true);

    // Parse repository input
    const parsedRepo = parseRepositoryInput(repositoryInput);

    if (!parsedRepo) {
      setError('Invalid repository format. Use "owner/repo", GitHub/GitLab/BitBucket URL, or a local folder path like "/path/to/folder" or "C:\\path\\to\\folder".');
      setIsSubmitting(false);
      return;
    }

    const { owner, repo, type, localPath } = parsedRepo;

    // Store tokens in query params if they exist
    const params = new URLSearchParams();
    if (accessToken) {
      params.append('token', accessToken);
    }
    // Always include the type parameter
    params.append('type', (type == 'local' ? type : selectedPlatform) || 'github');
    // Add local path if it exists
    if (localPath) {
      params.append('local_path', encodeURIComponent(localPath));
    } else {
      params.append('repo_url', encodeURIComponent(repositoryInput));
    }
    // Add model parameters
    params.append('provider', provider);
    params.append('model', model);
    if (isCustomModel && customModel) {
      params.append('custom_model', customModel);
    }
    // Add file filters configuration
    if (excludedDirs) {
      params.append('excluded_dirs', excludedDirs);
    }
    if (excludedFiles) {
      params.append('excluded_files', excludedFiles);
    }
    if (includedDirs) {
      params.append('included_dirs', includedDirs);
    }
    if (includedFiles) {
      params.append('included_files', includedFiles);
    }

    // Add language parameter
    params.append('language', selectedLanguage);

    // Add comprehensive parameter
    params.append('comprehensive', isComprehensiveView.toString());

    const queryString = params.toString() ? `?${params.toString()}` : '';

    // Navigate to the dynamic route
    router.push(`/${owner}/${repo}${queryString}`);

    // The isSubmitting state will be reset when the component unmounts during navigation
  };

  return (
    <div className="h-screen bg-[var(--background)] flex flex-col overflow-hidden">
      {/* Simplified Header */}
      <header className="border-b border-[var(--border-color)] bg-[var(--card-bg)] flex-shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Left: Logo and Brand */}
            <div className="flex items-center">
              <div className="bg-[var(--accent-primary)] p-2 rounded-lg mr-3">
                <FaWikipediaW className="text-xl text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-[var(--accent-primary)]">{t('common.appName')}</h1>
                <p className="text-xs text-[var(--muted)]">{t('common.tagline')}</p>
              </div>
            </div>

            {/* Center: Quick Repository Input (Desktop only) */}
            <div className="hidden lg:block flex-1 max-w-xl mx-8">
              <form onSubmit={handleFormSubmit} className="flex gap-2">
                <div className="relative flex-1">
                  <RepositorySelector
                    projects={projects}
                    selectedRepository={repositoryInput}
                    onRepositorySelect={handleRepositorySelect}
                    placeholder={t('form.repoPlaceholder') || "Quick process: github.com/owner/repo"}
                  />
                  {error && (
                    <div className="absolute top-full left-0 text-[var(--highlight)] text-xs mt-1 z-10">
                      {error}
                    </div>
                  )}
                </div>
                <button
                  type="submit"
                  className="px-4 py-2 bg-[var(--accent-primary)] text-white rounded-lg hover:bg-[var(--accent-primary)]/90 transition-colors disabled:opacity-50 text-sm"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? t('common.processing') : 'Process'}
                </button>
              </form>
            </div>

            {/* Right: Settings and Theme */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => setIsConfigModalOpen(true)}
                className="text-[var(--muted)] hover:text-[var(--foreground)] transition-colors p-2 rounded-lg hover:bg-[var(--background)]"
                title="Settings"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
              <Link href="/wiki/projects"
                className="text-[var(--muted)] hover:text-[var(--accent-primary)] text-sm font-medium transition-colors">
                Wiki Projects
              </Link>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex overflow-hidden min-h-0">
        {/* Desktop: Sidebar + Main Content */}
        <div className="hidden md:flex w-full h-full">
          {/* Left Sidebar - Projects Panel */}
          <div className="w-96 border-r border-[var(--border-color)] bg-[var(--card-bg)] flex flex-col h-full">
            <ExistingProjectsPanel
              projects={projects}
              onRepositorySelect={handleAskRepositorySelect}
              selectedRepository={selectedRepository}
              isLoading={projectsLoading}
              searchQuery={searchQuery}
              onSearchQueryChange={setSearchQuery}
              viewMode={viewMode}
              onViewModeChange={setViewMode}
            />
          </div>

          {/* Main Content Area - Chat */}
          <div className="flex-1 flex flex-col min-w-0 h-full">
            <ChatPanel
              repoInfo={repoInfo}
              projects={projects}
              provider={provider}
              model={model}
              isCustomModel={isCustomModel}
              customModel={customModel}
              language={selectedLanguage}
            />
          </div>
        </div>

        {/* Mobile: Tab Layout */}
        <div className="md:hidden flex flex-col w-full">
          {/* Mobile Header with Repository Input */}
          <div className="p-4 bg-[var(--card-bg)] border-b border-[var(--border-color)]">
            <form onSubmit={handleFormSubmit} className="flex gap-2">
              <div className="relative flex-1">
                <RepositorySelector
                  projects={projects}
                  selectedRepository={repositoryInput}
                  onRepositorySelect={handleRepositorySelect}
                  placeholder={t('form.repoPlaceholder') || "Enter repository URL..."}
                />
                {error && (
                  <div className="text-[var(--highlight)] text-xs mt-1">
                    {error}
                  </div>
                )}
              </div>
              <button
                type="submit"
                className="px-4 py-2 bg-[var(--accent-primary)] text-white rounded-lg disabled:opacity-50 text-sm"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Processing...' : 'Process'}
              </button>
            </form>
          </div>

          {/* Mobile Tab Navigation */}
          <div className="flex bg-[var(--card-bg)] border-b border-[var(--border-color)]">
            <button
              onClick={() => setMobileActiveTab('projects')}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
                mobileActiveTab === 'projects'
                  ? 'text-[var(--accent-primary)] bg-[var(--accent-primary)]/10 border-b-2 border-[var(--accent-primary)]'
                  : 'text-[var(--muted)] hover:text-[var(--foreground)]'
              }`}
            >
              Projects ({projects.length})
            </button>
            <button
              onClick={() => setMobileActiveTab('chat')}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
                mobileActiveTab === 'chat'
                  ? 'text-[var(--accent-primary)] bg-[var(--accent-primary)]/10 border-b-2 border-[var(--accent-primary)]'
                  : 'text-[var(--muted)] hover:text-[var(--foreground)]'
              }`}
            >
              Ask {repoInfo ? `(${repoInfo.owner}/${repoInfo.repo})` : ''}
            </button>
          </div>

          {/* Mobile Content */}
          <div className="flex-1 overflow-hidden">
            {mobileActiveTab === 'projects' ? (
              <ExistingProjectsPanel
                projects={projects}
                onRepositorySelect={(repo) => {
                  handleAskRepositorySelect(repo);
                  setMobileActiveTab('chat'); // Auto-switch to chat when repository selected
                }}
                selectedRepository={selectedRepository}
                isLoading={projectsLoading}
                searchQuery={searchQuery}
                onSearchQueryChange={setSearchQuery}
                viewMode={viewMode}
                onViewModeChange={setViewMode}
              />
            ) : (
              <ChatPanel
                repoInfo={repoInfo}
                projects={projects}
                provider={provider}
                model={model}
                isCustomModel={isCustomModel}
                customModel={customModel}
                language={selectedLanguage}
              />
            )}
          </div>
        </div>

        {/* Fallback welcome content for empty state */}
        {!projectsLoading && projects.length === 0 && (
          <div className="p-8 bg-[var(--card-bg)] rounded-lg shadow-custom card-japanese m-6">
            {/* Header section */}
            <div className="flex flex-col items-center w-full mb-8">
              <div className="flex flex-col items-center mb-6 gap-4">
                <div className="relative">
                  <div className="absolute -inset-1 bg-[var(--accent-primary)]/20 rounded-full blur-md"></div>
                  <FaWikipediaW className="text-5xl text-[var(--accent-primary)] relative z-10" />
                </div>
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-[var(--foreground)] font-serif mb-1">{t('home.welcome')}</h2>
                  <p className="text-[var(--accent-primary)] text-sm">{t('home.welcomeTagline')}</p>
                </div>
              </div>

              <p className="text-[var(--foreground)] text-center mb-8 text-lg leading-relaxed">
                {t('home.description')}
              </p>
            </div>

            {/* Quick Start section */}
            <div className="w-full mb-10 bg-[var(--accent-primary)]/5 border border-[var(--accent-primary)]/20 rounded-lg p-5">
              <h3 className="text-sm font-semibold text-[var(--accent-primary)] mb-3 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {t('home.quickStart')}
              </h3>
              <p className="text-sm text-[var(--foreground)] mb-3">{t('home.enterRepoUrl')}</p>
              <div className="text-xs text-[var(--muted)] space-y-2">
                <div className="bg-[var(--background)]/70 p-3 rounded border border-[var(--border-color)] font-mono">
                  https://github.com/AsyncFuncAI/deepwiki-open
                </div>
                <p className="text-center text-[var(--muted)]">
                  Process a repository first to use the Ask feature
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Configuration Modal */}
      <ConfigurationModal
        isOpen={isConfigModalOpen}
        onClose={() => setIsConfigModalOpen(false)}
        repositoryInput={repositoryInput}
        selectedLanguage={selectedLanguage}
        setSelectedLanguage={setSelectedLanguage}
        supportedLanguages={supportedLanguages}
        isComprehensiveView={isComprehensiveView}
        setIsComprehensiveView={setIsComprehensiveView}
        provider={provider}
        setProvider={setProvider}
        model={model}
        setModel={setModel}
        isCustomModel={isCustomModel}
        setIsCustomModel={setIsCustomModel}
        customModel={customModel}
        setCustomModel={setCustomModel}
        selectedPlatform={selectedPlatform}
        setSelectedPlatform={setSelectedPlatform}
        accessToken={accessToken}
        setAccessToken={setAccessToken}
        excludedDirs={excludedDirs}
        setExcludedDirs={setExcludedDirs}
        excludedFiles={excludedFiles}
        setExcludedFiles={setExcludedFiles}
        includedDirs={includedDirs}
        setIncludedDirs={setIncludedDirs}
        includedFiles={includedFiles}
        setIncludedFiles={setIncludedFiles}
        onSubmit={handleGenerateWiki}
        isSubmitting={isSubmitting}
        authRequired={authRequired}
        authCode={authCode}
        setAuthCode={setAuthCode}
        isAuthLoading={isAuthLoading}
      />

      {/* Minimal Footer */}
      <footer className="border-t border-[var(--border-color)] bg-[var(--card-bg)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <p className="text-[var(--muted)] text-sm">{t('footer.copyright')}</p>
            <div className="flex items-center space-x-4">
              <a href="https://github.com/AsyncFuncAI/deepwiki-open" target="_blank" rel="noopener noreferrer"
                className="text-[var(--muted)] hover:text-[var(--accent-primary)] transition-colors">
                <FaGithub className="text-lg" />
              </a>
              <a href="https://buymeacoffee.com/sheing" target="_blank" rel="noopener noreferrer"
                className="text-[var(--muted)] hover:text-[var(--accent-primary)] transition-colors">
                <FaCoffee className="text-lg" />
              </a>
              <a href="https://x.com/sashimikun_void" target="_blank" rel="noopener noreferrer"
                className="text-[var(--muted)] hover:text-[var(--accent-primary)] transition-colors">
                <FaTwitter className="text-lg" />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}