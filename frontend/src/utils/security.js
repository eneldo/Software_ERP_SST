// ============================================================
// SECURITY UTILS - ERP SST PRO ENTERPRISE
// FASE 36.6 — Seguridad Enterprise Backend/Frontend
// Archivo: frontend/src/utils/security.js
// ============================================================

const TOKEN_KEY = "access_token";
const USER_KEY = "user";

export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token) {
  if (!token) return;
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    clearSession();
    return null;
  }
}

export function safeText(value, fallback = "") {
  if (value === null || value === undefined) return fallback;
  return String(value).replace(/[<>]/g, "").trim();
}

export function isSafeInternalPath(path) {
  return typeof path === "string" && path.startsWith("/") && !path.startsWith("//");
}
