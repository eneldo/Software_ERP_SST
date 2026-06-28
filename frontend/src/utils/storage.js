// ============================================================
// STORAGE SEGURO - ERP SST PRO
// FASE 36.4 — Normalización Enterprise
// ============================================================

export const AUTH_TOKEN_KEY = "access_token";
export const AUTH_USER_KEY = "user";

export function getAuthToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthToken(token) {
  if (token) localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function clearAuthSession() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem(AUTH_USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}
