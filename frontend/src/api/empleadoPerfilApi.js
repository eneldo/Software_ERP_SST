import api from "./axios";
import { limpiarParams } from "./apiHelpers";

const downloadBlob = async (response, fallbackName) => {
  const disposition = response.headers?.["content-disposition"] || "";
  const match = disposition.match(/filename\*?=(?:UTF-8''|\")?([^";]+)/i);
  const fileName = match ? decodeURIComponent(match[1].replace(/"/g, "")) : fallbackName;

  const contentType = response?.headers?.["content-type"] || "application/octet-stream";
  const arrayBuffer = response.data instanceof Blob ? await response.data.arrayBuffer() : response.data;
  const bytes = new Uint8Array(arrayBuffer);
  let binary = "";
  for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
  const base64 = btoa(binary);
  const dataUrl = `data:${contentType};base64,${base64}`;
  const link = document.createElement("a");
  link.href = dataUrl;
  link.setAttribute("download", fileName);
  document.body.appendChild(link);
  link.click();
  link.remove();
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
