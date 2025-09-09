'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import RepoInfo from '@/types/repoinfo';
import getRepoUrl from '@/utils/getRepoUrl';
import { ProcessedProject } from '@/types/shared';

// Hooks
import { useChatWebSocket } from '@/hooks/useChatWebSocket';
import { useResearchMode } from '@/hooks/useResearchMode';
import { useModelConfiguration } from '@/hooks/useModelConfiguration';

// Components
import MessageList from './components/ChatInterface/MessageList';
import MessageInput from './components/ChatInterface/MessageInput';
import ActionButtons from './components/ChatInterface/ActionButtons';
import ResearchNavigation from './components/ResearchMode/ResearchNavigation';
import ResearchToggle from './components/ResearchMode/ResearchToggle';
import ModelSelectionModal from '@/components/ModelSelectionModal';

// Note: MultiRepositorySelector and parseRepositoryUrl will be used in future iterations
import { ChatCompletionRequest } from '@/utils/websocketClient';

interface AskProps {
  repoInfo: RepoInfo | RepoInfo[];
  projects?: ProcessedProject[];
  provider?: string;
  model?: string;
  isCustomModel?: boolean;
  customModel?: string;
  language?: string;
  onRef?: (ref: { clearConversation: () => void }) => void;
  onMultiRepositoryModeChange?: (enabled: boolean) => void;
}

const Ask: React.FC<AskProps> = ({
  repoInfo,
  projects: _projects = [], // eslint-disable-line @typescript-eslint/no-unused-vars
  provider = '',
  model = '',
  isCustomModel = false,
  customModel = '',
  language = 'en',
  onRef,
  onMultiRepositoryModeChange: _onMultiRepositoryModeChange // eslint-disable-line @typescript-eslint/no-unused-vars
}) => {
  // State
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentRepoInfo] = useState(repoInfo);
  const [selectedRepositories, setSelectedRepositories] = useState<string[]>([]); // eslint-disable-line @typescript-eslint/no-unused-vars
  const [isModelSelectionModalOpen, setIsModelSelectionModalOpen] = useState(false);
  
  // Refs
  const inputRef = useRef<HTMLInputElement>(null);
  
  // Hooks
  const { messages } = useLanguage();
  const webSocket = useChatWebSocket();
  const research = useResearchMode();
  const modelConfig = useModelConfiguration({ provider, model, isCustomModel, customModel });

  // Clear conversation callback - defined early for use in other effects
  const clearConversation = useCallback(() => {
    setQuestion('');
    setResponse('');
    research.resetResearch();
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, [research]);

  // Initialize selected repositories when repoInfo changes
  useEffect(() => {
    if (Array.isArray(repoInfo)) {
      setSelectedRepositories(repoInfo.map(repo => getRepoUrl(repo)));
    } else {
      setSelectedRepositories([getRepoUrl(repoInfo)]);
    }
  }, [repoInfo]);

  // Expose clearConversation method to parent component
  useEffect(() => {
    if (onRef) {
      onRef({ clearConversation });
    }
  }, [onRef, clearConversation]);

  // Focus input on component mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const downloadResponse = () => {
    const blob = new Blob([response], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `response-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleSubmit = () => {
    if (!question.trim() || isLoading) return;

    setIsLoading(true);
    setResponse('');
    research.resetResearch();

    // Create request body
    const requestBody: ChatCompletionRequest = {
      repo_url: Array.isArray(currentRepoInfo) 
        ? currentRepoInfo.map(repo => getRepoUrl(repo))
        : getRepoUrl(currentRepoInfo),
      type: Array.isArray(currentRepoInfo) ? currentRepoInfo[0]?.type || 'github' : currentRepoInfo.type,
      messages: [{ 
        role: 'user' as const, 
        content: research.researchState.isEnabled ? `[DEEP RESEARCH] ${question}` : question 
      }],
      provider: modelConfig.config.selectedProvider,
      model: modelConfig.effectiveModel,
      language: language
    };

    // Add token if available
    if (Array.isArray(currentRepoInfo) && currentRepoInfo.length > 0 && currentRepoInfo[0]?.token) {
      requestBody.token = currentRepoInfo[0].token;
    } else if (!Array.isArray(currentRepoInfo) && currentRepoInfo?.token) {
      requestBody.token = currentRepoInfo.token;
    }

    let fullResponse = '';

    // Connect WebSocket
    webSocket.connect(requestBody, {
      onMessage: (message: string) => {
        const controlRegex = /\{\s*"type"\s*:\s*"(?:progress|error)"[\s\S]*?\}/g;
        const cleaned = (message || '').replace(controlRegex, '');
        
        if (cleaned && cleaned.trim().length > 0) {
          fullResponse += cleaned;
          setResponse(fullResponse);
          
          // Update research stage if enabled
          if (research.researchState.isEnabled) {
            research.updateResearchStage(fullResponse, 1);
          }
        }
      },
      onError: (error: Event) => {
        console.error('WebSocket error:', error);
        setResponse(prev => prev + '\n\nError: Connection failed. Please try again.');
        setIsLoading(false);
      },
      onClose: () => {
        setIsLoading(false);
      }
    });
  };

  return (
    <div className="h-full flex flex-col">
      {/* Model Selection Header */}
      <div className="p-4 border-b border-[var(--border-color)] bg-[var(--card-bg)] flex-shrink-0">
        <div className="flex items-center justify-end">
          <button
            type="button"
            onClick={() => setIsModelSelectionModalOpen(true)}
            className="text-xs px-2.5 py-1 rounded border border-[var(--border-color)]/40 bg-[var(--background)]/10 text-[var(--foreground)]/80 hover:bg-[var(--background)]/30 hover:text-[var(--foreground)] transition-colors flex items-center gap-1.5"
          >
            <span>{modelConfig.config.selectedProvider}/{modelConfig.effectiveModel}</span>
            <svg className="h-3.5 w-3.5 text-[var(--accent-primary)]/70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
        </div>
      </div>

      {/* Message List */}
      <MessageList 
        response={response}
        isLoading={isLoading}
        isEmpty={!response}
      />

      {/* Research Navigation */}
      {research.researchState.isEnabled && (
        <div className="px-4">
          <ResearchNavigation
            stages={research.researchState.stages}
            currentStageIndex={research.researchState.currentStageIndex}
            onNavigate={(index) => {
              research.navigateToStage(index);
              if (research.researchState.stages[index]) {
                setResponse(research.researchState.stages[index].content);
              }
            }}
          />
        </div>
      )}

      {/* Action Buttons */}
      <div className="px-4">
        <ActionButtons
          response={response}
          onDownload={downloadResponse}
          onClear={clearConversation}
        />
      </div>

      {/* Input Form */}
      <div className="border-t border-[var(--border-color)] bg-[var(--card-bg)] p-4 flex-shrink-0">
        <div className="space-y-3">
          <MessageInput
            value={question}
            onChange={setQuestion}
            onSubmit={handleSubmit}
            placeholder={messages.ask?.placeholder || 'Ask about this repository...'}
            disabled={isLoading}
            isLoading={isLoading}
          />
          
          <ResearchToggle
            enabled={research.researchState.isEnabled}
            onToggle={research.toggleResearch}
            isComplete={research.researchState.isComplete}
            iteration={research.researchState.iteration}
          />
        </div>
      </div>

      {/* Model Selection Modal */}
      <ModelSelectionModal
        isOpen={isModelSelectionModalOpen}
        onClose={() => setIsModelSelectionModalOpen(false)}
        provider={modelConfig.config.selectedProvider}
        setProvider={modelConfig.updateProvider}
        model={modelConfig.config.selectedModel}
        setModel={modelConfig.updateModel}
        isCustomModel={modelConfig.config.isCustomModel}
        setIsCustomModel={modelConfig.toggleCustomModel}
        customModel={modelConfig.config.customModel}
        setCustomModel={modelConfig.updateCustomModel}
        isComprehensiveView={modelConfig.config.isComprehensiveView}
        setIsComprehensiveView={modelConfig.updateComprehensiveView}
        showFileFilters={false}
        onApply={() => {
          console.log('Model selection applied:', modelConfig.config.selectedProvider, modelConfig.effectiveModel);
        }}
        showWikiType={false}
        authRequired={false}
        isAuthLoading={false}
      />
    </div>
  );
};

export default Ask;
