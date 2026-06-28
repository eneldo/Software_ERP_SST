// ============================================================
// API DASHBOARD BI MEDIDAS CORRECTIVAS
// ERP SST PRO
// FASE 1.1.8.7.5.4
// Archivo: frontend/src/api/medidasCorrectivasBiApi.js
// ============================================================

import api from "./axios";

const BASE_URL = "/medidas-correctivas-bi";

function cleanParams(params = {}) {
  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== "" && value !== null && value !== undefined)
  );
}

export async function obtenerDashboardBiMedidasCorrectivas(params = {}) {
  const { data } = await api.get(`${BASE_URL}/dashboard`, { params: cleanParams(params) });
  return data;
}
