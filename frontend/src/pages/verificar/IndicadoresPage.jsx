// ============================================================
// INDICADORES SST BI EXECUTIVE
// FASE 1.1.18.1 — NÚCLEO INDICADORES SST
// Archivo: frontend/src/pages/verificar/IndicadoresPage.jsx
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Download,
  Edit3,
  Eye,
  FileSpreadsheet,
  FileText,
  Gauge,
  Loader2,
  Plus,
  RefreshCcw,
  Save,
  Search,
  Target,
  Trash2,
  TrendingUp,
  X,
} from "lucide-react";

import {
  actualizarIndicadorSST,
  crearIndicadorSST,
  dashboardIndicadoresSST,
  eliminarIndicadorSST,
  exportarDashboardIndicadoresPDF,
  exportarIndicadoresExcel,
  exportarIndicadoresPDF,
  listarIndicadoresSST,
} from "../../api/indicadorSstApi";
import { listarEmpresasSST } from "../../api/empresaSstApi";
import { listarSedesSST } from "../../api/sedeSstApi";
import { listarAreasSST } from "../../api/areaSstApi";

import IndicadoresBI from "../../components/indicadores/IndicadoresBI";

import "../../styles/indicadores-sst.css";
import "../../styles/indicadores-bi.css";

const FORM_INICIAL = {
  empresa_id: "",
  sede_id: "",
  area_id: "",
  cargo_id: "",
  codigo: "",
  nombre: "",
  descripcion: "",
  categoria: "GESTION",
  tipo_indicador: "RESULTADO",
  origen_dato: "MANUAL",
  frecuencia: "MENSUAL",
  formula: "",
  unidad: "%",
  meta: 100,
  valor_actual: 0,
  resultado: 0,
  semaforo: "ROJO",
  tendencia: "ESTABLE",
  periodo_inicio: "",
  periodo_fin: "",
  responsable: "",
  fuente: "",
  observaciones: "",
  activo: true,
};

const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

const categorias = [
  "GESTION",
  "INSPECCIONES",
  "HALLAZGOS",
  "CAPA",
  "INCIDENTES",
  "ACCIDENTES",
  "CAPACITACION",
  "EPP",
  "EXAMENES",
  "AUDITORIAS",
  "DOCUMENTAL",
  "BI SST",
];

const frecuencias = ["MENSUAL", "BIMESTRAL", "TRIMESTRAL", "SEMESTRAL", "ANUAL"];
const tiposIndicador = ["ESTRUCTURA", "PROCESO", "RESULTADO", "IMPACTO"];
const semaforos = ["VERDE", "AMARILLO", "ROJO"];

const normalizarLista = (data) => (Array.isArray(data) ? data : data?.items || data?.data || []);
const numero = (value, digits = 0) => Number(value || 0).toLocaleString("es-CO", { maximumFractionDigits: digits });

const indicadorColorClass = (semaforo = "ROJO") => {
  const valor = String(semaforo || "").toUpperCase();
  if (valor === "VERDE") return "green";
  if (valor === "AMARILLO") return "yellow";
  return "red";
};

const calcularResultadoManual = (valor, meta) => {
  const v = Number(valor || 0);
  const m = Number(meta || 0);
  if (!m) return 0;
  return Math.round((v / m) * 10000) / 100;
};

const semaforoResultado = (resultado) => {
  const r = Number(resultado || 0);
  if (r >= 90) return "VERDE";
  if (r >= 70) return "AMARILLO";
  return "ROJO";
};

const limpiarPayload = (form) => ({
  empresa_id: Number(form.empresa_id || 0),
  sede_id: form.sede_id ? Number(form.sede_id) : null,
  area_id: form.area_id ? Number(form.area_id) : null,
  cargo_id: form.cargo_id ? Number(form.cargo_id) : null,
  codigo: form.codigo,
  nombre: form.nombre,
  descripcion: form.descripcion || null,
  categoria: form.categoria || "GESTION",
  tipo_indicador: form.tipo_indicador || "RESULTADO",
  origen_dato: form.origen_dato || "MANUAL",
  frecuencia: form.frecuencia || "MENSUAL",
  formula: form.formula || null,
  unidad: form.unidad || "%",
  meta: Number(form.meta || 0),
  valor_actual: Number(form.valor_actual || 0),
  resultado: Number(form.resultado || 0),
  semaforo: form.semaforo || semaforoResultado(form.resultado),
  tendencia: form.tendencia || "ESTABLE",
  periodo_inicio: form.periodo_inicio || null,
  periodo_fin: form.periodo_fin || null,
  responsable: form.responsable || null,
  fuente: form.fuente || null,
  observaciones: form.observaciones || null,
  activo: Boolean(form.activo),
});

function KpiCard({ icon: Icon, label, value, color = "blue", onClick }) {
  return (
    <button className="indicador-kpi-card" onClick={onClick} type="button">
      <span className={`indicador-kpi-icon ${color}`}><Icon size={20} /></span>
      <span>{label}</span>
      <strong>{value}</strong>
    </button>
  );
}

function DistributionBars({ titulo, data = {}, icon: Icon }) {
  const entries = Object.entries(data || {}).sort((a, b) => Number(b[1]) - Number(a[1]));
  const max = Math.max(...entries.map(([, value]) => Number(value || 0)), 1);

  return (
    <article className="indicador-chart-card">
      <h3>{Icon && <Icon size={15} />} {titulo}</h3>
      {entries.length ? entries.map(([label, value]) => (
        <div className="indicador-bar-row" key={label}>
          <div><strong>{label}</strong><span>{value}</span></div>
          <i><b style={{ width: `${Math.max((Number(value || 0) / max) * 100, 3)}%` }} /></i>
        </div>
      )) : <p className="indicador-empty">Sin información registrada.</p>}
    </article>
  );
}

export default function IndicadoresPage() {
  const [items, setItems] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [areas, setAreas] = useState([]);

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [modal, setModal] = useState(false);
  const [detalle, setDetalle] = useState(null);
  const [editando, setEditando] = useState(null);
  const [form, setForm] = useState(FORM_INICIAL);

  const [filtros, setFiltros] = useState({
    buscar: "",
    empresa_id: "",
    sede_id: "",
    area_id: "",
    categoria: "",
    semaforo: "",
  });

  const [vista, setVista] = useState("indicadores");

  const [pagina, setPagina] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const filtrosApi = useMemo(() => ({
    empresa_id: filtros.empresa_id,
    sede_id: filtros.sede_id,
    area_id: filtros.area_id,
    categoria: filtros.categoria,
    semaforo: filtros.semaforo,
    buscar: filtros.buscar,
  }), [filtros]);

  const cargarCatalogos = async () => {
    const [emp, sed, are] = await Promise.allSettled([
      listarEmpresasSST(),
      listarSedesSST(),
      listarAreasSST(),
    ]);
    if (emp.status === "fulfilled") setEmpresas(normalizarLista(emp.value));
    if (sed.status === "fulfilled") setSedes(normalizarLista(sed.value));
    if (are.status === "fulfilled") setAreas(normalizarLista(are.value));
  };

  const cargarDatos = async () => {
    try {
      setLoading(true);
      setError("");
      const [listado, dash] = await Promise.all([
        listarIndicadoresSST(filtrosApi),
        dashboardIndicadoresSST(filtrosApi),
      ]);
      setItems(normalizarLista(listado));
      setDashboard(dash);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No fue posible cargar Indicadores SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarCatalogos();
  }, []);

  useEffect(() => {
    cargarDatos();
    setPagina(1);
  }, [filtrosApi]);

  const kpis = dashboard?.kpis_automaticos || [];
  const todosIndicadores = useMemo(() => [
    ...kpis.map((kpi) => ({ ...kpi, automatico: true, id: `auto-${kpi.codigo}` })),
    ...items.map((item) => ({
      ...item,
      automatico: false,
      valor: Number(item.valor_actual || 0),
      cumplimiento: Number(item.resultado || 0),
      fuente: item.fuente || "Manual",
    })),
  ], [kpis, items]);

  const totalPaginas = Math.max(1, Math.ceil(todosIndicadores.length / pageSize));
  const paginaSegura = Math.min(pagina, totalPaginas);
  const visibles = todosIndicadores.slice((paginaSegura - 1) * pageSize, paginaSegura * pageSize);

  const cerrarModales = () => {
    setModal(false);
    setDetalle(null);
    setEditando(null);
    setForm(FORM_INICIAL);
  };

  const abrirCrear = () => {
    setEditando(null);
    setDetalle(null);
    setForm({
      ...FORM_INICIAL,
      empresa_id: filtros.empresa_id || (empresas.length === 1 ? empresas[0].id : ""),
      sede_id: filtros.sede_id || "",
      area_id: filtros.area_id || "",
      codigo: `IND-SST-${String(items.length + 1).padStart(3, "0")}`,
    });
    setModal(true);
  };

  const abrirEditar = (item) => {
    setEditando(item);
    setDetalle(null);
    setForm({
      ...FORM_INICIAL,
      ...item,
      empresa_id: item.empresa_id || "",
      sede_id: item.sede_id || "",
      area_id: item.area_id || "",
      cargo_id: item.cargo_id || "",
      periodo_inicio: item.periodo_inicio || "",
      periodo_fin: item.periodo_fin || "",
      meta: Number(item.meta || 0),
      valor_actual: Number(item.valor_actual || 0),
      resultado: Number(item.resultado || 0),
      activo: item.activo !== false,
    });
    setModal(true);
  };

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setForm((prev) => {
      const next = { ...prev, [name]: type === "checkbox" ? checked : value };
      if (["valor_actual", "meta"].includes(name)) {
        const resultado = calcularResultadoManual(next.valor_actual, next.meta);
        next.resultado = resultado;
        next.semaforo = semaforoResultado(resultado);
      }
      return next;
    });
  };

  const guardar = async (event) => {
    event.preventDefault();
    try {
      setSaving(true);
      setError("");
      const payload = limpiarPayload(form);
      if (!payload.empresa_id) {
        setError("Debe seleccionar una empresa.");
        return;
      }
      if (editando?.id) {
        await actualizarIndicadorSST(editando.id, payload);
        setSuccess("Indicador actualizado correctamente.");
      } else {
        await crearIndicadorSST(payload);
        setSuccess("Indicador creado correctamente.");
      }
      cerrarModales();
      cargarDatos();
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No fue posible guardar el indicador.");
    } finally {
      setSaving(false);
    }
  };

  const eliminar = async (item) => {
    if (!window.confirm(`¿Desea desactivar el indicador ${item.codigo}?`)) return;
    try {
      await eliminarIndicadorSST(item.id);
      setSuccess("Indicador desactivado correctamente.");
      cargarDatos();
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No fue posible desactivar el indicador.");
    }
  };

  const exportar = async (tipo) => {
    try {
      if (tipo === "excel") await exportarIndicadoresExcel(filtrosApi);
      if (tipo === "pdf") await exportarIndicadoresPDF(filtrosApi);
      if (tipo === "dashboard") await exportarDashboardIndicadoresPDF(filtrosApi);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No fue posible generar la exportación.");
    }
  };

  return (
    <main className="indicadores-page">
      <section className="indicadores-hero">
        <div>
          <h1>Indicadores SST</h1>
          <p>Monitorea el cumplimiento, desempeño y resultados del SG-SST.</p>
        </div>
        <div className="indicadores-hero-actions">
          <button title="Actualizar" onClick={cargarDatos} className="btn-indicador secondary"><RefreshCcw size={16} /> Actualizar</button>
          <button title="Exportar Excel" onClick={() => exportar("excel")} className="btn-indicador secondary"><FileSpreadsheet size={16} /> Excel</button>
          <button title="Exportar PDF" onClick={() => exportar("pdf")} className="btn-indicador secondary"><FileText size={16} /> PDF</button>
          <button title="Exportar dashboard PDF" onClick={() => exportar("dashboard")} className="btn-indicador secondary"><BarChart3 size={16} /> Dashboard PDF</button>
          <button title="Nuevo indicador" onClick={abrirCrear} className="btn-indicador primary"><Plus size={16} /> Nuevo indicador</button>
        </div>
      </section>

      {error && <div className="indicadores-alert error"><AlertTriangle size={17} /> {typeof error === "string" ? error : JSON.stringify(error)}</div>}
      {success && <div className="indicadores-alert success"><CheckCircle2 size={17} /> {success}<button onClick={() => setSuccess("")}><X size={15} /></button></div>}
      <nav className="indicadores-tabs" aria-label="Vistas indicadores SST">
        <button
          type="button"
          className={`indicadores-tab ${vista === "indicadores" ? "active" : ""}`}
          onClick={() => setVista("indicadores")}
        >
          <Gauge size={16} /> Indicadores SST
        </button>
        <button
          type="button"
          className={`indicadores-tab ${vista === "bi" ? "active" : ""}`}
          onClick={() => setVista("bi")}
        >
          <BarChart3 size={16} /> Análisis BI
        </button>
      </nav>

      {vista === "bi" ? (
        <IndicadoresBI filtros={filtrosApi} />
      ) : (
      <section className="indicadores-grid">
        <div className="indicadores-main">
          <div className="indicadores-kpis">
            <KpiCard icon={Gauge} label="Total indicadores" value={dashboard?.total_indicadores || 0} color="blue" />
            <KpiCard icon={Activity} label="Automáticos" value={dashboard?.automaticos || 0} color="purple" />
            <KpiCard icon={Edit3} label="Manuales" value={dashboard?.manuales || 0} color="amber" />
            <KpiCard icon={CheckCircle2} label="Verdes" value={dashboard?.verdes || 0} color="green" onClick={() => setFiltros({ ...filtros, semaforo: "VERDE" })} />
            <KpiCard icon={AlertTriangle} label="Rojos" value={dashboard?.rojos || 0} color="red" onClick={() => setFiltros({ ...filtros, semaforo: "ROJO" })} />
          </div>

          <div className="indicadores-kpis wide">
            <article className="indicador-progress-card">
              <span>Cumplimiento global</span>
              <strong>{numero(dashboard?.cumplimiento_global || 0, 1)}%</strong>
              <i><b style={{ width: `${Math.min(Number(dashboard?.cumplimiento_global || 0), 100)}%` }} /></i>
            </article>
            <article className="indicador-progress-card">
              <span>Score SST</span>
              <strong>{numero(dashboard?.score_sst || 0, 1)}%</strong>
              <i><b style={{ width: `${Math.min(Number(dashboard?.score_sst || 0), 100)}%` }} /></i>
            </article>
            <article className="indicador-progress-card">
              <span>Semáforo global</span>
              <strong className={`semaforo-text ${indicadorColorClass(dashboard?.semaforo_global)}`}>{dashboard?.semaforo_global || "ROJO"}</strong>
              <i><b style={{ width: `${Math.min(Number(dashboard?.score_sst || 0), 100)}%` }} /></i>
            </article>
          </div>

          <div className="indicadores-chart-grid">
            <DistributionBars titulo="Por categoría" data={dashboard?.distribucion_categoria || {}} icon={BarChart3} />
            <DistributionBars titulo="Por semáforo" data={dashboard?.distribucion_semaforo || {}} icon={Target} />
          </div>

          <section className="indicadores-panel">
            <div className="indicadores-toolbar">
              <div className="indicadores-search"><Search size={17} /><input placeholder="Buscar por código, indicador, fuente o responsable..." value={filtros.buscar} onChange={(e) => setFiltros({ ...filtros, buscar: e.target.value })} /></div>
              <button className="btn-indicador secondary" onClick={() => setFiltros({ buscar: "", empresa_id: "", sede_id: "", area_id: "", categoria: "", semaforo: "" })}><X size={15} /> Limpiar</button>
              <button className="btn-indicador secondary" onClick={cargarDatos}><RefreshCcw size={15} /> Actualizar</button>
            </div>

            <div className="indicadores-filters">
              <select value={filtros.empresa_id} onChange={(e) => setFiltros({ ...filtros, empresa_id: e.target.value })}>
                <option value="">Todas las empresas</option>
                {empresas.map((emp) => <option key={emp.id} value={emp.id}>{emp.nombre}</option>)}
              </select>
              <select value={filtros.sede_id} onChange={(e) => setFiltros({ ...filtros, sede_id: e.target.value })}>
                <option value="">Todas las sedes</option>
                {sedes.map((sede) => <option key={sede.id} value={sede.id}>{sede.nombre}</option>)}
              </select>
              <select value={filtros.area_id} onChange={(e) => setFiltros({ ...filtros, area_id: e.target.value })}>
                <option value="">Todas las áreas</option>
                {areas.map((area) => <option key={area.id} value={area.id}>{area.nombre}</option>)}
              </select>
              <select value={filtros.categoria} onChange={(e) => setFiltros({ ...filtros, categoria: e.target.value })}>
                <option value="">Todas las categorías</option>
                {categorias.map((cat) => <option key={cat} value={cat}>{cat}</option>)}
              </select>
              <select value={filtros.semaforo} onChange={(e) => setFiltros({ ...filtros, semaforo: e.target.value })}>
                <option value="">Todos los semáforos</option>
                {semaforos.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            <div className="indicadores-table-wrap">
              <table className="indicadores-table">
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Indicador</th>
                    <th>Categoría</th>
                    <th>Valor</th>
                    <th>Meta</th>
                    <th>Cumpl.</th>
                    <th>Semáforo</th>
                    <th>Fuente</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {visibles.length ? visibles.map((item) => (
                    <tr key={item.id}>
                      <td><strong>{item.codigo}</strong><small>{item.automatico ? "Automático" : "Manual"}</small></td>
                      <td><b>{item.nombre}</b><small>{item.descripcion || item.formula || "Indicador SST"}</small></td>
                      <td><span className="indicador-chip">{item.categoria}</span></td>
                      <td><strong>{numero(item.valor ?? item.valor_actual, 2)} {item.unidad}</strong></td>
                      <td>{numero(item.meta, 2)} {item.unidad}</td>
                      <td><div className="indicador-mini-progress"><i style={{ width: `${Math.min(Number(item.cumplimiento ?? item.resultado ?? 0), 100)}%` }} /></div><small>{numero(item.cumplimiento ?? item.resultado ?? 0, 1)}%</small></td>
                      <td><span className={`indicador-status ${indicadorColorClass(item.semaforo)}`}>{item.semaforo}</span></td>
                      <td>{item.fuente || "Manual"}</td>
                      <td className="indicadores-actions">
                        <button onClick={() => setDetalle(item)} title="Ver detalle"><Eye size={15} /></button>
                        {!item.automatico && <button onClick={() => abrirEditar(item)} title="Editar"><Edit3 size={15} /></button>}
                        {!item.automatico && <button onClick={() => eliminar(item)} title="Eliminar"><Trash2 size={15} /></button>}
                      </td>
                    </tr>
                  )) : (
                    <tr><td colSpan="9" className="indicador-empty-row">{loading ? "Cargando..." : "No hay indicadores registrados."}</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="indicadores-pagination">
              <span>Mostrando {todosIndicadores.length ? (paginaSegura - 1) * pageSize + 1 : 0} - {Math.min(paginaSegura * pageSize, todosIndicadores.length)} de {todosIndicadores.length}</span>
              <div>
                <select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPagina(1); }}>
                  {PAGE_SIZE_OPTIONS.map((size) => <option key={size} value={size}>{size}</option>)}
                </select>
                <button onClick={() => setPagina(1)} disabled={paginaSegura === 1}><ChevronsLeft size={16} /></button>
                <button onClick={() => setPagina((p) => Math.max(1, p - 1))} disabled={paginaSegura === 1}><ChevronLeft size={16} /></button>
                <span>Página {paginaSegura}/{totalPaginas}</span>
                <button onClick={() => setPagina((p) => Math.min(totalPaginas, p + 1))} disabled={paginaSegura === totalPaginas}><ChevronRight size={16} /></button>
                <button onClick={() => setPagina(totalPaginas)} disabled={paginaSegura === totalPaginas}><ChevronsRight size={16} /></button>
              </div>
            </div>
          </section>
        </div>

        <aside className="indicadores-side">
          <article className="indicadores-side-card main">
            <h3>Dashboard inteligente</h3>
            <div className={`indicadores-ring ${indicadorColorClass(dashboard?.semaforo_global)}`}>
              <strong>{numero(dashboard?.score_sst || 0, 0)}%</strong><span>Score SST</span>
            </div>
            <p>{dashboard?.semaforo_global || "ROJO"}: control ejecutivo de indicadores SG-SST.</p>
          </article>
          <article className="indicadores-side-card">
            <h3>Alertas Indicadores</h3>
            <p>Rojos <strong>{dashboard?.alertas?.rojos || 0}</strong></p>
            <p>Amarillos <strong>{dashboard?.alertas?.amarillos || 0}</strong></p>
            <p>Verdes <strong>{dashboard?.alertas?.verdes || 0}</strong></p>
          </article>
          <article className="indicadores-side-card">
            <h3>Recomendaciones PRO</h3>
            <ul>{(dashboard?.recomendaciones || []).map((rec, idx) => <li key={idx}>{rec}</li>)}</ul>
          </article>
        </aside>
      </section>
      )}

      {modal && (
        <div className="indicador-modal-backdrop">
          <section className="indicador-modal">
            <header>
              <div><span>{editando ? "Editar indicador" : "Nuevo indicador"}</span><h2>{form.nombre || "Indicador SST"}</h2><p>Registro manual complementario para el tablero BI SST Executive.</p></div>
              <button onClick={cerrarModales}><X /></button>
            </header>
            <form onSubmit={guardar} className="indicador-form">
              <div className="indicador-form-grid">
                <label>Empresa<select name="empresa_id" value={form.empresa_id} onChange={handleChange} required><option value="">Seleccione...</option>{empresas.map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}</select></label>
                <label>Sede<select name="sede_id" value={form.sede_id || ""} onChange={handleChange}><option value="">Sin sede</option>{sedes.map((s) => <option key={s.id} value={s.id}>{s.nombre}</option>)}</select></label>
                <label>Área<select name="area_id" value={form.area_id || ""} onChange={handleChange}><option value="">Sin área</option>{areas.map((a) => <option key={a.id} value={a.id}>{a.nombre}</option>)}</select></label>
                <label>Código<input name="codigo" value={form.codigo} onChange={handleChange} required /></label>
                <label>Nombre<input name="nombre" value={form.nombre} onChange={handleChange} required /></label>
                <label>Categoría<select name="categoria" value={form.categoria} onChange={handleChange}>{categorias.map((x) => <option key={x}>{x}</option>)}</select></label>
                <label>Tipo<select name="tipo_indicador" value={form.tipo_indicador} onChange={handleChange}>{tiposIndicador.map((x) => <option key={x}>{x}</option>)}</select></label>
                <label>Frecuencia<select name="frecuencia" value={form.frecuencia} onChange={handleChange}>{frecuencias.map((x) => <option key={x}>{x}</option>)}</select></label>
                <label>Unidad<input name="unidad" value={form.unidad} onChange={handleChange} /></label>
                <label>Meta<input type="number" name="meta" value={form.meta} onChange={handleChange} /></label>
                <label>Valor actual<input type="number" name="valor_actual" value={form.valor_actual} onChange={handleChange} /></label>
                <label>Resultado %<input type="number" name="resultado" value={form.resultado} onChange={handleChange} /></label>
                <label>Semáforo<select name="semaforo" value={form.semaforo} onChange={handleChange}>{semaforos.map((x) => <option key={x}>{x}</option>)}</select></label>
                <label>Tendencia<select name="tendencia" value={form.tendencia || "ESTABLE"} onChange={handleChange}>{["MEJORA", "ESTABLE", "DESMEJORA"].map((x) => <option key={x}>{x}</option>)}</select></label>
                <label>Responsable<input name="responsable" value={form.responsable || ""} onChange={handleChange} /></label>
                <label>Periodo inicio<input type="date" name="periodo_inicio" value={form.periodo_inicio || ""} onChange={handleChange} /></label>
                <label>Periodo fin<input type="date" name="periodo_fin" value={form.periodo_fin || ""} onChange={handleChange} /></label>
                <label className="full">Descripción<textarea name="descripcion" value={form.descripcion || ""} onChange={handleChange} /></label>
                <label className="full">Fórmula<textarea name="formula" value={form.formula || ""} onChange={handleChange} /></label>
                <label className="full">Fuente<input name="fuente" value={form.fuente || ""} onChange={handleChange} /></label>
                <label className="full">Observaciones<textarea name="observaciones" value={form.observaciones || ""} onChange={handleChange} /></label>
                {editando && <label className="switch">Activo <input type="checkbox" name="activo" checked={form.activo} onChange={handleChange} /></label>}
              </div>
              <footer>
                <button type="button" className="btn-indicador secondary" onClick={cerrarModales}>Cancelar</button>
                <button type="submit" className="btn-indicador primary" disabled={saving}>{saving ? <Loader2 className="spin" size={16} /> : <Save size={16} />} Guardar indicador</button>
              </footer>
            </form>
          </section>
        </div>
      )}

      {detalle && (
        <div className="indicador-modal-backdrop">
          <section className="indicador-detail-modal">
            <header><div><span>Detalle indicador</span><h2>{detalle.nombre}</h2><p>{detalle.codigo} · {detalle.categoria} · {detalle.fuente || "Manual"}</p></div><button onClick={() => setDetalle(null)}><X /></button></header>
            <div className="indicador-detail-grid">
              <article><span>Valor</span><strong>{numero(detalle.valor ?? detalle.valor_actual, 2)} {detalle.unidad}</strong></article>
              <article><span>Meta</span><strong>{numero(detalle.meta, 2)} {detalle.unidad}</strong></article>
              <article><span>Cumplimiento</span><strong>{numero(detalle.cumplimiento ?? detalle.resultado, 2)}%</strong></article>
              <article><span>Semáforo</span><strong className={`semaforo-text ${indicadorColorClass(detalle.semaforo)}`}>{detalle.semaforo}</strong></article>
              <article className="wide"><span>Descripción</span><strong>{detalle.descripcion || "—"}</strong></article>
              <article className="wide"><span>Fórmula</span><strong>{detalle.formula || "—"}</strong></article>
              <article><span>Responsable</span><strong>{detalle.responsable || "—"}</strong></article>
              <article><span>Frecuencia</span><strong>{detalle.frecuencia || "—"}</strong></article>
              <article><span>Tendencia</span><strong>{detalle.tendencia || "ESTABLE"}</strong></article>
            </div>
            <footer><button className="btn-indicador primary" onClick={() => setDetalle(null)}>Cerrar</button></footer>
          </section>
        </div>
      )}
    </main>
  );
}
