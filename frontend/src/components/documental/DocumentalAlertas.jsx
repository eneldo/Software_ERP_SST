// ============================================================
// COMPONENTE: DocumentalAlertas
// FASE 1.8.4.3.9.2
// Alertas visuales Enterprise: vencidos, próximos, revisión y aprobador.
// ============================================================

import React from "react";
import { AlertCircle, CheckCircle2, Clock3, ShieldAlert, UserX } from "lucide-react";

export default function DocumentalAlertas({ kpis = {}, alertas = {} }) {
  const items = [];

  const vencidos = alertas.vencidos ?? kpis.vencidos ?? 0;
  const proximos = alertas.proximos ?? kpis.proximos_vencer ?? 0;
  const revision = alertas.pendientes_revision ?? kpis.pendientes_revision ?? 0;
  const sinAprobador = alertas.sin_aprobador ?? 0;

  if (vencidos > 0) {
    items.push({ tone: "danger", icon: ShieldAlert, title: "Documentos vencidos", text: `${vencidos} documentos requieren revisión inmediata.` });
  }
  if (proximos > 0) {
    items.push({ tone: "warning", icon: Clock3, title: "Próximos vencimientos", text: `${proximos} documentos están próximos a vencer.` });
  }
  if (revision > 0) {
    items.push({ tone: "info", icon: AlertCircle, title: "Revisiones pendientes", text: `${revision} documentos requieren revisión o aprobación.` });
  }
  if (sinAprobador > 0) {
    items.push({ tone: "purple", icon: UserX, title: "Sin aprobador asignado", text: `${sinAprobador} documentos no tienen aprobador definido.` });
  }
  if (items.length === 0) {
    items.push({ tone: "success", icon: CheckCircle2, title: "Control documental estable", text: "No hay alertas críticas en el Centro Documental SST." });
  }

  return (
    <article className="ccd-panel ccd-alert-panel">
      <div className="ccd-panel-title">
        <div>
          <h3>Alertas documentales</h3>
          <p>Riesgos, vencimientos y acciones preventivas.</p>
        </div>
      </div>

      <div className="ccd-alert-list">
        {items.map((alerta) => {
          const Icon = alerta.icon;
          return (
            <div className={`ccd-alert ${alerta.tone}`} key={alerta.title}>
              <Icon size={20} />
              <div>
                <strong>{alerta.title}</strong>
                <span>{alerta.text}</span>
              </div>
            </div>
          );
        })}
      </div>
    </article>
  );
}
