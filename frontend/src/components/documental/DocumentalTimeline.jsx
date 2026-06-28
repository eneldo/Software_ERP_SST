// ============================================================
// COMPONENTE: DocumentalTimeline
// Línea de tiempo ejecutiva del flujo documental.
// ============================================================

import React from "react";
import {
  CheckCircle2,
  FilePlus2,
  FileSearch,
  ShieldCheck,
  TimerReset,
} from "lucide-react";

export default function DocumentalTimeline({ kpis = {} }) {
  const steps = [
    {
      title: "Creación documental",
      text: `${kpis.total_documentos || 0} documentos registrados en biblioteca.`,
      icon: FilePlus2,
      status: "done",
    },
    {
      title: "Revisión SST",
      text: `${kpis.pendientes_revision || 0} documentos pendientes de revisión.`,
      icon: FileSearch,
      status: (kpis.pendientes_revision || 0) > 0 ? "warning" : "done",
    },
    {
      title: "Aprobación",
      text: `${kpis.vigentes || 0} documentos aprobados y vigentes.`,
      icon: CheckCircle2,
      status: (kpis.vigentes || 0) > 0 ? "done" : "pending",
    },
    {
      title: "Control de vigencia",
      text: `${kpis.vencidos || 0} vencidos · ${kpis.proximos_vencer || 0} próximos a vencer.`,
      icon: TimerReset,
      status: (kpis.vencidos || 0) > 0 ? "danger" : "done",
    },
    {
      title: "Cumplimiento SG-SST",
      text: `${Number(kpis.cumplimiento_documental || 0).toFixed(1)}% de cumplimiento documental.`,
      icon: ShieldCheck,
      status: Number(kpis.cumplimiento_documental || 0) >= 80 ? "done" : "warning",
    },
  ];

  return (
    <article className="ccd-panel ccd-timeline-panel">
      <div className="ccd-panel-title">
        <div>
          <h3>Línea de tiempo documental</h3>
          <p>Flujo Enterprise de creación, revisión, aprobación y vigencia.</p>
        </div>
      </div>

      <div className="ccd-timeline">
        {steps.map((step) => {
          const Icon = step.icon;
          return (
            <div className={`ccd-timeline-item ${step.status}`} key={step.title}>
              <div className="ccd-timeline-icon">
                <Icon size={18} />
              </div>
              <div>
                <h4>{step.title}</h4>
                <p>{step.text}</p>
              </div>
            </div>
          );
        })}
      </div>
    </article>
  );
}
