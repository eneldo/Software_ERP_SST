import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Building2,
  CalendarCheck,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  FileWarning,
  Gauge,
  RefreshCcw,
  ShieldAlert,
  Stethoscope,
  Target,
  Users,
} from "lucide-react";
import { Link } from "react-router-dom";
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
import { listarAreasSST } from "../../api/areaSstApi";
import { listarEmpresasSST } from "../../api/empresaSstApi";
import { obtenerResumenCompletoBI } from "../../api/indicadorBiApi";
import { listarSedesSST } from "../../api/sedeSstApi";
import {
  RankingPanel,
  TopHallazgosPanel,
  TopRiesgosPanel,
  TrendChart,
} from "../../components/indicadores/IndicadoresBICharts";
import PublicReportPublisher from "../../components/dashboard/PublicReportPublisher";
import "../../styles/dashboard-ejecutivo-sst.css";
import "../../styles/indicadores-bi.css";

const COLORS = {
  ACEPTABLE: "#16a34a",
  MODERADO: "#f59e0b",
  CRITICO: "#dc2626",
  SIN_EVALUACION: "#64748b",
};

const normalizarLista = (value) => {
  if (Array.isArray(value)) return value;
  if (Array.isArray(value?.items)) return value.items;
  if (Array.isArray(value?.data)) return value.data;
  return [];
};

const numero = (value, decimals = 0) =>
  Number(value || 0).toLocaleString("es-CO", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

const fechaLegible = (value) => {
  if (!value) return "Sin actualización registrada";
  const fecha = new Date(value);
  if (Number.isNaN(fecha.getTime())) return "Sin actualización registrada";
  return fecha.toLocaleString("es-CO", { dateStyle: "medium", timeStyle: "short" });
};

function KpiCard({ icon: Icon, label, value, detail, color = "blue" }) {
  return (
    <article className={`summary-card ${color}`}>
      <Icon size={30} />
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        {detail && <small>{detail}</small>}
      </div>
    </article>
  );
}

export default function DashboardEjecutivo() {
  const rolUsuario = useMemo(() => {
    try {
      return String(JSON.parse(localStorage.getItem("user") || "{}")?.rol || "").toUpperCase();
    } catch {
      return "";
    }
  }, []);
  const puedeFiltrarCatalogos = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST"].includes(rolUsuario);
  const puedePublicarReporte = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST"].includes(rolUsuario);
  const [data, setData] = useState(null);
  const [bi, setBi] = useState(null);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [areas, setAreas] = useState([]);
  const [filtros, setFiltros] = useState({
    empresa_id: "",
    sede_id: "",
    area_id: "",
    periodo: "12",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!puedeFiltrarCatalogos) return undefined;
    let activo = true;
    const cargarCatalogos = async () => {
      try {
        const [empresasData, sedesData, areasData] = await Promise.all([
          listarEmpresasSST(),
          listarSedesSST(),
          listarAreasSST(),
        ]);
        if (!activo) return;
        setEmpresas(normalizarLista(empresasData));
        setSedes(normalizarLista(sedesData));
        setAreas(normalizarLista(areasData));
      } catch (err) {
        console.error("No se pudieron cargar los filtros del dashboard", err);
      }
    };
    cargarCatalogos();
    return () => {
      activo = false;
    };
  }, [puedeFiltrarCatalogos]);

  const filtrosApi = useMemo(
    () => ({
      empresa_id: filtros.empresa_id || undefined,
      sede_id: filtros.sede_id || undefined,
      area_id: filtros.area_id || undefined,
    }),
    [filtros.empresa_id, filtros.sede_id, filtros.area_id]
  );

  const cargarDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError("");
      const [dashboardResponse, biResponse] = await Promise.all([
        api.get("/dashboard-sst/resumen", {
          params: { empresa_id: filtrosApi.empresa_id },
        }),
        obtenerResumenCompletoBI(filtrosApi),
      ]);
      setData(dashboardResponse.data);
      setBi(biResponse);
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
          "No se pudo cargar el Dashboard Ejecutivo SST."
      );
    } finally {
      setLoading(false);
    }
  }, [filtrosApi]);

  useEffect(() => {
    cargarDashboard();
  }, [cargarDashboard]);

  const cambiarFiltro = (campo, valor) => {
    setFiltros((actual) => {
      const siguiente = { ...actual, [campo]: valor };
      if (campo === "empresa_id") {
        siguiente.sede_id = "";
        siguiente.area_id = "";
      }
      if (campo === "sede_id") siguiente.area_id = "";
      return siguiente;
    });
  };

  const sedesFiltradas = useMemo(
    () =>
      sedes.filter(
        (sede) =>
          !filtros.empresa_id ||
          String(sede.empresa_id) === String(filtros.empresa_id)
      ),
    [sedes, filtros.empresa_id]
  );

  const areasFiltradas = useMemo(
    () =>
      areas.filter(
        (area) =>
          (!filtros.empresa_id ||
            String(area.empresa_id) === String(filtros.empresa_id)) &&
          (!filtros.sede_id ||
            String(area.sede_id) === String(filtros.sede_id))
      ),
    [areas, filtros.empresa_id, filtros.sede_id]
  );

  const graficaNiveles = useMemo(
    () => [
      { name: "Aceptables", value: data?.empresas_aceptables || 0, color: COLORS.ACEPTABLE },
      { name: "Moderadas", value: data?.empresas_moderadas || 0, color: COLORS.MODERADO },
      { name: "Críticas", value: data?.empresas_criticas || 0, color: COLORS.CRITICO },
      {
        name: "Sin evaluación",
        value: data?.empresas_sin_evaluacion || 0,
        color: COLORS.SIN_EVALUACION,
      },
    ],
    [data]
  );

  const rankingGrafica = useMemo(
    () =>
      (data?.ranking || []).map((item) => {
        const empresa =
          item.empresa.length > 22
            ? `${item.empresa.substring(0, 22)}...`
            : item.empresa;
        return {
          empresa_id: item.empresa_id,
          empresa,
          empresaKey: `${empresa}||${item.empresa_id}`,
          porcentaje: Number(item.porcentaje || 0),
          nivel: item.nivel,
        };
      }),
    [data]
  );

  const clasePromedio = useMemo(() => {
    const promedio = Number(data?.promedio_general || 0);
    if (promedio >= 86) return "aceptable";
    if (promedio >= 61) return "moderado";
    return "critico";
  }, [data]);

  const kpis = bi?.resumen?.kpis || {};
  const recomendaciones = bi?.resumen?.recomendaciones || [];
  const mesesVisibles = Number(filtros.periodo || 12);
  const tendencias = (bi?.tendencias || []).slice(-mesesVisibles);
  const ultimaActualizacion = bi?.resumen?.fecha_generacion;

  return (
    <AdminLayout>
      <div className="sst-exec-page">
        <section className="hero-exec-card">
          <div className="hero-left">
            <span className="phase-pill">SST Enterprise Plus</span>
            <h2>Dashboard Ejecutivo SST PRO</h2>
            <p>
              Visión integral de evaluación, prevención, operación y cierre de acciones del SG-SST.
            </p>
            <div className="dashboard-filters" aria-label="Filtros del dashboard">
              <label>
                Empresa
                <select
                  value={filtros.empresa_id}
                  onChange={(event) => cambiarFiltro("empresa_id", event.target.value)}
                >
                  <option value="">Todas</option>
                  {empresas.map((empresa) => (
                    <option key={empresa.id} value={empresa.id}>{empresa.nombre}</option>
                  ))}
                </select>
              </label>
              <label>
                Sede
                <select
                  value={filtros.sede_id}
                  onChange={(event) => cambiarFiltro("sede_id", event.target.value)}
                >
                  <option value="">Todas</option>
                  {sedesFiltradas.map((sede) => (
                    <option key={sede.id} value={sede.id}>{sede.nombre}</option>
                  ))}
                </select>
              </label>
              <label>
                Área
                <select
                  value={filtros.area_id}
                  onChange={(event) => cambiarFiltro("area_id", event.target.value)}
                >
                  <option value="">Todas</option>
                  {areasFiltradas.map((area) => (
                    <option key={area.id} value={area.id}>{area.nombre}</option>
                  ))}
                </select>
              </label>
              <label>
                Tendencia
                <select
                  value={filtros.periodo}
                  onChange={(event) => cambiarFiltro("periodo", event.target.value)}
                >
                  <option value="6">Últimos 6 meses</option>
                  <option value="12">Últimos 12 meses</option>
                </select>
              </label>
            </div>
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
              <span className="dashboard-updated">
                <Clock3 size={15} /> {fechaLegible(ultimaActualizacion)}
              </span>
            </div>
          </div>

          <div className={`compliance-gauge ${clasePromedio}`}>
            <span>Cumplimiento de evaluadas</span>
            <strong>{numero(data?.promedio_general, 1)}%</strong>
            <p>Cobertura: {numero(data?.cobertura_evaluacion, 1)}%</p>
          </div>
        </section>

        {puedePublicarReporte && <PublicReportPublisher />}

        {error && (
          <div className="sst-error-card"><AlertTriangle size={18} />{error}</div>
        )}
        {loading && !data && (
          <div className="sst-state-card">Cargando indicadores ejecutivos SST...</div>
        )}

        {data && (
          <>
            <section className="executive-summary-grid executive-summary-grid-primary">
              <KpiCard icon={Building2} label="Empresas activas" value={numero(data.total_empresas)} detail={`${numero(data.empresas_evaluadas)} evaluadas`} color="blue" />
              <KpiCard icon={ClipboardCheck} label="Cobertura evaluación" value={`${numero(data.cobertura_evaluacion, 1)}%`} detail={`${numero(data.empresas_sin_evaluacion)} sin evaluar`} color="cyan" />
              <KpiCard icon={Gauge} label="Score SST integral" value={`${numero(kpis.score_sst, 1)}%`} detail={`Semáforo ${kpis.semaforo || "ROJO"}`} color="purple" />
              <KpiCard icon={ShieldAlert} label="Empresas críticas" value={numero(data.empresas_criticas)} detail="Excluye empresas sin evaluación" color="red" />
              <KpiCard icon={FileWarning} label="Acciones vencidas" value={numero(data.acciones_vencidas)} detail={`${numero(data.acciones_pendientes)} pendientes`} color="orange" />
              <KpiCard icon={Target} label="Cierre plan mejora" value={`${numero(data.cumplimiento_plan_mejoramiento, 1)}%`} detail={`${numero(data.acciones_finalizadas)} de ${numero(data.total_acciones)} finalizadas`} color="green" />
              <KpiCard icon={Activity} label="Eventos graves" value={numero(kpis.eventos_graves)} detail={`${numero(kpis.eventos_abiertos)} eventos abiertos`} color="red" />
              <KpiCard icon={Stethoscope} label="Cobertura exámenes" value={`${numero(kpis.cobertura_examenes, 1)}%`} detail={`${numero(kpis.empleados)} empleados activos`} color="gray" />
            </section>

            <section className="operational-kpis" aria-label="Indicadores operativos SST">
              <KpiCard icon={ClipboardCheck} label="Inspecciones" value={numero(kpis.inspecciones)} detail={`${numero(kpis.cumplimiento_inspecciones, 1)}% cerradas`} color="blue" />
              <KpiCard icon={Target} label="CAPA" value={numero(kpis.capa)} detail={`${numero(kpis.capa_abiertas)} abiertas`} color="purple" />
              <KpiCard icon={AlertTriangle} label="Hallazgos" value={numero(kpis.hallazgos)} detail={`${numero(kpis.hallazgos_abiertos)} abiertos`} color="orange" />
              <KpiCard icon={BarChart3} label="Auditorías" value={numero(kpis.auditorias)} detail={`${numero(kpis.cumplimiento_auditorias, 1)}% ejecutadas`} color="green" />
              <KpiCard icon={CalendarCheck} label="Capacitaciones" value={numero(kpis.capacitaciones)} detail={`${numero(kpis.cumplimiento_capacitaciones, 1)}% ejecutadas`} color="cyan" />
              <KpiCard icon={Users} label="Cobertura EPP" value={`${numero(kpis.cobertura_epp, 1)}%`} detail="Entregas frente a empleados" color="gray" />
            </section>

            <section className="sst-analytics-grid">
              <article className="analytics-panel">
                <div className="panel-heading">
                  <h3>Distribución por nivel SST</h3>
                  <span>Sin evaluación se muestra por separado</span>
                </div>
                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie data={graficaNiveles} dataKey="value" nameKey="name" outerRadius={90} label>
                      {graficaNiveles.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </article>

              <article className="analytics-panel">
                <div className="panel-heading">
                  <h3>Cumplimiento por empresa</h3>
                  <span>Última evaluación inicial vigente</span>
                </div>
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={rankingGrafica}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="empresaKey"
                      tick={{ fontSize: 10 }}
                      tickFormatter={(value) => String(value).split("||")[0]}
                    />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Bar dataKey="porcentaje">
                      {rankingGrafica.map((entry) => <Cell key={entry.empresa_id} fill={COLORS[entry.nivel] || COLORS.CRITICO} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </article>
            </section>

            <TrendChart data={tendencias} />

            <section className="bi-grid-2 dashboard-bi-grid">
              <RankingPanel title="Sedes que requieren intervención" subtitle="Menor score SST primero." data={bi?.ranking_sedes || []} type="sede" />
              <RankingPanel title="Áreas que requieren intervención" subtitle="Menor score, hallazgos y CAPA abiertas." data={bi?.ranking_areas || []} type="area" />
            </section>

            <section className="bi-grid-2 dashboard-bi-grid">
              <TopRiesgosPanel data={bi?.top_riesgos || []} />
              <TopHallazgosPanel data={bi?.top_hallazgos || []} />
            </section>

            <section className="sst-bottom-grid dashboard-actions-grid">
              <article className="analytics-panel">
                <div className="panel-heading">
                  <h3>Alertas de evaluación y mejora</h3>
                  <span>Acceso directo a la gestión</span>
                </div>
                <div className="sst-alert-list">
                  {(data.alertas || []).length ? data.alertas.map((alerta, index) => (
                    <div className="sst-alert-item danger" key={`${alerta}-${index}`}>
                      <AlertTriangle size={16} />
                      <span>{alerta}</span>
                      <Link className="sst-alert-action" to="/planear/evaluacion-inicial">Gestionar</Link>
                    </div>
                  )) : (
                    <div className="sst-ok-message"><CheckCircle2 size={18} />No hay alertas críticas registradas.</div>
                  )}
                </div>
              </article>

              <article className="analytics-panel executive-recommendations">
                <div className="panel-heading">
                  <h3>Prioridades gerenciales</h3>
                  <span>Generadas con los datos actuales</span>
                </div>
                <ul>
                  {recomendaciones.length ? recomendaciones.map((item, index) => (
                    <li key={`${item}-${index}`}>{item}</li>
                  )) : <li>Mantener el seguimiento mensual del SG-SST.</li>}
                </ul>
                <Link className="secondary-dashboard-link" to="/verificar/indicadores">Abrir BI completo</Link>
              </article>
            </section>
          </>
        )}
      </div>
    </AdminLayout>
  );
}
