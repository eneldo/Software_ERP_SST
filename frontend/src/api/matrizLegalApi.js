// ============================================================
// API MATRIZ LEGAL SST
// FASE 1.8.5.2 - MATRIZ LEGAL SST BI EXECUTIVE
// Archivo: frontend/src/api/matrizLegalApi.js
// ============================================================

import api from "./axios";

export const matrizLegalApi = {
  listar: (params = {}) => api.get("/planear/matriz-legal/", { params }),
  obtener: (id) => api.get(`/planear/matriz-legal/${id}`),
  crear: (data) => api.post("/planear/matriz-legal/", data),
  actualizar: (id, data) => api.put(`/planear/matriz-legal/${id}`, data),
  eliminar: (id) => api.delete(`/planear/matriz-legal/${id}`),

  resumen: (empresaId) => api.get(`/planear/matriz-legal/resumen/${empresaId}`),
  dashboard: (empresaId) => api.get(`/planear/matriz-legal/dashboard/${empresaId}`),
  bi: (empresaId) => api.get(`/planear/matriz-legal/bi/${empresaId}`),

  cargarBase: (empresaId) =>
    api.post(`/planear/matriz-legal/cargar-base/${empresaId}`),

  subirEvidencia: (id, formData) =>
    api.post(`/planear/matriz-legal/${id}/evidencia`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
};

export default matrizLegalApi;
