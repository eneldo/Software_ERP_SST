// ============================================================
// API AXIOS - ERP SST PRO ENTERPRISE
// FASE 36.8 — Logging Enterprise y Manejo de Errores
// Archivo: frontend/src/api/axios.js
// ============================================================

import axios from "axios";
import { clearSession, getAccessToken, setAccessToken } from "../utils/security";
import { logger } from "../utils/logger";
import { API_BASE_URL } from "../config/env";

const DEFAULT_TIMEOUT = 30000;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: Number(import.meta.env.VITE_API_TIMEOUT || DEFAULT_TIMEOUT),
  withCredentials: true,
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
  async (error) => {
    const status = error?.response?.status;
    const originalRequest = error?.config || {};

    if (status === 401 && !originalRequest.__isRefreshRequest && !originalRequest.__retry) {
      originalRequest.__retry = true;
      try {
        const { data } = await api.post("/auth/refresh", null, { __isRefreshRequest: true });
        if (data?.access_token) {
          setAccessToken(data.access_token);
          if (data.usuario) {
            localStorage.setItem("user", JSON.stringify(data.usuario));
          }
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        logger.warn("No fue posible renovar la sesion.", refreshError);
      }
    }

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
