import api from "./axios";
import { limpiarParams, normalizarLista } from "./apiHelpers";

const BASE_URL = "/sst/emergencias";

async function listar(recurso, empresaId) {
  const { data } = await api.get(`${BASE_URL}/${recurso}`, {
    params: limpiarParams({ empresa_id: empresaId }),
  });
  return normalizarLista(data);
}

async function crear(recurso, payload) {
  const { data } = await api.post(`${BASE_URL}/${recurso}`, payload);
  return data;
}

async function actualizar(recurso, id, payload) {
  const { data } = await api.put(`${BASE_URL}/${recurso}/${id}`, payload);
  return data;
}

async function eliminar(recurso, id) {
  const { data } = await api.delete(`${BASE_URL}/${recurso}/${id}`);
  return data;
}

export const listarBrigadas = (empresaId) => listar("brigadas", empresaId);
export const crearBrigada = (payload) => crear("brigadas", payload);
export const actualizarBrigada = (id, payload) => actualizar("brigadas", id, payload);
export const eliminarBrigada = (id) => eliminar("brigadas", id);

export const listarSimulacros = (empresaId) => listar("simulacros", empresaId);
export const crearSimulacro = (payload) => crear("simulacros", payload);
export const actualizarSimulacro = (id, payload) => actualizar("simulacros", id, payload);
export const eliminarSimulacro = (id) => eliminar("simulacros", id);

export const listarAmenazas = (empresaId) => listar("amenazas", empresaId);
export const crearAmenaza = (payload) => crear("amenazas", payload);
export const actualizarAmenaza = (id, payload) => actualizar("amenazas", id, payload);
export const eliminarAmenaza = (id) => eliminar("amenazas", id);

export const listarInspecciones = (empresaId) => listar("inspecciones", empresaId);
export const crearInspeccion = (payload) => crear("inspecciones", payload);
export const actualizarInspeccion = (id, payload) => actualizar("inspecciones", id, payload);
export const eliminarInspeccion = (id) => eliminar("inspecciones", id);

export async function listarIntegrantesBrigada(brigadaId) {
  const { data } = await api.get(`${BASE_URL}/brigadas/${brigadaId}/integrantes`);
  return normalizarLista(data);
}

export async function agregarIntegranteBrigada(brigadaId, payload) {
  const { data } = await api.post(`${BASE_URL}/brigadas/${brigadaId}/integrantes`, payload);
  return data;
}

export async function eliminarIntegranteBrigada(brigadaId, integranteId) {
  const { data } = await api.delete(`${BASE_URL}/brigadas/${brigadaId}/integrantes/${integranteId}`);
  return data;
}
