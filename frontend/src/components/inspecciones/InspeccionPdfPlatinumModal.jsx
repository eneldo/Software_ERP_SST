// ============================================================
// ERP SST ENTERPRISE
// ------------------------------------------------------------
// Módulo      : Inspecciones SST
// Fase        : 1.1.8.7.9
// Archivo     : InspeccionPdfPlatinumModal.jsx
// Ubicación   : frontend/src/components/inspecciones/
// Versión     : Platinum Executive
// ------------------------------------------------------------
// Descripción:
// Modal reutilizable para exportación del Reporte PDF Ejecutivo
// Platinum. Puede usarse en cualquier página donde exista una
// inspección seleccionada.
// ============================================================

import React from "react";
import InspeccionPdfPlatinumButtons from "./InspeccionPdfPlatinumButtons";
import "../../styles/inspecciones-pdf-platinum.css";

export default function InspeccionPdfPlatinumModal({
  open,
  inspeccion,
  onClose,
}) {
  if (!open) return null;

  return (
    <div className="pdf-platinum-modal-backdrop">
      <section className="pdf-platinum-modal">
        <header className="pdf-platinum-modal-header">
          <div>
            <span>INSPECCIÓN SST</span>
            <h2>Exportación Ejecutiva Platinum</h2>
            <p>
              Genera el reporte final con portada premium, índice, dashboard,
              evidencias, CAPA completa, firmas, QR y hash documental.
            </p>
          </div>
          <button type="button" onClick={onClose} aria-label="Cerrar modal">
            ×
          </button>
        </header>

        <div className="pdf-platinum-modal-body">
          <div className="pdf-platinum-modal-summary">
            <small>Inspección seleccionada</small>
            <strong>{inspeccion?.codigo || "Sin código"}</strong>
            <p>{inspeccion?.titulo || inspeccion?.descripcion || "Sin descripción disponible"}</p>
          </div>

          <InspeccionPdfPlatinumButtons inspeccionId={inspeccion?.id} />
        </div>
      </section>
    </div>
  );
}
