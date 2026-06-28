// ============================================================
// API REPORTE ANÓNIMO SST PÚBLICO - ERP SST PRO
// FASE 1.1.25.6 — Evidencias Inteligentes
// Archivo: frontend/src/api/reporteAnonimoSstApi.js
// ============================================================

import api from "./axios";

const BASE_URL = "/reporte-anonimo-sst";

export const obtenerOpcionesReporteAnonimoSST = async () => {
  const { data } = await api.get(`${BASE_URL}/opciones`, { skipAuth: true });
  return data;
};

export const crearReporteAnonimoSST = async (formData) => {
  const { data } = await api.post(`${BASE_URL}/reportes`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    skipAuth: true,
  });
  return data;
};

export default {
  opciones: obtenerOpcionesReporteAnonimoSST,
  crear: crearReporteAnonimoSST,
};
