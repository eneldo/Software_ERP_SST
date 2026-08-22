// ============================================================
// UTILIDADES COMPARTIDAS API - ERP SST PRO
// Elimina duplicación de normalizarLista, limpiarParams, descargarBlob
// ============================================================

import api from "./axios";

export function normalizarLista(data) {
  if (Array.isArray(data)) return data;
  if (data?.items && Array.isArray(data.items)) return data.items;
  if (data?.data && Array.isArray(data.data)) return data.data;
  if (data?.results && Array.isArray(data.results)) return data.results;
  return [];
}

export function limpiarParams(params = {}) {
  const clean = {};
  for (const [key, value] of Object.entries(params)) {
    if (value === null || value === undefined || value === "") continue;
    clean[key] = value;
  }
  return clean;
}

export async function descargarBlob(url, filename) {
  const response = await api.get(url, { responseType: "blob" });
  const blob = new Blob([response.data]);
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = downloadUrl;
  link.download = filename || "descarga";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);
}
