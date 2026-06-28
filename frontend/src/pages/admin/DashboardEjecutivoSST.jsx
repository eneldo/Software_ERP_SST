// ============================================================
// DASHBOARD EJECUTIVO SST PRO
// FASE 1.4.3 - DASHBOARD SST ENTERPRISE PLUS
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Award,
  BarChart3,
  Building2,
  CheckCircle2,
  ClipboardCheck,
  ClipboardList,
  RefreshCcw,
  ShieldAlert,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import AdminLayout from "../../layouts/AdminLayout";
import api from "../../api/axios";
import "../../styles/dashboard-ejecutivo-sst.css";

const COLORS = {
  ACEPTABLE: "#16a34a",
  MODERADO: "#f59e0b",
  CRITICO: "#dc2626",
  SIN_EVALUACION: "#64748b",
};

export default function DashboardEjecutivo() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const cargarDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/dashboard-sst/resumen");
      setData(response.data);
    } catch (err) {
      console.error(err);
      setError("No se pudo cargar el Dashboard Ejecutivo SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDashboard();
  }, []);

  const graficaNiveles = useMemo(() => {
    if (!data) return [];

    return [
      {
        name: "Aceptables",
        value: data.empresas_aceptables || 0,
        color: COLORS.ACEPTABLE,
      },
      {
        name: "Moderadas",
        value: data.empresas_moderadas || 0,
        color: COLORS.MODERADO,
      },
      {
        name: "Críticas",
        value: data.empresas_criticas || 0,
        color: COLORS.CRITICO,
      },
    ];
  }, [data]);

  const rankingGrafica = useMemo(() => {
    if (!data?.ranking) return [];

    return data.ranking.map((item) => ({
      empresa:
        item.empresa.length > 22
          ? `${item.empresa.substring(0, 22)}...`
          : item.empresa,
      porcentaje: Number(item.porcentaje || 0),
      nivel: item.nivel,
    }));
  }, [data]);

  const clasePromedio = useMemo(() => {
    const promedio = Number(data?.promedio_general || 0);

    if (promedio >= 86) return "aceptable";
    if (promedio >= 61) return "moderado";
    return "critico";
  }, [data]);

  const totalEstandares = useMemo(() => {
    if (!data?.ranking) return 0;

    return data.ranking.reduce(
      (acc, item) => acc + Number(item.total_estandares || 0),
      0
    );
  }, [data]);

  const empresasEvaluadas = useMemo(() => {
    if (!data?.ranking) return 0;

    return data.ranking.filter((item) => item.nivel !== "SIN_EVALUACION")
      .length;
  }, [data]);

  const empresasSinEvaluar = useMemo(() => {
    if (!data?.ranking) return 0;

    return data.ranking.filter((item) => item.nivel === "SIN_EVALUACION")
      .length;
  }, [data]);

  const top3Empresas = useMemo(() => {
    if (!data?.ranking) return [];

    return [...data.ranking]
      .filter((item) => item.nivel !== "SIN_EVALUACION")
      .sort((a, b) => Number(b.porcentaje || 0) - Number(a.porcentaje || 0))
      .slice(0, 3);
  }, [data]);

  const obtenerMedalla = (index) => {
    if (index === 0) return "🥇";
    if (index === 1) return "🥈";
    return "🥉";
  };

  const obtenerClaseAlerta = (alerta) => {
    const texto = String(alerta || "").toLowerCase();

    if (texto.includes("no tiene evaluación")) return "info";
    if (texto.includes("plan de mejora")) return "warning";
    return "danger";
  };

  return (
    <AdminLayout>
      <div className="sst-exec-page">
        <section className="hero-exec-card">
          <div className="hero-left">
            <span className="phase-pill">FASE 1.4.3 · SST Enterprise Plus</span>

            <h2>Dashboard Ejecutivo SST PRO</h2>

            <p>
              Panel gerencial para visualizar cumplimiento real del SG-SST según
              estándares mínimos aplicables: 3, 7, 21 o 60.
            </p>

            <div className="hero-actions">
              <button
                type="button"
                className="primary-action"
                onClick={cargarDashboard}
                disabled={loading}
              >
                <RefreshCcw size={18} />
                {loading ? "Actualizando..." : "Actualizar"}
              </button>
            </div>
          </div>

          <div className={`compliance-gauge ${clasePromedio}`}>
            <span>Cumplimiento SST</span>
            <strong>{data?.promedio_general ?? 0}%</strong>
            <p>
              {clasePromedio === "aceptable"
                ? "Nivel ACEPTABLE"
                : clasePromedio === "moderado"
                ? "Nivel MODERADO"
                : "Nivel CRÍTICO"}
            </p>
          </div>
        </section>

        {error && (
          <div className="sst-error-card">
            <AlertTriangle size={18} />
            {error}
          </div>
        )}

        {loading && (
          <div className="sst-state-card">
            Cargando indicadores ejecutivos SST...
          </div>
        )}

        {!loading && data && (
          <>
            <section className="executive-summary-grid">
              <article className="summary-card blue">
                <Building2 size={30} />
                <div>
                  <span>Total Empresas</span>
                  <strong>{data.total_empresas}</strong>
                </div>
              </article>

              <article className="summary-card green">
                <ShieldCheck size={30} />
                <div>
                  <span>Aceptables</span>
                  <strong>{data.empresas_aceptables}</strong>
                </div>
              </article>

              <article className="summary-card orange">
                <TrendingUp size={30} />
                <div>
                  <span>Moderadas</span>
                  <strong>{data.empresas_moderadas}</strong>
                </div>
              </article>

              <article className="summary-card red">
                <ShieldAlert size={30} />
                <div>
                  <span>Críticas</span>
                  <strong>{data.empresas_criticas}</strong>
                </div>
              </article>

              <article className="summary-card purple">
                <ClipboardList size={30} />
                <div>
                  <span>Total Estándares</span>
                  <strong>{totalEstandares}</strong>
                </div>
              </article>

              <article className="summary-card cyan">
                <ClipboardCheck size={30} />
                <div>
                  <span>Evaluadas</span>
                  <strong>{empresasEvaluadas}</strong>
                </div>
              </article>

              <article className="summary-card gray">
                <BarChart3 size={30} />
                <div>
                  <span>Sin Evaluar</span>
                  <strong>{empresasSinEvaluar}</strong>
                </div>
              </article>
            </section>

            <section className="sst-analytics-grid">
              <article className="analytics-panel">
                <div className="panel-heading">
                  <h3>Distribución por nivel SST</h3>
                  <span>Aceptable / Moderado / Crítico</span>
                </div>

                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie
                      data={graficaNiveles}
                      dataKey="value"
                      nameKey="name"
                      outerRadius={90}
                      label
                    >
                      {graficaNiveles.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </article>

              <article className="analytics-panel">
                <div className="panel-heading">
                  <h3>Ranking cumplimiento por empresa</h3>
                  <span>Porcentaje SG-SST</span>
                </div>

                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={rankingGrafica}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="empresa" tick={{ fontSize: 10 }} />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Bar dataKey="porcentaje">
                      {rankingGrafica.map((entry, index) => (
                        <Cell
                          key={index}
                          fill={COLORS[entry.nivel] || COLORS.CRITICO}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </article>
            </section>

            <section className="sst-plus-grid">
              <article className="analytics-panel">
                <div className="panel-heading">
                  <h3>Top Empresas SST</h3>
                  <span>Mayor cumplimiento</span>
                </div>

                <div className="top-empresas">
                  {top3Empresas.length > 0 ? (
                    top3Empresas.map((empresa, index) => (
                      <div key={empresa.empresa_id} className="top-card">
                        <div className="top-posicion">
                          {obtenerMedalla(index)}
                        </div>

                        <div className="top-info">
                          <strong>{empresa.empresa}</strong>
                          <span>
                            {empresa.porcentaje}% cumplimiento ·{" "}
                            {empresa.total_estandares} estándares
                          </span>
                        </div>

                        <div className={`top-level ${empresa.nivel.toLowerCase()}`}>
                          {empresa.nivel}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="sst-ok-message">
                      <AlertTriangle size={18} />
                      Aún no hay empresas evaluadas para generar top SST.
                    </div>
                  )}
                </div>
              </article>

              <article className="analytics-panel">
                <div className="panel-heading">
                  <h3>Semáforo Ejecutivo</h3>
                  <span>Resolución 0312</span>
                </div>

                <div className="semaforo-sst">
                  <div className={`semaforo-item ${clasePromedio}`}>
                    <Award size={36} />
                    <strong>{data.promedio_general}%</strong>
                    <span>
                      {clasePromedio === "aceptable"
                        ? "Aceptable"
                        : clasePromedio === "moderado"
                        ? "Moderado"
                        : "Crítico"}
                    </span>
                  </div>

                  <div className="semaforo-rangos">
                    <p>
                      <b>0% - 60%</b> Crítico
                    </p>
                    <p>
                      <b>61% - 85%</b> Moderado
                    </p>
                    <p>
                      <b>86% - 100%</b> Aceptable
                    </p>
                  </div>
                </div>
              </article>
            </section>

            <section className="sst-bottom-grid">
              <article className="analytics-panel">
                <div className="panel-heading">
                  <h3>Ranking Ejecutivo SST</h3>
                  <span>Última evaluación inicial por empresa</span>
                </div>

                <div className="sst-ranking-list">
                  {data.ranking.map((item) => (
                    <div className="sst-ranking-item" key={item.empresa_id}>
                      <div>
                        <strong>{item.empresa}</strong>
                        <span>
                          {item.total_estandares} estándares · Cumplen{" "}
                          {item.cumplen} · No cumplen {item.no_cumplen} · No
                          aplican {item.no_aplican}
                        </span>
                      </div>

                      <div className={`sst-level ${item.nivel.toLowerCase()}`}>
                        {item.porcentaje}%
                        <small>{item.nivel}</small>
                      </div>
                    </div>
                  ))}
                </div>
              </article>

              <article className="analytics-panel alert-panel">
                <div className="panel-heading">
                  <h3>Alertas Inteligentes SST</h3>
                  <span>Acciones sugeridas por nivel de cumplimiento</span>
                </div>

                <div className="sst-alert-list">
                  {data.alertas.length > 0 ? (
                    data.alertas.map((alerta, index) => (
                      <div
                        className={`sst-alert-item ${obtenerClaseAlerta(
                          alerta
                        )}`}
                        key={index}
                      >
                        <AlertTriangle size={16} />
                        <span>{alerta}</span>
                      </div>
                    ))
                  ) : (
                    <div className="sst-ok-message">
                      <CheckCircle2 size={18} />
                      No hay alertas críticas registradas.
                    </div>
                  )}
                </div>
              </article>
            </section>
          </>
        )}
      </div>
    </AdminLayout>
  );
}