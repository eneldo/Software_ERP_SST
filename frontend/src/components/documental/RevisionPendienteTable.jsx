// ============================================================
// COMPONENTE: RevisionPendienteTable
// Lista ejecutiva de responsables y carga documental.
// ============================================================

import React from "react";
import { UserCheck2 } from "lucide-react";

export default function RevisionPendienteTable({ responsables = [] }) {
  return (
    <article className="ccd-panel ccd-table-panel">
      <div className="ccd-panel-title">
        <div>
          <h3>Responsables documentales</h3>
          <p>Carga documental por responsable SST.</p>
        </div>
        <UserCheck2 size={22} />
      </div>

      {responsables.length === 0 ? (
        <div className="ccd-empty">Sin responsables asociados.</div>
      ) : (
        <div className="ccd-table-wrap compact">
          <table className="ccd-table">
            <thead><tr><th>Responsable</th><th>Total documentos</th></tr></thead>
            <tbody>
              {responsables.map((item) => (
                <tr key={item.nombre}>
                  <td>{item.nombre || "Sin responsable"}</td>
                  <td><span className="ccd-pill info">{item.total}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </article>
  );
}
