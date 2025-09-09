/**
 * Wiki utility functions
 */

/**
 * Generate cache key for localStorage
 */
export const getCacheKey = (
  owner: string, 
  repo: string, 
  repoType: string, 
  language: string, 
  isComprehensive: boolean = true
): string => {
  return `deepwiki_cache_${repoType}_${owner}_${repo}_${language}_${isComprehensive ? 'comprehensive' : 'concise'}`;
};

/**
 * Add tokens and parameters to request body
 */
export const addTokensToRequestBody = (
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  requestBody: Record<string, any>,
  token: string,
  repoType: string,
  provider: string = '',
  model: string = '',
  isCustomModel: boolean = false,
  customModel: string = '',
  language: string = 'en',
  excludedDirs?: string,
  excludedFiles?: string,
  includedDirs?: string,
  includedFiles?: string
): void => {
  if (token !== '') {
    requestBody.token = token;
  }

  // Add provider-based model selection parameters
  requestBody.provider = provider;
  requestBody.model = model;
  if (isCustomModel && customModel) {
    requestBody.custom_model = customModel;
  }

  requestBody.language = language;

  // Add file filter parameters if provided
  if (excludedDirs) {
    requestBody.excluded_dirs = excludedDirs;
  }
  if (excludedFiles) {
    requestBody.excluded_files = excludedFiles;
  }
  if (includedDirs) {
    requestBody.included_dirs = includedDirs;
  }
  if (includedFiles) {
    requestBody.included_files = includedFiles;
  }
};

/**
 * Create GitHub API headers
 */
export const createGithubHeaders = (githubToken: string): HeadersInit => {
  const headers: HeadersInit = {
    'Accept': 'application/vnd.github.v3+json'
  };

  if (githubToken) {
    headers['Authorization'] = `Bearer ${githubToken}`;
  }

  return headers;
};

/**
 * Create GitLab API headers
 */
export const createGitlabHeaders = (gitlabToken: string): HeadersInit => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (gitlabToken) {
    headers['PRIVATE-TOKEN'] = gitlabToken;
  }

  return headers;
};

/**
 * Create Bitbucket API headers
 */
export const createBitbucketHeaders = (bitbucketToken: string): HeadersInit => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (bitbucketToken) {
    headers['Authorization'] = `Bearer ${bitbucketToken}`;
  }

  return headers;
};

/**
 * Generate proper repository file URLs
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const generateFileUrl = (filePath: string, repoInfo: any, defaultBranch: string): string => {
  if (repoInfo.type === 'local') {
    // For local repositories, we can't generate web URLs
    return filePath;
  }

  const repoUrl = repoInfo.repoUrl;
  if (!repoUrl) {
    return filePath;
  }

  try {
    const url = new URL(repoUrl);
    const hostname = url.hostname;
    
    if (hostname === 'github.com' || hostname.includes('github')) {
      // GitHub URL format: https://github.com/owner/repo/blob/branch/path
      return `${repoUrl}/blob/${defaultBranch}/${filePath}`;
    } else if (hostname === 'gitlab.com' || hostname.includes('gitlab')) {
      // GitLab URL format: https://gitlab.com/owner/repo/-/blob/branch/path
      return `${repoUrl}/-/blob/${defaultBranch}/${filePath}`;
    } else if (hostname === 'bitbucket.org' || hostname.includes('bitbucket')) {
      // Bitbucket URL format: https://bitbucket.org/owner/repo/src/branch/path
      return `${repoUrl}/src/${defaultBranch}/${filePath}`;
    }
  } catch (error) {
    console.warn('Error generating file URL:', error);
  }

  // Fallback to just the file path
  return filePath;
};
