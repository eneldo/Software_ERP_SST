// ============================================================
// UTILIDADES URL ARCHIVOS /UPLOADS
// ERP SST PRO
// FASE 1.1.8.7.5.1 — Miniaturas reales + visor
// Archivo: frontend/src/utils/fileUrl.js
// ============================================================

import api from "../api/axios";

export function getApiBaseUrl() {
  const base = api?.defaults?.baseURL || import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
  return String(base).replace(/\/$/, "");
}

export function resolveFileUrl(value) {
  if (!value) return "";

  const raw = String(value).trim();

  if (!raw) return "";

  if (raw.startsWith("http://") || raw.startsWith("https://") || raw.startsWith("blob:") || raw.startsWith("data:")) {
    return raw;
  }

  if (raw.startsWith("/uploads/")) {
    return `${getApiBaseUrl()}${raw}`;
  }

  if (raw.includes("\\app\\uploads\\") || raw.includes("/app/uploads/")) {
    const normalized = raw.replaceAll("\\", "/");
    const index = normalized.indexOf("/app/uploads/");
    if (index >= 0) {
      return `${getApiBaseUrl()}/uploads/${normalized.slice(index + "/app/uploads/".length)}`;
    }
  }

  if (raw.includes("/uploads/")) {
    const index = raw.indexOf("/uploads/");
    return `${getApiBaseUrl()}${raw.slice(index)}`;
  }

  return raw;
}

export function isImageEvidence(item = {}) {
  const mime = String(item.mime_type || "").toLowerCase();
  const ext = String(item.extension || item.nombre_archivo || "").toLowerCase();

  return (
    mime.startsWith("image/") ||
    ext.endsWith(".jpg") ||
    ext.endsWith(".jpeg") ||
    ext.endsWith(".png") ||
    ext.endsWith(".webp") ||
    ext === "jpg" ||
    ext === "jpeg" ||
    ext === "png" ||
    ext === "webp"
  );
}

export function getBestImageUrl(item = {}) {
  return resolveFileUrl(
    item.thumbnail_url ||
      item.preview_url ||
      item.url ||
      item.ruta ||
      item.full_url
  );
}

export function getDownloadUrl(item = {}) {
  return resolveFileUrl(item.url || item.preview_url || item.ruta || item.full_url);
}
