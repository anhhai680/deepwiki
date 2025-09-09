// Function to fix activation/deactivation sequence mismatches
export const fixActivationDeactivationSequence = (chart: string): string => {
  const lines = chart.split('\n');
  
  // Track activation state for participants
  const activationState = new Map<string, boolean>();
  const processedLines: string[] = [];
  
  // Patterns for activation and deactivation (both with original participant names)
  const activatePattern = /^.*?->>[+](.+?):\s*.*/;
  const deactivatePattern = /^.*?-->>[−](.+?):\s*.*/;
  
  lines.forEach((line) => {
    const trimmedLine = line.trim();
    
    // Skip empty lines and declarations
    if (!trimmedLine || trimmedLine.startsWith('participant') || trimmedLine.startsWith('sequenceDiagram')) {
      processedLines.push(line);
      return;
    }
    
    // Check for activation
    const activateMatch = line.match(activatePattern);
    if (activateMatch) {
      const participant = activateMatch[1].trim();
      activationState.set(participant, true);
      processedLines.push(line);
      return;
    }
    
    // Check for deactivation
    const deactivateMatch = line.match(deactivatePattern);
    if (deactivateMatch) {
      const participant = deactivateMatch[1].trim();
      
      // Only include deactivation if participant is currently active
      if (activationState.get(participant) === true) {
        activationState.set(participant, false);
        processedLines.push(line);
      }
      // Skip invalid deactivations (when participant is not active)
      return;
    }
    
    // Regular line (message without activation/deactivation)
    processedLines.push(line);
  });
  
  return processedLines.join('\n');
};

// Function to clean and fix common Mermaid syntax issues
export const preprocessMermaidChart = (chart: string): string => {
  let cleanedChart = chart;
  
  // Detect diagram type for specific preprocessing
  const isSequenceDiagram = cleanedChart.trim().startsWith('sequenceDiagram');
  
  if (isSequenceDiagram) {
    // Fix activation/deactivation sequences while preserving original participant names
    cleanedChart = fixActivationDeactivationSequence(cleanedChart);
  } else {
    // Handle flowchart and other diagram types
    
    // Single comprehensive regex to fix all node bracket issues at once
    // This handles:
    // 1. Incomplete brackets: NodeId[Text without closing bracket
    // 2. Text with special characters: NodeId[Text with spaces and (parentheses)]
    // 3. Multiline incomplete patterns: NodeId[Text\n
    cleanedChart = cleanedChart.replace(
      /(\w+)\[([^\]]*?)(?:\]|$|\n)/gm,
      (match, nodeId, text) => {
        // Check if this is already properly quoted
        if (text.startsWith('"') && text.endsWith('"')) {
          return match;
        }
        
        // Determine the ending (was it closed, end of string, or newline?)
        const wasProperlyClosedBracket = match.endsWith(']');
        const wasNewline = match.endsWith('\n');
        
        // Clean and quote the text if it needs special handling
        const needsQuoting = text.includes(' ') || 
                            text.includes('(') || 
                            text.includes(')') || 
                            text.includes('[') || 
                            !wasProperlyClosedBracket;
        
        if (needsQuoting) {
          const escapedText = text.replace(/"/g, '\\"');
          return `${nodeId}["${escapedText}"]${wasNewline ? '\n' : ''}`;
        }
        
        // If it was an incomplete bracket, just close it properly
        if (!wasProperlyClosedBracket) {
          return `${nodeId}[${text}]${wasNewline ? '\n' : ''}`;
        }
        
        return match;
      }
    );
    
    // Normalize arrow syntax with proper spacing for flowcharts
    cleanedChart = cleanedChart.replace(/\s*-->\s*/g, ' --> ');
    cleanedChart = cleanedChart.replace(/\s*--->\s*/g, ' ---> ');
    cleanedChart = cleanedChart.replace(/\s*-\.->s*/g, ' -.-> ');
    cleanedChart = cleanedChart.replace(/\s*==>\s*/g, ' ==> ');
  }
  
  // Common cleanup for all diagram types
  // Normalize whitespace but preserve line structure
  cleanedChart = cleanedChart.split('\n').map(line => 
    line.trim().replace(/\s+/g, ' ')
  ).join('\n');
  
  return cleanedChart.trim();
};
