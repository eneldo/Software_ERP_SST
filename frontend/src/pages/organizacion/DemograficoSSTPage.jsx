
import React, { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Users,
  Search,
  Filter,
  RefreshCw,
  Eye,
  Pencil,
  Trash2,
  Download,
  Upload,
  FileText,
  ChevronLeft,
  ChevronRight,
  X,
  AlertCircle,
  CheckCircle,
  Building2,
  Loader2,
  Plus,
  Minus,
  CalendarDays,
  ClipboardCheck,
  FileSpreadsheet,
  MapPin,
  Percent,
  UserCheck,
  UserMinus,
} from "lucide-react";

import {
  listarPerfilesSociodemograficos,
  obtenerPerfilSociodemografico,
  eliminarPerfilSociodemografico,
  exportarPerfilesExcel,
  descargarPlantillaExcel,
  importarPerfilExcel,
  crearPerfilSociodemografico,
  actualizarPerfilSociodemografico,
  obtenerDashboardPerfilSociodemografico,
  exportarDashboardPerfilExcel,
  exportarDashboardPerfilPdf,
} from "../../api/empleadoPerfilApi";
import { listarEmpresasSST } from "../../api/empresaSstApi";
import { listarEmpleados } from "../../api/empleadoSstApi";
import { listarSedesSST } from "../../api/sedeSstApi";
import { getStoredUser } from "../../utils/security";

import "../../styles/organizacion-common.css";

const formatearFecha = (fecha) => {
  if (!fecha) return "—";
  const partes = String(fecha).split("T")[0].split("-");
  if (partes.length !== 3) return fecha;
  return `${partes[2]}/${partes[1]}/${partes[0]}`;
};

const valorOSiNo = (valor) => {
  if (valor === null || valor === undefined || valor === "") return "—";
  if (typeof valor === "boolean") return valor ? "Sí" : "No";
  return String(valor);
};

const calcularEdad = (fechaNacimiento) => {
  if (!fechaNacimiento) return null;
  const hoy = new Date();
  const nacimiento = new Date(fechaNacimiento);
  if (isNaN(nacimiento.getTime())) return null;
  let edad = hoy.getFullYear() - nacimiento.getFullYear();
  const mesActual = hoy.getMonth();
  const diaActual = hoy.getDate();
  if (mesActual < nacimiento.getMonth() || (mesActual === nacimiento.getMonth() && diaActual < nacimiento.getDate())) {
    edad--;
  }
  return edad >= 0 ? edad : null;
};

const obtenerNombreEmpresa = (perfil, empresas) => {
  if (perfil.empresa_nombre) return perfil.empresa_nombre;
  const emp = empresas.find((e) => e.id === perfil.empresa_id);
  return emp ? emp.nombre : "—";
};

const ESTADO_INICIAL_FORM = {
  nombres_completos: "",
  tipo_documento: "CC",
  numero_documento: "",
  libreta_militar: "",
  fecha_nacimiento: "",
  lugar_nacimiento: "",
  edad: null,
  raza_pertenencia_etnica: "",
  telefono_celular: "",
  estado_civil: "",
  conyuge_nombre: "",
  conyuge_ocupacion: "",
  conyuge_edad: null,
  conyuge_celular: "",
  numero_dependientes: null,
  hijos: [],
  direccion_residencia: "",
  barrio: "",
  ciudad_municipio: "",
  estrato_socioeconomico: null,
  tipo_vivienda: "",
  servicios_vivienda: [],
  medio_transporte: "",
  medio_transporte_otro: "",
  tiempo_desplazamiento: "",
  cargo_actual: "",
  area_departamento: "",
  sede_centro_trabajo: "",
  tipo_contrato: "",
  tiempo_laborado: "",
  antiguedad_cargo: "",
  ultima_empresa: "",
  nivel_escolaridad: "",
  detalle_titulos: "",
  eps_actual: "",
  fondo_pensiones: "",
  tipo_rh: "",
  diagnostico_previo: false,
  diagnostico_detalle: "",
  actividad_fisica: "",
  consumo_cigarrillo: "",
  consumo_alcohol: "",
  talla_camisa: "",
  talla_pantalon: "",
  talla_chaqueta: "",
  talla_overol: "",
  talla_calzado: "",
  referencia_1_nombre: "",
  referencia_1_ocupacion: "",
  referencia_1_telefono: "",
  referencia_2_nombre: "",
  referencia_2_ocupacion: "",
  referencia_2_telefono: "",
  consentimiento_informado: false,
  fecha_firma: "",
  completado: false,
};

const SECCIONES = [
  "Identificación",
  "Sociodemográficas",
  "Vivienda",
  "Laboral",
  "Salud",
  "Referencias",
  "Consentimiento",
];

const ANIO_ACTUAL = new Date().getFullYear();
const MESES = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
];

const DASHBOARD_VACIO = {
  periodo: null,
  kpis: {
    total_periodo: 0,
    activos: 0,
    inactivos: 0,
    perfiles_registrados: 0,
    perfiles_completados: 0,
    cobertura_perfil: 0,
    sin_fecha_ingreso: 0,
    datos_historicos_incompletos: 0,
  },
  tendencia_mensual: [],
  por_sede: [],
};

function normalizarLista(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

function DashboardKpi({ icon: Icon, label, value, suffix = "", tone = "blue" }) {
  return (
    <article className={`demografico-dashboard-kpi tone-${tone}`}>
      <span className="demografico-dashboard-kpi-icon"><Icon size={18} aria-hidden="true" /></span>
      <div>
        <span>{label}</span>
        <strong>{value ?? 0}{suffix}</strong>
      </div>
    </article>
  );
}

export default function DemograficoSSTPage() {
  const [perfiles, setPerfiles] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  const [modalDetalle, setModalDetalle] = useState(false);
  const [perfilDetalle, setPerfilDetalle] = useState(null);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);

  const [modalEliminar, setModalEliminar] = useState(false);
  const [perfilEliminar, setPerfilEliminar] = useState(null);
  const [eliminando, setEliminando] = useState(false);

  const [modalImportar, setModalImportar] = useState(false);
  const [archivoImportar, setArchivoImportar] = useState(null);
  const [importando, setImportando] = useState(false);

  const [modalEmpleado, setModalEmpleado] = useState(false);
  const [empleados, setEmpleados] = useState([]);
  const [cargandoEmpleados, setCargandoEmpleados] = useState(false);
  const [busquedaEmpleado, setBusquedaEmpleado] = useState("");

  const [modalFormulario, setModalFormulario] = useState(false);
  const [perfilEditando, setPerfilEditando] = useState(null);
  const [seccionActiva, setSeccionActiva] = useState(1);
  const [guardando, setGuardando] = useState(false);
  const [form, setForm] = useState({ ...ESTADO_INICIAL_FORM });
  const [empleadoSeleccionado, setEmpleadoSeleccionado] = useState(null);

  const [filtros, setFiltros] = useState(() => ({
    buscar: "",
    empresa_id: String(getStoredUser()?.empresa_id || ""),
    sede_id: "",
    anio: String(ANIO_ACTUAL),
    mes: "",
  }));
  const [dashboard, setDashboard] = useState(DASHBOARD_VACIO);
  const [cargandoDashboard, setCargandoDashboard] = useState(false);
  const [errorDashboard, setErrorDashboard] = useState("");
  const [exportandoDashboard, setExportandoDashboard] = useState("");
  const [dashboardVersion, setDashboardVersion] = useState(0);
  const [pagina, setPagina] = useState(1);
  const [porPagina] = useState(10);

  const cargarEmpresas = async () => {
    try {
      const data = await listarEmpresasSST();
      setEmpresas(data);
      setFiltros((prev) => (
        prev.empresa_id || !data[0]?.id
          ? prev
          : { ...prev, empresa_id: String(data[0].id) }
      ));
    } catch (err) {
      console.error(err);
    }
  };

  const cargarPerfiles = async () => {
    setCargando(true);
    setError("");
    try {
      const params = {};
      if (filtros.empresa_id) params.empresa_id = filtros.empresa_id;
      const data = await listarPerfilesSociodemograficos(params);
      setPerfiles(Array.isArray(data) ? data : []);
      setPagina(1);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudieron cargar los perfiles sociodemográficos.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarEmpresas();
  }, []);

  useEffect(() => {
    cargarPerfiles();
  }, [filtros.empresa_id]);

  useEffect(() => {
    let activo = true;
    if (!filtros.empresa_id) {
      setSedes([]);
      return undefined;
    }
    listarSedesSST({ empresa_id: filtros.empresa_id })
      .then((data) => {
        if (activo) {
          setSedes(normalizarLista(data).filter(
            (sede) => Number(sede.empresa_id) === Number(filtros.empresa_id),
          ));
        }
      })
      .catch((err) => {
        console.error(err);
        if (activo) setSedes([]);
      });
    return () => { activo = false; };
  }, [filtros.empresa_id]);

  useEffect(() => {
    let activo = true;
    if (!filtros.empresa_id || !/^\d{4}$/.test(filtros.anio)) {
      setDashboard(DASHBOARD_VACIO);
      setErrorDashboard("");
      return undefined;
    }

    setCargandoDashboard(true);
    setErrorDashboard("");
    obtenerDashboardPerfilSociodemografico({
      empresa_id: Number(filtros.empresa_id),
      sede_id: filtros.sede_id ? Number(filtros.sede_id) : undefined,
      anio: Number(filtros.anio),
      mes: filtros.mes ? Number(filtros.mes) : undefined,
    })
      .then((data) => {
        if (!activo) return;
        setDashboard({
          ...DASHBOARD_VACIO,
          ...(data || {}),
          kpis: { ...DASHBOARD_VACIO.kpis, ...(data?.kpis || {}) },
          tendencia_mensual: Array.isArray(data?.tendencia_mensual) ? data.tendencia_mensual : [],
          por_sede: Array.isArray(data?.por_sede) ? data.por_sede : [],
        });
      })
      .catch((err) => {
        console.error(err);
        if (activo) {
          setDashboard(DASHBOARD_VACIO);
          setErrorDashboard(err?.response?.data?.detail || "No se pudo cargar el dashboard del periodo.");
        }
      })
      .finally(() => {
        if (activo) setCargandoDashboard(false);
      });

    return () => { activo = false; };
  }, [filtros.empresa_id, filtros.sede_id, filtros.anio, filtros.mes, dashboardVersion]);

  const perfilesFiltrados = useMemo(() => {
    const texto = filtros.buscar.toLowerCase().trim();
    if (!texto) return perfiles;
    return perfiles.filter((perfil) => {
      const campos = [
        perfil.nombres_completos,
        perfil.numero_documento,
        perfil.tipo_documento,
        perfil.nombre_empleado,
        perfil.empleado_nombre,
      ];
      return campos
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(texto);
    });
  }, [perfiles, filtros.buscar]);

  const totalPaginas = Math.max(1, Math.ceil(perfilesFiltrados.length / porPagina));
  const inicio = (pagina - 1) * porPagina;
  const perfilesPagina = perfilesFiltrados.slice(inicio, inicio + porPagina);

  const cargarEmpleados = async () => {
    setCargandoEmpleados(true);
    try {
      const params = {};
      if (filtros.empresa_id) params.empresa_id = filtros.empresa_id;
      const data = await listarEmpleados(params);
      setEmpleados(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudieron cargar los empleados.");
    } finally {
      setCargandoEmpleados(false);
    }
  };

  const abrirModalEmpleado = () => {
    setBusquedaEmpleado("");
    setModalEmpleado(true);
    cargarEmpleados();
  };

  const seleccionarEmpleado = (empleado) => {
    setPerfilEditando(null);
    setSeccionActiva(1);
    setEmpleadoSeleccionado(empleado);
    const nombreCompleto = `${empleado.nombres || ""} ${empleado.apellidos || ""}`.trim();
    setForm({
      ...ESTADO_INICIAL_FORM,
      nombres_completos: nombreCompleto,
      tipo_documento: empleado.tipo_documento || "CC",
      numero_documento: empleado.documento || "",
      fecha_nacimiento: empleado.fecha_nacimiento || "",
      edad: calcularEdad(empleado.fecha_nacimiento),
      telefono_celular: empleado.telefono || "",
      cargo_actual: empleado.cargo_nombre || "",
      area_departamento: empleado.area_nombre || "",
      sede_centro_trabajo: empleado.sede_nombre || "",
    });
    setModalEmpleado(false);
    setModalFormulario(true);
  };

  const abrirFormularioCrear = () => {
    setPerfilEditando(null);
    setSeccionActiva(1);
    setEmpleadoSeleccionado(null);
    setForm({ ...ESTADO_INICIAL_FORM });
    setModalFormulario(true);
  };

  const abrirFormularioEditar = (perfil) => {
    setPerfilEditando(perfil);
    setSeccionActiva(1);
    setEmpleadoSeleccionado(null);
    const datos = { ...ESTADO_INICIAL_FORM };
    const campos = Object.keys(datos);
    campos.forEach((campo) => {
      if (perfil[campo] !== undefined && perfil[campo] !== null) {
        datos[campo] = perfil[campo];
      }
    });
    if (typeof datos.servicios_vivienda === "string") {
      datos.servicios_vivienda = datos.servicios_vivienda
        ? datos.servicios_vivienda.split(",").map((s) => s.trim())
        : [];
    }
    if (!Array.isArray(datos.hijos)) {
      datos.hijos = [];
    }
    datos.edad = calcularEdad(datos.fecha_nacimiento);
    datos.hijos = datos.hijos.map((h) => ({
      ...h,
      edad: h.edad ?? calcularEdad(h.fecha_nacimiento),
    }));
    setForm(datos);
    setModalFormulario(true);
  };

  const cerrarFormulario = () => {
    setModalFormulario(false);
    setPerfilEditando(null);
    setEmpleadoSeleccionado(null);
    setSeccionActiva(1);
    setForm({ ...ESTADO_INICIAL_FORM });
  };

  const manejarCambio = (seccion, campo, valor) => {
    setForm((prev) => ({ ...prev, [campo]: valor }));
  };

  const agregarHijo = () => {
    setForm((prev) => ({
      ...prev,
      hijos: [...(prev.hijos || []), { nombre: "", fecha_nacimiento: "", edad: null, escolaridad: "" }],
    }));
  };

  const eliminarHijo = (index) => {
    setForm((prev) => ({
      ...prev,
      hijos: prev.hijos.filter((_, i) => i !== index),
    }));
  };

  const cambiarHijo = (index, campo, valor) => {
    setForm((prev) => {
      const hijos = [...prev.hijos];
      const hijoActualizado = { ...hijos[index], [campo]: valor };
      if (campo === "fecha_nacimiento") {
        hijoActualizado.edad = calcularEdad(valor);
      }
      hijos[index] = hijoActualizado;
      return { ...prev, hijos };
    });
  };

  const toggleServicioVivienda = (servicio) => {
    setForm((prev) => {
      const actual = prev.servicios_vivienda || [];
      if (actual.includes(servicio)) {
        return { ...prev, servicios_vivienda: actual.filter((s) => s !== servicio) };
      }
      return { ...prev, servicios_vivienda: [...actual, servicio] };
    });
  };

  const guardarPerfil = async () => {
    if (!form.nombres_completos?.trim()) {
      setError("El nombre completo es obligatorio.");
      return;
    }
    setGuardando(true);
    setError("");
    setMensaje("");
    try {
      const payload = { ...form };
      if (empleadoSeleccionado && !perfilEditando) {
        payload.empleado_id = empleadoSeleccionado.id;
      }
      if (perfilEditando) {
        payload.empresa_id = perfilEditando.empresa_id;
        const empleadoId = perfilEditando.empleado_id || perfilEditando.id;
        await actualizarPerfilSociodemografico(empleadoId, payload, perfilEditando.empresa_id);
        setMensaje("Perfil actualizado correctamente.");
      } else {
        await crearPerfilSociodemografico(payload);
        setMensaje("Perfil creado correctamente.");
      }
      cerrarFormulario();
      await cargarPerfiles();
      setDashboardVersion((version) => version + 1);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudo guardar el perfil.");
    } finally {
      setGuardando(false);
    }
  };

  const empleadosFiltrados = useMemo(() => {
    const texto = busquedaEmpleado.toLowerCase().trim();
    if (!texto) return empleados;
    return empleados.filter((emp) => {
      const nombreCompleto = `${emp.nombres || ""} ${emp.apellidos || ""}`.trim();
      const campos = [nombreCompleto, emp.documento, emp.cargo_nombre, emp.correo];
      return campos.filter(Boolean).join(" ").toLowerCase().includes(texto);
    });
  }, [empleados, busquedaEmpleado]);

  const abrirDetalle = async (perfil) => {
    setModalDetalle(true);
    setCargandoDetalle(true);
    setPerfilDetalle(null);
    try {
      const empleadoId = perfil.empleado_id || perfil.id;
      const empresaId = perfil.empresa_id || filtros.empresa_id || undefined;
      const data = await obtenerPerfilSociodemografico(empleadoId, empresaId);
      setPerfilDetalle(data);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudo cargar el detalle del perfil.");
      setModalDetalle(false);
    } finally {
      setCargandoDetalle(false);
    }
  };

  const cerrarDetalle = () => {
    setModalDetalle(false);
    setPerfilDetalle(null);
  };

  const confirmarEliminar = (perfil) => {
    setPerfilEliminar(perfil);
    setModalEliminar(true);
  };

  const cerrarEliminar = () => {
    setModalEliminar(false);
    setPerfilEliminar(null);
  };

  const ejecutarEliminar = async () => {
    if (!perfilEliminar) return;
    setEliminando(true);
    setError("");
    setMensaje("");
    try {
      const empleadoId = perfilEliminar.empleado_id || perfilEliminar.id;
      const empresaId = perfilEliminar.empresa_id || filtros.empresa_id || undefined;
      await eliminarPerfilSociodemografico(empleadoId, empresaId);
      setMensaje("Perfil eliminado correctamente.");
      cerrarEliminar();
      await cargarPerfiles();
      setDashboardVersion((version) => version + 1);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudo eliminar el perfil.");
    } finally {
      setEliminando(false);
    }
  };

  const exportarExcel = async () => {
    setError("");
    setMensaje("");
    try {
      const params = {};
      if (filtros.empresa_id) params.empresa_id = filtros.empresa_id;
      await exportarPerfilesExcel(params);
      setMensaje("Archivo Excel exportado correctamente.");
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudo exportar el archivo Excel.");
    }
  };

  const parametrosDashboard = () => ({
    empresa_id: Number(filtros.empresa_id),
    sede_id: filtros.sede_id ? Number(filtros.sede_id) : undefined,
    anio: Number(filtros.anio),
    mes: filtros.mes ? Number(filtros.mes) : undefined,
  });

  const exportarDashboard = async (formato) => {
    if (!filtros.empresa_id || !/^\d{4}$/.test(filtros.anio)) {
      setErrorDashboard("Selecciona una empresa y un año para exportar el dashboard.");
      return;
    }
    setExportandoDashboard(formato);
    setErrorDashboard("");
    try {
      if (formato === "excel") {
        await exportarDashboardPerfilExcel(parametrosDashboard());
      } else {
        await exportarDashboardPerfilPdf(parametrosDashboard());
      }
      setMensaje(`Dashboard ${formato === "excel" ? "Excel" : "PDF"} exportado correctamente.`);
    } catch (err) {
      console.error(err);
      setErrorDashboard(`No se pudo exportar el dashboard en ${formato === "excel" ? "Excel" : "PDF"}.`);
    } finally {
      setExportandoDashboard("");
    }
  };

  const actualizarPagina = () => {
    cargarPerfiles();
    setDashboardVersion((version) => version + 1);
  };

  const descargarPlantilla = async () => {
    setError("");
    setMensaje("");
    try {
      await descargarPlantillaExcel();
      setMensaje("Plantilla descargada correctamente.");
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudo descargar la plantilla.");
    }
  };

  const abrirImportar = () => {
    setArchivoImportar(null);
    setModalImportar(true);
  };

  const cerrarImportar = () => {
    setModalImportar(false);
    setArchivoImportar(null);
  };

  const ejecutarImportar = async () => {
    if (!archivoImportar) {
      setError("Selecciona un archivo Excel para importar.");
      return;
    }
    const empresaId = filtros.empresa_id || empresas[0]?.id;
    if (!empresaId) {
      setError("Selecciona una empresa antes de importar.");
      return;
    }
    setImportando(true);
    setError("");
    setMensaje("");
    try {
      const resultado = await importarPerfilExcel(archivoImportar, empresaId);
      setMensaje(resultado?.mensaje || "Importación completada correctamente.");
      cerrarImportar();
      await cargarPerfiles();
      setDashboardVersion((version) => version + 1);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No se pudo importar el archivo.");
    } finally {
      setImportando(false);
    }
  };

  const limpiarFiltros = () => {
    setFiltros((prev) => ({
      ...prev,
      buscar: "",
      sede_id: "",
      anio: String(ANIO_ACTUAL),
      mes: "",
    }));
  };

  const renderSeccionIdentificacion = () => (
    <div className="demografico-form-section">
      <h4>1. Identificación</h4>
      <div className="demografico-form-grid">
        <div className="demografico-form-field">
          <label>Nombres completos *</label>
          <input
            type="text"
            value={form.nombres_completos}
            onChange={(e) => manejarCambio(1, "nombres_completos", e.target.value)}
            placeholder="Nombres completos"
          />
        </div>
        <div className="demografico-form-field">
          <label>Tipo de documento</label>
          <select value={form.tipo_documento} onChange={(e) => manejarCambio(1, "tipo_documento", e.target.value)}>
            <option value="CC">Cédula de Ciudadanía</option>
            <option value="CE">Cédula de Extranjería</option>
            <option value="TI">Tarjeta de Identidad</option>
            <option value="PASAPORTE">Pasaporte</option>
          </select>
        </div>
        <div className="demografico-form-field">
          <label>Número de documento</label>
          <input
            type="text"
            value={form.numero_documento}
            onChange={(e) => manejarCambio(1, "numero_documento", e.target.value)}
            placeholder="Número de documento"
          />
        </div>
        <div className="demografico-form-field">
          <label>Libreta militar</label>
          <input
            type="text"
            value={form.libreta_militar}
            onChange={(e) => manejarCambio(1, "libreta_militar", e.target.value)}
            placeholder="Libreta militar"
          />
        </div>
        <div className="demografico-form-field">
          <label>Fecha de nacimiento</label>
          <input
            type="date"
            value={form.fecha_nacimiento}
            onChange={(e) => {
              const fecha = e.target.value;
              setForm((prev) => ({
                ...prev,
                fecha_nacimiento: fecha,
                edad: calcularEdad(fecha),
              }));
            }}
          />
        </div>
        <div className="demografico-form-field">
          <label>Lugar de nacimiento</label>
          <input
            type="text"
            value={form.lugar_nacimiento}
            onChange={(e) => manejarCambio(1, "lugar_nacimiento", e.target.value)}
            placeholder="Lugar de nacimiento"
          />
        </div>
        <div className="demografico-form-field">
          <label>Edad</label>
          <input
            type="number"
            value={form.edad ?? ""}
            readOnly
            placeholder="Edad"
            style={{ backgroundColor: "#f1f5f9", cursor: "not-allowed" }}
          />
        </div>
        <div className="demografico-form-field">
          <label>Raza / Pertenencia étnica</label>
          <input
            type="text"
            value={form.raza_pertenencia_etnica}
            onChange={(e) => manejarCambio(1, "raza_pertenencia_etnica", e.target.value)}
            placeholder="Raza / pertenencia étnica"
          />
        </div>
        <div className="demografico-form-field">
          <label>Teléfono celular</label>
          <input
            type="text"
            value={form.telefono_celular}
            onChange={(e) => manejarCambio(1, "telefono_celular", e.target.value)}
            placeholder="Teléfono celular"
          />
        </div>
      </div>
    </div>
  );

  const renderSeccionSociodemograficas = () => (
    <div className="demografico-form-section">
      <h4>2. Información Sociodemográfica</h4>
      <div className="demografico-form-grid">
        <div className="demografico-form-field">
          <label>Estado civil</label>
          <select value={form.estado_civil} onChange={(e) => manejarCambio(2, "estado_civil", e.target.value)}>
            <option value="">Seleccionar...</option>
            <option value="Soltero(a)">Soltero(a)</option>
            <option value="Casado(a)">Casado(a)</option>
            <option value="Unión libre">Unión libre</option>
            <option value="Separado(a)/Divorciado(a)">Separado(a)/Divorciado(a)</option>
            <option value="Viudo(a)">Viudo(a)</option>
          </select>
        </div>
        <div className="demografico-form-field">
          <label>Número de dependientes</label>
          <input
            type="number"
            value={form.numero_dependientes ?? ""}
            onChange={(e) => manejarCambio(2, "numero_dependientes", e.target.value ? Number(e.target.value) : null)}
            placeholder="Número de dependientes"
          />
        </div>
        <div className="demografico-form-field">
          <label>Nombre del cónyuge</label>
          <input
            type="text"
            value={form.conyuge_nombre}
            onChange={(e) => manejarCambio(2, "conyuge_nombre", e.target.value)}
            placeholder="Nombre del cónyuge"
          />
        </div>
        <div className="demografico-form-field">
          <label>Ocupación del cónyuge</label>
          <input
            type="text"
            value={form.conyuge_ocupacion}
            onChange={(e) => manejarCambio(2, "conyuge_ocupacion", e.target.value)}
            placeholder="Ocupación del cónyuge"
          />
        </div>
        <div className="demografico-form-field">
          <label>Edad del cónyuge</label>
          <input
            type="number"
            value={form.conyuge_edad ?? ""}
            onChange={(e) => manejarCambio(2, "conyuge_edad", e.target.value ? Number(e.target.value) : null)}
            placeholder="Edad del cónyuge"
          />
        </div>
        <div className="demografico-form-field">
          <label>Celular del cónyuge</label>
          <input
            type="text"
            value={form.conyuge_celular}
            onChange={(e) => manejarCambio(2, "conyuge_celular", e.target.value)}
            placeholder="Celular del cónyuge"
          />
        </div>
      </div>
      <div className="demografico-form-hijos">
        <div className="demografico-form-hijos-header">
          <h5>Hijos / Dependientes</h5>
          <button className="btn-secondary-sst btn-sm" onClick={agregarHijo} type="button">
            <Plus size={14} /> Agregar hijo
          </button>
        </div>
        {form.hijos && form.hijos.length > 0 ? (
          form.hijos.map((hijo, idx) => (
            <div key={idx} className="demografico-form-hijo-row">
              <div className="demografico-form-field">
                <label>Nombre</label>
                <input
                  type="text"
                  value={hijo.nombre}
                  onChange={(e) => cambiarHijo(idx, "nombre", e.target.value)}
                  placeholder="Nombre del hijo"
                />
              </div>
              <div className="demografico-form-field">
                <label>Fecha nacimiento</label>
                <input
                  type="date"
                  value={hijo.fecha_nacimiento || ""}
                  onChange={(e) => cambiarHijo(idx, "fecha_nacimiento", e.target.value)}
                />
              </div>
                  <div className="demografico-form-field">
                    <label>Edad</label>
                    <input
                      type="number"
                      value={hijo.edad ?? ""}
                      readOnly
                      placeholder="Edad"
                      style={{ backgroundColor: "#f1f5f9", cursor: "not-allowed" }}
                    />
                  </div>
              <div className="demografico-form-field">
                <label>Escolaridad</label>
                <input
                  type="text"
                  value={hijo.escolaridad}
                  onChange={(e) => cambiarHijo(idx, "escolaridad", e.target.value)}
                  placeholder="Escolaridad"
                />
              </div>
              <button className="demografico-icon-btn delete" onClick={() => eliminarHijo(idx)} title="Eliminar hijo" type="button">
                <Trash2 size={14} />
              </button>
            </div>
          ))
        ) : (
          <p className="demografico-empty-hijos">No hay hijos registrados.</p>
        )}
      </div>
    </div>
  );

  const renderSeccionVivienda = () => (
    <div className="demografico-form-section">
      <h4>3. Vivienda</h4>
      <div className="demografico-form-grid">
        <div className="demografico-form-field demografico-field-wide">
          <label>Dirección de residencia</label>
          <input
            type="text"
            value={form.direccion_residencia}
            onChange={(e) => manejarCambio(3, "direccion_residencia", e.target.value)}
            placeholder="Dirección de residencia"
          />
        </div>
        <div className="demografico-form-field">
          <label>Barrio</label>
          <input
            type="text"
            value={form.barrio}
            onChange={(e) => manejarCambio(3, "barrio", e.target.value)}
            placeholder="Barrio"
          />
        </div>
        <div className="demografico-form-field">
          <label>Ciudad / Municipio</label>
          <input
            type="text"
            value={form.ciudad_municipio}
            onChange={(e) => manejarCambio(3, "ciudad_municipio", e.target.value)}
            placeholder="Ciudad / Municipio"
          />
        </div>
        <div className="demografico-form-field">
          <label>Estrato socioeconómico</label>
          <select
            value={form.estrato_socioeconomico ?? ""}
            onChange={(e) => manejarCambio(3, "estrato_socioeconomico", e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">Seleccionar...</option>
            <option value={1}>1</option>
            <option value={2}>2</option>
            <option value={3}>3</option>
            <option value={4}>4</option>
            <option value={5}>5</option>
            <option value={6}>6</option>
          </select>
        </div>
        <div className="demografico-form-field">
          <label>Tipo de vivienda</label>
          <select value={form.tipo_vivienda} onChange={(e) => manejarCambio(3, "tipo_vivienda", e.target.value)}>
            <option value="">Seleccionar...</option>
            <option value="Propia">Propia</option>
            <option value="Arrendada">Arrendada</option>
            <option value="Familiar">Familiar</option>
          </select>
        </div>
        <div className="demografico-form-field demografico-field-wide">
          <label>Servicios de vivienda</label>
          <div className="demografico-form-checkboxes">
            {["Acueducto", "Alcantarillado", "Energía eléctrica", "Gas natural"].map((servicio) => (
              <label key={servicio} className="demografico-checkbox-label">
                <input
                  type="checkbox"
                  checked={(form.servicios_vivienda || []).includes(servicio)}
                  onChange={() => toggleServicioVivienda(servicio)}
                />
                {servicio}
              </label>
            ))}
          </div>
        </div>
        <div className="demografico-form-field">
          <label>Medio de transporte</label>
          <select value={form.medio_transporte} onChange={(e) => manejarCambio(3, "medio_transporte", e.target.value)}>
            <option value="">Seleccionar...</option>
            <option value="Transporte público">Transporte público</option>
            <option value="Vehículo particular">Vehículo particular</option>
            <option value="Motocicleta">Motocicleta</option>
            <option value="Bicicleta/Patineta">Bicicleta/Patineta</option>
            <option value="A pie">A pie</option>
            <option value="Otro">Otro</option>
          </select>
        </div>
        {form.medio_transporte === "Otro" && (
          <div className="demografico-form-field">
            <label>Otro medio de transporte</label>
            <input
              type="text"
              value={form.medio_transporte_otro}
              onChange={(e) => manejarCambio(3, "medio_transporte_otro", e.target.value)}
              placeholder="Especifique el medio de transporte"
            />
          </div>
        )}
        <div className="demografico-form-field">
          <label>Tiempo de desplazamiento</label>
          <select value={form.tiempo_desplazamiento} onChange={(e) => manejarCambio(3, "tiempo_desplazamiento", e.target.value)}>
            <option value="">Seleccionar...</option>
            <option value="Menos de 30 min">Menos de 30 min</option>
            <option value="30 a 60 min">30 a 60 min</option>
            <option value="1 a 2 horas">1 a 2 horas</option>
            <option value="Más de 2 horas">Más de 2 horas</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderSeccionLaboral = () => (
    <div className="demografico-form-section">
      <h4>4. Información Laboral</h4>
      <div className="demografico-form-grid">
        <div className="demografico-form-field">
          <label>Cargo actual</label>
          <input
            type="text"
            value={form.cargo_actual}
            onChange={(e) => manejarCambio(4, "cargo_actual", e.target.value)}
            placeholder="Cargo actual"
          />
        </div>
        <div className="demografico-form-field">
          <label>Área / Departamento</label>
          <input
            type="text"
            value={form.area_departamento}
            onChange={(e) => manejarCambio(4, "area_departamento", e.target.value)}
            placeholder="Área / Departamento"
          />
        </div>
        <div className="demografico-form-field">
          <label>Sede / Centro de trabajo</label>
          <input
            type="text"
            value={form.sede_centro_trabajo}
            onChange={(e) => manejarCambio(4, "sede_centro_trabajo", e.target.value)}
            placeholder="Sede / Centro de trabajo"
          />
        </div>
        <div className="demografico-form-field">
          <label>Tipo de contrato</label>
          <select value={form.tipo_contrato} onChange={(e) => manejarCambio(4, "tipo_contrato", e.target.value)}>
            <option value="">Seleccionar...</option>
            <option value="Término fijo">Término fijo</option>
            <option value="Término indefinido">Término indefinido</option>
            <option value="Obra o labor">Obra o labor</option>
            <option value="Aprendiz/Practicante">Aprendiz/Practicante</option>
            <option value="Prestación de servicios">Prestación de servicios</option>
          </select>
        </div>
        <div className="demografico-form-field">
          <label>Tiempo laborado</label>
          <input
            type="text"
            value={form.tiempo_laborado}
            onChange={(e) => manejarCambio(4, "tiempo_laborado", e.target.value)}
            placeholder="Tiempo laborado"
          />
        </div>
        <div className="demografico-form-field">
          <label>Antigüedad en el cargo</label>
          <select value={form.antiguedad_cargo} onChange={(e) => manejarCambio(4, "antiguedad_cargo", e.target.value)}>
            <option value="">Seleccionar...</option>
            <option value="Menos de 1 año">Menos de 1 año</option>
            <option value="1 a 3 años">1 a 3 años</option>
            <option value="Más de 3 años">Más de 3 años</option>
          </select>
        </div>
        <div className="demografico-form-field">
          <label>Última empresa</label>
          <input
            type="text"
            value={form.ultima_empresa}
            onChange={(e) => manejarCambio(4, "ultima_empresa", e.target.value)}
            placeholder="Última empresa"
          />
        </div>
        <div className="demografico-form-field">
          <label>Nivel de escolaridad</label>
          <select value={form.nivel_escolaridad} onChange={(e) => manejarCambio(4, "nivel_escolaridad", e.target.value)}>
            <option value="">Seleccionar...</option>
            <option value="Primaria">Primaria</option>
            <option value="Secundaria/Bachillerato">Secundaria/Bachillerato</option>
            <option value="Técnico">Técnico</option>
            <option value="Tecnológico">Tecnológico</option>
            <option value="Profesional">Profesional</option>
            <option value="Posgrado/Especialización/Maestría">Posgrado/Especialización/Maestría</option>
          </select>
        </div>
        <div className="demografico-form-field demografico-field-wide">
          <label>Detalle de títulos</label>
          <input
            type="text"
            value={form.detalle_titulos}
            onChange={(e) => manejarCambio(4, "detalle_titulos", e.target.value)}
            placeholder="Detalle de títulos obtenidos"
          />
        </div>
      </div>
    </div>
  );

  const renderSeccionSalud = () => (
    <div className="demografico-form-section">
      <h4>5. Información de Salud</h4>
      <div className="demografico-form-grid">
        <div className="demografico-form-field">
          <label>EPS actual</label>
          <input
            type="text"
            value={form.eps_actual}
            onChange={(e) => manejarCambio(5, "eps_actual", e.target.value)}
            placeholder="EPS actual"
          />
        </div>
        <div className="demografico-form-field">
          <label>Fondo de pensiones</label>
          <input
            type="text"
            value={form.fondo_pensiones}
            onChange={(e) => manejarCambio(5, "fondo_pensiones", e.target.value)}
            placeholder="Fondo de pensiones"
          />
        </div>
        <div className="demografico-form-field">
          <label>Tipo de RH</label>
          <select value={form.tipo_rh} onChange={(e) => manejarCambio(5, "tipo_rh", e.target.value)}>
            <option value="">Seleccionar...</option>
            <option value="A+">A+</option>
            <option value="A-">A-</option>
            <option value="B+">B+</option>
            <option value="B-">B-</option>
            <option value="AB+">AB+</option>
            <option value="AB-">AB-</option>
            <option value="O+">O+</option>
            <option value="O-">O-</option>
          </select>
        </div>
        <div className="demografico-form-field">
          <label className="demografico-checkbox-label">
            <input
              type="checkbox"
              checked={form.diagnostico_previo}
              onChange={(e) => manejarCambio(5, "diagnostico_previo", e.target.checked)}
            />
            Diagnóstico previo
          </label>
        </div>
        {form.diagnostico_previo && (
          <div className="demografico-form-field demografico-field-wide">
            <label>Detalle del diagnóstico</label>
            <input
              type="text"
              value={form.diagnostico_detalle}
              onChange={(e) => manejarCambio(5, "diagnostico_detalle", e.target.value)}
              placeholder="Detalle del diagnóstico"
            />
          </div>
        )}
        <div className="demografico-form-field">
          <label>Actividad física</label>
          <select value={form.actividad_fisica} onChange={(e) => manejarCambio(5, "actividad_fisica", e.target.value)}>
            <option value="">Seleccionar...</option>
            <option value="Sí">Sí</option>
            <option value="No">No</option>
          </select>
        </div>
        <div className="demografico-form-field">
          <label>Consumo de cigarrillo</label>
          <select value={form.consumo_cigarrillo} onChange={(e) => manejarCambio(5, "consumo_cigarrillo", e.target.value)}>
            <option value="">Seleccionar...</option>
            <option value="Nunca">Nunca</option>
            <option value="Ocasional">Ocasional</option>
            <option value="Frecuente (Diario)">Frecuente (Diario)</option>
          </select>
        </div>
        <div className="demografico-form-field">
          <label>Consumo de alcohol</label>
          <select value={form.consumo_alcohol} onChange={(e) => manejarCambio(5, "consumo_alcohol", e.target.value)}>
            <option value="">Seleccionar...</option>
            <option value="Nunca">Nunca</option>
            <option value="Ocasional (Eventos/Fines de semana)">Ocasional (Eventos/Fines de semana)</option>
            <option value="Frecuente">Frecuente</option>
          </select>
        </div>
      </div>
      <div className="demografico-form-subsection">
        <h5>Tallas para dotación</h5>
        <div className="demografico-form-grid">
          <div className="demografico-form-field">
            <label>Talla camisa</label>
            <input
              type="text"
              value={form.talla_camisa}
              onChange={(e) => manejarCambio(5, "talla_camisa", e.target.value)}
              placeholder="Talla camisa"
            />
          </div>
          <div className="demografico-form-field">
            <label>Talla pantalón</label>
            <input
              type="text"
              value={form.talla_pantalon}
              onChange={(e) => manejarCambio(5, "talla_pantalon", e.target.value)}
              placeholder="Talla pantalón"
            />
          </div>
          <div className="demografico-form-field">
            <label>Talla chaqueta</label>
            <input
              type="text"
              value={form.talla_chaqueta}
              onChange={(e) => manejarCambio(5, "talla_chaqueta", e.target.value)}
              placeholder="Talla chaqueta"
            />
          </div>
          <div className="demografico-form-field">
            <label>Talla overol</label>
            <input
              type="text"
              value={form.talla_overol}
              onChange={(e) => manejarCambio(5, "talla_overol", e.target.value)}
              placeholder="Talla overol"
            />
          </div>
          <div className="demografico-form-field">
            <label>Talla calzado</label>
            <input
              type="text"
              value={form.talla_calzado}
              onChange={(e) => manejarCambio(5, "talla_calzado", e.target.value)}
              placeholder="Talla calzado"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderSeccionReferencias = () => (
    <div className="demografico-form-section">
      <h4>6. Referencias</h4>
      <div className="demografico-form-grid">
        <div className="demografico-form-field">
          <label>Nombre referencia 1</label>
          <input
            type="text"
            value={form.referencia_1_nombre}
            onChange={(e) => manejarCambio(6, "referencia_1_nombre", e.target.value)}
            placeholder="Nombre referencia 1"
          />
        </div>
        <div className="demografico-form-field">
          <label>Ocupación referencia 1</label>
          <input
            type="text"
            value={form.referencia_1_ocupacion}
            onChange={(e) => manejarCambio(6, "referencia_1_ocupacion", e.target.value)}
            placeholder="Ocupación referencia 1"
          />
        </div>
        <div className="demografico-form-field">
          <label>Teléfono referencia 1</label>
          <input
            type="text"
            value={form.referencia_1_telefono}
            onChange={(e) => manejarCambio(6, "referencia_1_telefono", e.target.value)}
            placeholder="Teléfono referencia 1"
          />
        </div>
        <div className="demografico-form-field">
          <label>Nombre referencia 2</label>
          <input
            type="text"
            value={form.referencia_2_nombre}
            onChange={(e) => manejarCambio(6, "referencia_2_nombre", e.target.value)}
            placeholder="Nombre referencia 2"
          />
        </div>
        <div className="demografico-form-field">
          <label>Ocupación referencia 2</label>
          <input
            type="text"
            value={form.referencia_2_ocupacion}
            onChange={(e) => manejarCambio(6, "referencia_2_ocupacion", e.target.value)}
            placeholder="Ocupación referencia 2"
          />
        </div>
        <div className="demografico-form-field">
          <label>Teléfono referencia 2</label>
          <input
            type="text"
            value={form.referencia_2_telefono}
            onChange={(e) => manejarCambio(6, "referencia_2_telefono", e.target.value)}
            placeholder="Teléfono referencia 2"
          />
        </div>
      </div>
    </div>
  );

  const renderSeccionConsentimiento = () => (
    <div className="demografico-form-section">
      <h4>7. Consentimiento Informado</h4>
      <div className="demografico-form-consentimiento-text">
        <p>
          De conformidad con la Ley 1581 de 2012 y su Decreto Reglamentario 1377 de 2013, autorizo de manera libre, previa,
          expresa e informada a <strong>{obtenerNombreEmpresa({ empresa_id: filtros.empresa_id || empresas[0]?.id }, empresas)}</strong> para
          recolectar, almacenar, usar y circular los datos personales suministrados en el presente formulario, los cuales serán
          utilizados únicamente para fines de gestión del riesgo laboral, control de salud ocupacional y cumplimiento de la
          normatividad vigente en materia de seguridad y salud en el trabajo.
        </p>
      </div>
      <div className="demografico-form-grid">
        <div className="demografico-form-field">
          <label className="demografico-checkbox-label">
            <input
              type="checkbox"
              checked={form.consentimiento_informado}
              onChange={(e) => manejarCambio(7, "consentimiento_informado", e.target.checked)}
            />
            Acepto el tratamiento de mis datos personales
          </label>
        </div>
        <div className="demografico-form-field">
          <label>Fecha de firma</label>
          <input
            type="date"
            value={form.fecha_firma}
            onChange={(e) => manejarCambio(7, "fecha_firma", e.target.value)}
          />
        </div>
        <div className="demografico-form-field">
          <label className="demografico-checkbox-label">
            <input
              type="checkbox"
              checked={form.completado}
              onChange={(e) => manejarCambio(7, "completado", e.target.checked)}
            />
            Encuesta completada
          </label>
        </div>
      </div>
    </div>
  );

  const renderContenidoSeccion = () => {
    switch (seccionActiva) {
      case 1: return renderSeccionIdentificacion();
      case 2: return renderSeccionSociodemograficas();
      case 3: return renderSeccionVivienda();
      case 4: return renderSeccionLaboral();
      case 5: return renderSeccionSalud();
      case 6: return renderSeccionReferencias();
      case 7: return renderSeccionConsentimiento();
      default: return null;
    }
  };

  return (
    <main className="demografico-sst-page">
      <section className="demografico-sst-hero">
        <div className="demografico-hero-content">
          <h1>Perfiles Sociodemográficos</h1>
          <p>
            Encuesta Integral de Perfil Sociodemográfico, Salud y Actualización de Hoja de Vida — Ley 1581 de 2012
          </p>
        </div>
        <div className="demografico-hero-actions">
          <button className="btn-primary-sst" onClick={abrirModalEmpleado} type="button">
            <Users size={16} /> Nuevo perfil
          </button>
          <button className="btn-secondary-sst" onClick={actualizarPagina} disabled={cargando || cargandoDashboard} type="button">
            <RefreshCw size={16} className={cargando ? "spin-demografico" : ""} /> Actualizar
          </button>
          <button className="btn-secondary-sst" onClick={descargarPlantilla} type="button">
            <FileText size={16} /> Plantilla
          </button>
          <button className="btn-secondary-sst" onClick={abrirImportar} type="button">
            <Upload size={16} /> Importar
          </button>
          <button className="btn-primary-sst" onClick={exportarExcel} type="button">
            <Download size={16} /> Excel perfiles
          </button>
        </div>
      </section>

      {error && (
        <div className="demografico-alert error">
          <AlertCircle size={16} />
          <span>{error}</span>
          <button onClick={() => setError("")} type="button"><X size={16} /></button>
        </div>
      )}

      {mensaje && (
        <div className="demografico-alert success">
          <CheckCircle size={16} />
          <span>{mensaje}</span>
          <button onClick={() => setMensaje("")} type="button"><X size={16} /></button>
        </div>
      )}

      <section className="demografico-dashboard" aria-labelledby="demografico-dashboard-title">
        <header className="demografico-dashboard-header">
          <div>
            <span className="demografico-dashboard-eyebrow">Corte histórico de personal</span>
            <h2 id="demografico-dashboard-title">Dashboard de cobertura sociodemográfica</h2>
            <p>
              {dashboard.periodo?.etiqueta || "Selecciona un periodo"}
              {dashboard.periodo?.fecha_corte && <> · Corte al {formatearFecha(dashboard.periodo.fecha_corte)}</>}
            </p>
          </div>
          <div className="demografico-dashboard-actions">
            <button
              className="btn-secondary-sst btn-sm"
              type="button"
              onClick={() => exportarDashboard("excel")}
              disabled={Boolean(exportandoDashboard) || !filtros.empresa_id || !/^\d{4}$/.test(filtros.anio)}
            >
              {exportandoDashboard === "excel" ? <Loader2 size={15} className="spin-demografico" /> : <FileSpreadsheet size={15} />}
              Excel dashboard
            </button>
            <button
              className="btn-secondary-sst btn-sm"
              type="button"
              onClick={() => exportarDashboard("pdf")}
              disabled={Boolean(exportandoDashboard) || !filtros.empresa_id || !/^\d{4}$/.test(filtros.anio)}
            >
              {exportandoDashboard === "pdf" ? <Loader2 size={15} className="spin-demografico" /> : <FileText size={15} />}
              PDF dashboard
            </button>
          </div>
        </header>

        <div className="demografico-dashboard-filters" aria-label="Filtros del dashboard">
          <label>
            <span>Empresa</span>
            <select
              value={filtros.empresa_id}
              onChange={(e) => setFiltros((prev) => ({ ...prev, empresa_id: e.target.value, sede_id: "" }))}
            >
              <option value="">Selecciona una empresa</option>
              {empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>{empresa.nombre}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Sede</span>
            <select
              value={filtros.sede_id}
              onChange={(e) => setFiltros((prev) => ({ ...prev, sede_id: e.target.value }))}
              disabled={!filtros.empresa_id}
            >
              <option value="">Todas las sedes</option>
              {sedes.map((sede) => (
                <option key={sede.id} value={sede.id}>{sede.nombre}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Año</span>
            <input
              type="text"
              inputMode="numeric"
              pattern="\d{4}"
              maxLength={4}
              value={filtros.anio}
              onChange={(e) => setFiltros((prev) => ({
                ...prev,
                anio: e.target.value.replace(/\D/g, "").slice(0, 4),
              }))}
              aria-label="Año del dashboard"
            />
          </label>
          <label>
            <span>Mes opcional</span>
            <select value={filtros.mes} onChange={(e) => setFiltros((prev) => ({ ...prev, mes: e.target.value }))}>
              <option value="">Todo el año</option>
              {MESES.map((nombre, index) => (
                <option key={nombre} value={index + 1}>{nombre}</option>
              ))}
            </select>
          </label>
        </div>

        {errorDashboard && (
          <div className="demografico-dashboard-message error" role="alert">
            <AlertCircle size={17} /> {errorDashboard}
          </div>
        )}

        {(Number(dashboard.kpis.sin_fecha_ingreso) > 0 || Number(dashboard.kpis.datos_historicos_incompletos) > 0) && (
          <div className="demografico-dashboard-message warning" role="status">
            <AlertCircle size={17} />
            <span>
              Calidad histórica por revisar: {dashboard.kpis.sin_fecha_ingreso || 0} empleado(s) sin fecha de ingreso y{" "}
              {dashboard.kpis.datos_historicos_incompletos || 0} registro(s) con datos históricos incompletos.
            </span>
          </div>
        )}

        <div className={`demografico-dashboard-content ${cargandoDashboard ? "is-loading" : ""}`} aria-busy={cargandoDashboard}>
          <div className="demografico-dashboard-kpis">
            <DashboardKpi icon={CalendarDays} label="Plantilla al corte" value={dashboard.kpis.total_periodo} tone="navy" />
            <DashboardKpi icon={UserCheck} label="Activos" value={dashboard.kpis.activos} tone="green" />
            <DashboardKpi icon={UserMinus} label="Inactivos" value={dashboard.kpis.inactivos} tone="red" />
            <DashboardKpi icon={Users} label="Perfiles registrados" value={dashboard.kpis.perfiles_registrados} tone="blue" />
            <DashboardKpi icon={ClipboardCheck} label="Perfiles completados" value={dashboard.kpis.perfiles_completados} tone="purple" />
            <DashboardKpi icon={Percent} label="Cobertura" value={dashboard.kpis.cobertura_perfil} suffix="%" tone="teal" />
          </div>

          <div className="demografico-dashboard-charts">
            <article className="demografico-chart-card" aria-label="Tendencia mensual de empleados activos e inactivos">
              <div className="demografico-chart-title">
                <div><h3>Tendencia mensual</h3><p>Activos e inactivos durante {filtros.anio || "el periodo"}</p></div>
                <CalendarDays size={18} aria-hidden="true" />
              </div>
              {dashboard.tendencia_mensual.length > 0 ? (
                <ResponsiveContainer width="100%" height={230}>
                  <LineChart data={dashboard.tendencia_mensual} accessibilityLayer margin={{ top: 10, right: 12, left: -18, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="nombre" tick={{ fontSize: 11 }} stroke="#64748b" />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} stroke="#64748b" />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="activos" name="Activos" stroke="#16a34a" strokeWidth={2.5} dot={{ r: 3 }} />
                    <Line type="monotone" dataKey="inactivos" name="Inactivos" stroke="#dc2626" strokeWidth={2.5} strokeDasharray="6 4" dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : <p className="demografico-chart-empty">Sin datos mensuales para el periodo seleccionado.</p>}
            </article>

            <article className="demografico-chart-card" aria-label="Distribución de empleados por sede">
              <div className="demografico-chart-title">
                <div><h3>Plantilla por sede</h3><p>Comparación de activos e inactivos</p></div>
                <MapPin size={18} aria-hidden="true" />
              </div>
              {dashboard.por_sede.length > 0 ? (
                <ResponsiveContainer width="100%" height={230}>
                  <BarChart data={dashboard.por_sede} layout="vertical" accessibilityLayer margin={{ top: 10, right: 12, left: 8, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
                    <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} stroke="#64748b" />
                    <YAxis type="category" dataKey="nombre" width={90} tick={{ fontSize: 11 }} stroke="#64748b" />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="activos" name="Activos" fill="#2563eb" radius={[0, 4, 4, 0]} />
                    <Bar dataKey="inactivos" name="Inactivos" fill="#f59e0b" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : <p className="demografico-chart-empty">Sin distribución por sede para el periodo seleccionado.</p>}
            </article>
          </div>
        </div>
      </section>

      <section className="demografico-toolbar">
        <label className="demografico-search-box">
          <Search size={17} />
          <input
            value={filtros.buscar}
            placeholder="Buscar por nombre, documento..."
            onChange={(e) => setFiltros((prev) => ({ ...prev, buscar: e.target.value }))}
          />
        </label>
        <div className="demografico-toolbar-filters">
          <button className="btn-secondary-sst btn-sm" type="button" onClick={limpiarFiltros}>
            <Filter size={15} /> Limpiar filtros
          </button>
        </div>
      </section>

      <section className="demografico-table-wrapper">
        <table className="demografico-table">
          <thead>
            <tr>
              <th>Empleado</th>
              <th>Documento</th>
              <th>Empresa</th>
              <th>Estado</th>
              <th>Fecha creación</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {cargando ? (
              <tr>
                <td colSpan="6" className="demografico-empty-row">
                  <Loader2 size={18} className="spin-demografico" /> Cargando perfiles...
                </td>
              </tr>
            ) : perfilesPagina.length === 0 ? (
              <tr>
                <td colSpan="6" className="demografico-empty-row">
                  <Users size={18} /> No hay perfiles para los filtros seleccionados.
                </td>
              </tr>
            ) : (
              perfilesPagina.map((perfil, idx) => (
                <tr key={perfil.id || perfil.empleado_id || idx}>
                  <td>
                    <div className="demografico-empleado-cell">
                      <Users size={16} />
                      <strong>{perfil.nombres_completos || perfil.nombre_empleado || perfil.empleado_nombre || "Sin nombre"}</strong>
                    </div>
                  </td>
                  <td>
                    <span className="demografico-doc-pill">
                      {perfil.tipo_documento || "CC"} {perfil.numero_documento || "—"}
                    </span>
                  </td>
                  <td>
                    <span className="demografico-empresa-cell">
                      <Building2 size={14} />
                      {obtenerNombreEmpresa(perfil, empresas)}
                    </span>
                  </td>
                  <td>
                    <span className={`demografico-estado-pill ${perfil.estado === "completado" || perfil.completado ? "completado" : "borrador"}`}>
                      {perfil.estado === "completado" || perfil.completado ? "Completado" : "Borrador"}
                    </span>
                  </td>
                  <td>{formatearFecha(perfil.fecha_creacion || perfil.created_at)}</td>
                  <td>
                    <div className="demografico-actions">
                      <button
                        className="demografico-icon-btn edit"
                        onClick={() => abrirFormularioEditar(perfil)}
                        title="Editar"
                        type="button"
                      >
                        <Pencil size={16} />
                      </button>
                      <button
                        className="demografico-icon-btn view"
                        onClick={() => abrirDetalle(perfil)}
                        title="Ver detalle"
                        type="button"
                      >
                        <Eye size={16} />
                      </button>
                      <button
                        className="demografico-icon-btn delete"
                        onClick={() => confirmarEliminar(perfil)}
                        title="Eliminar"
                        type="button"
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
      </section>

      <section className="demografico-pagination">
        <span>
          Mostrando {perfilesPagina.length ? inicio + 1 : 0} - {Math.min(inicio + porPagina, perfilesFiltrados.length)} de {perfilesFiltrados.length} registros
        </span>
        <div className="demografico-pagination-controls">
          <button disabled={pagina <= 1} onClick={() => setPagina((p) => p - 1)} type="button">
            <ChevronLeft size={16} />
          </button>
          <span>Página {pagina} / {totalPaginas}</span>
          <button disabled={pagina >= totalPaginas} onClick={() => setPagina((p) => p + 1)} type="button">
            <ChevronRight size={16} />
          </button>
        </div>
      </section>

      {modalDetalle && (
        <div className="demografico-modal-backdrop">
          <section className="demografico-modal-card demografico-modal-detalle">
            <header className="demografico-modal-header">
              <div className="demografico-modal-header-title">
                <Users size={22} />
                <div>
                  <h2>Detalle del Perfil Sociodemográfico</h2>
                  <p>{perfilDetalle?.nombres_completos || "Cargando..."}</p>
                </div>
              </div>
              <button className="demografico-modal-close" onClick={cerrarDetalle} type="button">
                <X size={18} />
              </button>
            </header>

            <div className="demografico-modal-body">
              {cargandoDetalle ? (
                <div className="demografico-loading-detail">
                  <Loader2 size={24} className="spin-demografico" />
                  <span>Cargando detalle del perfil...</span>
                </div>
              ) : perfilDetalle ? (
                <>
                  <div className="demografico-detail-section">
                    <h3>1. Identificación</h3>
                    <div className="demografico-detail-grid">
                      <div className="demografico-detail-field">
                        <label>Nombres completos</label>
                        <span>{perfilDetalle.nombres_completos || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Tipo de documento</label>
                        <span>{perfilDetalle.tipo_documento || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Número de documento</label>
                        <span>{perfilDetalle.numero_documento || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Libreta militar</label>
                        <span>{valorOSiNo(perfilDetalle.libreta_militar)}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Fecha de nacimiento</label>
                        <span>{formatearFecha(perfilDetalle.fecha_nacimiento)}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Lugar de nacimiento</label>
                        <span>{perfilDetalle.lugar_nacimiento || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Edad</label>
                        <span>{perfilDetalle.edad || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Raza / Grupo étnico</label>
                        <span>{perfilDetalle.raza_pertenencia_etnica || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Teléfono</label>
                        <span>{perfilDetalle.telefono_celular || "—"}</span>
                      </div>
                    </div>
                  </div>

                  <div className="demografico-detail-section">
                    <h3>2. Información Sociodemográfica</h3>
                    <div className="demografico-detail-grid">
                      <div className="demografico-detail-field">
                        <label>Estado civil</label>
                        <span>{perfilDetalle.estado_civil || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Nombre del cónyuge</label>
                        <span>{perfilDetalle.conyuge_nombre || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Ocupación del cónyuge</label>
                        <span>{perfilDetalle.conyuge_ocupacion || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Edad del cónyuge</label>
                        <span>{perfilDetalle.conyuge_edad || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Celular del cónyuge</label>
                        <span>{perfilDetalle.conyuge_celular || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Número de dependientes</label>
                        <span>{perfilDetalle.numero_dependientes ?? "—"}</span>
                      </div>
                      <div className="demografico-detail-field demografico-field-wide">
                        <label>Hijos / Dependientes</label>
                        <span>
                          {Array.isArray(perfilDetalle.hijos) && perfilDetalle.hijos.length > 0
                            ? perfilDetalle.hijos.map((h) => `${h.nombre} (Edad: ${h.edad ?? "—"})`).join(", ")
                            : "—"}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="demografico-detail-section">
                    <h3>3. Vivienda</h3>
                    <div className="demografico-detail-grid">
                      <div className="demografico-detail-field">
                        <label>Dirección</label>
                        <span>{perfilDetalle.direccion_residencia || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Barrio</label>
                        <span>{perfilDetalle.barrio || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Ciudad</label>
                        <span>{perfilDetalle.ciudad_municipio || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Estrato</label>
                        <span>{perfilDetalle.estrato_socioeconomico || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Tipo de vivienda</label>
                        <span>{perfilDetalle.tipo_vivienda || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Servicios públicos</label>
                        <span>
                          {Array.isArray(perfilDetalle.servicios_vivienda) ? perfilDetalle.servicios_vivienda.join(", ") : "—"}
                        </span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Medio de transporte</label>
                        <span>{perfilDetalle.medio_transporte || "—"}</span>
                      </div>
                      {perfilDetalle.medio_transporte === "Otro" && (
                        <div className="demografico-detail-field">
                          <label>Otro medio de transporte</label>
                          <span>{perfilDetalle.medio_transporte_otro || "—"}</span>
                        </div>
                      )}
                      <div className="demografico-detail-field">
                        <label>Tiempo de desplazamiento</label>
                        <span>{perfilDetalle.tiempo_desplazamiento || "—"}</span>
                      </div>
                    </div>
                  </div>

                  <div className="demografico-detail-section">
                    <h3>4. Información Laboral</h3>
                    <div className="demografico-detail-grid">
                      <div className="demografico-detail-field">
                        <label>Cargo</label>
                        <span>{perfilDetalle.cargo_actual || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Área</label>
                        <span>{perfilDetalle.area_departamento || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Sede</label>
                        <span>{perfilDetalle.sede_centro_trabajo || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Tipo de contrato</label>
                        <span>{perfilDetalle.tipo_contrato || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Tiempo laborado</label>
                        <span>{perfilDetalle.tiempo_laborado || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Antigüedad en el cargo</label>
                        <span>{perfilDetalle.antiguedad_cargo || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Última empresa</label>
                        <span>{perfilDetalle.ultima_empresa || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Escolaridad</label>
                        <span>{perfilDetalle.nivel_escolaridad || "—"}</span>
                      </div>
                      <div className="demografico-detail-field demografico-field-wide">
                        <label>Detalle de títulos</label>
                        <span>{perfilDetalle.detalle_titulos || "—"}</span>
                      </div>
                    </div>
                  </div>

                  <div className="demografico-detail-section">
                    <h3>5. Información de Salud</h3>
                    <div className="demografico-detail-grid">
                      <div className="demografico-detail-field">
                        <label>EPS</label>
                        <span>{perfilDetalle.eps_actual || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Fondo de pensión</label>
                        <span>{perfilDetalle.fondo_pensiones || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>RH</label>
                        <span>{perfilDetalle.tipo_rh || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Diagnóstico previo</label>
                        <span>{valorOSiNo(perfilDetalle.diagnostico_previo)}</span>
                      </div>
                      {perfilDetalle.diagnostico_previo && (
                        <div className="demografico-detail-field demografico-field-wide">
                          <label>Detalle diagnóstico</label>
                          <span>{perfilDetalle.diagnostico_detalle || "—"}</span>
                        </div>
                      )}
                      <div className="demografico-detail-field">
                        <label>Actividad física</label>
                        <span>{perfilDetalle.actividad_fisica || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Consumo cigarrillo</label>
                        <span>{perfilDetalle.consumo_cigarrillo || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Consumo alcohol</label>
                        <span>{perfilDetalle.consumo_alcohol || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Talla camisa</label>
                        <span>{perfilDetalle.talla_camisa || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Talla pantalón</label>
                        <span>{perfilDetalle.talla_pantalon || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Talla chaqueta</label>
                        <span>{perfilDetalle.talla_chaqueta || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Talla overol</label>
                        <span>{perfilDetalle.talla_overol || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Talla calzado</label>
                        <span>{perfilDetalle.talla_calzado || "—"}</span>
                      </div>
                    </div>
                  </div>

                  <div className="demografico-detail-section">
                    <h3>6. Referencias</h3>
                    <div className="demografico-detail-grid">
                      <div className="demografico-detail-field">
                        <label>Nombre referencia 1</label>
                        <span>{perfilDetalle.referencia_1_nombre || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Ocupación referencia 1</label>
                        <span>{perfilDetalle.referencia_1_ocupacion || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Teléfono referencia 1</label>
                        <span>{perfilDetalle.referencia_1_telefono || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Nombre referencia 2</label>
                        <span>{perfilDetalle.referencia_2_nombre || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Ocupación referencia 2</label>
                        <span>{perfilDetalle.referencia_2_ocupacion || "—"}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Teléfono referencia 2</label>
                        <span>{perfilDetalle.referencia_2_telefono || "—"}</span>
                      </div>
                    </div>
                  </div>

                  <div className="demografico-detail-section">
                    <h3>7. Consentimiento</h3>
                    <div className="demografico-detail-grid">
                      <div className="demografico-detail-field">
                        <label>Consentimiento tratamiento de datos</label>
                        <span>{valorOSiNo(perfilDetalle.consentimiento_informado)}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Fecha de firma</label>
                        <span>{formatearFecha(perfilDetalle.fecha_firma)}</span>
                      </div>
                      <div className="demografico-detail-field">
                        <label>Encuesta completada</label>
                        <span className={`demografico-estado-pill ${perfilDetalle.completado ? "completado" : "borrador"}`}>
                          {perfilDetalle.completado ? "Completado" : "Borrador"}
                        </span>
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="demografico-loading-detail">
                  <AlertCircle size={24} />
                  <span>No se pudo cargar el detalle del perfil.</span>
                </div>
              )}
            </div>

            <footer className="demografico-modal-footer">
              <button className="btn-secondary-sst" onClick={cerrarDetalle} type="button">Cerrar</button>
            </footer>
          </section>
        </div>
      )}

      {modalEliminar && perfilEliminar && (
        <div className="demografico-modal-backdrop">
          <section className="demografico-modal-card demografico-modal-eliminar">
            <header className="demografico-modal-header">
              <div className="demografico-modal-header-title">
                <AlertCircle size={22} />
                <div>
                  <h2>Confirmar eliminación</h2>
                  <p>Esta acción no se puede deshacer.</p>
                </div>
              </div>
              <button className="demografico-modal-close" onClick={cerrarEliminar} type="button">
                <X size={18} />
              </button>
            </header>
            <div className="demografico-modal-body">
              <p className="demografico-eliminar-msg">
                ¿Estás seguro de que deseas eliminar el perfil de{" "}
                <strong>{perfilEliminar.nombres_completos || perfilEliminar.nombre_empleado || "este empleado"}</strong>?
              </p>
            </div>
            <footer className="demografico-modal-footer">
              <button className="btn-secondary-sst" onClick={cerrarEliminar} disabled={eliminando} type="button">
                Cancelar
              </button>
              <button className="btn-danger-sst" onClick={ejecutarEliminar} disabled={eliminando} type="button">
                {eliminando ? (
                  <>
                    <Loader2 size={16} className="spin-demografico" /> Eliminando...
                  </>
                ) : (
                  <>
                    <Trash2 size={16} /> Confirmar
                  </>
                )}
              </button>
            </footer>
          </section>
        </div>
      )}

      {modalImportar && (
        <div className="demografico-modal-backdrop">
          <section className="demografico-modal-card demografico-modal-importar">
            <header className="demografico-modal-header">
              <div className="demografico-modal-header-title">
                <Upload size={22} />
                <div>
                  <h2>Importar perfiles desde Excel</h2>
                  <p>Selecciona un archivo .xlsx con los datos de los perfiles.</p>
                </div>
              </div>
              <button className="demografico-modal-close" onClick={cerrarImportar} type="button">
                <X size={18} />
              </button>
            </header>
            <div className="demografico-modal-body">
              <label className="demografico-file-input-label">
                <FileText size={20} />
                <span>{archivoImportar ? archivoImportar.name : "Seleccionar archivo..."}</span>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={(e) => setArchivoImportar(e.target.files?.[0] || null)}
                  style={{ display: "none" }}
                />
              </label>
              {!filtros.empresa_id && empresas.length > 0 && (
                <p className="demografico-importar-hint">
                  Se usará la primera empresa disponible si no hay filtro de empresa activo.
                </p>
              )}
            </div>
            <footer className="demografico-modal-footer">
              <button className="btn-secondary-sst" onClick={cerrarImportar} disabled={importando} type="button">
                Cancelar
              </button>
              <button className="btn-primary-sst" onClick={ejecutarImportar} disabled={importando || !archivoImportar} type="button">
                {importando ? (
                  <>
                    <Loader2 size={16} className="spin-demografico" /> Importando...
                  </>
                ) : (
                  <>
                    <Upload size={16} /> Importar
                  </>
                )}
              </button>
            </footer>
          </section>
        </div>
      )}

      {modalEmpleado && (
        <div className="demografico-modal-backdrop">
          <section className="demografico-modal-card demografico-modal-empleados">
            <header className="demografico-modal-header">
              <div className="demografico-modal-header-title">
                <Users size={22} />
                <div>
                  <h2>Seleccionar empleado</h2>
                  <p>Selecciona un empleado para crear su perfil sociodemográfico.</p>
                </div>
              </div>
              <button className="demografico-modal-close" onClick={() => setModalEmpleado(false)} type="button">
                <X size={18} />
              </button>
            </header>
            <div className="demografico-modal-body">
              <label className="demografico-search-box">
                <Search size={17} />
                <input
                  value={busquedaEmpleado}
                  placeholder="Buscar por nombre, documento, cargo..."
                  onChange={(e) => setBusquedaEmpleado(e.target.value)}
                />
              </label>
              {cargandoEmpleados ? (
                <div className="demografico-loading-detail">
                  <Loader2 size={24} className="spin-demografico" />
                  <span>Cargando empleados...</span>
                </div>
              ) : empleadosFiltrados.length === 0 ? (
                <div className="demografico-loading-detail">
                  <Users size={24} />
                  <span>No se encontraron empleados.</span>
                </div>
              ) : (
                <table className="demografico-table">
                  <thead>
                    <tr>
                      <th>Nombre</th>
                      <th>Documento</th>
                      <th>Cargo</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {empleadosFiltrados.map((emp) => (
                      <tr key={emp.id}>
                        <td>
                          <div className="demografico-empleado-cell">
                            <Users size={16} />
                            <strong>{`${emp.nombres || ""} ${emp.apellidos || ""}`.trim() || "Sin nombre"}</strong>
                          </div>
                        </td>
                        <td>
                          <span className="demografico-doc-pill">
                            {emp.tipo_documento || "CC"} {emp.numero_documento || emp.documento || "—"}
                          </span>
                        </td>
                        <td>{emp.cargo_nombre || "—"}</td>
                        <td>
                          <button
                            className="btn-primary-sst btn-sm"
                            onClick={() => seleccionarEmpleado(emp)}
                            type="button"
                          >
                            Seleccionar
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
            <footer className="demografico-modal-footer">
              <button className="btn-secondary-sst" onClick={() => setModalEmpleado(false)} type="button">
                Cerrar
              </button>
            </footer>
          </section>
        </div>
      )}

      {modalFormulario && (
        <div className="demografico-modal-backdrop">
          <section className="demografico-modal-card demografico-modal-formulario">
            <header className="demografico-modal-header">
              <div className="demografico-modal-header-title">
                <Users size={22} />
                <div>
                  <h2>{perfilEditando ? "Editar Perfil Sociodemográfico" : "Nuevo Perfil Sociodemográfico"}</h2>
                  <p>
                    {perfilEditando
                      ? `Editando perfil de ${perfilEditando.nombres_completos || "—"}`
                      : empleadoSeleccionado
                        ? `Empleado: ${empleadoSeleccionado.nombre_completo || empleadoSeleccionado.nombres_completos || "—"}`
                        : "Complete los campos del formulario"}
                  </p>
                </div>
              </div>
              <button className="demografico-modal-close" onClick={cerrarFormulario} type="button">
                <X size={18} />
              </button>
            </header>

            <div className="demografico-form-tabs">
              {SECCIONES.map((nombre, idx) => (
                <button
                  key={idx + 1}
                  className={`demografico-form-tab ${seccionActiva === idx + 1 ? "active" : ""}`}
                  onClick={() => setSeccionActiva(idx + 1)}
                  type="button"
                >
                  {idx + 1}. {nombre}
                </button>
              ))}
            </div>

            <div className="demografico-modal-body">
              {renderContenidoSeccion()}
            </div>

            <footer className="demografico-modal-footer">
              <button className="btn-secondary-sst" onClick={cerrarFormulario} disabled={guardando} type="button">
                Cancelar
              </button>
              {seccionActiva > 1 && (
                <button
                  className="btn-secondary-sst"
                  onClick={() => setSeccionActiva((s) => s - 1)}
                  disabled={guardando}
                  type="button"
                >
                  <ChevronLeft size={16} /> Anterior
                </button>
              )}
              {seccionActiva < 7 ? (
                <button
                  className="btn-primary-sst"
                  onClick={() => setSeccionActiva((s) => s + 1)}
                  disabled={guardando}
                  type="button"
                >
                  Siguiente <ChevronRight size={16} />
                </button>
              ) : (
                <button
                  className="btn-primary-sst"
                  onClick={guardarPerfil}
                  disabled={guardando}
                  type="button"
                >
                  {guardando ? (
                    <>
                      <Loader2 size={16} className="spin-demografico" /> Guardando...
                    </>
                  ) : (
                    <>
                      <CheckCircle size={16} /> Guardar perfil
                    </>
                  )}
                </button>
              )}
            </footer>
          </section>
        </div>
      )}
    </main>
  );
}
