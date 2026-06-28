// ============================================================
// GALERÍA EVIDENCIAS REPORTES SST
// FASE 1.1.25.6
// Archivo: frontend/src/components/reportes/ReporteGaleriaEvidencias.jsx
// ============================================================

import React, { useState } from "react";
import { FileText, Image, Music, Trash2, Video } from "lucide-react";
import ReporteViewerModal from "./ReporteViewerModal";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const fullUrl = (url) => (!url ? "" : url.startsWith("http") ? url : `${API_BASE}${url}`);

const iconByType = (tipo) => {
  if (tipo === "IMAGEN") return <Image size={18} />;
  if (tipo === "VIDEO") return <Video size={18} />;
  if (tipo === "AUDIO") return <Music size={18} />;
  return <FileText size={18} />;
};

export default function ReporteGaleriaEvidencias({ evidencias = [], onDelete }) {
  const [viewer, setViewer] = useState(null);
  if (!evidencias.length) return <div className="rep-ev-empty">Sin evidencias cargadas.</div>;
  return (
    <>
      <div className="rep-ev-grid">
        {evidencias.map((ev) => {
          const thumb = fullUrl(ev.archivo_thumbnail_url || ev.archivo_url);
          return (
            <div className="rep-ev-card" key={ev.id}>
              <button type="button" className="rep-ev-preview" onClick={() => setViewer(ev)}>
                {ev.tipo_archivo === "IMAGEN" ? <img src={thumb} alt={ev.archivo_nombre || "Evidencia"} /> : <span>{iconByType(ev.tipo_archivo)}</span>}
              </button>
              <div className="rep-ev-info">
                <strong title={ev.archivo_nombre}>{ev.archivo_nombre || "Evidencia"}</strong>
                <small>{ev.tipo_archivo} · {ev.categoria_ia || "SIN_CLASIFICAR"}</small>
                {ev.peso_original_bytes && ev.peso_optimizado_bytes && (
                  <small>{Math.round((ev.peso_optimizado_bytes / 1024) * 10) / 10} KB optimizado</small>
                )}
              </div>
              {onDelete && <button type="button" className="rep-ev-delete" onClick={() => onDelete(ev)}><Trash2 size={15} /></button>}
            </div>
          );
        })}
      </div>
      <ReporteViewerModal evidencia={viewer} onClose={() => setViewer(null)} />
    </>
  );
}
