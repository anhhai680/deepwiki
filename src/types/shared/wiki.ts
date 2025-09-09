// Wiki-related types
export interface WikiSection {
  id: string;
  title: string;
  pages: string[];
  subsections?: string[];
}

export interface WikiPage {
  id: string;
  title: string;
  content: string;
  filePaths: string[];
  importance: 'high' | 'medium' | 'low';
  relatedPages: string[];
  parentId?: string;
  isSection?: boolean;
  children?: string[];
}

export interface WikiStructure {
  id: string;
  title: string;
  description: string;
  pages: WikiPage[];
  sections: WikiSection[];
  rootSections: string[];
}

// Wiki generation state
export interface WikiGenerationState {
  isLoading: boolean;
  loadingMessage?: string;
  error: string | null;
  wikiStructure?: WikiStructure;
  currentPageId?: string;
  generatedPages: Record<string, WikiPage>;
  pagesInProgress: Set<string>;
  isExporting: boolean;
  exportError: string | null;
}

// Wiki generation request types
export interface WikiGenerationRequest {
  repoUrl: string;
  type: string;
  provider: string;
  model: string;
  isCustomModel: boolean;
  customModel: string;
  language: string;
  token?: string;
  excludedDirs?: string;
  excludedFiles?: string;
  includedDirs?: string;
  includedFiles?: string;
}
