// ============================================================
// API GLOBAL - ELIMINACIÓN INTELIGENTE ENTERPRISE
// ERP SST PRO ENTERPRISE
// FASE 37.3 — Smart Delete Enterprise v2
// Archivo: frontend/src/api/smartDeleteApi.js
// ============================================================

import api from "./axios";

export const listarEntidadesProtegidas = async () => {
  const response = await api.get("/integridad/entidades");
  return response.data;
};

export const validarEliminacionInteligente = async (entidad, id) => {
  if (!entidad) throw new Error("Entidad requerida para validar eliminación.");
  if (!id) throw new Error("ID requerido para validar eliminación.");

  const response = await api.get(`/integridad/eliminacion/${entidad}/${id}`);
  return response.data;
};

// Alias semántico v2: usa el mismo endpoint, pero expresa mejor el objetivo.
export const analizarImpactoEliminacion = async (entidad, id) => {
  return validarEliminacionInteligente(entidad, id);
};

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

export const inactivarRegistroInteligente = async (entidad, id) => {
  return ejecutarEliminacionInteligente(entidad, id, "INACTIVATE", true);
};
