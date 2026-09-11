// ============================================================
// DASHBOARD EJECUTIVO BI MEDIDAS CORRECTIVAS
// ERP SST PRO
// FASE 1.1.8.7.5.4
// Archivo: frontend/src/components/medidas/MedidasCorrectivasBIDashboard.jsx
// ============================================================

import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Clock3,
  DollarSign,
  RefreshCcw,
  ShieldAlert,
  ShieldCheck,
  Target,
  TrendingUp,
  UserX,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { toastError } from "../../utils/toast";

import { obtenerDashboardBiMedidasCorrectivas } from "../../api/medidasCorrectivasBiApi";
import "../../styles/medidas-correctivas-bi.css";

function money(value) {
  const number = Number(value || 0);
  return number.toLocaleString("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  });
}

function BarList({ title, items = [], suffix = "" }) {
  const max = Math.max(...items.map((x) => Number(x.value || 0)), 1);

  return (
    <article className="mcbi-card">
      <h3>{title}</h3>
      <div className="mcbi-bars">
        {items.map((item) => (
          <div className="mcbi-bar-row" key={item.name}>
            <div className="mcbi-bar-label">
              <span>{item.name}</span>
              <strong>{item.value}{suffix}</strong>
            </div>
            <div className="mcbi-bar-track">
              <span style={{ width: `${Math.max((Number(item.value || 0) / max) * 100, 4)}%` }} />
            </div>
          </div>
        ))}
        {!items.length && <div className="mcbi-empty">Sin datos disponibles.</div>}
      </div>
    </article>
  );
}

function Kpi({ icon: Icon, label, value, tone = "blue", sub }) {
  return (
    <article className={`mcbi-kpi ${tone}`}>
      <Icon size={22} />
      <span>{label}</span>
      <strong>{value}</strong>
      {sub && <small>{sub}</small>}
    </article>
  );
}

function Semaforo({ data = {} }) {
  const color = String(data.color || "VERDE").toLowerCase();

  return (
    <article className={`mcbi-semaforo ${color}`}>
      <div className="mcbi-semaforo-icon">
        {color === "rojo" ? <ShieldAlert size={30} /> : color === "naranja" ? <AlertTriangle size={30} /> : <ShieldCheck size={30} />}
      </div>
      <div>
        <span>Semáforo BI</span>
        <h2>{data.nivel || "CONTROLADO"}</h2>
        <p>{data.mensaje || "Gestión bajo control."}</p>
      </div>
      <strong>{data.score_riesgo ?? 0}</strong>
    </article>
  );
}

export default function MedidasCorrectivasBIDashboard({ empresaId = "", compact = false }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  async function cargar() {
    setLoading(true);
    try {
      const result = await obtenerDashboardBiMedidasCorrectivas({ empresa_id: empresaId });
      setData(result);
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No fue posible cargar el Dashboard BI.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    cargar();
  }, [empresaId]);

  const kpis = data?.kpis || {};
  const eficacia = data?.eficacia || {};
  const costos = data?.costos || {};
  const alertas = data?.alertas || {};
  const charts = data?.charts || {};
  const ranking = data?.ranking || {};
  const recomendaciones = data?.recomendaciones || [];

  const cumplimientoTone = useMemo(() => {
    const value = Number(kpis.cumplimiento || 0);
    if (value >= 80) return "green";
    if (value >= 50) return "orange";
    return "red";
  }, [kpis.cumplimiento]);

  return (
    <section className={`mcbi-dashboard ${compact ? "compact" : ""}`}>
      <div className="mcbi-header">
        <div>
          <span>BI Ejecutivo · Medidas Correctivas</span>
          <h2>Dashboard Ejecutivo BI</h2>
          <p>Control gerencial de eficacia, vencimientos, costos, alertas y desempeño del ciclo PHVA.</p>
        </div>

        <button className="mcbi-btn" onClick={cargar} disabled={loading}>
          <RefreshCcw size={17} />
          {loading ? "Cargando..." : "Actualizar BI"}
        </button>
      </div>

      <Semaforo data={data?.semaforo} />

      <div className="mcbi-kpi-grid">
        <Kpi icon={Target} label="Total medidas" value={kpis.total || 0} />
        <Kpi icon={Clock3} label="Abiertas" value={kpis.abiertas || 0} tone="orange" />
        <Kpi icon={AlertTriangle} label="Vencidas" value={kpis.vencidas || 0} tone="red" />
        <Kpi icon={CheckCircle2} label="Cerradas" value={kpis.cerradas || 0} tone="green" />
        <Kpi icon={TrendingUp} label="Cumplimiento" value={`${kpis.cumplimiento || 0}%`} tone={cumplimientoTone} />
        <Kpi icon={ShieldCheck} label="Eficacia promedio" value={`${eficacia.promedio || 0}%`} tone="blue" />
        <Kpi icon={UserX} label="Sin responsable" value={kpis.sin_responsable || 0} tone="red" />
        <Kpi icon={BarChart3} label="Alertas críticas" value={alertas.criticas || 0} tone="red" />
        <Kpi icon={DollarSign} label="Costo real" value={money(costos.real)} tone="green" sub={`Desv: ${money(costos.desviacion)}`} />
      </div>

      <div className="mcbi-recs">
        <h3>Recomendaciones ejecutivas</h3>
        {recomendaciones.map((item) => (
          <div key={item}>
            <AlertTriangle size={16} />
            {item}
          </div>
        ))}
      </div>

      <div className="mcbi-chart-grid">
        <BarList title="Medidas por estado" items={charts.por_estado || []} />
        <BarList title="Medidas por prioridad" items={charts.por_prioridad || []} />
        <BarList title="Medidas por origen" items={charts.por_origen || []} />
        <BarList title="Eficacia" items={charts.eficacia || []} />
        <BarList title="Responsables" items={charts.por_responsable || []} />
        <BarList title="Cumplimiento mensual" items={charts.cumplimiento_mensual || []} suffix="%" />
      </div>

      <div className="mcbi-bottom-grid">
        <article className="mcbi-card">
          <h3>Ranking medidas vencidas</h3>
          <div className="mcbi-ranking">
            {(ranking.vencidas || []).map((item) => (
              <div key={item.id}>
                <strong>{item.codigo}</strong>
                <span>{item.titulo}</span>
                <small>{item.dias_vencida} día(s) vencida · {item.responsable} · {item.prioridad}</small>
              </div>
            ))}
            {!(ranking.vencidas || []).length && <div className="mcbi-empty">No hay medidas vencidas.</div>}
          </div>
        </article>

        <BarList title="Costo real por área" items={charts.costo_por_area || []} />
      </div>
    </section>
  );
}
