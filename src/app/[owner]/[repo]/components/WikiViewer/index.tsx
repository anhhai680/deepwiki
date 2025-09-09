'use client';

import React from 'react';
import { FaBookOpen } from 'react-icons/fa';
import Markdown from '@/components/Markdown';
import { WikiPage, WikiStructure } from '@/types/shared';
import { RepoInfo } from '@/types/repoinfo';

interface WikiViewerProps {
  wikiStructure: WikiStructure;
  currentPageId?: string;
  generatedPages: Record<string, WikiPage>;
  repoInfo: RepoInfo;
  defaultBranch: string;
  onPageSelect: (pageId: string) => void;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  messages: any;
}

const WikiViewer: React.FC<WikiViewerProps> = ({
  wikiStructure,
  currentPageId,
  generatedPages,
  repoInfo,
  defaultBranch,
  onPageSelect,
  messages
}) => {
  if (!currentPageId || !generatedPages[currentPageId]) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-[var(--muted)] h-full">
        <div className="relative mb-4">
          <div className="absolute -inset-2 bg-[var(--accent-primary)]/5 rounded-full blur-md"></div>
          <FaBookOpen className="text-4xl relative z-10" />
        </div>
        <p className="font-serif">
          {messages.repoPage?.selectPagePrompt || 'Select a page from the navigation to view its content'}
        </p>
      </div>
    );
  }

  const currentPage = generatedPages[currentPageId];

  return (
    <div className="p-6">
      <div className="prose prose-sm md:prose-base lg:prose-lg max-w-none">
        <Markdown
          content={currentPage.content}
          repoInfo={{
            type: repoInfo.type,
            repoUrl: repoInfo.repoUrl || undefined,
            defaultBranch: defaultBranch,
            owner: repoInfo.owner,
            repo: repoInfo.repo
          }}
        />
      </div>

      {/* Related Pages */}
      {currentPage.relatedPages.length > 0 && (
        <div className="mt-8 pt-4 border-t border-[var(--border-color)]">
          <h4 className="text-sm font-semibold text-[var(--muted)] mb-3">
            {messages.repoPage?.relatedPages || 'Related Pages:'}
          </h4>
          <div className="flex flex-wrap gap-2">
            {currentPage.relatedPages.map(relatedId => {
              const relatedPage = wikiStructure.pages.find(p => p.id === relatedId);
              return relatedPage ? (
                <button
                  key={relatedId}
                  className="bg-[var(--accent-primary)]/10 hover:bg-[var(--accent-primary)]/20 text-xs text-[var(--accent-primary)] px-3 py-1.5 rounded-md transition-colors truncate max-w-full border border-[var(--accent-primary)]/20"
                  onClick={() => onPageSelect(relatedId)}
                >
                  {relatedPage.title}
                </button>
              ) : null;
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default WikiViewer;
