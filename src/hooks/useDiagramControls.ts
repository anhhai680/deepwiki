import { useEffect, useRef } from 'react';

export const useDiagramControls = (svg: string, zoomingEnabled: boolean) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (svg && zoomingEnabled && containerRef.current) {
      const initializePanZoom = async () => {
        const svgElement = containerRef.current?.querySelector('svg');
        if (svgElement) {
          // Remove any max-width constraints
          svgElement.style.maxWidth = 'none';
          svgElement.style.width = '100%';
          svgElement.style.height = '100%';

          try {
            // Dynamically import svg-pan-zoom only when needed in the browser
            const svgPanZoom = (await import('svg-pan-zoom')).default;

            svgPanZoom(svgElement, {
              zoomEnabled: true,
              controlIconsEnabled: true,
              fit: true,
              center: true,
              minZoom: 0.1,
              maxZoom: 10,
              zoomScaleSensitivity: 0.3,
            });
          } catch (error) {
            console.error('Failed to load svg-pan-zoom:', error);
          }
        }
      };

      // Wait for the SVG to be rendered
      setTimeout(() => {
        void initializePanZoom();
      }, 100);
    }
  }, [svg, zoomingEnabled]);

  return { containerRef };
};
