// ============================================================
// INDICADOR DE EFICACIA EN TABLA PRINCIPAL
// ERP SST PRO
// FASE 1.1.8.7.5.3
// Archivo: frontend/src/components/medidas/EficaciaIndicadorTabla.jsx
// ============================================================

import { AlertTriangle, CheckCircle2, Clock3, ShieldCheck } from "lucide-react";
import { getEficaciaEstado } from "../../utils/eficaciaMedidas";

import "../../styles/medidas-eficacia-tabla.css";

function IconByState({ state }) {
  if (state === "EFICAZ") return <CheckCircle2 size={15} />;
  if (state === "PARCIAL") return <ShieldCheck size={15} />;
  if (state === "NO_EFICAZ") return <AlertTriangle size={15} />;
  return <Clock3 size={15} />;
}

export default function EficaciaIndicadorTabla({ medida, compact = false }) {
  const eficacia = getEficaciaEstado(medida);

  return (
    <div className={`met-eficacia ${eficacia.className} ${compact ? "compact" : ""}`} title={eficacia.description}>
      <div className="met-eficacia-head">
        <span className="met-eficacia-icon">
          <IconByState state={eficacia.key} />
        </span>

        <strong>{eficacia.shortLabel}</strong>
      </div>

      {!compact && (
        <>
          <div className="met-eficacia-bar">
            <span style={{ width: `${eficacia.percent ?? 0}%` }} />
          </div>

          <small>
            {eficacia.percent !== null && eficacia.percent !== undefined
              ? `${eficacia.percent}%`
              : "Sin verificar"}
          </small>
        </>
      )}
    </div>
  );
}
