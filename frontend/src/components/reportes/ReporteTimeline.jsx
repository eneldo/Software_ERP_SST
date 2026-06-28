// ============================================================
// TIMELINE REPORTES SST
// FASE 1.1.25.6
// Archivo: frontend/src/components/reportes/ReporteTimeline.jsx
// ============================================================

import React from "react";

const formatDate = (v) => {
  if (!v) return "Sin fecha";
  try { return new Date(v).toLocaleString(); } catch { return v; }
};

export default function ReporteTimeline({ items = [] }) {
  if (!items.length) return <div className="rep-ev-empty">Sin eventos de timeline.</div>;
  return (
    <div className="rep-timeline">
      {items.map((it, idx) => (
        <div className="rep-timeline-item" key={`${it.tipo}-${idx}`}>
          <span className="rep-timeline-dot" />
          <div>
            <strong>{it.titulo}</strong>
            <small>{formatDate(it.fecha)} · {it.tipo}</small>
            {it.descripcion && <p>{it.descripcion}</p>}
          </div>
        </div>
      ))}
    </div>
  );
}
