// ============================================================
// API INDICADORES SST BI EXECUTIVE
// FASE 1.1.18.1 — NÚCLEO INDICADORES SST
// Archivo: frontend/src/api/indicadorSstApi.js
// ============================================================

import api from "./axios";
import { normalizarLista, limpiarParams } from "./apiHelpers";

const BASE_URL = "/indicadores";

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

export const listarIndicadoresSST = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/`, { params: limpiarParams(params) });
  return normalizarLista(response.data);
};

export const dashboardIndicadoresSST = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/dashboard/resumen`, { params: limpiarParams(params) });
  return response.data;
};

export const obtenerIndicadorSST = async (id) => {
  const response = await api.get(`${BASE_URL}/${id}`);
  return response.data;
};

export const crearIndicadorSST = async (payload) => {
  const response = await api.post(`${BASE_URL}/`, payload);
  return response.data;
};

export const actualizarIndicadorSST = async (id, payload) => {
  const response = await api.put(`${BASE_URL}/${id}`, payload);
  return response.data;
};

export const eliminarIndicadorSST = async (id) => {
  const response = await api.delete(`${BASE_URL}/${id}`);
  return response.data;
};

export const exportarIndicadoresExcel = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/export/excel`, {
    params: limpiarParams(params),
    responseType: "blob",
  });
  descargarBlob(response, "indicadores_sst_bi_executive.xlsx");
};

export const exportarIndicadoresPDF = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/export/pdf`, {
    params: limpiarParams(params),
    responseType: "blob",
  });
  descargarBlob(response, "indicadores_sst_bi_executive.pdf");
};

export const exportarDashboardIndicadoresPDF = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/export/dashboard-pdf`, {
    params: limpiarParams(params),
    responseType: "blob",
  });
  descargarBlob(response, "dashboard_indicadores_sst.pdf");
};

const indicadorSstApi = {
  listar: listarIndicadoresSST,
  dashboard: dashboardIndicadoresSST,
  obtener: obtenerIndicadorSST,
  crear: crearIndicadorSST,
  actualizar: actualizarIndicadorSST,
  eliminar: eliminarIndicadorSST,
  exportarExcel: exportarIndicadoresExcel,
  exportarPDF: exportarIndicadoresPDF,
  exportarDashboardPDF: exportarDashboardIndicadoresPDF,
};

export default indicadorSstApi;
