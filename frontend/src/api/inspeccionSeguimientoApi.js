// ============================================================
// API PLANES DE ACCIÓN Y SEGUIMIENTO DE HALLAZGOS SST
// FASE 1.1.8.6 — PLANES DE ACCIÓN Y SEGUIMIENTO ENTERPRISE
// Archivo: frontend/src/api/inspeccionSeguimientoApi.js
// ============================================================

import api from "./axios";
import { normalizarLista, limpiarParams } from "./apiHelpers";

const BASE_URL = "/inspecciones-seguimientos";

const descargarBlob = async (url, filename, params = {}) => {
  const response = await api.get(url, { params: limpiarParams(params), responseType: "blob" });
  const href = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = href;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(href);
};

export const dashboardSeguimientosHallazgos = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/dashboard/resumen`, { params: limpiarParams(params) });
  return response.data;
};

export const listarSeguimientosHallazgo = async (hallazgoId) => {
  const response = await api.get(`${BASE_URL}/${hallazgoId}`);
  return normalizarLista(response.data);
};

export const crearSeguimientoHallazgo = async (payload) => {
  const response = await api.post(`${BASE_URL}/`, payload);
  return response.data;
};

export const actualizarSeguimientoHallazgo = async (seguimientoId, payload) => {
  const response = await api.put(`${BASE_URL}/${seguimientoId}`, payload);
  return response.data;
};

export const eliminarSeguimientoHallazgo = async (seguimientoId) => {
  const response = await api.delete(`${BASE_URL}/${seguimientoId}`);
  return response.data;
};

export const cerrarHallazgoConPlanAccion = async (hallazgoId, payload = {}) => {
  const response = await api.post(`${BASE_URL}/hallazgos/${hallazgoId}/cerrar`, payload);
  return response.data;
};

export const listarEvidenciasSeguimiento = async (seguimientoId) => {
  const response = await api.get(`${BASE_URL}/${seguimientoId}/evidencias`);
  return normalizarLista(response.data);
};

export const subirEvidenciaSeguimiento = async (seguimientoId, formData) => {
  const response = await api.post(`${BASE_URL}/${seguimientoId}/evidencias`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const eliminarEvidenciaSeguimiento = async (seguimientoId, archivoId) => {
  const response = await api.delete(`${BASE_URL}/${seguimientoId}/evidencias/${archivoId}`);
  return response.data;
};

export const exportarSeguimientosHallazgosExcel = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/excel`, "seguimientos_hallazgos_sst.xlsx", params);

export const exportarSeguimientosHallazgosPdf = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/pdf`, "seguimientos_hallazgos_sst.pdf", params);

const inspeccionSeguimientoApi = {
  dashboard: dashboardSeguimientosHallazgos,
  listar: listarSeguimientosHallazgo,
  crear: crearSeguimientoHallazgo,
  actualizar: actualizarSeguimientoHallazgo,
  eliminar: eliminarSeguimientoHallazgo,
  cerrarHallazgo: cerrarHallazgoConPlanAccion,
  listarEvidencias: listarEvidenciasSeguimiento,
  subirEvidencia: subirEvidenciaSeguimiento,
  eliminarEvidencia: eliminarEvidenciaSeguimiento,
  excel: exportarSeguimientosHallazgosExcel,
  pdf: exportarSeguimientosHallazgosPdf,
};

export default inspeccionSeguimientoApi;
