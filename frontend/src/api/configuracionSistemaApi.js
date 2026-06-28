// ============================================================
// API CONFIGURACIÓN SISTEMA PRO
// ERP SST PRO ENTERPRISE
// FASE 35.4.2
// Archivo: frontend/src/api/configuracionSistemaApi.js
// ============================================================

import api from "./axios";

const BASE_URL = "/configuracion-sistema";

export async function obtenerConfiguracionSistema() {
  const { data } = await api.get(`${BASE_URL}/`);
  return data;
}

export async function actualizarConfiguracionSistema(payload) {
  const { data } = await api.put(`${BASE_URL}/`, payload);
  return data;
}

export async function obtenerHealthConfiguracionSistema() {
  const { data } = await api.get(`${BASE_URL}/health`);
  return data;
}
