'use client';

import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import { FaComments, FaTimes, FaExclamationTriangle } from 'react-icons/fa';
import Link from 'next/link';

// Components
import Ask from '@/components/Ask';
import ThemeToggle from '@/components/theme-toggle';
// import ModelSelectionModal from '@/components/ModelSelectionModal';
import RepositoryHeader from './RepositoryHeader';
import WikiViewer from './WikiViewer';
import WikiSidebar from './WikiSidebar';

// Hooks and utilities
import { useLanguage } from '@/contexts/LanguageContext';
import { useProcessedProjects } from '@/hooks/useProcessedProjects';
import { useWikiGeneration } from '@/hooks/useWikiGeneration';
import { useModelConfiguration } from '@/hooks/useModelConfiguration';
import { RepoInfo } from '@/types/repoinfo';

// Styles
const wikiStyles = `
  .prose code {
    @apply bg-[var(--background)]/70 px-1.5 py-0.5 rounded font-mono text-xs border border-[var(--border-color)];
  }
  .prose pre {
    @apply bg-[var(--background)]/80 text-[var(--foreground)] rounded-md p-4 overflow-x-auto border border-[var(--border-color)] shadow-sm;
  }
  .prose h1, .prose h2, .prose h3, .prose h4 {
    @apply font-serif text-[var(--foreground)];
  }
  .prose p {
    @apply text-[var(--foreground)] leading-relaxed;
  }
  .prose a {
    @apply text-[var(--accent-primary)] hover:text-[var(--highlight)] transition-colors no-underline border-b border-[var(--border-color)] hover:border-[var(--accent-primary)];
  }
`;

const RepoPageOrchestrator: React.FC = () => {
  // Route parameters
  const params = useParams();
  const searchParams = useSearchParams();
  const { messages } = useLanguage();
  const { projects } = useProcessedProjects();

  // Extract route data
  const owner = params.owner as string;
  const repo = params.repo as string;
  const token = searchParams.get('token') || '';
  const localPath = searchParams.get('local_path') ? decodeURIComponent(searchParams.get('local_path') || '') : undefined;
  const repoUrl = searchParams.get('repo_url') ? decodeURIComponent(searchParams.get('repo_url') || '') : undefined;
  const language = searchParams.get('language') || 'en';
  const repoType = repoUrl?.includes('bitbucket.org') ? 'bitbucket' :
    repoUrl?.includes('gitlab.com') ? 'gitlab' :
    repoUrl?.includes('github.com') ? 'github' : searchParams.get('type') || 'github';

  // Create repo info object
  const repoInfo = useMemo<RepoInfo>(() => ({
    owner,
    repo,
    type: repoType,
    token: token || null,
    localPath: localPath || null,
    repoUrl: repoUrl || null
  }), [owner, repo, repoType, token, localPath, repoUrl]);

  // Local state
  const [defaultBranch] = useState<string>('main');
  const [repositoryFiles] = useState<string[]>([]);
  const [isAskModalOpen, setIsAskModalOpen] = useState(false);
  // const [isModelSelectionModalOpen, setIsModelSelectionModalOpen] = useState(false);
  const askComponentRef = useRef<{ clearConversation: () => void } | null>(null);

  // Model configuration
  const modelConfig = useModelConfiguration({
    provider: searchParams.get('provider') || '',
    model: searchParams.get('model') || '',
    isCustomModel: searchParams.get('is_custom_model') === 'true',
    customModel: searchParams.get('custom_model') || ''
  });

  // Wiki generation
  const wikiGeneration = useWikiGeneration({
    repoInfo,
    defaultBranch,
    repositoryFiles,
    language,
    provider: searchParams.get('provider') || 'openai',
    model: searchParams.get('model') || 'gpt-4.1-mini',
    isCustomModel: searchParams.get('custom_model') ? true : false,
    customModel: searchParams.get('custom_model') || '',
    excludedDirs: searchParams.get('excluded_dirs') || '',
    excludedFiles: searchParams.get('excluded_files') || '',
    includedDirs: searchParams.get('included_dirs') || '',
    includedFiles: searchParams.get('included_files') || '',
    isComprehensiveView: searchParams.get('comprehensive') !== 'false'
  });

  // Handle page selection
  const handlePageSelect = (pageId: string) => {
    if (wikiGeneration.currentPageId !== pageId) {
      wikiGeneration.setCurrentPageId(pageId);
    }
  };

  // Handle wiki refresh using the hook's refreshWiki function
  const handleRefresh = useCallback(async () => {
    await wikiGeneration.refreshWiki();
  }, [wikiGeneration]);

  // Close modal on escape key
  useEffect(() => {
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsAskModalOpen(false);
      }
    };

    if (isAskModalOpen) {
      window.addEventListener('keydown', handleEsc);
    }

    return () => {
      window.removeEventListener('keydown', handleEsc);
    };
  }, [isAskModalOpen]);

  // Scroll to top when page changes
  useEffect(() => {
    const wikiContent = document.getElementById('wiki-content');
    if (wikiContent) {
      wikiContent.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [wikiGeneration.currentPageId]);

  return (
    <div className="h-screen paper-texture flex flex-col">
      <style>{wikiStyles}</style>
      
      <RepositoryHeader messages={messages} />
      
      <main className="flex-1 w-full overflow-y-auto">
        {wikiGeneration.isLoading ? (
          <div className="flex flex-col items-center justify-center p-8 bg-[var(--card-bg)] rounded-lg shadow-custom card-japanese">
            <div className="relative mb-6">
              <div className="absolute -inset-4 bg-[var(--accent-primary)]/10 rounded-full blur-md animate-pulse"></div>
              <div className="relative flex items-center justify-center">
                <div className="w-3 h-3 bg-[var(--accent-primary)]/70 rounded-full animate-pulse"></div>
                <div className="w-3 h-3 bg-[var(--accent-primary)]/70 rounded-full animate-pulse delay-75 mx-2"></div>
                <div className="w-3 h-3 bg-[var(--accent-primary)]/70 rounded-full animate-pulse delay-150"></div>
              </div>
            </div>
            <p className="text-[var(--foreground)] text-center mb-3 font-serif">
              {wikiGeneration.loadingMessage || messages.common?.loading || 'Loading...'}
            </p>
          </div>
        ) : wikiGeneration.error ? (
          <div className="bg-[var(--highlight)]/5 border border-[var(--highlight)]/30 rounded-lg p-5 mb-4 shadow-sm">
            <div className="flex items-center text-[var(--highlight)] mb-3">
              <FaExclamationTriangle className="mr-2" />
              <span className="font-bold font-serif">{messages.repoPage?.errorTitle || messages.common?.error || 'Error'}</span>
            </div>
            <p className="text-[var(--foreground)] text-sm mb-3">{wikiGeneration.error}</p>
            <div className="mt-5">
              <Link href="/" className="btn-japanese px-5 py-2 inline-flex items-center gap-1.5">
                {messages.repoPage?.backToHome || 'Back to Home'}
              </Link>
            </div>
          </div>
        ) : wikiGeneration.wikiStructure ? (
          <div className="h-full overflow-y-auto flex flex-col lg:flex-row gap-4 w-full overflow-hidden bg-[var(--card-bg)] rounded-lg shadow-custom card-japanese">
            <WikiSidebar
              wikiStructure={wikiGeneration.wikiStructure}
              currentPageId={wikiGeneration.currentPageId}
              repoInfo={repoInfo}
              isComprehensiveView={true}
              onPageSelect={handlePageSelect}
              onRefresh={handleRefresh}
              onExport={wikiGeneration.exportWiki}
              isLoading={wikiGeneration.isLoading}
              messages={messages}
            />
            
            <div className="flex-1 overflow-y-auto" id="wiki-content">
              <WikiViewer
                wikiStructure={wikiGeneration.wikiStructure}
                currentPageId={wikiGeneration.currentPageId}
                generatedPages={wikiGeneration.generatedPages}
                repoInfo={repoInfo}
                defaultBranch={defaultBranch}
                onPageSelect={handlePageSelect}
                messages={messages}
              />
            </div>
          </div>
        ) : null}
      </main>

      <footer className="w-full mt-8 flex flex-col gap-4 px-4">
        <div className="flex justify-between items-center gap-4 text-center text-[var(--muted)] text-sm h-fit w-full bg-[var(--card-bg)] rounded-lg p-3 shadow-sm border border-[var(--border-color)]">
          <p className="flex-1 font-serif">
            {messages.footer?.copyright || 'DeepWiki - Generate Wiki from GitHub/Gitlab/Bitbucket repositories'}
          </p>
          <ThemeToggle />
        </div>
      </footer>

      {/* Floating Chat Button */}
      {!wikiGeneration.isLoading && wikiGeneration.wikiStructure && (
        <button
          onClick={() => setIsAskModalOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-[var(--accent-primary)] text-white shadow-lg flex items-center justify-center hover:bg-[var(--accent-primary)]/90 transition-all z-50"
          aria-label={messages.ask?.title || 'Ask about this repository'}
        >
          <FaComments className="text-xl" />
        </button>
      )}

      {/* Ask Modal */}
      <div className={`fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 transition-opacity duration-300 ${isAskModalOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
        <div className="bg-[var(--card-bg)] rounded-lg shadow-xl w-full max-w-3xl max-h-[80vh] flex flex-col">
          <div className="flex items-center justify-end p-3 absolute top-0 right-0 z-10">
            <button
              onClick={() => setIsAskModalOpen(false)}
              className="text-[var(--muted)] hover:text-[var(--foreground)] transition-colors bg-[var(--card-bg)]/80 rounded-full p-2"
              aria-label="Close"
            >
              <FaTimes className="text-xl" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <Ask
              repoInfo={repoInfo}
              projects={projects}
              provider={modelConfig.config.selectedProvider}
              model={modelConfig.config.selectedModel}
              isCustomModel={modelConfig.config.isCustomModel}
              customModel={modelConfig.config.customModel}
              language={language}
              onRef={(ref: { clearConversation: () => void }) => (askComponentRef.current = ref)}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default RepoPageOrchestrator;
