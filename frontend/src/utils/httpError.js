// ============================================================
// ERRORES HTTP NORMALIZADOS - ERP SST PRO
// FASE 36.4 — Normalización Enterprise
// ============================================================

export function getErrorMessage(error, fallback = "No fue posible procesar la solicitud.") {
  const detail = error?.response?.data?.detail || error?.response?.data?.detalle;
  const message = error?.response?.data?.mensaje || error?.response?.data?.message;

  if (typeof message === "string" && message.trim()) return message;
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail) && detail.length) return "Hay campos pendientes por corregir.";
  if (error?.message) return error.message;
  return fallback;
}
