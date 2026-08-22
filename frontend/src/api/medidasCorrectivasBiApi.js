// ============================================================
// API DASHBOARD BI MEDIDAS CORRECTIVAS
// ERP SST PRO
// FASE 1.1.8.7.5.4
// Archivo: frontend/src/api/medidasCorrectivasBiApi.js
// ============================================================

import api from "./axios";
import { limpiarParams } from "./apiHelpers";

const BASE_URL = "/medidas-correctivas-bi";

export async function obtenerDashboardBiMedidasCorrectivas(params = {}) {
  const { data } = await api.get(`${BASE_URL}/dashboard`, { params: limpiarParams(params) });
  return data;
}
