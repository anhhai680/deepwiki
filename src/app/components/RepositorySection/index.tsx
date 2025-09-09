import React from 'react';
import RepositoryInput from './RepositoryInput';
import GenerationForm from './GenerationForm';

interface Config {
  isComprehensiveView: boolean;
  provider: string;
  model: string;
  isCustomModel: boolean;
  customModel: string;
  selectedPlatform: 'github' | 'gitlab' | 'bitbucket';
  excludedDirs: string;
  excludedFiles: string;
  includedDirs: string;
  includedFiles: string;
}

interface RepositorySectionProps {
  repositoryInput: string;
  onRepositorySelect: (repoUrl: string) => void;
  isSubmitting: boolean;
  error: string | null;
  config: Config;
  onConfigChange: (updates: Partial<Config>) => void;
  accessToken: string;
  onAccessTokenChange: (token: string) => void;
  authRequired: boolean;
  authCode: string;
  onAuthCodeChange: (code: string) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
  onGenerate: () => void;
}

const RepositorySection: React.FC<RepositorySectionProps> = ({
  repositoryInput,
  onRepositorySelect,
  isSubmitting,
  error,
  config,
  onConfigChange,
  accessToken,
  onAccessTokenChange,
  authRequired,
  authCode,
  onAuthCodeChange,
  t,
  onGenerate,
}) => {
  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-[var(--foreground)] mb-2 font-serif">
          {t('home.title')}
        </h2>
        <p className="text-[var(--muted)] font-serif text-lg">
          {t('home.subtitle')}
        </p>
      </div>

      <RepositoryInput
        value={repositoryInput}
        onSelect={onRepositorySelect}
        error={error}
        t={t}
      />

      <GenerationForm
        config={config}
        onConfigChange={onConfigChange}
        accessToken={accessToken}
        onAccessTokenChange={onAccessTokenChange}
        authRequired={authRequired}
        authCode={authCode}
        onAuthCodeChange={onAuthCodeChange}
        isSubmitting={isSubmitting}
        t={t}
        onGenerate={onGenerate}
      />

    </div>
  );
};

export default RepositorySection;
