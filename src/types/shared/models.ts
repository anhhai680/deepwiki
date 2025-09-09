// Model and provider types
export interface Model {
  id: string;
  name: string;
}

export interface Provider {
  id: string;
  name: string;
  models: Model[];
  supportsCustomModel?: boolean;
  defaultModel?: string;
}

export interface ModelConfiguration {
  selectedProvider: string;
  selectedModel: string;
  isCustomModel: boolean;
  customModel: string;
  isComprehensiveView: boolean;
}

export interface ModelConfigResponse {
  providers: Provider[];
  defaultProvider: string;
}
