import { useState, useEffect, useCallback } from 'react';
import { ModelConfiguration, ModelConfigResponse, Provider } from '@/types/shared';

interface UseModelConfigurationProps {
  provider?: string;
  model?: string;
  isCustomModel?: boolean;
  customModel?: string;
}

export const useModelConfiguration = ({
  provider = '',
  model = '',
  isCustomModel = false,
  customModel = ''
}: UseModelConfigurationProps = {}) => {
  const [config, setConfig] = useState<ModelConfiguration>({
    selectedProvider: provider,
    selectedModel: model,
    isCustomModel,
    customModel,
    isComprehensiveView: true
  });

  const [availableConfig, setAvailableConfig] = useState<ModelConfigResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch available model configurations from API
  const fetchModelConfig = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch('/api/models/config');
      if (!response.ok) {
        throw new Error(`Error fetching model configurations: ${response.status}`);
      }

      const data: ModelConfigResponse = await response.json();
      setAvailableConfig(data);

      // Initialize with defaults if not already set
      if (!config.selectedProvider && data.defaultProvider) {
        const defaultProvider = data.providers.find((p: Provider) => p.id === data.defaultProvider);
        if (defaultProvider) {
          const defaultModel = defaultProvider.defaultModel || 
            (defaultProvider.models.length > 0 ? defaultProvider.models[0].id : '');
          
          setConfig(prev => ({
            ...prev,
            selectedProvider: data.defaultProvider,
            selectedModel: defaultModel
          }));
        }
      }
    } catch (err) {
      console.error('Failed to fetch model configurations:', err);
      setError('Failed to load model configurations. Using default options.');
    } finally {
      setIsLoading(false);
    }
  }, [config.selectedProvider]);

  // Update provider and reset model to default
  const updateProvider = useCallback((newProvider: string) => {
    setConfig(prev => ({ ...prev, selectedProvider: newProvider, isCustomModel: false }));
    
    setTimeout(() => {
      if (availableConfig) {
        const selectedProvider = availableConfig.providers.find((p: Provider) => p.id === newProvider);
        if (selectedProvider) {
          const defaultModel = selectedProvider.defaultModel || 
            (selectedProvider.models.length > 0 ? selectedProvider.models[0].id : '');
          setConfig(prev => ({ ...prev, selectedModel: defaultModel }));
        }
      }
    }, 10);
  }, [availableConfig]);

  // Update model
  const updateModel = useCallback((newModel: string) => {
    setConfig(prev => ({ ...prev, selectedModel: newModel }));
  }, []);

  // Toggle custom model
  const toggleCustomModel = useCallback((enabled: boolean) => {
    setConfig(prev => ({ ...prev, isCustomModel: enabled }));
  }, []);

  // Update custom model value
  const updateCustomModel = useCallback((value: string) => {
    setConfig(prev => ({ ...prev, customModel: value }));
  }, []);

  // Update comprehensive view
  const updateComprehensiveView = useCallback((enabled: boolean) => {
    setConfig(prev => ({ ...prev, isComprehensiveView: enabled }));
  }, []);

  // Get current provider details
  const currentProvider = availableConfig?.providers.find(p => p.id === config.selectedProvider) || null;

  // Get effective model (custom or selected)
  const effectiveModel = config.isCustomModel ? config.customModel : config.selectedModel;

  // Initialize configuration
  useEffect(() => {
    if (provider === '' || model === '') {
      fetchModelConfig();
    } else {
      setIsLoading(false);
    }
  }, [provider, model, fetchModelConfig]);

  return {
    config,
    availableConfig,
    currentProvider,
    effectiveModel,
    isLoading,
    error,
    
    // Actions
    updateProvider,
    updateModel,
    toggleCustomModel,
    updateCustomModel,
    updateComprehensiveView,
    refetch: fetchModelConfig,
    
    // Computed properties
    hasCustomModelSupport: currentProvider?.supportsCustomModel || false,
    isConfigured: !!config.selectedProvider && !!effectiveModel
  };
};
