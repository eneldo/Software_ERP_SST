// ============================================================
// API AXIOS - ERP SST PRO ENTERPRISE
// FASE 36.8 — Logging Enterprise y Manejo de Errores
// Archivo: frontend/src/api/axios.js
// ============================================================

import axios from "axios";
import { clearSession, getAccessToken } from "../utils/security";
import { logger } from "../utils/logger";

const DEFAULT_API_URL = "http://127.0.0.1:8000";
const DEFAULT_TIMEOUT = 30000;

function normalizeBaseURL(value) {
  const raw = String(value || DEFAULT_API_URL).trim();
  return raw.endsWith("/") ? raw.slice(0, -1) : raw;
}

export const API_BASE_URL = normalizeBaseURL(
  import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL
);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: Number(import.meta.env.VITE_API_TIMEOUT || DEFAULT_TIMEOUT),
  headers: {
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    config.headers["X-Request-ID"] = crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;

    if (status === 401) {
      clearSession();
      const isLogin = window.location.pathname === "/";
      if (!isLogin) {
        window.location.replace("/");
      }
    }

    if (status === 429) {
      error.userMessage = "Demasiadas solicitudes. Intente nuevamente en unos segundos.";
    } else if (status >= 500) {
      error.userMessage = "El servidor no pudo procesar la solicitud. Intente nuevamente.";
    } else {
      error.userMessage =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        error?.message ||
        "No fue posible completar la solicitud.";
    }

    logger.error("Error HTTP API", error, { status });

    return Promise.reject(error);
  }
);

export default api;
