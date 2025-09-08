import { ResearchStage } from '@/types/shared';

/**
 * Check if research is complete based on response content
 */
export const checkIfResearchComplete = (content: string): boolean => {
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

/**
 * Extract research stage from the response
 */
export const extractResearchStage = (content: string, iteration: number): ResearchStage | null => {
  // Check for research plan (first iteration)
  if (iteration === 1 && content.includes('## Research Plan')) {
    const planMatch = content.match(/## Research Plan([\\s\\S]*?)(?:## Next Steps|$)/);
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
    const updateMatch = content.match(new RegExp(`## Research Update ${iteration}([\\\\s\\\\S]*?)(?:## Next Steps|$)`));
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
    const conclusionMatch = content.match(/## Final Conclusion([\\s\\S]*?)$/);
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

/**
 * Generate completion note for forced research completion
 */
export const generateCompletionNote = (): string => {
  return "\\n\\n## Final Conclusion\\nAfter multiple iterations of deep research, we've gathered significant insights about this topic. This concludes our investigation process, having reached the maximum number of research iterations. The findings presented across all iterations collectively form our comprehensive answer to the original question.";
};
