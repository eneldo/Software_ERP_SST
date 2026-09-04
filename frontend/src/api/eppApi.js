// ============================================================
// API EPP SST ENTERPRISE - ERP SST PRO
// FASE 1.1.7.1 — EPP SST BASE
// Archivo: frontend/src/api/eppApi.js
// ============================================================

import api from "./axios";
import { normalizarLista, limpiarParams } from "./apiHelpers";

const BASE_URL = "/epp";

export const listarCatalogoEPP = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/catalogo`, { params: limpiarParams(params) });
  return normalizarLista(response.data);
};

export const crearCatalogoEPP = async (payload) => {
  const response = await api.post(`${BASE_URL}/catalogo`, payload);
  return response.data;
};

export const actualizarCatalogoEPP = async (id, payload) => {
  const response = await api.put(`${BASE_URL}/catalogo/${id}`, payload);
  return response.data;
};

export const eliminarCatalogoEPP = async (id) => {
  const response = await api.delete(`${BASE_URL}/catalogo/${id}`);
  return response.data;
};

export const subirFichaTecnicaEPP = async (catalogoId, formData) => {
  const response = await api.post(`${BASE_URL}/catalogo/${catalogoId}/ficha-tecnica`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const eliminarFichaTecnicaEPP = async (catalogoId) => {
  const response = await api.delete(`${BASE_URL}/catalogo/${catalogoId}/ficha-tecnica`);
  return response.data;
};

export const listarEntregasEPP = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/entregas`, { params: limpiarParams(params) });
  return normalizarLista(response.data);
};

export const obtenerEntregaEPP = async (id) => {
  const response = await api.get(`${BASE_URL}/entregas/${id}`);
  return response.data;
};

export const crearEntregaEPP = async (payload) => {
  const response = await api.post(`${BASE_URL}/entregas`, payload);
  return response.data;
};

export const actualizarEntregaEPP = async (id, payload) => {
  const response = await api.put(`${BASE_URL}/entregas/${id}`, payload);
  return response.data;
};

export const marcarRecibidoEPP = async (id, recibido = true) => {
  const response = await api.patch(`${BASE_URL}/entregas/${id}/recibido`, null, { params: { recibido } });
  return response.data;
};

export const eliminarEntregaEPP = async (id) => {
  const response = await api.delete(`${BASE_URL}/entregas/${id}`);
  return response.data;
};

export const crearEntregaLoteEPP = async (payload) => {
  const response = await api.post(`${BASE_URL}/entregas/lote`, payload);
  return response.data;
};

export const consolidadoEntregasEPP = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/entregas/consolidado`, { params: limpiarParams(params) });
  return normalizarLista(response.data);
};

export const dashboardEPP = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/dashboard`, { params: limpiarParams(params) });
  return response.data;
};

export const listarEvidenciasEPP = async (entregaId) => {
  const response = await api.get(`${BASE_URL}/entregas/${entregaId}/evidencias`);
  return normalizarLista(response.data);
};

export const subirEvidenciaEPP = async (entregaId, formData) => {
  const response = await api.post(`${BASE_URL}/entregas/${entregaId}/evidencias`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const eliminarEvidenciaEPP = async (entregaId, archivoId) => {
  const response = await api.delete(`${BASE_URL}/entregas/${entregaId}/evidencias/${archivoId}`);
  return response.data;
};

export const firmarEntregaEPP = async (entregaId, payload) => {
  const response = await api.post(`${BASE_URL}/entregas/${entregaId}/firma`, payload);
  return response.data;
};

export const urlDescargaArchivoEPP = (url) => url;

const descargarBlob = (response, nombreFallback) => {
  const blob = new Blob([response.data], {
    type: response.headers?.["content-type"] || "application/octet-stream",
  });
  const disposition = response.headers?.["content-disposition"] || "";
  const match = disposition.match(/filename="?([^"]+)"?/i);
  const filename = match?.[1] || nombreFallback;

  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

const descargarArchivo = async (endpoint, nombreFallback, params = {}) => {
  const response = await api.get(endpoint, {
    params: limpiarParams(params),
    responseType: "blob",
  });
  descargarBlob(response, nombreFallback);
  return true;
};

export const exportarCatalogoEPPExcel = (params = {}) =>
  descargarArchivo(`${BASE_URL}/export/catalogo/excel`, "catalogo_epp_sst.xlsx", params);

export const exportarEntregasEPPExcel = (params = {}) =>
  descargarArchivo(`${BASE_URL}/export/entregas/excel`, "entregas_epp_sst.xlsx", params);

export const exportarEntregasEPPPDF = (params = {}) =>
  descargarArchivo(`${BASE_URL}/export/entregas/pdf`, "entregas_epp_sst.pdf", params);

export const exportarFichaEntregaEPPPDF = (entregaId) =>
  descargarArchivo(`${BASE_URL}/export/entregas/${entregaId}/pdf`, `ficha_entrega_epp_${entregaId}.pdf`);

export const exportarReposicionesEPPExcel = (dias = 30) =>
  descargarArchivo(`${BASE_URL}/export/reposiciones/excel`, `reposiciones_epp_${dias}_dias.xlsx`, { dias });

export const exportarReposicionesEPPPDF = (dias = 30) =>
  descargarArchivo(`${BASE_URL}/export/reposiciones/pdf`, `reposiciones_epp_${dias}_dias.pdf`, { dias });

export const exportarPendientesFirmaEPPExcel = () =>
  descargarArchivo(`${BASE_URL}/export/firmas/excel`, "pendientes_firma_epp.xlsx");

export const exportarPendientesFirmaEPPPDF = () =>
  descargarArchivo(`${BASE_URL}/export/firmas/pdf`, "pendientes_firma_epp.pdf");

const eppApi = {
  listarCatalogo: listarCatalogoEPP,
  crearCatalogo: crearCatalogoEPP,
  actualizarCatalogo: actualizarCatalogoEPP,
  eliminarCatalogo: eliminarCatalogoEPP,
  subirFichaTecnica: subirFichaTecnicaEPP,
  eliminarFichaTecnica: eliminarFichaTecnicaEPP,
  listarEntregas: listarEntregasEPP,
  obtenerEntrega: obtenerEntregaEPP,
  crearEntrega: crearEntregaEPP,
  actualizarEntrega: actualizarEntregaEPP,
  marcarRecibido: marcarRecibidoEPP,
  eliminarEntrega: eliminarEntregaEPP,
  crearEntregaLote: crearEntregaLoteEPP,
  consolidadoEntregas: consolidadoEntregasEPP,
  dashboard: dashboardEPP,
  listarEvidencias: listarEvidenciasEPP,
  subirEvidencia: subirEvidenciaEPP,
  eliminarEvidencia: eliminarEvidenciaEPP,
  firmarEntrega: firmarEntregaEPP,
  exportarCatalogoExcel: exportarCatalogoEPPExcel,
  exportarEntregasExcel: exportarEntregasEPPExcel,
  exportarEntregasPDF: exportarEntregasEPPPDF,
  exportarFichaEntregaPDF: exportarFichaEntregaEPPPDF,
  exportarReposicionesExcel: exportarReposicionesEPPExcel,
  exportarReposicionesPDF: exportarReposicionesEPPPDF,
  exportarPendientesFirmaExcel: exportarPendientesFirmaEPPExcel,
  exportarPendientesFirmaPDF: exportarPendientesFirmaEPPPDF,
};

export default eppApi;
