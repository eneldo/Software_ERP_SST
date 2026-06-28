// ============================================================
// COMPONENTE: FirmaResumenCards
// KPIs del módulo de firma y aprobación digital SST.
// ============================================================

import React from "react";
import {
  FileText,
  CheckCircle2,
  Clock3,
  ShieldCheck,
  XCircle,
  PenLine,
} from "lucide-react";

export default function FirmaResumenCards({ resumen = {} }) {
  const cards = [
    {
      label: "Total documentos",
      value: resumen.total_documentos || 0,
      icon: <FileText size={22} />,
      type: "blue",
      detail: "Documentos controlados",
    },
    {
      label: "Firmados",
      value: resumen.documentos_firmados || 0,
      icon: <PenLine size={22} />,
      type: "green",
      detail: "Con firma registrada",
    },
    {
      label: "Pendientes",
      value: resumen.documentos_pendientes || 0,
      icon: <Clock3 size={22} />,
      type: "yellow",
      detail: "Por firma o aprobación",
    },
    {
      label: "Aprobados",
      value: resumen.aprobados || 0,
      icon: <ShieldCheck size={22} />,
      type: "cyan",
      detail: "Validación documental",
    },
    {
      label: "Rechazados",
      value: resumen.rechazados || 0,
      icon: <XCircle size={22} />,
      type: "red",
      detail: "Con observaciones",
    },
    {
      label: "Cumplimiento firmas",
      value: `${resumen.cumplimiento_firmas || 0}%`,
      icon: <CheckCircle2 size={22} />,
      type: "dark",
      detail: "Indicador SG-SST",
    },
  ];

  return (
    <section className="firma-kpi-grid">
      {cards.map((card) => (
        <article className={`firma-kpi-card ${card.type}`} key={card.label}>
          <div className="firma-kpi-icon">{card.icon}</div>
          <div>
            <h3>{card.value}</h3>
            <p>{card.label}</p>
            <small>{card.detail}</small>
          </div>
        </article>
      ))}
    </section>
  );
}
