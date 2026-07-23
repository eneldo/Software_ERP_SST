import React, { useState } from "react";
import { FileText, Image, Loader2, Music, Trash2, Video } from "lucide-react";
import ReporteViewerModal from "./ReporteViewerModal";
import useReporteAssetUrl from "./useReporteAssetUrl";

const iconByType = (tipo) => {
  if (tipo === "IMAGEN") return <Image size={18} />;
  if (tipo === "VIDEO") return <Video size={18} />;
  if (tipo === "AUDIO") return <Music size={18} />;
  return <FileText size={18} />;
};

function EvidenciaCard({ evidencia, onOpen, onDelete }) {
  const isImage = evidencia.tipo_archivo === "IMAGEN";
  const thumbnail = useReporteAssetUrl(isImage ? (evidencia.archivo_thumbnail_url || evidencia.archivo_url) : "");
  return (
    <div className="rep-ev-card">
      <button type="button" className="rep-ev-preview" onClick={() => onOpen(evidencia)} title="Ver evidencia completa" aria-label={`Ver evidencia ${evidencia.archivo_nombre || "SST"}`}>
        {isImage && thumbnail.loading && <Loader2 className="rep-ev-loading" size={24} />}
        {isImage && thumbnail.url && <img src={thumbnail.url} alt={`Miniatura de ${evidencia.archivo_nombre || "evidencia SST"}`} />}
        {isImage && thumbnail.error && <span className="rep-ev-error"><Image size={18} /><small>Vista no disponible</small></span>}
        {!isImage && <span>{iconByType(evidencia.tipo_archivo)}</span>}
      </button>
      <div className="rep-ev-info">
        <strong title={evidencia.archivo_nombre}>{evidencia.archivo_nombre || "Evidencia"}</strong>
        <small>{evidencia.tipo_archivo} · {evidencia.categoria_ia || "SIN_CLASIFICAR"}</small>
        {evidencia.peso_original_bytes && evidencia.peso_optimizado_bytes && <small>{Math.round((evidencia.peso_optimizado_bytes / 1024) * 10) / 10} KB optimizado</small>}
      </div>
      {onDelete && <button type="button" className="rep-ev-delete" title="Eliminar evidencia" aria-label="Eliminar evidencia" onClick={() => onDelete(evidencia)}><Trash2 size={15} /></button>}
    </div>
  );
}

export default function ReporteGaleriaEvidencias({ evidencias = [], onDelete }) {
  const [viewer, setViewer] = useState(null);
  if (!evidencias.length) return <div className="rep-ev-empty">Sin evidencias cargadas.</div>;
  return (
    <>
      <div className="rep-ev-grid">{evidencias.map((ev) => <EvidenciaCard key={ev.id} evidencia={ev} onOpen={setViewer} onDelete={onDelete} />)}</div>
      <ReporteViewerModal evidencia={viewer} onClose={() => setViewer(null)} />
    </>
  );
}
