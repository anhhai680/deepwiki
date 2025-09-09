// Chat-related types
export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ResearchStage {
  title: string;
  content: string;
  iteration: number;
  type: 'plan' | 'update' | 'conclusion';
}

export interface ChatState {
  messages: Message[];
  currentResponse: string;
  isLoading: boolean;
  error: string | null;
}

export interface ResearchState {
  stages: ResearchStage[];
  currentStageIndex: number;
  iteration: number;
  isComplete: boolean;
  isEnabled: boolean;
}
