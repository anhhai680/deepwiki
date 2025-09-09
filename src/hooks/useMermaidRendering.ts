import { useState, useEffect, useRef } from 'react';
import mermaid from 'mermaid';
import { initializeMermaid } from '@/utils/mermaidConfig';
import { preprocessMermaidChart } from '@/utils/diagramSanitization';

export const useMermaidRendering = (chart: string) => {
  const [svg, setSvg] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const idRef = useRef(`mermaid-${Math.random().toString(36).substring(2, 9)}`);
  const isDarkModeRef = useRef(
    typeof window !== 'undefined' &&
    window.matchMedia &&
    window.matchMedia('(prefers-color-scheme: dark)').matches
  );

  useEffect(() => {
    // Initialize Mermaid on first render
    initializeMermaid();
  }, []);

  useEffect(() => {
    if (!chart) return;

    let isMounted = true;

    const renderChart = async () => {
      if (!isMounted) return;

      try {
        setIsLoading(true);
        setError(null);
        setSvg('');

        // Preprocess the chart to fix common syntax issues
        const cleanedChart = preprocessMermaidChart(chart);

        // Render the chart with cleaned syntax
        const { svg: renderedSvg } = await mermaid.render(idRef.current, cleanedChart);

        if (!isMounted) return;

        let processedSvg = renderedSvg;
        if (isDarkModeRef.current) {
          processedSvg = processedSvg.replace('<svg ', '<svg data-theme="dark" ');
        }

        setSvg(processedSvg);

        // Call mermaid.contentLoaded to ensure proper initialization
        setTimeout(() => {
          mermaid.contentLoaded();
        }, 50);
      } catch (err) {
        console.error('Mermaid rendering error:', err);

        const errorMessage = err instanceof Error ? err.message : String(err);

        if (isMounted) {
          setError(errorMessage);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    renderChart();

    return () => {
      isMounted = false;
    };
  }, [chart]);

  const getErrorDebugInfo = () => {
    if (!error || !chart) return null;

    const cleanedChart = preprocessMermaidChart(chart);
    
    return {
      originalChart: chart,
      cleanedChart,
      errorMessage: error,
      wasChartCleaned: cleanedChart !== chart,
    };
  };

  return {
    svg,
    error,
    isLoading,
    getErrorDebugInfo,
  };
};
