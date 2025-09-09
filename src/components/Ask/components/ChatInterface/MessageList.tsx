'use client';

import React, { useEffect, useRef } from 'react';
import Markdown from '@/components/Markdown';

interface MessageListProps {
  response: string;
  isLoading: boolean;
  isEmpty?: boolean;
}

const EmptyState: React.FC = () => (
  <div className="flex-1 flex items-center justify-center p-8">
    <div className="text-center max-w-md">
      <div className="text-4xl mb-4 text-[var(--muted)]">💭</div>
      <h3 className="text-lg font-semibold text-[var(--foreground)] mb-2">
        Ask anything about your codebase
      </h3>
      <p className="text-[var(--muted)] text-sm">
        Start a conversation by typing your question below. I can help you understand code structure, find implementations, and explain complex logic.
      </p>
    </div>
  </div>
);

const LoadingIndicator: React.FC<{ researchIteration?: number }> = ({ 
  researchIteration = 0 
}) => (
  <div className="p-4 border-t border-[var(--border-color)]">
    <div className="flex items-center space-x-3 text-[var(--muted)]">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-[var(--accent-primary)] rounded-full animate-pulse"></div>
        <div className="w-2 h-2 bg-[var(--accent-primary)] rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
        <div className="w-2 h-2 bg-[var(--accent-primary)] rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
      </div>
      <span className="text-sm">Thinking...</span>
    </div>

    {/* Deep Research Progress */}
    {researchIteration > 0 && (
      <div className="mt-3 space-y-2">
        <div className="text-xs text-[var(--muted)] space-y-1">
          {researchIteration >= 1 && (
            <div className="flex items-center">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
              <span>Analyzing codebase structure...</span>
            </div>
          )}
          {researchIteration >= 2 && (
            <div className="flex items-center">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
              <span>Researching related components...</span>
            </div>
          )}
          {researchIteration >= 3 && (
            <div className="flex items-center">
              <div className="w-2 h-2 bg-orange-500 rounded-full mr-2"></div>
              <span>Deep diving into implementation details...</span>
            </div>
          )}
          {researchIteration >= 4 && (
            <div className="flex items-center">
              <div className="w-2 h-2 bg-red-500 rounded-full mr-2"></div>
              <span>Cross-referencing documentation...</span>
            </div>
          )}
          {researchIteration >= 5 && (
            <div className="flex items-center">
              <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
              <span>Finalizing comprehensive answer...</span>
            </div>
          )}
        </div>
      </div>
    )}
  </div>
);

const MessageList: React.FC<MessageListProps> = ({
  response,
  isLoading,
  isEmpty = false
}) => {
  const responseRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when response changes
  useEffect(() => {
    if (responseRef.current) {
      responseRef.current.scrollTop = responseRef.current.scrollHeight;
    }
  }, [response]);

  if (isEmpty && !response) {
    return <EmptyState />;
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {response && (
        <div className="p-4">
          <div ref={responseRef}>
            <Markdown content={response} />
          </div>
        </div>
      )}
      
      {isLoading && <LoadingIndicator />}
    </div>
  );
};

export default MessageList;
