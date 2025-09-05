'use client';

import React from 'react';
import Ask from '@/components/Ask';
import { ChatPanelProps } from '@/types/home-page-ask';

export default function ChatPanel({
  repoInfo,
  projects,
  provider,
  model,
  isCustomModel,
  customModel,
  language,
  className = '',
}: ChatPanelProps) {
  // If no repository is selected, show placeholder
  if (!repoInfo) {
    return (
      <div className={`h-full flex flex-col bg-[var(--card-bg)] ${className}`}>
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center max-w-md">
            <div className="text-6xl mb-6 text-[var(--muted)]">💬</div>
            <h3 className="text-xl font-semibold text-[var(--foreground)] mb-3">
              Start a Conversation
            </h3>
            <p className="text-[var(--muted)] leading-relaxed">
              Select a repository from the sidebar to start asking questions about your codebase. 
              I can help you understand code structure, find specific implementations, and explain complex logic.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`h-full flex flex-col bg-[var(--card-bg)] ${className}`}>
      {/* Minimal Header */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--border-color)] flex-shrink-0">
        <div>
          <h3 className="text-lg font-semibold text-[var(--foreground)]">
            Chat
          </h3>
          <p className="text-sm text-[var(--muted)]">
            {repoInfo.owner}/{repoInfo.repo}
          </p>
        </div>
      </div>

      {/* Ask component container - Full remaining height */}
      <div className="flex-1 min-h-0">
        <Ask
          repoInfo={repoInfo}
          projects={projects}
          provider={provider}
          model={model}
          isCustomModel={isCustomModel}
          customModel={customModel}
          language={language}
        />
      </div>
    </div>
  );
}
