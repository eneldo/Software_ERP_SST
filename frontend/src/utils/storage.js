// ============================================================
// STORAGE SEGURO - ERP SST PRO
// FASE 36.4 — Normalización Enterprise
// Re-exports desde security.js para backward compatibility
// ============================================================

export {
  getAccessToken as getAuthToken,
  setAccessToken as setAuthToken,
  clearSession as clearAuthSession,
  getStoredUser,
} from "./security";

export const AUTH_TOKEN_KEY = "access_token";
export const AUTH_USER_KEY = "user";
