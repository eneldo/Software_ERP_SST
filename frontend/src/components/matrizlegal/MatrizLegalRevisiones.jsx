// ============================================================
// COMPONENTE: MatrizLegalRevisiones
// FASE 1.8.5.2 - Próximas revisiones legales
// ============================================================

import React from "react";
import { CalendarClock } from "lucide-react";

export default function MatrizLegalRevisiones({ dashboard = {} }) {
  const data = dashboard?.proximas_revision_items || [];

  return (
    <article className="ml-bi-card">
      <div className="ml-panel-head mini">
        <div>
          <h3>Próximas revisiones</h3>
          <p>Requisitos a revisar o vencer en los próximos 30 días.</p>
        </div>
        <CalendarClock size={18} />
      </div>

      {data.length ? (
        <div className="ml-review-list">
          {data.map((item) => (
            <div className="ml-review-item" key={`${item.id}-${item.tipo}`}>
              <div>
                <strong>{item.codigo}</strong>
                <span>{item.norma}</span>
                <small>{item.tipo}: {item.fecha}</small>
              </div>
              <b>{item.dias} días</b>
            </div>
          ))}
        </div>
      ) : (
        <div className="ml-empty-bi">No hay revisiones próximas.</div>
      )}
    </article>
  );
}
