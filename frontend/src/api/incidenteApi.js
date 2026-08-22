// ============================================================
// API INCIDENTES Y ACCIDENTES SST ENTERPRISE
// FASE 1.1.8.8.5 — DASHBOARD Y EXPORTACIONES
// Archivo: frontend/src/api/incidenteApi.js
// ============================================================

import api from "./axios";
import { resolveFileUrl } from "../utils/fileUrl";
import { normalizarLista, limpiarParams } from "./apiHelpers";

const BASE_URL = "/incidentes";

export const listarIncidentesSST = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/`, { params: limpiarParams(params) });
  return normalizarLista(response.data);
};

export const obtenerIncidenteSST = async (id) => {
  const response = await api.get(`${BASE_URL}/${id}`);
  return response.data;
};

export const crearIncidenteSST = async (payload) => {
  const response = await api.post(`${BASE_URL}/`, payload);
  return response.data;
};

export const actualizarIncidenteSST = async (id, payload) => {
  const response = await api.put(`${BASE_URL}/${id}`, payload);
  return response.data;
};

export const eliminarIncidenteSST = async (id) => {
  const response = await api.delete(`${BASE_URL}/${id}`);
  return response.data;
};

export const dashboardIncidentesSST = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/dashboard/resumen`, { params: limpiarParams(params) });
  return response.data;
};


export const obtenerInvestigacionIncidenteSST = async (incidenteId) => {
  const response = await api.get(`${BASE_URL}/${incidenteId}/investigacion`);
  return response.data;
};

export const actualizarInvestigacionIncidenteSST = async (incidenteId, payload) => {
  const response = await api.put(`${BASE_URL}/${incidenteId}/investigacion`, payload);
  return response.data;
};

export const obtenerArbolCausasIncidenteSST = async (incidenteId) => {
  const response = await api.get(`${BASE_URL}/${incidenteId}/arbol-causas`);
  return response.data;
};

export const actualizarArbolCausasIncidenteSST = async (incidenteId, payload) => {
  const response = await api.put(`${BASE_URL}/${incidenteId}/arbol-causas`, payload);
  return response.data;
};

export const cerrarInvestigacionIncidenteSST = async (incidenteId, payload) => {
  const response = await api.post(`${BASE_URL}/${incidenteId}/cerrar-investigacion`, payload);
  return response.data;
};

export const generarCapaDesdeIncidenteSST = async (incidenteId) => {
  const response = await api.post(`${BASE_URL}/${incidenteId}/generar-capa`);
  return response.data;
};

export const listarLesionadosIncidenteSST = async (incidenteId) => {
  const response = await api.get(`${BASE_URL}/${incidenteId}/lesionados`);
  return normalizarLista(response.data);
};

export const crearLesionadoIncidenteSST = async (incidenteId, payload) => {
  const response = await api.post(`${BASE_URL}/${incidenteId}/lesionados`, {
    ...payload,
    incidente_id: incidenteId,
  });
  return response.data;
};

export const actualizarLesionadoIncidenteSST = async (lesionadoId, payload) => {
  const response = await api.put(`${BASE_URL}/lesionados/${lesionadoId}`, payload);
  return response.data;
};

export const eliminarLesionadoIncidenteSST = async (lesionadoId) => {
  const response = await api.delete(`${BASE_URL}/lesionados/${lesionadoId}`);
  return response.data;
};

export const listarTestigosIncidenteSST = async (incidenteId) => {
  const response = await api.get(`${BASE_URL}/${incidenteId}/testigos`);
  return normalizarLista(response.data);
};

export const crearTestigoIncidenteSST = async (incidenteId, payload) => {
  const response = await api.post(`${BASE_URL}/${incidenteId}/testigos`, {
    ...payload,
    incidente_id: incidenteId,
  });
  return response.data;
};

export const actualizarTestigoIncidenteSST = async (testigoId, payload) => {
  const response = await api.put(`${BASE_URL}/testigos/${testigoId}`, payload);
  return response.data;
};

export const eliminarTestigoIncidenteSST = async (testigoId) => {
  const response = await api.delete(`${BASE_URL}/testigos/${testigoId}`);
  return response.data;
};

export const listarEvidenciasIncidenteSST = async (incidenteId) => {
  const response = await api.get(`${BASE_URL}/${incidenteId}/evidencias`);
  return normalizarLista(response.data);
};

export const subirEvidenciaIncidenteSST = async (incidenteId, formData) => {
  const response = await api.post(`${BASE_URL}/${incidenteId}/evidencias`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const eliminarEvidenciaIncidenteSST = async (incidenteId, archivoId) => {
  const response = await api.delete(`${BASE_URL}/${incidenteId}/evidencias/${archivoId}`);
  return response.data;
};

export const urlArchivoIncidenteSST = resolveFileUrl;


const descargarBlob = async (url, filename, params = {}) => {
  const response = await api.get(url, {
    params: limpiarParams(params),
    responseType: "blob",
  });
  const disposition = response.headers?.["content-disposition"] || "";
  const match = disposition.match(/filename\*?=(?:UTF-8''|\")?([^";]+)/i);
  const finalName = match ? decodeURIComponent(match[1].replace(/"/g, "")) : filename;
  const href = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = href;
  link.setAttribute("download", finalName);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(href);
};

export const exportarIncidentesExcelGeneral = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/excel-general`, "incidentes_accidentes_sst_general.xlsx", params);

export const exportarIncidentesPdfGeneral = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/pdf-general`, "incidentes_accidentes_sst_general.pdf", params);

export const exportarDashboardEjecutivoIncidentesPdf = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/dashboard-ejecutivo-pdf`, "dashboard_ejecutivo_incidentes_sst.pdf", params);

export const exportarIncidentePdfIndividual = (id) =>
  descargarBlob(`${BASE_URL}/${id}/pdf-individual`, `incidente_accidente_${id}.pdf`);

export const exportarActaInvestigacionPdf = (id) =>
  descargarBlob(`${BASE_URL}/${id}/acta-investigacion-pdf`, `acta_investigacion_${id}.pdf`);

export const exportarInformeIncidentePdf = (id) =>
  descargarBlob(`${BASE_URL}/${id}/informe-incidente-pdf`, `informe_incidente_${id}.pdf`);

export const exportarInformeAccidentePdf = (id) =>
  descargarBlob(`${BASE_URL}/${id}/informe-accidente-pdf`, `informe_accidente_${id}.pdf`);

const incidenteApi = {
  listar: listarIncidentesSST,
  obtener: obtenerIncidenteSST,
  crear: crearIncidenteSST,
  actualizar: actualizarIncidenteSST,
  eliminar: eliminarIncidenteSST,
  dashboard: dashboardIncidentesSST,
  obtenerInvestigacion: obtenerInvestigacionIncidenteSST,
  actualizarInvestigacion: actualizarInvestigacionIncidenteSST,
  obtenerArbolCausas: obtenerArbolCausasIncidenteSST,
  actualizarArbolCausas: actualizarArbolCausasIncidenteSST,
  cerrarInvestigacion: cerrarInvestigacionIncidenteSST,
  generarCapa: generarCapaDesdeIncidenteSST,
  listarLesionados: listarLesionadosIncidenteSST,
  crearLesionado: crearLesionadoIncidenteSST,
  actualizarLesionado: actualizarLesionadoIncidenteSST,
  eliminarLesionado: eliminarLesionadoIncidenteSST,
  listarTestigos: listarTestigosIncidenteSST,
  crearTestigo: crearTestigoIncidenteSST,
  actualizarTestigo: actualizarTestigoIncidenteSST,
  eliminarTestigo: eliminarTestigoIncidenteSST,
  listarEvidencias: listarEvidenciasIncidenteSST,
  subirEvidencia: subirEvidenciaIncidenteSST,
  eliminarEvidencia: eliminarEvidenciaIncidenteSST,
  urlArchivo: urlArchivoIncidenteSST,
  exportarExcelGeneral: exportarIncidentesExcelGeneral,
  exportarPdfGeneral: exportarIncidentesPdfGeneral,
  exportarDashboardPdf: exportarDashboardEjecutivoIncidentesPdf,
  exportarPdfIndividual: exportarIncidentePdfIndividual,
  exportarActaInvestigacionPdf: exportarActaInvestigacionPdf,
  exportarInformeIncidentePdf: exportarInformeIncidentePdf,
  exportarInformeAccidentePdf: exportarInformeAccidentePdf,
};

export default incidenteApi;
