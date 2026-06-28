// ============================================================
// COMPONENTE: HistorialVersionesModal
// FASE 1.8.4.3.9.2
// Modal para consultar trazabilidad y versiones documentales.
// ============================================================

import React from "react";
import { Download, History, X } from "lucide-react";

const formatDateTime = (value) => {
  if (!value) return "Sin fecha";
  return new Date(value).toLocaleString("es-CO", {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export default function HistorialVersionesModal({ open, documento, versiones = [], loading, onClose }) {
  if (!open) return null;

  return (
    <div className="ccd-modal-backdrop" role="presentation" onClick={onClose}>
      <section className="ccd-modal" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
        <header className="ccd-modal-header">
          <div>
            <span><History size={16} /> Historial documental</span>
            <h2>{documento?.titulo || "Documento SST"}</h2>
            <p>{documento?.codigo_documental || "S/C"} · Versión actual {documento?.version || "1.0"}</p>
          </div>
          <button type="button" onClick={onClose} aria-label="Cerrar modal"><X size={20} /></button>
        </header>

        {loading ? (
          <div className="ccd-empty">Cargando historial...</div>
        ) : versiones.length === 0 ? (
          <div className="ccd-empty">Este documento aún no tiene versiones históricas registradas.</div>
        ) : (
          <div className="ccd-version-list">
            {versiones.map((item) => (
              <article className="ccd-version-item" key={item.id}>
                <div className="ccd-version-badge">v{item.version}</div>
                <div>
                  <h4>{item.descripcion_cambio || "Actualización documental"}</h4>
                  <p>Usuario: <strong>{item.usuario || "Sistema"}</strong></p>
                  <small>{formatDateTime(item.fecha_creacion)}</small>
                </div>
                {item.archivo_url && (
                  <a href={item.archivo_url} target="_blank" rel="noreferrer">
                    <Download size={16} /> Abrir
                  </a>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
