// ============================================================
// COMPONENTE: MatrizLegalDashboard
// FASE 1.8.5.1 / 1.8.5.2
// Dashboard Ejecutivo Legal SST Enterprise
// ============================================================

import React from "react";
import {
  Scale,
  ShieldCheck,
  AlertTriangle,
  FileWarning,
  Users,
  Activity,
} from "lucide-react";

export default function MatrizLegalDashboard({ dashboard = {}, kpis = {} }) {
  const total = dashboard?.total ?? kpis?.total ?? 0;
  const cumplimiento =
    dashboard?.porcentaje_cumplimiento ?? kpis?.porcentaje ?? 0;

  const cards = [
    {
      label: "Total requisitos",
      value: total,
      note: "Inventario normativo activo",
      icon: <Scale size={20} />,
      type: "blue",
    },
    {
      label: "Cumplimiento legal",
      value: `${cumplimiento}%`,
      note: "Requisitos en estado CUMPLE",
      icon: <ShieldCheck size={20} />,
      type: "green",
    },
    {
      label: "Sin evidencia",
      value: dashboard?.sin_evidencia ?? 0,
      note: "Requieren soporte documental",
      icon: <FileWarning size={20} />,
      type: "yellow",
    },
    {
      label: "No cumplen",
      value: dashboard?.no_cumplen ?? kpis?.noCumplen ?? 0,
      note: "Riesgo legal inmediato",
      icon: <AlertTriangle size={20} />,
      type: "red",
    },
    {
      label: "Responsables",
      value: dashboard?.responsables ?? 0,
      note: "Responsables asignados",
      icon: <Users size={20} />,
      type: "cyan",
    },
    {
      label: "Riesgo legal",
      value: dashboard?.riesgo_legal || "BAJO",
      note: "Evaluación automática",
      icon: <Activity size={20} />,
      type:
        dashboard?.riesgo_legal === "ALTO"
          ? "red"
          : dashboard?.riesgo_legal === "MEDIO"
          ? "yellow"
          : "green",
    },
  ];

  return (
    <section className="ml-executive-kpis">
      {cards.map((card) => (
        <article className={`ml-executive-card ${card.type}`} key={card.label}>
          <div className="ml-executive-icon">{card.icon}</div>
          <div>
            <span>{card.label}</span>
            <strong>{card.value}</strong>
            <small>{card.note}</small>
          </div>
        </article>
      ))}
    </section>
  );
}
