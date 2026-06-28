// ============================================================
// COMPONENTE: MatrizLegalRiesgo
// FASE 1.8.5.2 - Riesgo Legal Executive
// ============================================================

import React from "react";
import { ShieldAlert, ShieldCheck, ShieldQuestion } from "lucide-react";

export default function MatrizLegalRiesgo({ dashboard = {} }) {
  const riesgo = dashboard?.riesgo_legal || "BAJO";
  const cumplimiento = dashboard?.porcentaje_cumplimiento || 0;

  const config = {
    BAJO: {
      icon: <ShieldCheck size={30} />,
      text: "Control legal estable",
      className: "bajo",
    },
    MEDIO: {
      icon: <ShieldQuestion size={30} />,
      text: "Existen brechas documentales o preventivas",
      className: "medio",
    },
    ALTO: {
      icon: <ShieldAlert size={30} />,
      text: "Requiere gestión inmediata de cumplimiento",
      className: "alto",
    },
  };

  const item = config[riesgo] || config.BAJO;

  return (
    <article className={`ml-risk-card ${item.className}`}>
      <div className="ml-panel-head mini">
        <div>
          <h3>Riesgo legal ejecutivo</h3>
          <p>Clasificación automática según cumplimiento y alertas.</p>
        </div>
        {item.icon}
      </div>

      <div className="ml-risk-body">
        <span>RIESGO</span>
        <strong>{riesgo}</strong>
        <p>{item.text}</p>
      </div>

      <div className="ml-risk-footer">
        <span>Cumplimiento actual</span>
        <b>{cumplimiento}%</b>
      </div>
    </article>
  );
}
