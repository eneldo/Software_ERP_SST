import api from "./axios";

export const bibliotecaDocumentalApi = {
  listar: (params = {}) => {
    return api.get("/biblioteca-documental/", { params });
  },

  obtener: (id) => {
    return api.get(`/biblioteca-documental/${id}`);
  },

  crear: (data) => {
    return api.post("/biblioteca-documental/", data);
  },

  subir: (formData) => {
    return api.post("/biblioteca-documental/subir", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  actualizar: (id, data) => {
    return api.put(`/biblioteca-documental/${id}`, data);
  },

  marcarVigente: (id) => {
    return api.patch(`/biblioteca-documental/${id}/vigente`);
  },

  marcarObsoleto: (id) => {
    return api.patch(`/biblioteca-documental/${id}/obsoleto`);
  },

  eliminar: (id) => {
    return api.delete(`/biblioteca-documental/${id}`);
  },
};