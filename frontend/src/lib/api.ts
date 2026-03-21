// Public API surface for the frontend.
// This file exposes a stable interface used by components, while
// internally delegating to the middleware API layer. The middleware
// service is responsible for talking to external providers and
// keeping API keys/credentials on the server side only.

import { middlewareApi } from "./middlewareApi";

export const api = {
  analyzeProfile: (resume: string, jd: string) =>
    middlewareApi.analyzeProfile({ resume, jd }),

  generateTest: (skills: string[]) =>
    middlewareApi.generateTest({ skills }),

  evaluateTest: (answers: Record<string, string>) =>
    middlewareApi.evaluateTest({ answers }),

  computePath: (data: {
    skills: string[];
    proficiency: Record<string, number>;
    importance_scores: Record<string, number>;
    user_confidence: Record<string, number>;
  }) => middlewareApi.computePath(data),

  chat: (message: string, context?: unknown) =>
    middlewareApi.chat({ message, context }),
};
