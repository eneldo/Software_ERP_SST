// ============================================================
// API PORTAL DEL EMPLEADO SST - ERP SST PRO
// FASE 1.1.25.2 — FRONTEND PORTAL DEL EMPLEADO SST
// Archivo: frontend/src/api/portalEmpleadoApi.js
// ============================================================

import api from "./axios";
import { resolveFileUrl } from "../utils/fileUrl";
import { normalizarLista, limpiarParams } from "./apiHelpers";

const BASE_URL = "/portal-empleado";

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

export const obtenerPerfilEmpleadoSST = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/mi-perfil`, { params: limpiarParams(params) });
  return data;
};

export const dashboardPortalEmpleadoSST = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/dashboard`, { params: limpiarParams(params) });
  return data;
};

export const resumenPortalEmpleadoSST = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/resumen`, { params: limpiarParams(params) });
  return data;
};

export const listarMisCapacitacionesSST = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/mis-capacitaciones`, { params: limpiarParams(params) });
  return normalizarLista(data);
};

export const listarMisEPPSST = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/mis-epp`, { params: limpiarParams(params) });
  return normalizarLista(data);
};

export const listarMisExamenesSST = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/mis-examenes`, { params: limpiarParams(params) });
  return normalizarLista(data);
};

export const listarReportesEmpleadoSST = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/reportes`, { params: limpiarParams(params) });
  return normalizarLista(data);
};

export const obtenerReporteEmpleadoSST = async (id) => {
  const { data } = await api.get(`${BASE_URL}/reportes/${id}`);
  return data;
};

export const crearReporteEmpleadoSST = async (payload) => {
  const { data } = await api.post(`${BASE_URL}/reportes`, payload);
  return data;
};

export const crearReporteEmpleadoFormSST = async (formData) => {
  const { data } = await api.post(`${BASE_URL}/reportes/form`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};

export const subirEvidenciaReporteEmpleadoSST = async (reporteId, formData) => {
  const { data } = await api.post(`${BASE_URL}/reportes/${reporteId}/evidencia`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};

export const actualizarReporteEmpleadoSST = async (id, payload) => {
  const { data } = await api.put(`${BASE_URL}/reportes/${id}`, payload);
  return data;
};

export const cambiarEstadoReporteEmpleadoSST = async (id, payload) => {
  const { data } = await api.patch(`${BASE_URL}/reportes/${id}/estado`, payload);
  return data;
};

export const eliminarReporteEmpleadoSST = async (id) => {
  const { data } = await api.delete(`${BASE_URL}/reportes/${id}`);
  return data;
};

export const exportarReportesEmpleadoExcel = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/reportes/export/excel`, {
    params: limpiarParams(params),
    responseType: "blob",
  });
  descargarBlob(response, "reportes_portal_empleado_sst.xlsx");
};

export const urlArchivoPortalEmpleadoSST = resolveFileUrl;

export const esImagenReporteSST = (archivo = {}) => {
  const mime = String(archivo?.archivo_mime_type || archivo?.mime_type || "").toLowerCase();
  const nombre = String(archivo?.archivo_nombre || archivo?.nombre_original || "").toLowerCase();
  return mime.startsWith("image/") || /\.(jpg|jpeg|png|webp)$/i.test(nombre);
};

export const esPdfReporteSST = (archivo = {}) => {
  const mime = String(archivo?.archivo_mime_type || archivo?.mime_type || "").toLowerCase();
  const nombre = String(archivo?.archivo_nombre || archivo?.nombre_original || "").toLowerCase();
  return mime.includes("pdf") || nombre.endsWith(".pdf");
};

export const esVideoReporteSST = (archivo = {}) => {
  const mime = String(archivo?.archivo_mime_type || archivo?.mime_type || "").toLowerCase();
  const nombre = String(archivo?.archivo_nombre || archivo?.nombre_original || "").toLowerCase();
  return mime.startsWith("video/") || /\.(mp4|mov|webm)$/i.test(nombre);
};

const portalEmpleadoApi = {
  perfil: obtenerPerfilEmpleadoSST,
  dashboard: dashboardPortalEmpleadoSST,
  resumen: resumenPortalEmpleadoSST,
  capacitaciones: listarMisCapacitacionesSST,
  epp: listarMisEPPSST,
  examenes: listarMisExamenesSST,
  reportes: listarReportesEmpleadoSST,
  obtenerReporte: obtenerReporteEmpleadoSST,
  crearReporte: crearReporteEmpleadoSST,
  crearReporteForm: crearReporteEmpleadoFormSST,
  subirEvidencia: subirEvidenciaReporteEmpleadoSST,
  actualizarReporte: actualizarReporteEmpleadoSST,
  cambiarEstado: cambiarEstadoReporteEmpleadoSST,
  eliminarReporte: eliminarReporteEmpleadoSST,
};

export default portalEmpleadoApi;
