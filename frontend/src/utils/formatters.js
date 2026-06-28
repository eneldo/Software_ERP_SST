// ============================================================
// FORMATOS TRANSVERSALES - ERP SST PRO
// FASE 36.4 — Normalización Enterprise
// ============================================================

export function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString("es-CO");
}

export function formatDateTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString("es-CO");
}

export function formatPercent(value) {
  const number = Number(value || 0);
  return `${number.toFixed(0)}%`;
}
