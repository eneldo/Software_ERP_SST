// ============================================================
// API EMPLEADOS SST - ERP SST PRO
// FASE 1.1.5.3 — EXPORTACIÓN PDF / EXCEL
// Archivo: frontend/src/api/empleadoSstApi.js
// ============================================================

import api from "./axios";

const cleanParams = (params = {}) => {
  const cleaned = {};
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "" && value !== "TODOS") {
      cleaned[key] = value;
    }
  });
  return cleaned;
};

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

export const listarEmpleados = async (params = {}) => {
  const { data } = await api.get("/empleados/", { params: cleanParams(params) });
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
  const { data } = await api.get("/empleados/dashboard", { params: cleanParams(params) });
  return data;
};

export const exportarEmpleadosExcel = async (params = {}) => {
  const response = await api.get("/empleados/export/excel", {
    params: cleanParams(params),
    responseType: "blob",
  });
  downloadBlob(response, "empleados_sst.xlsx");
};

export const exportarEmpleadosPdf = async (params = {}) => {
  const response = await api.get("/empleados/export/pdf", {
    params: cleanParams(params),
    responseType: "blob",
  });
  downloadBlob(response, "empleados_sst.pdf");
};

export const exportarFichaEmpleadoPdf = async (id) => {
  const response = await api.get(`/empleados/${id}/pdf`, { responseType: "blob" });
  downloadBlob(response, `ficha_empleado_${id}.pdf`);
};
