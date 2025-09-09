'use client';

import React from 'react';
import { FaFolder, FaGithub, FaGitlab, FaBitbucket, FaSync, FaDownload } from 'react-icons/fa';
import WikiTreeView from '@/components/WikiTreeView';
import { WikiStructure } from '@/types/shared';
import { RepoInfo } from '@/types/repoinfo';

interface WikiSidebarProps {
  wikiStructure: WikiStructure;
  currentPageId?: string;
  repoInfo: RepoInfo;
  isComprehensiveView: boolean;
  onPageSelect: (pageId: string) => void;
  onRefresh?: () => void;
  onExport?: (format: 'markdown' | 'json') => void;
  isLoading: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  messages: any;
}

const WikiSidebar: React.FC<WikiSidebarProps> = ({
  wikiStructure,
  currentPageId,
  repoInfo,
  isComprehensiveView,
  onPageSelect,
  onRefresh,
  onExport,
  isLoading,
  messages
}) => {
  const getRepoIcon = () => {
    switch (repoInfo.type) {
      case 'github':
        return <FaGithub className="mr-2" />;
      case 'gitlab':
        return <FaGitlab className="mr-2" />;
      case 'bitbucket':
        return <FaBitbucket className="mr-2" />;
      case 'local':
        return <FaFolder className="mr-2" />;
      default:
        return <FaGithub className="mr-2" />;
    }
  };

  return (
    <div className="h-full w-full lg:w-[280px] xl:w-[320px] flex-shrink-0 bg-[var(--background)]/50 rounded-lg rounded-r-none p-5 border-b lg:border-b-0 lg:border-r border-[var(--border-color)] overflow-y-auto">
      {/* Wiki Title and Description */}
      <h3 className="text-lg font-bold text-[var(--foreground)] mb-3 font-serif">
        {wikiStructure.title}
      </h3>
      <p className="text-[var(--muted)] text-sm mb-5 leading-relaxed">
        {wikiStructure.description}
      </p>

      {/* Repository Info */}
      <div className="text-xs text-[var(--muted)] mb-5 flex items-center">
        {repoInfo.type === 'local' ? (
          <div className="flex items-center">
            <FaFolder className="mr-2" />
            <span className="break-all">{repoInfo.localPath}</span>
          </div>
        ) : (
          <>
            {getRepoIcon()}
            <a
              href={repoInfo.repoUrl ?? ''}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-[var(--accent-primary)] transition-colors border-b border-[var(--border-color)] hover:border-[var(--accent-primary)]"
            >
              {repoInfo.owner}/{repoInfo.repo}
            </a>
          </>
        )}
      </div>

      {/* Wiki Type Indicator */}
      <div className="mb-3 flex items-center text-xs text-[var(--muted)]">
        <span className="mr-2">Wiki Type:</span>
        <span className={`px-2 py-0.5 rounded-full ${
          isComprehensiveView
            ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30'
            : 'bg-[var(--muted)]/10 text-[var(--muted)] border border-[var(--border-color)]'
        }`}>
          {isComprehensiveView ? 'Comprehensive' : 'Concise'}
        </span>
      </div>

      {/* Action Buttons */}
      <div className="mb-5 flex items-center gap-2">
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="flex-1 text-xs px-2 py-1.5 bg-[var(--background)] border border-[var(--border-color)] text-[var(--foreground)] rounded-md hover:bg-[var(--background)]/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-1"
            title={messages.repoPage?.refreshTooltip || 'Regenerate wiki with current settings'}
          >
            <FaSync className={`text-xs ${isLoading ? 'animate-spin' : ''}`} />
            {messages.repoPage?.refresh || 'Refresh'}
          </button>
        )}
        
        {onExport && (
          <div className="relative group">
            <button
              className="flex-1 text-xs px-2 py-1.5 bg-[var(--background)] border border-[var(--border-color)] text-[var(--foreground)] rounded-md hover:bg-[var(--background)]/80 transition-colors flex items-center justify-center gap-1"
              disabled={isLoading}
            >
              <FaDownload className="text-xs" />
              {messages.repoPage?.export || 'Export'}
            </button>
            
            {/* Export Options Dropdown */}
            <div className="absolute top-full left-0 mt-1 w-full bg-[var(--card-bg)] border border-[var(--border-color)] rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
              <button
                onClick={() => onExport('markdown')}
                className="w-full text-left px-3 py-2 text-xs text-[var(--foreground)] hover:bg-[var(--background)]/50 transition-colors"
                disabled={isLoading}
              >
                Export as Markdown
              </button>
              <button
                onClick={() => onExport('json')}
                className="w-full text-left px-3 py-2 text-xs text-[var(--foreground)] hover:bg-[var(--background)]/50 transition-colors border-t border-[var(--border-color)]"
                disabled={isLoading}
              >
                Export as JSON
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Wiki Navigation Tree */}
      <WikiTreeView
        wikiStructure={wikiStructure}
        currentPageId={currentPageId}
        onPageSelect={onPageSelect}
      />
    </div>
  );
};

export default WikiSidebar;
