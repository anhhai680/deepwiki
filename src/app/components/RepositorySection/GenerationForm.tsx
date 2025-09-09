import React from 'react';
import TokenInput from '@/components/TokenInput';

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

interface GenerationFormProps {
  config: Config;
  onConfigChange: (updates: Partial<Config>) => void;
  accessToken: string;
  onAccessTokenChange: (token: string) => void;
  authRequired: boolean;
  authCode: string;
  onAuthCodeChange: (code: string) => void;
  isSubmitting: boolean;
  t: (key: string, params?: Record<string, string | number>) => string;
  onGenerate: () => void;
}

const GenerationForm: React.FC<GenerationFormProps> = ({
  config,
  onConfigChange,
  accessToken,
  onAccessTokenChange,
  authRequired,
  authCode,
  onAuthCodeChange,
  isSubmitting,
  t,
  onGenerate,
}) => {
  return (
    <div className="space-y-4">
      {/* Platform Selection */}
      <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg p-6 shadow-custom card-japanese">
        <h3 className="text-lg font-semibold text-[var(--foreground)] mb-4 font-serif">
          {t('form.platform')}
        </h3>
        <div className="flex gap-2">
          {(['github', 'gitlab', 'bitbucket'] as const).map((platform) => (
            <button
              key={platform}
              onClick={() => onConfigChange({ selectedPlatform: platform })}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors capitalize ${
                config.selectedPlatform === platform
                  ? 'bg-[var(--accent-primary)] text-white'
                  : 'bg-[var(--background)] text-[var(--foreground)] border border-[var(--border-color)] hover:bg-[var(--accent-primary)]/10'
              }`}
            >
              {platform}
            </button>
          ))}
        </div>
      </div>

      {/* Access Token */}
      <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg p-6 shadow-custom card-japanese">
        <h3 className="text-lg font-semibold text-[var(--foreground)] mb-4 font-serif">
          {t('form.accessToken')}
        </h3>
        <TokenInput
          selectedPlatform={config.selectedPlatform}
          setSelectedPlatform={(platform) => onConfigChange({ selectedPlatform: platform })}
          accessToken={accessToken}
          setAccessToken={onAccessTokenChange}
          allowPlatformChange={false}
        />
        <p className="text-xs text-[var(--muted)] mt-2">
          {t('form.tokenHelp')}
        </p>
      </div>

      {/* Authentication Code (if required) */}
      {authRequired && (
        <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg p-6 shadow-custom card-japanese">
          <h3 className="text-lg font-semibold text-[var(--foreground)] mb-4 font-serif">
            {t('form.authCode')}
          </h3>
          <input
            type="password"
            value={authCode}
            onChange={(e) => onAuthCodeChange(e.target.value)}
            className="w-full px-3 py-2 border border-[var(--border-color)] rounded-lg bg-[var(--background)] text-[var(--foreground)] focus:ring-2 focus:ring-[var(--accent-primary)]/50 focus:border-[var(--accent-primary)] transition-colors"
            placeholder="Enter authorization code"
            required
          />
        </div>
      )}

      {/* Wiki Type Selection */}
      <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg p-6 shadow-custom card-japanese">
        <h3 className="text-lg font-semibold text-[var(--foreground)] mb-4 font-serif">
          {t('form.wikiType')}
        </h3>
        <div className="flex gap-2">
          <button
            onClick={() => onConfigChange({ isComprehensiveView: true })}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              config.isComprehensiveView
                ? 'bg-[var(--accent-primary)] text-white'
                : 'bg-[var(--background)] text-[var(--foreground)] border border-[var(--border-color)] hover:bg-[var(--accent-primary)]/10'
            }`}
          >
            {t('form.comprehensive')}
          </button>
          <button
            onClick={() => onConfigChange({ isComprehensiveView: false })}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              !config.isComprehensiveView
                ? 'bg-[var(--accent-primary)] text-white'
                : 'bg-[var(--background)] text-[var(--foreground)] border border-[var(--border-color)] hover:bg-[var(--accent-primary)]/10'
            }`}
          >
            {t('form.summary')}
          </button>
        </div>
      </div>

      {/* Generate Button */}
      <div className="flex justify-center pt-4">
        <button
          onClick={onGenerate}
          disabled={isSubmitting}
          className="px-8 py-3 bg-[var(--accent-primary)] text-white rounded-lg font-medium hover:bg-[var(--accent-primary)]/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          {isSubmitting ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              {t('common.processing')}
            </>
          ) : (
            t('form.generateWiki')
          )}
        </button>
      </div>
    </div>
  );
};

export default GenerationForm;
