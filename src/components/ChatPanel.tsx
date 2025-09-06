'use client';

import React from 'react';
import Ask from '@/components/Ask';
import { ChatPanelProps } from '@/types/home-page-ask';
import { RepoInfo } from '@/types/repoinfo';

export default function ChatPanel({
  repoInfo,
  repoInfos = [],
  projects,
  provider,
  model,
  isCustomModel,
  customModel,
  language,
  className = '',
  isMultiRepositoryMode = false,
  onMultiRepositoryModeChange,
}: ChatPanelProps) {
  // Determine if we have any repositories selected
  const hasRepositories = isMultiRepositoryMode 
    ? repoInfos.length > 0 
    : repoInfo !== null;

  // If no repository is selected, show placeholder
  if (!hasRepositories) {
    return (
      <div className={`h-full flex flex-col bg-[var(--card-bg)] ${className}`}>
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center max-w-md">
            <div className="text-6xl mb-6 text-[var(--muted)]">💬</div>
            <h3 className="text-xl font-semibold text-[var(--foreground)] mb-3">
              Start a Conversation
            </h3>
            <p className="text-[var(--muted)] leading-relaxed">
              {isMultiRepositoryMode 
                ? 'Select repositories from the sidebar using multi-select mode to start asking questions about multiple codebases simultaneously.'
                : 'Select a repository from the sidebar to start asking questions about your codebase. I can help you understand code structure, find specific implementations, and explain complex logic.'
              }
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`h-full flex flex-col bg-[var(--card-bg)] ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--border-color)] flex-shrink-0">
        <div>
          <h3 className="text-lg font-semibold text-[var(--foreground)]">
            Chat
          </h3>
          <p className="text-sm text-[var(--muted)]">
            {isMultiRepositoryMode 
              ? `${repoInfos.length} repositories selected`
              : `${repoInfo?.owner}/${repoInfo?.repo}`
            }
          </p>
        </div>
      </div>

      {/* Ask component container - Full remaining height */}
      <div className="flex-1 min-h-0">
        <Ask
          repoInfo={isMultiRepositoryMode ? repoInfos : (repoInfo as RepoInfo)}
          projects={projects}
          provider={provider}
          model={model}
          isCustomModel={isCustomModel}
          customModel={customModel}
          language={language}
          onMultiRepositoryModeChange={onMultiRepositoryModeChange}
        />
      </div>
    </div>
  );
}
