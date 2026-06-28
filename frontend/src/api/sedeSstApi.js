// ============================================================
// API SEDES SST ANALYTICS PRO
// Archivo: frontend/src/api/sedeSstApi.js
// FASE 1.1.2.4 — Sedes SST Analytics PRO
// ============================================================

import api from "./axios";

/**
 * Lista sedes con filtros opcionales soportados por el backend.
 */
export const listarSedesSST = async (params = {}) => {
  const response = await api.get("/sedes/", { params });
  return response.data;
};

/**
 * Obtiene el resumen KPI de sedes.
 */
export const obtenerDashboardSedesSST = async (params = {}) => {
  const response = await api.get("/sedes/dashboard/resumen", { params });
  return response.data;
};

/**
 * Obtiene una sede por ID.
 */
export const obtenerSedeSST = async (id) => {
  const response = await api.get(`/sedes/${id}`);
  return response.data;
};

/**
 * Crea una nueva sede.
 */
export const crearSedeSST = async (data) => {
  const response = await api.post("/sedes/", data);
  return response.data;
};

/**
 * Actualiza una sede existente.
 */
export const actualizarSedeSST = async (id, data) => {
  const response = await api.put(`/sedes/${id}`, data);
  return response.data;
};

/**
 * Desactiva lógicamente una sede.
 */
export const eliminarSedeSST = async (id) => {
  const response = await api.delete(`/sedes/${id}`);
  return response.data;
};

/**
 * Activa o desactiva una sede usando PATCH /sedes/{id}/estado.
 */
export const cambiarEstadoSedeSST = async (id, activo) => {
  const response = await api.patch(`/sedes/${id}/estado`, null, {
    params: { activo },
  });
  return response.data;
};

/**
 * Lista empresas para selector Empresa -> Sede.
 */
export const listarEmpresasParaSedesSST = async () => {
  const response = await api.get("/empresas/");
  return response.data;
};
