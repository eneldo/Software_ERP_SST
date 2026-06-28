// ============================================================
// COMPONENTE: HistorialFirmasModal
// Modal para visualizar la trazabilidad de firmas del documento.
// ============================================================

import React from "react";
import { X, History, ShieldCheck, UserRound } from "lucide-react";
import EstadoFirmaBadge from "./EstadoFirmaBadge";

function formatDate(value) {
  if (!value) return "Sin fecha";
  return new Date(value).toLocaleString("es-CO", {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function HistorialFirmasModal({
  open,
  documento,
  historial = [],
  onClose,
}) {
  if (!open) return null;

  return (
    <div className="firma-modal-backdrop">
      <div className="firma-modal wide">
        <header className="firma-modal-header">
          <div>
            <span>Historial de firmas</span>
            <h2>{documento?.titulo || "Documento"}</h2>
            <p>{documento?.codigo_documental || documento?.codigo || "Trazabilidad documental"}</p>
          </div>

          <button type="button" className="firma-icon-button" onClick={onClose}>
            <X size={20} />
          </button>
        </header>

        {historial.length === 0 ? (
          <div className="firma-empty">
            <History size={24} />
            No hay firmas registradas para este documento.
          </div>
        ) : (
          <div className="firma-history-list">
            {historial.map((item) => (
              <article className="firma-history-item" key={item.id}>
                <div className="firma-history-icon">
                  <ShieldCheck size={20} />
                </div>

                <div className="firma-history-content">
                  <div className="firma-history-top">
                    <strong>{item.rol_firmante}</strong>
                    <EstadoFirmaBadge estado={item.estado || "FIRMADO"} />
                  </div>

                  <p>
                    <UserRound size={14} />
                    {item.nombre_firmante} · {item.cargo_firmante}
                  </p>

                  <small>{formatDate(item.fecha_firma || item.fecha_creacion)}</small>

                  {item.observaciones && (
                    <div className="firma-history-note">
                      {item.observaciones}
                    </div>
                  )}

                  {item.hash_firma && (
                    <code className="firma-hash">Hash: {item.hash_firma}</code>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
