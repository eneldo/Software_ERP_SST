// ============================================================
// CHARTS BI EXECUTIVE SST
// FASE 1.1.18.2 — BI EXECUTIVE SST ENTERPRISE
// Archivo: frontend/src/components/indicadores/IndicadoresBICharts.jsx
// ============================================================

import React from "react";
import { AlertTriangle, BarChart3, Building2, MapPinned, TrendingUp } from "lucide-react";

const numero = (value, decimals = 0) =>
  Number(value || 0).toLocaleString("es-CO", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

const semaforoClass = (value = "") => {
  const sem = String(value || "").toUpperCase();
  if (sem === "VERDE") return "green";
  if (sem === "AMARILLO") return "yellow";
  return "red";
};

function maxValue(rows = [], keys = []) {
  return Math.max(
    1,
    ...rows.flatMap((row) => keys.map((key) => Number(row?.[key] || 0)))
  );
}

export function TrendChart({ data = [] }) {
  const max = maxValue(data, ["inspecciones", "capa", "incidentes", "accidentes", "auditorias", "capacitaciones"]);

  return (
    <article className="bi-panel bi-trend-panel">
      <header>
        <h3><TrendingUp size={17} /> Tendencia últimos 12 meses</h3>
        <p>Comparativo mensual de módulos críticos del SG-SST.</p>
      </header>

      <div className="bi-trend-grid">
        {data.map((row) => (
          <div className="bi-trend-month" key={row.mes}>
            <div className="bi-bars">
              <span title={`Inspecciones: ${row.inspecciones}`} style={{ height: `${Math.max((row.inspecciones / max) * 100, 4)}%` }} />
              <span title={`CAPA: ${row.capa}`} style={{ height: `${Math.max((row.capa / max) * 100, 4)}%` }} />
              <span title={`Incidentes: ${row.incidentes}`} style={{ height: `${Math.max((row.incidentes / max) * 100, 4)}%` }} />
              <span title={`Accidentes: ${row.accidentes}`} style={{ height: `${Math.max((row.accidentes / max) * 100, 4)}%` }} />
              <span title={`Auditorías: ${row.auditorias}`} style={{ height: `${Math.max((row.auditorias / max) * 100, 4)}%` }} />
              <span title={`Capacitaciones: ${row.capacitaciones}`} style={{ height: `${Math.max((row.capacitaciones / max) * 100, 4)}%` }} />
            </div>
            <small>{row.mes}</small>
          </div>
        ))}
      </div>

      <footer className="bi-legend">
        <span><i className="c1" /> Inspecciones</span>
        <span><i className="c2" /> CAPA</span>
        <span><i className="c3" /> Incidentes</span>
        <span><i className="c4" /> Accidentes</span>
        <span><i className="c5" /> Auditorías</span>
        <span><i className="c6" /> Capacitaciones</span>
      </footer>
    </article>
  );
}

export function RankingPanel({ title, subtitle, data = [], type = "sede" }) {
  const max = Math.max(1, ...data.map((item) => Number(item.score_sst || 0)));
  const Icon = type === "area" ? MapPinned : Building2;

  return (
    <article className="bi-panel">
      <header>
        <h3><Icon size={17} /> {title}</h3>
        <p>{subtitle}</p>
      </header>

      <div className="bi-ranking-list">
        {data.length ? data.slice(0, 8).map((item, index) => (
          <div className="bi-ranking-row" key={`${item.id || item.nombre}-${index}`}>
            <div>
              <strong>{index + 1}. {item.nombre}</strong>
              <small>
                {numero(item.eventos)} eventos · {numero(item.hallazgos_abiertos)} hallazgos abiertos · {numero(item.capa_abiertas)} CAPA abiertas
              </small>
            </div>
            <span className={`bi-semaforo ${semaforoClass(item.semaforo)}`}>{item.semaforo}</span>
            <i><b style={{ width: `${Math.max((Number(item.score_sst || 0) / max) * 100, 5)}%` }} /></i>
            <em>{numero(item.score_sst, 1)}%</em>
          </div>
        )) : (
          <p className="bi-empty">Sin información para mostrar.</p>
        )}
      </div>
    </article>
  );
}

export function TopRiesgosPanel({ data = [] }) {
  const max = Math.max(1, ...data.map((item) => Number(item.nivel_riesgo || 0)));

  return (
    <article className="bi-panel">
      <header>
        <h3><AlertTriangle size={17} /> Top riesgos prioritarios</h3>
        <p>Tomado de la matriz de peligros y valoración del riesgo.</p>
      </header>

      <div className="bi-risk-list">
        {data.length ? data.slice(0, 8).map((item) => (
          <div className="bi-risk-row" key={item.id}>
            <strong>{item.peligro}</strong>
            <small>{item.proceso} · {item.clasificacion} · {item.interpretacion}</small>
            <i><b style={{ width: `${Math.max((Number(item.nivel_riesgo || 0) / max) * 100, 5)}%` }} /></i>
            <span>Nivel {item.nivel_riesgo}</span>
          </div>
        )) : (
          <p className="bi-empty">Sin riesgos registrados en matriz de peligros.</p>
        )}
      </div>
    </article>
  );
}

export function TopHallazgosPanel({ data = [] }) {
  return (
    <article className="bi-panel">
      <header>
        <h3><BarChart3 size={17} /> Hallazgos críticos y abiertos</h3>
        <p>Integración de inspecciones y auditorías SST.</p>
      </header>

      <div className="bi-hallazgos-list">
        {data.length ? data.slice(0, 10).map((item) => (
          <div className="bi-hallazgo-row" key={`${item.origen}-${item.id}`}>
            <span className={`bi-semaforo ${semaforoClass(item.riesgo)}`}>{item.riesgo || "MEDIO"}</span>
            <div>
              <strong>{item.descripcion}</strong>
              <small>{item.origen} · {item.tipo || "Hallazgo"} · {item.estado || "ABIERTO"} · {item.responsable || "Sin responsable"}</small>
            </div>
          </div>
        )) : (
          <p className="bi-empty">Sin hallazgos críticos registrados.</p>
        )}
      </div>
    </article>
  );
}
