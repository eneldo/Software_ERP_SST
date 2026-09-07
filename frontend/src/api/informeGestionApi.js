// ============================================================
// API INFORME DE GESTIÓN SG-SST
// Archivo: frontend/src/api/informeGestionApi.js
// ============================================================

import api from "./axios";
import { normalizarLista, limpiarParams } from "./apiHelpers";

const BASE_URL = "/api/sgsst/informes-gestion";

const descargarBlob = (response, nombreFallback) => {
  const disposition = response.headers?.["content-disposition"] || "";
  const match = disposition.match(/filename\*?=(?:UTF-8''|\")?([^";]+)/i);
  const fileName = match ? decodeURIComponent(match[1].replace(/"/g, "")) : nombreFallback;

  const blob = new Blob([response.data], {
    type: response.headers?.["content-type"] || "application/octet-stream",
  });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", fileName);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

// ============================================================
// INFORMES PRINCIPALES
// ============================================================

export const listarInformes = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/`, { params: limpiarParams(params) });
  return normalizarLista(response.data);
};

export const obtenerInforme = async (id) => {
  const response = await api.get(`${BASE_URL}/${id}`);
  return response.data;
};

export const crearInforme = async (payload) => {
  const response = await api.post(`${BASE_URL}/`, payload);
  return response.data;
};

export const actualizarInforme = async (id, payload) => {
  const response = await api.put(`${BASE_URL}/${id}`, payload);
  return response.data;
};

export const eliminarInforme = async (id) => {
  const response = await api.delete(`${BASE_URL}/${id}`);
  return response.data;
};

// ============================================================
// CONSOLIDACIÓN Y GENERACIÓN
// ============================================================

export const consolidarInforme = async (informeId, forzar = false) => {
  const response = await api.post(`${BASE_URL}/${informeId}/generar`, {
    informe_id: informeId,
    forzar,
  });
  return response.data;
};

// ============================================================
// FLUJO DE APROBACIÓN
// ============================================================

export const presentarInforme = async (informeId, observaciones = "") => {
  const response = await api.post(`${BASE_URL}/${informeId}/presentar`, {
    informe_id: informeId,
    observaciones,
  });
  return response.data;
};

export const aprobarInforme = async (informeId, resultado, observaciones = "") => {
  const response = await api.post(`${BASE_URL}/${informeId}/aprobar`, {
    informe_id: informeId,
    resultado,
    observaciones,
  });
  return response.data;
};

export const devolverInforme = async (informeId, observaciones = "") => {
  const response = await api.post(`${BASE_URL}/${informeId}/devolver`, null, {
    params: { observaciones },
  });
  return response.data;
};

export const cerrarInforme = async (informeId) => {
  const response = await api.post(`${BASE_URL}/${informeId}/cerrar`);
  return response.data;
};

// ============================================================
// DASHBOARD
// ============================================================

export const dashboardInforme = async (informeId) => {
  const response = await api.get(`${BASE_URL}/${informeId}/dashboard`);
  return response.data;
};

// ============================================================
// SECCIONES
// ============================================================

export const listarSecciones = async (informeId) => {
  const response = await api.get(`${BASE_URL}/${informeId}/secciones`);
  return normalizarLista(response.data);
};

export const actualizarSeccion = async (informeId, seccionId, payload) => {
  const response = await api.put(`${BASE_URL}/${informeId}/secciones/${seccionId}`, payload);
  return response.data;
};

// ============================================================
// EVIDENCIAS
// ============================================================

export const listarEvidencias = async (informeId) => {
  const response = await api.get(`${BASE_URL}/${informeId}/evidencias`);
  return normalizarLista(response.data);
};

export const crearEvidencia = async (informeId, payload) => {
  const response = await api.post(`${BASE_URL}/${informeId}/evidencias`, payload);
  return response.data;
};

export const eliminarEvidencia = async (informeId, evidenciaId) => {
  const response = await api.delete(`${BASE_URL}/${informeId}/evidencias/${evidenciaId}`);
  return response.data;
};

// ============================================================
// RECOMENDACIONES
// ============================================================

export const listarRecomendaciones = async (informeId) => {
  const response = await api.get(`${BASE_URL}/${informeId}/recomendaciones`);
  return normalizarLista(response.data);
};

export const crearRecomendacion = async (informeId, payload) => {
  const response = await api.post(`${BASE_URL}/${informeId}/recomendaciones`, payload);
  return response.data;
};

export const actualizarRecomendacion = async (informeId, recomendacionId, payload) => {
  const response = await api.put(
    `${BASE_URL}/${informeId}/recomendaciones/${recomendacionId}`,
    payload
  );
  return response.data;
};

// ============================================================
// VERSIONES
// ============================================================

export const listarVersiones = async (informeId) => {
  const response = await api.get(`${BASE_URL}/${informeId}/versiones`);
  return normalizarLista(response.data);
};

// ============================================================
// RENDICIÓN DE CUENTAS
// ============================================================

export const listarRendiciones = async (informeId) => {
  const response = await api.get(`${BASE_URL}/${informeId}/rendiciones`);
  return normalizarLista(response.data);
};

export const crearRendicion = async (informeId, payload) => {
  const response = await api.post(`${BASE_URL}/${informeId}/rendiciones`, payload);
  return response.data;
};

export const actualizarRendicion = async (informeId, rendicionId, payload) => {
  const response = await api.put(`${BASE_URL}/${informeId}/rendiciones/${rendicionId}`, payload);
  return response.data;
};

export const crearResponsabilidad = async (informeId, rendicionId, payload) => {
  const response = await api.post(
    `${BASE_URL}/${informeId}/rendiciones/${rendicionId}/responsabilidades`,
    payload
  );
  return response.data;
};

// ============================================================
// AUDITORÍA
// ============================================================

export const auditoriaInforme = async (informeId) => {
  const response = await api.get(`${BASE_URL}/${informeId}/auditoria`);
  return response.data;
};

// ============================================================
// EXPORTACIONES
// ============================================================

export const exportarInformePDF = async (informeId) => {
  const response = await api.get(`${BASE_URL}/${informeId}/pdf`, {
    responseType: "blob",
  });
  descargarBlob(response, `informe_gestion_${informeId}.pdf`);
};

export const exportarInformeExcel = async (informeId) => {
  const response = await api.get(`${BASE_URL}/${informeId}/excel`, {
    responseType: "blob",
  });
  descargarBlob(response, `informe_gestion_${informeId}.xlsx`);
};

// ============================================================
// OBJETO API DEFAULT
// ============================================================

const informeGestionApi = {
  listar: listarInformes,
  obtener: obtenerInforme,
  crear: crearInforme,
  actualizar: actualizarInforme,
  eliminar: eliminarInforme,
  consolidar: consolidarInforme,
  presentar: presentarInforme,
  aprobar: aprobarInforme,
  devolver: devolverInforme,
  cerrar: cerrarInforme,
  dashboard: dashboardInforme,
  listarSecciones,
  actualizarSeccion,
  listarEvidencias,
  crearEvidencia,
  eliminarEvidencia,
  listarRecomendaciones,
  crearRecomendacion,
  actualizarRecomendacion,
  listarVersiones,
  listarRendiciones,
  crearRendicion,
  actualizarRendicion,
  crearResponsabilidad,
  auditoriaInforme,
  exportarPDF: exportarInformePDF,
  exportarExcel: exportarInformeExcel,
};

export default informeGestionApi;
