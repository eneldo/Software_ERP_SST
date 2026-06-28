// ============================================================
// COMPONENTE: MatrizLegalResponsables
// FASE 1.8.5.2 - Top responsables SST
// ============================================================

import React from "react";
import { UsersRound } from "lucide-react";

export default function MatrizLegalResponsables({ dashboard = {} }) {
  const data = dashboard?.responsables_top || [];

  return (
    <article className="ml-bi-card">
      <div className="ml-panel-head mini">
        <div>
          <h3>Top responsables SST</h3>
          <p>Carga normativa por responsable asignado.</p>
        </div>
        <UsersRound size={18} />
      </div>

      {data.length ? (
        <div className="ml-top-list">
          {data.map((item, index) => (
            <div className="ml-top-item" key={`${item.nombre}-${index}`}>
              <div>
                <strong>{item.nombre}</strong>
                <span>Responsable legal SST</span>
              </div>
              <b>{item.total}</b>
            </div>
          ))}
        </div>
      ) : (
        <div className="ml-empty-bi">No hay responsables asignados.</div>
      )}
    </article>
  );
}
