// ============================================================
// VISOR MODAL EVIDENCIAS REPORTES SST
// FASE 1.1.25.6
// Archivo: frontend/src/components/reportes/ReporteViewerModal.jsx
// ============================================================

import React from "react";
import { Download, X } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const fullUrl = (url) => (!url ? "" : url.startsWith("http") ? url : `${API_BASE}${url}`);

export default function ReporteViewerModal({ evidencia, onClose }) {
  if (!evidencia) return null;
  const url = fullUrl(evidencia.archivo_url);
  const tipo = evidencia.tipo_archivo || "OTRO";
  return (
    <div className="rep-ev-modal-backdrop" onClick={onClose}>
      <div className="rep-ev-modal" onClick={(e) => e.stopPropagation()}>
        <div className="rep-ev-modal-head">
          <div>
            <h3>{evidencia.archivo_nombre || "Evidencia SST"}</h3>
            <p>{tipo} · {evidencia.categoria_ia || "Sin clasificación"}</p>
          </div>
          <div className="rep-ev-modal-actions">
            <a href={url} target="_blank" rel="noreferrer" title="Abrir/descargar"><Download size={18} /></a>
            <button type="button" onClick={onClose}><X size={18} /></button>
          </div>
        </div>
        <div className="rep-ev-modal-body">
          {tipo === "IMAGEN" && <img src={url} alt={evidencia.archivo_nombre || "Evidencia"} />}
          {tipo === "VIDEO" && <video src={url} controls />}
          {tipo === "PDF" && <iframe src={url} title="PDF evidencia" />}
          {tipo === "AUDIO" && <audio src={url} controls />}
          {!['IMAGEN','VIDEO','PDF','AUDIO'].includes(tipo) && <a href={url} target="_blank" rel="noreferrer">Abrir evidencia</a>}
        </div>
      </div>
    </div>
  );
}
