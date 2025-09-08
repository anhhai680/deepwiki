'use client';

import React from 'react';

interface MessageInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  placeholder?: string;
  disabled?: boolean;
  isLoading?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({
  value,
  onChange,
  onSubmit,
  placeholder = 'Ask about this repository...',
  disabled = false,
  isLoading = false
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!value.trim() || disabled) return;
    onSubmit();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="relative">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="block w-full rounded-lg border border-[var(--border-color)] bg-[var(--background)] text-[var(--foreground)] px-4 py-3 pr-16 text-sm focus:border-[var(--accent-primary)] focus:ring-2 focus:ring-[var(--accent-primary)]/20 focus:outline-none transition-all resize-none"
          disabled={disabled}
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className={`absolute right-2 top-1/2 transform -translate-y-1/2 p-2 rounded-md ${
            disabled || !value.trim()
              ? 'bg-[var(--muted)] text-[var(--background)] cursor-not-allowed'
              : 'bg-[var(--accent-primary)] text-white hover:bg-[var(--accent-primary)]/90'
          } transition-all duration-200`}
        >
          {isLoading ? (
            <div className="w-4 h-4 rounded-full border-2 border-t-transparent border-white animate-spin" />
          ) : (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>
    </form>
  );
};

export default MessageInput;
