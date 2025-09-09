'use client';

import React from 'react';
import { FaChevronLeft, FaChevronRight } from 'react-icons/fa';
import { ResearchStage } from '@/types/shared';

interface ResearchNavigationProps {
  stages: ResearchStage[];
  currentStageIndex: number;
  onNavigate: (index: number) => void;
}

const ResearchNavigation: React.FC<ResearchNavigationProps> = ({
  stages,
  currentStageIndex,
  onNavigate
}) => {
  if (stages.length <= 1) return null;

  const canNavigatePrev = currentStageIndex > 0;
  const canNavigateNext = currentStageIndex < stages.length - 1;

  const handlePrevious = () => {
    if (canNavigatePrev) {
      onNavigate(currentStageIndex - 1);
    }
  };

  const handleNext = () => {
    if (canNavigateNext) {
      onNavigate(currentStageIndex + 1);
    }
  };

  return (
    <div className="flex items-center space-x-2 mt-4 p-3 bg-[var(--background)] rounded-lg border border-[var(--border-color)]">
      <button
        onClick={handlePrevious}
        disabled={!canNavigatePrev}
        className={`p-1 rounded-md ${
          !canNavigatePrev 
            ? 'text-gray-400 dark:text-gray-600' 
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
        }`}
        aria-label="Previous stage"
      >
        <FaChevronLeft size={12} />
      </button>

      <div className="text-xs text-gray-600 dark:text-gray-400">
        {currentStageIndex + 1} / {stages.length}
      </div>

      <button
        onClick={handleNext}
        disabled={!canNavigateNext}
        className={`p-1 rounded-md ${
          !canNavigateNext 
            ? 'text-gray-400 dark:text-gray-600' 
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
        }`}
        aria-label="Next stage"
      >
        <FaChevronRight size={12} />
      </button>

      <div className="text-xs text-gray-600 dark:text-gray-400 ml-2">
        {stages[currentStageIndex]?.title || `Stage ${currentStageIndex + 1}`}
      </div>
    </div>
  );
};

export default ResearchNavigation;
