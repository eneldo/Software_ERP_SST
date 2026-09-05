import api from "./axios";
import { limpiarParams, normalizarLista } from "./apiHelpers";

const BASE_URL = "/sst/comites";

export async function listarComites(params = {}) {
  const { data } = await api.get(`${BASE_URL}/`, { params: limpiarParams(params) });
  return normalizarLista(data);
}

export async function crearComite(payload) {
  const { data } = await api.post(`${BASE_URL}/`, payload);
  return data;
}

export async function actualizarComite(id, payload) {
  const { data } = await api.put(`${BASE_URL}/${id}`, payload);
  return data;
}

export async function eliminarComite(id) {
  const { data } = await api.delete(`${BASE_URL}/${id}`);
  return data;
}

export async function listarIntegrantes(comiteId) {
  const { data } = await api.get(`${BASE_URL}/${comiteId}/integrantes`);
  return normalizarLista(data);
}

export async function agregarIntegrante(comiteId, payload) {
  const { data } = await api.post(`${BASE_URL}/${comiteId}/integrantes`, payload);
  return data;
}

export async function eliminarIntegrante(comiteId, integranteId) {
  const { data } = await api.delete(`${BASE_URL}/${comiteId}/integrantes/${integranteId}`);
  return data;
}

export async function listarReuniones(comiteId) {
  const { data } = await api.get(`${BASE_URL}/${comiteId}/reuniones`);
  return normalizarLista(data);
}

export async function crearReunion(comiteId, payload) {
  const { data } = await api.post(`${BASE_URL}/${comiteId}/reuniones`, payload);
  return data;
}
