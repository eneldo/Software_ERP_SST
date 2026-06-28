// ============================================================
// EXPORTACIONES ENTERPRISE MEDIDA CORRECTIVA
// ERP SST PRO
// FASE 1.1.8.7.6.1 — PDF + Excel individual
// ============================================================

import { FileDown, FileSpreadsheet } from "lucide-react";
import { useState } from "react";

import {
  descargarExcelMedidaCorrectiva,
  descargarPdfMedidaCorrectiva,
} from "../../api/medidasCorrectivasExportApi";

import "../../styles/medidas-exportaciones-enterprise.css";

export default function ExportacionesMedidaEnterprise({ medida, compact = false, className = "" }) {
  const [loadingPdf, setLoadingPdf] = useState(false);
  const [loadingExcel, setLoadingExcel] = useState(false);

  const medidaId = medida?.id;
  const codigo = medida?.codigo || medidaId;

  async function handlePdf() {
    if (!medidaId) {
      alert("Debe abrir o seleccionar una medida correctiva.");
      return;
    }

    setLoadingPdf(true);
    try {
      await descargarPdfMedidaCorrectiva(medidaId, codigo);
    } catch (error) {
      console.error(error);
      alert(error?.response?.data?.detail || "No fue posible generar el PDF ejecutivo.");
    } finally {
      setLoadingPdf(false);
    }
  }

  async function handleExcel() {
    if (!medidaId) {
      alert("Debe abrir o seleccionar una medida correctiva.");
      return;
    }

    setLoadingExcel(true);
    try {
      await descargarExcelMedidaCorrectiva(medidaId, codigo);
    } catch (error) {
      console.error(error);
      alert(error?.response?.data?.detail || "No fue posible generar el Excel ejecutivo.");
    } finally {
      setLoadingExcel(false);
    }
  }

  return (
    <div className={`mee-actions ${compact ? "compact" : ""} ${className}`}>
      <button
        type="button"
        className={compact ? "mee-icon-btn pdf" : "mee-btn pdf"}
        onClick={handlePdf}
        disabled={loadingPdf}
        title="Descargar PDF ejecutivo"
      >
        <FileDown size={16} />
        {!compact && (loadingPdf ? "Generando PDF..." : "PDF Ejecutivo")}
      </button>

      <button
        type="button"
        className={compact ? "mee-icon-btn excel" : "mee-btn excel"}
        onClick={handleExcel}
        disabled={loadingExcel}
        title="Descargar Excel ejecutivo"
      >
        <FileSpreadsheet size={16} />
        {!compact && (loadingExcel ? "Generando Excel..." : "Excel Ejecutivo")}
      </button>
    </div>
  );
}
