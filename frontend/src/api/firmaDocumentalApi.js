// ============================================================
// API: Firma y Aprobación Digital Documental SST
// Archivo: frontend/src/api/firmaDocumentalApi.js
// FASE 1.8.4.3.10.5 - Firma Gerencia + Certificado PDF Oficial
// ============================================================

import api from "./axios";

export const firmaDocumentalApi = {
  resumen: (params = {}) => api.get("/firma-documental/resumen", { params }),

  documentos: (params = {}) => api.get("/firma-documental/documentos", { params }),

  historial: (documentoId) =>
    api.get(`/firma-documental/historial/${documentoId}`),

  workflow: (documentoId) =>
    api.get(`/firma-documental/workflow/${documentoId}`),

  certificado: (firmaDocumentalId) =>
    api.get(`/firma-documental/certificado/${firmaDocumentalId}`),

  firmar: (payload) => api.post("/firma-documental/firmar", payload),

  aprobar: (documentoId, payload = {}) =>
    api.post(`/firma-documental/documento/${documentoId}/aprobar`, payload),

  rechazar: (documentoId, payload = {}) =>
    api.post(`/firma-documental/documento/${documentoId}/rechazar`, payload),

  anular: (firmaDocumentalId) =>
    api.delete(`/firma-documental/${firmaDocumentalId}`),
};

export default firmaDocumentalApi;
