// ============================================================
// AUTH SERVICE - ERP SST PRO ENTERPRISE
// FASE HARDENING — Autenticación separada del App.jsx
// Archivo: frontend/src/services/authService.js
// ============================================================

import api from "../api/axios";

const ACCESS_TOKEN_KEY = "access_token";
const USER_KEY = "user";

export async function login({ correo, password }) {
  const payload = {
    correo: String(correo || "").trim().toLowerCase(),
    password: String(password || ""),
  };

  const { data } = await api.post("/auth/login-json", payload);

  if (!data?.access_token) {
    throw new Error("Respuesta inválida del servidor de autenticación.");
  }

  localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.usuario || {}));

  return data;
}

export function logout() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getCurrentUser() {
  try {
    const rawUser = localStorage.getItem(USER_KEY);
    return rawUser ? JSON.parse(rawUser) : null;
  } catch (error) {
    console.warn("No fue posible leer el usuario autenticado.", error);
    return null;
  }
}

export function isAuthenticated() {
  return Boolean(getAccessToken());
}
