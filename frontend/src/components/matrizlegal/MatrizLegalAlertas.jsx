// ============================================================
// COMPONENTE: MatrizLegalAlertas
// FASE 1.8.5.1 / 1.8.5.2
// Alertas legales inteligentes
// ============================================================

import React from "react";
import { AlertTriangle, CheckCircle2, FileWarning, UserX, CalendarClock } from "lucide-react";

export default function MatrizLegalAlertas({ dashboard = {} }) {
  const alertas = [];

  if ((dashboard?.no_cumplen || 0) > 0) {
    alertas.push({
      tipo: "alta",
      icon: <AlertTriangle size={18} />,
      titulo: "Requisitos NO CUMPLE",
      texto: `${dashboard.no_cumplen} requisito(s) requieren plan de acción inmediato.`,
    });
  }

  if ((dashboard?.sin_evidencia || 0) > 0) {
    alertas.push({
      tipo: "media",
      icon: <FileWarning size={18} />,
      titulo: "Evidencias pendientes",
      texto: `${dashboard.sin_evidencia} requisito(s) no tienen evidencia cargada.`,
    });
  }

  if ((dashboard?.sin_responsable || 0) > 0) {
    alertas.push({
      tipo: "media",
      icon: <UserX size={18} />,
      titulo: "Responsables faltantes",
      texto: `${dashboard.sin_responsable} requisito(s) no tienen responsable asignado.`,
    });
  }

  if ((dashboard?.proximas_revision || 0) > 0) {
    alertas.push({
      tipo: "media",
      icon: <CalendarClock size={18} />,
      titulo: "Revisiones próximas",
      texto: `${dashboard.proximas_revision} requisito(s) vencen o requieren revisión en los próximos 30 días.`,
    });
  }

  if (alertas.length === 0) {
    alertas.push({
      tipo: "ok",
      icon: <CheckCircle2 size={18} />,
      titulo: "Control legal estable",
      texto: "No hay alertas críticas para la matriz legal seleccionada.",
    });
  }

  return (
    <section className="ml-alertas-enterprise">
      <div className="ml-panel-head">
        <div>
          <h3>Alertas legales inteligentes</h3>
          <p>Riesgos normativos, evidencias pendientes y revisiones preventivas.</p>
        </div>
      </div>

      <div className="ml-alert-list">
        {alertas.map((alerta, index) => (
          <article className={`ml-alert-item ${alerta.tipo}`} key={index}>
            <div className="ml-alert-icon">{alerta.icon}</div>
            <div>
              <strong>{alerta.titulo}</strong>
              <p>{alerta.texto}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
