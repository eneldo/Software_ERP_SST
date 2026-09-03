// ============================================================
// ÁREAS SST ENTERPRISE 360°
// Archivo: frontend/src/pages/organizacion/AreasSSTPage.jsx
// FASE 1.1.3.4 — Histórico SST por Área
// ============================================================

import { useEffect, useMemo, useState } from "react";
import useSmartDelete from "../../hooks/useSmartDelete";

import {
  Activity,
  AlertCircle,
  BarChart3,
  Building2,
  CalendarDays,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  ClipboardList,
  Download,
  Edit3,
  Eye,
  FileText,
  Filter,
  Gauge,
  History,
  Layers3,
  Loader2,
  LayoutDashboard,
  MapPin,
  Network,
  Plus,
  Printer,
  RefreshCw,
  Route,
  Save,
  Search,
  ShieldAlert,
  ShieldCheck,
  Sidebar,
  Sparkles,
  Target,
  Trash2,
  TrendingUp,
  Users,
  X,
} from "lucide-react";

import {
  actualizarAreaSST,
  cambiarEstadoAreaSST,
  crearAreaSST,
  listarAreasSST,
  listarEmpresasParaAreasSST,
  listarSedesParaAreasSST,
  obtenerDashboardAreasSST,
  listarHistorialAreaSST,
  crearHistorialAreaSST,
  eliminarHistorialAreaSST,
  exportarAreasSSTExcel,
  exportarAreasSSTPDF,
} from "../../api/areaSstApi";

import "../../styles/areas-sst.css";

const FORM_INICIAL = {
  empresa_id: "",
  sede_id: "",
  nombre: "",
  codigo_area: "",
  descripcion: "",
  tipo_area: "OPERATIVA",
  nivel_riesgo: "MEDIO",
  proceso_asociado: "",
  responsable_area: "",
  cargo_responsable: "",
  correo_responsable: "",
  telefono_responsable: "",
  numero_empleados: 0,
  activo: true,
};

const TIPOS_AREA = [
  "ADMINISTRATIVA",
  "OPERATIVA",
  "ASISTENCIAL",
  "LOGÍSTICA",
  "MANTENIMIENTO",
  "ALMACÉN",
  "SERVICIOS GENERALES",
];

const NIVELES_RIESGO = ["BAJO", "MEDIO", "ALTO", "CRÍTICO"];
const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

const HISTORIAL_FORM_INICIAL = {
  tipo_evento: "INSPECCIÓN SST",
  titulo: "",
  descripcion: "",
  impacto_sst: "MEDIO",
  estado_resultante: "REGISTRADO",
  responsable: "",
  evidencia_url: "",
  fecha_evento: "",
};

const TIPOS_EVENTO_HISTORIAL = [
  "INSPECCIÓN SST",
  "HALLAZGO",
  "PLAN DE MEJORA",
  "CAPACITACIÓN",
  "AUDITORÍA",
  "CAMBIO RESPONSABLE",
  "ACTUALIZACIÓN RIESGO",
  "OBSERVACIÓN",
];

const ESTADOS_HISTORIAL = ["REGISTRADO", "EN SEGUIMIENTO", "CERRADO", "FINALIZADO"];

function normalizarTexto(valor) {
  return String(valor ?? "").trim();
}

function estadoTexto(activo) {
  return activo ? "ACTIVA" : "INACTIVA";
}

function formatoFecha(fecha) {
  if (!fecha) return "—";
  try {
    return new Intl.DateTimeFormat("es-CO", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).format(new Date(fecha));
  } catch {
    return "—";
  }
}

function formatoFechaHora(fecha) {
  if (!fecha) return "—";
  try {
    return new Intl.DateTimeFormat("es-CO", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(fecha));
  } catch {
    return "—";
  }
}

function inicialesArea(nombre) {
  const limpio = normalizarTexto(nombre);
  if (!limpio) return "AR";

  return limpio
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0])
    .join("")
    .toUpperCase();
}

function descargarCSV(nombreArchivo, filas) {
  const contenido = filas
    .map((fila) =>
      fila
        .map((campo) => {
          const texto = String(campo ?? "").replaceAll('"', '""');
          return `"${texto}"`;
        })
        .join(";")
    )
    .join("\n");

  const blob = new Blob(["\ufeff" + contenido], {
    type: "text/csv;charset=utf-8;",
  });

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = nombreArchivo;
  link.click();
  URL.revokeObjectURL(url);
}

function agruparPorCampo(lista, campo, fallback = "Sin clasificar") {
  return lista.reduce((acc, item) => {
    const clave = normalizarTexto(item[campo]) || fallback;
    acc[clave] = (acc[clave] || 0) + 1;
    return acc;
  }, {});
}

function agruparEmpleadosPorCampo(lista, campo, fallback = "Sin clasificar") {
  return lista.reduce((acc, item) => {
    const clave = normalizarTexto(item[campo]) || fallback;
    acc[clave] = (acc[clave] || 0) + Number(item.numero_empleados || 0);
    return acc;
  }, {});
}

function convertirDistribucion(objeto) {
  return Object.entries(objeto || {})
    .map(([label, value]) => ({ label, value: Number(value || 0) }))
    .sort((a, b) => b.value - a.value);
}

function maximoValor(lista) {
  return Math.max(1, ...lista.map((item) => Number(item.value || 0)));
}

function porcentaje(valor, total) {
  if (!total) return 0;
  return Math.round((Number(valor || 0) / Number(total || 1)) * 100);
}

function MiniBarChart({ titulo, subtitulo, data, icon: Icon }) {
  const max = maximoValor(data);

  return (
    <article className="areas-exec-card">
      <div className="exec-card-header">
        <div>
          <span>{subtitulo}</span>
          <h3>{titulo}</h3>
        </div>
        <div className="exec-card-icon">
          <Icon size={20} />
        </div>
      </div>

      <div className="exec-bars">
        {data.length === 0 ? (
          <div className="exec-empty">Sin datos disponibles</div>
        ) : (
          data.slice(0, 7).map((item) => (
            <div className="exec-bar-row" key={item.label}>
              <div className="exec-bar-meta">
                <strong>{item.label}</strong>
                <span>{item.value}</span>
              </div>
              <div className="exec-bar-track">
                <div
                  className="exec-bar-fill"
                  style={{ width: `${Math.max(7, (item.value / max) * 100)}%` }}
                />
              </div>
            </div>
          ))
        )}
      </div>
    </article>
  );
}

function DonutEstado({ activas, inactivas }) {
  const total = Number(activas || 0) + Number(inactivas || 0);
  const pctActivas = porcentaje(activas, total);

  return (
    <article className="areas-exec-card donut-card">
      <div className="exec-card-header">
        <div>
          <span>Control operativo</span>
          <h3>Estado de áreas</h3>
        </div>
        <div className="exec-card-icon green">
          <Gauge size={20} />
        </div>
      </div>

      <div className="donut-layout">
        <div
          className="donut"
          style={{
            background: `conic-gradient(#16a34a 0 ${pctActivas}%, #ef4444 ${pctActivas}% 100%)`,
          }}
        >
          <div className="donut-center">
            <strong>{pctActivas}%</strong>
            <span>activas</span>
          </div>
        </div>

        <div className="donut-legend">
          <div>
            <span className="legend-dot green" />
            Activas <strong>{activas}</strong>
          </div>
          <div>
            <span className="legend-dot red" />
            Inactivas <strong>{inactivas}</strong>
          </div>
          <div>
            <span className="legend-dot blue" />
            Total <strong>{total}</strong>
          </div>
        </div>
      </div>
    </article>
  );
}

function riesgoClass(nivel) {
  const limpio = normalizarTexto(nivel).toUpperCase();
  if (limpio === "BAJO") return "bajo";
  if (limpio === "MEDIO") return "medio";
  if (limpio === "ALTO") return "alto";
  if (limpio === "CRÍTICO" || limpio === "CRITICO") return "critico";
  return "medio";
}

function AnalyticsAreaPanel({ area, promedioEmpleados, totalEmpleados, onVerHistorial }) {
  if (!area) {
    return (
      <section className="analytics-empty-panel">
        <div className="analytics-empty-icon">
          <Activity size={24} />
        </div>
        <div>
          <h3>Selecciona un área para ver Analytics PRO</h3>
          <p>
            Usa el botón “Analytics” de la tabla para abrir una ficha ejecutiva
            del área con indicadores, accesos rápidos y lectura gerencial.
          </p>
        </div>
      </section>
    );
  }

  const empleados = Number(area.numero_empleados || 0);
  const pesoPoblacional = porcentaje(empleados, totalEmpleados);
  const saludOperativa = area.activo ? 100 : 0;
  const criticidad =
    area.nivel_riesgo === "CRÍTICO" || area.nivel_riesgo === "ALTO"
      ? "Requiere seguimiento SST prioritario"
      : empleados >= promedioEmpleados
      ? "Carga poblacional relevante"
      : "Seguimiento estándar";

  return (
    <section className="analytics-area-panel">
      <div className="analytics-area-header">
        <div className="area-avatar analytics-avatar">
          {inicialesArea(area.nombre)}
        </div>

        <div>
          <span>Dashboard individual de área</span>
          <h2>{area.nombre}</h2>
          <p>
            {area.empresa_nombre || "Sin empresa"} ·{" "}
            {area.sede_nombre || "Sin sede"} · {area.codigo_area || "Sin código"}
          </p>
        </div>
      </div>

      <div className="analytics-area-grid">
        <article>
          <span>Estado operativo</span>
          <strong>{estadoTexto(area.activo)}</strong>
          <div className="analytics-meter">
            <div style={{ width: `${saludOperativa}%` }} />
          </div>
        </article>

        <article>
          <span>Peso poblacional</span>
          <strong>{pesoPoblacional}%</strong>
          <div className="analytics-meter purple">
            <div style={{ width: `${pesoPoblacional}%` }} />
          </div>
        </article>

        <article>
          <span>Nivel de riesgo</span>
          <strong>{area.nivel_riesgo || "MEDIO"}</strong>
          <p>{criticidad}</p>
        </article>

        <article>
          <span>Proceso asociado</span>
          <strong>{area.proceso_asociado || "Sin proceso"}</strong>
          <p>{area.responsable_area || "Sin responsable asignado"}</p>
        </article>
      </div>

      <div className="quick-actions-areas">
        <button type="button">
          <Users size={17} />
          Ver Empleados
        </button>
        <button type="button">
          <Layers3 size={17} />
          Ver Cargos
        </button>
        <button type="button">
          <ShieldAlert size={17} />
          Riesgos
        </button>
        <button type="button">
          <ClipboardList size={17} />
          Plan Anual
        </button>
        <button type="button" onClick={() => onVerHistorial?.(area)}>
          <History size={17} />
          Histórico SST
        </button>
        <button type="button">
          <FileText size={17} />
          Documentos
        </button>
      </div>
    </section>
  );
}


function DashboardLateralInteligente({
  areas,
  areasFiltradas,
  totalEmpleados,
  promedioEmpleados,
  areaAnalytics,
  setFiltroEstado,
  setFiltroRiesgo,
  setBusqueda,
  setAreaAnalytics,
  cargarDatos,
  cargando,
  className = "",
  sidebarVisible,
  onToggleSidebar,
}) {
  const total = areasFiltradas.length;
  const activas = areasFiltradas.filter((area) => area.activo).length;
  const inactivas = Math.max(0, total - activas);
  const riesgoAlto = areasFiltradas.filter((area) =>
    ["ALTO", "CRÍTICO", "CRITICO"].includes(
      normalizarTexto(area.nivel_riesgo).toUpperCase()
    )
  ).length;
  const sinResponsable = areasFiltradas.filter(
    (area) => !normalizarTexto(area.responsable_area)
  ).length;
  const sinProceso = areasFiltradas.filter(
    (area) => !normalizarTexto(area.proceso_asociado)
  ).length;
  const sinCodigo = areasFiltradas.filter(
    (area) => !normalizarTexto(area.codigo_area)
  ).length;

  const saludBase = total === 0 ? 0 : Math.round((activas / total) * 100);
  const penalizacion = Math.min(
    35,
    riesgoAlto * 6 + sinResponsable * 4 + sinProceso * 3 + sinCodigo * 2
  );
  const indiceGestion = Math.max(0, Math.min(100, saludBase - penalizacion + 15));

  const areaCritica = [...areasFiltradas].sort((a, b) => {
    const peso = { "CRÍTICO": 4, CRITICO: 4, ALTO: 3, MEDIO: 2, BAJO: 1 };
    const riesgoB = peso[normalizarTexto(b.nivel_riesgo).toUpperCase()] || 0;
    const riesgoA = peso[normalizarTexto(a.nivel_riesgo).toUpperCase()] || 0;
    if (riesgoB !== riesgoA) return riesgoB - riesgoA;
    return Number(b.numero_empleados || 0) - Number(a.numero_empleados || 0);
  })[0];

  const alertas = [
    {
      id: "riesgo",
      titulo: "Riesgo alto/crítico",
      valor: riesgoAlto,
      detalle: "Áreas que requieren priorización SST.",
      accion: () => setFiltroRiesgo("ALTO"),
      icon: ShieldAlert,
      tipo: "danger",
    },
    {
      id: "responsable",
      titulo: "Sin responsable",
      valor: sinResponsable,
      detalle: "Completar responsable del área mejora trazabilidad.",
      accion: () => setBusqueda("sin responsable"),
      icon: Users,
      tipo: "warning",
    },
    {
      id: "proceso",
      titulo: "Sin proceso",
      valor: sinProceso,
      detalle: "Relacionar proceso facilita matriz de peligros y planes.",
      accion: () => setBusqueda("sin proceso"),
      icon: Route,
      tipo: "info",
    },
  ];

  const recomendaciones = [
    riesgoAlto > 0
      ? "Priorizar inspección y plan de intervención para áreas ALTO/CRÍTICO."
      : "Mantener seguimiento preventivo; no hay áreas críticas visibles.",
    sinResponsable > 0
      ? "Asignar responsable SST/operativo a las áreas pendientes."
      : "La trazabilidad de responsables se encuentra completa en los filtros actuales.",
    promedioEmpleados > 0
      ? `Promedio actual: ${promedioEmpleados} empleados por área. Validar carga poblacional.`
      : "Registrar empleados por área para fortalecer indicadores SST.",
  ];

  return (
    <aside className={`areas-smart-sidebar ${className}`} aria-label="Dashboard lateral inteligente de áreas SST">
      <div className="smart-sidebar-card smart-principal">
        <div className="smart-sidebar-header">
          <div>
            <span></span>
            <h2>Dashboard lateral inteligente</h2>
          </div>
          <div className="areas-sidebar-header-actions">
            <button
              type="button"
              className="areas-sidebar-toggle-btn"
              onClick={onToggleSidebar}
              title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
              aria-label={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
              aria-pressed={!sidebarVisible}
            >
              {sidebarVisible ? <Sidebar size={18} /> : <LayoutDashboard size={18} />}
            </button>
            <div className="smart-icon-main">
              <Sparkles size={20} />
            </div>
          </div>
        </div>

        <div className="smart-score-wrap">
          <div
            className="smart-score-ring"
            style={{ "--score": `${indiceGestion * 3.6}deg` }}
          >
            <strong>{indiceGestion}%</strong>
            <span>Índice</span>
          </div>
          <div className="smart-score-text">
            <strong>{indiceGestion >= 80 ? "Gestión estable" : indiceGestion >= 55 ? "Gestión en control" : "Requiere acción"}</strong>
            <p>
              Calculado con estado, riesgo, responsables, procesos y codificación de áreas.
            </p>
          </div>
        </div>

        <div className="smart-mini-kpis">
          <button type="button" onClick={() => setFiltroEstado("")}>
            <span>Total</span>
            <strong>{total}</strong>
          </button>
          <button type="button" onClick={() => setFiltroEstado("true")}>
            <span>Activas</span>
            <strong>{activas}</strong>
          </button>
          <button type="button" onClick={() => setFiltroEstado("false")}>
            <span>Inactivas</span>
            <strong>{inactivas}</strong>
          </button>
        </div>
      </div>

      <div className="smart-sidebar-card">
        <div className="smart-section-title">
          <Gauge size={17} />
          <span>Alertas inteligentes</span>
        </div>

        <div className="smart-alert-list">
          {alertas.map((alerta) => {
            const Icon = alerta.icon;
            return (
              <button
                key={alerta.id}
                type="button"
                className={`smart-alert-item ${alerta.tipo}`}
                onClick={alerta.accion}
              >
                <div className="smart-alert-icon">
                  <Icon size={16} />
                </div>
                <div>
                  <strong>{alerta.valor}</strong>
                  <span>{alerta.titulo}</span>
                  <p>{alerta.detalle}</p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <div className="smart-sidebar-card">
        <div className="smart-section-title">
          <Target size={17} />
          <span>Área prioritaria</span>
        </div>

        {areaCritica ? (
          <button
            type="button"
            className="smart-priority-area"
            onClick={() => setAreaAnalytics(areaCritica)}
          >
            <div className="area-avatar smart-avatar">
              {inicialesArea(areaCritica.nombre)}
            </div>
            <div>
              <strong>{areaCritica.nombre}</strong>
              <span>{areaCritica.nivel_riesgo || "MEDIO"} · {areaCritica.numero_empleados || 0} empleados</span>
              <p>{areaCritica.sede_nombre || "Sin sede"}</p>
            </div>
          </button>
        ) : (
          <div className="smart-empty">No hay áreas visibles para priorizar.</div>
        )}
      </div>

      <div className="smart-sidebar-card">
        <div className="smart-section-title">
          <ClipboardList size={17} />
          <span>Recomendaciones PRO</span>
        </div>

        <ul className="smart-recommendations">
          {recomendaciones.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>

      <div className="smart-sidebar-card smart-actions">
        <button type="button" onClick={cargarDatos} disabled={cargando}>
          <RefreshCw size={16} className={cargando ? "spin-areas" : ""} />
          Actualizar analytics
        </button>
        <button type="button" onClick={() => setFiltroRiesgo("CRÍTICO")}>
          <ShieldAlert size={16} />
          Ver críticos
        </button>
        <button type="button" onClick={() => areaAnalytics && setAreaAnalytics(areaAnalytics)} disabled={!areaAnalytics}>
          <Activity size={16} />
          Mantener área seleccionada
        </button>
      </div>
    </aside>
  );
}

export default function AreasSSTPage() {
  const [areas, setAreas] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [dashboard, setDashboard] = useState({
    total_areas: 0,
    areas_activas: 0,
    areas_inactivas: 0,
    total_empleados: 0,
    tipos_area: {},
    niveles_riesgo: {},
    procesos: {},
  });

  const [form, setForm] = useState(FORM_INICIAL);
  const [areaSeleccionada, setAreaSeleccionada] = useState(null);
  const [areaAnalytics, setAreaAnalytics] = useState(null);
  const [editandoId, setEditandoId] = useState(null);

  const [busqueda, setBusqueda] = useState("");
  const [filtroEmpresa, setFiltroEmpresa] = useState("");
  const [filtroSede, setFiltroSede] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("");
  const [filtroRiesgo, setFiltroRiesgo] = useState("");

  const [paginaActual, setPaginaActual] = useState(1);
  const [registrosPorPagina, setRegistrosPorPagina] = useState(10);
  const [sidebarVisible, setSidebarVisible] = useState(true);

  const [modalFormulario, setModalFormulario] = useState(false);
  const [modalDetalle, setModalDetalle] = useState(false);
  const [modalHistorial, setModalHistorial] = useState(false);
  const [areaHistorial, setAreaHistorial] = useState(null);
  const [historialArea, setHistorialArea] = useState([]);
  const [historialForm, setHistorialForm] = useState(HISTORIAL_FORM_INICIAL);
  const [cargandoHistorial, setCargandoHistorial] = useState(false);
  const [guardandoHistorial, setGuardandoHistorial] = useState(false);

  const [cargando, setCargando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [exportando, setExportando] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  const cargarDatos = async () => {
    try {
      setCargando(true);
      setError("");

      const params = {};
      if (filtroEmpresa) params.empresa_id = Number(filtroEmpresa);
      if (filtroSede) params.sede_id = Number(filtroSede);
      if (filtroEstado !== "") params.activo = filtroEstado === "true";
      if (filtroTipo) params.tipo_area = filtroTipo;
      if (filtroRiesgo) params.nivel_riesgo = filtroRiesgo;
      if (busqueda) params.buscar = busqueda;

      const sedeParams = {};
      if (filtroEmpresa) sedeParams.empresa_id = Number(filtroEmpresa);

      const [areasData, empresasData, sedesData, dashboardData] = await Promise.all([
        listarAreasSST(params),
        listarEmpresasParaAreasSST(),
        listarSedesParaAreasSST(sedeParams),
        obtenerDashboardAreasSST(
          filtroEmpresa || filtroSede
            ? {
                ...(filtroEmpresa ? { empresa_id: Number(filtroEmpresa) } : {}),
                ...(filtroSede ? { sede_id: Number(filtroSede) } : {}),
              }
            : {}
        ),
      ]);

      const areasList = Array.isArray(areasData) ? areasData : [];
      setAreas(areasList);
      setEmpresas(Array.isArray(empresasData) ? empresasData : []);
      setSedes(Array.isArray(sedesData) ? sedesData : []);
      setDashboard(dashboardData || {});

      if (!areaAnalytics && areasList.length > 0) {
        setAreaAnalytics(areasList[0]);
      }
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
          "No fue posible cargar las áreas. Verifica backend, token y conexión."
      );
    } finally {
      setCargando(false);
    }
  };

  const smartDelete = useSmartDelete({
    entidad: "area",
    etiquetaEntidad: "área",
    getNombre: (area) => area?.nombre || "Área sin nombre",
    getDescripcion: (area) =>
      [
        area?.empresa_nombre ? `Empresa: ${area.empresa_nombre}` : null,
        area?.sede_nombre ? `Sede: ${area.sede_nombre}` : null,
        area?.codigo_area ? `Código: ${area.codigo_area}` : null,
      ]
        .filter(Boolean)
        .join(" · "),
    onSuccess: async (resultado) => {
      setMensaje(
        resultado?.accion === "INACTIVADO"
          ? "Área inactivada correctamente por trazabilidad."
          : "Área eliminada definitivamente."
      );
      await cargarDatos();
    },
    onError: (mensajeError) => {
      setError(mensajeError || "No fue posible ejecutar la eliminación inteligente del área.");
    },
  });

  useEffect(() => {
    cargarDatos();
  }, []);

  useEffect(() => {
    setPaginaActual(1);
  }, [busqueda, filtroEmpresa, filtroSede, filtroEstado, filtroTipo, filtroRiesgo]);

  const sedesFiltradasFormulario = useMemo(() => {
    if (!form.empresa_id) return sedes;
    return sedes.filter((sede) => Number(sede.empresa_id) === Number(form.empresa_id));
  }, [sedes, form.empresa_id]);

  const sedesDisponiblesFiltro = useMemo(() => {
    if (!filtroEmpresa) return sedes;
    return sedes.filter((sede) => Number(sede.empresa_id) === Number(filtroEmpresa));
  }, [sedes, filtroEmpresa]);

  const areasFiltradasCliente = useMemo(() => {
    const q = busqueda.toLowerCase().trim();

    return areas.filter((area) => {
      const coincideBusqueda =
        !q ||
        [
          area.nombre,
          area.codigo_area,
          area.empresa_nombre,
          area.empresa_nit,
          area.sede_nombre,
          area.sede_ciudad,
          area.descripcion,
          area.proceso_asociado,
          area.responsable_area,
          area.cargo_responsable,
          area.tipo_area,
          area.nivel_riesgo,
        ]
          .join(" ")
          .toLowerCase()
          .includes(q);

      const coincideEmpresa =
        !filtroEmpresa || Number(area.empresa_id) === Number(filtroEmpresa);

      const coincideSede =
        !filtroSede || Number(area.sede_id) === Number(filtroSede);

      const coincideEstado =
        filtroEstado === "" || String(Boolean(area.activo)) === filtroEstado;

      const coincideTipo =
        !filtroTipo ||
        normalizarTexto(area.tipo_area).toLowerCase() ===
          filtroTipo.toLowerCase();

      const coincideRiesgo =
        !filtroRiesgo ||
        normalizarTexto(area.nivel_riesgo).toLowerCase() ===
          filtroRiesgo.toLowerCase();

      return (
        coincideBusqueda &&
        coincideEmpresa &&
        coincideSede &&
        coincideEstado &&
        coincideTipo &&
        coincideRiesgo
      );
    });
  }, [
    areas,
    busqueda,
    filtroEmpresa,
    filtroSede,
    filtroEstado,
    filtroTipo,
    filtroRiesgo,
  ]);

  const totalPaginas = Math.max(
    1,
    Math.ceil(areasFiltradasCliente.length / registrosPorPagina)
  );

  const paginaSegura = Math.min(paginaActual, totalPaginas);

  const areasPaginadas = useMemo(() => {
    const inicio = (paginaSegura - 1) * registrosPorPagina;
    return areasFiltradasCliente.slice(inicio, inicio + registrosPorPagina);
  }, [areasFiltradasCliente, paginaSegura, registrosPorPagina]);

  const rangoInicio =
    areasFiltradasCliente.length === 0
      ? 0
      : (paginaSegura - 1) * registrosPorPagina + 1;

  const rangoFin = Math.min(
    paginaSegura * registrosPorPagina,
    areasFiltradasCliente.length
  );

  const totalEmpleadosFiltrados = useMemo(
    () =>
      areasFiltradasCliente.reduce(
        (acc, area) => acc + Number(area.numero_empleados || 0),
        0
      ),
    [areasFiltradasCliente]
  );

  const distribucionTipos = useMemo(
    () => convertirDistribucion(agruparPorCampo(areasFiltradasCliente, "tipo_area")),
    [areasFiltradasCliente]
  );

  const distribucionRiesgos = useMemo(
    () => convertirDistribucion(agruparPorCampo(areasFiltradasCliente, "nivel_riesgo")),
    [areasFiltradasCliente]
  );

  const empleadosPorArea = useMemo(
    () =>
      areasFiltradasCliente
        .map((area) => ({
          label: area.nombre || "Sin área",
          value: Number(area.numero_empleados || 0),
        }))
        .sort((a, b) => b.value - a.value),
    [areasFiltradasCliente]
  );

  const empleadosPorSede = useMemo(
    () =>
      convertirDistribucion(
        agruparEmpleadosPorCampo(areasFiltradasCliente, "sede_nombre", "Sin sede")
      ),
    [areasFiltradasCliente]
  );

  const areaMayorEmpleados = useMemo(() => {
    if (!areasFiltradasCliente.length) return null;
    return [...areasFiltradasCliente].sort(
      (a, b) => Number(b.numero_empleados || 0) - Number(a.numero_empleados || 0)
    )[0];
  }, [areasFiltradasCliente]);

  const promedioEmpleados = useMemo(() => {
    if (!areasFiltradasCliente.length) return 0;
    return Math.round(totalEmpleadosFiltrados / areasFiltradasCliente.length);
  }, [areasFiltradasCliente.length, totalEmpleadosFiltrados]);

  const abrirCrear = () => {
    setEditandoId(null);
    setAreaSeleccionada(null);
    setAreaHistorial(null);
    setForm({
      ...FORM_INICIAL,
      empresa_id:
        filtroEmpresa ||
        (empresas.length === 1 ? String(empresas[0].id) : ""),
      sede_id: filtroSede || "",
    });
    setModalFormulario(true);
  };

  const abrirEditar = (area) => {
    setEditandoId(area.id);
    setAreaSeleccionada(area);
    setForm({
      empresa_id: area.empresa_id || "",
      sede_id: area.sede_id || "",
      nombre: area.nombre || "",
      codigo_area: area.codigo_area || "",
      descripcion: area.descripcion || "",
      tipo_area: area.tipo_area || "OPERATIVA",
      nivel_riesgo: area.nivel_riesgo || "MEDIO",
      proceso_asociado: area.proceso_asociado || "",
      responsable_area: area.responsable_area || "",
      cargo_responsable: area.cargo_responsable || "",
      correo_responsable: area.correo_responsable || "",
      telefono_responsable: area.telefono_responsable || "",
      numero_empleados: area.numero_empleados ?? 0,
      activo: Boolean(area.activo),
    });
    setModalFormulario(true);
  };

  const abrirDetalle = (area) => {
    setAreaSeleccionada(area);
    setAreaAnalytics(area);
    setModalDetalle(true);
  };

  const abrirHistorial = async (area) => {
    try {
      setAreaHistorial(area);
      setModalHistorial(true);
      setHistorialForm({
        ...HISTORIAL_FORM_INICIAL,
        responsable: area?.responsable_area || "",
      });
      setCargandoHistorial(true);
      setError("");

      const eventos = await listarHistorialAreaSST(area.id, { limite: 150 });
      setHistorialArea(Array.isArray(eventos) ? eventos : []);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No fue posible cargar el histórico SST del área.");
    } finally {
      setCargandoHistorial(false);
    }
  };

  const handleHistorialChange = (event) => {
    const { name, value } = event.target;
    setHistorialForm((prev) => ({ ...prev, [name]: value }));
  };

  const guardarEventoHistorial = async (event) => {
    event.preventDefault();

    if (!areaHistorial?.id) return;

    if (!normalizarTexto(historialForm.titulo)) {
      setError("El título del evento histórico es obligatorio.");
      return;
    }

    try {
      setGuardandoHistorial(true);
      setError("");

      const payload = {
        tipo_evento: historialForm.tipo_evento,
        titulo: normalizarTexto(historialForm.titulo),
        descripcion: normalizarTexto(historialForm.descripcion) || null,
        impacto_sst: historialForm.impacto_sst,
        estado_resultante: historialForm.estado_resultante,
        responsable: normalizarTexto(historialForm.responsable) || null,
        evidencia_url: normalizarTexto(historialForm.evidencia_url) || null,
        fecha_evento: historialForm.fecha_evento || null,
      };

      await crearHistorialAreaSST(areaHistorial.id, payload);
      const eventos = await listarHistorialAreaSST(areaHistorial.id, { limite: 150 });
      setHistorialArea(Array.isArray(eventos) ? eventos : []);
      setHistorialForm({
        ...HISTORIAL_FORM_INICIAL,
        responsable: areaHistorial?.responsable_area || "",
      });
      setMensaje("Evento agregado al histórico SST del área.");
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No fue posible guardar el evento histórico.");
    } finally {
      setGuardandoHistorial(false);
    }
  };

  const eliminarEventoHistorial = async (evento) => {
    const confirmar = window.confirm(`¿Eliminar del histórico el evento: ${evento.titulo}?`);
    if (!confirmar) return;

    try {
      setGuardandoHistorial(true);
      await eliminarHistorialAreaSST(evento.id);
      setHistorialArea((prev) => prev.filter((item) => item.id !== evento.id));
      setMensaje("Evento histórico eliminado correctamente.");
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No fue posible eliminar el evento histórico.");
    } finally {
      setGuardandoHistorial(false);
    }
  };

  const cerrarModales = () => {
    setModalFormulario(false);
    setModalDetalle(false);
    setModalHistorial(false);
    setEditandoId(null);
    setAreaSeleccionada(null);
    setAreaHistorial(null);
    setForm(FORM_INICIAL);
  };

  const limpiarFiltros = () => {
    setBusqueda("");
    setFiltroEmpresa("");
    setFiltroSede("");
    setFiltroEstado("");
    setFiltroTipo("");
    setFiltroRiesgo("");
    setPaginaActual(1);
    setTimeout(cargarDatos, 0);
  };

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;

    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
      ...(name === "empresa_id" ? { sede_id: "" } : {}),
    }));
  };

  const validarFormulario = () => {
    if (!form.empresa_id) return "Selecciona la empresa.";
    if (!normalizarTexto(form.nombre)) return "El nombre del área es obligatorio.";
    if (Number(form.numero_empleados || 0) < 0) {
      return "El número de empleados no puede ser negativo.";
    }
    return "";
  };

  const guardarArea = async (event) => {
    event.preventDefault();

    const validacion = validarFormulario();
    if (validacion) {
      setError(validacion);
      return;
    }

    try {
      setGuardando(true);
      setError("");
      setMensaje("");

      const payload = {
        empresa_id: Number(form.empresa_id),
        sede_id: form.sede_id ? Number(form.sede_id) : null,
        nombre: normalizarTexto(form.nombre),
        codigo_area: normalizarTexto(form.codigo_area) || null,
        descripcion: normalizarTexto(form.descripcion) || null,
        tipo_area: normalizarTexto(form.tipo_area) || "OPERATIVA",
        nivel_riesgo: normalizarTexto(form.nivel_riesgo) || "MEDIO",
        proceso_asociado: normalizarTexto(form.proceso_asociado) || null,
        responsable_area: normalizarTexto(form.responsable_area) || null,
        cargo_responsable: normalizarTexto(form.cargo_responsable) || null,
        correo_responsable: normalizarTexto(form.correo_responsable) || null,
        telefono_responsable: normalizarTexto(form.telefono_responsable) || null,
        numero_empleados: Number(form.numero_empleados || 0),
      };

      if (editandoId) {
        await actualizarAreaSST(editandoId, {
          ...payload,
          activo: Boolean(form.activo),
        });
        setMensaje("Área actualizada correctamente.");
      } else {
        await crearAreaSST(payload);
        setMensaje("Área creada correctamente.");
      }

      cerrarModales();
      await cargarDatos();
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
          "No fue posible guardar el área. Revisa los datos enviados."
      );
    } finally {
      setGuardando(false);
    }
  };

  const alternarEstado = async (area) => {
    try {
      setError("");
      setMensaje("");
      await cambiarEstadoAreaSST(area.id, !area.activo);
      setMensaje(
        area.activo
          ? "Área inactivada correctamente."
          : "Área activada correctamente."
      );
      await cargarDatos();
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail || "No fue posible cambiar el estado."
      );
    }
  };

  const parametrosExportacion = () => ({
    empresa_id: filtroEmpresa || undefined,
    sede_id: filtroSede || undefined,
    activo: filtroEstado === "" ? undefined : filtroEstado,
    nivel_riesgo: filtroRiesgo || undefined,
    buscar: busqueda || undefined,
  });

  const exportarAreas = async () => {
    try {
      setError("");
      setMensaje("");
      setExportando(true);
      await exportarAreasSSTExcel(parametrosExportacion());
      setMensaje("Excel generado correctamente con los filtros aplicados.");
    } catch (err) {
      console.error(err);
      setError("No fue posible generar el Excel de áreas SST. Verifica el backend y las dependencias openpyxl.");
    } finally {
      setExportando(false);
    }
  };

  const imprimirPDF = async () => {
    try {
      setError("");
      setMensaje("");
      setExportando(true);
      await exportarAreasSSTPDF(parametrosExportacion());
      setMensaje("PDF generado correctamente con los filtros aplicados.");
    } catch (err) {
      console.error(err);
      setError("No fue posible generar el PDF de áreas SST. Verifica el backend y la dependencia reportlab.");
    } finally {
      setExportando(false);
    }
  };

  const kpis = [
    {
      label: "Total áreas",
      value: dashboard.total_areas ?? areas.length,
      icon: Network,
      color: "blue",
      action: () => setFiltroEstado(""),
    },
    {
      label: "Activas",
      value:
        dashboard.areas_activas ??
        areas.filter((area) => area.activo).length,
      icon: CheckCircle2,
      color: "green",
      action: () => setFiltroEstado("true"),
    },
    {
      label: "Inactivas",
      value:
        dashboard.areas_inactivas ??
        areas.filter((area) => !area.activo).length,
      icon: AlertCircle,
      color: "red",
      action: () => setFiltroEstado("false"),
    },
    {
      label: "Riesgo alto/crítico",
      value: areas.filter((area) =>
        ["ALTO", "CRÍTICO", "CRITICO"].includes(
          normalizarTexto(area.nivel_riesgo).toUpperCase()
        )
      ).length,
      icon: ShieldAlert,
      color: "amber",
      action: () => setFiltroRiesgo("ALTO"),
    },
    {
      label: "Empleados",
      value: dashboard.total_empleados ?? totalEmpleadosFiltrados,
      icon: Users,
      color: "purple",
      action: () =>
        setAreas((prev) =>
          [...prev].sort(
            (a, b) =>
              Number(b.numero_empleados || 0) - Number(a.numero_empleados || 0)
          )
        ),
    },
  ];

  return (
    <main className="areas-sst-page">
      <section className="areas-sst-hero">
        <div className="areas-hero-content">
          <h1>Áreas SST 360°</h1>

          <p>
            Gestiona las áreas y consulta sus responsables, personal y nivel de riesgo.
          </p>
        </div>

        <div className="areas-hero-actions">
          <button className="btn-secondary-areas" onClick={imprimirPDF} disabled={exportando}>
            {exportando ? <Loader2 size={17} className="spin" /> : <Printer size={17} />}
            Exportar PDF
          </button>

          <button className="btn-secondary-areas" onClick={exportarAreas} disabled={exportando}>
            {exportando ? <Loader2 size={17} className="spin" /> : <Download size={17} />}
            Exportar Excel
          </button>

          <button className="btn-primary-areas" onClick={abrirCrear}>
            <Plus size={18} />
            Nueva área
          </button>
        </div>
      </section>

      {error && (
        <div className="areas-sst-alert error">
          <AlertCircle size={18} />
          <span>{error}</span>
          <button onClick={() => setError("")}>
            <X size={16} />
          </button>
        </div>
      )}

      {mensaje && (
        <div className="areas-sst-alert success">
          <CheckCircle2 size={18} />
          <span>{mensaje}</span>
          <button onClick={() => setMensaje("")}>
            <X size={16} />
          </button>
        </div>
      )}

      <section className={`areas-intelligent-layout ${!sidebarVisible ? "sidebar-collapsed" : ""}`}>
        <div className="areas-intelligent-main">
      <section className="areas-sst-kpis">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <button
              key={kpi.label}
              className="area-kpi-card"
              type="button"
              onClick={kpi.action}
            >
              <div className={`kpi-icon-areas ${kpi.color}`}>
                <Icon size={22} />
              </div>
              <div>
                <span>{kpi.label}</span>
                <strong>{kpi.value}</strong>
              </div>
            </button>
          );
        })}
      </section>

      <section className="areas-executive-grid">
        <DonutEstado
          activas={
            dashboard.areas_activas ??
            areasFiltradasCliente.filter((area) => area.activo).length
          }
          inactivas={
            dashboard.areas_inactivas ??
            areasFiltradasCliente.filter((area) => !area.activo).length
          }
        />

        <MiniBarChart
          titulo="Áreas por tipo"
          subtitulo="Distribución organizacional"
          data={distribucionTipos}
          icon={Network}
        />

        <MiniBarChart
          titulo="Niveles de riesgo"
          subtitulo="Priorización SST"
          data={distribucionRiesgos}
          icon={ShieldAlert}
        />

        <MiniBarChart
          titulo="Empleados por sede"
          subtitulo="Carga poblacional"
          data={empleadosPorSede}
          icon={TrendingUp}
        />
      </section>

      <section className="areas-exec-summary">
        <article>
          <div className="summary-icon">
            <Target size={20} />
          </div>
          <div>
            <span>Área con más empleados</span>
            <strong>{areaMayorEmpleados?.nombre || "Sin datos"}</strong>
            <p>
              {areaMayorEmpleados
                ? `${areaMayorEmpleados.numero_empleados || 0} empleados · ${
                    areaMayorEmpleados.sede_nombre || "Sin sede"
                  }`
                : "No existen áreas registradas para calcular este indicador."}
            </p>
          </div>
        </article>

        <article>
          <div className="summary-icon purple">
            <BarChart3 size={20} />
          </div>
          <div>
            <span>Promedio empleados por área</span>
            <strong>{promedioEmpleados}</strong>
            <p>Promedio calculado sobre las áreas visibles en los filtros.</p>
          </div>
        </article>

        <article>
          <div className="summary-icon amber">
            <Route size={20} />
          </div>
          <div>
            <span>Tipos de área activos</span>
            <strong>{distribucionTipos.length}</strong>
            <p>Clasificación operativa disponible para la estructura SST.</p>
          </div>
        </article>
      </section>

      <AnalyticsAreaPanel
        area={areaAnalytics}
        promedioEmpleados={promedioEmpleados}
        totalEmpleados={totalEmpleadosFiltrados}
        onVerHistorial={abrirHistorial}
      />

      <section className="areas-tipos-strip">
        {NIVELES_RIESGO.map((riesgo) => (
          <button
            key={riesgo}
            type="button"
            className={`riesgo-chip ${filtroRiesgo === riesgo ? "active" : ""}`}
            onClick={() => setFiltroRiesgo(filtroRiesgo === riesgo ? "" : riesgo)}
          >
            {riesgo}: {areas.filter((area) => area.nivel_riesgo === riesgo).length}
          </button>
        ))}
      </section>

      <section className="areas-sst-panel">
        <div className="areas-sst-toolbar">
          <div className="search-box-areas">
            <Search size={18} />
            <input
              value={busqueda}
              onChange={(event) => setBusqueda(event.target.value)}
              placeholder="Buscar por área, empresa, sede, proceso, responsable..."
            />
          </div>

          <div className="toolbar-actions-areas">
            <button className="btn-secondary-areas" onClick={limpiarFiltros}>
              <Filter size={17} />
              Limpiar
            </button>

            <button
              className="btn-secondary-areas"
              onClick={cargarDatos}
              disabled={cargando}
            >
              <RefreshCw
                size={17}
                className={cargando ? "spin-areas" : ""}
              />
              Actualizar
            </button>

            <button
              className="btn-secondary-areas"
              type="button"
              onClick={() => setSidebarVisible((visible) => !visible)}
              title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
              aria-label={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
              aria-pressed={!sidebarVisible}
            >
              {sidebarVisible ? <Sidebar size={17} /> : <LayoutDashboard size={17} />}
            </button>
          </div>
        </div>

        <div className="filters-grid-areas">
          <label>
            Empresa
            <select
              value={filtroEmpresa}
              onChange={(event) => {
                setFiltroEmpresa(event.target.value);
                setFiltroSede("");
              }}
            >
              <option value="">Todas</option>
              {empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>
                  {empresa.nombre}
                </option>
              ))}
            </select>
          </label>

          <label>
            Sede
            <select
              value={filtroSede}
              onChange={(event) => setFiltroSede(event.target.value)}
            >
              <option value="">Todas</option>
              {sedesDisponiblesFiltro.map((sede) => (
                <option key={sede.id} value={sede.id}>
                  {sede.nombre}
                </option>
              ))}
            </select>
          </label>

          <label>
            Estado
            <select
              value={filtroEstado}
              onChange={(event) => setFiltroEstado(event.target.value)}
            >
              <option value="">Todas</option>
              <option value="true">Activas</option>
              <option value="false">Inactivas</option>
            </select>
          </label>

          <label>
            Riesgo
            <select
              value={filtroRiesgo}
              onChange={(event) => setFiltroRiesgo(event.target.value)}
            >
              <option value="">Todos</option>
              {NIVELES_RIESGO.map((riesgo) => (
                <option key={riesgo} value={riesgo}>
                  {riesgo}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="areas-table-wrapper">
          <table className="areas-table">
            <thead>
              <tr>
                <th>Empresa</th>
                <th>Sede</th>
                <th>Código</th>
                <th>Área</th>
                <th>Tipo</th>
                <th>Riesgo</th>
                <th>Proceso</th>
                <th>Responsable</th>
                <th>Empleados</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {cargando ? (
                <tr>
                  <td colSpan="11" className="empty-row-areas">
                    <Loader2 className="spin-areas" size={18} />
                    Cargando áreas...
                  </td>
                </tr>
              ) : areasPaginadas.length === 0 ? (
                <tr>
                  <td colSpan="11" className="empty-row-areas">
                    <Network size={18} />
                    No hay áreas para los filtros seleccionados.
                  </td>
                </tr>
              ) : (
                areasPaginadas.map((area) => (
                  <tr
                    key={area.id}
                    className={
                      areaAnalytics?.id === area.id ? "selected-row-areas" : ""
                    }
                  >
                    <td>
                      <div className="empresa-cell-areas">
                        <div className="empresa-avatar-areas">
                          <Building2 size={17} />
                        </div>
                        <div>
                          <strong>{area.empresa_nombre || "Sin empresa"}</strong>
                          <span>NIT: {area.empresa_nit || "—"}</span>
                        </div>
                      </div>
                    </td>

                    <td>
                      <div className="sede-cell-areas">
                        <MapPin size={15} />
                        <div>
                          <strong>{area.sede_nombre || "Sin sede"}</strong>
                          <span>{area.sede_ciudad || "—"}</span>
                        </div>
                      </div>
                    </td>

                    <td>
                      <span className="codigo-pill-areas">
                        {area.codigo_area || "SIN-CÓDIGO"}
                      </span>
                    </td>

                    <td>
                      <button
                        type="button"
                        className="area-name-button"
                        onClick={() => setAreaAnalytics(area)}
                      >
                        <div className="area-avatar">
                          {inicialesArea(area.nombre)}
                        </div>
                        <div>
                          <strong>{area.nombre}</strong>
                          <span>{area.descripcion || "Sin descripción"}</span>
                        </div>
                      </button>
                    </td>

                    <td>
                      <span className="tipo-pill-areas">
                        {area.tipo_area || "OPERATIVA"}
                      </span>
                    </td>

                    <td>
                      <span className={`riesgo-pill-areas ${riesgoClass(area.nivel_riesgo)}`}>
                        {area.nivel_riesgo || "MEDIO"}
                      </span>
                    </td>

                    <td>
                      <strong className="table-strong-areas">
                        {area.proceso_asociado || "—"}
                      </strong>
                    </td>

                    <td>
                      <strong className="table-strong-areas">
                        {area.responsable_area || "—"}
                      </strong>
                      <span className="muted-areas">
                        {area.cargo_responsable || "Sin cargo"}
                      </span>
                    </td>

                    <td>
                      <span className="empleados-pill-areas">
                        <Users size={14} />
                        {area.numero_empleados || 0}
                      </span>
                    </td>

                    <td>
                      <button
                        className={
                          area.activo
                            ? "status-pill-areas active"
                            : "status-pill-areas inactive"
                        }
                        type="button"
                        onClick={() => alternarEstado(area)}
                        title="Cambiar estado"
                      >
                        {estadoTexto(area.activo)}
                      </button>
                    </td>

                    <td>
                      <div className="table-actions-areas">
                        <button
                          className="icon-btn-areas analytics"
                          onClick={() => setAreaAnalytics(area)}
                          title="Analytics área"
                        >
                          <Activity size={16} />
                        </button>

                        <button
                          className="icon-btn-areas history"
                          onClick={() => abrirHistorial(area)}
                          title="Histórico SST"
                        >
                          <History size={16} />
                        </button>

                        <button
                          className="icon-btn-areas view"
                          onClick={() => abrirDetalle(area)}
                          title="Ver detalle"
                        >
                          <Eye size={16} />
                        </button>

                        <button
                          className="icon-btn-areas edit"
                          onClick={() => abrirEditar(area)}
                          title="Editar área"
                        >
                          <Edit3 size={16} />
                        </button>

                        <button
                          className="icon-btn-areas delete"
                          onClick={() => smartDelete.open(area)}
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

        <div className="pagination-areas">
          <div className="pagination-info-areas">
            Mostrando <strong>{rangoInicio}</strong> -{" "}
            <strong>{rangoFin}</strong> de{" "}
            <strong>{areasFiltradasCliente.length}</strong> áreas
          </div>

          <div className="pagination-controls-areas">
            <label>
              Registros
              <select
                value={registrosPorPagina}
                onChange={(event) => {
                  setRegistrosPorPagina(Number(event.target.value));
                  setPaginaActual(1);
                }}
              >
                {PAGE_SIZE_OPTIONS.map((cantidad) => (
                  <option key={cantidad} value={cantidad}>
                    {cantidad}
                  </option>
                ))}
              </select>
            </label>

            <button
              onClick={() => setPaginaActual(1)}
              disabled={paginaSegura === 1}
            >
              <ChevronsLeft size={17} />
            </button>

            <button
              onClick={() => setPaginaActual((prev) => Math.max(1, prev - 1))}
              disabled={paginaSegura === 1}
            >
              <ChevronLeft size={17} />
            </button>

            <span>
              Página <strong>{paginaSegura}</strong> de{" "}
              <strong>{totalPaginas}</strong>
            </span>

            <button
              onClick={() =>
                setPaginaActual((prev) => Math.min(totalPaginas, prev + 1))
              }
              disabled={paginaSegura === totalPaginas}
            >
              <ChevronRight size={17} />
            </button>

            <button
              onClick={() => setPaginaActual(totalPaginas)}
              disabled={paginaSegura === totalPaginas}
            >
              <ChevronsRight size={17} />
            </button>
          </div>
        </div>
      </section>

      <section className="areas-executive-grid bottom">
        <MiniBarChart
          titulo="Empleados por área"
          subtitulo="Ranking operativo"
          data={empleadosPorArea}
          icon={Users}
        />

        <article className="areas-exec-card narrative-card">
          <div className="exec-card-header">
            <div>
              <span>Lectura ejecutiva</span>
              <h3>Resumen gerencial</h3>
            </div>
            <div className="exec-card-icon purple">
              <FileText size={20} />
            </div>
          </div>

          <p>
            El módulo consolida <strong>{areasFiltradasCliente.length}</strong>{" "}
            áreas visibles con <strong>{totalEmpleadosFiltrados}</strong>{" "}
            empleados asociados. El área con mayor carga poblacional es{" "}
            <strong>{areaMayorEmpleados?.nombre || "sin información"}</strong>.
          </p>

          <p>
            Esta información será la base para relacionar cargos, empleados,
            matrices de peligros, planes de trabajo, inspecciones y reportes SST
            por área.
          </p>
        </article>
      </section>

        </div>

        <DashboardLateralInteligente
          areas={areas}
          areasFiltradas={areasFiltradasCliente}
          totalEmpleados={totalEmpleadosFiltrados}
          promedioEmpleados={promedioEmpleados}
          areaAnalytics={areaAnalytics}
          setFiltroEstado={setFiltroEstado}
          setFiltroRiesgo={setFiltroRiesgo}
          setBusqueda={setBusqueda}
          setAreaAnalytics={setAreaAnalytics}
          cargarDatos={cargarDatos}
          cargando={cargando}
          className={sidebarVisible ? "" : "sidebar-hidden"}
          sidebarVisible={sidebarVisible}
          onToggleSidebar={() => setSidebarVisible((visible) => !visible)}
        />
      </section>

      {modalFormulario && (
        <section className="modal-backdrop-areas">
          <div className="modal-card-areas enterprise-modal-areas">
            <div className="modal-header-areas">
              <div>
                <h2>{editandoId ? "Editar área" : "Nueva área SST"}</h2>
                <p>
                  Registra los datos de empresa, sede, responsable, proceso,
                  clasificación SST y población del área.
                </p>
              </div>

              <button className="modal-close-areas" onClick={cerrarModales}>
                <X size={20} />
              </button>
            </div>

            <form className="area-form" onSubmit={guardarArea}>
              <div className="form-section-title-areas">
                <Building2 size={18} />
                Ubicación organizacional
              </div>

              <div className="form-grid-areas">
                <label>
                  Empresa *
                  <select
                    name="empresa_id"
                    value={form.empresa_id}
                    onChange={handleChange}
                  >
                    <option value="">Seleccione empresa</option>
                    {empresas.map((empresa) => (
                      <option key={empresa.id} value={empresa.id}>
                        {empresa.nombre} — NIT {empresa.nit}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Sede
                  <select
                    name="sede_id"
                    value={form.sede_id}
                    onChange={handleChange}
                  >
                    <option value="">Sin sede asignada</option>
                    {sedesFiltradasFormulario.map((sede) => (
                      <option key={sede.id} value={sede.id}>
                        {sede.nombre} — {sede.ciudad || "Sin ciudad"}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Código área
                  <input
                    name="codigo_area"
                    value={form.codigo_area}
                    onChange={handleChange}
                    placeholder="Ej: ADM-001"
                  />
                </label>
              </div>

              <div className="form-section-title-areas">
                <Network size={18} />
                Datos del área
              </div>

              <div className="form-grid-areas">
                <label>
                  Nombre área *
                  <input
                    name="nombre"
                    value={form.nombre}
                    onChange={handleChange}
                    placeholder="Ej: Talento Humano"
                  />
                </label>

                <label>
                  Tipo área
                  <select
                    name="tipo_area"
                    value={form.tipo_area}
                    onChange={handleChange}
                  >
                    {TIPOS_AREA.map((tipo) => (
                      <option key={tipo} value={tipo}>
                        {tipo}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Nivel de riesgo
                  <select
                    name="nivel_riesgo"
                    value={form.nivel_riesgo}
                    onChange={handleChange}
                  >
                    {NIVELES_RIESGO.map((riesgo) => (
                      <option key={riesgo} value={riesgo}>
                        {riesgo}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Proceso asociado
                  <input
                    name="proceso_asociado"
                    value={form.proceso_asociado}
                    onChange={handleChange}
                    placeholder="Ej: Gestión Humana"
                  />
                </label>

                <label>
                  Número empleados
                  <input
                    type="number"
                    name="numero_empleados"
                    value={form.numero_empleados}
                    onChange={handleChange}
                    min="0"
                  />
                </label>

                <label className="form-full-areas">
                  Descripción
                  <input
                    name="descripcion"
                    value={form.descripcion}
                    onChange={handleChange}
                    placeholder="Descripción funcional del área"
                  />
                </label>
              </div>

              <div className="form-section-title-areas">
                <ClipboardList size={18} />
                Responsable del área
              </div>

              <div className="form-grid-areas">
                <label>
                  Responsable
                  <input
                    name="responsable_area"
                    value={form.responsable_area}
                    onChange={handleChange}
                    placeholder="Nombre del responsable"
                  />
                </label>

                <label>
                  Cargo responsable
                  <input
                    name="cargo_responsable"
                    value={form.cargo_responsable}
                    onChange={handleChange}
                    placeholder="Ej: Coordinador de área"
                  />
                </label>

                <label>
                  Correo
                  <input
                    type="email"
                    name="correo_responsable"
                    value={form.correo_responsable}
                    onChange={handleChange}
                    placeholder="correo@empresa.com"
                  />
                </label>

                <label>
                  Teléfono
                  <input
                    name="telefono_responsable"
                    value={form.telefono_responsable}
                    onChange={handleChange}
                    placeholder="Teléfono de contacto"
                  />
                </label>

                {editandoId && (
                  <label className="form-switch-areas">
                    Estado
                    <span>
                      <input
                        type="checkbox"
                        name="activo"
                        checked={form.activo}
                        onChange={handleChange}
                      />
                      {form.activo ? "Activa" : "Inactiva"}
                    </span>
                  </label>
                )}
              </div>

              <div className="modal-actions-areas sticky-actions-areas">
                <button
                  type="button"
                  className="btn-secondary-areas"
                  onClick={cerrarModales}
                >
                  Cancelar
                </button>

                <button
                  type="submit"
                  className="btn-primary-areas"
                  disabled={guardando}
                >
                  {guardando ? (
                    <Loader2 className="spin-areas" size={17} />
                  ) : (
                    <Save size={17} />
                  )}
                  {guardando ? "Guardando..." : "Guardar área"}
                </button>
              </div>
            </form>
          </div>
        </section>
      )}

      {modalDetalle && areaSeleccionada && (
        <section className="modal-backdrop-areas">
          <div className="modal-card-areas detail-modal-areas">
            <div className="modal-header-areas detail-header-areas">
              <div className="detail-title-areas">
                <div className="area-avatar large">
                  {inicialesArea(areaSeleccionada.nombre)}
                </div>
                <div>
                  <h2>{areaSeleccionada.nombre}</h2>
                  <p>
                    {areaSeleccionada.empresa_nombre || "Sin empresa"} ·{" "}
                    {areaSeleccionada.sede_nombre || "Sin sede"} ·{" "}
                    {areaSeleccionada.codigo_area || "Sin código"}
                  </p>
                </div>
              </div>

              <button className="modal-close-areas" onClick={cerrarModales}>
                <X size={20} />
              </button>
            </div>

            <AnalyticsAreaPanel
              area={areaSeleccionada}
              promedioEmpleados={promedioEmpleados}
              totalEmpleados={totalEmpleadosFiltrados}
              onVerHistorial={abrirHistorial}
            />

            <div className="detail-grid-areas">
              <article>
                <span>Empresa</span>
                <strong>{areaSeleccionada.empresa_nombre || "—"}</strong>
              </article>

              <article>
                <span>Sede</span>
                <strong>{areaSeleccionada.sede_nombre || "—"}</strong>
              </article>

              <article>
                <span>Estado</span>
                <strong>{estadoTexto(areaSeleccionada.activo)}</strong>
              </article>

              <article>
                <span>Tipo área</span>
                <strong>{areaSeleccionada.tipo_area || "OPERATIVA"}</strong>
              </article>

              <article>
                <span>Nivel de riesgo</span>
                <strong>{areaSeleccionada.nivel_riesgo || "MEDIO"}</strong>
              </article>

              <article>
                <span>Empleados</span>
                <strong>{areaSeleccionada.numero_empleados || 0}</strong>
              </article>

              <article className="wide">
                <span>Descripción</span>
                <strong>{areaSeleccionada.descripcion || "—"}</strong>
              </article>

              <article>
                <span>Proceso</span>
                <strong>{areaSeleccionada.proceso_asociado || "—"}</strong>
              </article>

              <article>
                <span>Responsable</span>
                <strong>{areaSeleccionada.responsable_area || "—"}</strong>
              </article>

              <article>
                <span>Cargo responsable</span>
                <strong>{areaSeleccionada.cargo_responsable || "—"}</strong>
              </article>

              <article>
                <span>Correo</span>
                <strong>{areaSeleccionada.correo_responsable || "—"}</strong>
              </article>

              <article>
                <span>Fecha creación</span>
                <strong>{formatoFecha(areaSeleccionada.fecha_creacion)}</strong>
              </article>
            </div>

            <div className="modal-actions-areas">
              <button
                className="btn-secondary-areas"
                onClick={() => {
                  setModalDetalle(false);
    setModalHistorial(false);
                  abrirEditar(areaSeleccionada);
                }}
              >
                <Edit3 size={17} />
                Editar
              </button>

              <button className="btn-primary-areas" onClick={cerrarModales}>
                Cerrar
              </button>
            </div>
          </div>
        </section>
      )}

      {modalHistorial && areaHistorial && (
        <section className="modal-backdrop-areas">
          <div className="modal-card-areas historial-modal-areas">
            <div className="modal-header-areas detail-header-areas">
              <div className="detail-title-areas">
                <div className="area-avatar large">
                  {inicialesArea(areaHistorial.nombre)}
                </div>
                <div>
                  <h2>Histórico SST por Área</h2>
                  <p>
                    {areaHistorial.nombre} · {areaHistorial.empresa_nombre || "Sin empresa"} ·{" "}
                    {areaHistorial.sede_nombre || "Sin sede"}
                  </p>
                </div>
              </div>

              <button className="modal-close-areas" onClick={cerrarModales}>
                <X size={20} />
              </button>
            </div>

            <div className="historial-sst-layout">
              <form className="historial-sst-form" onSubmit={guardarEventoHistorial}>
                <div className="form-section-title-areas">
                  <History size={18} />
                  Nuevo evento histórico
                </div>

                <div className="form-grid-areas historial-form-grid">
                  <label>
                    Tipo evento
                    <select
                      name="tipo_evento"
                      value={historialForm.tipo_evento}
                      onChange={handleHistorialChange}
                    >
                      {TIPOS_EVENTO_HISTORIAL.map((tipo) => (
                        <option key={tipo} value={tipo}>
                          {tipo}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Impacto SST
                    <select
                      name="impacto_sst"
                      value={historialForm.impacto_sst}
                      onChange={handleHistorialChange}
                    >
                      {NIVELES_RIESGO.map((riesgo) => (
                        <option key={riesgo} value={riesgo}>
                          {riesgo}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Estado
                    <select
                      name="estado_resultante"
                      value={historialForm.estado_resultante}
                      onChange={handleHistorialChange}
                    >
                      {ESTADOS_HISTORIAL.map((estado) => (
                        <option key={estado} value={estado}>
                          {estado}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label className="form-full-areas">
                    Título *
                    <input
                      name="titulo"
                      value={historialForm.titulo}
                      onChange={handleHistorialChange}
                      placeholder="Ej: Inspección locativa del área"
                    />
                  </label>

                  <label>
                    Responsable
                    <input
                      name="responsable"
                      value={historialForm.responsable}
                      onChange={handleHistorialChange}
                      placeholder="Responsable del seguimiento"
                    />
                  </label>

                  <label>
                    Fecha evento
                    <input
                      type="datetime-local"
                      name="fecha_evento"
                      value={historialForm.fecha_evento}
                      onChange={handleHistorialChange}
                    />
                  </label>

                  <label>
                    Evidencia URL
                    <input
                      name="evidencia_url"
                      value={historialForm.evidencia_url}
                      onChange={handleHistorialChange}
                      placeholder="https://..."
                    />
                  </label>

                  <label className="form-full-areas">
                    Descripción / observación SST
                    <textarea
                      name="descripcion"
                      value={historialForm.descripcion}
                      onChange={handleHistorialChange}
                      placeholder="Describe el evento, hallazgo, acción tomada o seguimiento realizado..."
                    />
                  </label>
                </div>

                <div className="modal-actions-areas historial-actions-form">
                  <button className="btn-secondary-areas" type="button" onClick={() => abrirHistorial(areaHistorial)}>
                    <RefreshCw size={17} className={cargandoHistorial ? "spin-areas" : ""} />
                    Recargar
                  </button>

                  <button className="btn-primary-areas" type="submit" disabled={guardandoHistorial}>
                    {guardandoHistorial ? <Loader2 className="spin-areas" size={17} /> : <Save size={17} />}
                    Guardar evento
                  </button>
                </div>
              </form>

              <div className="historial-sst-timeline">
                <div className="historial-summary-cards">
                  <article>
                    <span>Total eventos</span>
                    <strong>{historialArea.length}</strong>
                  </article>
                  <article>
                    <span>Alto/Crítico</span>
                    <strong>
                      {historialArea.filter((item) => ["ALTO", "CRÍTICO", "CRITICO"].includes(String(item.impacto_sst || "").toUpperCase())).length}
                    </strong>
                  </article>
                  <article>
                    <span>Abiertos</span>
                    <strong>
                      {historialArea.filter((item) => !["CERRADO", "FINALIZADO", "RESUELTO"].includes(String(item.estado_resultante || "").toUpperCase())).length}
                    </strong>
                  </article>
                </div>

                {cargandoHistorial ? (
                  <div className="historial-empty-state">
                    <Loader2 className="spin-areas" size={20} />
                    Cargando histórico SST...
                  </div>
                ) : historialArea.length === 0 ? (
                  <div className="historial-empty-state">
                    <History size={22} />
                    <strong>Sin eventos históricos registrados</strong>
                    <p>Agrega inspecciones, hallazgos, acciones de mejora, auditorías o cambios SST del área.</p>
                  </div>
                ) : (
                  <div className="historial-timeline-list">
                    {historialArea.map((evento) => (
                      <article key={evento.id} className="historial-event-card">
                        <div className="historial-event-marker">
                          <CalendarDays size={16} />
                        </div>
                        <div className="historial-event-body">
                          <div className="historial-event-head">
                            <div>
                              <span>{evento.tipo_evento}</span>
                              <h3>{evento.titulo}</h3>
                            </div>
                            <button
                              type="button"
                              className="icon-btn-areas delete"
                              onClick={() => eliminarEventoHistorial(evento)}
                              disabled={guardandoHistorial}
                              title="Eliminar evento"
                            >
                              <Trash2 size={15} />
                            </button>
                          </div>

                          <p>{evento.descripcion || "Sin descripción registrada."}</p>

                          <div className="historial-event-meta">
                            <span className={`riesgo-pill-areas ${riesgoClass(evento.impacto_sst)}`}>
                              {evento.impacto_sst || "MEDIO"}
                            </span>
                            <span className="codigo-pill-areas">
                              {evento.estado_resultante || "REGISTRADO"}
                            </span>
                            <span>
                              <Users size={13} /> {evento.responsable || "Sin responsable"}
                            </span>
                            <span>
                              <CalendarDays size={13} /> {formatoFechaHora(evento.fecha_evento)}
                            </span>
                          </div>

                          {evento.evidencia_url && (
                            <a
                              className="historial-evidencia-link"
                              href={evento.evidencia_url}
                              target="_blank"
                              rel="noreferrer"
                            >
                              <FileText size={14} /> Ver evidencia
                            </a>
                          )}
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="modal-actions-areas">
              <button className="btn-primary-areas" onClick={cerrarModales}>
                Cerrar histórico
              </button>
            </div>
          </div>
        </section>
      )}

      {smartDelete.modal}
    </main>
  );
}
