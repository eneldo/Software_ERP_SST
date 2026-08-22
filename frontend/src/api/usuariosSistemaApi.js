// ============================================================
// API USUARIOS DEL SISTEMA PRO
// ERP SST PRO ENTERPRISE
// FASE HARDENING — CRUD completo de usuarios
// ============================================================

import api from "./axios";
import { normalizarLista } from "./apiHelpers";

export const listarUsuariosSistema = async (params = {}) => {
  const response = await api.get("/usuarios-sistema/", { params });
  return normalizarLista(response.data);
};

export const obtenerUsuarioSistema = async (id) => {
  const response = await api.get(`/usuarios-sistema/${id}`);
  return response.data;
};

export const crearUsuarioSistema = async (data) => {
  const response = await api.post("/usuarios-sistema/", data);
  return response.data;
};

export const actualizarUsuarioSistema = async (id, data) => {
  const response = await api.put(`/usuarios-sistema/${id}`, data);
  return response.data;
};

export const cambiarPasswordUsuarioSistema = async (id, password) => {
  const response = await api.patch(`/usuarios-sistema/${id}/password`, { password });
  return response.data;
};

export const cambiarEstadoUsuarioSistema = async (id) => {
  const response = await api.patch(`/usuarios-sistema/${id}/toggle-activo`);
  return response.data;
};

export const eliminarUsuarioSistema = async (id) => {
  const response = await api.delete(`/usuarios-sistema/${id}`);
  return response.data;
};

export const obtenerStatsUsuariosSistema = async () => {
  const response = await api.get("/usuarios-sistema/stats");
  return response.data;
};

export const listarRolesSistema = async () => {
  const response = await api.get("/usuarios-sistema/roles-disponibles");
  return normalizarLista(response.data);
};
