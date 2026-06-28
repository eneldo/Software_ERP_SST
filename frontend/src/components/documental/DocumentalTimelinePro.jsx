// ============================================================
// COMPONENTE: DocumentalTimelinePro
// FASE 1.8.4.3.9.2
// Línea de tiempo visual del ciclo de vida documental SST.
// ============================================================

import React from "react";
import { CheckCircle2, FilePlus2, FileSearch, ShieldCheck, TimerReset } from "lucide-react";

export default function DocumentalTimelinePro({ kpis = {} }) {
  const cumplimiento = Number(kpis.cumplimiento_documental || 0);
  const steps = [
    { title: "Creado", text: `${kpis.total_documentos || 0} documentos registrados.`, icon: FilePlus2, status: "done" },
    { title: "Revisado", text: `${kpis.pendientes_revision || 0} pendientes de revisión SST.`, icon: FileSearch, status: (kpis.pendientes_revision || 0) > 0 ? "warning" : "done" },
    { title: "Aprobado", text: `${kpis.vigentes || 0} documentos aprobados y disponibles.`, icon: CheckCircle2, status: (kpis.vigentes || 0) > 0 ? "done" : "pending" },
    { title: "Vigencia", text: `${kpis.vencidos || 0} vencidos · ${kpis.proximos_vencer || 0} próximos.`, icon: TimerReset, status: (kpis.vencidos || 0) > 0 ? "danger" : "done" },
    { title: "Cumplimiento", text: `${cumplimiento.toFixed(1)}% cumplimiento SG-SST.`, icon: ShieldCheck, status: cumplimiento >= 80 ? "done" : "warning" },
  ];

  return (
    <article className="ccd-panel ccd-timeline-panel">
      <div className="ccd-panel-title">
        <div>
          <h3>Timeline documental PRO</h3>
          <p>Flujo visual de creación, revisión, aprobación y vigencia.</p>
        </div>
      </div>

      <div className="ccd-timeline-pro">
        {steps.map((step) => {
          const Icon = step.icon;
          return (
            <div className={`ccd-timeline-pro-item ${step.status}`} key={step.title}>
              <div className="ccd-timeline-pro-icon"><Icon size={18} /></div>
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
