// ============================================================
// API CARGOS SST - ERP SST PRO
// Archivo: frontend/src/api/cargoSstApi.js
// FASE 1.1.4.3 — Exportación PDF / Excel
// Compatible con imports nombrados y export default.
// ============================================================

import api from "./axios";
import { normalizarLista, limpiarParams } from "./apiHelpers";

const BASE_URL = "/cargos";

const descargarBlob = async (blob, filename) => {
  const contentType = blob instanceof Blob ? blob.type || "application/octet-stream" : "application/octet-stream";
  const arrayBuffer = blob instanceof Blob ? await blob.arrayBuffer() : blob;
  const bytes = new Uint8Array(arrayBuffer);
  let binary = "";
  for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
  const base64 = btoa(binary);
  const dataUrl = `data:${contentType};base64,${base64}`;
  const link = document.createElement("a");
  link.href = dataUrl;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
};

const nombreFecha = () => {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}`;
};

const normalizarCargo = (cargo = {}) => ({
  ...cargo,
  codigo: cargo.codigo ?? cargo.codigo_cargo ?? "",
  tipo: cargo.tipo ?? cargo.tipo_cargo ?? "OPERATIVO",
  proceso: cargo.proceso ?? cargo.proceso_asociado ?? "",
  empleados_asociados: cargo.empleados_asociados ?? cargo.numero_empleados ?? 0,
  requiere_examen_medico: cargo.requiere_examen_medico ?? Boolean(cargo.examenes_medicos),
  requiere_capacitacion: cargo.requiere_capacitacion ?? Boolean(cargo.capacitaciones_requeridas),
  funciones: cargo.funciones ?? cargo.perfil_sst ?? "",
});

const normalizarDashboard = (data = {}) => ({
  ...data,
  riesgo_alto_critico: data.riesgo_alto_critico ?? data.alto_critico ?? 0,
  distribucion_riesgo: data.distribucion_riesgo ?? data.cargos_por_riesgo ?? [],
  distribucion_tipo: data.distribucion_tipo ?? data.cargos_por_tipo ?? [],
  cargos_prioritarios: data.cargos_prioritarios ?? (data.cargo_prioritario ? [data.cargo_prioritario] : []),
  requieren_examen_medico: data.requieren_examen_medico ?? 0,
  requieren_capacitacion: data.requieren_capacitacion ?? 0,
});

export const listarCargosSST = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/`, { params: limpiarParams(params) });
  return normalizarLista(response.data).map(normalizarCargo);
};

export const obtenerDashboardCargosSST = async (params = {}) => {
  try {
    const response = await api.get(`${BASE_URL}/dashboard/resumen`, { params: limpiarParams(params) });
    return normalizarDashboard(response.data);
  } catch (error) {
    if (error?.response?.status === 404 || error?.response?.status === 405) {
      const response = await api.get(`${BASE_URL}/dashboard`, { params: limpiarParams(params) });
      return normalizarDashboard(response.data);
    }
    throw error;
  }
};

export const obtenerCargoSST = async (id) => {
  const response = await api.get(`${BASE_URL}/${id}`);
  return normalizarCargo(response.data);
};

export const crearCargoSST = async (data) => {
  const response = await api.post(`${BASE_URL}/`, data);
  return normalizarCargo(response.data);
};

export const actualizarCargoSST = async (id, data) => {
  const response = await api.put(`${BASE_URL}/${id}`, data);
  return normalizarCargo(response.data);
};

export const obtenerEppCargoSST = async (id) => {
  const response = await api.get(`${BASE_URL}/${id}/epp`);
  return response.data;
};

export const actualizarEppCargoSST = async (id, eppIds) => {
  const response = await api.put(`${BASE_URL}/${id}/epp`, { epp_ids: eppIds });
  return response.data;
};

export const cambiarEstadoCargoSST = async (id, activo) => {
  try {
    const response = await api.patch(`${BASE_URL}/${id}/estado`, null, { params: { activo } });
    return normalizarCargo(response.data);
  } catch (error) {
    if (error?.response?.status === 404 || error?.response?.status === 405) {
      const response = await api.put(`${BASE_URL}/${id}`, { activo });
      return normalizarCargo(response.data);
    }
    throw error;
  }
};

export const eliminarCargoSST = async (id) => {
  const response = await api.delete(`${BASE_URL}/${id}`);
  return response.data;
};

export const exportarCargosExcelSST = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/export/excel`, {
    params: limpiarParams(params),
    responseType: "blob",
  });
  descargarBlob(response.data, `cargos_sst_${nombreFecha()}.xlsx`);
};

export const exportarCargosPdfSST = async (params = {}) => {
  const response = await api.get(`${BASE_URL}/export/pdf`, {
    params: limpiarParams(params),
    responseType: "blob",
  });
  descargarBlob(response.data, `reporte_cargos_sst_${nombreFecha()}.pdf`);
};

export const exportarFichaCargoPdfSST = async (id, nombre = "cargo") => {
  const response = await api.get(`${BASE_URL}/${id}/export/pdf`, { responseType: "blob" });
  const seguro = String(nombre || "cargo").toLowerCase().replace(/[^a-z0-9áéíóúñ_-]+/gi, "_");
  descargarBlob(response.data, `ficha_cargo_sst_${seguro}_${nombreFecha()}.pdf`);
};

export const listarEmpresasParaCargosSST = async () => {
  const response = await api.get("/empresas/");
  return normalizarLista(response.data);
};

export const listarSedesParaCargosSST = async (params = {}) => {
  const response = await api.get("/sedes/", { params: limpiarParams(params) });
  return normalizarLista(response.data);
};

export const listarAreasParaCargosSST = async (params = {}) => {
  const response = await api.get("/areas/", { params: limpiarParams(params) });
  return normalizarLista(response.data);
};

const cargoSstApi = {
  listar: listarCargosSST,
  dashboard: obtenerDashboardCargosSST,
  obtener: obtenerCargoSST,
  crear: crearCargoSST,
  actualizar: actualizarCargoSST,
  obtenerEpp: obtenerEppCargoSST,
  actualizarEpp: actualizarEppCargoSST,
  cambiarEstado: cambiarEstadoCargoSST,
  eliminar: eliminarCargoSST,
  exportarExcel: exportarCargosExcelSST,
  exportarPdf: exportarCargosPdfSST,
  exportarFichaPdf: exportarFichaCargoPdfSST,
  listarEmpresas: listarEmpresasParaCargosSST,
  listarSedes: listarSedesParaCargosSST,
  listarAreas: listarAreasParaCargosSST,
};

export default cargoSstApi;
