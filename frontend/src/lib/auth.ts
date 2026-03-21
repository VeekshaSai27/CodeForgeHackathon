export function isLoggedIn(): boolean {
  if (typeof window === "undefined") return false;

  try {
    return !!window.localStorage.getItem("user");
  } catch {
    return false;
  }
}

export function logout(): void {
  if (typeof window === "undefined") return;

  try {
    window.localStorage.removeItem("user");
  } catch {
    // ignore
  }
}
