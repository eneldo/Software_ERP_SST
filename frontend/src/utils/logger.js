// ============================================================
// FRONTEND LOGGER - ERP SST PRO ENTERPRISE
// FASE 36.8 — Logging Enterprise y Manejo de Errores
// Archivo: frontend/src/utils/logger.js
// ============================================================

const ENABLE_CONSOLE = String(import.meta.env.VITE_ENABLE_CONSOLE_LOGS || "false") === "true";
const APP_VERSION = import.meta.env.VITE_APP_VERSION || "dev";

function normalizeError(error) {
  if (!error) return { message: "Error desconocido" };

  return {
    message: error?.userMessage || error?.message || "Error desconocido",
    status: error?.response?.status,
    code: error?.response?.data?.code,
    requestId: error?.response?.data?.request_id || error?.response?.headers?.["x-request-id"],
    url: error?.config?.url,
    method: error?.config?.method,
    version: APP_VERSION,
  };
}

export const logger = {
  info(message, context = {}) {
    if (ENABLE_CONSOLE) console.info(`[ERP SST] ${message}`, context);
  },
  warn(message, context = {}) {
    if (ENABLE_CONSOLE) console.warn(`[ERP SST] ${message}`, context);
  },
  error(message, error = null, context = {}) {
    const payload = { ...context, error: normalizeError(error) };
    if (ENABLE_CONSOLE) console.error(`[ERP SST] ${message}`, payload);
    return payload;
  },
  normalizeError,
};

export function getFriendlyErrorMessage(error, fallback = "No fue posible completar la solicitud.") {
  return (
    error?.userMessage ||
    error?.response?.data?.message ||
    error?.response?.data?.detail ||
    error?.message ||
    fallback
  );
}
