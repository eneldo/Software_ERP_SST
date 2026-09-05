// ============================================================
// PÁGINA EMPRESAS SST ENTERPRISE PRO
// Archivo: frontend/src/pages/organizacion/EmpresasSSTPage.jsx
// FASE 1.1.1.C — Empresas SST Enterprise PRO
// ============================================================

import { useEffect, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  Building2,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Download,
  Eye,
  Factory,
  FileSpreadsheet,
  Filter,
  ImagePlus,
  Loader2,
  MapPin,
  Pencil,
  Plus,
  RefreshCw,
  Save,
  Search,
  ShieldCheck,
  Trash2,
  UploadCloud,
  Users,
  X,
} from "lucide-react";

import {
  actualizarEmpresaSST,
  construirUrlLogoEmpresa,
  crearEmpresaSST,
  ejecutarEliminacionInteligenteEmpresaSST,
  eliminarLogoEmpresaSST,
  inactivarEmpresaSST,
  listarEmpresasSST,
  validarEliminacionEmpresaSST,
  subirLogoEmpresaSST,
} from "../../api/empresaSstApi";

import AutocompleteCIIU from "../../components/common/AutocompleteCIIU";
import EliminacionInteligenteModal from "../../components/common/EliminacionInteligenteModal";

import "../../styles/empresas-sst.css";

const ESTADO_INICIAL = {
  nombre: "",
  nit: "",
  digito_verificacion: "",
  direccion: "",
  telefono: "",
  correo: "",
  representante_legal: "",
  responsable_sst: "",
  actividad_economica: "",
  arl: "",
  numero_trabajadores: 1,
  clase_riesgo: "I",
  tipo_empresa: "EMPRESA",
  estado: true,
};

const CLASES_RIESGO = ["I", "II", "III", "IV", "V"];
const TIPOS_EMPRESA = ["EMPRESA", "CONTRATISTA", "TEMPORAL", "INDEPENDIENTE", "COOPERATIVA"];
const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

const tabsFormulario = [
  { id: "generales", label: "Datos generales" },
  { id: "contacto", label: "Contacto" },
  { id: "sst", label: "SST" },
  { id: "clasificacion", label: "Clasificación" },
];

const normalizarEstado = (estado) => estado === true || estado === "ACTIVA" || estado === "true";
const textoEstado = (estado) => (normalizarEstado(estado) ? "ACTIVA" : "INACTIVA");
const limpiarTexto = (valor) => String(valor ?? "").toLowerCase().trim();

const formatNumber = (value) => {
  const numero = Number(value || 0);
  return new Intl.NumberFormat("es-CO").format(numero);
};

const getInitials = (nombre = "") => {
  const parts = nombre.trim().split(" ").filter(Boolean).slice(0, 2);
  if (!parts.length) return "ES";
  return parts.map((p) => p[0]).join("").toUpperCase();
};

const descargarArchivo = (contenido, nombreArchivo, tipo = "text/csv;charset=utf-8;") => {
  const blob = new Blob([contenido], { type: tipo });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", nombreArchivo);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export default function EmpresasSSTPage() {
  const [empresas, setEmpresas] = useState([]);
  const [form, setForm] = useState(ESTADO_INICIAL);
  const [empresaSeleccionada, setEmpresaSeleccionada] = useState(null);
  const [empresaDetalle, setEmpresaDetalle] = useState(null);
  const [modalFormulario, setModalFormulario] = useState(false);
  const [modalDetalle, setModalDetalle] = useState(false);
  const [tabActiva, setTabActiva] = useState("generales");
  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("TODAS");
  const [filtroRiesgo, setFiltroRiesgo] = useState("TODAS");
  const [filtroTipo, setFiltroTipo] = useState("TODAS");
  const [filtroArl, setFiltroArl] = useState("TODAS");
  const [pageSize, setPageSize] = useState(10);
  const [page, setPage] = useState(1);
  const [cargando, setCargando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [subiendoLogoId, setSubiendoLogoId] = useState(null);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [modalEliminacion, setModalEliminacion] = useState(false);
  const [empresaAEliminar, setEmpresaAEliminar] = useState(null);
  const [validacionEliminacion, setValidacionEliminacion] = useState(null);
  const [ejecutandoEliminacion, setEjecutandoEliminacion] = useState(false);

  const fileInputRef = useRef(null);
  const empresaLogoTargetRef = useRef(null);

  const cargarEmpresas = async () => {
    try {
      setCargando(true);
      setError("");
      const data = await listarEmpresasSST();
      setEmpresas(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error cargando empresas SST:", err);
      setError("No fue posible cargar las empresas SST. Verifica backend, token y permisos.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarEmpresas();
  }, []);

  useEffect(() => {
    setPage(1);
  }, [busqueda, filtroEstado, filtroRiesgo, filtroTipo, filtroArl, pageSize]);

  const arlsDisponibles = useMemo(() => {
    const set = new Set(empresas.map((e) => e.arl).filter(Boolean));
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [empresas]);

  const kpis = useMemo(() => {
    const activas = empresas.filter((e) => normalizarEstado(e.estado)).length;
    const inactivas = empresas.length - activas;
    const trabajadores = empresas.reduce((acc, e) => acc + Number(e.numero_trabajadores || 0), 0);
    const riesgoAlto = empresas.filter((e) => ["IV", "V"].includes(e.clase_riesgo)).length;
    const conLogo = empresas.filter((e) => Boolean(e.logo)).length;

    return {
      total: empresas.length,
      activas,
      inactivas,
      trabajadores,
      riesgoAlto,
      conLogo,
    };
  }, [empresas]);

  const empresasFiltradas = useMemo(() => {
    const q = limpiarTexto(busqueda);

    return empresas.filter((empresa) => {
      const estadoEmpresa = textoEstado(empresa.estado);
      const matchEstado = filtroEstado === "TODAS" || estadoEmpresa === filtroEstado;
      const matchRiesgo = filtroRiesgo === "TODAS" || empresa.clase_riesgo === filtroRiesgo;
      const matchTipo = filtroTipo === "TODAS" || empresa.tipo_empresa === filtroTipo;
      const matchArl = filtroArl === "TODAS" || empresa.arl === filtroArl;

      const textoBusqueda = [
        empresa.nombre,
        empresa.nit,
        empresa.direccion,
        empresa.telefono,
        empresa.correo,
        empresa.representante_legal,
        empresa.actividad_economica,
        empresa.arl,
        empresa.clase_riesgo,
        empresa.tipo_empresa,
        empresa.tipo_estandares_sst,
        empresa.descripcion_estandares_sst,
      ]
        .join(" ")
        .toLowerCase();

      const matchBusqueda = !q || textoBusqueda.includes(q);
      return matchEstado && matchRiesgo && matchTipo && matchArl && matchBusqueda;
    });
  }, [empresas, busqueda, filtroEstado, filtroRiesgo, filtroTipo, filtroArl]);

  const totalPages = Math.max(1, Math.ceil(empresasFiltradas.length / pageSize));
  const paginaActual = Math.min(page, totalPages);
  const startIndex = (paginaActual - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, empresasFiltradas.length);
  const empresasPaginadas = empresasFiltradas.slice(startIndex, endIndex);

  const resumenRiesgos = useMemo(() => {
    return CLASES_RIESGO.reduce((acc, riesgo) => {
      acc[riesgo] = empresas.filter((e) => e.clase_riesgo === riesgo).length;
      return acc;
    }, {});
  }, [empresas]);

  const limpiarFiltros = () => {
    setBusqueda("");
    setFiltroEstado("TODAS");
    setFiltroRiesgo("TODAS");
    setFiltroTipo("TODAS");
    setFiltroArl("TODAS");
  };

  const abrirCrear = () => {
    setEmpresaSeleccionada(null);
    setForm(ESTADO_INICIAL);
    setTabActiva("generales");
    setModalFormulario(true);
    setError("");
    setMensaje("");
  };

  const abrirEditar = (empresa) => {
    setEmpresaSeleccionada(empresa);
    setForm({
      nombre: empresa.nombre || "",
      nit: empresa.nit || "",
      digito_verificacion: empresa.digito_verificacion || "",
      direccion: empresa.direccion || "",
      telefono: empresa.telefono || "",
      correo: empresa.correo || "",
      representante_legal: empresa.representante_legal || "",
      responsable_sst: empresa.responsable_sst || "",
      actividad_economica: empresa.actividad_economica || "",
      arl: empresa.arl || "",
      numero_trabajadores: Number(empresa.numero_trabajadores || 1),
      clase_riesgo: empresa.clase_riesgo || "I",
      tipo_empresa: empresa.tipo_empresa || "EMPRESA",
      estado: normalizarEstado(empresa.estado),
    });
    setTabActiva("generales");
    setModalFormulario(true);
    setError("");
    setMensaje("");
  };

  const abrirDetalle = (empresa) => {
    setEmpresaDetalle(empresa);
    setModalDetalle(true);
  };

  const cerrarFormulario = () => {
    setModalFormulario(false);
    setEmpresaSeleccionada(null);
    setForm(ESTADO_INICIAL);
    setTabActiva("generales");
  };

  const cerrarDetalle = () => {
    setModalDetalle(false);
    setEmpresaDetalle(null);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const crearPayload = () => ({
    nombre: form.nombre.trim(),
    nit: form.nit.trim(),
    digito_verificacion: form.digito_verificacion?.trim() || null,
    direccion: form.direccion?.trim() || null,
    telefono: form.telefono?.trim() || null,
    correo: form.correo?.trim() || null,
    representante_legal: form.representante_legal?.trim() || null,
    responsable_sst: form.responsable_sst?.trim() || null,
    actividad_economica: form.actividad_economica?.trim() || null,
    arl: form.arl?.trim() || null,
    numero_trabajadores: Math.max(1, Number(form.numero_trabajadores || 1)),
    clase_riesgo: form.clase_riesgo || "I",
    tipo_empresa: form.tipo_empresa || "EMPRESA",
    estado: Boolean(form.estado),
  });

  const guardarEmpresa = async (e) => {
    e.preventDefault();

    if (!form.nombre.trim()) {
      setError("El nombre de la empresa es obligatorio.");
      setTabActiva("generales");
      return;
    }

    if (!form.nit.trim()) {
      setError("El NIT de la empresa es obligatorio.");
      setTabActiva("generales");
      return;
    }

    try {
      setGuardando(true);
      setError("");
      setMensaje("");

      const payload = crearPayload();

      if (empresaSeleccionada?.id) {
        await actualizarEmpresaSST(empresaSeleccionada.id, payload);
        setMensaje("Empresa actualizada correctamente.");
      } else {
        await crearEmpresaSST(payload);
        setMensaje("Empresa creada correctamente.");
      }

      await cargarEmpresas();
      cerrarFormulario();
    } catch (err) {
      console.error("Error guardando empresa:", err);
      const detalle = err?.response?.data?.detail;
      setError(typeof detalle === "string" ? detalle : "No fue posible guardar la empresa. Revisa los campos o permisos.");
    } finally {
      setGuardando(false);
    }
  };

  const borrarEmpresa = async (empresa) => {
    if (!empresa?.id) return;

    try {
      setError("");
      setMensaje("");
      setEjecutandoEliminacion(true);
      setEmpresaAEliminar(empresa);

      const validacion = await validarEliminacionEmpresaSST(empresa.id);
      setValidacionEliminacion(validacion);
      setModalEliminacion(true);
    } catch (err) {
      console.error("Error validando eliminación inteligente de empresa:", err);
      setError("No fue posible validar la integridad de la empresa antes de eliminar.");
      setEmpresaAEliminar(null);
      setValidacionEliminacion(null);
      setModalEliminacion(false);
    } finally {
      setEjecutandoEliminacion(false);
    }
  };

  const cerrarModalEliminacion = () => {
    if (ejecutandoEliminacion) return;
    setModalEliminacion(false);
    setEmpresaAEliminar(null);
    setValidacionEliminacion(null);
  };

  const confirmarEliminacionEmpresa = async () => {
    if (!empresaAEliminar?.id) return;

    try {
      setEjecutandoEliminacion(true);
      setError("");
      setMensaje("");

      const resultado = await ejecutarEliminacionInteligenteEmpresaSST(empresaAEliminar.id, "DELETE");
      await cargarEmpresas();
      setMensaje(resultado?.message || "Empresa eliminada definitivamente correctamente.");
      cerrarModalEliminacion();
    } catch (err) {
      console.error("Error ejecutando eliminación inteligente de empresa:", err);
      const detalle = err?.response?.data?.detail;
      setError(
        typeof detalle === "string"
          ? detalle
          : detalle?.message || "No fue posible eliminar la empresa. Verifica permisos o dependencias."
      );
    } finally {
      setEjecutandoEliminacion(false);
    }
  };

  const inactivarEmpresaDesdeModal = async () => {
    if (!empresaAEliminar?.id) return;

    try {
      setEjecutandoEliminacion(true);
      setError("");
      setMensaje("");

      const resultado = await inactivarEmpresaSST(empresaAEliminar.id);
      await cargarEmpresas();
      setMensaje(resultado?.message || "Empresa inactivada correctamente.");
      cerrarModalEliminacion();
    } catch (err) {
      console.error("Error inactivando empresa:", err);
      const detalle = err?.response?.data?.detail;
      setError(
        typeof detalle === "string"
          ? detalle
          : detalle?.message || "No fue posible inactivar la empresa. Verifica permisos SUPER_ADMIN."
      );
    } finally {
      setEjecutandoEliminacion(false);
    }
  };

  const seleccionarLogo = (empresa) => {
    empresaLogoTargetRef.current = empresa;
    fileInputRef.current?.click();
  };

  const handleLogoChange = async (e) => {
    const file = e.target.files?.[0];
    const empresa = empresaLogoTargetRef.current;

    if (!file || !empresa?.id) return;

    try {
      setSubiendoLogoId(empresa.id);
      setError("");
      setMensaje("");
      await subirLogoEmpresaSST(empresa.id, file);
      await cargarEmpresas();
      setMensaje("Logo corporativo actualizado correctamente.");
    } catch (err) {
      console.error("Error subiendo logo:", err);
      setError("No fue posible subir el logo. Usa PNG, JPG, JPEG o WEBP.");
    } finally {
      setSubiendoLogoId(null);
      empresaLogoTargetRef.current = null;
      e.target.value = "";
    }
  };

  const borrarLogo = async (empresa) => {
    const confirmar = window.confirm(`¿Deseas eliminar el logo de "${empresa.nombre}"?`);
    if (!confirmar) return;

    try {
      setSubiendoLogoId(empresa.id);
      setError("");
      setMensaje("");
      await eliminarLogoEmpresaSST(empresa.id);
      await cargarEmpresas();
      setMensaje("Logo eliminado correctamente.");
    } catch (err) {
      console.error("Error eliminando logo:", err);
      setError("No fue posible eliminar el logo corporativo.");
    } finally {
      setSubiendoLogoId(null);
    }
  };

  const exportarCSV = () => {
    const columnas = [
      "ID",
      "Nombre",
      "NIT",
      "Representante Legal",
      "Telefono",
      "Correo",
      "Direccion",
      "Actividad Economica",
      "ARL",
      "Trabajadores",
      "Clase Riesgo",
      "Tipo Empresa",
      "Tipo Estandares SST",
      "Total Estandares SST",
      "Descripcion Estandares SST",
      "Estado",
    ];

    const filas = empresasFiltradas.map((e) => [
      e.id,
      e.nombre,
      e.nit,
      e.representante_legal,
      e.telefono,
      e.correo,
      e.direccion,
      e.actividad_economica,
      e.arl,
      e.numero_trabajadores,
      e.clase_riesgo,
      e.tipo_empresa,
      e.tipo_estandares_sst,
      e.total_estandares_sst,
      e.descripcion_estandares_sst,
      textoEstado(e.estado),
    ]);

    const csv = [columnas, ...filas]
      .map((fila) => fila.map((valor) => `"${String(valor ?? "").replaceAll('"', '""')}"`).join(";"))
      .join("\n");

    descargarArchivo(`\uFEFF${csv}`, `empresas_sst_${new Date().toISOString().slice(0, 10)}.csv`);
  };

  const cambiarPagina = (nuevaPagina) => {
    setPage(Math.min(Math.max(1, nuevaPagina), totalPages));
  };

  const renderLogo = (empresa, size = "normal") => {
    const logoUrl = construirUrlLogoEmpresa(empresa.logo);

    if (logoUrl) {
      return (
        <img
          className={`empresa-logo-img ${size}`}
          src={logoUrl}
          alt={`Logo ${empresa.nombre}`}
          onError={(e) => {
            e.currentTarget.style.display = "none";
          }}
        />
      );
    }

    return <div className={`empresa-logo-fallback ${size}`}>{getInitials(empresa.nombre)}</div>;
  };

  const renderFormularioTab = () => {
    if (tabActiva === "generales") {
      return (
        <div className="form-grid-sst">
          <label>
            Nombre comercial *
            <input name="nombre" value={form.nombre} onChange={handleChange} placeholder="Ej: Clínica Central" />
          </label>

          <label>
            NIT *
            <input name="nit" value={form.nit} onChange={handleChange} placeholder="Ej: 900123456" />
          </label>

          <label>
            Dígito de verificación
            <input name="digito_verificacion" inputMode="numeric" maxLength="1" value={form.digito_verificacion} onChange={handleChange} placeholder="7" />
          </label>

          <label>
            Tipo de empresa
            <select name="tipo_empresa" value={form.tipo_empresa} onChange={handleChange}>
              {TIPOS_EMPRESA.map((tipo) => (
                <option key={tipo} value={tipo}>{tipo}</option>
              ))}
            </select>
          </label>

          <label className="form-switch-sst">
            Estado operativo
            <span>
              <input type="checkbox" name="estado" checked={Boolean(form.estado)} onChange={handleChange} />
              <b>{form.estado ? "ACTIVA" : "INACTIVA"}</b>
            </span>
          </label>
        </div>
      );
    }

    if (tabActiva === "contacto") {
      return (
        <div className="form-grid-sst">
          <label>
            Dirección
            <input name="direccion" value={form.direccion} onChange={handleChange} placeholder="Dirección principal" />
          </label>

          <label>
            Teléfono
            <input name="telefono" value={form.telefono} onChange={handleChange} placeholder="Teléfono corporativo" />
          </label>

          <label>
            Correo corporativo
            <input type="email" name="correo" value={form.correo} onChange={handleChange} placeholder="correo@empresa.com" />
          </label>
        </div>
      );
    }

    if (tabActiva === "sst") {
      return (
        <div className="form-grid-sst">
          <label>
            Representante legal
            <input name="representante_legal" value={form.representante_legal} onChange={handleChange} placeholder="Nombre completo" />
          </label>

          <label>
            Responsable del SG-SST
            <input name="responsable_sst" value={form.responsable_sst} onChange={handleChange} placeholder="Nombre completo" />
          </label>

          <label>
            ARL
            <input name="arl" value={form.arl} onChange={handleChange} placeholder="Ej: SURA, POSITIVA, COLMENA" />
          </label>

          <label className="form-full-sst">
            Actividad económica
            <AutocompleteCIIU
              value={form.actividad_economica}
              onChange={(val) => setForm((prev) => ({ ...prev, actividad_economica: val }))}
              placeholder="Ej: Actividades hospitalarias"
            />
          </label>
        </div>
      );
    }

    return (
      <div className="form-grid-sst">
        <label>
          Clase de riesgo
          <select name="clase_riesgo" value={form.clase_riesgo} onChange={handleChange}>
            {CLASES_RIESGO.map((riesgo) => (
              <option key={riesgo} value={riesgo}>Clase {riesgo}</option>
            ))}
          </select>
        </label>

        <label>
          Número de trabajadores
          <input type="number" min="1" name="numero_trabajadores" value={form.numero_trabajadores} onChange={handleChange} />
        </label>

        <div className="clasificacion-preview-sst form-full-sst">
          <ShieldCheck size={22} />
          <div>
            <strong>Clasificación automática SST</strong>
            <p>
              Al guardar, el backend calcula el tipo de estándares mínimos aplicables según trabajadores,
              clase de riesgo y tipo de empresa.
            </p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <main className="empresas-sst-page">
      <input ref={fileInputRef} type="file" accept="image/png,image/jpeg,image/jpg,image/webp" className="hidden-file-input-sst" onChange={handleLogoChange} />

      <section className="empresas-sst-hero">
        <div className="hero-content-sst">
          <h1>Empresas SST 360°</h1>

          <p>
            Gestiona las empresas y consulta su clasificación y estado SST.
          </p>
        </div>

        <div className="hero-actions-sst">
          <button className="btn-secondary-sst hero-button" onClick={exportarCSV} disabled={!empresasFiltradas.length}>
            <FileSpreadsheet size={18} />
            Exportar
          </button>

          <button className="btn-primary-sst hero-button" onClick={abrirCrear}>
            <Plus size={18} />
            Nueva empresa
          </button>
        </div>
      </section>

      {(error || mensaje) && (
        <section className={error ? "empresas-sst-alert error" : "empresas-sst-alert success"}>
          {error ? <AlertTriangle size={18} /> : <CheckCircle2 size={18} />}
          <span>{error || mensaje}</span>
          <button onClick={() => { setError(""); setMensaje(""); }}><X size={16} /></button>
        </section>
      )}

      <section className="empresas-sst-kpis">
        <button className="empresa-kpi-card" onClick={() => { limpiarFiltros(); }}>
          <div className="kpi-icon blue"><Building2 size={22} /></div>
          <div><span>Total empresas</span><strong>{formatNumber(kpis.total)}</strong></div>
        </button>

        <button className="empresa-kpi-card" onClick={() => setFiltroEstado("ACTIVA")}>
          <div className="kpi-icon green"><ShieldCheck size={22} /></div>
          <div><span>Activas</span><strong>{formatNumber(kpis.activas)}</strong></div>
        </button>

        <button className="empresa-kpi-card" onClick={() => setFiltroEstado("INACTIVA")}>
          <div className="kpi-icon red"><X size={22} /></div>
          <div><span>Inactivas</span><strong>{formatNumber(kpis.inactivas)}</strong></div>
        </button>

        <button className="empresa-kpi-card" onClick={() => setFiltroRiesgo("V")}>
          <div className="kpi-icon amber"><Factory size={22} /></div>
          <div><span>Riesgo IV/V</span><strong>{formatNumber(kpis.riesgoAlto)}</strong></div>
        </button>

        <button className="empresa-kpi-card" onClick={() => { limpiarFiltros(); }}>
          <div className="kpi-icon purple"><Users size={22} /></div>
          <div><span>Trabajadores</span><strong>{formatNumber(kpis.trabajadores)}</strong></div>
        </button>
      </section>

      <section className="riesgos-strip-sst">
        {CLASES_RIESGO.map((riesgo) => (
          <button key={riesgo} className={filtroRiesgo === riesgo ? "riesgo-chip active" : "riesgo-chip"} onClick={() => setFiltroRiesgo(filtroRiesgo === riesgo ? "TODAS" : riesgo)}>
            Riesgo {riesgo}: <strong>{resumenRiesgos[riesgo] || 0}</strong>
          </button>
        ))}
      </section>

      <section className="empresas-sst-panel">
        <div className="empresas-sst-toolbar">
          <div className="search-box-sst">
            <Search size={18} />
            <input type="text" placeholder="Buscar por empresa, NIT, ARL, actividad, representante..." value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
          </div>

          <div className="toolbar-actions-sst">
            <button className="btn-secondary-sst" onClick={limpiarFiltros}>
              <Filter size={17} />
              Limpiar
            </button>

            <button className="btn-secondary-sst" onClick={cargarEmpresas} disabled={cargando}>
              {cargando ? <Loader2 className="spin-sst" size={17} /> : <RefreshCw size={17} />}
              Actualizar
            </button>
          </div>
        </div>

        <div className="filters-grid-sst">
          <label>
            Estado
            <select value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)}>
              <option value="TODAS">Todas</option>
              <option value="ACTIVA">Activas</option>
              <option value="INACTIVA">Inactivas</option>
            </select>
          </label>

          <label>
            Clase de riesgo
            <select value={filtroRiesgo} onChange={(e) => setFiltroRiesgo(e.target.value)}>
              <option value="TODAS">Todas</option>
              {CLASES_RIESGO.map((r) => <option key={r} value={r}>Clase {r}</option>)}
            </select>
          </label>

          <label>
            Tipo empresa
            <select value={filtroTipo} onChange={(e) => setFiltroTipo(e.target.value)}>
              <option value="TODAS">Todas</option>
              {TIPOS_EMPRESA.map((tipo) => <option key={tipo} value={tipo}>{tipo}</option>)}
            </select>
          </label>

          <label>
            ARL
            <select value={filtroArl} onChange={(e) => setFiltroArl(e.target.value)}>
              <option value="TODAS">Todas</option>
              {arlsDisponibles.map((arl) => <option key={arl} value={arl}>{arl}</option>)}
            </select>
          </label>
        </div>

        <div className="empresas-sst-table-wrapper">
          <table className="empresas-sst-table">
            <thead>
              <tr>
                <th>Logo</th>
                <th>Empresa</th>
                <th>NIT</th>
                <th>ARL</th>
                <th>Riesgo</th>
                <th>Trabajadores</th>
                <th>Estándares SST</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {cargando ? (
                <tr><td colSpan="9" className="empty-row"><Loader2 className="spin-sst" size={18} /> Cargando empresas...</td></tr>
              ) : empresasPaginadas.length === 0 ? (
                <tr><td colSpan="9" className="empty-row">No hay empresas que coincidan con los filtros aplicados.</td></tr>
              ) : (
                empresasPaginadas.map((empresa) => (
                  <tr key={empresa.id}>
                    <td>
                      <div className="logo-actions-cell">
                        {renderLogo(empresa)}
                        <button className="mini-logo-btn" onClick={() => seleccionarLogo(empresa)} title="Subir o cambiar logo" disabled={subiendoLogoId === empresa.id}>
                          {subiendoLogoId === empresa.id ? <Loader2 className="spin-sst" size={14} /> : <UploadCloud size={14} />}
                        </button>
                      </div>
                    </td>

                    <td>
                      <div className="empresa-name-cell">
                        <div>
                          <strong>{empresa.nombre}</strong>
                          <span>{empresa.actividad_economica || "Sin actividad económica"}</span>
                        </div>
                      </div>
                    </td>

                    <td>{empresa.nit || "—"}</td>
                    <td>{empresa.arl || "Sin ARL"}</td>

                    <td><span className={`risk-pill risk-${empresa.clase_riesgo || "I"}`}>Clase {empresa.clase_riesgo || "I"}</span></td>
                    <td>{formatNumber(empresa.numero_trabajadores || 0)}</td>

                    <td>
                      <div className="standards-cell">
                        <strong>{empresa.tipo_estandares_sst || "—"}</strong>
                        <span>{empresa.total_estandares_sst || 0} estándares</span>
                      </div>
                    </td>

                    <td><span className={normalizarEstado(empresa.estado) ? "status-pill active" : "status-pill inactive"}>{textoEstado(empresa.estado)}</span></td>

                    <td>
                      <div className="table-actions">
                        <button className="icon-btn view" onClick={() => abrirDetalle(empresa)} title="Ver detalle"><Eye size={16} /></button>
                        <button className="icon-btn edit" onClick={() => abrirEditar(empresa)} title="Editar empresa"><Pencil size={16} /></button>
                        {empresa.logo && <button className="icon-btn logo-delete" onClick={() => borrarLogo(empresa)} title="Eliminar logo"><ImagePlus size={16} /></button>}
                        <button className="icon-btn delete" onClick={() => borrarEmpresa(empresa)} title="Eliminación inteligente"><Trash2 size={16} /></button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="pagination-sst">
          <div className="pagination-info-sst">
            Mostrando <strong>{empresasFiltradas.length ? startIndex + 1 : 0}</strong> - <strong>{endIndex}</strong> de <strong>{empresasFiltradas.length}</strong> empresas
          </div>

          <div className="pagination-controls-sst">
            <label>
              Registros
              <select value={pageSize} onChange={(e) => setPageSize(Number(e.target.value))}>
                {PAGE_SIZE_OPTIONS.map((size) => <option key={size} value={size}>{size}</option>)}
              </select>
            </label>

            <button onClick={() => cambiarPagina(1)} disabled={paginaActual === 1}><ChevronsLeft size={16} /></button>
            <button onClick={() => cambiarPagina(paginaActual - 1)} disabled={paginaActual === 1}><ChevronLeft size={16} /></button>
            <span>Página <strong>{paginaActual}</strong> de <strong>{totalPages}</strong></span>
            <button onClick={() => cambiarPagina(paginaActual + 1)} disabled={paginaActual === totalPages}><ChevronRight size={16} /></button>
            <button onClick={() => cambiarPagina(totalPages)} disabled={paginaActual === totalPages}><ChevronsRight size={16} /></button>
          </div>
        </div>
      </section>

      {modalFormulario && (
        <section className="modal-backdrop-sst">
          <div className="modal-card-sst enterprise-modal-sst">
            <div className="modal-header-sst">
              <div>
                <h2>{empresaSeleccionada ? "Editar empresa SST" : "Nueva empresa SST"}</h2>
                <p>Gestiona la información legal, contacto, ARL y clasificación SST.</p>
              </div>
              <button className="modal-close-sst" onClick={cerrarFormulario}><X size={20} /></button>
            </div>

            <div className="tabs-sst">
              {tabsFormulario.map((tab) => (
                <button key={tab.id} className={tabActiva === tab.id ? "active" : ""} onClick={() => setTabActiva(tab.id)}>{tab.label}</button>
              ))}
            </div>

            <form className="empresa-form-sst" onSubmit={guardarEmpresa}>
              {renderFormularioTab()}

              <div className="modal-actions-sst sticky-actions-sst">
                <button type="button" className="btn-secondary-sst" onClick={cerrarFormulario}>Cancelar</button>
                <button type="submit" className="btn-primary-sst" disabled={guardando}>
                  {guardando ? <Loader2 className="spin-sst" size={17} /> : <Save size={17} />}
                  {guardando ? "Guardando..." : "Guardar empresa"}
                </button>
              </div>
            </form>
          </div>
        </section>
      )}

      {modalDetalle && empresaDetalle && (
        <section className="modal-backdrop-sst">
          <div className="modal-card-sst detail-modal-sst">
            <div className="modal-header-sst detail-header-sst">
              <div className="detail-title-sst">
                {renderLogo(empresaDetalle, "large")}
                <div>
                  <h2>{empresaDetalle.nombre}</h2>
                  <p>NIT {empresaDetalle.nit} · {textoEstado(empresaDetalle.estado)}</p>
                </div>
              </div>
              <button className="modal-close-sst" onClick={cerrarDetalle}><X size={20} /></button>
            </div>

            <div className="detail-grid-sst">
              <article><span>Representante legal</span><strong>{empresaDetalle.representante_legal || "—"}</strong></article>
              <article><span>ARL</span><strong>{empresaDetalle.arl || "—"}</strong></article>
              <article><span>Teléfono</span><strong>{empresaDetalle.telefono || "—"}</strong></article>
              <article><span>Correo</span><strong>{empresaDetalle.correo || "—"}</strong></article>
              <article className="wide"><span>Dirección</span><strong>{empresaDetalle.direccion || "—"}</strong></article>
              <article className="wide"><span>Actividad económica</span><strong>{empresaDetalle.actividad_economica || "—"}</strong></article>
              <article><span>Trabajadores</span><strong>{formatNumber(empresaDetalle.numero_trabajadores || 0)}</strong></article>
              <article><span>Clase de riesgo</span><strong>Clase {empresaDetalle.clase_riesgo || "I"}</strong></article>
              <article><span>Tipo empresa</span><strong>{empresaDetalle.tipo_empresa || "EMPRESA"}</strong></article>
              <article><span>Tipo estándares SST</span><strong>{empresaDetalle.tipo_estandares_sst || "—"}</strong></article>
              <article><span>Total estándares</span><strong>{empresaDetalle.total_estandares_sst || 0}</strong></article>
              <article className="wide"><span>Descripción estándares SST</span><strong>{empresaDetalle.descripcion_estandares_sst || "Sin descripción"}</strong></article>
            </div>

            <div className="modal-actions-sst">
              <button className="btn-secondary-sst" onClick={() => seleccionarLogo(empresaDetalle)}><UploadCloud size={17} /> Subir logo</button>
              <button className="btn-secondary-sst" onClick={cerrarDetalle}>Cerrar</button>
              <button className="btn-primary-sst" onClick={() => { cerrarDetalle(); abrirEditar(empresaDetalle); }}><Pencil size={17} /> Editar</button>
            </div>
          </div>
        </section>
      )}

      <EliminacionInteligenteModal
        abierto={modalEliminacion}
        entidad="empresa"
        registroNombre={empresaAEliminar ? `${empresaAEliminar.nombre} · NIT ${empresaAEliminar.nit || "Sin NIT"}` : "Empresa seleccionada"}
        validacion={validacionEliminacion}
        ejecutando={ejecutandoEliminacion}
        onCancelar={cerrarModalEliminacion}
        onEliminar={confirmarEliminacionEmpresa}
        onInactivar={inactivarEmpresaDesdeModal}
      />

    </main>
  );
}
