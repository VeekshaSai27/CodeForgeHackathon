// Centralized middleware API layer.
// The frontend should never talk directly to external APIs.
// Instead, it calls these endpoints on a backend middleware service
// which holds and protects any secret API keys.

const MIDDLEWARE_BASE: string =
  import.meta.env.VITE_API_BASE_URL || "/middleware";

async function middlewareRequest<T>(
  endpoint: string,
  payload: unknown
): Promise<T> {
  const url = `${MIDDLEWARE_BASE}${endpoint}`;

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload ?? {}),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    const message = text || res.statusText || "Unknown error";
    throw new Error(`Middleware API error ${res.status}: ${message}`);
  }

  return res.json() as Promise<T>;
}

export const middlewareApi = {
  analyzeProfile: (payload: { resume: string; jd: string }) =>
    middlewareRequest("/analyze-profile", payload),

  generateTest: (payload: { skills: string[] }) =>
    middlewareRequest("/generate-test", payload),

  evaluateTest: (payload: { answers: Record<string, string> }) =>
    middlewareRequest("/evaluate-test", payload),

  computePath: (payload: {
    skills: string[];
    proficiency: Record<string, number>;
    importance_scores: Record<string, number>;
    user_confidence: Record<string, number>;
  }) => middlewareRequest("/compute-path", payload),

  chat: (payload: { message: string; context?: unknown }) =>
    middlewareRequest<{ response: string }>("/chat", payload),
};
