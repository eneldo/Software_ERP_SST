// ============================================================
// BOTÓN PDF EJECUTIVO MEDIDA CORRECTIVA
// ERP SST PRO
// FASE 1.1.8.7.6
// Archivo: frontend/src/components/medidas/BotonPdfMedidaCorrectiva.jsx
// ============================================================

import { FileDown } from "lucide-react";
import { useState } from "react";

import { descargarPdfMedidaCorrectiva } from "../../api/medidasCorrectivasExportApi";
import { toastError, toastWarning } from "../../utils/toast";

export default function BotonPdfMedidaCorrectiva({ medidaId, className = "mc-btn ghost" }) {
  const [loading, setLoading] = useState(false);

  async function handleDownload() {
    if (!medidaId) {
      toastWarning("Advertencia", "Debe seleccionar una medida correctiva.");
      return;
    }

    setLoading(true);
    try {
      await descargarPdfMedidaCorrectiva(medidaId);
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No fue posible generar el PDF ejecutivo.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <button className={className} type="button" onClick={handleDownload} disabled={loading}>
      <FileDown size={16} />
      {loading ? "Generando PDF..." : "PDF Ejecutivo"}
    </button>
  );
}
