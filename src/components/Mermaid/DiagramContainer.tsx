import React from 'react';

interface DiagramContainerProps {
  svg: string;
  isLoading: boolean;
  error: string | null;
  errorDebugInfo: {
    originalChart: string;
    cleanedChart: string;
    errorMessage: string;
    wasChartCleaned: boolean;
  } | null;
  zoomingEnabled?: boolean;
  className?: string;
  onClick?: () => void;
  containerRef?: React.RefObject<HTMLDivElement | null>;
}

const DiagramContainer: React.FC<DiagramContainerProps> = ({
  svg,
  isLoading,
  error,
  errorDebugInfo,
  zoomingEnabled = false,
  className = '',
  onClick,
  containerRef,
}) => {
  if (error) {
    return (
      <div className={`border border-[var(--highlight)]/30 rounded-md p-4 bg-[var(--highlight)]/5 ${className}`}>
        <div className="flex items-center mb-3">
          <div className="text-[var(--highlight)] text-xs font-medium flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Chart Rendering Error
          </div>
        </div>
        {errorDebugInfo && (
          <div className="text-xs overflow-auto">
            <div className="text-red-500 dark:text-red-400 text-xs mb-2">
              <strong>Chart Rendering Error</strong><br/>
              {errorDebugInfo.errorMessage}
            </div>
            <div className="text-xs mb-2">
              <strong>Original Chart:</strong>
            </div>
            <pre className="text-xs overflow-auto p-2 bg-gray-100 dark:bg-gray-800 rounded mb-2">{errorDebugInfo.originalChart}</pre>
            {errorDebugInfo.wasChartCleaned && (
              <>
                <div className="text-xs mb-2">
                  <strong>Cleaned Chart (attempted fix):</strong>
                </div>
                <pre className="text-xs overflow-auto p-2 bg-gray-100 dark:bg-gray-800 rounded">{errorDebugInfo.cleanedChart}</pre>
              </>
            )}
          </div>
        )}
        <div className="mt-3 text-xs text-[var(--muted)] font-serif">
          The chart has a syntax error and cannot be rendered.
        </div>
      </div>
    );
  }

  if (isLoading || !svg) {
    return (
      <div className={`flex justify-center items-center p-4 ${className}`}>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-[var(--accent-primary)]/70 rounded-full animate-pulse"></div>
          <div className="w-2 h-2 bg-[var(--accent-primary)]/70 rounded-full animate-pulse delay-75"></div>
          <div className="w-2 h-2 bg-[var(--accent-primary)]/70 rounded-full animate-pulse delay-150"></div>
          <span className="text-[var(--muted)] text-xs ml-2 font-serif">Rendering chart...</span>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`w-full max-w-full ${zoomingEnabled ? "h-[600px] p-4" : ""}`}
    >
      <div
        className={`relative group ${zoomingEnabled ? "h-full rounded-lg border-2 border-black" : ""}`}
      >
        <div
          className={`flex justify-center overflow-auto text-center my-2 cursor-pointer hover:shadow-md transition-shadow duration-200 rounded-md ${className} ${zoomingEnabled ? "h-full" : ""}`}
          dangerouslySetInnerHTML={{ __html: svg }}
          onClick={zoomingEnabled ? undefined : onClick}
          title={zoomingEnabled ? undefined : "Click to view fullscreen"}
        />

        {!zoomingEnabled && onClick && (
          <div className="absolute top-2 right-2 bg-gray-700/70 dark:bg-gray-900/70 text-white p-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center gap-1.5 text-xs shadow-md pointer-events-none">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              <line x1="11" y1="8" x2="11" y2="14"></line>
              <line x1="8" y1="11" x2="14" y2="11"></line>
            </svg>
            <span>Click to zoom</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default DiagramContainer;
