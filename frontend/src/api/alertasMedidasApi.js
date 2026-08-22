// ============================================================
// API WORKFLOW + EFICACIA + ALERTAS MEDIDAS CORRECTIVAS
// ERP SST PRO
// FASE 1.1.8.7.4 — Frontend Enterprise
// Archivo: frontend/src/api/alertasMedidasApi.js
// ============================================================

import api from "./axios";
import { limpiarParams } from "./apiHelpers";

const BASE_URL = "/medidas-correctivas-enterprise";

export async function listarAlertasMedidas(params = {}) {
  const { data } = await api.get(`${BASE_URL}/alertas`, { params: limpiarParams(params) });
  return data;
}

export async function generarAlertasMedidas(params = {}) {
  const { data } = await api.post(`${BASE_URL}/alertas/generar`, null, { params: limpiarParams(params) });
  return data;
}

export async function marcarAlertaMedidaLeida(id) {
  const { data } = await api.post(`${BASE_URL}/alertas/${id}/leer`);
  return data;
}

export async function archivarAlertaMedida(id) {
  const { data } = await api.post(`${BASE_URL}/alertas/${id}/archivar`);
  return data;
}

export async function obtenerWorkflowMedida(id) {
  const { data } = await api.get(`${BASE_URL}/${id}/workflow`);
  return data;
}

export async function avanzarWorkflowMedida(id, payload) {
  const { data } = await api.post(`${BASE_URL}/${id}/workflow/avanzar`, payload);
  return data;
}

export async function evaluarEficaciaMedida(id, payload) {
  const { data } = await api.post(`${BASE_URL}/${id}/eficacia`, payload);
  return data;
}
