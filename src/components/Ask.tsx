'use client';

import React, {useState, useRef, useEffect} from 'react';
import {FaChevronLeft, FaChevronRight } from 'react-icons/fa';
import Markdown from './Markdown';
import { useLanguage } from '@/contexts/LanguageContext';
import RepoInfo from '@/types/repoinfo';
import getRepoUrl from '@/utils/getRepoUrl';
import ModelSelectionModal from './ModelSelectionModal';
import { createChatWebSocket, closeWebSocket, ChatCompletionRequest } from '@/utils/websocketClient';
import MultiRepositorySelector from './MultiRepositorySelector';

interface Model {
  id: string;
  name: string;
}

interface Provider {
  id: string;
  name: string;
  models: Model[];
  supportsCustomModel?: boolean;
  defaultModel?: string;
}

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface ResearchStage {
  title: string;
  content: string;
  iteration: number;
  type: 'plan' | 'update' | 'conclusion';
}

interface ProcessedProject {
  id: string;
  owner: string;
  repo: string;
  name: string;
  repo_type: string;
  submittedAt: number;
  language: string;
}

interface AskProps {
  repoInfo: RepoInfo | RepoInfo[];
  projects?: ProcessedProject[];
  provider?: string;
  model?: string;
  isCustomModel?: boolean;
  customModel?: string;
  language?: string;
  onRef?: (ref: { clearConversation: () => void }) => void;
}

const Ask: React.FC<AskProps> = ({
  repoInfo,
  projects = [],
  provider = '',
  model = '',
  isCustomModel = false,
  customModel = '',
  language = 'en',
  onRef
}) => {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [deepResearch, setDeepResearch] = useState(false);

  // Multi-repository state
  const [currentRepoInfo, setCurrentRepoInfo] = useState(repoInfo);
  const [selectedRepositories, setSelectedRepositories] = useState<string[]>([]);

  // Initialize selected repositories when repoInfo changes
  useEffect(() => {
    if (Array.isArray(repoInfo)) {
      setSelectedRepositories(repoInfo.map(repo => getRepoUrl(repo)));
    } else {
      setSelectedRepositories([getRepoUrl(repoInfo)]);
    }
  }, [repoInfo]);

  // Helper functions for URL parsing
  const extractOwnerFromUrl = (url: string): string => {
    try {
      const urlObj = new URL(url);
      const pathParts = urlObj.pathname.split('/').filter(part => part);
      return pathParts[0] || 'unknown';
    } catch {
      return 'unknown';
    }
  };

  const extractRepoFromUrl = (url: string): string => {
    try {
      const urlObj = new URL(url);
      const pathParts = urlObj.pathname.split('/').filter(part => part);
      return pathParts[1] || 'unknown';
    } catch {
      return 'unknown';
    }
  };

  const extractTypeFromUrl = (url: string): string => {
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

  // Model selection state
  const [selectedProvider, setSelectedProvider] = useState(provider);
  const [selectedModel, setSelectedModel] = useState(model);
  const [isCustomSelectedModel, setIsCustomSelectedModel] = useState(isCustomModel);
  const [customSelectedModel, setCustomSelectedModel] = useState(customModel);
  const [isModelSelectionModalOpen, setIsModelSelectionModalOpen] = useState(false);
  const [isComprehensiveView, setIsComprehensiveView] = useState(true);

  // Get language context for translations
  const { messages } = useLanguage();

  // Research navigation state
  const [researchStages, setResearchStages] = useState<ResearchStage[]>([]);
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [conversationHistory, setConversationHistory] = useState<Message[]>([]);
  const [researchIteration, setResearchIteration] = useState(0);
  const [researchComplete, setResearchComplete] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const responseRef = useRef<HTMLDivElement>(null);
  const providerRef = useRef(provider);
  const modelRef = useRef(model);

  // Focus input on component mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Expose clearConversation method to parent component
  useEffect(() => {
    if (onRef) {
      onRef({ clearConversation });
    }
  }, [onRef]);

  // Scroll to bottom of response when it changes
  useEffect(() => {
    if (responseRef.current) {
      responseRef.current.scrollTop = responseRef.current.scrollHeight;
    }
  }, [response]);

  // Close WebSocket when component unmounts
  useEffect(() => {
    return () => {
      closeWebSocket(webSocketRef.current);
    };
  }, []);

  useEffect(() => {
    providerRef.current = provider;
    modelRef.current = model;
  }, [provider, model]);

  useEffect(() => {
    const fetchModel = async () => {
      try {
        setIsLoading(true);

        const response = await fetch('/api/models/config');
        if (!response.ok) {
          throw new Error(`Error fetching model configurations: ${response.status}`);
        }

        const data = await response.json();

        // use latest provider/model ref to check
        if(providerRef.current == '' || modelRef.current== '') {
          setSelectedProvider(data.defaultProvider);

          // Find the default provider and set its default model
          const selectedProvider = data.providers.find((p:Provider) => p.id === data.defaultProvider);
          if (selectedProvider) {
            // Use the provider's default model if available, otherwise fall back to first model
            const defaultModel = selectedProvider.defaultModel || 
              (selectedProvider.models.length > 0 ? selectedProvider.models[0].id : '');
            if (defaultModel) {
              setSelectedModel(defaultModel);
            }
          }
        } else {
          setSelectedProvider(providerRef.current);
          setSelectedModel(modelRef.current);
        }
      } catch (err) {
        console.error('Failed to fetch model configurations:', err);
      } finally {
        setIsLoading(false);
      }
    };
    if(provider == '' || model == '') {
      fetchModel()
    }
  }, [provider, model]);

  const clearConversation = () => {
    setQuestion('');
    setResponse('');
    setConversationHistory([]);
    setResearchIteration(0);
    setResearchComplete(false);
    setResearchStages([]);
    setCurrentStageIndex(0);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };
  const downloadresponse = () =>{
  const blob = new Blob([response], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `response-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

  // Function to check if research is complete based on response content
  const checkIfResearchComplete = (content: string): boolean => {
    // Check for explicit final conclusion markers
    if (content.includes('## Final Conclusion')) {
      return true;
    }

    // Check for conclusion sections that don't indicate further research
    if ((content.includes('## Conclusion') || content.includes('## Summary')) &&
      !content.includes('I will now proceed to') &&
      !content.includes('Next Steps') &&
      !content.includes('next iteration')) {
      return true;
    }

    // Check for phrases that explicitly indicate completion
    if (content.includes('This concludes our research') ||
      content.includes('This completes our investigation') ||
      content.includes('This concludes the deep research process') ||
      content.includes('Key Findings and Implementation Details') ||
      content.includes('In conclusion,') ||
      (content.includes('Final') && content.includes('Conclusion'))) {
      return true;
    }

    // Check for topic-specific completion indicators
    if (content.includes('Dockerfile') &&
      (content.includes('This Dockerfile') || content.includes('The Dockerfile')) &&
      !content.includes('Next Steps') &&
      !content.includes('In the next iteration')) {
      return true;
    }

    return false;
  };

  // Function to extract research stages from the response
  const extractResearchStage = (content: string, iteration: number): ResearchStage | null => {
    // Check for research plan (first iteration)
    if (iteration === 1 && content.includes('## Research Plan')) {
      const planMatch = content.match(/## Research Plan([\s\S]*?)(?:## Next Steps|$)/);
      if (planMatch) {
        return {
          title: 'Research Plan',
          content: content,
          iteration: 1,
          type: 'plan'
        };
      }
    }

    // Check for research updates (iterations 1-4)
    if (iteration >= 1 && iteration <= 4) {
      const updateMatch = content.match(new RegExp(`## Research Update ${iteration}([\\s\\S]*?)(?:## Next Steps|$)`));
      if (updateMatch) {
        return {
          title: `Research Update ${iteration}`,
          content: content,
          iteration: iteration,
          type: 'update'
        };
      }
    }

    // Check for final conclusion
    if (content.includes('## Final Conclusion')) {
      const conclusionMatch = content.match(/## Final Conclusion([\s\S]*?)$/);
      if (conclusionMatch) {
        return {
          title: 'Final Conclusion',
          content: content,
          iteration: iteration,
          type: 'conclusion'
        };
      }
    }

    return null;
  };

  // Function to navigate to a specific research stage
  const navigateToStage = (index: number) => {
    if (index >= 0 && index < researchStages.length) {
      setCurrentStageIndex(index);
      setResponse(researchStages[index].content);
    }
  };

  // Function to navigate to the next research stage
  const navigateToNextStage = () => {
    if (currentStageIndex < researchStages.length - 1) {
      navigateToStage(currentStageIndex + 1);
    }
  };

  // Function to navigate to the previous research stage
  const navigateToPreviousStage = () => {
    if (currentStageIndex > 0) {
      navigateToStage(currentStageIndex - 1);
    }
  };

  // WebSocket reference
  const webSocketRef = useRef<WebSocket | null>(null);

  // Function to continue research automatically
  const continueResearch = async () => {
    if (!deepResearch || researchComplete || !response || isLoading) return;

    // Add a small delay to allow the user to read the current response
    await new Promise(resolve => setTimeout(resolve, 2000));

    setIsLoading(true);

    try {
      // Store the current response for use in the history
      const currentResponse = response;

      // Create a new message from the AI's previous response
      const newHistory: Message[] = [
        ...conversationHistory,
        {
          role: 'assistant',
          content: currentResponse
        },
        {
          role: 'user',
          content: '[DEEP RESEARCH] Continue the research'
        }
      ];

      // Update conversation history
      setConversationHistory(newHistory);

      // Increment research iteration
      const newIteration = researchIteration + 1;
      setResearchIteration(newIteration);

      // Clear previous response
      setResponse('');

      // Prepare the request body
      const requestBody: ChatCompletionRequest = {
        repo_url: Array.isArray(currentRepoInfo) 
          ? currentRepoInfo.map(repo => getRepoUrl(repo))
          : getRepoUrl(currentRepoInfo),
        type: Array.isArray(currentRepoInfo) ? currentRepoInfo[0]?.type || 'github' : currentRepoInfo.type,
        messages: newHistory.map(msg => ({ role: msg.role as 'user' | 'assistant', content: msg.content })),
        provider: selectedProvider,
        model: isCustomSelectedModel ? customSelectedModel : selectedModel,
        language: language
      };

      // Add tokens if available (use first token for multiple repos, or single token for single repo)
      if (Array.isArray(currentRepoInfo) && currentRepoInfo.length > 0 && currentRepoInfo[0]?.token) {
        requestBody.token = currentRepoInfo[0].token;
      } else if (!Array.isArray(currentRepoInfo) && currentRepoInfo?.token) {
        requestBody.token = currentRepoInfo.token;
      }

      // Close any existing WebSocket connection
      closeWebSocket(webSocketRef.current);

      let fullResponse = '';

      // Create a new WebSocket connection
      webSocketRef.current = createChatWebSocket(
        requestBody,
        // Message handler
        (message: string) => {
          // Filter out progress/error JSON control messages just in case
          const controlRegex = /\{\s*"type"\s*:\s*"(?:progress|error)"[\s\S]*?\}/g;
          const cleaned = (message || '').replace(controlRegex, '');
          try {
            const maybeJson = JSON.parse(cleaned);
            if (maybeJson && typeof maybeJson === 'object' && 'type' in maybeJson) {
              const t = String(maybeJson.type);
              if (t === 'progress' || t === 'error') {
                return; // ignore control frames
              }
            }
          } catch {
            // not JSON, proceed
          }
          if (cleaned && cleaned.trim().length > 0) {
            fullResponse += cleaned;
          }
          setResponse(fullResponse);

          // Extract research stage if this is a deep research response
          if (deepResearch) {
            const stage = extractResearchStage(fullResponse, newIteration);
            if (stage) {
              // Add the stage to the research stages if it's not already there
              setResearchStages(prev => {
                // Check if we already have this stage
                const existingStageIndex = prev.findIndex(s => s.iteration === stage.iteration && s.type === stage.type);
                if (existingStageIndex >= 0) {
                  // Update existing stage
                  const newStages = [...prev];
                  newStages[existingStageIndex] = stage;
                  return newStages;
                } else {
                  // Add new stage
                  return [...prev, stage];
                }
              });

              // Update current stage index to the latest stage
              setCurrentStageIndex(researchStages.length);
            }
          }
        },
        // Error handler
        (error: Event) => {
          console.error('WebSocket error:', error);
          setResponse(prev => prev + '\n\nError: WebSocket connection failed. Falling back to HTTP...');

          // Fallback to HTTP if WebSocket fails
          fallbackToHttp(requestBody);
        },
        // Close handler
        () => {
          // Check if research is complete when the WebSocket closes
          const isComplete = checkIfResearchComplete(fullResponse);

          // Force completion after a maximum number of iterations (5)
          const forceComplete = newIteration >= 5;

          if (forceComplete && !isComplete) {
            // If we're forcing completion, append a comprehensive conclusion to the response
            const completionNote = "\n\n## Final Conclusion\nAfter multiple iterations of deep research, we've gathered significant insights about this topic. This concludes our investigation process, having reached the maximum number of research iterations. The findings presented across all iterations collectively form our comprehensive answer to the original question.";
            fullResponse += completionNote;
            setResponse(fullResponse);
            setResearchComplete(true);
          } else {
            setResearchComplete(isComplete);
          }

          setIsLoading(false);
          // Close the WebSocket connection after processing is complete
          closeWebSocket(webSocketRef.current);
        }
      );
    } catch (error) {
      console.error('Error during API call:', error);
      setResponse(prev => prev + '\n\nError: Failed to continue research. Please try again.');
      setResearchComplete(true);
      setIsLoading(false);
    }
  };

  // Fallback to HTTP if WebSocket fails
  const fallbackToHttp = async (requestBody: ChatCompletionRequest) => {
    try {
      // Make the API call using HTTP
      const apiResponse = await fetch(`/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!apiResponse.ok) {
        throw new Error(`API error: ${apiResponse.status}`);
      }

      // Process the streaming response
      const reader = apiResponse.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Failed to get response reader');
      }

      // Read the stream
      let fullResponse = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        fullResponse += chunk;
        setResponse(fullResponse);

        // Extract research stage if this is a deep research response
        if (deepResearch) {
          const stage = extractResearchStage(fullResponse, researchIteration);
          if (stage) {
            // Add the stage to the research stages
            setResearchStages(prev => {
              const existingStageIndex = prev.findIndex(s => s.iteration === stage.iteration && s.type === stage.type);
              if (existingStageIndex >= 0) {
                const newStages = [...prev];
                newStages[existingStageIndex] = stage;
                return newStages;
              } else {
                return [...prev, stage];
              }
            });
          }
        }
      }

      // Check if research is complete
      const isComplete = checkIfResearchComplete(fullResponse);

      // Force completion after a maximum number of iterations (5)
      const forceComplete = researchIteration >= 5;

      if (forceComplete && !isComplete) {
        // If we're forcing completion, append a comprehensive conclusion to the response
        const completionNote = "\n\n## Final Conclusion\nAfter multiple iterations of deep research, we've gathered significant insights about this topic. This concludes our investigation process, having reached the maximum number of research iterations. The findings presented across all iterations collectively form our comprehensive answer to the original question.";
        fullResponse += completionNote;
        setResponse(fullResponse);
        setResearchComplete(true);
      } else {
        setResearchComplete(isComplete);
      }
    } catch (error) {
      console.error('Error during HTTP fallback:', error);
      setResponse(prev => prev + '\n\nError: Failed to get a response. Please try again.');
      setResearchComplete(true);
    } finally {
      setIsLoading(false);
    }
  };

  // Effect to continue research when response is updated
  useEffect(() => {
    if (deepResearch && response && !isLoading && !researchComplete) {
      const isComplete = checkIfResearchComplete(response);
      if (isComplete) {
        setResearchComplete(true);
      } else if (researchIteration > 0 && researchIteration < 5) {
        // Only auto-continue if we're already in a research process and haven't reached max iterations
        // Use setTimeout to avoid potential infinite loops
        const timer = setTimeout(() => {
          continueResearch();
        }, 1000);
        return () => clearTimeout(timer);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [response, isLoading, deepResearch, researchComplete, researchIteration]);

  // Effect to update research stages when the response changes
  useEffect(() => {
    if (deepResearch && response && !isLoading) {
      // Try to extract a research stage from the response
      const stage = extractResearchStage(response, researchIteration);
      if (stage) {
        // Add or update the stage in the research stages
        setResearchStages(prev => {
          // Check if we already have this stage
          const existingStageIndex = prev.findIndex(s => s.iteration === stage.iteration && s.type === stage.type);
          if (existingStageIndex >= 0) {
            // Update existing stage
            const newStages = [...prev];
            newStages[existingStageIndex] = stage;
            return newStages;
          } else {
            // Add new stage
            return [...prev, stage];
          }
        });

        // Update current stage index to point to this stage
        setCurrentStageIndex(prev => {
          const newIndex = researchStages.findIndex(s => s.iteration === stage.iteration && s.type === stage.type);
          return newIndex >= 0 ? newIndex : prev;
        });
      }
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [response, isLoading, deepResearch, researchIteration]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!question.trim() || isLoading) return;

    handleConfirmAsk();
  };

  // Handle confirm and send request
  const handleConfirmAsk = async () => {
    setIsLoading(true);
    setResponse('');
    setResearchIteration(0);
    setResearchComplete(false);

    try {
      // Create initial message
      const initialMessage: Message = {
        role: 'user',
        content: deepResearch ? `[DEEP RESEARCH] ${question}` : question
      };

      // Set initial conversation history
      const newHistory: Message[] = [initialMessage];
      setConversationHistory(newHistory);

      // Prepare request body
      const requestBody: ChatCompletionRequest = {
        repo_url: Array.isArray(currentRepoInfo) 
          ? currentRepoInfo.map(repo => getRepoUrl(repo))
          : getRepoUrl(currentRepoInfo),
        type: Array.isArray(currentRepoInfo) ? currentRepoInfo[0]?.type || 'github' : currentRepoInfo.type,
        messages: newHistory.map(msg => ({ role: msg.role as 'user' | 'assistant', content: msg.content })),
        provider: selectedProvider,
        model: isCustomSelectedModel ? customSelectedModel : selectedModel,
        language: language
      };

      // Add tokens if available (use first token for multiple repos, or single token for single repo)
      if (Array.isArray(currentRepoInfo) && currentRepoInfo.length > 0 && currentRepoInfo[0]?.token) {
        requestBody.token = currentRepoInfo[0].token;
      } else if (!Array.isArray(currentRepoInfo) && currentRepoInfo?.token) {
        requestBody.token = currentRepoInfo.token;
      }

      // Close any existing WebSocket connection
      closeWebSocket(webSocketRef.current);

      let fullResponse = '';

      // Create a new WebSocket connection
      webSocketRef.current = createChatWebSocket(
        requestBody,
        // Message handler
        (message: string) => {
          const controlRegex = /\{\s*"type"\s*:\s*"(?:progress|error)"[\s\S]*?\}/g;
          const cleaned = (message || '').replace(controlRegex, '');
          try {
            const maybeJson = JSON.parse(cleaned);
            if (maybeJson && typeof maybeJson === 'object' && 'type' in maybeJson) {
              const t = String(maybeJson.type);
              if (t === 'progress' || t === 'error') {
                return;
              }
            }
          } catch {}
          if (cleaned && cleaned.trim().length > 0) {
            fullResponse += cleaned;
          }
          setResponse(fullResponse);

          // Extract research stage if this is a deep research response
          if (deepResearch) {
            const stage = extractResearchStage(fullResponse, 1); // First iteration
            if (stage) {
              // Add the stage to the research stages
              setResearchStages([stage]);
              setCurrentStageIndex(0);
            }
          }
        },
        // Error handler
        (error: Event) => {
          console.error('WebSocket error:', error);
          setResponse(prev => prev + '\n\nError: WebSocket connection failed. Falling back to HTTP...');

          // Fallback to HTTP if WebSocket fails
          fallbackToHttp(requestBody);
        },
        // Close handler
        () => {
          // If deep research is enabled, check if we should continue
          if (deepResearch) {
            const isComplete = checkIfResearchComplete(fullResponse);
            setResearchComplete(isComplete);

            // If not complete, start the research process
            if (!isComplete) {
              setResearchIteration(1);
              // The continueResearch function will be triggered by the useEffect
            }
          }

          setIsLoading(false);
          // Close the WebSocket connection after processing is complete
          closeWebSocket(webSocketRef.current);
        }
      );
    } catch (error) {
      console.error('Error during API call:', error);
      setResponse(prev => prev + '\n\nError: Failed to get a response. Please try again.');
      setResearchComplete(true);
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Model Selection Header - Fixed at top */}
      <div className="p-4 border-b border-[var(--border-color)] bg-[var(--card-bg)] flex-shrink-0">
        <div className="flex items-center justify-end">
          <button
            type="button"
            onClick={() => setIsModelSelectionModalOpen(true)}
            className="text-xs px-2.5 py-1 rounded border border-[var(--border-color)]/40 bg-[var(--background)]/10 text-[var(--foreground)]/80 hover:bg-[var(--background)]/30 hover:text-[var(--foreground)] transition-colors flex items-center gap-1.5"
          >
            <span>{selectedProvider}/{isCustomSelectedModel ? customSelectedModel : selectedModel}</span>
            <svg className="h-3.5 w-3.5 text-[var(--accent-primary)]/70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
        </div>
      </div>

      {/* Conversation Area - Scrollable */}
      <div className="flex-1 overflow-y-auto">
        {/* Response/Conversation History */}
        {response ? (
          <div className="p-4">
            <div ref={responseRef}>
              <Markdown content={response} />
            </div>

            {/* Research Navigation */}
            {deepResearch && researchStages.length > 1 && (
              <div className="flex items-center space-x-2 mt-4 p-3 bg-[var(--background)] rounded-lg border border-[var(--border-color)]">
                <button
                  onClick={() => navigateToPreviousStage()}
                  disabled={currentStageIndex === 0}
                  className={`p-1 rounded-md ${currentStageIndex === 0 ? 'text-gray-400 dark:text-gray-600' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'}`}
                  aria-label="Previous stage"
                >
                  <FaChevronLeft size={12} />
                </button>

                <div className="text-xs text-gray-600 dark:text-gray-400">
                  {currentStageIndex + 1} / {researchStages.length}
                </div>

                <button
                  onClick={() => navigateToNextStage()}
                  disabled={currentStageIndex === researchStages.length - 1}
                  className={`p-1 rounded-md ${currentStageIndex === researchStages.length - 1 ? 'text-gray-400 dark:text-gray-600' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'}`}
                  aria-label="Next stage"
                >
                  <FaChevronRight size={12} />
                </button>

                <div className="text-xs text-gray-600 dark:text-gray-400 ml-2">
                  {researchStages[currentStageIndex]?.title || `Stage ${currentStageIndex + 1}`}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center space-x-2 mt-4">
              <button
                onClick={downloadresponse}
                className="text-xs px-3 py-1.5 bg-[var(--background)] border border-[var(--border-color)] text-[var(--foreground)] rounded-md hover:bg-[var(--background)]/80 transition-colors flex items-center gap-1.5"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download
              </button>
              <button
                onClick={clearConversation}
                className="text-xs px-3 py-1.5 bg-[var(--background)] border border-[var(--border-color)] text-[var(--foreground)] rounded-md hover:bg-[var(--background)]/80 transition-colors flex items-center gap-1.5"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Clear
              </button>
            </div>
          </div>
        ) : (
          // Empty state when no conversation
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center max-w-md">
              <div className="text-4xl mb-4 text-[var(--muted)]">💭</div>
              <h3 className="text-lg font-semibold text-[var(--foreground)] mb-2">
                Ask anything about your codebase
              </h3>
              <p className="text-[var(--muted)] text-sm">
                Start a conversation by typing your question below. I can help you understand code structure, find implementations, and explain complex logic.
              </p>
            </div>
          </div>
        )}

        {/* Loading Animation */}
        {isLoading && (
          <div className="p-4 border-t border-[var(--border-color)]">
            <div className="flex items-center space-x-3 text-[var(--muted)]">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-[var(--accent-primary)] rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-[var(--accent-primary)] rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                <div className="w-2 h-2 bg-[var(--accent-primary)] rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
              </div>
              <span className="text-sm">Thinking...</span>
            </div>

            {/* Deep Research Progress */}
            {deepResearch && researchIteration > 0 && (
              <div className="mt-3 space-y-2">
                <div className="text-xs text-[var(--muted)] space-y-1">
                  {researchIteration >= 1 && (
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                      <span>Analyzing codebase structure...</span>
                    </div>
                  )}
                  {researchIteration >= 2 && (
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                      <span>Researching related components...</span>
                    </div>
                  )}
                  {researchIteration >= 3 && (
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-orange-500 rounded-full mr-2"></div>
                      <span>Deep diving into implementation details...</span>
                    </div>
                  )}
                  {researchIteration >= 4 && (
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-red-500 rounded-full mr-2"></div>
                      <span>Cross-referencing documentation...</span>
                    </div>
                  )}
                  {researchIteration >= 5 && (
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                      <span>Finalizing comprehensive answer...</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Fixed Input Form at Bottom */}
      <div className="border-t border-[var(--border-color)] bg-[var(--card-bg)] p-4 flex-shrink-0">
        <form onSubmit={handleSubmit} className="space-y-3">
          {/* Input Field */}
          <div className="relative">
            <input
              ref={inputRef}
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder={messages.ask?.placeholder || 'Ask about this repository...'}
              className="block w-full rounded-lg border border-[var(--border-color)] bg-[var(--background)] text-[var(--foreground)] px-4 py-3 pr-16 text-sm focus:border-[var(--accent-primary)] focus:ring-2 focus:ring-[var(--accent-primary)]/20 focus:outline-none transition-all resize-none"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !question.trim()}
              className={`absolute right-2 top-1/2 transform -translate-y-1/2 p-2 rounded-md ${
                isLoading || !question.trim()
                  ? 'bg-[var(--muted)] text-[var(--background)] cursor-not-allowed'
                  : 'bg-[var(--accent-primary)] text-white hover:bg-[var(--accent-primary)]/90'
              } transition-all duration-200`}
            >
              {isLoading ? (
                <div className="w-4 h-4 rounded-full border-2 border-t-transparent border-white animate-spin" />
              ) : (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </button>
          </div>

          {/* Options Row */}
          <div className="flex items-center justify-between text-xs">
            {/* Deep Research Toggle */}
            <div className="flex items-center space-x-4">
              <label className="flex items-center cursor-pointer">
                <span className="text-[var(--muted)] mr-2">Deep Research</span>
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={deepResearch}
                    onChange={() => setDeepResearch(!deepResearch)}
                    className="sr-only"
                  />
                  <div className={`w-10 h-5 rounded-full transition-colors ${deepResearch ? 'bg-purple-600' : 'bg-gray-300 dark:bg-gray-600'}`}></div>
                  <div className={`absolute left-0.5 top-0.5 w-4 h-4 rounded-full bg-white transition-transform transform ${deepResearch ? 'translate-x-5' : ''}`}></div>
                </div>
              </label>
              <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded p-2 w-72 z-10">
                <div className="relative">
                  <div className="absolute -bottom-2 left-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-800"></div>
                  <p className="mb-1">Deep Research conducts a multi-turn investigation process:</p>
                  <ul className="list-disc pl-4 text-xs">
                    <li><strong>Initial Research:</strong> Creates a research plan and initial findings</li>
                    <li><strong>Iteration 1:</strong> Explores specific aspects in depth</li>
                    <li><strong>Iteration 2:</strong> Investigates remaining questions</li>
                    <li><strong>Iterations 3-4:</strong> Dives deeper into complex areas</li>
                    <li><strong>Final Conclusion:</strong> Comprehensive answer based on all iterations</li>
                  </ul>
                  <p className="mt-1 text-xs italic">The AI automatically continues research until complete (up to 5 iterations)</p>
                </div>
              </div>
            </div>
            {deepResearch && (
              <div className="text-xs text-purple-600 dark:text-purple-400">
                Multi-turn research process enabled
                {researchIteration > 0 && !researchComplete && ` (iteration ${researchIteration})`}
                {researchComplete && ` (complete)`}
              </div>
            )}
          </div>

          {/* Multi-Repository toggle and input */}
          <div className="flex items-center mt-2 justify-between">
            <div className="group relative">
              <label className="flex items-center cursor-pointer">
                <span className="text-xs text-gray-600 dark:text-gray-400 mr-2">Multi-Repository</span>
                <div className="relative">
                                  <input
                  type="checkbox"
                  checked={Array.isArray(currentRepoInfo)}
                  onChange={() => {
                    if (Array.isArray(currentRepoInfo)) {
                      // Switch to single repository mode
                      setCurrentRepoInfo(currentRepoInfo[0] || currentRepoInfo);
                    } else {
                      // Switch to multi-repository mode
                      setCurrentRepoInfo([currentRepoInfo]);
                    }
                  }}
                    className="sr-only"
                  />
                  <div className={`w-10 h-5 rounded-full transition-colors ${Array.isArray(currentRepoInfo) ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'}`}></div>
                  <div className={`absolute left-0.5 top-0.5 w-4 h-4 rounded-full bg-white transition-transform transform ${Array.isArray(currentRepoInfo) ? 'translate-x-5' : ''}`}></div>
                </div>
              </label>
              <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded p-2 w-72 z-10">
                <div className="relative">
                  <div className="absolute -bottom-2 left-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-800"></div>
                  <p className="mb-1">Multi-Repository mode allows you to query multiple repositories simultaneously:</p>
                  <ul className="list-disc pl-4 text-xs">
                    <li><strong>Single Mode:</strong> Query one repository at a time</li>
                    <li><strong>Multi Mode:</strong> Query multiple repositories and get combined results</li>
                    <li><strong>Smart Merging:</strong> Results are intelligently combined from all repositories</li>
                  </ul>
                  <p className="mt-1 text-xs italic">Toggle to switch between single and multiple repository modes</p>
                </div>
              </div>
            </div>
            {Array.isArray(currentRepoInfo) && (
              <div className="text-xs text-blue-600 dark:text-blue-400">
                Multi-repository mode enabled ({currentRepoInfo.length} repos)
              </div>
            )}
          </div>

          {/* Multi-repository input fields */}
          {Array.isArray(currentRepoInfo) && (
            <div className="mt-3 space-y-2">
              <MultiRepositorySelector
                projects={projects}
                selectedRepositories={selectedRepositories}
                onRepositoriesChange={(repos) => {
                  setSelectedRepositories(repos);
                  // Convert URLs back to RepoInfo objects for the existing logic
                  const newRepos = repos.map(url => ({
                    owner: extractOwnerFromUrl(url),
                    repo: extractRepoFromUrl(url),
                    type: extractTypeFromUrl(url),
                    token: currentRepoInfo[0]?.token || null,
                    localPath: null,
                    repoUrl: url.trim()
                  }));
                  setCurrentRepoInfo(newRepos);
                }}
                placeholder="Search and select repositories..."
                disabled={isLoading}
              />
            </div>
          )}
        </form>
      </div>

      {/* Model Selection Modal */}
      <ModelSelectionModal
        isOpen={isModelSelectionModalOpen}
        onClose={() => setIsModelSelectionModalOpen(false)}
        provider={selectedProvider}
        setProvider={setSelectedProvider}
        model={selectedModel}
        setModel={setSelectedModel}
        isCustomModel={isCustomSelectedModel}
        setIsCustomModel={setIsCustomSelectedModel}
        customModel={customSelectedModel}
        setCustomModel={setCustomSelectedModel}
        isComprehensiveView={isComprehensiveView}
        setIsComprehensiveView={setIsComprehensiveView}
        showFileFilters={false}
        onApply={() => {
          console.log('Model selection applied:', selectedProvider, selectedModel);
        }}
        showWikiType={false}
        authRequired={false}
        isAuthLoading={false}
      />
    </div>
  );
};

export default Ask;
