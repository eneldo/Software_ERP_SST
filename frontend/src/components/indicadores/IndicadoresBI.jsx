// ============================================================
// INDICADORES BI EXECUTIVE SST ENTERPRISE
// FASE 1.1.18.2 — BI EXECUTIVE SST ENTERPRISE
// Archivo: frontend/src/components/indicadores/IndicadoresBI.jsx
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Loader2, RefreshCcw, ShieldCheck } from "lucide-react";

import {
  obtenerResumenCompletoBI,
} from "../../api/indicadorBiApi";

import IndicadoresBICards from "./IndicadoresBICards";
import {
  RankingPanel,
  TopHallazgosPanel,
  TopRiesgosPanel,
  TrendChart,
} from "./IndicadoresBICharts";

const numero = (value, decimals = 0) =>
  Number(value || 0).toLocaleString("es-CO", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

const limpiarFiltros = (filtros = {}) => ({
  empresa_id: filtros.empresa_id || "",
  sede_id: filtros.sede_id || "",
  area_id: filtros.area_id || "",
});

const semaforoClass = (value = "") => {
  const sem = String(value || "").toUpperCase();
  if (sem === "VERDE") return "green";
  if (sem === "AMARILLO") return "yellow";
  return "red";
};

export default function IndicadoresBI({ filtros = {} }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const filtrosApi = useMemo(() => limpiarFiltros(filtros), [filtros]);

  const cargarBI = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await obtenerResumenCompletoBI(filtrosApi);
      setData(response);
    } catch (err) {
      console.error("Error cargando BI SST", err);
      setError(err?.response?.data?.detail || "No fue posible cargar BI Executive SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarBI();
  }, [JSON.stringify(filtrosApi)]);

  const resumen = data?.resumen?.kpis || {};
  const recomendaciones = data?.resumen?.recomendaciones || [];
  const tendencias = data?.tendencias || [];
  const sedes = data?.ranking_sedes || [];
  const areas = data?.ranking_areas || [];
  const riesgos = data?.top_riesgos || [];
  const hallazgos = data?.top_hallazgos || [];

  return (
    <section className="bi-executive-page">
      <div className="bi-header">
        <div>
          <span><ShieldCheck size={15} /> BI EXECUTIVE SST ENTERPRISE</span>
          <h2>BI Executive SST Enterprise</h2>
          <p>
            Inteligencia gerencial con tendencias, ranking de sedes, ranking de áreas,
            riesgos críticos, hallazgos y score ejecutivo del SG-SST.
          </p>
        </div>

        <button className="btn-indicador secondary" onClick={cargarBI} disabled={loading}>
          {loading ? <Loader2 className="spin" size={16} /> : <RefreshCcw size={16} />}
          Actualizar BI
        </button>
      </div>

      {error && (
        <div className="bi-alert">
          <AlertTriangle size={17} />
          <span>{typeof error === "string" ? error : JSON.stringify(error)}</span>
        </div>
      )}

      <IndicadoresBICards kpis={resumen} />

      <section className="bi-score-panel">
        <article>
          <span>Score Ejecutivo SST</span>
          <strong className={`bi-score-${semaforoClass(resumen.semaforo)}`}>
            {numero(resumen.score_sst, 1)}%
          </strong>
          <p>Semáforo: <b>{resumen.semaforo || "ROJO"}</b></p>
          <i><b style={{ width: `${Math.min(Number(resumen.score_sst || 0), 100)}%` }} /></i>
        </article>

        <article>
          <span>Control de Eventos</span>
          <strong>{numero(resumen.control_eventos, 1)}%</strong>
          <p>{numero(resumen.eventos_abiertos)} eventos abiertos de {numero(resumen.eventos)} registrados.</p>
          <i><b style={{ width: `${Math.min(Number(resumen.control_eventos || 0), 100)}%` }} /></i>
        </article>

        <article>
          <span>Cumplimiento CAPA</span>
          <strong>{numero(resumen.cumplimiento_capa, 1)}%</strong>
          <p>{numero(resumen.capa_cerradas)} cerradas · {numero(resumen.capa_abiertas)} abiertas.</p>
          <i><b style={{ width: `${Math.min(Number(resumen.cumplimiento_capa || 0), 100)}%` }} /></i>
        </article>
      </section>

      <TrendChart data={tendencias} />

      <section className="bi-grid-2">
        <RankingPanel
          title="Ranking ejecutivo por sede"
          subtitle="Ordenado de menor a mayor score para priorizar intervención."
          data={sedes}
          type="sede"
        />

        <RankingPanel
          title="Ranking ejecutivo por área"
          subtitle="Áreas con menor score, hallazgos abiertos, CAPA y eventos SST."
          data={areas}
          type="area"
        />
      </section>

      <section className="bi-grid-2">
        <TopRiesgosPanel data={riesgos} />
        <TopHallazgosPanel data={hallazgos} />
      </section>

      <section className="bi-recommendations">
        <h3>Recomendaciones BI PRO</h3>
        <ul>
          {recomendaciones.length ? recomendaciones.map((rec, index) => (
            <li key={index}>{rec}</li>
          )) : (
            <li>Sin recomendaciones críticas para el periodo.</li>
          )}
        </ul>
      </section>
    </section>
  );
}
