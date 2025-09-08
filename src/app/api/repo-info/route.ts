import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const owner = searchParams.get('owner');
  const repo = searchParams.get('repo');
  const type = searchParams.get('type') || 'github';
  const token = searchParams.get('token');
  const repoUrl = searchParams.get('repo_url');

  if (!owner || !repo) {
    return NextResponse.json(
      { error: 'Owner and repo parameters are required' },
      { status: 400 }
    );
  }

  try {
    console.log(`Fetching repository info for ${owner}/${repo} (${type})`);

    let defaultBranch = 'main';
    let files: string[] = [];

    if (type === 'github') {
      // Fetch repository information from GitHub API
      const repoApiUrl = `https://api.github.com/repos/${owner}/${repo}`;
      const contentsApiUrl = `https://api.github.com/repos/${owner}/${repo}/git/trees/HEAD?recursive=1`;
      
      const headers: Record<string, string> = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'DeepWiki/1.0'
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Get repository information (including default branch)
      const repoResponse = await fetch(repoApiUrl, { headers });
      
      if (repoResponse.ok) {
        const repoData = await repoResponse.json();
        defaultBranch = repoData.default_branch || 'main';
        console.log(`GitHub repository ${owner}/${repo} default branch: ${defaultBranch}`);
      } else {
        console.warn(`Failed to fetch repository info from GitHub API: ${repoResponse.status}`);
      }

      // Get file list from the repository
      const contentsResponse = await fetch(contentsApiUrl, { headers });
      
      if (contentsResponse.ok) {
        const contentsData = await contentsResponse.json();
        
        if (contentsData.tree && Array.isArray(contentsData.tree)) {
          files = contentsData.tree
            .filter((item: { type: string; path: string }) => item.type === 'blob') // Only files, not directories
            .map((item: { type: string; path: string }) => item.path)
            .sort();
          
          console.log(`Found ${files.length} files in repository`);
        }
      } else {
        console.warn(`Failed to fetch repository contents from GitHub API: ${contentsResponse.status}`);
      }

    } else if (type === 'gitlab') {
      // For GitLab, construct API URLs
      const baseUrl = repoUrl ? new URL(repoUrl).origin : 'https://gitlab.com';
      const projectPath = encodeURIComponent(`${owner}/${repo}`);
      const repoApiUrl = `${baseUrl}/api/v4/projects/${projectPath}`;
      const treeApiUrl = `${baseUrl}/api/v4/projects/${projectPath}/repository/tree?recursive=true&per_page=1000`;
      
      const headers: Record<string, string> = {
        'Accept': 'application/json'
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Get repository information
      const repoResponse = await fetch(repoApiUrl, { headers });
      
      if (repoResponse.ok) {
        const repoData = await repoResponse.json();
        defaultBranch = repoData.default_branch || 'main';
        console.log(`GitLab repository ${owner}/${repo} default branch: ${defaultBranch}`);
      } else {
        console.warn(`Failed to fetch repository info from GitLab API: ${repoResponse.status}`);
      }

      // Get file list
      const treeResponse = await fetch(treeApiUrl, { headers });
      
      if (treeResponse.ok) {
        const treeData = await treeResponse.json();
        
        if (Array.isArray(treeData)) {
          files = treeData
            .filter((item: { type: string; path: string }) => item.type === 'blob') // Only files
            .map((item: { type: string; path: string }) => item.path)
            .sort();
          
          console.log(`Found ${files.length} files in GitLab repository`);
        }
      } else {
        console.warn(`Failed to fetch repository tree from GitLab API: ${treeResponse.status}`);
      }

    } else if (type === 'bitbucket') {
      // For Bitbucket, construct API URLs
      const repoApiUrl = `https://api.bitbucket.org/2.0/repositories/${owner}/${repo}`;
      
      const headers: Record<string, string> = {
        'Accept': 'application/json'
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Get repository information
      const repoResponse = await fetch(repoApiUrl, { headers });
      
      if (repoResponse.ok) {
        const repoData = await repoResponse.json();
        defaultBranch = repoData.mainbranch?.name || 'main';
        console.log(`Bitbucket repository ${owner}/${repo} default branch: ${defaultBranch}`);
      } else {
        console.warn(`Failed to fetch repository info from Bitbucket API: ${repoResponse.status}`);
      }

      // Note: Getting a full file list from Bitbucket is more complex and may require pagination
      // For now, we'll just set the default branch
      console.log('File list fetching not yet implemented for Bitbucket');
    }

    // Return the repository information
    const result = {
      default_branch: defaultBranch,
      files,
      type,
      owner,
      repo
    };

    console.log(`Repository info result:`, result);
    return NextResponse.json(result);

  } catch (error) {
    console.error('Error fetching repository information:', error);
    
    // Return a fallback response with sensible defaults
    return NextResponse.json({
      default_branch: 'main',
      files: [],
      type,
      owner,
      repo,
      error: 'Failed to fetch repository information'
    }, { status: 500 });
  }
}
