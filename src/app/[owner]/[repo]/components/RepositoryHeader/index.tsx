'use client';

import React from 'react';
import Link from 'next/link';
import { FaHome } from 'react-icons/fa';

interface RepositoryHeaderProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  messages: any;
}

const RepositoryHeader: React.FC<RepositoryHeaderProps> = ({ messages }) => {
  return (
    <header className="w-full mb-8 h-fit">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 px-4">
        <div className="flex items-center gap-4">
          <Link 
            href="/" 
            className="text-[var(--accent-primary)] hover:text-[var(--highlight)] flex items-center gap-1.5 transition-colors border-b border-[var(--border-color)] hover:border-[var(--accent-primary)] pb-0.5"
          >
            <FaHome /> 
            {messages.repoPage?.home || 'Home'}
          </Link>
        </div>
      </div>
    </header>
  );
};

export default RepositoryHeader;
