import { useState, useCallback } from 'react';
import { ResearchStage, ResearchState } from '@/types/shared';
import { extractResearchStage, checkIfResearchComplete } from '@/utils/shared/researchHelpers';

export const useResearchMode = () => {
  const [researchState, setResearchState] = useState<ResearchState>({
    stages: [],
    currentStageIndex: 0,
    iteration: 0,
    isComplete: false,
    isEnabled: false
  });

  const toggleResearch = useCallback((enabled: boolean) => {
    setResearchState(prev => ({
      ...prev,
      isEnabled: enabled
    }));
  }, []);

  const resetResearch = useCallback(() => {
    setResearchState({
      stages: [],
      currentStageIndex: 0,
      iteration: 0,
      isComplete: false,
      isEnabled: researchState.isEnabled
    });
  }, [researchState.isEnabled]);

  const updateResearchStage = useCallback((content: string, iteration: number) => {
    const stage = extractResearchStage(content, iteration);
    if (stage) {
      setResearchState(prev => {
        const existingStageIndex = prev.stages.findIndex(
          s => s.iteration === stage.iteration && s.type === stage.type
        );
        
        let newStages: ResearchStage[];
        if (existingStageIndex >= 0) {
          // Update existing stage
          newStages = [...prev.stages];
          newStages[existingStageIndex] = stage;
        } else {
          // Add new stage
          newStages = [...prev.stages, stage];
        }

        return {
          ...prev,
          stages: newStages,
          currentStageIndex: newStages.length - 1
        };
      });
    }

    // Check if research is complete
    const isComplete = checkIfResearchComplete(content);
    if (isComplete) {
      setResearchState(prev => ({ ...prev, isComplete: true }));
    }
  }, []);

  const navigateToStage = useCallback((index: number) => {
    setResearchState(prev => ({
      ...prev,
      currentStageIndex: Math.max(0, Math.min(index, prev.stages.length - 1))
    }));
  }, []);

  const setIteration = useCallback((iteration: number) => {
    setResearchState(prev => ({
      ...prev,
      iteration
    }));
  }, []);

  const setComplete = useCallback((complete: boolean) => {
    setResearchState(prev => ({
      ...prev,
      isComplete: complete
    }));
  }, []);

  return {
    researchState,
    toggleResearch,
    resetResearch,
    updateResearchStage,
    navigateToStage,
    setIteration,
    setComplete,
    
    // Computed properties
    canNavigateNext: researchState.currentStageIndex < researchState.stages.length - 1,
    canNavigatePrev: researchState.currentStageIndex > 0,
    currentStage: researchState.stages[researchState.currentStageIndex] || null,
    
    // Helper methods
    navigateNext: () => navigateToStage(researchState.currentStageIndex + 1),
    navigatePrev: () => navigateToStage(researchState.currentStageIndex - 1)
  };
};
