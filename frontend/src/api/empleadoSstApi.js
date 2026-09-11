// ============================================================
// API EMPLEADOS SST - ERP SST PRO
// FASE 1.1.5.3 — EXPORTACIÓN PDF / EXCEL
// Archivo: frontend/src/api/empleadoSstApi.js
// ============================================================

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

export const listarEmpleados = async (params = {}) => {
  const { data } = await api.get("/empleados/", { params: limpiarParams(params) });
  return data;
};

export const obtenerEmpleado = async (id) => {
  const { data } = await api.get(`/empleados/${id}`);
  return data;
};

export const crearEmpleado = async (payload) => {
  const { data } = await api.post("/empleados/", payload);
  return data;
};

export const actualizarEmpleado = async (id, payload) => {
  const { data } = await api.put(`/empleados/${id}`, payload);
  return data;
};

export const eliminarEmpleado = async (id) => {
  const { data } = await api.delete(`/empleados/${id}`);
  return data;
};

export const dashboardEmpleados = async (params = {}) => {
  const { data } = await api.get("/empleados/dashboard", { params: limpiarParams(params) });
  return data;
};

export const exportarEmpleadosExcel = async (params = {}) => {
  const response = await api.get("/empleados/export/excel", {
    params: limpiarParams(params),
    responseType: "blob",
  });
  downloadBlob(response, "empleados_sst.xlsx");
};

export const exportarEmpleadosPdf = async (params = {}) => {
  const response = await api.get("/empleados/export/pdf", {
    params: limpiarParams(params),
    responseType: "blob",
  });
  downloadBlob(response, "empleados_sst.pdf");
};

export const exportarFichaEmpleadoPdf = async (id) => {
  const response = await api.get(`/empleados/${id}/pdf`, { responseType: "blob" });
  downloadBlob(response, `ficha_empleado_${id}.pdf`);
};
