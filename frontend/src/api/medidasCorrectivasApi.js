// ============================================================
// API CENTRO DE MEDIDAS CORRECTIVAS ENTERPRISE
// ERP SST PRO
// FASE 1.1.8.7.4 — Frontend Enterprise
// Archivo: frontend/src/api/medidasCorrectivasApi.js
// ============================================================

import api from "./axios";

const BASE_URL = "/medidas-correctivas";

function cleanParams(params = {}) {
  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== "" && value !== null && value !== undefined)
  );
}

export async function listarMedidasCorrectivas(params = {}) {
  const { data } = await api.get(`${BASE_URL}/`, { params: cleanParams(params) });
  return data;
}

export async function obtenerDashboardMedidasCorrectivas(params = {}) {
  const { data } = await api.get(`${BASE_URL}/dashboard/resumen`, { params: cleanParams(params) });
  return data;
}

export async function obtenerMedidaCorrectiva(id) {
  const { data } = await api.get(`${BASE_URL}/${id}`);
  return data;
}

export async function crearMedidaCorrectiva(payload) {
  const { data } = await api.post(`${BASE_URL}/`, payload);
  return data;
}

export async function actualizarMedidaCorrectiva(id, payload) {
  const { data } = await api.put(`${BASE_URL}/${id}`, payload);
  return data;
}

export async function eliminarMedidaCorrectiva(id) {
  const { data } = await api.delete(`${BASE_URL}/${id}`);
  return data;
}

export async function aprobarMedidaCorrectiva(id, payload = {}) {
  const { data } = await api.post(`${BASE_URL}/${id}/aprobar`, payload);
  return data;
}

export async function cerrarMedidaCorrectiva(id, payload) {
  const { data } = await api.post(`${BASE_URL}/${id}/cerrar`, payload);
  return data;
}

export async function listarSeguimientosMedida(id) {
  const { data } = await api.get(`${BASE_URL}/${id}/seguimientos`);
  return data;
}

export async function crearSeguimientoMedida(id, payload) {
  const { data } = await api.post(`${BASE_URL}/${id}/seguimientos`, payload);
  return data;
}

export async function listarEvidenciasMedida(id) {
  const { data } = await api.get(`${BASE_URL}/${id}/evidencias`);
  return data;
}

export async function subirEvidenciaMedida(id, formData) {
  const { data } = await api.post(`${BASE_URL}/${id}/evidencias`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export function getMedidasCorrectivasExcelUrl(params = {}) {
  const query = new URLSearchParams(cleanParams(params)).toString();
  return `${api.defaults.baseURL}${BASE_URL}/exportaciones/excel-general${query ? `?${query}` : ""}`;
}
