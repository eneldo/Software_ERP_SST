// ============================================================
// COMPONENTE: DocumentosPorVencer
// Tabla ejecutiva de documentos próximos a vencer.
// ============================================================

import React from "react";
import { AlertTriangle, CalendarClock } from "lucide-react";

const formatDate = (date) => {
  if (!date) return "Sin fecha";
  return new Date(`${date}T00:00:00`).toLocaleDateString("es-CO", { year: "numeric", month: "short", day: "2-digit" });
};

export default function DocumentosPorVencer({ documentos = [] }) {
  return (
    <article className="ccd-panel ccd-table-panel">
      <div className="ccd-panel-title">
        <div>
          <h3>Documentos próximos a vencer</h3>
          <p>Alertas documentales para revisión preventiva.</p>
        </div>
        <CalendarClock size={22} />
      </div>

      {documentos.length === 0 ? (
        <div className="ccd-empty success"><AlertTriangle size={20} /> No hay documentos próximos a vencer en el rango consultado.</div>
      ) : (
        <div className="ccd-table-wrap">
          <table className="ccd-table">
            <thead>
              <tr><th>Código</th><th>Documento</th><th>Categoría</th><th>Responsable</th><th>Vence</th><th>Días</th></tr>
            </thead>
            <tbody>
              {documentos.map((doc) => (
                <tr key={doc.id}>
                  <td><strong>{doc.codigo_documental || "S/C"}</strong></td>
                  <td>{doc.titulo || "Documento SST"}</td>
                  <td>{doc.categoria || "General"}</td>
                  <td>{doc.responsable || "Sin responsable"}</td>
                  <td>{formatDate(doc.fecha_vencimiento)}</td>
                  <td><span className="ccd-pill warning">{doc.dias_restantes ?? "--"} días</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </article>
  );
}
