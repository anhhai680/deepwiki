import React, { useState } from 'react';
import DiagramContainer from './DiagramContainer';
import FullScreenModal from './FullScreenModal';
import { useMermaidRendering } from '@/hooks/useMermaidRendering';
import { useDiagramControls } from '@/hooks/useDiagramControls';

interface MermaidProps {
  chart: string;
  className?: string;
  zoomingEnabled?: boolean;
}

const Mermaid: React.FC<MermaidProps> = ({ 
  chart, 
  className = '', 
  zoomingEnabled = false 
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Use custom hooks for rendering and controls
  const { svg, error, isLoading, getErrorDebugInfo } = useMermaidRendering(chart);
  const { containerRef } = useDiagramControls(svg, zoomingEnabled);

  const handleDiagramClick = () => {
    if (!error && svg && !zoomingEnabled) {
      setIsFullscreen(true);
    }
  };

  const errorDebugInfo = getErrorDebugInfo();

  return (
    <>
      <DiagramContainer
        svg={svg}
        isLoading={isLoading}
        error={error}
        errorDebugInfo={errorDebugInfo}
        zoomingEnabled={zoomingEnabled}
        className={className}
        onClick={handleDiagramClick}
        containerRef={containerRef}
      />

      {!zoomingEnabled && (
        <FullScreenModal
          isOpen={isFullscreen}
          onClose={() => setIsFullscreen(false)}
        >
          <div dangerouslySetInnerHTML={{ __html: svg }} />
        </FullScreenModal>
      )}
    </>
  );
};

export default Mermaid;
