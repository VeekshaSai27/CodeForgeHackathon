export interface AnalyzeProfileResponse {
  skills: string[];
  importance_scores: Record<string, number>;
  user_confidence: Record<string, number>;
}

export interface QuizQuestion {
  id: string;
  skill: string;
  question: string;
  options: string[];
  correct_answer?: string;
  // Defaults to "mcq" when undefined for backward compatibility
  type?: "mcq" | "coding";
  starterCode?: string;
  language?: string;
}

export interface EvaluateTestResponse {
  proficiency: Record<string, number>;
  weak_areas: string[];
}

export interface LearningPathItem {
  skill: string;
  status: "completed" | "current" | "locked";
  priority_score: number;
  reasoning: string;
  resources: Resource[];
}

export interface Resource {
  type: "video" | "documentation" | "practice";
  title: string;
  url: string;
}

export interface ComputePathResponse {
  learning_path: LearningPathItem[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}
