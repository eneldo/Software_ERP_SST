import api from "./axios";
import { limpiarParams } from "./apiHelpers";

const BASE_URL = "/profesiograma";

// ── Tipos de Evaluación ─────────────────────────────────────

export const listarTiposEvaluacion = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/tipos-evaluacion`, { params: limpiarParams(params) });
  return data;
};

export const crearTipoEvaluacion = async (payload) => {
  const { data } = await api.post(`${BASE_URL}/tipos-evaluacion`, payload);
  return data;
};

export const actualizarTipoEvaluacion = async (id, payload) => {
  const { data } = await api.put(`${BASE_URL}/tipos-evaluacion/${id}`, payload);
  return data;
};

export const eliminarTipoEvaluacion = async (id) => {
  const { data } = await api.delete(`${BASE_URL}/tipos-evaluacion/${id}`);
  return data;
};

// ── Catálogo de Exámenes ────────────────────────────────────

export const listarExamenesCatalogo = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/examenes-catalogo`, { params: limpiarParams(params) });
  return data;
};

export const crearExamenCatalogo = async (payload) => {
  const { data } = await api.post(`${BASE_URL}/examenes-catalogo`, payload);
  return data;
};

export const actualizarExamenCatalogo = async (id, payload) => {
  const { data } = await api.put(`${BASE_URL}/examenes-catalogo/${id}`, payload);
  return data;
};

export const eliminarExamenCatalogo = async (id) => {
  const { data } = await api.delete(`${BASE_URL}/examenes-catalogo/${id}`);
  return data;
};

// ── Profesiograma ───────────────────────────────────────────

export const obtenerProfesiograma = async (cargoId) => {
  const { data } = await api.get(`${BASE_URL}/cargo/${cargoId}`);
  return data;
};

export const guardarProfesiograma = async (cargoId, payload) => {
  const { data } = await api.post(`${BASE_URL}/cargo/${cargoId}`, payload);
  return data;
};

export const eliminarProfesiograma = async (profesiogramaId) => {
  const { data } = await api.delete(`${BASE_URL}/${profesiogramaId}`);
  return data;
};

export const listarProfesiogramas = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/listar`, { params: limpiarParams(params) });
  return data;
};
