// ============================================================
// API GLOBAL - ELIMINACIÓN INTELIGENTE ENTERPRISE
// ERP SST PRO ENTERPRISE
// FASE 37.2 — Framework Global de Eliminación Inteligente
// Archivo: frontend/src/api/smartDeleteApi.js
// ============================================================

import api from "./axios";

/**
 * Lista las entidades protegidas por el motor global.
 * Backend: GET /integridad/entidades
 */
export const listarEntidadesProtegidas = async () => {
  const response = await api.get("/integridad/entidades");
  return response.data;
};

/**
 * Valida si un registro puede eliminarse físicamente.
 * Backend: GET /integridad/eliminacion/{entidad}/{registro_id}
 */
export const validarEliminacionInteligente = async (entidad, id) => {
  if (!entidad) throw new Error("Entidad requerida para validar eliminación.");
  if (!id) throw new Error("ID requerido para validar eliminación.");

  const response = await api.get(`/integridad/eliminacion/${entidad}/${id}`);
  return response.data;
};

/**
 * Ejecuta eliminación inteligente.
 * modo DELETE: elimina físicamente si el motor lo permite.
 * modo INACTIVATE: inactiva el registro conservando trazabilidad.
 * Backend: DELETE /integridad/eliminacion/{entidad}/{registro_id}
 */
export const ejecutarEliminacionInteligente = async (
  entidad,
  id,
  modo = "DELETE",
  confirmar = true
) => {
  if (!entidad) throw new Error("Entidad requerida para ejecutar eliminación.");
  if (!id) throw new Error("ID requerido para ejecutar eliminación.");

  const response = await api.delete(`/integridad/eliminacion/${entidad}/${id}`, {
    params: {
      modo,
      confirmar,
    },
  });

  return response.data;
};

/**
 * Inactiva un registro usando el motor global.
 */
export const inactivarRegistroInteligente = async (entidad, id) => {
  return ejecutarEliminacionInteligente(entidad, id, "INACTIVATE", true);
};
