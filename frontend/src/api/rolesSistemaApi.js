// ============================================================
// API ROLES DEL SISTEMA PRO - ERP SST PRO ENTERPRISE
// Archivo: frontend/src/api/rolesSistemaApi.js
// ============================================================

import api from "./axios";
import { normalizarLista } from "./apiHelpers";

export const listarRolesSistemaAdmin = async () => {
  const { data } = await api.get("/roles/");
  return normalizarLista(data);
};

export const crearRolSistema = async (payload) => {
  const { data } = await api.post("/roles/", payload);
  return data;
};

export const actualizarRolSistema = async (rolId, payload) => {
  const { data } = await api.put(`/roles/${rolId}`, payload);
  return data;
};

export const eliminarRolSistema = async (rolId) => {
  const { data } = await api.delete(`/roles/${rolId}`);
  return data;
};
