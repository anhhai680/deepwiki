import React from 'react';
import { FaWikipediaW } from 'react-icons/fa';
import ThemeToggle from '@/components/theme-toggle';

interface HomeLayoutProps {
  mobileActiveTab: 'projects' | 'chat';
  onTabChange: (tab: 'projects' | 'chat') => void;
  leftColumn: React.ReactNode;
  rightColumn: React.ReactNode;
}

const HomeLayout: React.FC<HomeLayoutProps> = ({
  mobileActiveTab,
  onTabChange,
  leftColumn,
  rightColumn,
}) => {
  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Header */}
      <header className="border-b border-[var(--border-color)] bg-[var(--card-bg)]/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FaWikipediaW className="text-2xl text-[var(--accent-primary)]" />
              <h1 className="text-2xl font-bold text-[var(--foreground)] font-serif">
                DeepWiki
              </h1>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Mobile Tab Navigation */}
      <div className="lg:hidden border-b border-[var(--border-color)] bg-[var(--card-bg)]">
        <div className="container mx-auto px-4">
          <div className="flex">
            <button
              onClick={() => onTabChange('projects')}
              className={`flex-1 py-3 text-center font-medium text-sm transition-colors ${
                mobileActiveTab === 'projects'
                  ? 'text-[var(--accent-primary)] border-b-2 border-[var(--accent-primary)]'
                  : 'text-[var(--muted)] hover:text-[var(--foreground)]'
              }`}
            >
              Projects
            </button>
            <button
              onClick={() => onTabChange('chat')}
              className={`flex-1 py-3 text-center font-medium text-sm transition-colors ${
                mobileActiveTab === 'chat'
                  ? 'text-[var(--accent-primary)] border-b-2 border-[var(--accent-primary)]'
                  : 'text-[var(--muted)] hover:text-[var(--foreground)]'
              }`}
            >
              Chat
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 flex-1">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
          {/* Left Column - Projects */}
          <div className={`${mobileActiveTab === 'projects' ? 'block' : 'hidden'} lg:block`}>
            {leftColumn}
          </div>

          {/* Right Column - Chat */}
          <div className={`${mobileActiveTab === 'chat' ? 'block' : 'hidden'} lg:block`}>
            {rightColumn}
          </div>
        </div>
      </main>
    </div>
  );
};

export default HomeLayout;
