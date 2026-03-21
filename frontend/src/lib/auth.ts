export function isLoggedIn(): boolean {
  return !!localStorage.getItem("user");
}

export function logout() {
  localStorage.removeItem("user");
  sessionStorage.clear();
}
