import api from "./axios";
import { limpiarParams } from "./apiHelpers";

const downloadBlob = (response, fallbackName) => {
  const disposition = response.headers?.["content-disposition"] || "";
  const match = disposition.match(/filename\*?=(?:UTF-8''|\")?([^";]+)/i);
  const fileName = match ? decodeURIComponent(match[1].replace(/"/g, "")) : fallbackName;

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", fileName);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const obtenerPerfilSociodemografico = async (empleadoId, empresaId) => {
  const params = {};
  if (empresaId) params.empresa_id = empresaId;
  const { data } = await api.get(`/empleados-perfil/empleado/${empleadoId}`, { params: limpiarParams(params) });
  return data;
};

export const crearPerfilSociodemografico = async (payload) => {
  const { data } = await api.post("/empleados-perfil", payload);
  return data;
};

export const actualizarPerfilSociodemografico = async (empleadoId, payload, empresaId) => {
  const params = {};
  if (empresaId) params.empresa_id = empresaId;
  const { data } = await api.put(`/empleados-perfil/empleado/${empleadoId}`, payload, { params: limpiarParams(params) });
  return data;
};

export const eliminarPerfilSociodemografico = async (empleadoId, empresaId) => {
  const params = {};
  if (empresaId) params.empresa_id = empresaId;
  const { data } = await api.delete(`/empleados-perfil/empleado/${empleadoId}`, { params: limpiarParams(params) });
  return data;
};

export const listarPerfilesSociodemograficos = async (params = {}) => {
  const { data } = await api.get("/empleados-perfil", { params: limpiarParams(params) });
  return data;
};

export const exportarPerfilesExcel = async (params = {}) => {
  const response = await api.get("/empleados-perfil/exportar-excel", {
    params: limpiarParams(params),
    responseType: "blob",
  });
  downloadBlob(response, "perfiles_sociodemograficos.xlsx");
};

export const descargarPlantillaExcel = async () => {
  const response = await api.get("/empleados-perfil/plantilla-excel", { responseType: "blob" });
  downloadBlob(response, "plantilla_perfil_sociodemografico.xlsx");
};

export const importarPerfilExcel = async (archivo, empresaId) => {
  const formData = new FormData();
  formData.append("archivo", archivo);
  const { data } = await api.post(`/empleados-perfil/importar-excel?empresa_id=${empresaId}`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};
