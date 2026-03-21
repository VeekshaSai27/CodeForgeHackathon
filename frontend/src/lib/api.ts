const API_BASE = import.meta.env.VITE_API_URL || "";

const SESSION_HEADER = "X-Session-Token";

function getToken(): string | null {
  return sessionStorage.getItem(SESSION_HEADER);
}

function saveToken(res: Record<string, unknown>) {
  const token = res[SESSION_HEADER];
  if (typeof token === "string") {
    sessionStorage.setItem(SESSION_HEADER, token);
  }
}

async function request<T>(endpoint: string, body: unknown): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers[SESSION_HEADER] = token;

  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }

  const data = await res.json();
  saveToken(data);
  return data as T;
}

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
