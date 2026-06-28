import api from "./axios";

export const evaluacionInicialApi = {
  listar: (params = {}) => api.get("/planear/evaluacion-inicial/", { params }),

  obtener: (id) => api.get(`/planear/evaluacion-inicial/${id}`),

  crear: (data) => api.post("/planear/evaluacion-inicial/", data),

  actualizar: (id, data) => api.put(`/planear/evaluacion-inicial/${id}`, data),

  agregarItem: (evaluacionId, data) =>
    api.post(`/planear/evaluacion-inicial/${evaluacionId}/items`, data),

  actualizarItem: (itemId, data) =>
    api.put(`/planear/evaluacion-inicial/items/${itemId}`, data),

  eliminarItem: (itemId) =>
    api.delete(`/planear/evaluacion-inicial/items/${itemId}`),

  finalizar: (id) =>
    api.patch(`/planear/evaluacion-inicial/${id}/finalizar`),

  eliminar: (id) =>
    api.delete(`/planear/evaluacion-inicial/${id}`),
};