// ============================================================
// COMPONENTE: WorkflowAprobacion
// Línea visual del flujo: Documento -> Firma SST -> Gerencia -> Aprobado.
// ============================================================

import React from "react";
import { FileText, PenLine, Building2, ShieldCheck } from "lucide-react";

export default function WorkflowAprobacion({ documento }) {
  const firmadoSst = Boolean(documento?.firmado_responsable_sst);
  const firmadoGerencia = Boolean(documento?.firmado_gerencia);
  const aprobado = documento?.estado_revision === "APROBADO" || documento?.estado === "APROBADO";

  const steps = [
    {
      label: "Documento",
      detail: documento?.codigo_documental || "Controlado",
      active: true,
      icon: <FileText size={18} />,
    },
    {
      label: "Firma SST",
      detail: firmadoSst ? "Firmado" : "Pendiente",
      active: firmadoSst,
      icon: <PenLine size={18} />,
    },
    {
      label: "Gerencia",
      detail: firmadoGerencia ? "Firmado" : "Pendiente",
      active: firmadoGerencia,
      icon: <Building2 size={18} />,
    },
    {
      label: "Aprobación",
      detail: aprobado ? "Aprobado" : "En gestión",
      active: aprobado,
      icon: <ShieldCheck size={18} />,
    },
  ];

  return (
    <section className="firma-workflow">
      {steps.map((step, index) => (
        <React.Fragment key={step.label}>
          <div className={`firma-workflow-step ${step.active ? "active" : ""}`}>
            <div className="firma-workflow-icon">{step.icon}</div>
            <strong>{step.label}</strong>
            <span>{step.detail}</span>
          </div>

          {index < steps.length - 1 && (
            <div className={`firma-workflow-line ${steps[index + 1].active ? "active" : ""}`} />
          )}
        </React.Fragment>
      ))}
    </section>
  );
}
