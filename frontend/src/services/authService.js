// ============================================================
// AUTH SERVICE - ERP SST PRO ENTERPRISE
// FASE HARDENING — Autenticación separada del App.jsx
// Archivo: frontend/src/services/authService.js
// ============================================================

import api from "../api/axios";
import { setAccessToken, clearSession, getStoredUser, getAccessToken } from "../utils/security";

export async function login({ correo, password }) {
  const payload = {
    correo: String(correo || "").trim().toLowerCase(),
    password: String(password || ""),
  };

  const { data } = await api.post("/auth/login-json", payload);

  if (!data?.access_token) {
    throw new Error("Respuesta inválida del servidor de autenticación.");
  }

  setAccessToken(data.access_token);
  localStorage.setItem("user", JSON.stringify(data.usuario || {}));

  return data;
}

export async function logout() {
  try {
    await api.post("/auth/logout");
  } catch {
    // La limpieza local debe ocurrir incluso si el backend no responde.
  }
  clearSession();
}

export function getAccessTokenFromAuth() {
  return getAccessToken();
}

export function getCurrentUser() {
  return getStoredUser();
}

export function isAuthenticated() {
  return Boolean(getAccessToken());
}
