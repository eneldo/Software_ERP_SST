// ============================================================
// USO DEL ARCHIVO:
// API Frontend para el módulo de Versionado Documental
// de Revisión por la Dirección SST.
//
// Usa el Axios central del proyecto:
// frontend/src/api/axios.js
//
// Permite:
// - Listar versiones
// - Obtener detalle de versión
// - Crear snapshot manual
// - Comparar versiones
// - Restaurar versión anterior
//
// FASE 1.8.4.3.8 — Portal Ejecutivo Historial Documental
// ============================================================

import api from "./axios";

export async function listarVersionesRevision(revisionId) {
  const response = await api.get(
    `/verificar/revision-direccion/${revisionId}/versiones`
  );

  return response.data;
}

export async function obtenerDetalleVersion(versionId) {
  const response = await api.get(
    `/verificar/revision-direccion/versiones/${versionId}`
  );

  return response.data;
}

export async function crearSnapshotManual(
  revisionId,
  observacion = "Snapshot manual"
) {
  const response = await api.post(
    `/verificar/revision-direccion/${revisionId}/versiones/snapshot`,
    null,
    {
      params: {
        observacion,
      },
    }
  );

  return response.data;
}

export async function restaurarVersion(
  versionId,
  observacion = "Restauración documental"
) {
  const response = await api.post(
    `/verificar/revision-direccion/versiones/${versionId}/restaurar`,
    {
      observacion,
    }
  );

  return response.data;
}

export async function compararVersiones(versionOrigenId, versionDestinoId) {
  const response = await api.get(
    `/verificar/revision-direccion/versiones/comparar`,
    {
      params: {
        version_origen_id: versionOrigenId,
        version_destino_id: versionDestinoId,
      },
    }
  );

  return response.data;
}