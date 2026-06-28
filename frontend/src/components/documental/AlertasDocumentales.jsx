// ============================================================
// COMPONENTE: AlertasDocumentales
// Alertas ejecutivas para comité SST y gerencia.
// ============================================================

import React from "react";
import { AlertCircle, CheckCircle2, Clock3, ShieldAlert } from "lucide-react";

export default function AlertasDocumentales({ kpis = {} }) {
  const alertas = [];

  if ((kpis.vencidos || 0) > 0) {
    alertas.push({
      tone: "danger",
      icon: ShieldAlert,
      title: "Documentos vencidos",
      text: `Existen ${kpis.vencidos} documentos vencidos. Se recomienda iniciar revisión inmediata.`,
    });
  }

  if ((kpis.proximos_vencer || 0) > 0) {
    alertas.push({
      tone: "warning",
      icon: Clock3,
      title: "Próximos vencimientos",
      text: `${kpis.proximos_vencer} documentos están próximos a vencer.`,
    });
  }

  if ((kpis.pendientes_revision || 0) > 0) {
    alertas.push({
      tone: "info",
      icon: AlertCircle,
      title: "Revisiones pendientes",
      text: `${kpis.pendientes_revision} documentos requieren revisión o aprobación.`,
    });
  }

  if (alertas.length === 0) {
    alertas.push({
      tone: "success",
      icon: CheckCircle2,
      title: "Control documental estable",
      text: "No hay alertas críticas en el Centro de Control Documental SST.",
    });
  }

  return (
    <article className="ccd-panel ccd-alert-panel">
      <div className="ccd-panel-title">
        <div>
          <h3>Alertas documentales</h3>
          <p>Riesgos y acciones preventivas.</p>
        </div>
      </div>

      <div className="ccd-alert-list">
        {alertas.map((alerta) => {
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
