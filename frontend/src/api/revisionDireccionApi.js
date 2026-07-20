// ============================================================
// API - REVISIÓN POR LA DIRECCIÓN SST ENTERPRISE
// FASE 1.8.2
// Archivo: frontend/src/api/revisionDireccionApi.js
// ============================================================

import api from "./axios";

export async function obtenerDashboardRevisionDireccion(empresaId = null) {
  const params = {};

  if (empresaId) {
    params.empresa_id = empresaId;
  }

  const response = await api.get("/verificar/revision-direccion/dashboard", { params });

  return response.data;
}

export async function listarRevisionesDireccion(empresaId = null) {
  const params = {};

  if (empresaId) {
    params.empresa_id = empresaId;
  }

  const response = await api.get("/verificar/revision-direccion/", { params });

  return response.data;
}

export async function obtenerRevisionDireccion(revisionId) {
  const response = await api.get(`/verificar/revision-direccion/${revisionId}`);

  return response.data;
}

export async function crearRevisionDireccion(payload) {
  const response = await api.post("/verificar/revision-direccion/", payload);

  return response.data;
}

export async function actualizarRevisionDireccion(revisionId, payload) {
  const response = await api.put(`/verificar/revision-direccion/${revisionId}`, payload);

  return response.data;
}

export async function cambiarEstadoRevision(revisionId, estado) {
  const response = await api.patch(
    `/verificar/revision-direccion/${revisionId}/estado`,
    null,
    { params: { estado } }
  );

  return response.data;
}

export async function eliminarRevisionDireccion(revisionId) {
  const response = await api.delete(`/verificar/revision-direccion/${revisionId}`);

  return response.data;
}

export async function crearCompromisoRevision(revisionId, payload) {
  const response = await api.post(
    `/verificar/revision-direccion/${revisionId}/compromisos`,
    payload
  );

  return response.data;
}

export async function actualizarCompromisoRevision(compromisoId, payload) {
  const response = await api.put(
    `/verificar/revision-direccion/compromisos/${compromisoId}`,
    payload
  );

  return response.data;
}

export async function eliminarCompromisoRevision(compromisoId) {
  const response = await api.delete(
    `/verificar/revision-direccion/compromisos/${compromisoId}`
  );

  return response.data;
}

export async function exportarPdfRevisionDireccion(revisionId) {
  const response = await api.get(
    `/verificar/revision-direccion-pdf/${revisionId}`,
    { responseType: "blob" }
  );

  const blob = new Blob([response.data], {
    type: "application/pdf",
  });

  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = `revision_direccion_${revisionId}.pdf`;
  document.body.appendChild(link);
  link.click();

  link.remove();
  window.URL.revokeObjectURL(url);
}
