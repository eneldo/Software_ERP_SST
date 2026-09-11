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
  const contentType = response?.headers?.["content-type"] || "application/octet-stream";
  const arrayBuffer = response.data instanceof Blob ? await response.data.arrayBuffer() : response.data;
  const bytes = new Uint8Array(arrayBuffer);
  let binary = "";
  for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
  const base64 = btoa(binary);
  const dataUrl = `data:${contentType};base64,${base64}`;
  const link = document.createElement("a");
  link.href = dataUrl;
  link.download = filename || "descarga";
  document.body.appendChild(link);
  link.click();
  link.remove();
}
