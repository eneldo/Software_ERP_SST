// ============================================================
// API EVIDENCIAS INTELIGENTES MEDIDAS CORRECTIVAS
// ERP SST PRO
// FASE 1.1.8.7.5
// Archivo: frontend/src/api/medidasEvidenciasInteligentesApi.js
// ============================================================

import api from "./axios";

const BASE_URL = "/medidas-correctivas-inteligentes";

export async function obtenerEvidenciasInteligentesMedida(id) {
  const { data } = await api.get(`${BASE_URL}/${id}`);
  return data;
}
