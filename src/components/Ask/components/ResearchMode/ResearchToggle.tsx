'use client';

import React from 'react';

interface ResearchToggleProps {
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
  isComplete?: boolean;
  iteration?: number;
}

const ResearchToggle: React.FC<ResearchToggleProps> = ({
  enabled,
  onToggle,
  isComplete = false,
  iteration = 0
}) => {
  return (
    <div className="flex items-center justify-between text-xs">
      {/* Deep Research Toggle */}
      <div className="flex items-center space-x-4">
        <label className="flex items-center cursor-pointer">
          <span className="text-[var(--muted)] mr-2">Deep Research</span>
          <div className="relative">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(e) => onToggle(e.target.checked)}
              className="sr-only"
            />
            <div className={`w-10 h-5 rounded-full transition-colors ${
              enabled ? 'bg-purple-600' : 'bg-gray-300 dark:bg-gray-600'
            }`}></div>
            <div className={`absolute left-0.5 top-0.5 w-4 h-4 rounded-full bg-white transition-transform transform ${
              enabled ? 'translate-x-5' : ''
            }`}></div>
          </div>
        </label>
        
        {/* Tooltip */}
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
      
      {/* Status Display */}
      {enabled && (
        <div className="text-xs text-purple-600 dark:text-purple-400">
          Multi-turn research process enabled
          {iteration > 0 && !isComplete && ` (iteration ${iteration})`}
          {isComplete && ` (complete)`}
        </div>
      )}
    </div>
  );
};

export default ResearchToggle;
