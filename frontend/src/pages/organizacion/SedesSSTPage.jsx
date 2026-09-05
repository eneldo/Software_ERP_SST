// ============================================================
// SEDES SST ANALYTICS PRO
// Archivo: frontend/src/pages/organizacion/SedesSSTPage.jsx
// FASE 1.1.2.4 — Sedes SST Analytics PRO
// ============================================================

import { useEffect, useMemo, useState } from "react";
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
  FileSpreadsheet,
  FileText,
  Filter,
  Gauge,
  Layers3,
  Loader2,
  MapPin,
  Network,
  PieChart,
  Plus,
  Printer,
  RefreshCw,
  Route,
  Save,
  Search,
  ShieldCheck,
  Target,
  Trash2,
  TrendingUp,
  Users,
  X,
} from "lucide-react";

import {
  actualizarSedeSST,
  cambiarEstadoSedeSST,
  crearSedeSST,
  eliminarInteligenteSedeSST,
  listarEmpresasParaSedesSST,
  listarSedesSST,
  obtenerDashboardSedesSST,
  validarEliminacionSedeSST,
} from "../../api/sedeSstApi";

import EliminacionInteligenteModal from "../../components/common/EliminacionInteligenteModal";

import "../../styles/sedes-sst.css";

const FORM_INICIAL = {
  empresa_id: "",
  nombre: "",
  codigo_sede: "",
  tipo_sede: "PRINCIPAL",
  direccion: "",
  ciudad: "",
  departamento: "",
  telefono: "",
  correo: "",
  responsable_sede: "",
  cargo_responsable: "",
  numero_empleados: 0,
  activo: true,
};

const TIPOS_SEDE = [
  "PRINCIPAL",
  "ADMINISTRATIVA",
  "OPERATIVA",
  "PLANTA",
  "BODEGA",
  "SUCURSAL",
  "CENTRO_TRABAJO",
];

const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

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

function inicialesSede(nombre) {
  const limpio = normalizarTexto(nombre);
  if (!limpio) return "SD";

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

function obtenerMensajeErrorApi(err, fallback = "No fue posible completar la operación.") {
  const data = err?.response?.data;

  if (!data) return fallback;
  if (typeof data === "string") return data;
  if (data.detail) return data.detail;
  if (data.message) return data.message;
  if (data.mensaje) return data.mensaje;

  return fallback;
}

function resumenDependencias(dependencies = []) {
  if (!Array.isArray(dependencies) || dependencies.length === 0) {
    return "Sin dependencias registradas.";
  }

  return dependencies
    .slice(0, 8)
    .map((item) => `• ${item.label || item.table}: ${item.count || 0}`)
    .join("\n");
}

function MiniBarChart({ titulo, subtitulo, data, icon: Icon }) {
  const max = maximoValor(data);

  return (
    <article className="sedes-exec-card">
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
    <article className="sedes-exec-card donut-card">
      <div className="exec-card-header">
        <div>
          <span>Control operativo</span>
          <h3>Estado de sedes</h3>
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

function AnalyticsSedePanel({ sede, promedioEmpleados, totalEmpleados }) {
  if (!sede) {
    return (
      <section className="analytics-empty-panel">
        <div className="analytics-empty-icon">
          <Activity size={24} />
        </div>
        <div>
          <h3>Selecciona una sede para ver Analytics PRO</h3>
          <p>
            Usa el botón “Ver” de la tabla para abrir una ficha ejecutiva con
            accesos rápidos, indicadores y lectura gerencial de la sede.
          </p>
        </div>
      </section>
    );
  }

  const empleados = Number(sede.numero_empleados || 0);
  const pesoPoblacional = porcentaje(empleados, totalEmpleados);

  const saludOperativa = sede.activo ? 100 : 0;
  const criticidad =
    empleados >= promedioEmpleados * 1.5
      ? "Alta carga poblacional"
      : empleados >= promedioEmpleados
      ? "Carga media"
      : "Carga baja";

  return (
    <section className="analytics-sede-panel">
      <div className="analytics-sede-header">
        <div className="sede-avatar analytics-avatar">
          {inicialesSede(sede.nombre)}
        </div>

        <div>
          <span>Dashboard individual de sede</span>
          <h2>{sede.nombre}</h2>
          <p>
            {sede.empresa_nombre || "Sin empresa"} ·{" "}
            {sede.codigo_sede || "Sin código"} · {sede.ciudad || "Sin ciudad"}
          </p>
        </div>
      </div>

      <div className="analytics-sede-grid">
        <article>
          <span>Estado operativo</span>
          <strong>{estadoTexto(sede.activo)}</strong>
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
          <span>Empleados</span>
          <strong>{empleados}</strong>
          <p>{criticidad}</p>
        </article>

        <article>
          <span>Tipo sede</span>
          <strong>{sede.tipo_sede || "PRINCIPAL"}</strong>
          <p>{sede.responsable_sede || "Sin responsable asignado"}</p>
        </article>
      </div>

      <div className="quick-actions-sedes">
        <button type="button">
          <Network size={17} />
          Ver Áreas
        </button>
        <button type="button">
          <Layers3 size={17} />
          Ver Cargos
        </button>
        <button type="button">
          <Users size={17} />
          Ver Empleados
        </button>
        <button type="button">
          <ShieldCheck size={17} />
          Matriz Peligros
        </button>
        <button type="button">
          <ClipboardList size={17} />
          Plan Anual
        </button>
      </div>
    </section>
  );
}

export default function SedesSSTPage() {
  const [sedes, setSedes] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [dashboard, setDashboard] = useState({
    total_sedes: 0,
    sedes_activas: 0,
    sedes_inactivas: 0,
    total_empleados: 0,
    total_ciudades: 0,
    ciudades: [],
    tipos_sede: {},
  });

  const [form, setForm] = useState(FORM_INICIAL);
  const [sedeSeleccionada, setSedeSeleccionada] = useState(null);
  const [sedeAnalytics, setSedeAnalytics] = useState(null);
  const [editandoId, setEditandoId] = useState(null);

  const [busqueda, setBusqueda] = useState("");
  const [filtroEmpresa, setFiltroEmpresa] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");
  const [filtroCiudad, setFiltroCiudad] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("");

  const [paginaActual, setPaginaActual] = useState(1);
  const [registrosPorPagina, setRegistrosPorPagina] = useState(10);

  const [modalFormulario, setModalFormulario] = useState(false);
  const [modalDetalle, setModalDetalle] = useState(false);
  const [modalEliminacion, setModalEliminacion] = useState({
    abierto: false,
    sede: null,
    validacion: null,
  });

  const [cargando, setCargando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [ejecutandoEliminacion, setEjecutandoEliminacion] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  const cargarDatos = async () => {
    try {
      setCargando(true);
      setError("");

      const params = {};
      if (filtroEmpresa) params.empresa_id = Number(filtroEmpresa);
      if (filtroEstado !== "") params.activo = filtroEstado === "true";
      if (filtroCiudad) params.ciudad = filtroCiudad;
      if (filtroTipo) params.tipo_sede = filtroTipo;
      if (busqueda) params.buscar = busqueda;

      const [sedesData, empresasData, dashboardData] = await Promise.all([
        listarSedesSST(params),
        listarEmpresasParaSedesSST(),
        obtenerDashboardSedesSST(
          filtroEmpresa ? { empresa_id: Number(filtroEmpresa) } : {}
        ),
      ]);

      const sedesList = Array.isArray(sedesData) ? sedesData : [];
      setSedes(sedesList);
      setEmpresas(Array.isArray(empresasData) ? empresasData : []);
      setDashboard(dashboardData || {});

      if (!sedeAnalytics && sedesList.length > 0) {
        setSedeAnalytics(sedesList[0]);
      }
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
          "No fue posible cargar las sedes. Verifica backend, token y conexión."
      );
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  useEffect(() => {
    setPaginaActual(1);
  }, [busqueda, filtroEmpresa, filtroEstado, filtroCiudad, filtroTipo]);

  const ciudadesDisponibles = useMemo(() => {
    const ciudades = sedes
      .map((sede) => sede.ciudad)
      .filter(Boolean)
      .map((ciudad) => ciudad.trim());

    return Array.from(new Set(ciudades)).sort((a, b) => a.localeCompare(b));
  }, [sedes]);

  const sedesFiltradasCliente = useMemo(() => {
    const q = busqueda.toLowerCase().trim();

    return sedes.filter((sede) => {
      const coincideBusqueda =
        !q ||
        [
          sede.nombre,
          sede.codigo_sede,
          sede.empresa_nombre,
          sede.empresa_nit,
          sede.ciudad,
          sede.departamento,
          sede.direccion,
          sede.telefono,
          sede.correo,
          sede.responsable_sede,
          sede.cargo_responsable,
          sede.tipo_sede,
        ]
          .join(" ")
          .toLowerCase()
          .includes(q);

      const coincideEmpresa =
        !filtroEmpresa || Number(sede.empresa_id) === Number(filtroEmpresa);

      const coincideEstado =
        filtroEstado === "" || String(Boolean(sede.activo)) === filtroEstado;

      const coincideCiudad =
        !filtroCiudad ||
        normalizarTexto(sede.ciudad).toLowerCase() ===
          filtroCiudad.toLowerCase();

      const coincideTipo =
        !filtroTipo ||
        normalizarTexto(sede.tipo_sede).toLowerCase() ===
          filtroTipo.toLowerCase();

      return (
        coincideBusqueda &&
        coincideEmpresa &&
        coincideEstado &&
        coincideCiudad &&
        coincideTipo
      );
    });
  }, [sedes, busqueda, filtroEmpresa, filtroEstado, filtroCiudad, filtroTipo]);

  const totalPaginas = Math.max(
    1,
    Math.ceil(sedesFiltradasCliente.length / registrosPorPagina)
  );

  const paginaSegura = Math.min(paginaActual, totalPaginas);

  const sedesPaginadas = useMemo(() => {
    const inicio = (paginaSegura - 1) * registrosPorPagina;
    const fin = inicio + registrosPorPagina;
    return sedesFiltradasCliente.slice(inicio, fin);
  }, [sedesFiltradasCliente, paginaSegura, registrosPorPagina]);

  const rangoInicio =
    sedesFiltradasCliente.length === 0
      ? 0
      : (paginaSegura - 1) * registrosPorPagina + 1;

  const rangoFin = Math.min(
    paginaSegura * registrosPorPagina,
    sedesFiltradasCliente.length
  );

  const totalEmpleadosFiltrados = useMemo(
    () =>
      sedesFiltradasCliente.reduce(
        (acc, sede) => acc + Number(sede.numero_empleados || 0),
        0
      ),
    [sedesFiltradasCliente]
  );

  const distribucionTipos = useMemo(
    () => convertirDistribucion(agruparPorCampo(sedesFiltradasCliente, "tipo_sede")),
    [sedesFiltradasCliente]
  );

  const distribucionCiudades = useMemo(
    () => convertirDistribucion(agruparPorCampo(sedesFiltradasCliente, "ciudad", "Sin ciudad")),
    [sedesFiltradasCliente]
  );

  const empleadosPorSede = useMemo(
    () =>
      sedesFiltradasCliente
        .map((sede) => ({
          label: sede.nombre || "Sin sede",
          value: Number(sede.numero_empleados || 0),
        }))
        .sort((a, b) => b.value - a.value),
    [sedesFiltradasCliente]
  );

  const empleadosPorEmpresa = useMemo(
    () =>
      convertirDistribucion(
        agruparEmpleadosPorCampo(
          sedesFiltradasCliente,
          "empresa_nombre",
          "Sin empresa"
        )
      ),
    [sedesFiltradasCliente]
  );

  const sedeMayorEmpleados = useMemo(() => {
    if (!sedesFiltradasCliente.length) return null;
    return [...sedesFiltradasCliente].sort(
      (a, b) => Number(b.numero_empleados || 0) - Number(a.numero_empleados || 0)
    )[0];
  }, [sedesFiltradasCliente]);

  const promedioEmpleados = useMemo(() => {
    if (!sedesFiltradasCliente.length) return 0;
    const total = sedesFiltradasCliente.reduce(
      (acc, sede) => acc + Number(sede.numero_empleados || 0),
      0
    );
    return Math.round(total / sedesFiltradasCliente.length);
  }, [sedesFiltradasCliente]);

  const abrirCrear = () => {
    setEditandoId(null);
    setSedeSeleccionada(null);
    setForm({
      ...FORM_INICIAL,
      empresa_id:
        filtroEmpresa ||
        (empresas.length === 1 ? String(empresas[0].id) : ""),
    });
    setModalFormulario(true);
  };

  const abrirEditar = (sede) => {
    setEditandoId(sede.id);
    setSedeSeleccionada(sede);
    setForm({
      empresa_id: sede.empresa_id || "",
      nombre: sede.nombre || "",
      codigo_sede: sede.codigo_sede || "",
      tipo_sede: sede.tipo_sede || "PRINCIPAL",
      direccion: sede.direccion || "",
      ciudad: sede.ciudad || "",
      departamento: sede.departamento || "",
      telefono: sede.telefono || "",
      correo: sede.correo || "",
      responsable_sede: sede.responsable_sede || "",
      cargo_responsable: sede.cargo_responsable || "",
      numero_empleados: sede.numero_empleados ?? 0,
      activo: Boolean(sede.activo),
    });
    setModalFormulario(true);
  };

  const abrirDetalle = (sede) => {
    setSedeSeleccionada(sede);
    setSedeAnalytics(sede);
    setModalDetalle(true);
  };

  const cerrarModales = () => {
    setModalFormulario(false);
    setModalDetalle(false);
    setEditandoId(null);
    setSedeSeleccionada(null);
    setForm(FORM_INICIAL);
  };

  const limpiarFiltros = () => {
    setBusqueda("");
    setFiltroEmpresa("");
    setFiltroEstado("");
    setFiltroCiudad("");
    setFiltroTipo("");
    setPaginaActual(1);
    setTimeout(cargarDatos, 0);
  };

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;

    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const validarFormulario = () => {
    if (!form.empresa_id) return "Selecciona la empresa.";
    if (!normalizarTexto(form.nombre)) return "El nombre de la sede es obligatorio.";
    if (Number(form.numero_empleados || 0) < 0) {
      return "El número de empleados no puede ser negativo.";
    }
    return "";
  };

  const guardarSede = async (event) => {
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
        nombre: normalizarTexto(form.nombre),
        codigo_sede: normalizarTexto(form.codigo_sede) || null,
        tipo_sede: normalizarTexto(form.tipo_sede) || "PRINCIPAL",
        direccion: normalizarTexto(form.direccion) || null,
        ciudad: normalizarTexto(form.ciudad) || null,
        departamento: normalizarTexto(form.departamento) || null,
        telefono: normalizarTexto(form.telefono) || null,
        correo: normalizarTexto(form.correo) || null,
        responsable_sede: normalizarTexto(form.responsable_sede) || null,
        cargo_responsable: normalizarTexto(form.cargo_responsable) || null,
        numero_empleados: Number(form.numero_empleados || 0),
      };

      if (editandoId) {
        await actualizarSedeSST(editandoId, {
          ...payload,
          activo: Boolean(form.activo),
        });
        setMensaje("Sede actualizada correctamente.");
      } else {
        await crearSedeSST(payload);
        setMensaje("Sede creada correctamente.");
      }

      cerrarModales();
      await cargarDatos();
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
          "No fue posible guardar la sede. Revisa los datos enviados."
      );
    } finally {
      setGuardando(false);
    }
  };

  const eliminarSedeInteligente = async (sede) => {
    try {
      setError("");
      setMensaje("");

      const validacion = await validarEliminacionSedeSST(sede.id);
      setModalEliminacion({
        abierto: true,
        sede,
        validacion,
      });
    } catch (err) {
      console.error(err);
      setError(
        obtenerMensajeErrorApi(
          err,
          "No fue posible validar la eliminación inteligente de la sede."
        )
      );
    }
  };

  const cerrarModalEliminacion = () => {
    if (ejecutandoEliminacion) return;
    setModalEliminacion({
      abierto: false,
      sede: null,
      validacion: null,
    });
  };

  const ejecutarEliminacionModal = async (modo) => {
    const sede = modalEliminacion.sede;
    if (!sede) return;

    try {
      setEjecutandoEliminacion(true);
      setError("");
      setMensaje("");

      const resultado = await eliminarInteligenteSedeSST(sede.id, {
        modo,
        confirmar: true,
      });

      if (!resultado?.success) {
        throw new Error(
          resultado?.message || "No fue posible ejecutar la eliminación inteligente."
        );
      }

      setMensaje(
        resultado.message ||
          (modo === "DELETE"
            ? "Sede eliminada definitivamente."
            : "Sede inactivada correctamente.")
      );

      setModalEliminacion({
        abierto: false,
        sede: null,
        validacion: null,
      });

      await cargarDatos();
    } catch (err) {
      console.error(err);
      setError(
        err?.message ||
          obtenerMensajeErrorApi(
            err,
            "No fue posible ejecutar la eliminación inteligente de la sede."
          )
      );
    } finally {
      setEjecutandoEliminacion(false);
    }
  };

  const alternarEstado = async (sede) => {
    try {
      setError("");
      setMensaje("");
      await cambiarEstadoSedeSST(sede.id, !sede.activo);
      setMensaje(
        sede.activo
          ? "Sede inactivada correctamente."
          : "Sede activada correctamente."
      );
      await cargarDatos();
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail || "No fue posible cambiar el estado."
      );
    }
  };

  const exportarSedes = () => {
    const filas = [
      [
        "Empresa",
        "NIT",
        "Código",
        "Sede",
        "Tipo",
        "Ciudad",
        "Departamento",
        "Dirección",
        "Teléfono",
        "Correo",
        "Responsable",
        "Cargo Responsable",
        "Empleados",
        "Estado",
      ],
      ...sedesFiltradasCliente.map((sede) => [
        sede.empresa_nombre,
        sede.empresa_nit,
        sede.codigo_sede,
        sede.nombre,
        sede.tipo_sede,
        sede.ciudad,
        sede.departamento,
        sede.direccion,
        sede.telefono,
        sede.correo,
        sede.responsable_sede,
        sede.cargo_responsable,
        sede.numero_empleados,
        estadoTexto(sede.activo),
      ]),
    ];

    descargarCSV("sedes_sst_analytics_pro.csv", filas);
  };

  const imprimirPDF = () => {
    window.print();
  };

  const kpis = [
    {
      label: "Total sedes",
      value: dashboard.total_sedes ?? sedes.length,
      icon: Building2,
      color: "blue",
      action: () => setFiltroEstado(""),
    },
    {
      label: "Activas",
      value:
        dashboard.sedes_activas ??
        sedes.filter((sede) => sede.activo).length,
      icon: CheckCircle2,
      color: "green",
      action: () => setFiltroEstado("true"),
    },
    {
      label: "Inactivas",
      value:
        dashboard.sedes_inactivas ??
        sedes.filter((sede) => !sede.activo).length,
      icon: AlertCircle,
      color: "red",
      action: () => setFiltroEstado("false"),
    },
    {
      label: "Ciudades",
      value: dashboard.total_ciudades ?? ciudadesDisponibles.length,
      icon: MapPin,
      color: "amber",
      action: () => {},
    },
    {
      label: "Empleados",
      value: dashboard.total_empleados ?? totalEmpleadosFiltrados,
      icon: Users,
      color: "purple",
      action: () =>
        setSedes((prev) =>
          [...prev].sort(
            (a, b) => Number(b.numero_empleados || 0) - Number(a.numero_empleados || 0)
          )
        ),
    },
  ];

  return (
    <main className="sedes-sst-page">
      <section className="sedes-sst-hero">
        <div className="sedes-hero-content">
          <h1>Sedes SST 360°</h1>

          <p>
            Gestiona las sedes y consulta su distribución, personal y estado SST.
          </p>
        </div>

        <div className="sedes-hero-actions">
          <button className="btn-secondary-sedes" onClick={imprimirPDF}>
            <Printer size={17} />
            Imprimir PDF
          </button>

          <button className="btn-secondary-sedes" onClick={exportarSedes}>
            <Download size={17} />
            Exportar Excel
          </button>

          <button className="btn-primary-sedes" onClick={abrirCrear}>
            <Plus size={18} />
            Nueva sede
          </button>
        </div>
      </section>

      {error && (
        <div className="sedes-sst-alert error">
          <AlertCircle size={18} />
          <span>{error}</span>
          <button onClick={() => setError("")}>
            <X size={16} />
          </button>
        </div>
      )}

      {mensaje && (
        <div className="sedes-sst-alert success">
          <CheckCircle2 size={18} />
          <span>{mensaje}</span>
          <button onClick={() => setMensaje("")}>
            <X size={16} />
          </button>
        </div>
      )}

      <section className="sedes-sst-kpis">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <button
              key={kpi.label}
              className="sede-kpi-card"
              type="button"
              onClick={kpi.action}
            >
              <div className={`kpi-icon-sedes ${kpi.color}`}>
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

      <section className="sedes-executive-grid">
        <DonutEstado
          activas={
            dashboard.sedes_activas ??
            sedesFiltradasCliente.filter((sede) => sede.activo).length
          }
          inactivas={
            dashboard.sedes_inactivas ??
            sedesFiltradasCliente.filter((sede) => !sede.activo).length
          }
        />

        <MiniBarChart
          titulo="Sedes por tipo"
          subtitulo="Distribución organizacional"
          data={distribucionTipos}
          icon={PieChart}
        />

        <MiniBarChart
          titulo="Sedes por ciudad"
          subtitulo="Cobertura geográfica"
          data={distribucionCiudades}
          icon={MapPin}
        />

        <MiniBarChart
          titulo="Empleados por empresa"
          subtitulo="Carga poblacional"
          data={empleadosPorEmpresa}
          icon={TrendingUp}
        />
      </section>

      <section className="sedes-exec-summary">
        <article>
          <div className="summary-icon">
            <Target size={20} />
          </div>
          <div>
            <span>Sede con más empleados</span>
            <strong>{sedeMayorEmpleados?.nombre || "Sin datos"}</strong>
            <p>
              {sedeMayorEmpleados
                ? `${sedeMayorEmpleados.numero_empleados || 0} empleados · ${
                    sedeMayorEmpleados.ciudad || "Sin ciudad"
                  }`
                : "No existen sedes registradas para calcular este indicador."}
            </p>
          </div>
        </article>

        <article>
          <div className="summary-icon purple">
            <BarChart3 size={20} />
          </div>
          <div>
            <span>Promedio empleados por sede</span>
            <strong>{promedioEmpleados}</strong>
            <p>Promedio calculado sobre las sedes visibles en los filtros.</p>
          </div>
        </article>

        <article>
          <div className="summary-icon amber">
            <Route size={20} />
          </div>
          <div>
            <span>Cobertura de ciudades</span>
            <strong>{ciudadesDisponibles.length}</strong>
            <p>Ciudades registradas en la estructura organizacional SST.</p>
          </div>
        </article>
      </section>

      <AnalyticsSedePanel
        sede={sedeAnalytics}
        promedioEmpleados={promedioEmpleados}
        totalEmpleados={totalEmpleadosFiltrados}
      />

      <section className="sedes-tipos-strip">
        {TIPOS_SEDE.map((tipo) => (
          <button
            key={tipo}
            type="button"
            className={`tipo-chip ${filtroTipo === tipo ? "active" : ""}`}
            onClick={() => setFiltroTipo(filtroTipo === tipo ? "" : tipo)}
          >
            {tipo}: {sedes.filter((sede) => sede.tipo_sede === tipo).length}
          </button>
        ))}
      </section>

      <section className="sedes-sst-panel">
        <div className="sedes-sst-toolbar">
          <div className="search-box-sedes">
            <Search size={18} />
            <input
              value={busqueda}
              onChange={(event) => setBusqueda(event.target.value)}
              placeholder="Buscar por sede, empresa, NIT, ciudad, responsable..."
            />
          </div>

          <div className="toolbar-actions-sedes">
            <button className="btn-secondary-sedes" onClick={limpiarFiltros}>
              <Filter size={17} />
              Limpiar
            </button>

            <button
              className="btn-secondary-sedes"
              onClick={cargarDatos}
              disabled={cargando}
            >
              <RefreshCw
                size={17}
                className={cargando ? "spin-sedes" : ""}
              />
              Actualizar
            </button>
          </div>
        </div>

        <div className="filters-grid-sedes">
          <label>
            Empresa
            <select
              value={filtroEmpresa}
              onChange={(event) => setFiltroEmpresa(event.target.value)}
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
            Ciudad
            <select
              value={filtroCiudad}
              onChange={(event) => setFiltroCiudad(event.target.value)}
            >
              <option value="">Todas</option>
              {ciudadesDisponibles.map((ciudad) => (
                <option key={ciudad} value={ciudad}>
                  {ciudad}
                </option>
              ))}
            </select>
          </label>

          <label>
            Tipo sede
            <select
              value={filtroTipo}
              onChange={(event) => setFiltroTipo(event.target.value)}
            >
              <option value="">Todas</option>
              {TIPOS_SEDE.map((tipo) => (
                <option key={tipo} value={tipo}>
                  {tipo}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="sedes-table-wrapper">
          <table className="sedes-table">
            <thead>
              <tr>
                <th>Empresa</th>
                <th>Código</th>
                <th>Sede</th>
                <th>Ubicación</th>
                <th>Contacto</th>
                <th>Responsable</th>
                <th>Empleados</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {cargando ? (
                <tr>
                  <td colSpan="10" className="empty-row-sedes">
                    <Loader2 className="spin-sedes" size={18} />
                    Cargando sedes...
                  </td>
                </tr>
              ) : sedesPaginadas.length === 0 ? (
                <tr>
                  <td colSpan="10" className="empty-row-sedes">
                    <MapPin size={18} />
                    No hay sedes para los filtros seleccionados.
                  </td>
                </tr>
              ) : (
                sedesPaginadas.map((sede) => (
                  <tr
                    key={sede.id}
                    className={
                      sedeAnalytics?.id === sede.id ? "selected-row-sedes" : ""
                    }
                  >
                    <td>
                      <div className="empresa-cell-sedes">
                        <div className="empresa-avatar-sedes">
                          <Building2 size={17} />
                        </div>
                        <div>
                          <strong>{sede.empresa_nombre || "Sin empresa"}</strong>
                          <span>NIT: {sede.empresa_nit || "—"}</span>
                        </div>
                      </div>
                    </td>

                    <td>
                      <span className="codigo-pill-sedes">
                        {sede.codigo_sede || "SIN-CÓDIGO"}
                      </span>
                    </td>

                    <td>
                      <button
                        type="button"
                        className="sede-name-button"
                        onClick={() => setSedeAnalytics(sede)}
                      >
                        <div className="sede-avatar">
                          {inicialesSede(sede.nombre)}
                        </div>
                        <div>
                          <strong>{sede.nombre}</strong>
                          <span>Creada: {formatoFecha(sede.fecha_creacion)}</span>
                        </div>
                      </button>
                    </td>

                    <td>
                      <div className="location-cell-sedes">
                        <MapPin size={15} />
                        <span>
                          {sede.ciudad || "—"}
                          {sede.departamento ? `, ${sede.departamento}` : ""}
                        </span>
                      </div>
                      <small>{sede.direccion || "Sin dirección"}</small>
                    </td>

                    <td>
                      <strong className="table-strong-sedes">
                        {sede.telefono || "—"}
                      </strong>
                      <span className="muted-sedes">{sede.correo || "—"}</span>
                    </td>

                    <td>
                      <strong className="table-strong-sedes">
                        {sede.responsable_sede || "—"}
                      </strong>
                      <span className="muted-sedes">
                        {sede.cargo_responsable || "Sin cargo"}
                      </span>
                    </td>

                    <td>
                      <span className="empleados-pill-sedes">
                        <Users size={14} />
                        {sede.numero_empleados || 0}
                      </span>
                    </td>

                    <td>
                      <span className="tipo-pill-sedes">
                        {sede.tipo_sede || "PRINCIPAL"}
                      </span>
                    </td>

                    <td>
                      <button
                        className={
                          sede.activo
                            ? "status-pill-sedes active"
                            : "status-pill-sedes inactive"
                        }
                        type="button"
                        onClick={() => alternarEstado(sede)}
                        title="Cambiar estado"
                      >
                        {estadoTexto(sede.activo)}
                      </button>
                    </td>

                    <td>
                      <div className="table-actions-sedes">
                        <button
                          className="icon-btn-sedes analytics"
                          onClick={() => setSedeAnalytics(sede)}
                          title="Analytics sede"
                        >
                          <Activity size={16} />
                        </button>

                        <button
                          className="icon-btn-sedes view"
                          onClick={() => abrirDetalle(sede)}
                          title="Ver detalle"
                        >
                          <Eye size={16} />
                        </button>

                        <button
                          className="icon-btn-sedes edit"
                          onClick={() => abrirEditar(sede)}
                          title="Editar sede"
                        >
                          <Edit3 size={16} />
                        </button>

                        <button
                          className="icon-btn-sedes delete"
                          onClick={() => eliminarSedeInteligente(sede)}
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

        <div className="pagination-sedes">
          <div className="pagination-info-sedes">
            Mostrando <strong>{rangoInicio}</strong> -{" "}
            <strong>{rangoFin}</strong> de{" "}
            <strong>{sedesFiltradasCliente.length}</strong> sedes
          </div>

          <div className="pagination-controls-sedes">
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

      <section className="sedes-executive-grid bottom">
        <MiniBarChart
          titulo="Empleados por sede"
          subtitulo="Ranking operativo"
          data={empleadosPorSede}
          icon={Users}
        />

        <article className="sedes-exec-card narrative-card">
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
            El módulo consolida <strong>{sedesFiltradasCliente.length}</strong>{" "}
            sedes visibles con <strong>{totalEmpleadosFiltrados}</strong>{" "}
            empleados asociados. La sede con mayor carga poblacional es{" "}
            <strong>{sedeMayorEmpleados?.nombre || "sin información"}</strong>.
          </p>

          <p>
            Esta información será la base para relacionar áreas, cargos,
            empleados, matrices de peligros, planes de trabajo y reportes SST
            por sede.
          </p>
        </article>
      </section>

      {modalFormulario && (
        <section className="modal-backdrop-sedes">
          <div className="modal-card-sedes enterprise-modal-sedes">
            <div className="modal-header-sedes">
              <div>
                <h2>{editandoId ? "Editar sede" : "Nueva sede SST"}</h2>
                <p>
                  Registra los datos corporativos, ubicación, contacto y
                  responsable de la sede.
                </p>
              </div>

              <button className="modal-close-sedes" onClick={cerrarModales}>
                <X size={20} />
              </button>
            </div>

            <form className="sede-form" onSubmit={guardarSede}>
              <div className="form-section-title-sedes">
                <Building2 size={18} />
                Datos generales
              </div>

              <div className="form-grid-sedes">
                <label className="form-full-sedes">
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
                  Nombre sede *
                  <input
                    name="nombre"
                    value={form.nombre}
                    onChange={handleChange}
                    placeholder="Ej: Sede Principal Yopal"
                  />
                </label>

                <label>
                  Código sede
                  <input
                    name="codigo_sede"
                    value={form.codigo_sede}
                    onChange={handleChange}
                    placeholder="Ej: YOP-001"
                  />
                </label>

                <label>
                  Tipo sede
                  <select
                    name="tipo_sede"
                    value={form.tipo_sede}
                    onChange={handleChange}
                  >
                    {TIPOS_SEDE.map((tipo) => (
                      <option key={tipo} value={tipo}>
                        {tipo}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="form-section-title-sedes">
                <MapPin size={18} />
                Ubicación
              </div>

              <div className="form-grid-sedes">
                <label className="form-full-sedes">
                  Dirección
                  <input
                    name="direccion"
                    value={form.direccion}
                    onChange={handleChange}
                    placeholder="Dirección física de la sede"
                  />
                </label>

                <label>
                  Ciudad
                  <input
                    name="ciudad"
                    value={form.ciudad}
                    onChange={handleChange}
                    placeholder="Ej: Yopal"
                  />
                </label>

                <label>
                  Departamento
                  <input
                    name="departamento"
                    value={form.departamento}
                    onChange={handleChange}
                    placeholder="Ej: Casanare"
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
              </div>

              <div className="form-section-title-sedes">
                <ClipboardList size={18} />
                Contacto y responsable
              </div>

              <div className="form-grid-sedes">
                <label>
                  Teléfono
                  <input
                    name="telefono"
                    value={form.telefono}
                    onChange={handleChange}
                    placeholder="Teléfono de contacto"
                  />
                </label>

                <label>
                  Correo
                  <input
                    type="email"
                    name="correo"
                    value={form.correo}
                    onChange={handleChange}
                    placeholder="correo@sede.com"
                  />
                </label>

                <label>
                  Responsable sede
                  <input
                    name="responsable_sede"
                    value={form.responsable_sede}
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
                    placeholder="Ej: Coordinador SST"
                  />
                </label>

                {editandoId && (
                  <label className="form-switch-sedes">
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

              <div className="modal-actions-sedes sticky-actions-sedes">
                <button
                  type="button"
                  className="btn-secondary-sedes"
                  onClick={cerrarModales}
                >
                  Cancelar
                </button>

                <button
                  type="submit"
                  className="btn-primary-sedes"
                  disabled={guardando}
                >
                  {guardando ? (
                    <Loader2 className="spin-sedes" size={17} />
                  ) : (
                    <Save size={17} />
                  )}
                  {guardando ? "Guardando..." : "Guardar sede"}
                </button>
              </div>
            </form>
          </div>
        </section>
      )}

      {modalDetalle && sedeSeleccionada && (
        <section className="modal-backdrop-sedes">
          <div className="modal-card-sedes detail-modal-sedes">
            <div className="modal-header-sedes detail-header-sedes">
              <div className="detail-title-sedes">
                <div className="sede-avatar large">
                  {inicialesSede(sedeSeleccionada.nombre)}
                </div>
                <div>
                  <h2>{sedeSeleccionada.nombre}</h2>
                  <p>
                    {sedeSeleccionada.empresa_nombre || "Sin empresa"} ·{" "}
                    {sedeSeleccionada.codigo_sede || "Sin código"}
                  </p>
                </div>
              </div>

              <button className="modal-close-sedes" onClick={cerrarModales}>
                <X size={20} />
              </button>
            </div>

            <AnalyticsSedePanel
              sede={sedeSeleccionada}
              promedioEmpleados={promedioEmpleados}
              totalEmpleados={totalEmpleadosFiltrados}
            />

            <div className="detail-grid-sedes">
              <article>
                <span>Empresa</span>
                <strong>{sedeSeleccionada.empresa_nombre || "—"}</strong>
              </article>

              <article>
                <span>NIT</span>
                <strong>{sedeSeleccionada.empresa_nit || "—"}</strong>
              </article>

              <article>
                <span>Estado</span>
                <strong>{estadoTexto(sedeSeleccionada.activo)}</strong>
              </article>

              <article>
                <span>Tipo sede</span>
                <strong>{sedeSeleccionada.tipo_sede || "PRINCIPAL"}</strong>
              </article>

              <article>
                <span>Ciudad</span>
                <strong>
                  {sedeSeleccionada.ciudad || "—"}
                  {sedeSeleccionada.departamento
                    ? `, ${sedeSeleccionada.departamento}`
                    : ""}
                </strong>
              </article>

              <article>
                <span>Empleados</span>
                <strong>{sedeSeleccionada.numero_empleados || 0}</strong>
              </article>

              <article className="wide">
                <span>Dirección</span>
                <strong>{sedeSeleccionada.direccion || "—"}</strong>
              </article>

              <article>
                <span>Teléfono</span>
                <strong>{sedeSeleccionada.telefono || "—"}</strong>
              </article>

              <article>
                <span>Correo</span>
                <strong>{sedeSeleccionada.correo || "—"}</strong>
              </article>

              <article>
                <span>Responsable</span>
                <strong>{sedeSeleccionada.responsable_sede || "—"}</strong>
              </article>

              <article>
                <span>Cargo responsable</span>
                <strong>{sedeSeleccionada.cargo_responsable || "—"}</strong>
              </article>

              <article>
                <span>Fecha creación</span>
                <strong>{formatoFecha(sedeSeleccionada.fecha_creacion)}</strong>
              </article>
            </div>

            <div className="modal-actions-sedes">
              <button
                className="btn-secondary-sedes"
                onClick={() => {
                  setModalDetalle(false);
                  abrirEditar(sedeSeleccionada);
                }}
              >
                <Edit3 size={17} />
                Editar
              </button>

              <button className="btn-primary-sedes" onClick={cerrarModales}>
                Cerrar
              </button>
            </div>
          </div>
        </section>
      )}

      <EliminacionInteligenteModal
        abierto={modalEliminacion.abierto}
        entidad="sede"
        registroNombre={modalEliminacion.sede?.nombre || "Sede seleccionada"}
        validacion={modalEliminacion.validacion}
        ejecutando={ejecutandoEliminacion}
        onCancelar={cerrarModalEliminacion}
        onEliminar={() => ejecutarEliminacionModal("DELETE")}
        onInactivar={() => ejecutarEliminacionModal("INACTIVATE")}
      />
    </main>
  );
}
