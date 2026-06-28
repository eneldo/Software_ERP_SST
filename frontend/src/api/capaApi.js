// ============================================================
// API CAPA SST ENTERPRISE - ERP SST PRO
// FASE 1.1.8.7.1 — Optimización CAPA Enterprise
// Archivo: frontend/src/api/capaApi.js
// ============================================================

import api from "./axios";

const BASE_URL = "/capa";

const limpiarParams = (params = {}) =>
  Object.fromEntries(
    Object.entries(params).filter(
      ([, value]) => value !== "" && value !== null && value !== undefined && value !== "TODOS"
    )
  );

const normalizarLista = (data) => {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.data)) return data.data;
  return [];
};

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

export const listarCAPA = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/`, { params: limpiarParams(params) });
  return normalizarLista(response.data);
};

export const obtenerCAPA = async (id) => {
  const response = await api.get(`${BASE_URL}/${id}`);
  return response.data;
};

export const crearCAPA = async (payload) => {
  const response = await api.post(`${BASE_URL}/`, payload);
  return response.data;
};

export const crearCAPADesdeHallazgo = async (hallazgoId) => {
  const response = await api.post(`${BASE_URL}/desde-hallazgo/${hallazgoId}`);
  return response.data;
};

export const actualizarCAPA = async (id, payload) => {
  const response = await api.put(`${BASE_URL}/${id}`, payload);
  return response.data;
};

export const eliminarCAPA = async (id) => {
  const response = await api.delete(`${BASE_URL}/${id}`);
  return response.data;
};

export const cerrarCAPA = async (id, payload) => {
  const response = await api.post(`${BASE_URL}/${id}/cerrar`, payload);
  return response.data;
};

export const dashboardCAPA = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/dashboard/resumen`, { params: limpiarParams(params) });
  return response.data;
};

export const listarSeguimientosCAPA = async (capaId) => {
  const response = await api.get(`${BASE_URL}/${capaId}/seguimientos`);
  return normalizarLista(response.data);
};

export const crearSeguimientoCAPA = async (capaId, payload) => {
  const response = await api.post(`${BASE_URL}/${capaId}/seguimientos`, { ...payload, capa_id: capaId });
  return response.data;
};

export const actualizarSeguimientoCAPA = async (seguimientoId, payload) => {
  const response = await api.put(`${BASE_URL}/seguimientos/${seguimientoId}`, payload);
  return response.data;
};

export const eliminarSeguimientoCAPA = async (seguimientoId) => {
  const response = await api.delete(`${BASE_URL}/seguimientos/${seguimientoId}`);
  return response.data;
};

export const listarEvidenciasCAPA = async (capaId) => {
  const response = await api.get(`${BASE_URL}/${capaId}/evidencias`);
  return normalizarLista(response.data);
};

export const subirEvidenciaCAPA = async (capaId, formData) => {
  const response = await api.post(`${BASE_URL}/${capaId}/evidencias`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const eliminarEvidenciaCAPA = async (capaId, archivoId) => {
  const response = await api.delete(`${BASE_URL}/${capaId}/evidencias/${archivoId}`);
  return response.data;
};

export const exportarCAPAExcel = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/excel-general`, "capas_sst_general.xlsx", params);

export const exportarCAPAPdf = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/pdf-general`, "capas_sst_general.pdf", params);

export const exportarDashboardCAPAPdf = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/dashboard-pdf`, "dashboard_capa_sst.pdf", params);

export const exportarCAPAPdfIndividual = (id) =>
  descargarBlob(`${BASE_URL}/exportaciones/${id}/pdf-individual`, `capa_sst_${id}.pdf`);

export const exportarActaCAPAPdf = (id) =>
  descargarBlob(`${BASE_URL}/exportaciones/${id}/acta-pdf`, `acta_capa_sst_${id}.pdf`);

export const urlArchivoCAPA = (url) => {
  if (!url) return "";
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  const API_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
  return `${API_URL}${url.startsWith("/") ? url : `/${url}`}`;
};

export const urlPreviewCAPA = (archivo) => urlArchivoCAPA(archivo?.preview_url || archivo?.url);
export const urlMiniaturaCAPA = (archivo) => urlArchivoCAPA(archivo?.thumbnail_url || archivo?.preview_url || archivo?.url);

export const esImagenCAPA = (archivo) => String(archivo?.mime_type || "").startsWith("image/");
export const esPdfCAPA = (archivo) => String(archivo?.mime_type || "").includes("pdf");

const capaApi = {
  listar: listarCAPA,
  obtener: obtenerCAPA,
  crear: crearCAPA,
  crearDesdeHallazgo: crearCAPADesdeHallazgo,
  actualizar: actualizarCAPA,
  eliminar: eliminarCAPA,
  cerrar: cerrarCAPA,
  dashboard: dashboardCAPA,
  listarSeguimientos: listarSeguimientosCAPA,
  crearSeguimiento: crearSeguimientoCAPA,
  actualizarSeguimiento: actualizarSeguimientoCAPA,
  eliminarSeguimiento: eliminarSeguimientoCAPA,
  listarEvidencias: listarEvidenciasCAPA,
  subirEvidencia: subirEvidenciaCAPA,
  eliminarEvidencia: eliminarEvidenciaCAPA,
  excel: exportarCAPAExcel,
  pdf: exportarCAPAPdf,
  dashboardPdf: exportarDashboardCAPAPdf,
  pdfIndividual: exportarCAPAPdfIndividual,
  actaPdf: exportarActaCAPAPdf,
};

export default capaApi;
