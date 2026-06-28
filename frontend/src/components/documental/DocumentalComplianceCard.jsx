// ============================================================
// COMPONENTE: DocumentalComplianceCard
// FASE 1.8.4.3.9.2
// Indicador ejecutivo de cumplimiento documental SG-SST.
// ============================================================

import React from "react";
import { ShieldCheck } from "lucide-react";

export default function DocumentalComplianceCard({ value = 0 }) {
  const porcentaje = Math.max(0, Math.min(100, Number(value || 0)));
  const nivel = porcentaje >= 90 ? "Excelente" : porcentaje >= 75 ? "Aceptable" : porcentaje >= 50 ? "En mejora" : "Crítico";

  return (
    <article className="ccd-panel ccd-compliance-card">
      <div className="ccd-compliance-header">
        <div>
          <h3>Cumplimiento documental SG-SST</h3>
          <p>Indicador global para auditoría e ISO 45001.</p>
        </div>
        <ShieldCheck size={24} />
      </div>

      <div className="ccd-compliance-circle" style={{ "--ccd-progress": `${porcentaje}%` }}>
        <div>
          <strong>{porcentaje.toFixed(1)}%</strong>
          <span>{nivel}</span>
        </div>
      </div>

      <div className="ccd-compliance-bar">
        <span style={{ width: `${porcentaje}%` }} />
      </div>
    </article>
  );
}
