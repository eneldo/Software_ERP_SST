// ============================================================
// API INSPECCIONES SST ENTERPRISE - ERP SST PRO
// FASE 1.1.8 — INSPECCIONES SST ENTERPRISE
// Archivo: frontend/src/api/inspeccionSstApi.js
// ============================================================

import api from "./axios";

const BASE_URL = "/inspecciones";

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

export const listarInspeccionesSST = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/`, { params: limpiarParams(params) });
  return normalizarLista(response.data);
};

export const obtenerInspeccionSST = async (id) => {
  const response = await api.get(`${BASE_URL}/${id}`);
  return response.data;
};

export const crearInspeccionSST = async (payload) => {
  const response = await api.post(`${BASE_URL}/`, payload);
  return response.data;
};

export const actualizarInspeccionSST = async (id, payload) => {
  const response = await api.put(`${BASE_URL}/${id}`, payload);
  return response.data;
};

export const eliminarInspeccionSST = async (id) => {
  const response = await api.delete(`${BASE_URL}/${id}`);
  return response.data;
};

export const dashboardInspeccionesSST = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/dashboard/resumen`, { params: limpiarParams(params) });
  return response.data;
};

export const listarHallazgosInspeccionSST = async (inspeccionId) => {
  const response = await api.get(`${BASE_URL}/${inspeccionId}/hallazgos`);
  return normalizarLista(response.data);
};

export const crearHallazgoInspeccionSST = async (inspeccionId, payload) => {
  const response = await api.post(`${BASE_URL}/${inspeccionId}/hallazgos`, {
    ...payload,
    inspeccion_id: inspeccionId,
  });
  return response.data;
};

export const actualizarHallazgoInspeccionSST = async (hallazgoId, payload) => {
  const response = await api.put(`${BASE_URL}/hallazgos/${hallazgoId}`, payload);
  return response.data;
};

export const eliminarHallazgoInspeccionSST = async (hallazgoId) => {
  const response = await api.delete(`${BASE_URL}/hallazgos/${hallazgoId}`);
  return response.data;
};

export const listarEvidenciasInspeccionSST = async (inspeccionId) => {
  const response = await api.get(`${BASE_URL}/${inspeccionId}/evidencias`);
  return normalizarLista(response.data);
};

export const subirEvidenciaInspeccionSST = async (inspeccionId, formData) => {
  const response = await api.post(`${BASE_URL}/${inspeccionId}/evidencias`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const eliminarEvidenciaInspeccionSST = async (inspeccionId, archivoId) => {
  const response = await api.delete(`${BASE_URL}/${inspeccionId}/evidencias/${archivoId}`);
  return response.data;
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

export const exportarInspeccionesExcelGeneral = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/excel-general`, "inspecciones_sst_general.xlsx", params);

export const exportarInspeccionesPdfGeneral = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/pdf-general`, "inspecciones_sst_general.pdf", params);

export const exportarInspeccionPdfIndividual = (id) =>
  descargarBlob(`${BASE_URL}/exportaciones/${id}/pdf-individual`, `inspeccion_sst_${id}.pdf`);

export const exportarInspeccionActaPdf = (id) =>
  descargarBlob(`${BASE_URL}/exportaciones/${id}/acta-pdf`, `acta_inspeccion_sst_${id}.pdf`);

export const exportarHallazgosExcel = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/hallazgos-excel`, "hallazgos_inspecciones_sst.xlsx", params);

export const exportarHallazgosPdf = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/hallazgos-pdf`, "hallazgos_inspecciones_sst.pdf", params);

export const exportarSeguimientosPdf = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/seguimientos-pdf`, "seguimientos_inspecciones_sst.pdf", params);

export const exportarDashboardEjecutivoInspeccionesPdf = (params = {}) =>
  descargarBlob(`${BASE_URL}/exportaciones/dashboard-ejecutivo-pdf`, "dashboard_ejecutivo_inspecciones_sst.pdf", params);

export const registrarFirmaInspeccionSST = async (inspeccionId, payload) => {
  const response = await api.post(`${BASE_URL}/${inspeccionId}/firmas`, payload);
  return response.data;
};

export const cerrarDigitalmenteInspeccionSST = async (inspeccionId, payload = {}) => {
  const response = await api.post(`${BASE_URL}/${inspeccionId}/cierre-digital`, payload);
  return response.data;
};

export const urlArchivoInspeccionSST = (url) => {
  if (!url) return "";

  if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("data:")) {
    return url;
  }

  const API_URL =
    import.meta.env.VITE_API_URL ||
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000";

  return `${API_URL}${url.startsWith("/") ? url : `/${url}`}`;
};

const inspeccionSstApi = {
  listar: listarInspeccionesSST,
  obtener: obtenerInspeccionSST,
  crear: crearInspeccionSST,
  actualizar: actualizarInspeccionSST,
  eliminar: eliminarInspeccionSST,
  dashboard: dashboardInspeccionesSST,
  listarHallazgos: listarHallazgosInspeccionSST,
  crearHallazgo: crearHallazgoInspeccionSST,
  actualizarHallazgo: actualizarHallazgoInspeccionSST,
  eliminarHallazgo: eliminarHallazgoInspeccionSST,
  listarEvidencias: listarEvidenciasInspeccionSST,
  subirEvidencia: subirEvidenciaInspeccionSST,
  eliminarEvidencia: eliminarEvidenciaInspeccionSST,
  excelGeneral: exportarInspeccionesExcelGeneral,
  pdfGeneral: exportarInspeccionesPdfGeneral,
  pdfIndividual: exportarInspeccionPdfIndividual,
  actaPdf: exportarInspeccionActaPdf,
  hallazgosExcel: exportarHallazgosExcel,
  hallazgosPdf: exportarHallazgosPdf,
  seguimientosPdf: exportarSeguimientosPdf,
  dashboardPdf: exportarDashboardEjecutivoInspeccionesPdf,
  registrarFirma: registrarFirmaInspeccionSST,
  cierreDigital: cerrarDigitalmenteInspeccionSST,
};

export default inspeccionSstApi;
