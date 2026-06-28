import React from "react";
import {
  Archive,
  CheckCircle2,
  Clock3,
  XCircle,
  FileClock,
  History,
  ShieldCheck,
} from "lucide-react";

export default function DocumentalKPIs({ kpis = {} }) {
  const cards = [
    {
      title: "Total documentos",
      subtitle: "Inventario documental activo",
      value: kpis.total_documentos || 0,
      icon: <Archive size={22} />,
      type: "blue",
      tag: "Inventario SG-SST",
    },
    {
      title: "Vigentes",
      subtitle: "Aprobados y disponibles",
      value: kpis.vigentes || 0,
      icon: <CheckCircle2 size={22} />,
      type: "green",
      tag: "Controlado",
    },
    {
      title: "Próximos a vencer",
      subtitle: "Alertas dentro del rango",
      value: kpis.proximos_vencer || 0,
      icon: <Clock3 size={22} />,
      type: "yellow",
      tag: "Preventivo",
    },
    {
      title: "Vencidos",
      subtitle: "Requieren revisión inmediata",
      value: kpis.vencidos || 0,
      icon: <XCircle size={22} />,
      type: "red",
      tag: "Crítico",
    },
    {
      title: "Pendientes revisión",
      subtitle: "Documentos por gestionar",
      value: kpis.pendientes_revision || 0,
      icon: <FileClock size={22} />,
      type: "cyan",
      tag: "Workflow",
    },
    {
      title: "Versiones históricas",
      subtitle: "Trazabilidad documental",
      value: kpis.total_versiones || 0,
      icon: <History size={22} />,
      type: "purple",
      tag: "Auditable",
    },
    {
      title: "Cumplimiento documental",
      subtitle: "Vigentes sobre total documental",
      value: `${kpis.cumplimiento_documental || 0}%`,
      icon: <ShieldCheck size={22} />,
      type: "dark",
      tag: "ISO 45001",
    },
  ];

  return (
    <section className="ccd-kpi-grid-pro">
      {cards.map((card) => (
        <article className={`ccd-kpi-card-pro ${card.type}`} key={card.title}>
          <div className="ccd-kpi-top">
            <div className="ccd-kpi-icon-pro">{card.icon}</div>
            <span>{card.tag}</span>
          </div>

          <h3>{card.value}</h3>
          <p>{card.title}</p>
          <small>{card.subtitle}</small>
        </article>
      ))}
    </section>
  );
}