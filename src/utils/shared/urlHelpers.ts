/**
 * URL parsing utilities for repository information
 */

/**
 * Extract owner from repository URL
 */
export const extractOwnerFromUrl = (url: string): string => {
  try {
    const urlObj = new URL(url);
    const pathParts = urlObj.pathname.split('/').filter(part => part);
    return pathParts[0] || 'unknown';
  } catch {
    return 'unknown';
  }
};

/**
 * Extract repository name from URL
 */
export const extractRepoFromUrl = (url: string): string => {
  try {
    const urlObj = new URL(url);
    const pathParts = urlObj.pathname.split('/').filter(part => part);
    return pathParts[1] || 'unknown';
  } catch {
    return 'unknown';
  }
};

/**
 * Extract repository type from URL
 */
export const extractTypeFromUrl = (url: string): string => {
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname;
    if (hostname.includes('github')) return 'github';
    if (hostname.includes('gitlab')) return 'gitlab';
    if (hostname.includes('bitbucket')) return 'bitbucket';
    return 'github'; // default
  } catch {
    return 'github';
  }
};

/**
 * Parse repository URL into structured data
 */
export const parseRepositoryUrl = (url: string) => {
  return {
    owner: extractOwnerFromUrl(url),
    repo: extractRepoFromUrl(url),
    type: extractTypeFromUrl(url) as 'github' | 'gitlab' | 'bitbucket',
    url: url.trim()
  };
};
