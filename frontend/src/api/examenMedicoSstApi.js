// ============================================================
// API EXÁMENES MÉDICOS SST - ERP SST PRO
// FASE 1.1.6.2.1 — EVIDENCIAS MÉDICAS ENTERPRISE
// Archivo: frontend/src/api/examenMedicoSstApi.js
// ============================================================

import api from "./axios";
import { resolveFileUrl } from "../utils/fileUrl";
import { normalizarLista, limpiarParams } from "./apiHelpers";

const BASE_URL = "/examenes-medicos";

export const generarExamenesDesdeProfesiograma = async (empleadoId, data = {}) => {
  const response = await api.post(`${BASE_URL}/empleado/${empleadoId}/generar-desde-profesiograma`, data);
  return response.data;
};

export const listarExamenesMedicosSST = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/`, { params: limpiarParams(params) });
  return normalizarLista(response.data);
};

export const obtenerExamenMedicoSST = async (id) => {
  const response = await api.get(`${BASE_URL}/${id}`);
  return response.data;
};

export const crearExamenMedicoSST = async (payload) => {
  const response = await api.post(`${BASE_URL}/`, payload);
  return response.data;
};

export const actualizarExamenMedicoSST = async (id, payload) => {
  const response = await api.put(`${BASE_URL}/${id}`, payload);
  return response.data;
};

export const cambiarEstadoExamenMedicoSST = async (id, activo) => {
  const response = await api.patch(`${BASE_URL}/${id}/estado`, null, { params: { activo } });
  return response.data;
};

export const eliminarExamenMedicoSST = async (id) => {
  const response = await api.delete(`${BASE_URL}/${id}`);
  return response.data;
};

export const dashboardExamenesMedicosSST = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/dashboard`, { params: limpiarParams(params) });
  return response.data;
};


const descargarBlob = (blob, fallbackName) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fallbackName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

const descargarArchivo = async (endpoint, params = {}, fallbackName = "archivo") => {
  const response = await api.get(endpoint, {
    params: limpiarParams(params),
    responseType: "blob",
  });
  descargarBlob(response.data, fallbackName);
  return true;
};

export const exportarExamenesMedicosExcelSST = async (params = {}) =>
  descargarArchivo(`${BASE_URL}/export/excel`, params, "examenes_medicos_sst.xlsx");

export const exportarExamenesMedicosPdfSST = async (params = {}) =>
  descargarArchivo(`${BASE_URL}/export/pdf`, params, "reporte_examenes_medicos_sst.pdf");

export const exportarVencimientosExamenesPdfSST = async (params = {}) =>
  descargarArchivo(`${BASE_URL}/export/vencimientos/pdf`, params, "vencimientos_examenes_medicos_sst.pdf");

export const exportarRestriccionesExamenesPdfSST = async (params = {}) =>
  descargarArchivo(`${BASE_URL}/export/restricciones/pdf`, params, "restricciones_medicas_sst.pdf");

export const exportarFichaExamenMedicoPdfSST = async (id) =>
  descargarArchivo(`${BASE_URL}/${id}/export/pdf`, {}, `ficha_examen_medico_${id}.pdf`);

export const listarEvidenciasExamenMedicoSST = async (id) => {
  const response = await api.get(`${BASE_URL}/${id}/evidencias`);
  return normalizarLista(response.data);
};

export const subirEvidenciaExamenMedicoSST = async (id, file, descripcion = "", tipoEvidencia = "OTRO") => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("tipo_evidencia", tipoEvidencia || "OTRO");
  formData.append("descripcion", descripcion || "Evidencia médica ocupacional");

  const response = await api.post(`${BASE_URL}/${id}/evidencias`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const eliminarEvidenciaExamenMedicoSST = async (id, archivoId) => {
  const response = await api.delete(`${BASE_URL}/${id}/evidencias/${archivoId}`);
  return response.data;
};

export const obtenerUrlArchivoSST = resolveFileUrl;

export const abrirArchivoSST = (url) => {
  const finalUrl = resolveFileUrl(url);
  if (!finalUrl) return;
  window.open(finalUrl, "_blank", "noopener,noreferrer");
};

const examenMedicoSstApi = {
  listar: listarExamenesMedicosSST,
  obtener: obtenerExamenMedicoSST,
  crear: crearExamenMedicoSST,
  actualizar: actualizarExamenMedicoSST,
  cambiarEstado: cambiarEstadoExamenMedicoSST,
  eliminar: eliminarExamenMedicoSST,
  dashboard: dashboardExamenesMedicosSST,
  exportarExcel: exportarExamenesMedicosExcelSST,
  exportarPdf: exportarExamenesMedicosPdfSST,
  exportarVencimientosPdf: exportarVencimientosExamenesPdfSST,
  exportarRestriccionesPdf: exportarRestriccionesExamenesPdfSST,
  exportarFichaPdf: exportarFichaExamenMedicoPdfSST,
  generarDesdeProfesiograma: generarExamenesDesdeProfesiograma,
  evidencias: listarEvidenciasExamenMedicoSST,
  subirEvidencia: subirEvidenciaExamenMedicoSST,
  eliminarEvidencia: eliminarEvidenciaExamenMedicoSST,
  abrirArchivo: abrirArchivoSST,
  obtenerUrlArchivo: obtenerUrlArchivoSST,
};

export default examenMedicoSstApi;
