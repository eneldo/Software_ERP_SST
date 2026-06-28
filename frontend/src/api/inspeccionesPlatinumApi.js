// ============================================================
// ERP SST ENTERPRISE
// ------------------------------------------------------------
// Módulo      : Inspecciones SST
// Fase        : 1.1.8.7.9
// Archivo     : inspeccionesPlatinumApi.js
// Ubicación   : frontend/src/api/
// Versión     : Platinum Executive
// ------------------------------------------------------------
// Descripción:
// API frontend para abrir y descargar el Reporte PDF Ejecutivo
// Platinum final de Inspecciones SST.
//
// Ruta backend consumida:
// GET /inspecciones-exportaciones-platinum/{id}/pdf-platinum
// ============================================================

// ============================================================
// ÍNDICE
// ------------------------------------------------------------
// 1. Importaciones
// 2. Configuración base
// 3. Helpers
// 4. Descargar PDF Platinum
// 5. Abrir vista previa PDF Platinum
// ============================================================

// ============================================================
// 1. IMPORTACIONES
// ============================================================

import axios from "./axios";

// ============================================================
// 2. CONFIGURACIÓN BASE
// ============================================================

const PLATINUM_ENDPOINT = "/inspecciones-exportaciones-platinum";

// ============================================================
// 3. HELPERS
// ============================================================

const limpiarTextoArchivo = (texto) =>
  String(texto || "")
    .trim()
    .replace(/[^a-zA-Z0-9-_]/g, "_")
    .replace(/_+/g, "_")
    .substring(0, 90);

const construirNombreArchivo = (inspeccionId) => {
  const fecha = new Date().toISOString().slice(0, 10);
  return `inspeccion_sst_${limpiarTextoArchivo(inspeccionId)}_reporte_ejecutivo_platinum_${fecha}.pdf`;
};

const crearUrlBlobPdf = (response) => {
  const blob = new Blob([response.data], { type: "application/pdf" });
  return window.URL.createObjectURL(blob);
};

const obtenerMensajeError = (error) => {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((item) => item?.msg || item).join(" | ");
  if (detail && typeof detail === "object") return JSON.stringify(detail);

  return error?.message || "No fue posible generar el Reporte PDF Ejecutivo Platinum.";
};

// ============================================================
// 4. DESCARGAR PDF PLATINUM
// ------------------------------------------------------------
// Descarga el PDF generado por backend.
// ============================================================

export const descargarInspeccionPdfPlatinum = async (
  inspeccionId,
  usuario = "Sistema",
) => {
  if (!inspeccionId) {
    throw new Error("No se recibió el ID de la inspección.");
  }

  try {
    const response = await axios.get(
      `${PLATINUM_ENDPOINT}/${inspeccionId}/pdf-platinum`,
      {
        params: { usuario },
        responseType: "blob",
      },
    );

    const url = crearUrlBlobPdf(response);
    const link = document.createElement("a");

    link.href = url;
    link.download = construirNombreArchivo(inspeccionId);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    window.URL.revokeObjectURL(url);

    return true;
  } catch (error) {
    console.error("Error descargando PDF Platinum:", error);
    throw new Error(obtenerMensajeError(error));
  }
};

// ============================================================
// 5. ABRIR VISTA PREVIA PDF PLATINUM
// ------------------------------------------------------------
// Abre el PDF en una nueva pestaña para revisión ejecutiva.
// ============================================================

export const abrirInspeccionPdfPlatinum = async (
  inspeccionId,
  usuario = "Sistema",
) => {
  if (!inspeccionId) {
    throw new Error("No se recibió el ID de la inspección.");
  }

  try {
    const response = await axios.get(
      `${PLATINUM_ENDPOINT}/${inspeccionId}/pdf-platinum`,
      {
        params: { usuario },
        responseType: "blob",
      },
    );

    const url = crearUrlBlobPdf(response);
    const ventana = window.open(url, "_blank", "noopener,noreferrer");

    if (!ventana) {
      const link = document.createElement("a");
      link.href = url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    setTimeout(() => {
      window.URL.revokeObjectURL(url);
    }, 60000);

    return true;
  } catch (error) {
    console.error("Error abriendo PDF Platinum:", error);
    throw new Error(obtenerMensajeError(error));
  }
};
