// ============================================================
// SECURITY UTILS - ERP SST PRO ENTERPRISE
// FASE 36.6 — Seguridad Enterprise Backend/Frontend
// Archivo: frontend/src/utils/security.js
// ============================================================

const USER_KEY = "user";
let accessToken = null;
let refreshPromise = null;

export function getAccessToken() {
  return accessToken;
}

export function setAccessToken(token) {
  accessToken = token || null;
}

export function getRefreshPromise() {
  return refreshPromise;
}

export function setRefreshPromise(promise) {
  refreshPromise = promise;
}

export function clearSession() {
  accessToken = null;
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
