
import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BadgeCheck,
  BriefcaseBusiness,
  Building2,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  Download,
  Edit3,
  Eye,
  FileText,
  Filter,
  GraduationCap,
  HardHat,
  HeartPulse,
  Layers3,
  LayoutDashboard,
  MapPin,
  Network,
  Plus,
  RefreshCcw,
  Search,
  ShieldCheck,
  Sidebar,
  Trash2,
  Users,
  X,
} from "lucide-react";

import {
  actualizarCargoSST,
  actualizarEppCargoSST,
  cambiarEstadoCargoSST,
  crearCargoSST,
  exportarCargosExcelSST,
  exportarCargosPdfSST,
  exportarFichaCargoPdfSST,
  listarAreasParaCargosSST,
  listarCargosSST,
  listarEmpresasParaCargosSST,
  listarSedesParaCargosSST,
  obtenerDashboardCargosSST,
  obtenerEppCargoSST,
} from "../../api/cargoSstApi";
import { listarCatalogoEPP } from "../../api/eppApi";


import useSmartDelete from "../../hooks/useSmartDelete";

import "../../styles/cargos-sst.css";

const ESTADO_INICIAL_FORM = {
  nombre: "",
  descripcion: "",
  codigo: "",
  tipo: "OPERATIVO",
  nivel_riesgo: "MEDIO",
  proceso: "",
  empresa_id: "",
  sede_id: "",
  area_id: "",
  empleados_asociados: 0,
  exposicion: "MEDIA",
  requiere_epp: false,
  requiere_examen_medico: false,
  requiere_capacitacion: false,
  funciones: "",
  competencias: "",
  riesgos_asociados: "",
  observaciones: "",
  activo: true,
  epp_ids: [],
};

const TIPOS_CARGO = ["DIRECTIVO", "ADMINISTRATIVO", "OPERATIVO", "ASISTENCIAL", "TECNICO", "CONTRATISTA"];
const RIESGOS = ["BAJO", "MEDIO", "ALTO", "CRITICO"];
const EXPOSICIONES = ["BAJA", "MEDIA", "ALTA", "CRITICA"];

const normalizar = (valor) => String(valor ?? "").trim();
const numeroSeguro = (valor) => Number(valor || 0);

function obtenerNombreEmpresa(cargo) {
  return cargo?.empresa_nombre || cargo?.empresa?.nombre || "Sin empresa";
}

function obtenerNombreSede(cargo) {
  return cargo?.sede_nombre || cargo?.sede?.nombre || "Sin sede";
}

function obtenerNombreArea(cargo) {
  return cargo?.area_nombre || cargo?.area?.nombre || "Sin área";
}

function nivelClase(valor) {
  const riesgo = normalizar(valor).toLowerCase().replace("í", "i");
  if (riesgo.includes("critic")) return "critico";
  if (riesgo.includes("alto")) return "alto";
  if (riesgo.includes("bajo")) return "bajo";
  return "medio";
}

function construirPayload(form) {
  return {
    empresa_id: Number(form.empresa_id),
    sede_id: form.sede_id ? Number(form.sede_id) : null,
    area_id: form.area_id ? Number(form.area_id) : null,
    nombre: form.nombre,
    descripcion: form.descripcion,
    codigo_cargo: form.codigo || form.codigo_cargo || null,
    tipo_cargo: form.tipo || form.tipo_cargo || "OPERATIVO",
    proceso_asociado: form.proceso || form.proceso_asociado || null,
    nivel_riesgo: form.nivel_riesgo || "MEDIO",
    exposicion: form.exposicion || null,
    requiere_epp: Boolean(form.requiere_epp),
    epp_requerido: form.epp_requerido || null,
    examenes_medicos: form.examenes_medicos || (form.requiere_examen_medico ? "Requiere examen médico ocupacional según exposición del cargo." : null),
    capacitaciones_requeridas: form.capacitaciones_requeridas || (form.requiere_capacitacion ? "Requiere capacitación SST de acuerdo con funciones y nivel de riesgo." : null),
    perfil_sst: form.perfil_sst || form.funciones || null,
    competencias: form.competencias || null,
    riesgos_asociados: form.riesgos_asociados || null,
    numero_empleados: Number(form.empleados_asociados || form.numero_empleados || 0),
    activo: Boolean(form.activo),
  };
}

function KpiCard({ icon: Icon, label, value, tone, onClick }) {
  return (
    <button className="cargo-kpi-card" onClick={onClick} type="button">
      <span className={`cargo-kpi-icon ${tone || "blue"}`}>
        <Icon size={22} />
      </span>
      <span>{label}</span>
      <strong>{value}</strong>
    </button>
  );
}

function MiniBar({ label, value, total }) {
  const pct = total ? Math.min(100, Math.round((value / total) * 100)) : 0;
  return (
    <div className="cargo-mini-bar">
      <div>
        <strong>{label}</strong>
        <span>{value}</span>
      </div>
      <div className="cargo-mini-track">
        <span style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function CargosSmartSidebar({ dashboard, onFiltrarCriticos, onActualizar, className = "", sidebarVisible, onToggleSidebar }) {
  const indice = numeroSeguro(dashboard?.indice_gestion);
  const estado = indice >= 80 ? "Gestión estable" : indice >= 55 ? "Gestión por mejorar" : "Gestión crítica";

  return (
    <aside className={`cargos-smart-sidebar ${className}`}>
      <section className="cargo-smart-card cargo-smart-principal">
        <div className="cargo-smart-header">
          <div>
            <span>Cargos SST</span>
            <h2>Dashboard inteligente de cargos</h2>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <button
              type="button"
              className="sidebar-toggle-btn"
              onClick={onToggleSidebar}
              title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
              style={{
                display: "grid",
                placeItems: "center",
                width: "36px",
                height: "36px",
                border: "none",
                borderRadius: "12px",
                cursor: "pointer",
                color: "var(--cargo-slate-700)",
                background: "var(--cargo-slate-100)",
                transition: "0.2s ease",
              }}
            >
              {sidebarVisible ? <Sidebar size={18} /> : <LayoutDashboard size={18} />}
            </button>
            <div className="cargo-smart-icon"><BriefcaseBusiness size={21} /></div>
          </div>
        </div>

        <div className="cargo-smart-score">
          <div className="cargo-score-ring" style={{ "--score": `${indice * 3.6}deg` }}>
            <strong>{indice}%</strong>
            <span>ÍNDICE</span>
          </div>
          <div>
            <b>{estado}</b>
            <p>Calculado con riesgos, codificación, áreas, exposición y requisitos SST del cargo.</p>
          </div>
        </div>

        <div className="cargo-smart-mini">
          <article><span>Total</span><strong>{dashboard?.total_cargos || 0}</strong></article>
          <article><span>Activos</span><strong>{dashboard?.activos || 0}</strong></article>
          <article><span>Críticos</span><strong>{dashboard?.riesgo_alto_critico || 0}</strong></article>
        </div>
      </section>

      <section className="cargo-smart-card">
        <h3><AlertTriangle size={16} /> Alertas SST</h3>
        <div className="cargo-alert-list">
          <button type="button" onClick={onFiltrarCriticos}>
            <span className="danger"><AlertTriangle size={17} /></span>
            <div><strong>{dashboard?.riesgo_alto_critico || 0} Riesgo alto/crítico</strong><p>Cargos que requieren priorización de controles.</p></div>
          </button>
          <button type="button">
            <span className="warning"><Network size={17} /></span>
            <div><strong>{dashboard?.sin_area || 0} Sin área</strong><p>Completar área mejora trazabilidad SG-SST.</p></div>
          </button>
          <button type="button">
            <span className="info"><FileText size={17} /></span>
            <div><strong>{dashboard?.sin_codigo || 0} Sin código</strong><p>Codificación recomendada para control documental.</p></div>
          </button>
        </div>
      </section>

      <section className="cargo-smart-card">
        <div className="form-section-title-cargos"><ShieldCheck size={16} /> Requisitos SST</div>
        <MiniBar label="Requieren EPP" value={dashboard?.requieren_epp || 0} total={dashboard?.total_cargos || 1} />
        <MiniBar label="Examen médico" value={dashboard?.requieren_examen_medico || 0} total={dashboard?.total_cargos || 1} />
        <MiniBar label="Capacitación" value={dashboard?.requieren_capacitacion || 0} total={dashboard?.total_cargos || 1} />
      </section>

      <section className="cargo-smart-card">
        <h3><ClipboardList size={16} /> Recomendaciones PRO</h3>
        <ul className="cargo-recommendations">
          {(dashboard?.recomendaciones || []).map((item, index) => (
            <li key={`${item}-${index}`}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="cargo-smart-card cargo-smart-actions">
        <button type="button" onClick={onActualizar}><RefreshCcw size={16} /> Actualizar analytics</button>
        <button type="button" onClick={onFiltrarCriticos}><ShieldCheck size={16} /> Ver críticos</button>
      </section>
    </aside>
  );
}

export default function CargosSSTPage() {
  const [cargos, setCargos] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [areas, setAreas] = useState([]);
  const [catalogoEpp, setCatalogoEpp] = useState([]);
  const [cargandoEpp, setCargandoEpp] = useState(false);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [modalAbierto, setModalAbierto] = useState(false);
  const [detalle, setDetalle] = useState(null);
  const [editando, setEditando] = useState(null);
  const [form, setForm] = useState(ESTADO_INICIAL_FORM);

  const [filtros, setFiltros] = useState({
    buscar: "",
    empresa_id: "",
    sede_id: "",
    area_id: "",
    estado: "",
    riesgo: "",
    tipo: "",
  });

  const [pagina, setPagina] = useState(1);
  const [porPagina, setPorPagina] = useState(10);
  const [sidebarVisible, setSidebarVisible] = useState(true);

  const cargarSelectores = async () => {
    const [empresasData, sedesData, areasData] = await Promise.all([
      listarEmpresasParaCargosSST(),
      listarSedesParaCargosSST(),
      listarAreasParaCargosSST(),
    ]);
    setEmpresas(empresasData);
    setSedes(sedesData);
    setAreas(areasData);
  };

  const cargarDatos = async () => {
    setLoading(true);
    setError("");
    try {
      const params = Object.fromEntries(Object.entries(filtros).filter(([, value]) => value !== ""));
      const [cargosData, dashboardData] = await Promise.all([
        listarCargosSST(params),
        obtenerDashboardCargosSST({
          empresa_id: filtros.empresa_id || undefined,
          sede_id: filtros.sede_id || undefined,
          area_id: filtros.area_id || undefined,
        }),
      ]);
      setCargos(cargosData);
      setDashboard(dashboardData);
      setPagina(1);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudo cargar el módulo de cargos SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarSelectores().catch((err) => console.error(err));
  }, []);

  useEffect(() => {
    cargarDatos();
  }, [filtros.empresa_id, filtros.sede_id, filtros.area_id, filtros.riesgo, filtros.tipo]);

  useEffect(() => {
    if (!modalAbierto || !form.empresa_id) {
      setCatalogoEpp([]);
      return undefined;
    }
    let vigente = true;
    setCargandoEpp(true);
    listarCatalogoEPP({ empresa_id: form.empresa_id, estado: "ACTIVO" })
      .then((items) => {
        if (vigente) setCatalogoEpp(items.filter((item) => item.activo !== false));
      })
      .catch((err) => {
        console.error(err);
        if (vigente) setError(err?.response?.data?.detail || "No se pudo cargar el catálogo EPP.");
      })
      .finally(() => {
        if (vigente) setCargandoEpp(false);
      });
    return () => {
      vigente = false;
    };
  }, [modalAbierto, form.empresa_id]);

  const cargosFiltrados = useMemo(() => {
    const texto = filtros.buscar.toLowerCase().trim();
    if (!texto) return cargos;
    return cargos.filter((cargo) =>
      [
        cargo.nombre,
        cargo.codigo || cargo.codigo_cargo,
        cargo.descripcion,
        cargo.proceso || cargo.proceso_asociado,
        obtenerNombreEmpresa(cargo),
        obtenerNombreSede(cargo),
        obtenerNombreArea(cargo),
      ]
        .join(" ")
        .toLowerCase()
        .includes(texto)
    );
  }, [cargos, filtros.buscar]);

  const totalPaginas = Math.max(1, Math.ceil(cargosFiltrados.length / porPagina));
  const inicio = (pagina - 1) * porPagina;
  const cargosPagina = cargosFiltrados.slice(inicio, inicio + porPagina);

  const abrirNuevo = () => {
    setEditando(null);
    setForm({ ...ESTADO_INICIAL_FORM, empresa_id: empresas[0]?.id || "" });
    setModalAbierto(true);
  };

  const abrirEditar = async (cargo) => {
    setEditando(cargo);
    setForm({
      ...ESTADO_INICIAL_FORM,
      ...cargo,
      empresa_id: cargo.empresa_id || "",
      sede_id: cargo.sede_id || "",
      area_id: cargo.area_id || "",
      codigo: cargo.codigo || cargo.codigo_cargo || "",
      tipo: cargo.tipo || cargo.tipo_cargo || "OPERATIVO",
      proceso: cargo.proceso || cargo.proceso_asociado || "",
      empleados_asociados: cargo.empleados_asociados ?? cargo.numero_empleados ?? 0,
      requiere_examen_medico: cargo.requiere_examen_medico ?? Boolean(cargo.examenes_medicos),
      requiere_capacitacion: cargo.requiere_capacitacion ?? Boolean(cargo.capacitaciones_requeridas),
      funciones: cargo.funciones || cargo.perfil_sst || "",
      epp_ids: [],
    });
    setModalAbierto(true);
    try {
      const asignacion = await obtenerEppCargoSST(cargo.id);
      setForm((prev) => ({
        ...prev,
        requiere_epp: asignacion.epp_ids.length > 0 || prev.requiere_epp,
        epp_ids: asignacion.epp_ids,
      }));
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudieron cargar los EPP requeridos del cargo.");
    }
  };

  const abrirDetalle = async (cargo) => {
    setDetalle({ ...cargo, epps: null });
    try {
      const asignacion = await obtenerEppCargoSST(cargo.id);
      setDetalle((actual) => actual?.id === cargo.id ? { ...actual, epps: asignacion.epps } : actual);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudieron cargar los EPP requeridos del cargo.");
    }
  };

  const cerrarModal = () => {
    setModalAbierto(false);
    setEditando(null);
    setForm(ESTADO_INICIAL_FORM);
  };

  const manejarCambio = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
      ...(name === "empresa_id" ? { sede_id: "", area_id: "", epp_ids: [] } : {}),
      ...(name === "requiere_epp" && !checked ? { epp_ids: [] } : {}),
    }));
  };

  const alternarEpp = (eppId) => {
    setForm((prev) => {
      const seleccionado = prev.epp_ids.includes(eppId);
      const eppIds = seleccionado
        ? prev.epp_ids.filter((id) => id !== eppId)
        : [...prev.epp_ids, eppId];
      return { ...prev, epp_ids: eppIds, requiere_epp: eppIds.length > 0 };
    });
  };

  const guardarCargo = async (e) => {
    e.preventDefault();
    setGuardando(true);
    setError("");
    setSuccess("");
    try {
      const payload = construirPayload(form);
      if (!payload.empresa_id) {
        setError("Selecciona la empresa del cargo.");
        return;
      }
      if (form.requiere_epp && form.epp_ids.length === 0) {
        setError("Selecciona al menos un EPP requerido para el cargo.");
        return;
      }
      let cargoGuardado;
      if (editando?.id) {
        cargoGuardado = await actualizarCargoSST(editando.id, payload);
        setSuccess("Cargo actualizado correctamente.");
      } else {
        cargoGuardado = await crearCargoSST(payload);
        setSuccess("Cargo creado correctamente.");
      }
      await actualizarEppCargoSST(cargoGuardado.id, form.epp_ids);
      cerrarModal();
      await cargarDatos();
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudo guardar el cargo.");
    } finally {
      setGuardando(false);
    }
  };

  const alternarEstado = async (cargo) => {
    try {
      await cambiarEstadoCargoSST(cargo.id, !cargo.activo);
      await cargarDatos();
    } catch (err) {
      setError(err?.response?.data?.detail || "No se pudo cambiar el estado.");
    }
  };

  
  const smartDelete = useSmartDelete({
    entidad: "cargo",
    etiquetaEntidad: "cargo",
    getNombre: (cargo) => cargo.nombre,
    onSuccess: async () => {
      setSuccess("Operación de eliminación inteligente ejecutada correctamente.");
      await cargarDatos();
    },
  });

  const limpiarFiltros = () => {
    setFiltros({ buscar: "", empresa_id: "", sede_id: "", area_id: "", estado: "", riesgo: "", tipo: "" });
  };

  const filtrarCriticos = () => {
    setFiltros((prev) => ({ ...prev, riesgo: "CRITICO" }));
  };

  const obtenerParamsExportacion = () => {
    const params = {
      empresa_id: filtros.empresa_id,
      sede_id: filtros.sede_id,
      area_id: filtros.area_id,
      riesgo: filtros.riesgo,
      tipo: filtros.tipo,
      q: filtros.buscar,
    };
    return Object.fromEntries(Object.entries(params).filter(([, value]) => value !== "" && value !== null && value !== undefined));
  };

  const exportarExcel = async () => {
    setError("");
    setSuccess("");
    try {
      await exportarCargosExcelSST(obtenerParamsExportacion());
      setSuccess("Excel de cargos generado correctamente.");
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudo exportar el Excel de cargos.");
    }
  };

  const exportarPdf = async () => {
    setError("");
    setSuccess("");
    try {
      await exportarCargosPdfSST(obtenerParamsExportacion());
      setSuccess("PDF general de cargos generado correctamente.");
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudo exportar el PDF de cargos.");
    }
  };

  const exportarFicha = async (cargo) => {
    setError("");
    setSuccess("");
    try {
      await exportarFichaCargoPdfSST(cargo.id, cargo.codigo || cargo.codigo_cargo || cargo.nombre);
      setSuccess("Ficha PDF del cargo generada correctamente.");
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudo exportar la ficha PDF del cargo.");
    }
  };

  return (
    <main className="cargos-sst-page">
      <section className="cargos-sst-hero">
        <div>
          <h1>Cargos SST 360°</h1>
          <p>
            Gestiona los cargos y consulta sus requisitos, personal y nivel de riesgo.
          </p>
        </div>
        <div className="cargos-hero-actions">
          <button className="btn-secondary-cargos" onClick={cargarDatos} disabled={loading} type="button">
            <RefreshCcw size={16} className={loading ? "spin-cargos" : ""} /> Actualizar
          </button>
          <button className="btn-secondary-cargos" onClick={exportarExcel} type="button">
            <Download size={16} /> Excel
          </button>
          <button className="btn-secondary-cargos" onClick={exportarPdf} type="button">
            <FileText size={16} /> PDF
          </button>
          <button className="btn-primary-cargos" onClick={abrirNuevo} type="button">
            <Plus size={17} /> Nuevo cargo
          </button>
        </div>
      </section>

      {error && <div className="cargos-alert error"><span>{error}</span><button onClick={() => setError("")}><X size={16} /></button></div>}
      {success && <div className="cargos-alert success"><span>{success}</span><button onClick={() => setSuccess("")}><X size={16} /></button></div>}

      <div className={`cargos-intelligent-layout ${!sidebarVisible ? "sidebar-collapsed" : ""}`}>
        <section className="cargos-intelligent-main">
          <section className="cargos-kpis">
            <KpiCard icon={BriefcaseBusiness} label="Total cargos" value={dashboard?.total_cargos || 0} tone="blue" onClick={() => setFiltros((p) => ({ ...p, estado: "" }))} />
            <KpiCard icon={CheckCircle2} label="Activos" value={dashboard?.activos || 0} tone="green" onClick={() => setFiltros((p) => ({ ...p, estado: "ACTIVO" }))} />
            <KpiCard icon={AlertTriangle} label="Alto / crítico" value={dashboard?.riesgo_alto_critico || 0} tone="red" onClick={filtrarCriticos} />
            <KpiCard icon={HardHat} label="Requieren EPP" value={dashboard?.requieren_epp || 0} tone="amber" onClick={() => {}} />
            <KpiCard icon={Users} label="Empleados" value={dashboard?.empleados_asociados || 0} tone="purple" onClick={() => {}} />
          </section>

          <section className="cargos-executive-grid">
            <article className="cargo-exec-card">
              <div className="exec-title"><span>Distribución SST</span><h3>Cargos por riesgo</h3></div>
              <div className="exec-bars-cargos">
                {(dashboard?.distribucion_riesgo || []).slice(0, 5).map((item) => (
                  <MiniBar key={item.nombre} label={item.nombre} value={item.total} total={dashboard?.total_cargos || 1} />
                ))}
              </div>
            </article>
            <article className="cargo-exec-card">
              <div className="exec-title"><span>Clasificación</span><h3>Cargos por tipo</h3></div>
              <div className="exec-bars-cargos">
                {(dashboard?.distribucion_tipo || []).slice(0, 5).map((item) => (
                  <MiniBar key={item.nombre} label={item.nombre} value={item.total} total={dashboard?.total_cargos || 1} />
                ))}
              </div>
            </article>
            <article className="cargo-exec-card">
              <div className="exec-title"><span>Organización</span><h3>Cargos por área</h3></div>
              <div className="exec-bars-cargos">
                {(dashboard?.cargos_por_area || []).slice(0, 5).map((item) => (
                  <MiniBar key={item.nombre} label={item.nombre} value={item.total} total={dashboard?.total_cargos || 1} />
                ))}
              </div>
            </article>
          </section>

          <section className="cargo-priority-panel">
            <div className="priority-header">
              <div><span>Cargos prioritarios</span><h2>{dashboard?.cargos_prioritarios?.[0]?.nombre || "Sin prioridad crítica"}</h2></div>
              <BadgeCheck size={22} />
            </div>
            <div className="priority-list-cargos">
              {(dashboard?.cargos_prioritarios || []).slice(0, 4).map((cargo) => (
                <article key={cargo.id}>
                  <span className={`riesgo-pill-cargos ${nivelClase(cargo.riesgo)}`}>{cargo.riesgo}</span>
                  <strong>{cargo.nombre}</strong>
                  <p>{cargo.area} · {cargo.empleados} empleados</p>
                </article>
              ))}
            </div>
          </section>

          <section className="cargos-sst-panel">
            <div className="cargos-toolbar">
              <label className="search-box-cargos">
                <Search size={17} />
                <input
                  value={filtros.buscar}
                  placeholder="Buscar por cargo, código, empresa, sede, área, proceso..."
                  onChange={(e) => setFiltros((prev) => ({ ...prev, buscar: e.target.value }))}
                />
              </label>
              <div className="toolbar-actions-cargos">
                <button className="btn-secondary-cargos" type="button" onClick={limpiarFiltros}><Filter size={16} /> Limpiar</button>
                <button className="btn-secondary-cargos" type="button" onClick={exportarExcel}><Download size={16} /> Excel</button>
                <button className="btn-secondary-cargos" type="button" onClick={exportarPdf}><FileText size={16} /> PDF</button>
                <button className="btn-secondary-cargos" type="button" onClick={cargarDatos}><RefreshCcw size={16} /> Actualizar</button>
                <button className="btn-secondary-cargos" type="button" onClick={() => setSidebarVisible(!sidebarVisible)} title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}>
                  {sidebarVisible ? <Sidebar size={16} /> : <LayoutDashboard size={16} />}
                </button>
              </div>
            </div>

            <div className="filters-grid-cargos">
              <label>Empresa
                <select value={filtros.empresa_id} onChange={(e) => setFiltros((p) => ({ ...p, empresa_id: e.target.value, sede_id: "", area_id: "" }))}>
                  <option value="">Todas</option>
                  {empresas.map((empresa) => <option key={empresa.id} value={empresa.id}>{empresa.nombre}</option>)}
                </select>
              </label>
              <label>Sede
                <select value={filtros.sede_id} onChange={(e) => setFiltros((p) => ({ ...p, sede_id: e.target.value }))}>
                  <option value="">Todas</option>
                  {sedes.filter((sede) => !filtros.empresa_id || Number(sede.empresa_id) === Number(filtros.empresa_id)).map((sede) => <option key={sede.id} value={sede.id}>{sede.nombre}</option>)}
                </select>
              </label>
              <label>Área
                <select value={filtros.area_id} onChange={(e) => setFiltros((p) => ({ ...p, area_id: e.target.value }))}>
                  <option value="">Todas</option>
                  {areas.filter((area) => !filtros.empresa_id || Number(area.empresa_id) === Number(filtros.empresa_id)).map((area) => <option key={area.id} value={area.id}>{area.nombre}</option>)}
                </select>
              </label>
              <label>Riesgo
                <select value={filtros.riesgo} onChange={(e) => setFiltros((p) => ({ ...p, riesgo: e.target.value }))}>
                  <option value="">Todos</option>
                  {RIESGOS.map((riesgo) => <option key={riesgo} value={riesgo}>{riesgo}</option>)}
                </select>
              </label>
              <label>Tipo
                <select value={filtros.tipo} onChange={(e) => setFiltros((p) => ({ ...p, tipo: e.target.value }))}>
                  <option value="">Todos</option>
                  {TIPOS_CARGO.map((tipo) => <option key={tipo} value={tipo}>{tipo}</option>)}
                </select>
              </label>
            </div>

            <div className="cargos-table-wrapper">
              <table className="cargos-table">
                <thead>
                  <tr>
                    <th>Empresa</th>
                    <th>Sede</th>
                    <th>Área</th>
                    <th>Código</th>
                    <th>Cargo</th>
                    <th>Tipo</th>
                    <th>Riesgo</th>
                    <th>Empl.</th>
                    <th>Requisitos SST</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr><td colSpan="11" className="empty-row-cargos"><RefreshCcw className="spin-cargos" size={16} /> Cargando cargos...</td></tr>
                  ) : cargosPagina.length === 0 ? (
                    <tr><td colSpan="11" className="empty-row-cargos"><BriefcaseBusiness size={16} /> No hay cargos para los filtros seleccionados.</td></tr>
                  ) : (
                    cargosPagina.map((cargo) => (
                      <tr key={cargo.id}>
                        <td><div className="cargo-org-cell"><Building2 size={16} /><div><strong>{obtenerNombreEmpresa(cargo)}</strong><span>ID {cargo.empresa_id}</span></div></div></td>
                        <td><div className="cargo-org-cell"><MapPin size={16} /><div><strong>{obtenerNombreSede(cargo)}</strong><span>{cargo.sede_id ? `ID ${cargo.sede_id}` : "Opcional"}</span></div></div></td>
                        <td><div className="cargo-org-cell"><Network size={16} /><div><strong>{obtenerNombreArea(cargo)}</strong><span>{cargo.area_id ? `ID ${cargo.area_id}` : "Pendiente"}</span></div></div></td>
                        <td><span className="codigo-pill-cargos">{cargo.codigo || cargo.codigo_cargo || "SIN-CÓDIGO"}</span></td>
                        <td><button type="button" className="cargo-name-button" onClick={() => abrirDetalle(cargo)}><span className="cargo-avatar"><BriefcaseBusiness size={17} /></span><div><strong>{cargo.nombre}</strong><span>{cargo.descripcion || "Sin descripción"}</span></div></button></td>
                        <td><span className="tipo-pill-cargos">{cargo.tipo || cargo.tipo_cargo || "OPERATIVO"}</span></td>
                        <td><span className={`riesgo-pill-cargos ${nivelClase(cargo.nivel_riesgo)}`}>{cargo.nivel_riesgo || "MEDIO"}</span></td>
                        <td><span className="empleados-pill-cargos"><Users size={14} /> {cargo.empleados_asociados ?? cargo.numero_empleados ?? 0}</span></td>
                        <td>
                          <div className="reqs-cargos">
                            {cargo.requiere_epp && <span><HardHat size={13} /> EPP</span>}
                            {cargo.requiere_examen_medico && <span><HeartPulse size={13} /> Médico</span>}
                            {cargo.requiere_capacitacion && <span><GraduationCap size={13} /> Capacitación</span>}
                            {!cargo.requiere_epp && !cargo.requiere_examen_medico && !cargo.requiere_capacitacion && <small>Sin requisitos</small>}
                          </div>
                        </td>
                        <td><button className={`status-pill-cargos ${cargo.activo ? "active" : "inactive"}`} type="button" onClick={() => alternarEstado(cargo)}>{cargo.activo ? "ACTIVO" : "INACTIVO"}</button></td>
                        <td>
                          <div className="table-actions-cargos">
                            <button className="icon-btn-cargos view" onClick={() => abrirDetalle(cargo)} title="Ver"><Eye size={16} /></button>
                            <button className="icon-btn-cargos view" onClick={() => exportarFicha(cargo)} title="Ficha PDF"><Download size={16} /></button>
                            <button className="icon-btn-cargos edit" onClick={() => abrirEditar(cargo)} title="Editar"><Edit3 size={16} /></button>
                            {/* FASE 37.2.2.A — Botón conectado al Framework Global de Eliminación Inteligente */}
                            <button
                              className="icon-btn-cargos delete"
                              onClick={() => smartDelete.open(cargo)}
                              title="Eliminación inteligente"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            <div className="pagination-cargos">
              <span>Mostrando {cargosPagina.length ? inicio + 1 : 0} - {Math.min(inicio + porPagina, cargosFiltrados.length)} de {cargosFiltrados.length} cargos</span>
              <div>
                <label>Registros
                  <select value={porPagina} onChange={(e) => { setPorPagina(Number(e.target.value)); setPagina(1); }}>
                    <option value={10}>10</option>
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                  </select>
                </label>
                <button disabled={pagina <= 1} onClick={() => setPagina((p) => p - 1)}><ChevronLeft size={16} /></button>
                <span>Página {pagina} / {totalPaginas}</span>
                <button disabled={pagina >= totalPaginas} onClick={() => setPagina((p) => p + 1)}><ChevronRight size={16} /></button>
              </div>
            </div>
          </section>
        </section>

        <CargosSmartSidebar
          dashboard={dashboard}
          onFiltrarCriticos={filtrarCriticos}
          onActualizar={cargarDatos}
          className={sidebarVisible ? "" : "sidebar-hidden"}
          sidebarVisible={sidebarVisible}
          onToggleSidebar={() => setSidebarVisible(!sidebarVisible)}
        />
      </div>

      {modalAbierto && (
        <div className="modal-backdrop-cargos">
          <section className="modal-card-cargos enterprise-modal-cargos">
            <header className="modal-header-cargos modal-header-gradient-cargos">
              <div className="modal-title-cargos">
                <span className="modal-title-icon-cargos"><BriefcaseBusiness size={22} /></span>
                <div>
                  <span className="modal-eyebrow-cargos">Exportación PDF / Excel</span>
                  <h2>{editando ? "Editar cargo SST" : "Nuevo cargo SST"}</h2>
                  <p>Caracterización organizacional del cargo, riesgos, exposición y requisitos SST.</p>
                </div>
              </div>
              <button className="modal-close-cargos" onClick={cerrarModal} type="button"><X size={18} /></button>
            </header>
            <form className="cargo-form" onSubmit={guardarCargo}>
              <div className="form-section-title-cargos"><Layers3 size={16} /> Información organizacional</div>
              <div className="form-grid-cargos">
                <label>Empresa *
                  <select name="empresa_id" value={form.empresa_id} onChange={manejarCambio} required>
                    <option value="">Seleccionar</option>
                    {empresas.map((empresa) => <option key={empresa.id} value={empresa.id}>{empresa.nombre}</option>)}
                  </select>
                </label>
                <label>Sede
                  <select name="sede_id" value={form.sede_id || ""} onChange={manejarCambio}>
                    <option value="">Opcional</option>
                    {sedes.filter((sede) => !form.empresa_id || Number(sede.empresa_id) === Number(form.empresa_id)).map((sede) => <option key={sede.id} value={sede.id}>{sede.nombre}</option>)}
                  </select>
                </label>
                <label>Área
                  <select name="area_id" value={form.area_id || ""} onChange={manejarCambio}>
                    <option value="">Opcional</option>
                    {areas.filter((area) => !form.empresa_id || Number(area.empresa_id) === Number(form.empresa_id)).map((area) => <option key={area.id} value={area.id}>{area.nombre}</option>)}
                  </select>
                </label>
              </div>

              <div className="form-section-title-cargos"><BriefcaseBusiness size={16} /> Perfil del cargo</div>
              <div className="form-grid-cargos">
                <label>Nombre del cargo *<input name="nombre" value={form.nombre} onChange={manejarCambio} required /></label>
                <label>Código<input name="codigo" value={form.codigo || ""} onChange={manejarCambio} placeholder="Ej: CARGO-001" /></label>
                <label>Tipo
                  <select name="tipo" value={form.tipo || "OPERATIVO"} onChange={manejarCambio}>{TIPOS_CARGO.map((tipo) => <option key={tipo}>{tipo}</option>)}</select>
                </label>
                <label>Nivel de riesgo
                  <select name="nivel_riesgo" value={form.nivel_riesgo || "MEDIO"} onChange={manejarCambio}>{RIESGOS.map((riesgo) => <option key={riesgo}>{riesgo}</option>)}</select>
                </label>
                <label>Exposición
                  <select name="exposicion" value={form.exposicion || "MEDIA"} onChange={manejarCambio}>{EXPOSICIONES.map((expo) => <option key={expo}>{expo}</option>)}</select>
                </label>
                <label>Empleados asociados<input type="number" min="0" name="empleados_asociados" value={form.empleados_asociados || 0} onChange={manejarCambio} /></label>
                <label className="form-full-cargos">Proceso<input name="proceso" value={form.proceso || ""} onChange={manejarCambio} placeholder="Proceso asociado al cargo" /></label>
                <label className="form-full-cargos">Descripción<input name="descripcion" value={form.descripcion || ""} onChange={manejarCambio} /></label>
              </div>

              <div className="form-section-title-cargos"><ShieldCheck size={16} /> Requisitos SST</div>
              <div className="switch-grid-cargos">
                <label><input type="checkbox" name="requiere_epp" checked={!!form.requiere_epp} onChange={manejarCambio} /> Requiere EPP</label>
                <label><input type="checkbox" name="requiere_examen_medico" checked={!!form.requiere_examen_medico} onChange={manejarCambio} /> Examen médico</label>
                <label><input type="checkbox" name="requiere_capacitacion" checked={!!form.requiere_capacitacion} onChange={manejarCambio} /> Capacitación</label>
                <label><input type="checkbox" name="activo" checked={!!form.activo} onChange={manejarCambio} /> Cargo activo</label>
              </div>

              {form.requiere_epp && (
                <div className="cargo-epp-selector">
                  <div className="cargo-epp-selector-header">
                    <div>
                      <strong>EPP obligatorios del catálogo</strong>
                      <span>{form.epp_ids.length} seleccionados</span>
                    </div>
                    <HardHat size={20} />
                  </div>
                  {cargandoEpp ? (
                    <p className="cargo-epp-empty"><RefreshCcw className="spin-cargos" size={15} /> Cargando catálogo...</p>
                  ) : catalogoEpp.length === 0 ? (
                    <p className="cargo-epp-empty">La empresa no tiene EPP activos en el catálogo.</p>
                  ) : (
                    <div className="cargo-epp-options">
                      {catalogoEpp.map((epp) => (
                        <label key={epp.id} className={form.epp_ids.includes(epp.id) ? "selected" : ""}>
                          <input
                            type="checkbox"
                            checked={form.epp_ids.includes(epp.id)}
                            onChange={() => alternarEpp(epp.id)}
                          />
                          <span><strong>{epp.nombre}</strong><small>{epp.codigo} · {epp.categoria || "Sin categoría"}</small></span>
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              )}

              <div className="form-section-title-cargos"><ClipboardList size={16} /> Detalle SST</div>
              <div className="form-grid-cargos">
                <label className="form-full-cargos">Funciones<textarea name="funciones" value={form.funciones || ""} onChange={manejarCambio} rows={3} /></label>
                <label className="form-full-cargos">Competencias<textarea name="competencias" value={form.competencias || ""} onChange={manejarCambio} rows={3} /></label>
                <label className="form-full-cargos">Riesgos asociados<textarea name="riesgos_asociados" value={form.riesgos_asociados || ""} onChange={manejarCambio} rows={3} /></label>
                <label className="form-full-cargos">Observaciones<textarea name="observaciones" value={form.observaciones || ""} onChange={manejarCambio} rows={3} /></label>
              </div>

              <footer className="modal-actions-cargos sticky-actions-cargos">
                <button className="btn-secondary-cargos" type="button" onClick={cerrarModal}>Cancelar</button>
                <button className="btn-primary-cargos" disabled={guardando} type="submit">{guardando ? "Guardando..." : "Guardar cargo"}</button>
              </footer>
            </form>
          </section>
        </div>
      )}

      {detalle && (
        <div className="modal-backdrop-cargos">
          <section className="modal-card-cargos detail-modal-cargos">
            <header className="modal-header-cargos detail-header-cargos modal-header-gradient-cargos">
              <div className="detail-title-cargos"><span className="cargo-avatar large"><BriefcaseBusiness size={26} /></span><div><h2>{detalle.nombre}</h2><p>{obtenerNombreEmpresa(detalle)} · {obtenerNombreSede(detalle)} · {obtenerNombreArea(detalle)}</p></div></div>
              <button className="modal-close-cargos" onClick={() => setDetalle(null)}><X size={18} /></button>
            </header>
            <div className="detail-grid-cargos">
              <article><span>Código</span><strong>{detalle.codigo || detalle.codigo_cargo || "Sin código"}</strong></article>
              <article><span>Tipo</span><strong>{detalle.tipo || detalle.tipo_cargo || "OPERATIVO"}</strong></article>
              <article><span>Riesgo</span><strong>{detalle.nivel_riesgo || "MEDIO"}</strong></article>
              <article><span>Empleados</span><strong>{detalle.empleados_asociados ?? detalle.numero_empleados ?? 0}</strong></article>
              <article><span>Exposición</span><strong>{detalle.exposicion || "MEDIA"}</strong></article>
              <article><span>Estado</span><strong>{detalle.activo ? "ACTIVO" : "INACTIVO"}</strong></article>
              <article className="wide"><span>EPP requeridos</span><strong>{detalle.epps === null ? "Cargando catálogo..." : detalle.epps?.map((epp) => epp.nombre).join(", ") || "Sin EPP requeridos"}</strong></article>
              <article className="wide"><span>Funciones</span><strong>{detalle.funciones || "Sin funciones registradas"}</strong></article>
              <article className="wide"><span>Riesgos asociados</span><strong>{detalle.riesgos_asociados || "Sin riesgos asociados"}</strong></article>
              <article className="wide"><span>Observaciones</span><strong>{detalle.observaciones || "Sin observaciones"}</strong></article>
            </div>
            <footer className="modal-actions-cargos">
              <button className="btn-secondary-cargos" onClick={() => setDetalle(null)}>Cerrar</button>
              <button className="btn-primary-cargos" onClick={() => { setDetalle(null); abrirEditar(detalle); }}>Editar</button>
            </footer>
          </section>
        </div>
      )}

      
      {smartDelete.modal}
    </main>
  );
}
