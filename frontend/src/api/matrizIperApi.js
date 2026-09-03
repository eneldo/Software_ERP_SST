// ============================================================
// API MATRIZ IPER - GTC 45
// Identificación de Peligros, Evaluación y Valoración de Riesgos
// ============================================================

import api from "./axios";

export const matrizIperApi = {
  listar: (params = {}) => api.get("/planear/matriz-iper/", { params }),
  obtener: (id) => api.get(`/planear/matriz-iper/${id}`),
  crear: (data) => api.post("/planear/matriz-iper/", data),
  crearLote: (filas) => api.post("/planear/matriz-iper/lote", filas),
  actualizar: (id, data) => api.put(`/planear/matriz-iper/${id}`, data),
  actualizarLote: (filas) => api.put("/planear/matriz-iper/lote", filas),
  eliminar: (id) => api.delete(`/planear/matriz-iper/${id}`),
  dashboard: (empresaId) => api.get(`/planear/matriz-iper/dashboard/${empresaId}`),
  exportarExcel: (empresaId) => api.get(`/planear/matriz-iper/exportar/excel/${empresaId}`, { responseType: "blob" }),
  exportarPDF: (empresaId) => api.get(`/planear/matriz-iper/exportar/pdf/${empresaId}`, { responseType: "blob" }),
};

export default matrizIperApi;
