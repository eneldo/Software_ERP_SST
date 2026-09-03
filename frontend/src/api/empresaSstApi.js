// ============================================================
// API EMPRESAS SST ENTERPRISE PRO
// Archivo: frontend/src/api/empresaSstApi.js
// FASE 1.1.1.C — Empresas SST Enterprise PRO
// ============================================================

import api from "./axios";
import { API_BASE_URL } from "../config/env";

/**
 * Convierte la respuesta del backend a un arreglo seguro.
 * Esto evita errores si el backend responde null o con un formato inesperado.
 */
const normalizarLista = (data) => (Array.isArray(data) ? data : []);

/**
 * Obtiene todas las empresas SST activas registradas.
 * Backend: GET /empresas/
 */
export const listarEmpresasSST = async () => {
  const response = await api.get("/empresas/");
  return normalizarLista(response.data);
};

/**
 * Obtiene una empresa por ID.
 * Backend: GET /empresas/{empresa_id}
 */
export const obtenerEmpresaSST = async (id) => {
  const response = await api.get(`/empresas/${id}`);
  return response.data;
};

/**
 * Crea una nueva empresa SST.
 * Backend: POST /empresas/
 */
export const crearEmpresaSST = async (data) => {
  const response = await api.post("/empresas/", data);
  return response.data;
};

/**
 * Actualiza una empresa SST existente.
 * Backend: PUT /empresas/{empresa_id}
 */
export const actualizarEmpresaSST = async (id, data) => {
  const response = await api.put(`/empresas/${id}`, data);
  return response.data;
};

/**
 * Desactiva una empresa SST mediante eliminación lógica.
 * Backend: DELETE /empresas/{empresa_id}
 */
export const eliminarEmpresaSST = async (id) => {
  const response = await api.delete(`/empresas/${id}`);
  return response.data;
};

/**
 * Sube o cambia el logo corporativo de una empresa.
 * Backend: POST /empresas/{empresa_id}/logo
 */
export const subirLogoEmpresaSST = async (id, file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post(`/empresas/${id}/logo`, formData);

  return response.data;
};

/**
 * Elimina el logo corporativo de una empresa.
 * Backend: DELETE /empresas/{empresa_id}/logo
 */
export const eliminarLogoEmpresaSST = async (id) => {
  const response = await api.delete(`/empresas/${id}/logo`);
  return response.data;
};

/**
 * Construye una URL absoluta para visualizar logos desde el endpoint protegido.
 */
export const construirUrlLogoEmpresa = (logo) => {
  if (!logo) return null;
  if (logo.startsWith("http://") || logo.startsWith("https://")) return logo;

  const baseURL = API_BASE_URL;
  if (logo.startsWith("/uploads/logos/")) {
    const fileName = logo.split("/").pop();
    return `${baseURL}/logos-empresa/${fileName}`;
  }
  if (logo.startsWith("/uploads/")) {
    return `${baseURL}/archivos-protegidos/${logo.slice("/uploads/".length)}`;
  }
  return `${baseURL}${logo}`;
};

/**
 * Valida si una empresa puede eliminarse físicamente.
 * Backend: GET /integridad/eliminacion/empresa/{id}
 */
export const validarEliminacionEmpresaSST = async (id) => {
  const response = await api.get(`/integridad/eliminacion/empresa/${id}`);
  return response.data;
};

/**
 * Ejecuta eliminación inteligente de empresa.
 * modo DELETE: eliminación física solo si no tiene dependencias.
 * modo INACTIVATE: inactiva la empresa conservando trazabilidad.
 */
export const ejecutarEliminacionInteligenteEmpresaSST = async (id, modo = "DELETE") => {
  const response = await api.delete(`/integridad/eliminacion/empresa/${id}`, {
    params: {
      modo,
      confirmar: true,
    },
  });
  return response.data;
};

/**
 * Inactiva una empresa desde el motor de integridad.
 */
export const inactivarEmpresaSST = async (id) => {
  return ejecutarEliminacionInteligenteEmpresaSST(id, "INACTIVATE");
};
