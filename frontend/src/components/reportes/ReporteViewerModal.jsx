import React from "react";
import { Download, Loader2, X } from "lucide-react";
import useReporteAssetUrl from "./useReporteAssetUrl";

export default function ReporteViewerModal({ evidencia, onClose }) {
  const asset = useReporteAssetUrl(evidencia?.archivo_url);
  if (!evidencia) return null;
  const tipo = evidencia.tipo_archivo || "OTRO";
  return (
    <div className="rep-ev-modal-backdrop" onClick={onClose}>
      <div className="rep-ev-modal" onClick={(e) => e.stopPropagation()}>
        <div className="rep-ev-modal-head">
          <div><h3>{evidencia.archivo_nombre || "Evidencia SST"}</h3><p>{tipo} · {evidencia.categoria_ia || "Sin clasificación"}</p></div>
          <div className="rep-ev-modal-actions">
            {asset.url && <a href={asset.url} target="_blank" rel="noreferrer" download={evidencia.archivo_nombre} title="Abrir o descargar evidencia"><Download size={18} /></a>}
            <button type="button" onClick={onClose} title="Cerrar visor" aria-label="Cerrar visor"><X size={18} /></button>
          </div>
        </div>
        <div className="rep-ev-modal-body">
          {asset.loading && <div className="rep-ev-viewer-status"><Loader2 className="rep-ev-loading" /><span>Cargando evidencia...</span></div>}
          {asset.error && <div className="rep-ev-viewer-status error"><b>!</b><span>No fue posible cargar la evidencia.</span></div>}
          {asset.url && tipo === "IMAGEN" && <img src={asset.url} alt={evidencia.archivo_nombre || "Evidencia"} />}
          {asset.url && tipo === "VIDEO" && <video src={asset.url} controls />}
          {asset.url && tipo === "PDF" && <iframe src={asset.url} title="PDF evidencia" />}
          {asset.url && tipo === "AUDIO" && <audio src={asset.url} controls />}
          {asset.url && !["IMAGEN", "VIDEO", "PDF", "AUDIO"].includes(tipo) && <a href={asset.url} target="_blank" rel="noreferrer">Abrir evidencia</a>}
        </div>
      </div>
    </div>
  );
}
