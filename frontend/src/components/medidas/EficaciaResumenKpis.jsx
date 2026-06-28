// ============================================================
// KPIS RESUMEN EFICACIA MEDIDAS CORRECTIVAS
// ERP SST PRO
// FASE 1.1.8.7.5.3
// Archivo: frontend/src/components/medidas/EficaciaResumenKpis.jsx
// ============================================================

import { AlertTriangle, CheckCircle2, Clock3, ShieldCheck } from "lucide-react";
import { getEficaciaResumen } from "../../utils/eficaciaMedidas";

import "../../styles/medidas-eficacia-tabla.css";

export default function EficaciaResumenKpis({ medidas = [] }) {
  const resumen = getEficaciaResumen(medidas);

  return (
    <div className="met-kpi-grid">
      <article className="met-kpi eficaz">
        <CheckCircle2 size={20} />
        <span>Eficaces</span>
        <strong>{resumen.eficaces}</strong>
      </article>

      <article className="met-kpi parcial">
        <ShieldCheck size={20} />
        <span>Parciales</span>
        <strong>{resumen.parciales}</strong>
      </article>

      <article className="met-kpi no-eficaz">
        <AlertTriangle size={20} />
        <span>No eficaces</span>
        <strong>{resumen.no_eficaces}</strong>
      </article>

      <article className="met-kpi pendiente">
        <Clock3 size={20} />
        <span>Pendientes</span>
        <strong>{resumen.pendientes}</strong>
      </article>

      <article className="met-kpi promedio">
        <ShieldCheck size={20} />
        <span>Promedio eficacia</span>
        <strong>{resumen.promedio}%</strong>
      </article>
    </div>
  );
}
