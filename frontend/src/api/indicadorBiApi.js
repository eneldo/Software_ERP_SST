// ============================================================
// API INDICADORES BI EXECUTIVE SST ENTERPRISE
// FASE 1.1.18.2 — BI EXECUTIVE SST ENTERPRISE
// Archivo: frontend/src/api/indicadorBiApi.js
// ============================================================

import api from "./axios";

const BASE_URL = "/indicadores/bi";

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
  return [];
};

export const obtenerResumenBI = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/resumen`, { params: limpiarParams(params) });
  return data;
};

export const obtenerTendenciasBI = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/tendencias`, { params: limpiarParams(params) });
  return normalizarLista(data);
};

export const obtenerRankingSedesBI = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/ranking-sedes`, { params: limpiarParams(params) });
  return normalizarLista(data);
};

export const obtenerRankingAreasBI = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/ranking-areas`, { params: limpiarParams(params) });
  return normalizarLista(data);
};

export const obtenerTopRiesgosBI = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/top-riesgos`, { params: limpiarParams(params) });
  return normalizarLista(data);
};

export const obtenerTopHallazgosBI = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/top-hallazgos`, { params: limpiarParams(params) });
  return normalizarLista(data);
};

export const obtenerResumenCompletoBI = async (params = {}) => {
  const { data } = await api.get(`${BASE_URL}/resumen-completo`, { params: limpiarParams(params) });
  return data;
};

const indicadorBiApi = {
  resumen: obtenerResumenBI,
  tendencias: obtenerTendenciasBI,
  rankingSedes: obtenerRankingSedesBI,
  rankingAreas: obtenerRankingAreasBI,
  topRiesgos: obtenerTopRiesgosBI,
  topHallazgos: obtenerTopHallazgosBI,
  resumenCompleto: obtenerResumenCompletoBI,
};

export default indicadorBiApi;
