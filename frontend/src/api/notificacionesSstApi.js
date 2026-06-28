// ============================================================
// API NOTIFICACIONES SST ENTERPRISE - ERP SST PRO
// FASE 1.1.24.2 — Frontend Centro de Notificaciones SST
// Archivo: frontend/src/api/notificacionesSstApi.js
// ============================================================

import api from "./axios";

const BASE_URL = "/notificaciones";

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
  if (Array.isArray(data?.notificaciones)) return data.notificaciones;
  return [];
};

export const listarNotificacionesSST = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/`, { params: limpiarParams(params) });
  return normalizarLista(response.data);
};

export const dashboardNotificacionesSST = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/dashboard`, { params: limpiarParams(params) });
  return response.data;
};

export const obtenerNotificacionSST = async (id) => {
  const response = await api.get(`${BASE_URL}/${id}`);
  return response.data;
};

export const marcarNotificacionLeidaSST = async (id) => {
  const response = await api.put(`${BASE_URL}/${id}/leer`);
  return response.data;
};

export const marcarTodasNotificacionesLeidasSST = async (params = {}) => {
  const response = await api.put(`${BASE_URL}/leer-todas`, null, { params: limpiarParams(params) });
  return response.data;
};

export const eliminarNotificacionSST = async (id) => {
  const response = await api.delete(`${BASE_URL}/${id}`);
  return response.data;
};

export const generarNotificacionesSST = async (params = {}) => {
  const response = await api.post(`${BASE_URL}/generar`, null, { params: limpiarParams(params) });
  return response.data;
};

const notificacionesSstApi = {
  listar: listarNotificacionesSST,
  dashboard: dashboardNotificacionesSST,
  obtener: obtenerNotificacionSST,
  leer: marcarNotificacionLeidaSST,
  leerTodas: marcarTodasNotificacionesLeidasSST,
  eliminar: eliminarNotificacionSST,
  generar: generarNotificacionesSST,
};

export default notificacionesSstApi;
