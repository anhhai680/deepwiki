import React from 'react';
import RepositorySelector from '@/components/RepositorySelector';
import { useProcessedProjects } from '@/hooks/useProcessedProjects';

interface RepositoryInputProps {
  value: string;
  onSelect: (repoUrl: string) => void;
  error: string | null;
  t: (key: string, params?: Record<string, string | number>) => string;
}

const RepositoryInput: React.FC<RepositoryInputProps> = ({
  value,
  onSelect,
  error,
  t,
}) => {
  const { projects } = useProcessedProjects();

  return (
    <div className="space-y-4">
      <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg p-6 shadow-custom card-japanese">
        <h3 className="text-lg font-semibold text-[var(--foreground)] mb-4 font-serif">
          {t('form.repositoryInput')}
        </h3>
        
        <div className="space-y-3">
          <div className="relative">
            <RepositorySelector
              projects={projects}
              selectedRepository={value}
              onRepositorySelect={onSelect}
              placeholder={t('form.repoPlaceholder') || 'Enter repository URL (GitHub, GitLab, BitBucket) or local path...'}
            />
            {error && (
              <div className="absolute top-full left-0 text-[var(--highlight)] text-xs mt-1 z-10">
                {error}
              </div>
            )}
          </div>
          
          <div className="text-xs text-[var(--muted)] space-y-2">
            <p className="font-medium">Supported formats:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 font-mono text-xs">
              <div className="bg-[var(--background)]/70 p-2 rounded border border-[var(--border-color)]">
                https://github.com/owner/repo
              </div>
              <div className="bg-[var(--background)]/70 p-2 rounded border border-[var(--border-color)]">
                https://gitlab.com/owner/repo
              </div>
              <div className="bg-[var(--background)]/70 p-2 rounded border border-[var(--border-color)]">
                /path/to/local/folder
              </div>
              <div className="bg-[var(--background)]/70 p-2 rounded border border-[var(--border-color)]">
                C:\\path\\to\\folder
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RepositoryInput;
