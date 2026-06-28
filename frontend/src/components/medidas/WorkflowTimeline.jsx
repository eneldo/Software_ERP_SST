// ============================================================
// WORKFLOW TIMELINE — MEDIDAS CORRECTIVAS ENTERPRISE
// ERP SST PRO
// FASE 1.1.8.7.4
// Archivo: frontend/src/components/medidas/WorkflowTimeline.jsx
// ============================================================

import { CheckCircle2, Circle, Lock, RefreshCcw, Send } from "lucide-react";

function estadoLabel(value) {
  return String(value || "").replaceAll("_", " ");
}

export default function WorkflowTimeline({ workflow, loading, onRefresh, onAdvance }) {
  const pasos = workflow?.pasos || [];

  return (
    <section className="mc-enterprise-card">
      <div className="mc-enterprise-card-header">
        <div>
          <span>Workflow Enterprise</span>
          <h3>{estadoLabel(workflow?.estado_actual || "SIN ESTADO")}</h3>
        </div>
        <button className="mc-icon-btn" type="button" onClick={onRefresh} disabled={loading}>
          <RefreshCcw size={16} />
        </button>
      </div>

      <div className="mc-workflow-timeline">
        {pasos.map((paso) => (
          <div key={paso.estado} className={`mc-workflow-step ${String(paso.status || "").toLowerCase()}`}>
            <div className="mc-workflow-icon">
              {paso.status === "COMPLETADO" && <CheckCircle2 size={18} />}
              {paso.status === "ACTUAL" && <Circle size={18} />}
              {paso.status === "PENDIENTE" && <Lock size={18} />}
            </div>
            <span>{estadoLabel(paso.estado)}</span>
          </div>
        ))}
      </div>

      {!!workflow?.bloqueos?.length && (
        <div className="mc-workflow-blocks">
          <strong>Bloqueos para avanzar:</strong>
          <ul>
            {workflow.bloqueos.map((bloqueo) => (
              <li key={bloqueo}>{bloqueo}</li>
            ))}
          </ul>
        </div>
      )}

      <button
        className="mc-btn primary full"
        type="button"
        disabled={!workflow?.puede_avanzar || loading}
        onClick={() => onAdvance?.(workflow?.siguiente_estado)}
      >
        <Send size={16} />
        Avanzar a {estadoLabel(workflow?.siguiente_estado || "siguiente estado")}
      </button>
    </section>
  );
}
