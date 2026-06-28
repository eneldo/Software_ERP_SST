// ============================================================
// API - REVISIÓN POR LA DIRECCIÓN SST ENTERPRISE
// FASE 1.8.2
// Archivo: frontend/src/api/revisionDireccionApi.js
// ============================================================

import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function getAuthHeaders() {
  const token = localStorage.getItem("access_token");

  return {
    headers: {
      Authorization: token ? `Bearer ${token}` : "",
    },
  };
}

export async function obtenerDashboardRevisionDireccion(empresaId = null) {
  const params = {};

  if (empresaId) {
    params.empresa_id = empresaId;
  }

  const response = await axios.get(
    `${API_URL}/verificar/revision-direccion/dashboard`,
    {
      ...getAuthHeaders(),
      params,
    }
  );

  return response.data;
}

export async function listarRevisionesDireccion(empresaId = null) {
  const params = {};

  if (empresaId) {
    params.empresa_id = empresaId;
  }

  const response = await axios.get(
    `${API_URL}/verificar/revision-direccion/`,
    {
      ...getAuthHeaders(),
      params,
    }
  );

  return response.data;
}

export async function obtenerRevisionDireccion(revisionId) {
  const response = await axios.get(
    `${API_URL}/verificar/revision-direccion/${revisionId}`,
    getAuthHeaders()
  );

  return response.data;
}

export async function crearRevisionDireccion(payload) {
  const response = await axios.post(
    `${API_URL}/verificar/revision-direccion/`,
    payload,
    getAuthHeaders()
  );

  return response.data;
}

export async function actualizarRevisionDireccion(revisionId, payload) {
  const response = await axios.put(
    `${API_URL}/verificar/revision-direccion/${revisionId}`,
    payload,
    getAuthHeaders()
  );

  return response.data;
}

export async function cambiarEstadoRevision(revisionId, estado) {
  const response = await axios.patch(
    `${API_URL}/verificar/revision-direccion/${revisionId}/estado`,
    null,
    {
      ...getAuthHeaders(),
      params: {
        estado,
      },
    }
  );

  return response.data;
}

export async function eliminarRevisionDireccion(revisionId) {
  const response = await axios.delete(
    `${API_URL}/verificar/revision-direccion/${revisionId}`,
    getAuthHeaders()
  );

  return response.data;
}

export async function crearCompromisoRevision(revisionId, payload) {
  const response = await axios.post(
    `${API_URL}/verificar/revision-direccion/${revisionId}/compromisos`,
    payload,
    getAuthHeaders()
  );

  return response.data;
}

export async function actualizarCompromisoRevision(compromisoId, payload) {
  const response = await axios.put(
    `${API_URL}/verificar/revision-direccion/compromisos/${compromisoId}`,
    payload,
    getAuthHeaders()
  );

  return response.data;
}

export async function eliminarCompromisoRevision(compromisoId) {
  const response = await axios.delete(
    `${API_URL}/verificar/revision-direccion/compromisos/${compromisoId}`,
    getAuthHeaders()
  );

  return response.data;
}

export async function exportarPdfRevisionDireccion(revisionId) {
  const token = localStorage.getItem("access_token");

  const response = await axios.get(
    `${API_URL}/verificar/revision-direccion-pdf/${revisionId}`,
    {
      responseType: "blob",
      headers: {
        Authorization: token ? `Bearer ${token}` : "",
      },
    }
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