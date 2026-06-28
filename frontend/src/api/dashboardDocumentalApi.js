// ============================================================
// API: Dashboard Documental SST Enterprise
// Archivo: frontend/src/api/dashboardDocumentalApi.js
// FASE 1.8.4.3.9.2 - Centro Documental Enterprise Visual PRO
// ============================================================

import api from "./axios";

export const dashboardDocumentalApi = {
  resumen: (params = {}) => api.get("/dashboard-documental/resumen", { params }),
  vencimientos: (params = {}) => api.get("/dashboard-documental/vencimientos", { params }),
  indicadores: (params = {}) => api.get("/dashboard-documental/indicadores", { params }),

  documentosEnterprise: (params = {}) =>
    api.get("/documental-enterprise/documentos", { params }),

  alertasEnterprise: (params = {}) =>
    api.get("/documental-enterprise/alertas", { params }),

  historialEnterprise: (documentoId) =>
    api.get(`/documental-enterprise/historial/${documentoId}`),

  cambiarEstadoEnterprise: (documentoId, params = {}) =>
    api.patch(`/documental-enterprise/documentos/${documentoId}/estado`, null, { params }),
};

export default dashboardDocumentalApi;
