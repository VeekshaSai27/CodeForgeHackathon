import React, { createContext, useContext, useState, ReactNode } from "react";
import type {
  AnalyzeProfileResponse,
  EvaluateTestResponse,
  ComputePathResponse,
} from "@/types/onboarding";

interface OnboardingState {
  // From /analyze-profile
  skills: string[];
  importance_scores: Record<string, number>;
  user_confidence: Record<string, number>;

  // From /evaluate-test
  proficiency: Record<string, number>;
  weak_areas: string[];

  // From /compute-path
  learningPath: ComputePathResponse | null;

  // Setters
  setAnalysis: (data: AnalyzeProfileResponse) => void;
  setEvaluation: (data: EvaluateTestResponse) => void;
  setLearningPath: (data: ComputePathResponse) => void;
}

const OnboardingContext = createContext<OnboardingState | undefined>(undefined);

export function OnboardingProvider({ children }: { children: ReactNode }) {
  const [skills, setSkills] = useState<string[]>([]);
  const [importance_scores, setImportanceScores] = useState<Record<string, number>>({});
  const [user_confidence, setUserConfidence] = useState<Record<string, number>>({});
  const [proficiency, setProficiency] = useState<Record<string, number>>({});
  const [weak_areas, setWeakAreas] = useState<string[]>([]);
  const [learningPath, setLearningPathState] = useState<ComputePathResponse | null>(null);

  const setAnalysis = (data: AnalyzeProfileResponse) => {
    setSkills(data.skills);
    setImportanceScores(data.importance_scores);
    setUserConfidence(data.user_confidence);
  };

  const setEvaluation = (data: EvaluateTestResponse) => {
    setProficiency(data.proficiency);
    setWeakAreas(data.weak_areas);
  };

  const setLearningPath = (data: ComputePathResponse) => {
    setLearningPathState(data);
  };

  return (
    <OnboardingContext.Provider
      value={{
        skills,
        importance_scores,
        user_confidence,
        proficiency,
        weak_areas,
        learningPath,
        setAnalysis,
        setEvaluation,
        setLearningPath,
      }}
    >
      {children}
    </OnboardingContext.Provider>
  );
}

export function useOnboarding() {
  const ctx = useContext(OnboardingContext);
  if (!ctx) throw new Error("useOnboarding must be used within OnboardingProvider");
  return ctx;
}
