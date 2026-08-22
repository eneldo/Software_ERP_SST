// ============================================================
// API PERMISOS DEL SISTEMA PRO - ERP SST PRO ENTERPRISE
// Archivo: frontend/src/api/permisosSistemaApi.js
// ============================================================

import api from "./axios";
import { normalizarLista } from "./apiHelpers";

export const listarPermisosSistema = async () => {
  const { data } = await api.get("/permisos/");
  return normalizarLista(data);
};

export const crearPermisoSistema = async (payload) => {
  const { data } = await api.post("/permisos/", payload);
  return data;
};

export const actualizarPermisoSistema = async (id, payload) => {
  const { data } = await api.put(`/permisos/${id}`, payload);
  return data;
};

export const eliminarPermisoSistema = async (id) => {
  const { data } = await api.delete(`/permisos/${id}`);
  return data;
};

export const obtenerPermisosUsuarioSistema = async (usuarioId) => {
  const { data } = await api.get(`/permisos/usuario/${usuarioId}`);
  return data;
};

export const asignarPermisosUsuarioSistema = async (usuarioId, permisosIds) => {
  const { data } = await api.post("/permisos/usuario/asignar", {
    usuario_id: Number(usuarioId),
    permisos_ids: permisosIds.map((id) => Number(id)),
  });
  return data;
};

export const obtenerMisPermisosSistema = async () => {
  const { data } = await api.get("/permisos/mis-permisos");
  return data;
};
