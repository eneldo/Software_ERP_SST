// ============================================================
// CARDS BI EXECUTIVE SST
// FASE 1.1.18.2 — BI EXECUTIVE SST ENTERPRISE
// Archivo: frontend/src/components/indicadores/IndicadoresBICards.jsx
// ============================================================

import React from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  ClipboardCheck,
  Gauge,
  ShieldAlert,
  Target,
  Users,
} from "lucide-react";

const numero = (value, decimals = 0) =>
  Number(value || 0).toLocaleString("es-CO", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

const colorSemaforo = (value = "") => {
  const sem = String(value || "").toUpperCase();
  if (sem === "VERDE") return "green";
  if (sem === "AMARILLO") return "yellow";
  return "red";
};

function Card({ icon: Icon, label, value, detail, color = "blue" }) {
  return (
    <article className={`bi-card bi-card-${color}`}>
      <span className="bi-card-icon">
        <Icon size={21} />
      </span>
      <div>
        <small>{label}</small>
        <strong>{value}</strong>
        {detail && <p>{detail}</p>}
      </div>
    </article>
  );
}

export default function IndicadoresBICards({ kpis = {} }) {
  const semColor = colorSemaforo(kpis.semaforo);

  return (
    <section className="bi-cards-grid">
      <Card
        icon={Gauge}
        label="Score SST Ejecutivo"
        value={`${numero(kpis.score_sst, 1)}%`}
        detail={`Semáforo ${kpis.semaforo || "ROJO"}`}
        color={semColor}
      />

      <Card
        icon={ClipboardCheck}
        label="Inspecciones"
        value={numero(kpis.inspecciones)}
        detail={`${numero(kpis.cumplimiento_inspecciones, 1)}% cumplimiento`}
        color="blue"
      />

      <Card
        icon={Target}
        label="CAPA"
        value={numero(kpis.capa)}
        detail={`${numero(kpis.cumplimiento_capa, 1)}% cierre`}
        color="purple"
      />

      <Card
        icon={ShieldAlert}
        label="Eventos SST"
        value={numero(kpis.eventos)}
        detail={`${numero(kpis.eventos_abiertos)} abiertos`}
        color="amber"
      />

      <Card
        icon={AlertTriangle}
        label="Accidentes"
        value={numero(kpis.accidentes)}
        detail={`${numero(kpis.eventos_graves)} graves/críticos`}
        color="red"
      />

      <Card
        icon={Activity}
        label="Hallazgos"
        value={numero(kpis.hallazgos)}
        detail={`${numero(kpis.hallazgos_abiertos)} abiertos`}
        color="teal"
      />

      <Card
        icon={BarChart3}
        label="Auditorías"
        value={numero(kpis.auditorias)}
        detail={`${numero(kpis.cumplimiento_auditorias, 1)}% cumplimiento`}
        color="green"
      />

      <Card
        icon={Users}
        label="Empleados"
        value={numero(kpis.empleados)}
        detail={`${numero(kpis.cobertura_examenes, 1)}% exámenes`}
        color="slate"
      />
    </section>
  );
}
