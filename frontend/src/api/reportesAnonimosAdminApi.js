// ============================================================
// API GESTIÓN ADMINISTRATIVA REPORTES ANÓNIMOS SST
// ERP SST PRO
// FASE 1.1.25.5 — WORKFLOW INTELIGENTE REPORTES SST
// Archivo: frontend/src/api/reportesAnonimosAdminApi.js
// ============================================================

import api from "./axios";

const BASE_URL = "/reportes-anonimos";

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
  if (Array.isArray(data?.casos)) return data.casos;
  return [];
};

export const listarReportesAnonimosSST = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/`, { params: limpiarParams(params) });
  return normalizarLista(data);
};

export const dashboardReportesAnonimosSST = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/dashboard`, { params: limpiarParams(params) });
  return data;
};

export const obtenerReporteAnonimoSST = async (id) => {
  const { data } = await api.get(`${BASE_URL}/${id}`);
  return data;
};

export const actualizarReporteAnonimoSST = async (id, payload) => {
  const { data } = await api.put(`${BASE_URL}/${id}`, payload);
  return data;
};

export const listarResponsablesSST = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/responsables-sst`, { params: limpiarParams(params) });
  return normalizarLista(data);
};

export const listarMisCasosSST = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/mis-casos`, { params: limpiarParams(params) });
  return data;
};

export const asignarReporteAnonimoSST = async (id, payload) => {
  const { data } = await api.put(`${BASE_URL}/${id}/asignar`, payload);
  return data;
};

export const marcarReporteAnonimoEnProcesoSST = async (id) => {
  const { data } = await api.put(`${BASE_URL}/${id}/en-proceso`);
  return data;
};

export const cerrarReporteAnonimoSST = async (id, payload = {}) => {
  const { data } = await api.put(`${BASE_URL}/${id}/cerrar`, payload);
  return data;
};

export const anularReporteAnonimoSST = async (id, motivo = "") => {
  const { data } = await api.put(`${BASE_URL}/${id}/anular`, null, {
    params: limpiarParams({ motivo }),
  });
  return data;
};

export const crearInspeccionDesdeReporteSST = async (id, payload = {}) => {
  const { data } = await api.post(`${BASE_URL}/${id}/convertir/inspeccion`, payload);
  return data;
};

export const crearHallazgoDesdeReporteSST = async (id, payload = {}) => {
  const { data } = await api.post(`${BASE_URL}/${id}/convertir/hallazgo`, payload);
  return data;
};

export const crearCAPADesdeReporteSST = async (id, payload = {}) => {
  const { data } = await api.post(`${BASE_URL}/${id}/convertir/capa`, payload);
  return data;
};

// Compatibilidad con nombres usados en fase 1.1.25.4
export const marcarReporteConvertidoInspeccionSST = crearInspeccionDesdeReporteSST;
export const marcarReporteConvertidoCAPASST = crearCAPADesdeReporteSST;

export const eliminarReporteAnonimoSST = async (id) => {
  const { data } = await api.delete(`${BASE_URL}/${id}`);
  return data;
};

const reportesAnonimosAdminApi = {
  listar: listarReportesAnonimosSST,
  dashboard: dashboardReportesAnonimosSST,
  obtener: obtenerReporteAnonimoSST,
  actualizar: actualizarReporteAnonimoSST,
  responsables: listarResponsablesSST,
  misCasos: listarMisCasosSST,
  asignar: asignarReporteAnonimoSST,
  enProceso: marcarReporteAnonimoEnProcesoSST,
  cerrar: cerrarReporteAnonimoSST,
  anular: anularReporteAnonimoSST,
  crearInspeccion: crearInspeccionDesdeReporteSST,
  crearHallazgo: crearHallazgoDesdeReporteSST,
  crearCAPA: crearCAPADesdeReporteSST,
  convertirInspeccion: crearInspeccionDesdeReporteSST,
  convertirCAPA: crearCAPADesdeReporteSST,
  eliminar: eliminarReporteAnonimoSST,
};

export default reportesAnonimosAdminApi;

// ============================================================
// FASE 1.1.25.6 — Evidencias Inteligentes
// ============================================================
const EVIDENCIAS_URL = "/reportes-evidencias";

export const listarEvidenciasReporteSST = async (reporteId) => {
  const { data } = await api.get(`${EVIDENCIAS_URL}/reporte/${reporteId}`);
  return normalizarLista(data);
};

export const subirEvidenciasReporteSST = async (reporteId, archivos = []) => {
  const formData = new FormData();
  Array.from(archivos || []).forEach((file) => formData.append("archivos", file));
  const { data } = await api.post(`${EVIDENCIAS_URL}/reporte/${reporteId}`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return normalizarLista(data);
};

export const eliminarEvidenciaReporteSST = async (evidenciaId) => {
  const { data } = await api.delete(`${EVIDENCIAS_URL}/${evidenciaId}`);
  return data;
};

export const dashboardEvidenciasReportesSST = async (params = {}) => {
  const { data } = await api.get(`${EVIDENCIAS_URL}/dashboard`, { params: limpiarParams(params) });
  return data;
};

export const timelineReporteSST = async (reporteId) => {
  const { data } = await api.get(`${EVIDENCIAS_URL}/reporte/${reporteId}/timeline`);
  return normalizarLista(data);
};
