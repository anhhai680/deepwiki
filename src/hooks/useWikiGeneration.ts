import { useState, useCallback, useRef, useEffect } from 'react';
import { WikiStructure, WikiPage } from '@/types/shared';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import type { WikiGenerationRequest } from '@/types/shared';
import { RepoInfo } from '@/types/repoinfo';
import getRepoUrl from '@/utils/getRepoUrl';
import { addTokensToRequestBody } from '@/utils/shared/wikiHelpers';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { generateFileUrl } from '@/utils/shared/wikiHelpers';

interface UseWikiGenerationOptions {
  repoInfo: RepoInfo;
  defaultBranch: string;
  repositoryFiles: string[];
  language: string;
}

export const useWikiGeneration = ({ 
  repoInfo, 
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  defaultBranch, 
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  repositoryFiles, 
  language 
}: UseWikiGenerationOptions) => {
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState<string>();
  const [error, setError] = useState<string | null>(null);
  const [wikiStructure, setWikiStructure] = useState<WikiStructure>();
  const [currentPageId, setCurrentPageId] = useState<string>();
  const [generatedPages, setGeneratedPages] = useState<Record<string, WikiPage>>({});
  const [pagesInProgress, setPagesInProgress] = useState(new Set<string>());
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const activeContentRequests = useRef(new Map<string, boolean>()).current;

  const determineWikiStructure = useCallback(async (
    fileTreeData: string,
    readmeContent: string,
    owner: string,
    repo: string,
    provider: string,
    model: string,
    isCustomModel: boolean,
    customModel: string,
    token: string,
    excludedDirs: string,
    excludedFiles: string,
    includedDirs: string,
    includedFiles: string,
    isComprehensiveView: boolean
  ) => {
    setIsLoading(true);
    setError(null);
    setLoadingMessage('Determining wiki structure...');

    try {
      const repoUrl = getRepoUrl(repoInfo);
      let responseText = '';

      // Create request body
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const requestBody: Record<string, any> = {
        repo_url: repoUrl,
        type: repoInfo.type,
        messages: [{
          role: 'user',
          content: 'Determine wiki structure based on repository analysis'
        }]
      };

      // Add parameters
      addTokensToRequestBody(
        requestBody, 
        token, 
        repoInfo.type, 
        provider, 
        model, 
        isCustomModel, 
        customModel, 
        language,
        excludedDirs,
        excludedFiles,
        includedDirs,
        includedFiles
      );

      // Try WebSocket first, fallback to HTTP
      try {
        const serverBaseUrl = process.env.SERVER_BASE_URL || 'http://localhost:8001';
        const wsBaseUrl = serverBaseUrl.replace(/^http/, 'ws');
        const wsUrl = `${wsBaseUrl}/ws/chat`;

        const ws = new WebSocket(wsUrl);

        await new Promise<void>((resolve, reject) => {
          const timeout = setTimeout(() => reject(new Error('WebSocket timeout')), 5000);

          ws.onopen = () => {
            clearTimeout(timeout);
            ws.send(JSON.stringify(requestBody));
          };

          ws.onmessage = (event) => {
            responseText += event.data;
          };

          ws.onclose = () => resolve();
          ws.onerror = () => reject(new Error('WebSocket error'));
        });
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      } catch (wsError) {
        // Fallback to HTTP
        const response = await fetch(`/api/chat/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
          throw new Error(`Error determining wiki structure: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('Failed to get response reader');
        }

        responseText = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          responseText += decoder.decode(value, { stream: true });
        }
      }

      // Handle embedding errors
      if (responseText.includes('Error preparing retriever: Environment variable OPENAI_API_KEY must be set')) {
        throw new Error('OPENAI_API_KEY environment variable is not set. Please configure your OpenAI API key.');
      }

      if (responseText.includes('Ollama model') && responseText.includes('not found')) {
        throw new Error('The specified Ollama embedding model was not found. Please ensure the model is installed locally or select a different embedding model in the configuration.');
      }

      // Parse XML response
      responseText = responseText.replace(/^```(?:xml)?\s*/i, '').replace(/```\s*$/i, '');
      const xmlMatch = responseText.match(/<wiki_structure>[\s\S]*?<\/wiki_structure>/m);
      
      if (!xmlMatch) {
        throw new Error('No valid XML found in response');
      }

      const xmlText = xmlMatch[0].replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(xmlText, "text/xml");

      // Extract wiki structure from XML
      const titleEl = xmlDoc.querySelector('title');
      const descriptionEl = xmlDoc.querySelector('description');
      const pagesEls = xmlDoc.querySelectorAll('page');

      const title = titleEl?.textContent || '';
      const description = descriptionEl?.textContent || '';
      const pages: WikiPage[] = [];

      pagesEls.forEach(pageEl => {
        const id = pageEl.getAttribute('id') || `page-${pages.length + 1}`;
        const titleEl = pageEl.querySelector('title');
        const importanceEl = pageEl.querySelector('importance');
        const filePathEls = pageEl.querySelectorAll('file_path');
        const relatedEls = pageEl.querySelectorAll('related');

        const title = titleEl?.textContent || '';
        const importance = importanceEl?.textContent === 'high' ? 'high' :
          importanceEl?.textContent === 'medium' ? 'medium' : 'low';

        const filePaths: string[] = [];
        filePathEls.forEach(el => {
          if (el.textContent) filePaths.push(el.textContent);
        });

        const relatedPages: string[] = [];
        relatedEls.forEach(el => {
          if (el.textContent) relatedPages.push(el.textContent);
        });

        pages.push({
          id,
          title,
          content: '', // Will be generated later
          filePaths,
          importance: importance as 'high' | 'medium' | 'low',
          relatedPages
        });
      });

      // Extract sections if comprehensive view
      const sections: never[] = [];
      const rootSections: never[] = [];

      if (isComprehensiveView) {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const sectionsEls = xmlDoc.querySelectorAll('section');
        // ... section parsing logic would go here
      }

      const newWikiStructure: WikiStructure = {
        id: 'wiki',
        title,
        description,
        pages,
        sections,
        rootSections
      };

      setWikiStructure(newWikiStructure);
      setCurrentPageId(pages.length > 0 ? pages[0].id : undefined);

      // Start generating page content
      if (pages.length > 0) {
        await generatePageContent(pages, newWikiStructure, provider, model, isCustomModel, customModel, token, excludedDirs, excludedFiles, includedDirs, includedFiles);
      }

    } catch (err) {
      console.error('Error determining wiki structure:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setIsLoading(false);
      setLoadingMessage(undefined);
    }
  }, [repoInfo, language]);

  const generatePageContent = useCallback(async (
    pages: WikiPage[],
    structure: WikiStructure,
    provider: string,
    model: string,
    isCustomModel: boolean,
    customModel: string,
    token: string,
    excludedDirs: string,
    excludedFiles: string,
    includedDirs: string,
    includedFiles: string
  ) => {
    const MAX_CONCURRENT = 1;
    const queue = [...pages];
    let activeRequests = 0;

    const processQueue = () => {
      while (queue.length > 0 && activeRequests < MAX_CONCURRENT) {
        const page = queue.shift()!;
        activeRequests++;
        
        generateSinglePage(page, provider, model, isCustomModel, customModel, token, excludedDirs, excludedFiles, includedDirs, includedFiles)
          .finally(() => {
            activeRequests--;
            processQueue();
          });
      }
    };

    processQueue();
  }, [repoInfo, language]);

  const generateSinglePage = useCallback(async (
    page: WikiPage,
    provider: string,
    model: string,
    isCustomModel: boolean,
    customModel: string,
    token: string,
    excludedDirs: string,
    excludedFiles: string,
    includedDirs: string,
    includedFiles: string
  ) => {
    if (activeContentRequests.has(page.id)) return;
    
    activeContentRequests.set(page.id, true);
    setPagesInProgress(prev => new Set(prev).add(page.id));

    try {
      const repoUrl = getRepoUrl(repoInfo);
      const promptContent = `Generate wiki page content for: ${page.title}`;

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const requestBody: Record<string, any> = {
        repo_url: repoUrl,
        type: repoInfo.type,
        messages: [{ role: 'user', content: promptContent }]
      };

      addTokensToRequestBody(
        requestBody, 
        token, 
        repoInfo.type, 
        provider, 
        model, 
        isCustomModel, 
        customModel, 
        language,
        excludedDirs,
        excludedFiles,
        includedDirs,
        includedFiles
      );

      let content = '';

      // Try WebSocket first, fallback to HTTP
      try {
        const serverBaseUrl = process.env.SERVER_BASE_URL || 'http://localhost:8001';
        const wsBaseUrl = serverBaseUrl.replace(/^http/, 'ws');
        const wsUrl = `${wsBaseUrl}/ws/chat`;

        const ws = new WebSocket(wsUrl);

        await new Promise<void>((resolve, reject) => {
          const timeout = setTimeout(() => reject(new Error('WebSocket timeout')), 30000);

          ws.onopen = () => {
            clearTimeout(timeout);
            ws.send(JSON.stringify(requestBody));
          };

          ws.onmessage = (event) => {
            content += event.data;
          };

          ws.onclose = () => resolve();
          ws.onerror = () => reject(new Error('WebSocket error'));
        });
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      } catch (wsError) {
        // Fallback to HTTP
        const response = await fetch(`/api/chat/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
          throw new Error(`Error generating page content: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('Failed to get response reader');
        }

        content = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          content += decoder.decode(value, { stream: true });
        }
      }

      // Update generated pages
      setGeneratedPages(prev => ({
        ...prev,
        [page.id]: { ...page, content }
      }));

    } catch (err) {
      console.error(`Error generating page ${page.title}:`, err);
      setGeneratedPages(prev => ({
        ...prev,
        [page.id]: { ...page, content: 'Error generating content' }
      }));
    } finally {
      activeContentRequests.delete(page.id);
      setPagesInProgress(prev => {
        const newSet = new Set(prev);
        newSet.delete(page.id);
        return newSet;
      });
    }
  }, [repoInfo, language, activeContentRequests]);

  const exportWiki = useCallback(async (format: 'markdown' | 'json') => {
    if (!wikiStructure || Object.keys(generatedPages).length === 0) {
      setExportError('No wiki content to export');
      return;
    }

    try {
      setIsExporting(true);
      setExportError(null);

      const pagesToExport = wikiStructure.pages.map(page => ({
        ...page,
        content: generatedPages[page.id]?.content || 'Content not generated'
      }));

      const repoUrl = getRepoUrl(repoInfo);

      const response = await fetch(`/export/wiki`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo_url: repoUrl,
          type: repoInfo.type,
          pages: pagesToExport,
          format
        })
      });

      if (!response.ok) {
        const errorText = await response.text().catch(() => 'No error details available');
        throw new Error(`Error exporting wiki: ${response.status} - ${errorText}`);
      }

      // Download the file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${repoInfo.repo}_wiki.${format === 'markdown' ? 'md' : 'json'}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

    } catch (err) {
      console.error('Error exporting wiki:', err);
      setExportError(err instanceof Error ? err.message : 'Unknown error during export');
    } finally {
      setIsExporting(false);
    }
  }, [wikiStructure, generatedPages, repoInfo]);

  // Auto-initialize wiki generation when hook mounts
  useEffect(() => {
    const initializeWikiGeneration = async () => {
      if (isLoading) return; // Prevent duplicate initialization
      
      try {
        setIsLoading(true);
        setError(null);
        setLoadingMessage('Checking for cached wiki...');
        
        // Step 1: Try loading from server-side cache first
        const params = new URLSearchParams({
          owner: repoInfo.owner,
          repo: repoInfo.repo,
          repo_type: repoInfo.type,
          language: language,
          comprehensive: 'true' // Default to comprehensive
        });
        
        try {
          const response = await fetch(`/api/wiki_cache?${params.toString()}`);
          
          if (response.ok) {
            const cachedData = await response.json();
            if (cachedData && cachedData.wiki_structure && cachedData.generated_pages && Object.keys(cachedData.generated_pages).length > 0) {
              console.log('Using server-cached wiki data');
              
              // Ensure the cached structure has sections and rootSections
              const cachedStructure = {
                ...cachedData.wiki_structure,
                sections: cachedData.wiki_structure.sections || [],
                rootSections: cachedData.wiki_structure.rootSections || []
              };
              
              setWikiStructure(cachedStructure);
              setGeneratedPages(cachedData.generated_pages);
              setCurrentPageId(cachedStructure.pages.length > 0 ? cachedStructure.pages[0].id : undefined);
              setIsLoading(false);
              setLoadingMessage(undefined);
              return; // Exit early if cache is found
            }
          }
        } catch (error) {
          console.warn('Error checking cache, proceeding with fresh generation:', error);
        }
        
        // Step 2: No cache found, fetch repository structure and generate wiki
        setLoadingMessage('Fetching repository structure...');
        await fetchRepositoryStructureAndGenerateWiki();
        
      } catch (err) {
        console.error('Error initializing wiki generation:', err);
        setError(err instanceof Error ? err.message : 'Failed to initialize wiki generation');
        setIsLoading(false);
        setLoadingMessage(undefined);
      }
    };
    
    // Only initialize if we have valid repo info
    if (repoInfo.owner && repoInfo.repo) {
      initializeWikiGeneration();
    }
  }, [repoInfo.owner, repoInfo.repo, repoInfo.type, language]);
  
  // Function to fetch repository structure and generate wiki
  const fetchRepositoryStructureAndGenerateWiki = useCallback(async () => {
    let fileTreeData = '';
    let readmeContent = '';
    
    try {
      if (repoInfo.type === 'local' && repoInfo.localPath) {
        // Handle local repositories
        const response = await fetch(`/local_repo/structure?path=${encodeURIComponent(repoInfo.localPath)}`);
        
        if (!response.ok) {
          const errorData = await response.text();
          throw new Error(`Local repository API error (${response.status}): ${errorData}`);
        }
        
        const data = await response.json();
        fileTreeData = data.file_tree;
        readmeContent = data.readme;
        
      } else if (repoInfo.type === 'github') {
        // Handle GitHub repositories
        const githubApiBaseUrl = repoInfo.repoUrl?.includes('github.com') ? 'https://api.github.com' : 'https://api.github.com';
        
        // Try to get repository tree data
        const branchesToTry = ['main', 'master'];
        let treeData = null;
        
        for (const branch of branchesToTry) {
          const apiUrl = `${githubApiBaseUrl}/repos/${repoInfo.owner}/${repoInfo.repo}/git/trees/${branch}?recursive=1`;
          const headers: HeadersInit = {
            'Accept': 'application/vnd.github.v3+json'
          };
          
          if (repoInfo.token) {
            headers['Authorization'] = `Bearer ${repoInfo.token}`;
          }
          
          try {
            const response = await fetch(apiUrl, { headers });
            
            if (response.ok) {
              treeData = await response.json();
              console.log(`Successfully fetched repository structure from branch: ${branch}`);
              break;
            }
          } catch (err) {
            console.warn(`Error fetching branch ${branch}:`, err);
          }
        }
        
        if (!treeData || !treeData.tree) {
          throw new Error('Could not fetch repository structure. Repository might not exist, be empty or private.');
        }
        
        // Convert tree data to file list
        fileTreeData = treeData.tree
          .filter((item: { type: string; path: string }) => item.type === 'blob')
          .map((item: { type: string; path: string }) => item.path)
          .join('\n');
        
        // Try to fetch README.md content
        try {
          const readmeHeaders: HeadersInit = {
            'Accept': 'application/vnd.github.v3+json'
          };
          
          if (repoInfo.token) {
            readmeHeaders['Authorization'] = `Bearer ${repoInfo.token}`;
          }
          
          const readmeResponse = await fetch(`${githubApiBaseUrl}/repos/${repoInfo.owner}/${repoInfo.repo}/readme`, {
            headers: readmeHeaders
          });
          
          if (readmeResponse.ok) {
            const readmeData = await readmeResponse.json();
            readmeContent = atob(readmeData.content);
          }
        } catch (err) {
          console.warn('Could not fetch README.md:', err);
        }
        
      } else if (repoInfo.type === 'gitlab') {
        // Handle GitLab repositories
        const projectPath = repoInfo.repoUrl 
          ? new URL(repoInfo.repoUrl).pathname.slice(1) // Remove leading /
          : `${repoInfo.owner}/${repoInfo.repo}`;
        const projectDomain = repoInfo.repoUrl 
          ? new URL(repoInfo.repoUrl).origin 
          : 'https://gitlab.com';
        const encodedProjectPath = encodeURIComponent(projectPath);
        
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
        };
        
        if (repoInfo.token) {
          headers['PRIVATE-TOKEN'] = repoInfo.token;
        }
        
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const filesData: any[] = [];
        let defaultBranch = 'main';
        
        try {
          // Step 1: Get project info to determine default branch
          const projectInfoUrl = `${projectDomain}/api/v4/projects/${encodedProjectPath}`;
          const projectInfoRes = await fetch(projectInfoUrl, { headers });
          
          if (!projectInfoRes.ok) {
            const errorData = await projectInfoRes.text();
            throw new Error(`GitLab project info error: Status ${projectInfoRes.status}, Response: ${errorData}`);
          }
          
          const projectInfo = await projectInfoRes.json();
          defaultBranch = projectInfo.default_branch || 'main';
          console.log(`Found GitLab default branch: ${defaultBranch}`);
          
          // Step 2: Paginate to fetch full file tree
          let page = 1;
          let morePages = true;
          
          while (morePages) {
            const apiUrl = `${projectInfoUrl}/repository/tree?recursive=true&per_page=100&page=${page}`;
            const response = await fetch(apiUrl, { headers });
            
            if (!response.ok) {
              const errorData = await response.text();
              throw new Error(`Error fetching GitLab repository structure (page ${page}): ${errorData}`);
            }
            
            const pageData = await response.json();
            filesData.push(...pageData);
            
            const nextPage = response.headers.get('x-next-page');
            morePages = !!nextPage;
            page = nextPage ? parseInt(nextPage, 10) : page + 1;
          }
          
          if (!Array.isArray(filesData) || filesData.length === 0) {
            throw new Error('Could not fetch repository structure. Repository might be empty or inaccessible.');
          }
          
          // Convert files data to a string representation
          fileTreeData = filesData
            .filter((item: { type: string; path: string }) => item.type === 'blob')
            .map((item: { type: string; path: string }) => item.path)
            .join('\n');
          
          console.log(`GitLab repository contains ${filesData.length} files`);
          
          // Try to fetch README.md content
          try {
            const readmeResponse = await fetch(`${projectInfoUrl}/repository/files/README.md/raw?ref=${defaultBranch}`, {
              headers
            });
            
            if (readmeResponse.ok) {
              readmeContent = await readmeResponse.text();
            } else {
              console.warn(`Could not fetch GitLab README.md, status: ${readmeResponse.status}`);
            }
          } catch (err) {
            console.warn('Could not fetch GitLab README.md:', err);
          }
          
        } catch (err) {
          console.error('Error processing GitLab repository:', err);
          throw err;
        }
        
      } else if (repoInfo.type === 'bitbucket') {
        // Handle Bitbucket repositories
        const repoPath = `${repoInfo.owner}/${repoInfo.repo}`;
        const encodedRepoPath = encodeURIComponent(repoPath);
        
        let defaultBranch = 'main';
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
        };
        
        if (repoInfo.token) {
          headers['Authorization'] = `Bearer ${repoInfo.token}`;
        }
        
        try {
          // First get project info to determine default branch
          const projectInfoUrl = `https://api.bitbucket.org/2.0/repositories/${encodedRepoPath}`;
          const response = await fetch(projectInfoUrl, { headers });
          
          const responseText = await response.text();
          
          if (!response.ok) {
            throw new Error(`Bitbucket project info error: Status ${response.status}, Response: ${responseText}`);
          }
          
          const projectData = JSON.parse(responseText);
          defaultBranch = projectData.mainbranch.name;
          console.log(`Found Bitbucket default branch: ${defaultBranch}`);
          
          // Get repository file structure
          const apiUrl = `https://api.bitbucket.org/2.0/repositories/${encodedRepoPath}/src/${defaultBranch}/?recursive=true&per_page=100`;
          const structureResponse = await fetch(apiUrl, { headers });
          
          const structureResponseText = await structureResponse.text();
          
          if (!structureResponse.ok) {
            throw new Error(`Bitbucket structure error: Status ${structureResponse.status}, Response: ${structureResponseText}`);
          }
          
          const filesData = JSON.parse(structureResponseText);
          
          if (!filesData || !Array.isArray(filesData.values) || filesData.values.length === 0) {
            throw new Error('Could not fetch repository structure. Repository might not exist, be empty or private.');
          }
          
          // Convert files data to a string representation
          fileTreeData = filesData.values
            .filter((item: { type: string; path: string }) => item.type === 'commit_file')
            .map((item: { type: string; path: string }) => item.path)
            .join('\n');
          
          console.log(`Bitbucket repository contains ${filesData.values.length} files`);
          
          // Try to fetch README.md content
          try {
            const readmeResponse = await fetch(`https://api.bitbucket.org/2.0/repositories/${encodedRepoPath}/src/${defaultBranch}/README.md`, {
              headers
            });
            
            if (readmeResponse.ok) {
              readmeContent = await readmeResponse.text();
            } else {
              console.warn(`Could not fetch Bitbucket README.md, status: ${readmeResponse.status}`);
            }
          } catch (err) {
            console.warn('Could not fetch Bitbucket README.md:', err);
          }
          
        } catch (err) {
          console.error('Error processing Bitbucket repository:', err);
          throw err;
        }
        
      } else {
        throw new Error(`Repository type ${repoInfo.type} is not supported`);
      }
      
      // Step 3: Generate wiki structure using the determineWikiStructure function
      setLoadingMessage('Generating wiki structure...');
      await determineWikiStructure(
        fileTreeData,
        readmeContent,
        repoInfo.owner,
        repoInfo.repo,
        'google', // Default provider
        'gemini-1.5-flash', // Default model
        false, // isCustomModel
        '', // customModel
        repoInfo.token || '', // token
        '', // excludedDirs
        '', // excludedFiles
        '', // includedDirs
        '', // includedFiles
        true // isComprehensiveView
      );
      
    } catch (error) {
      console.error('Error in fetchRepositoryStructureAndGenerateWiki:', error);
      throw error;
    }
  }, [repoInfo, determineWikiStructure]);

  return {
    // State
    isLoading,
    loadingMessage,
    error,
    wikiStructure,
    currentPageId,
    generatedPages,
    pagesInProgress,
    isExporting,
    exportError,

    // Actions
    determineWikiStructure,
    exportWiki,
    setCurrentPageId,
    setError,
    setIsLoading,
    setLoadingMessage,

    // Computed
    totalPages: wikiStructure?.pages.length || 0,
    completedPages: wikiStructure?.pages.length ? wikiStructure.pages.length - pagesInProgress.size : 0,
    progressPercentage: wikiStructure?.pages.length 
      ? Math.max(5, 100 * (wikiStructure.pages.length - pagesInProgress.size) / wikiStructure.pages.length)
      : 0
  };
};
