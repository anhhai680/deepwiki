'use client';

import React from 'react';

interface ActionButtonsProps {
  response: string;
  onDownload: () => void;
  onClear: () => void;
}

const ActionButtons: React.FC<ActionButtonsProps> = ({
  response,
  onDownload,
  onClear
}) => {
  if (!response) return null;

  return (
    <div className="flex items-center space-x-2 mt-4">
      <button
        onClick={onDownload}
        className="text-xs px-3 py-1.5 bg-[var(--background)] border border-[var(--border-color)] text-[var(--foreground)] rounded-md hover:bg-[var(--background)]/80 transition-colors flex items-center gap-1.5"
      >
        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Download
      </button>
      <button
        onClick={onClear}
        className="text-xs px-3 py-1.5 bg-[var(--background)] border border-[var(--border-color)] text-[var(--foreground)] rounded-md hover:bg-[var(--background)]/80 transition-colors flex items-center gap-1.5"
      >
        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
        Clear
      </button>
    </div>
  );
};

export default ActionButtons;
