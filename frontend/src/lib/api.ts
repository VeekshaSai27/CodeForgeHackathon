const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000";

async function request<T>(endpoint: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  analyzeProfile: (resume: string, jd: string) =>
    request("/analyze-profile", { resume, jd }),

  generateTest: (skills: string[]) =>
    request("/generate-test", { skills }),

  evaluateTest: (answers: Record<string, string>) =>
    request("/evaluate-test", { answers }),

  computePath: (data: {
    skills: string[];
    proficiency: Record<string, number>;
    importance_scores: Record<string, number>;
    user_confidence: Record<string, number>;
  }) => request("/compute-path", data),

  chat: (message: string, context?: unknown) =>
    request<{ response: string }>("/chat", { message, context }),
};
