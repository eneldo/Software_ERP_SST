// ============================================================
// CONFIGURACIÓN FRONTEND - ERP SST PRO
// FASE 36.4 — Normalización Enterprise
// ============================================================

const DEFAULT_API_URL = "http://127.0.0.1:8000";

export function normalizeBaseURL(value) {
  const raw = String(value || DEFAULT_API_URL).trim();
  return raw.endsWith("/") ? raw.slice(0, -1) : raw;
}

export const APP_ENV = import.meta.env.MODE || "development";
export const API_BASE_URL = normalizeBaseURL(
  import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || DEFAULT_API_URL
);

export const IS_PRODUCTION = APP_ENV === "production";
