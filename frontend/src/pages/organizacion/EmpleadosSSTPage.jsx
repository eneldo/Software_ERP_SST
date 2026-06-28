// ============================================================
// EMPLEADOS SST ENTERPRISE 360° - ERP SST PRO
// FASE 1.1.5.3.1 — MEJORA INTERFAZ EMPLEADOS ENTERPRISE 360°
// Archivo: frontend/src/pages/organizacion/EmpleadosSSTPage.jsx
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  BarChart3,
  AlertTriangle,
  BriefcaseBusiness,
  Building2,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Download,
  Edit3,
  Eye,
  FileSpreadsheet,
  FileText,
  Filter,
  CalendarCheck,
  Mail,
  MapPin,
  PieChart,
  Network,
  Plus,
  RefreshCcw,
  Search,
  Target,
  Trash2,
  Users,
  X,
} from "lucide-react";

import {
  actualizarEmpleado,
  crearEmpleado,
  dashboardEmpleados,
  eliminarEmpleado,
  exportarEmpleadosExcel,
  exportarEmpleadosPdf,
  exportarFichaEmpleadoPdf,
  listarEmpleados,
} from "../../api/empleadoSstApi";
import { listarEmpresasSST } from "../../api/empresaSstApi";
import { listarSedesSST } from "../../api/sedeSstApi";
import { listarAreasSST } from "../../api/areaSstApi";
import { listarCargosSST } from "../../api/cargoSstApi";
import "../../styles/empleados-sst.css";

const initialForm = {
  nombres: "",
  apellidos: "",
  tipo_documento: "CC",
  documento: "",
  correo: "",
  telefono: "",
  fecha_nacimiento: "",
  fecha_ingreso: "",
  tipo_contrato: "INDEFINIDO",
  estado_laboral: "ACTIVO",
  empresa_id: "",
  sede_id: "",
  area_id: "",
  cargo_id: "",
  activo: true,
};

const emptyDashboard = {
  kpis: {
    total: 0,
    activos: 0,
    inactivos: 0,
    empresas: 0,
    sin_sede: 0,
    sin_area: 0,
    sin_cargo: 0,
    sin_correo: 0,
    completitud_organizacional: 100,
    activos_pct: 0,
    estructura_completa: 0,
    pendientes_criticos: 0,
  },
  charts: {
    por_empresa: [],
    por_sede: [],
    por_area: [],
    por_cargo: [],
    por_estado: [],
    por_contrato: [],
  },
  alertas: {
    sin_sede: 0,
    sin_area: 0,
    sin_cargo: 0,
    sin_correo: 0,
  },
};

function normalizarLista(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

function toSelect(value) {
  return value === null || value === undefined ? "" : String(value);
}

function toIntOrNull(value) {
  if (value === "" || value === null || value === undefined) return null;
  const parsed = Number(value);
  return Number.isNaN(parsed) ? null : parsed;
}

function nombreCompleto(empleado) {
  return `${empleado?.nombres || ""} ${empleado?.apellidos || ""}`.trim() || "Sin nombre";
}

function formatDate(date) {
  if (!date) return "Sin dato";
  return String(date).slice(0, 10);
}

function buscarNombre(lista, id, fallback = "Sin dato") {
  if (!id) return fallback;
  const item = lista.find((x) => Number(x.id) === Number(id));
  return item?.nombre || fallback;
}

function KpiCard({ icon: Icon, label, value, tone = "blue" }) {
  return (
    <article className={`emp-kpi-card emp-tone-${tone}`}>
      <div className="emp-kpi-icon"><Icon size={18} /></div>
      <div>
        <span>{label}</span>
        <strong>{value ?? 0}</strong>
      </div>
    </article>
  );
}

function MiniBar({ title, data = [] }) {
  const max = Math.max(...data.map((x) => Number(x.value || 0)), 1);
  return (
    <article className="emp-chart-card">
      <h3>{title}</h3>
      <div className="emp-chart-list">
        {data.length === 0 && <small>Sin datos disponibles</small>}
        {data.slice(0, 5).map((item) => (
          <div className="emp-bar-row" key={`${title}-${item.name}`}>
            <div className="emp-bar-meta">
              <span>{item.name}</span>
              <b>{item.value}</b>
            </div>
            <div className="emp-bar-track">
              <div style={{ width: `${(Number(item.value || 0) / max) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

function EmpleadoDetalleModal({ empleado, relaciones, onClose, onPdf }) {
  if (!empleado) return null;
  const { empresas, sedes, areas, cargos } = relaciones;
  return (
    <div className="emp-modal-backdrop">
      <section className="emp-detail-modal">
        <header className="emp-modal-header">
          <div>
            <span>Vista detallada del empleado</span>
            <h2>{nombreCompleto(empleado)}</h2>
            <p>Ficha organizacional conectada con empresa, sede, área y cargo.</p>
          </div>
          <button className="emp-close" onClick={onClose}><X size={20} /></button>
        </header>

        <div className="emp-detail-grid">
          <article>
            <h3>Información personal</h3>
            <p><b>Documento:</b> {empleado.tipo_documento} {empleado.documento}</p>
            <p><b>Correo:</b> {empleado.correo || "Sin correo"}</p>
            <p><b>Teléfono:</b> {empleado.telefono || "Sin teléfono"}</p>
            <p><b>Fecha nacimiento:</b> {formatDate(empleado.fecha_nacimiento)}</p>
          </article>
          <article>
            <h3>Información laboral</h3>
            <p><b>Empresa:</b> {empleado.empresa_nombre || buscarNombre(empresas, empleado.empresa_id, "Sin empresa")}</p>
            <p><b>Sede:</b> {empleado.sede_nombre || buscarNombre(sedes, empleado.sede_id, "Sin sede")}</p>
            <p><b>Área:</b> {empleado.area_nombre || buscarNombre(areas, empleado.area_id, "Sin área")}</p>
            <p><b>Cargo:</b> {empleado.cargo_nombre || buscarNombre(cargos, empleado.cargo_id, "Sin cargo")}</p>
            <p><b>Ingreso:</b> {formatDate(empleado.fecha_ingreso)}</p>
            <p><b>Contrato:</b> {empleado.tipo_contrato || "Sin dato"}</p>
          </article>
          <article>
            <h3>Estado SST</h3>
            <p><b>Estado laboral:</b> {empleado.estado_laboral || "Sin dato"}</p>
            <p><b>Activo:</b> {empleado.activo ? "Sí" : "No"}</p>
          </article>
        </div>

        <footer className="emp-modal-footer">
          <button className="emp-btn-light" onClick={onClose}>Cerrar</button>
          <button className="emp-btn-primary" onClick={() => onPdf(empleado.id)}><FileText size={16} /> Exportar ficha PDF</button>
        </footer>
      </section>
    </div>
  );
}

function EmpleadoFormModal({ empleado, relaciones, onClose, onSave }) {
  const [tab, setTab] = useState("personal");
  const [form, setForm] = useState(initialForm);
  const { empresas, sedes, areas, cargos } = relaciones;

  useEffect(() => {
    if (empleado) {
      setForm({
        ...initialForm,
        ...empleado,
        fecha_nacimiento: empleado.fecha_nacimiento ? String(empleado.fecha_nacimiento).slice(0, 10) : "",
        fecha_ingreso: empleado.fecha_ingreso ? String(empleado.fecha_ingreso).slice(0, 10) : "",
        empresa_id: toSelect(empleado.empresa_id),
        sede_id: toSelect(empleado.sede_id),
        area_id: toSelect(empleado.area_id),
        cargo_id: toSelect(empleado.cargo_id),
      });
    } else {
      setForm(initialForm);
    }
  }, [empleado]);

  const sedesFiltradas = useMemo(() => {
    if (!form.empresa_id) return sedes;
    return sedes.filter((s) => Number(s.empresa_id) === Number(form.empresa_id));
  }, [sedes, form.empresa_id]);

  const areasFiltradas = useMemo(() => {
    return areas.filter((a) => {
      if (form.empresa_id && Number(a.empresa_id) !== Number(form.empresa_id)) return false;
      if (form.sede_id && Number(a.sede_id) !== Number(form.sede_id)) return false;
      return true;
    });
  }, [areas, form.empresa_id, form.sede_id]);

  const cargosFiltrados = useMemo(() => {
    return cargos.filter((c) => {
      if (form.empresa_id && Number(c.empresa_id) !== Number(form.empresa_id)) return false;
      if (form.sede_id && Number(c.sede_id) !== Number(form.sede_id)) return false;
      if (form.area_id && Number(c.area_id) !== Number(form.area_id)) return false;
      return true;
    });
  }, [cargos, form.empresa_id, form.sede_id, form.area_id]);

  const setField = (field, value) => {
    setForm((prev) => {
      const next = { ...prev, [field]: value };
      if (field === "empresa_id") {
        next.sede_id = "";
        next.area_id = "";
        next.cargo_id = "";
      }
      if (field === "sede_id") {
        next.area_id = "";
        next.cargo_id = "";
      }
      if (field === "area_id") {
        next.cargo_id = "";
      }
      return next;
    });
  };

  const submit = (event) => {
    event.preventDefault();
    if (!form.nombres.trim() || !form.apellidos.trim() || !form.documento.trim() || !form.empresa_id) {
      alert("Completa nombres, apellidos, documento y empresa.");
      return;
    }
    onSave({
      ...form,
      empresa_id: Number(form.empresa_id),
      sede_id: toIntOrNull(form.sede_id),
      area_id: toIntOrNull(form.area_id),
      cargo_id: toIntOrNull(form.cargo_id),
      correo: form.correo || null,
      fecha_nacimiento: form.fecha_nacimiento || null,
      fecha_ingreso: form.fecha_ingreso || null,
    });
  };

  return (
    <div className="emp-modal-backdrop">
      <form className="emp-form-modal" onSubmit={submit}>
        <header className="emp-modal-header">
          <div>
            <span>{empleado ? "Editar empleado" : "Nuevo empleado"}</span>
            <h2>{empleado ? nombreCompleto(empleado) : "Empleado SST Enterprise 360°"}</h2>
            <p>Información personal y laboral conectada con empresa, sede, área y cargo.</p>
          </div>
          <button type="button" className="emp-close" onClick={onClose}><X size={20} /></button>
        </header>

        <nav className="emp-tabs">
          <button type="button" className={tab === "personal" ? "active" : ""} onClick={() => setTab("personal")}>Personal</button>
          <button type="button" className={tab === "laboral" ? "active" : ""} onClick={() => setTab("laboral")}>Laboral</button>
          <button type="button" className={tab === "contacto" ? "active" : ""} onClick={() => setTab("contacto")}>Contacto</button>
          <button type="button" className={tab === "sst" ? "active" : ""} onClick={() => setTab("sst")}>SST 360°</button>
        </nav>

        <div className="emp-modal-body">
          {tab === "personal" && (
            <div className="emp-form-grid">
              <label>Nombres *<input value={form.nombres} onChange={(e) => setField("nombres", e.target.value)} /></label>
              <label>Apellidos *<input value={form.apellidos} onChange={(e) => setField("apellidos", e.target.value)} /></label>
              <label>Tipo documento<select value={form.tipo_documento} onChange={(e) => setField("tipo_documento", e.target.value)}><option>CC</option><option>CE</option><option>TI</option><option>PASAPORTE</option></select></label>
              <label>Documento *<input value={form.documento} onChange={(e) => setField("documento", e.target.value)} /></label>
              <label>Fecha nacimiento<input type="date" value={form.fecha_nacimiento} onChange={(e) => setField("fecha_nacimiento", e.target.value)} /></label>
              <label>Estado laboral<select value={form.estado_laboral} onChange={(e) => setField("estado_laboral", e.target.value)}><option>ACTIVO</option><option>INACTIVO</option><option>RETIRADO</option><option>SUSPENDIDO</option></select></label>
            </div>
          )}

          {tab === "laboral" && (
            <div className="emp-form-grid">
              <label>Empresa *<select value={form.empresa_id} onChange={(e) => setField("empresa_id", e.target.value)}><option value="">Seleccione empresa</option>{empresas.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select></label>
              <label>Sede<select value={form.sede_id} onChange={(e) => setField("sede_id", e.target.value)}><option value="">Sin sede</option>{sedesFiltradas.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select></label>
              <label>Área<select value={form.area_id} onChange={(e) => setField("area_id", e.target.value)}><option value="">Sin área</option>{areasFiltradas.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select></label>
              <label>Cargo<select value={form.cargo_id} onChange={(e) => setField("cargo_id", e.target.value)}><option value="">Sin cargo</option>{cargosFiltrados.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select></label>
              <label>Fecha ingreso<input type="date" value={form.fecha_ingreso} onChange={(e) => setField("fecha_ingreso", e.target.value)} /></label>
              <label>Tipo contrato<select value={form.tipo_contrato} onChange={(e) => setField("tipo_contrato", e.target.value)}><option>INDEFINIDO</option><option>FIJO</option><option>OBRA LABOR</option><option>PRESTACIÓN DE SERVICIOS</option><option>APRENDIZAJE</option><option>TEMPORAL</option></select></label>
            </div>
          )}

          {tab === "contacto" && (
            <div className="emp-form-grid">
              <label>Correo<input type="email" value={form.correo || ""} onChange={(e) => setField("correo", e.target.value)} /></label>
              <label>Teléfono<input value={form.telefono || ""} onChange={(e) => setField("telefono", e.target.value)} /></label>
            </div>
          )}

          {tab === "sst" && (
            <div className="emp-sst-summary">
              <article><CheckCircle2 size={20} /><b>Empresa</b><span>{buscarNombre(empresas, form.empresa_id, "Pendiente")}</span></article>
              <article><MapPin size={20} /><b>Sede</b><span>{buscarNombre(sedes, form.sede_id, "Pendiente")}</span></article>
              <article><Network size={20} /><b>Área</b><span>{buscarNombre(areas, form.area_id, "Pendiente")}</span></article>
              <article><BriefcaseBusiness size={20} /><b>Cargo</b><span>{buscarNombre(cargos, form.cargo_id, "Pendiente")}</span></article>
            </div>
          )}
        </div>

        <footer className="emp-modal-footer">
          <button type="button" className="emp-btn-light" onClick={onClose}>Cancelar</button>
          <button type="submit" className="emp-btn-primary">Guardar empleado</button>
        </footer>
      </form>
    </div>
  );
}


function clampPercent(value) {
  const n = Number(value || 0);
  if (Number.isNaN(n)) return 0;
  return Math.max(0, Math.min(100, Math.round(n)));
}

function statusLabel(count) {
  return Number(count || 0) > 0 ? "Revisar" : "Óptimo";
}

function AlertRow({ icon: Icon, label, value, tone = "blue" }) {
  const count = Number(value || 0);
  return (
    <div className={`emp-alert-row emp-alert-${tone}`}>
      <span className="emp-alert-icon"><Icon size={18} /></span>
      <b>{label}</b>
      <strong>{count}</strong>
      <em className={count > 0 ? "warn" : "ok"}>{statusLabel(count)}</em>
      <ChevronRight size={18} />
    </div>
  );
}

function DistributionRow({ icon: Icon, label, value, total, tone = "blue" }) {
  const pct = total > 0 ? clampPercent((Number(value || 0) / Number(total || 1)) * 100) : 0;
  return (
    <div className={`emp-dist-row emp-dist-${tone}`}>
      <span className="emp-dist-icon"><Icon size={18} /></span>
      <div className="emp-dist-main">
        <div><b>{label}</b><strong>{value || 0}</strong><em>{pct}%</em></div>
        <div className="emp-dist-track"><span style={{ width: `${pct}%` }} /></div>
      </div>
    </div>
  );
}

function RecommendationRow({ icon: Icon, title, text, tone = "blue" }) {
  return (
    <div className={`emp-rec-row emp-rec-${tone}`}>
      <span><Icon size={18} /></span>
      <div><b>{title}</b><small>{text}</small></div>
      <ChevronRight size={18} />
    </div>
  );
}

export default function EmpleadosSSTPage() {
  const [empleados, setEmpleados] = useState([]);
  const [dashboard, setDashboard] = useState(emptyDashboard);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [areas, setAreas] = useState([]);
  const [cargos, setCargos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalForm, setModalForm] = useState(null);
  const [modalDetalle, setModalDetalle] = useState(null);
  const [filters, setFilters] = useState({ q: "", empresa_id: "", sede_id: "", area_id: "", cargo_id: "", estado: "" });
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const relaciones = { empresas, sedes, areas, cargos };

  const params = useMemo(() => ({ ...filters }), [filters]);

  const cargarCatalogos = async () => {
    const [emp, sed, ar, car] = await Promise.all([
      listarEmpresasSST(),
      listarSedesSST(),
      listarAreasSST(),
      listarCargosSST(),
    ]);
    setEmpresas(normalizarLista(emp));
    setSedes(normalizarLista(sed));
    setAreas(normalizarLista(ar));
    setCargos(normalizarLista(car));
  };

  const cargarDatos = async () => {
    setLoading(true);
    try {
      const [lista, dash] = await Promise.all([listarEmpleados(params), dashboardEmpleados(params)]);
      setEmpleados(normalizarLista(lista));
      setDashboard({ ...emptyDashboard, ...(dash || {}), kpis: { ...emptyDashboard.kpis, ...(dash?.kpis || {}) }, charts: { ...emptyDashboard.charts, ...(dash?.charts || {}) }, alertas: { ...emptyDashboard.alertas, ...(dash?.alertas || {}) } });
    } catch (error) {
      console.error(error);
      alert(error?.response?.data?.detail || "No se pudo cargar empleados.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargarCatalogos(); }, []);
  useEffect(() => { cargarDatos(); }, [params]);

  const guardar = async (payload) => {
    try {
      if (modalForm?.id) await actualizarEmpleado(modalForm.id, payload);
      else await crearEmpleado(payload);
      setModalForm(null);
      await cargarDatos();
    } catch (error) {
      console.error(error);
      alert(error?.response?.data?.detail || "No se pudo guardar el empleado.");
    }
  };

  const desactivar = async (empleado) => {
    if (!window.confirm(`¿Deseas desactivar a ${nombreCompleto(empleado)}?`)) return;
    try {
      await eliminarEmpleado(empleado.id);
      await cargarDatos();
    } catch (error) {
      console.error(error);
      alert(error?.response?.data?.detail || "No se pudo desactivar el empleado.");
    }
  };

  const exportExcel = async () => {
    try { await exportarEmpleadosExcel(params); } catch (error) { console.error(error); alert("No se pudo exportar Excel."); }
  };

  const exportPdf = async () => {
    try { await exportarEmpleadosPdf(params); } catch (error) { console.error(error); alert("No se pudo exportar PDF."); }
  };

  const exportFicha = async (id) => {
    try { await exportarFichaEmpleadoPdf(id); } catch (error) { console.error(error); alert("No se pudo exportar la ficha PDF."); }
  };

  const limpiarFiltros = () => setFilters({ q: "", empresa_id: "", sede_id: "", area_id: "", cargo_id: "", estado: "" });

  const sedesFiltro = filters.empresa_id ? sedes.filter((s) => Number(s.empresa_id) === Number(filters.empresa_id)) : sedes;
  const areasFiltro = areas.filter((a) => (!filters.empresa_id || Number(a.empresa_id) === Number(filters.empresa_id)) && (!filters.sede_id || Number(a.sede_id) === Number(filters.sede_id)));
  const cargosFiltro = cargos.filter((c) => (!filters.empresa_id || Number(c.empresa_id) === Number(filters.empresa_id)) && (!filters.sede_id || Number(c.sede_id) === Number(filters.sede_id)) && (!filters.area_id || Number(c.area_id) === Number(filters.area_id)));

  const totalRows = empleados.length;
  const totalPages = Math.max(1, Math.ceil(totalRows / pageSize));
  const safePage = Math.min(currentPage, totalPages);
  const startIndex = (safePage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, totalRows);
  const empleadosPaginados = empleados.slice(startIndex, endIndex);
  const totalAlertas = Number(dashboard.alertas.sin_sede || 0) + Number(dashboard.alertas.sin_area || 0) + Number(dashboard.alertas.sin_cargo || 0) + Number(dashboard.alertas.sin_correo || 0);
  const completitud = clampPercent(dashboard.kpis.completitud_organizacional);
  const estructuraTotal = Math.max(1, Number(dashboard.kpis.total || 0));

  useEffect(() => { setCurrentPage(1); }, [filters.q, filters.empresa_id, filters.sede_id, filters.area_id, filters.cargo_id, filters.estado, pageSize]);

  return (
    <main className="empleados-sst-page">
      <section className="emp-hero">
        <div>
          <span>FASE 1.1.5.3.1 · Empleados SST Enterprise 360°</span>
          <h1>Empleados SST Enterprise 360°</h1>
          <p>Gestión inteligente de empleados por empresa, sede, área y cargo con trazabilidad organizacional para SG-SST.</p>
        </div>
        <div className="emp-hero-actions">
          <button onClick={cargarDatos} className="emp-btn-light"><RefreshCcw size={16} /> Actualizar</button>
          <button onClick={exportExcel} className="emp-btn-light"><FileSpreadsheet size={16} /> Excel</button>
          <button onClick={exportPdf} className="emp-btn-light"><FileText size={16} /> PDF</button>
          <button onClick={() => setModalForm({})} className="emp-btn-primary"><Plus size={16} /> Nuevo empleado</button>
        </div>
      </section>

      <section className="emp-main-grid">
        <div className="emp-content">
          <section className="emp-kpis-grid emp-kpis-primary">
            <KpiCard icon={Users} label="Total empleados" value={dashboard.kpis.total} />
            <KpiCard icon={CheckCircle2} label="Activos" value={dashboard.kpis.activos} tone="green" />
            <KpiCard icon={AlertTriangle} label="Inactivos" value={dashboard.kpis.inactivos} tone="red" />
            <KpiCard icon={Building2} label="Empresas" value={dashboard.kpis.empresas} tone="purple" />
            <KpiCard icon={BriefcaseBusiness} label="Sin cargo" value={dashboard.kpis.sin_cargo} tone="yellow" />
          </section>

          <section className="emp-charts-grid emp-charts-featured">
            <MiniBar title="Empleados por empresa" data={dashboard.charts.por_empresa} />
            <MiniBar title="Empleados por sede" data={dashboard.charts.por_sede} />
            <MiniBar title="Empleados por área" data={dashboard.charts.por_area} />
          </section>

          <section className="emp-table-card">
            <div className="emp-filter-top">
              <div className="emp-search"><Search size={16} /><input placeholder="Buscar por nombre, apellido, documento o correo..." value={filters.q} onChange={(e) => setFilters((p) => ({ ...p, q: e.target.value }))} /></div>
              <button onClick={limpiarFiltros} className="emp-btn-light"><X size={15} /> Limpiar</button>
              <button onClick={cargarDatos} className="emp-btn-light"><RefreshCcw size={15} /> Actualizar</button>
            </div>
            <div className="emp-filters-grid">
              <select value={filters.empresa_id} onChange={(e) => setFilters((p) => ({ ...p, empresa_id: e.target.value, sede_id: "", area_id: "", cargo_id: "" }))}><option value="">Todas las empresas</option>{empresas.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select>
              <select value={filters.sede_id} onChange={(e) => setFilters((p) => ({ ...p, sede_id: e.target.value, area_id: "", cargo_id: "" }))}><option value="">Todas las sedes</option>{sedesFiltro.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select>
              <select value={filters.area_id} onChange={(e) => setFilters((p) => ({ ...p, area_id: e.target.value, cargo_id: "" }))}><option value="">Todas las áreas</option>{areasFiltro.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select>
              <select value={filters.cargo_id} onChange={(e) => setFilters((p) => ({ ...p, cargo_id: e.target.value }))}><option value="">Todos los cargos</option>{cargosFiltro.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select>
              <select value={filters.estado} onChange={(e) => setFilters((p) => ({ ...p, estado: e.target.value }))}><option value="">Todos los estados</option><option>ACTIVO</option><option>INACTIVO</option><option>RETIRADO</option><option>SUSPENDIDO</option></select>
            </div>

            <div className="emp-table-wrap">
              <table>
                <thead><tr><th>Documento</th><th>Empleado</th><th>Empresa</th><th>Sede</th><th>Área</th><th>Cargo</th><th>Estado</th><th>Acciones</th></tr></thead>
                <tbody>
                  {loading && <tr><td colSpan="8" className="emp-empty">Cargando empleados...</td></tr>}
                  {!loading && empleados.length === 0 && <tr><td colSpan="8" className="emp-empty">No hay empleados para mostrar.</td></tr>}
                  {!loading && empleadosPaginados.map((empleado) => (
                    <tr key={empleado.id}>
                      <td><b>{empleado.documento}</b><small>{empleado.tipo_documento}</small></td>
                      <td><div className="emp-person"><span>{(empleado.nombres || "E").slice(0, 1)}{(empleado.apellidos || "").slice(0, 1)}</span><div><b>{nombreCompleto(empleado)}</b><small>{empleado.correo || "Sin correo"}</small></div></div></td>
                      <td>{empleado.empresa_nombre || buscarNombre(empresas, empleado.empresa_id, "Sin empresa")}</td>
                      <td>{empleado.sede_nombre || buscarNombre(sedes, empleado.sede_id, "Sin sede")}</td>
                      <td>{empleado.area_nombre || buscarNombre(areas, empleado.area_id, "Sin área")}</td>
                      <td>{empleado.cargo_nombre || buscarNombre(cargos, empleado.cargo_id, "Sin cargo")}</td>
                      <td><span className={`emp-status ${(empleado.estado_laboral || "").toLowerCase()}`}>{empleado.estado_laboral}</span></td>
                      <td><div className="emp-actions"><button title="Ver" onClick={() => setModalDetalle(empleado)}><Eye size={15} /></button><button title="Ficha PDF" onClick={() => exportFicha(empleado.id)}><Download size={15} /></button><button title="Editar" onClick={() => setModalForm(empleado)}><Edit3 size={15} /></button><button title="Desactivar" onClick={() => desactivar(empleado)}><Trash2 size={15} /></button></div></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="emp-pagination">
              <div className="emp-page-info">
                Mostrando <b>{totalRows === 0 ? 0 : startIndex + 1}</b> - <b>{endIndex}</b> de <b>{totalRows}</b> empleados
              </div>
              <div className="emp-page-controls">
                <label>Registros
                  <select value={pageSize} onChange={(e) => setPageSize(Number(e.target.value))}>
                    <option value={5}>5</option>
                    <option value={10}>10</option>
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                  </select>
                </label>
                <button disabled={safePage <= 1} onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}><ChevronLeft size={16} /></button>
                <span>Página {safePage} / {totalPages}</span>
                <button disabled={safePage >= totalPages} onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}><ChevronRight size={16} /></button>
              </div>
            </div>
          </section>
        </div>

        <aside className="emp-right-panel emp-right-panel-pro">
          <article className="emp-intel-card emp-intel-pro">
            <div className="emp-side-title-row">
              <h3>Dashboard inteligente</h3>
              <span className="emp-ai-badge">AI</span>
            </div>
            <div className="emp-intel-body">
              <div className="emp-ring emp-ring-pro" style={{ background: `conic-gradient(#2563eb 0 ${completitud}%, #dbeafe ${completitud}% 100%)` }}>
                <strong>{completitud}%</strong><span>Índice </span>
              </div>
              <div className="emp-intel-copy">
                <h4>{completitud >= 90 ? "Gestión estable y óptima" : "Gestión con pendientes"}</h4>
                <p>Trazabilidad completa en empleados, estructura organizacional y estado laboral.</p>
                <em className={completitud >= 90 ? "ok" : "warn"}><CheckCircle2 size={14} /> {completitud >= 90 ? "Excelente" : "Revisar"}</em>
              </div>
            </div>
            <div className="emp-intel-mini-stats">
              <div><Users size={17} /><span>Total</span><b>{dashboard.kpis.total}</b></div>
              <div><CheckCircle2 size={17} /><span>Activos</span><b>{dashboard.kpis.activos}</b></div>
              <div><Users size={17} /><span>Inactivos</span><b>{dashboard.kpis.inactivos}</b></div>
              <div><Building2 size={17} /><span>Empresas</span><b>{dashboard.kpis.empresas}</b></div>
            </div>
          </article>

          <article className="emp-side-card emp-alerts-pro">
            <div className="emp-side-title-row">
              <h3><AlertTriangle size={18} /> Alertas organizacionales</h3>
              <span className={totalAlertas > 0 ? "emp-alert-badge warn" : "emp-alert-badge"}>{totalAlertas} críticas</span>
            </div>
            <div className="emp-alert-list">
              <AlertRow icon={Building2} label="Sin sede" value={dashboard.alertas.sin_sede} tone="blue" />
              <AlertRow icon={Network} label="Sin área" value={dashboard.alertas.sin_area} tone="purple" />
              <AlertRow icon={BriefcaseBusiness} label="Sin cargo" value={dashboard.alertas.sin_cargo} tone="orange" />
              <AlertRow icon={Mail} label="Sin correo" value={dashboard.alertas.sin_correo} tone="red" />
            </div>
            <button type="button" className="emp-side-link">Ver todas las alertas <ChevronRight size={16} /></button>
          </article>

          <article className="emp-side-card emp-distribution-pro">
            <div className="emp-side-title-row">
              <h3><PieChart size={18} /> Distribución base</h3>
              <span className="emp-detail-badge"><BarChart3 size={15} /> Ver detalle</span>
            </div>
            <DistributionRow icon={Building2} label="Empresas" value={dashboard.kpis.empresas} total={Math.max(1, dashboard.kpis.empresas)} tone="blue" />
            <DistributionRow icon={MapPin} label="Sedes" value={sedes.length} total={Math.max(1, sedes.length)} tone="green" />
            <DistributionRow icon={Network} label="Áreas" value={areas.length} total={Math.max(1, areas.length)} tone="purple" />
            <DistributionRow icon={BriefcaseBusiness} label="Cargos" value={cargos.length} total={Math.max(1, cargos.length)} tone="orange" />
          </article>

          <article className="emp-side-card emp-recommendations-pro">
            <div className="emp-side-title-row">
              <h3><Activity size={18} /> Recomendaciones PRO</h3>
              <span className="emp-pro-badge">PRO</span>
            </div>
            <div className="emp-rec-list">
              <RecommendationRow icon={Target} title="Estructura completa" text={dashboard.kpis.estructura_completa >= estructuraTotal ? "La estructura organizacional está completa." : "Completa sede, área y cargo en cada empleado."} tone="blue" />
              <RecommendationRow icon={Mail} title="Correos SST" text="Mantén actualizados los correos para notificaciones." tone="purple" />
              <RecommendationRow icon={FileSpreadsheet} title="Exportación periódica" text="Exporta el listado para auditorías y reportes." tone="green" />
              <RecommendationRow icon={CalendarCheck} title="Revisión continua" text="Revisa y actualiza la información regularmente." tone="orange" />
            </div>
            <button type="button" className="emp-side-link emp-purple-link">Ver todas las recomendaciones <ChevronRight size={16} /></button>
          </article>
        </aside>
      </section>

      {modalForm !== null && <EmpleadoFormModal empleado={modalForm?.id ? modalForm : null} relaciones={relaciones} onClose={() => setModalForm(null)} onSave={guardar} />}
      {modalDetalle && <EmpleadoDetalleModal empleado={modalDetalle} relaciones={relaciones} onClose={() => setModalDetalle(null)} onPdf={exportFicha} />}
    </main>
  );
}
