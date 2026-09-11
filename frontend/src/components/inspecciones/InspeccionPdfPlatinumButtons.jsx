// ============================================================
// ERP SST ENTERPRISE
// ------------------------------------------------------------
// Módulo      : Inspecciones SST
// Fase        : 1.1.8.7.9
// Archivo     : InspeccionPdfPlatinumButtons.jsx
// Ubicación   : frontend/src/components/inspecciones/
// Versión     : Platinum Executive
// ------------------------------------------------------------
// Descripción:
// Botonera frontend para abrir y descargar el Reporte PDF
// Ejecutivo Platinum final: portada premium, índice, dashboard,
// evidencias, CAPA completa, timeline, firmas, QR y hash.
// ============================================================

// ============================================================
// ÍNDICE
// ------------------------------------------------------------
// 1. Importaciones
// 2. Helper usuario actual
// 3. Componente principal
// 4. Estados
// 5. Acciones PDF
// 6. Render compacto
// 7. Render completo
// ============================================================

// ============================================================
// 1. IMPORTACIONES
// ============================================================

import React, { useState } from "react";
import { FileText, Loader } from "lucide-react";
import {
  abrirInspeccionPdfPlatinum,
  descargarInspeccionPdfPlatinum,
} from "../../api/inspeccionesPlatinumApi";
import "../../styles/inspecciones-pdf-platinum.css";

// ============================================================
// 2. HELPER USUARIO ACTUAL
// ------------------------------------------------------------
// Lee el usuario desde localStorage. Soporta varias estructuras
// usadas en el ERP: usuario, user, nombre, username, email.
// ============================================================

const obtenerUsuarioActual = () => {
  try {
    const rawUser = localStorage.getItem("usuario") || localStorage.getItem("user");

    if (!rawUser) return "Sistema";

    const user = JSON.parse(rawUser);

    return user?.nombre || user?.username || user?.email || "Sistema";
  } catch (error) {
    return "Sistema";
  }
};

// ============================================================
// 3. COMPONENTE PRINCIPAL
// ============================================================

export default function InspeccionPdfPlatinumButtons({
  inspeccionId,
  disabled = false,
  compacto = false,
}) {
  // ==========================================================
  // 4. ESTADOS
  // ==========================================================

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ==========================================================
  // 5. ACCIONES PDF
  // ----------------------------------------------------------
  // modo = "abrir"      -> vista previa en nueva pestaña
  // modo = "descargar"  -> descarga directa del PDF
  // ==========================================================

  const ejecutar = async (modo) => {
    if (!inspeccionId || loading || disabled) return;

    setLoading(true);
    setError("");

    try {
      const usuario = obtenerUsuarioActual();

      if (modo === "abrir") {
        await abrirInspeccionPdfPlatinum(inspeccionId, usuario);
      } else {
        await descargarInspeccionPdfPlatinum(inspeccionId, usuario);
      }
    } catch (err) {
      console.error("Error PDF Platinum:", err);
      setError(err?.message || "No fue posible generar el Reporte PDF Ejecutivo Platinum.");
    } finally {
      setLoading(false);
    }
  };

  // ==========================================================
  // 6. RENDER COMPACTO
  // ----------------------------------------------------------
  // Para usar dentro de una fila de tabla.
  // ==========================================================

  if (compacto) {
    return (
      <div className="pdf-platinum-compact">
        <button
          type="button"
          className="insp-action-btn insp-action-pdf"
          disabled={disabled || loading || !inspeccionId}
          onClick={() => ejecutar("descargar")}
          title={loading ? "Generando PDF..." : "Descargar Reporte PDF Platinum"}
        >
          {loading ? <Loader size={15} className="insp-spin" /> : <FileText size={15} />}
        </button>

        {error && <span className="pdf-platinum-error compact-error">{error}</span>}
      </div>
    );
  }

  // ==========================================================
  // 7. RENDER COMPLETO
  // ----------------------------------------------------------
  // Para usar dentro del modal de exportaciones o workflow.
  // ==========================================================

  return (
    <div className="pdf-platinum-box">
      <div className="pdf-platinum-info">
        <span className="pdf-platinum-badge">PLATINUM</span>

        <div>
          <strong>Reporte PDF Ejecutivo Platinum</strong>
          <p>
            Portada premium · Índice · Dashboard ejecutivo · Evidencias · CAPA · Firmas · QR.
          </p>
        </div>
      </div>

      <div className="pdf-platinum-actions">
        <button
          type="button"
          className="btn-pdf-platinum secondary"
          disabled={disabled || loading || !inspeccionId}
          onClick={() => ejecutar("abrir")}
        >
          {loading ? "Generando..." : "Vista previa"}
        </button>

        <button
          type="button"
          className="btn-pdf-platinum primary"
          disabled={disabled || loading || !inspeccionId}
          onClick={() => ejecutar("descargar")}
        >
          {loading ? "Generando..." : "Descargar PDF Platinum"}
        </button>
      </div>

      {error && <div className="pdf-platinum-error">{error}</div>}
    </div>
  );
}
