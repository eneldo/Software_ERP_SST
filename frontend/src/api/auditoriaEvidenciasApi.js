// ============================================================
// API AUDITORÍA INTEGRAL DE EVIDENCIAS
// ERP SST PRO ENTERPRISE
// FASE 35.4
// Archivo: frontend/src/api/auditoriaEvidenciasApi.js
// ============================================================

import api from "./axios";
import { limpiarParams } from "./apiHelpers";

const BASE_URL = "/auditoria-evidencias";

export async function obtenerHealthEvidencias() {
  const { data } = await api.get(`${BASE_URL}/health`);
  return data;
}

export async function listarModulosEvidencias() {
  const { data } = await api.get(`${BASE_URL}/modulos`);
  return data;
}

export async function auditarEvidencias(params = {}) {
  const { data } = await api.get(`${BASE_URL}/`, {
    params: limpiarParams(params),
  });

  return data;
}
