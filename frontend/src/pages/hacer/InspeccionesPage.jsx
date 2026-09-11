// ============================================================
// INSPECCIONES SST ENTERPRISE - ERP SST PRO
// FASE 1.1.8.7.9 — INSPECCIONES SST + PDF PLATINUM EXECUTIVE
// Archivo: frontend/src/pages/hacer/InspeccionesPage.jsx
// ============================================================

import React, { useEffect, useMemo, useState, useRef } from "react";
import {
  AlertTriangle,
  BarChart3,
  Building2,
  CalendarCheck,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  Download,
  Edit3,
  LayoutDashboard,
  PanelRightClose,
  PanelRightOpen,
  Settings,
  Sidebar,
  Eye,
  FileText,
  Filter,
  Image as ImageIcon,
  MapPin,
  Paperclip,
  Plus,
  ListChecks,
  Target,
  TrendingUp,
  RefreshCcw,
  Search,
  ShieldAlert,
  Trash2,
  UploadCloud,
  X,
} from "lucide-react";
import {
  actualizarHallazgoInspeccionSST,
  actualizarInspeccionSST,
  crearHallazgoInspeccionSST,
  crearInspeccionSST,
  dashboardInspeccionesSST,
  eliminarEvidenciaInspeccionSST,
  eliminarHallazgoInspeccionSST,
  eliminarInspeccionSST,
  listarEvidenciasInspeccionSST,
  listarHallazgosInspeccionSST,
  listarInspeccionesSST,
  subirEvidenciaInspeccionSST,
  urlArchivoInspeccionSST,
  exportarInspeccionesExcelGeneral,
  exportarInspeccionesPdfGeneral,
  exportarInspeccionPdfIndividual,
  exportarInspeccionActaPdf,
  exportarHallazgosExcel,
  exportarHallazgosPdf,
  exportarSeguimientosPdf,
  exportarDashboardEjecutivoInspeccionesPdf,
  registrarFirmaInspeccionSST,
  cerrarDigitalmenteInspeccionSST,
} from "../../api/inspeccionSstApi";
import {
  listarSeguimientosHallazgo,
  crearSeguimientoHallazgo,
  actualizarSeguimientoHallazgo,
  eliminarSeguimientoHallazgo,
} from "../../api/inspeccionSeguimientoApi";
import InspeccionPdfPlatinumButtons from "../../components/inspecciones/InspeccionPdfPlatinumButtons";
import { listarEmpresasSST } from "../../api/empresaSstApi";
import { listarSedesSST } from "../../api/sedeSstApi";
import { listarAreasSST } from "../../api/areaSstApi";
import { listarCargosSST } from "../../api/cargoSstApi";
import { listarEmpleados } from "../../api/empleadoSstApi";
import "../../styles/inspecciones-sst.css";

const hoy = () => new Date().toISOString().slice(0, 10);

const initialForm = {
  empresa_id: "",
  sede_id: "",
  area_id: "",
  cargo_id: "",
  empleado_id: "",
  codigo: "",
  tipo_inspeccion: "GENERAL",
  titulo: "",
  descripcion: "",
  lugar: "",
  responsable: "",
  fecha_programada: "",
  fecha_inspeccion: hoy(),
  estado: "PROGRAMADA",
  resultado: "PENDIENTE",
  nivel_riesgo: "BAJO",
  cumplimiento: 0,
  observaciones: "",
  activo: true,
};

const initialHallazgo = {
  descripcion: "",
  tipo_hallazgo: "CONDICION_INSEGURA",
  nivel_riesgo: "MEDIO",
  accion_recomendada: "",
  responsable: "",
  fecha_compromiso: "",
  estado: "ABIERTO",
  observaciones: "",
  activo: true,
};

const initialSeguimiento = {
  comentario: "",
  porcentaje_avance: 0,
};

const pick = (obj, keys) => Object.fromEntries(keys.map((k) => [k, obj?.[k] ?? ""]));
const n = (v) => Number(v || 0);
const pct = (v) => Math.max(0, Math.min(100, Number(v || 0)));
const title = (v) => String(v || "").replaceAll("_", " ").toLowerCase().replace(/(^|\s)\S/g, (t) => t.toUpperCase());


const limpiarId = (valor) => {
  if (valor === "" || valor === null || valor === undefined || valor === "TODOS") return null;
  const parsed = Number(valor);
  return Number.isNaN(parsed) ? null : parsed;
};

const limpiarFecha = (valor, fallback = null) => {
  const limpio = String(valor || "").trim();
  return limpio || fallback;
};

const obtenerMensajeError = (error, fallback = "No fue posible guardar la inspección.") => {
  const detail = error?.response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const campo = Array.isArray(item?.loc) ? item.loc.join(" → ") : "campo";
        return `${campo}: ${item?.msg || "valor inválido"}`;
      })
      .join("\n");
  }

  if (typeof detail === "string") return detail;
  if (detail && typeof detail === "object") return JSON.stringify(detail, null, 2);
  return error?.message || fallback;
};

const esImagenEvidencia = (archivo = {}) => {
  const mime = String(archivo.mime_type || "").toLowerCase();
  const ext = String(archivo.extension || archivo.nombre_archivo || archivo.url || "").toLowerCase();
  return mime.startsWith("image/") || ["png", "jpg", "jpeg", "webp", "gif", "bmp"].includes(ext) || /\.(png|jpe?g|webp|gif|bmp)$/i.test(ext);
};

const urlMiniaturaEvidencia = (archivo = {}) =>
  urlArchivoInspeccionSST(archivo.thumbnail_url || archivo.preview_url || archivo.url);

const urlPreviewEvidencia = (archivo = {}) =>
  urlArchivoInspeccionSST(archivo.preview_url || archivo.url || archivo.thumbnail_url);

function MiniBars({ data = [] }) {
  const max = Math.max(...data.map((x) => n(x.value)), 1);
  return (
    <div className="insp-bar-list">
      {data.length ? data.map((item) => (
        <div className="insp-bar-row" key={item.name}>
          <div className="insp-bar-meta"><span>{title(item.name)}</span><b>{item.value}</b></div>
          <div className="insp-bar-track"><i style={{ width: `${(n(item.value) / max) * 100}%` }} /></div>
        </div>
      )) : <small>Sin información registrada.</small>}
    </div>
  );
}

function Kpi({ icon: Icon, label, value, tone = "" }) {
  return <article className={`insp-kpi-card ${tone}`}><div className="insp-kpi-icon"><Icon size={20} /></div><div><small>{label}</small><strong>{value}</strong></div></article>;
}

export default function InspeccionesPage() {
  const [inspecciones, setInspecciones] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [areas, setAreas] = useState([]);
  const [cargos, setCargos] = useState([]);
  const [empleados, setEmpleados] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({ q: "", empresa_id: "", sede_id: "", area_id: "", cargo_id: "", empleado_id: "", estado: "", riesgo: "" });
  const [modal, setModal] = useState(false);
  const [detail, setDetail] = useState(null);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(initialForm);
  const [hallazgos, setHallazgos] = useState([]);
  const [hallazgoForm, setHallazgoForm] = useState(initialHallazgo);
  const [seguimientos, setSeguimientos] = useState({});
  const [seguimientoForm, setSeguimientoForm] = useState({});
  const [evidencias, setEvidencias] = useState([]);
  const [uploadDesc, setUploadDesc] = useState("Evidencia de inspección SST");
  const [uploadType, setUploadType] = useState("EVIDENCIA_FOTOGRAFICA");
  const [uploadFile, setUploadFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [firmaForm, setFirmaForm] = useState({ rol_firma: "INSPECTOR", nombre_firmante: "", firma_base64: "", observacion: "" });
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [notificacion, setNotificacion] = useState(null);
  const notificacionTimerRef = useRef(null);

  const mostrarNotificacion = (tipo = "success", titulo = "", mensaje = "") => {
    if (notificacionTimerRef.current) {
      clearTimeout(notificacionTimerRef.current);
    }

    setNotificacion({ tipo, titulo, mensaje });

    notificacionTimerRef.current = setTimeout(() => {
      setNotificacion(null);
      notificacionTimerRef.current = null;
    }, 5200);
  };

  const construirMensajeError = (error) => {
    if (!error) return "Error desconocido.";
    if (typeof error === "string") return error;
    const data = error?.response?.data;
    if (data?.detail) return typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    if (data?.message) return data.message;
    if (error?.message) return error.message;
    return "Error inesperado.";
  };

  useEffect(() => {
    return () => {
      if (notificacionTimerRef.current) {
        clearTimeout(notificacionTimerRef.current);
      }
    };
  }, []);

  const kpis = dashboard?.kpis || {};
  const charts = dashboard?.charts || {};
  const alertas = dashboard?.alertas || {};

  const hallazgosStats = useMemo(() => {
    const total = hallazgos.length;
    const abiertos = hallazgos.filter((h) => String(h.estado) === "ABIERTO").length;
    const seguimiento = hallazgos.filter((h) => String(h.estado) === "EN_SEGUIMIENTO").length;
    const cerrados = hallazgos.filter((h) => String(h.estado) === "CERRADO").length;
    const criticos = hallazgos.filter((h) => ["ALTO", "CRITICO"].includes(String(h.nivel_riesgo))).length;
    const vencidos = hallazgos.filter((h) => h.fecha_compromiso && h.fecha_compromiso < hoy() && String(h.estado) !== "CERRADO").length;
    const avancePromedio = total
      ? Math.round(hallazgos.reduce((acc, h) => {
          const lista = seguimientos[h.id] || [];
          const ultimo = lista[0];
          if (String(h.estado) === "CERRADO") return acc + 100;
          return acc + Number(ultimo?.porcentaje_avance || 0);
        }, 0) / total)
      : 0;
    const score = Math.max(0, Math.min(100, Math.round((cerrados / Math.max(total, 1)) * 100 - vencidos * 15 - criticos * 8 + avancePromedio * 0.25)));
    const semaforo = !total ? "SIN DATOS" : score >= 80 ? "VERDE" : score >= 50 ? "AMARILLO" : "ROJO";
    return { total, abiertos, seguimiento, cerrados, criticos, vencidos, avancePromedio, score, semaforo };
  }, [hallazgos, seguimientos]);

  const timelineHallazgos = useMemo(() => {
    const items = [];
    hallazgos.forEach((h) => {
      items.push({
        fecha: h.fecha_creacion || h.fecha_compromiso || "",
        titulo: `Hallazgo ${title(h.nivel_riesgo)}`,
        texto: h.descripcion,
        tipo: "hallazgo",
      });
      (seguimientos[h.id] || []).forEach((seg) => {
        items.push({
          fecha: seg.fecha_registro || "",
          titulo: `Seguimiento ${seg.porcentaje_avance || 0}%`,
          texto: seg.comentario,
          tipo: "seguimiento",
        });
      });
    });
    return items.sort((a, b) => new Date(b.fecha || 0) - new Date(a.fecha || 0)).slice(0, 8);
  }, [hallazgos, seguimientos]);

  const cargarCombos = async () => {
    const [emp, sed, ar, car, empl] = await Promise.all([
      listarEmpresasSST().catch(() => []),
      listarSedesSST().catch(() => []),
      listarAreasSST().catch(() => []),
      listarCargosSST().catch(() => []),
      listarEmpleados().catch(() => []),
    ]);
    setEmpresas(emp); setSedes(sed); setAreas(ar); setCargos(car); setEmpleados(empl);
  };

  const cargarDatos = async () => {
    setLoading(true);
    try {
      const params = { ...filters };
      const [lista, dash] = await Promise.all([
        listarInspeccionesSST(params),
        dashboardInspeccionesSST(params),
      ]);
      setInspecciones(lista);
      setDashboard(dash);
      setPage(1);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargarCombos(); }, []);
  useEffect(() => { cargarDatos(); }, []);

  const paginadas = useMemo(() => {
    const start = (page - 1) * pageSize;
    return inspecciones.slice(start, start + pageSize);
  }, [inspecciones, page, pageSize]);
  const totalPages = Math.max(1, Math.ceil(inspecciones.length / pageSize));

  const cargarHallazgosYSeguimientos = async (inspeccionId) => {
    const lista = await listarHallazgosInspeccionSST(inspeccionId).catch(() => []);
    setHallazgos(lista);
    const mapa = {};
    await Promise.all(
      lista.map(async (h) => {
        mapa[h.id] = await listarSeguimientosHallazgo(h.id).catch(() => []);
      })
    );
    setSeguimientos(mapa);
    const forms = {};
    lista.forEach((h) => {
      forms[h.id] = { ...initialSeguimiento };
    });
    setSeguimientoForm(forms);
    return lista;
  };

  const abrirNuevo = () => {
    setEditing(null);
    setDetail(null);
    setHallazgos([]);
    setSeguimientos({});
    setSeguimientoForm({});
    setEvidencias([]);
    setForm({ ...initialForm, codigo: `INSP-${Date.now().toString().slice(-6)}` });
    setModal(true);
  };

  const abrirEditar = async (item) => {
    setEditing(item);
    setDetail(item);
    setForm({ ...initialForm, ...pick(item, Object.keys(initialForm)) });
    await cargarHallazgosYSeguimientos(item.id);
    setEvidencias(await listarEvidenciasInspeccionSST(item.id, item.empresa_id).catch(() => []));
    setModal(true);
  };

  const guardarInspeccion = async () => {
    try {
      const esEdicion = Boolean(editing?.id);
      const payload = {
        ...form,
        empresa_id: limpiarId(form.empresa_id),
        sede_id: limpiarId(form.sede_id),
        area_id: limpiarId(form.area_id),
        cargo_id: limpiarId(form.cargo_id),
        empleado_id: limpiarId(form.empleado_id),
        fecha_programada: limpiarFecha(form.fecha_programada, null),
        fecha_inspeccion: limpiarFecha(form.fecha_inspeccion, hoy()),
        cumplimiento: Number(form.cumplimiento || 0),
        activo: Boolean(form.activo),
      };

      if (!payload.empresa_id || !payload.codigo || !payload.titulo || !payload.fecha_inspeccion) {
        mostrarNotificacion(
          "error",
          "No fue posible guardar la inspección",
          "Empresa, código, título y fecha de inspección son obligatorios."
        );
        return;
      }

      const saved = esEdicion
        ? await actualizarInspeccionSST(editing.id, payload)
        : await crearInspeccionSST(payload);

      setEditing(saved);
      setDetail(saved);
      setForm({ ...initialForm, ...pick(saved, Object.keys(initialForm)) });
      setModal(true);

      await cargarDatos();

      mostrarNotificacion(
        "success",
        esEdicion ? "Inspección actualizada con éxito" : "Inspección guardada con éxito",
        `${saved?.codigo || payload.codigo} · ${saved?.titulo || payload.titulo}`
      );
    } catch (error) {
      console.error("Error guardando inspección", error);
      mostrarNotificacion(
        "error",
        "No fue posible guardar la inspección",
        construirMensajeError(error)
      );
    }
  };

  const eliminar = async (item) => {
    if (!confirm(`¿Anular la inspección ${item.codigo}?`)) return;
    try {
      await eliminarInspeccionSST(item.id);
      await cargarDatos();
      mostrarNotificacion("success", "Inspección anulada", `${item.codigo} · ${item.titulo}`);
    } catch (error) {
      console.error("Error anulando inspección", error);
      mostrarNotificacion("error", "No fue posible anular la inspección", construirMensajeError(error));
    }
  };

  const guardarHallazgo = async () => {
    const targetId = editing?.id || detail?.id;

    if (!targetId) {
      alert("Primero debes guardar la inspección antes de agregar hallazgos.");
      return;
    }

    if (!hallazgoForm.descripcion?.trim()) {
      alert("Debe escribir la descripción del hallazgo.");
      return;
    }

    try {
      const payload = {
        inspeccion_id: Number(targetId),
        empresa_id: Number(
          form.empresa_id || detail?.empresa_id || editing?.empresa_id,
        ),

        descripcion: hallazgoForm.descripcion?.trim(),
        tipo_hallazgo: hallazgoForm.tipo_hallazgo || "CONDICION_INSEGURA",
        nivel_riesgo: hallazgoForm.nivel_riesgo || "MEDIO",
        accion_recomendada: hallazgoForm.accion_recomendada || "",
        responsable: hallazgoForm.responsable || "",
        fecha_compromiso: hallazgoForm.fecha_compromiso || null,
        fecha_cierre: null,
        estado: "ABIERTO",
        observaciones: hallazgoForm.observaciones || "",
        activo: true,
      };

      if (!payload.empresa_id) {
        alert("No fue posible agregar el hallazgo: falta empresa_id.");
        return;
      }

      await crearHallazgoInspeccionSST(targetId, payload);

      mostrarNotificacion("success", "Hallazgo agregado correctamente", hallazgoForm.descripcion?.trim().substring(0, 60));

      setHallazgoForm(initialHallazgo);
      await cargarHallazgosYSeguimientos(targetId);
      await cargarDatos();
    } catch (error) {
      console.error("Error guardando hallazgo", error);

      const detalle =
        error?.response?.data?.detail || error?.message || "Error desconocido";

      if (Array.isArray(detalle)) {
        alert(
          "❌ No fue posible agregar el hallazgo:\n\n" +
            detalle.map((e) => `${e.loc?.join(" → ")}: ${e.msg}`).join("\n"),
        );
      } else {
        alert(`❌ No fue posible agregar el hallazgo.\n\n${detalle}`);
      }
    }
  };

  const cerrarHallazgo = async (h) => {
    await actualizarHallazgoInspeccionSST(h.id, { estado: "CERRADO", fecha_cierre: hoy() });
    await cargarHallazgosYSeguimientos(detail.id);
    await cargarDatos();
  };

  const borrarHallazgo = async (h) => {
    if (!confirm("¿Anular este hallazgo?")) return;
    await eliminarHallazgoInspeccionSST(h.id);
    await cargarHallazgosYSeguimientos(detail.id);
    await cargarDatos();
  };

  const guardarSeguimiento = async (hallazgo) => {
    const formSeg = seguimientoForm[hallazgo.id] || initialSeguimiento;
    if (!formSeg.comentario?.trim()) return alert("Escribe el comentario del seguimiento.");
    await crearSeguimientoHallazgo({
      hallazgo_id: hallazgo.id,
      comentario: formSeg.comentario,
      porcentaje_avance: Number(formSeg.porcentaje_avance || 0),
    });
    if (String(hallazgo.estado) === "ABIERTO") {
      await actualizarHallazgoInspeccionSST(hallazgo.id, { estado: "EN_SEGUIMIENTO" });
    }
    setSeguimientoForm({ ...seguimientoForm, [hallazgo.id]: { ...initialSeguimiento } });
    await cargarHallazgosYSeguimientos(detail.id);
    await cargarDatos();
  };

  const actualizarAvanceSeguimiento = async (seguimiento, payload) => {
    await actualizarSeguimientoHallazgo(seguimiento.id, payload);
    await cargarHallazgosYSeguimientos(detail.id);
  };

  const borrarSeguimiento = async (seguimiento) => {
    if (!confirm("¿Eliminar este seguimiento?")) return;
    await eliminarSeguimientoHallazgo(seguimiento.id);
    await cargarHallazgosYSeguimientos(detail.id);
  };

  const subirEvidencia = async () => {
    const targetId = editing?.id || detail?.id;
    if (!targetId) return alert("Guarda primero la inspección.");
    if (!uploadFile) return alert("Selecciona un archivo.");
    const eid = detail?.empresa_id || editing?.empresa_id || form.empresa_id || filters.empresa_id;
    const fd = new FormData();
    fd.append("tipo_evidencia", uploadType);
    fd.append("descripcion", uploadDesc);
    fd.append("archivo", uploadFile);
    try {
      await subirEvidenciaInspeccionSST(targetId, fd, eid);
      setUploadFile(null);
      setUploadDesc("");
      setEvidencias(await listarEvidenciasInspeccionSST(targetId, eid));
      await cargarDatos();
      mostrarNotificacion("success", "Evidencia subida correctamente", `${uploadFile.name}`);
    } catch (error) {
      console.error("Error subiendo evidencia", error);
      mostrarNotificacion("error", "No fue posible subir la evidencia", construirMensajeError(error));
    }
  };

  const borrarEvidencia = async (archivo) => {
    if (!confirm("¿Eliminar evidencia?")) return;
    const eid = detail?.empresa_id || editing?.empresa_id || form.empresa_id || filters.empresa_id;
    try {
      await eliminarEvidenciaInspeccionSST(detail.id, archivo.id, eid);
      setEvidencias(await listarEvidenciasInspeccionSST(detail.id, eid));
      await cargarDatos();
      mostrarNotificacion("success", "Evidencia eliminada", archivo.nombre_original || "Archivo");
    } catch (error) {
      console.error("Error eliminando evidencia", error);
      mostrarNotificacion("error", "No fue posible eliminar la evidencia", construirMensajeError(error));
    }
  };



  const exportParams = () => ({ empresa_id: filters.empresa_id, sede_id: filters.sede_id, area_id: filters.area_id, estado: filters.estado, riesgo: filters.riesgo });

  const registrarFirma = async () => {
    const targetId = editing?.id || detail?.id;
    if (!targetId) return alert("Guarda primero la inspección.");
    if (!firmaForm.nombre_firmante.trim() || !firmaForm.firma_base64.trim()) return alert("Nombre y firma son obligatorios.");
    const saved = await registrarFirmaInspeccionSST(targetId, firmaForm);
    setEditing(saved);
    setDetail(saved);
    setFirmaForm({ rol_firma: "INSPECTOR", nombre_firmante: "", firma_base64: "", observacion: "" });
    await cargarDatos();
  };

  const cierreDigital = async () => {
    const targetId = editing?.id || detail?.id;
    if (!targetId) return alert("Guarda primero la inspección.");
    if (!confirm("¿Cerrar digitalmente esta inspección? Después quedará marcada como CERRADA.")) return;
    const saved = await cerrarDigitalmenteInspeccionSST(targetId, { observacion: "Cierre digital desde panel Enterprise" });
    setEditing(saved);
    setDetail(saved);
    await cargarDatos();
  };

  const riesgoClass = String(kpis.semaforo || "VERDE").toLowerCase();

  return (
    <main className="inspecciones-sst-page">
      {notificacion && (
        <div
          role="status"
          aria-live="polite"
          style={{
            position: "fixed",
            top: 18,
            right: 18,
            zIndex: 2000,
            width: "min(430px, calc(100vw - 36px))",
            display: "flex",
            gap: 12,
            alignItems: "flex-start",
            padding: "14px 15px",
            borderRadius: 18,
            background: notificacion.tipo === "success" ? "#dcfce7" : "#fee2e2",
            color: notificacion.tipo === "success" ? "#166534" : "#991b1b",
            border: `1px solid ${notificacion.tipo === "success" ? "#bbf7d0" : "#fecaca"}`,
            boxShadow: "0 18px 45px rgba(15, 23, 42, 0.18)",
            fontWeight: 850,
          }}
        >
          {notificacion.tipo === "success" ? (
            <CheckCircle2 size={22} />
          ) : (
            <AlertTriangle size={22} />
          )}
          <div style={{ flex: 1 }}>
            <strong style={{ display: "block", marginBottom: 4 }}>
              {notificacion.titulo}
            </strong>
            {notificacion.mensaje && (
              <span style={{ display: "block", whiteSpace: "pre-wrap", lineHeight: 1.35 }}>
                {notificacion.mensaje}
              </span>
            )}
          </div>
          <button
            type="button"
            onClick={() => setNotificacion(null)}
            style={{
              border: 0,
              background: "rgba(255,255,255,.55)",
              color: "inherit",
              borderRadius: 10,
              width: 28,
              height: 28,
              cursor: "pointer",
              display: "grid",
              placeItems: "center",
            }}
            title="Cerrar mensaje"
          >
            <X size={16} />
          </button>
        </div>
      )}

      <section className="insp-hero">
        <div>
          <h1>Inspecciones SST</h1>
          <p>Controla inspecciones, hallazgos, evidencias y acciones preventivas.</p>
        </div>
        <div className="insp-hero-actions">
          <button className="insp-btn-light" title="Actualizar datos" onClick={cargarDatos}><RefreshCcw size={16} /> Actualizar</button>
          <button
            className="insp-btn-light"
            title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
            onClick={() => setSidebarVisible((v) => !v)}
          >
            {sidebarVisible ? <Sidebar size={16} /> : <LayoutDashboard size={16} />}
          </button>
          <button className="insp-btn-light" title="Exportar Excel" onClick={() => exportarInspeccionesExcelGeneral(exportParams())}><Download size={16} /> Excel</button>
          <button className="insp-btn-light" title="Exportar PDF" onClick={() => exportarInspeccionesPdfGeneral(exportParams())}><FileText size={16} /> PDF</button>
          <button className="insp-btn-light" title="Exportar dashboard PDF" onClick={() => exportarDashboardEjecutivoInspeccionesPdf(exportParams())}><BarChart3 size={16} /> Dashboard PDF</button>
          <button className="insp-btn-primary" title="Registrar nueva inspección" onClick={abrirNuevo}><Plus size={16} /> Nueva inspección</button>
        </div>
      </section>

      <section className={`insp-main-grid${!sidebarVisible ? " insp-panel-collapsed" : ""}`}>
        <div className="insp-content">
          <section className="insp-kpis-grid">
            <Kpi icon={ClipboardCheck} label="Total inspecciones" value={kpis.total || 0} />
            <Kpi icon={CalendarCheck} label="Programadas" value={kpis.programadas || 0} tone="insp-tone-yellow" />
            <Kpi icon={CheckCircle2} label="Ejecutadas" value={kpis.ejecutadas || 0} tone="insp-tone-green" />
            <Kpi icon={ShieldAlert} label="Alto / Crítico" value={kpis.alto_critico || 0} tone="insp-tone-red" />
            <Kpi icon={Paperclip} label="Evidencias" value={kpis.evidencias || 0} tone="insp-tone-purple" />
          </section>

          <section className="insp-indicators-grid">
            <article><small>Cumplimiento</small><strong>{kpis.cumplimiento || 0}%</strong><div><span style={{ width: `${pct(kpis.cumplimiento)}%` }} /></div></article>
            <article><small>Hallazgos abiertos</small><strong>{kpis.hallazgos_abiertos || 0}</strong><div><span style={{ width: `${pct(kpis.hallazgos_abiertos ? 70 : 5)}%` }} /></div></article>
            <article><small>Hallazgos críticos</small><strong>{kpis.hallazgos_criticos || 0}</strong><div><span style={{ width: `${pct(kpis.hallazgos_criticos ? 90 : 5)}%` }} /></div></article>
            <article><small>Inspecciones vencidas</small><strong>{kpis.vencidas || 0}</strong><div><span style={{ width: `${pct(kpis.vencidas ? 90 : 5)}%` }} /></div></article>
          </section>

          <section className="insp-charts-grid">
            <article className="insp-chart-card"><h3><BarChart3 size={15} /> Por tipo</h3><MiniBars data={charts.por_tipo || []} /></article>
            <article className="insp-chart-card"><h3><ActivityIcon /> Por estado</h3><MiniBars data={charts.por_estado || []} /></article>
            <article className="insp-chart-card"><h3><AlertTriangle size={15} /> Por riesgo</h3><MiniBars data={charts.por_riesgo || []} /></article>
            <article className="insp-chart-card"><h3><MapPin size={15} /> Por área</h3><MiniBars data={charts.por_area || []} /></article>
            <article className="insp-chart-card"><h3><Building2 size={15} /> Por cargo</h3><MiniBars data={charts.por_cargo || []} /></article>
            <article className="insp-chart-card"><h3><CheckCircle2 size={15} /> Resultado</h3><MiniBars data={charts.por_resultado || []} /></article>
          </section>

          <section className={`insp-semaforo-card insp-semaforo-${riesgoClass}`}>
            <div><span>Semáforo inspecciones SST</span><h3>{kpis.semaforo || "VERDE"}</h3><p>Cumplimiento: {kpis.cumplimiento || 0}% · Hallazgos abiertos: {kpis.hallazgos_abiertos || 0}</p></div>
            <strong>{kpis.riesgo_score || 0}</strong>
          </section>

          <section className="insp-table-card">
            <div className="insp-filter-top">
              <label className="insp-search"><Search size={16} /><input placeholder="Buscar por código, título, responsable o lugar..." value={filters.q} onChange={(e) => setFilters({ ...filters, q: e.target.value })} /></label>
              <button className="insp-btn-light" onClick={() => setFilters({ q: "", empresa_id: "", sede_id: "", area_id: "", cargo_id: "", empleado_id: "", estado: "", riesgo: "" })}><Filter size={16} /> Limpiar</button>
              <button className="insp-btn-light" onClick={cargarDatos}><RefreshCcw size={16} /> Actualizar</button>
            </div>
            <div className="insp-filters-grid">
              <select value={filters.empresa_id} onChange={(e) => setFilters({ ...filters, empresa_id: e.target.value })}><option value="">Todas las empresas</option>{empresas.map((x) => <option value={x.id} key={x.id}>{x.nombre}</option>)}</select>
              <select value={filters.sede_id} onChange={(e) => setFilters({ ...filters, sede_id: e.target.value })}><option value="">Todas las sedes</option>{sedes.map((x) => <option value={x.id} key={x.id}>{x.nombre}</option>)}</select>
              <select value={filters.area_id} onChange={(e) => setFilters({ ...filters, area_id: e.target.value })}><option value="">Todas las áreas</option>{areas.map((x) => <option value={x.id} key={x.id}>{x.nombre}</option>)}</select>
              <select value={filters.estado} onChange={(e) => setFilters({ ...filters, estado: e.target.value })}><option value="">Todos los estados</option><option>PROGRAMADA</option><option>EN_PROCESO</option><option>EJECUTADA</option><option>CERRADA</option></select>
              <select value={filters.riesgo} onChange={(e) => setFilters({ ...filters, riesgo: e.target.value })}><option value="">Todos los riesgos</option><option>BAJO</option><option>MEDIO</option><option>ALTO</option><option>CRITICO</option></select>
            </div>
            <div className="insp-table-wrap">
              <table>
                <thead><tr><th>Código</th><th>Inspección</th><th>Empresa</th><th>Sede/Área</th><th>Fecha</th><th>Estado</th><th>Riesgo</th><th>Hallazgos</th><th>Evid.</th><th className="insp-th-actions"><Settings size={14} /> Acciones</th></tr></thead>
                <tbody>
                  {paginadas.map((item) => (
                    <tr key={item.id}>
                      <td><b>{item.codigo}</b></td>
                      <td><b>{item.titulo}</b><small>{title(item.tipo_inspeccion)}</small></td>
                      <td>{item.empresa_nombre || "-"}</td>
                      <td>{item.sede_nombre || "-"}<small>{item.area_nombre || "Sin área"}</small></td>
                      <td>{item.fecha_inspeccion}</td>
                      <td><span className={`insp-status ${String(item.estado).toLowerCase()}`}>{title(item.estado)}</span></td>
                      <td><span className={`insp-risk ${String(item.nivel_riesgo).toLowerCase()}`}>{title(item.nivel_riesgo)}</span></td>
                      <td>{item.hallazgos_abiertos}/{item.total_hallazgos}</td>
                      <td>{item.total_evidencias}</td>
                      <td>
                        <div className="insp-actions">
                          <button className="insp-action-btn insp-action-view" onClick={() => abrirEditar(item)} title="Ver detalle"><Eye size={15} /></button>
                          <button className="insp-action-btn insp-action-edit" onClick={() => abrirEditar(item)} title="Editar"><Edit3 size={15} /></button>
                          <span className="insp-action-sep" />
                          <InspeccionPdfPlatinumButtons inspeccionId={item.id} compacto />
                          <span className="insp-action-sep" />
                          <button className="insp-action-btn insp-action-delete" onClick={() => eliminar(item)} title="Eliminar"><Trash2 size={15} /></button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {!paginadas.length && <tr><td colSpan="10" className="insp-empty">No hay inspecciones registradas.</td></tr>}
                </tbody>
              </table>
            </div>
            <div className="insp-pagination"><span>Mostrando <b>{paginadas.length}</b> de <b>{inspecciones.length}</b> inspecciones</span><div className="insp-page-controls"><label>Registros<select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}><option>10</option><option>25</option><option>50</option></select></label><button disabled={page <= 1} onClick={() => setPage(page - 1)}>‹</button><span>Página {page}/{totalPages}</span><button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>›</button></div></div>
          </section>
        </div>

        <aside className={`insp-right-panel${!sidebarVisible ? " insp-panel-hidden" : ""}`} aria-label="Dashboard lateral inteligente de Inspecciones SST">
          {sidebarVisible && (<>
          <article className="insp-intel-card">
            <div className="insp-side-title-row">
              <h3>Dashboard inteligente</h3>
              <div className="insp-sidebar-header-actions">
                <button
                  type="button"
                  className="insp-sidebar-toggle-btn"
                  onClick={() => setSidebarVisible((v) => !v)}
                  title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
                  aria-label={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
                  aria-pressed={!sidebarVisible}
                >
                  {sidebarVisible ? <Sidebar size={18} /> : <LayoutDashboard size={18} />}
                </button>
                <span className="insp-ai-badge">AI</span>
              </div>
            </div>
            <div className="insp-intel-body"><div className="insp-ring" style={{ "--insp-ring": `${pct(kpis.cumplimiento || 0)}%` }}><strong>{kpis.cumplimiento || 0}%</strong><span>Índice inspección</span></div><div><h4>{kpis.semaforo === "ROJO" ? "Gestión crítica" : kpis.semaforo === "AMARILLO" ? "Gestión con pendientes" : "Gestión estable"}</h4><p>Seguimiento de inspecciones, hallazgos, evidencias y acciones preventivas.</p><em className={kpis.semaforo === "VERDE" ? "ok" : "warn"}>{kpis.semaforo === "VERDE" ? "Excelente" : "Revisar"}</em></div></div>
          </article>
          <article className="insp-side-card"><div className="insp-side-title-row"><h3><AlertTriangle size={17} /> Alertas SST</h3><b>{(alertas.vencidas || 0) + (alertas.hallazgos_criticos || 0)} críticas</b></div><p>Vencidas <strong>{alertas.vencidas || 0}</strong></p><p>Alto/crítico <strong>{alertas.alto_critico || 0}</strong></p><p>Hallazgos abiertos <strong>{alertas.hallazgos_abiertos || 0}</strong></p><p>Sin evidencia <strong>{alertas.sin_evidencia || 0}</strong></p></article>
          <article className="insp-side-card"><div className="insp-side-title-row"><h3><BarChart3 size={17} /> Distribución base</h3></div><p>Total <strong>{kpis.total || 0}</strong></p><p>Ejecutadas <strong>{kpis.ejecutadas || 0}</strong></p><p>Cerradas <strong>{kpis.cerradas || 0}</strong></p><p>Hallazgos <strong>{kpis.hallazgos || 0}</strong></p></article>
          <article className="insp-side-card insp-export-card"><div className="insp-side-title-row"><h3><Download size={17} /> Exportaciones</h3><span>PDF/Excel</span></div><button onClick={() => exportarHallazgosExcel(exportParams())}>Hallazgos Excel</button><button onClick={() => exportarHallazgosPdf(exportParams())}>Hallazgos PDF</button><button onClick={() => exportarSeguimientosPdf({ inspeccion_id: detail?.id || "" })}>Seguimientos PDF</button></article>
          <article className="insp-side-card"><div className="insp-side-title-row"><h3>Recomendaciones PRO</h3><span>PRO</span></div><ul>{(dashboard?.recomendaciones || []).map((r, i) => <li key={i}>{r}</li>)}</ul></article>
          </>)}
          {!sidebarVisible && (
            <button
              type="button"
              className="insp-sidebar-toggle-btn insp-sidebar-toggle-floating"
              onClick={() => setSidebarVisible((v) => !v)}
              title="Mostrar panel lateral"
              aria-label="Mostrar panel lateral"
            >
              <LayoutDashboard size={18} />
            </button>
          )}
        </aside>
      </section>

      {modal && (
        <div className="insp-modal-backdrop">
          <section className="insp-form-modal">
            <header className="insp-modal-header"><div><span>{editing ? "Editar inspección" : "Nueva inspección"}</span><h2>{form.titulo || "Inspección SST"}</h2><p>Información general, hallazgos, evidencias y trazabilidad preventiva.</p></div><button className="insp-close" onClick={() => setModal(false)}><X size={20} /></button></header>
            <div className="insp-modal-body">
              <div className="insp-form-grid">
                <label>Empresa *<select value={form.empresa_id} onChange={(e) => setForm({ ...form, empresa_id: e.target.value })}><option value="">Seleccione...</option>{empresas.map((x) => <option value={x.id} key={x.id}>{x.nombre}</option>)}</select></label>
                <label>Código *<input value={form.codigo} onChange={(e) => setForm({ ...form, codigo: e.target.value })} /></label>
                <label className="insp-full">Título *<input value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} /></label>
                <label>Tipo<select value={form.tipo_inspeccion} onChange={(e) => setForm({ ...form, tipo_inspeccion: e.target.value })}><option>GENERAL</option><option>LOCATIVA</option><option>EPP</option><option>MAQUINARIA</option><option>ORDEN_ASEO</option><option>SEGURIDAD</option></select></label>
                <label>Fecha inspección<input type="date" value={form.fecha_inspeccion} onChange={(e) => setForm({ ...form, fecha_inspeccion: e.target.value })} /></label>
                <label>Sede<select value={form.sede_id || ""} onChange={(e) => setForm({ ...form, sede_id: e.target.value })}><option value="">Sin sede</option>{sedes.map((x) => <option value={x.id} key={x.id}>{x.nombre}</option>)}</select></label>
                <label>Área<select value={form.area_id || ""} onChange={(e) => setForm({ ...form, area_id: e.target.value })}><option value="">Sin área</option>{areas.map((x) => <option value={x.id} key={x.id}>{x.nombre}</option>)}</select></label>
                <label>Estado<select value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })}><option>PROGRAMADA</option><option>EN_PROCESO</option><option>EJECUTADA</option><option>CERRADA</option><option>ANULADA</option></select></label>
                <label>Riesgo<select value={form.nivel_riesgo} onChange={(e) => setForm({ ...form, nivel_riesgo: e.target.value })}><option>BAJO</option><option>MEDIO</option><option>ALTO</option><option>CRITICO</option></select></label>
                <label>Cumplimiento<input type="number" min="0" max="100" value={form.cumplimiento} onChange={(e) => setForm({ ...form, cumplimiento: e.target.value })} /></label>
                <label>Responsable<input value={form.responsable || ""} onChange={(e) => setForm({ ...form, responsable: e.target.value })} /></label>
                <label className="insp-full">Descripción<textarea value={form.descripcion || ""} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} /></label>
              </div>

              <section className="insp-subpanel insp-hallazgos-pro-panel">
                <div className="insp-hallazgos-head">
                  <div>
                    <h3><ListChecks size={18} /> Hallazgos y planes de acción</h3>
                    <p>Gestión de hallazgos, responsables, fechas compromiso, avances y cierre preventivo.</p>
                  </div>
                  <span className={`insp-hallazgos-semaforo ${String(hallazgosStats.semaforo).toLowerCase().replaceAll(" ", "-")}`}>
                    {hallazgosStats.semaforo}
                  </span>
                </div>

                <div className="insp-hallazgos-dashboard">
                  <article><Target size={16} /><small>Total</small><strong>{hallazgosStats.total}</strong></article>
                  <article><AlertTriangle size={16} /><small>Abiertos</small><strong>{hallazgosStats.abiertos}</strong></article>
                  <article><Clock3 size={16} /><small>Seguimiento</small><strong>{hallazgosStats.seguimiento}</strong></article>
                  <article><CheckCircle2 size={16} /><small>Cerrados</small><strong>{hallazgosStats.cerrados}</strong></article>
                  <article><ShieldAlert size={16} /><small>Críticos</small><strong>{hallazgosStats.criticos}</strong></article>
                  <article><TrendingUp size={16} /><small>Avance</small><strong>{hallazgosStats.avancePromedio}%</strong></article>
                </div>

                <div className="insp-hallazgos-form-pro">
                  <input placeholder="Descripción del hallazgo" value={hallazgoForm.descripcion} onChange={(e) => setHallazgoForm({ ...hallazgoForm, descripcion: e.target.value })} />
                  <select value={hallazgoForm.tipo_hallazgo} onChange={(e) => setHallazgoForm({ ...hallazgoForm, tipo_hallazgo: e.target.value })}>
                    <option>CONDICION_INSEGURA</option><option>ACTO_INSEGURO</option><option>INCUMPLIMIENTO</option><option>MEJORA</option>
                  </select>
                  <select value={hallazgoForm.nivel_riesgo} onChange={(e) => setHallazgoForm({ ...hallazgoForm, nivel_riesgo: e.target.value })}><option>BAJO</option><option>MEDIO</option><option>ALTO</option><option>CRITICO</option></select>
                  <input placeholder="Responsable" value={hallazgoForm.responsable || ""} onChange={(e) => setHallazgoForm({ ...hallazgoForm, responsable: e.target.value })} />
                  <input type="date" value={hallazgoForm.fecha_compromiso || ""} onChange={(e) => setHallazgoForm({ ...hallazgoForm, fecha_compromiso: e.target.value })} />
                  <button className="insp-btn-light" onClick={guardarHallazgo}><Plus size={16} /> Agregar</button>
                  <textarea placeholder="Acción recomendada / plan de acción" value={hallazgoForm.accion_recomendada || ""} onChange={(e) => setHallazgoForm({ ...hallazgoForm, accion_recomendada: e.target.value })} />
                </div>

                <div className="insp-hallazgos-grid-pro">
                  <div className="insp-hallazgos-list-pro">
                    {hallazgos.map((h) => {
                      const formSeg = seguimientoForm[h.id] || initialSeguimiento;
                      const listaSeg = seguimientos[h.id] || [];
                      const ultimo = listaSeg[0];
                      const avance = String(h.estado) === "CERRADO" ? 100 : Number(ultimo?.porcentaje_avance || 0);
                      return (
                        <article className="insp-hallazgo-card-pro" key={h.id}>
                          <header>
                            <span className={`insp-risk ${String(h.nivel_riesgo).toLowerCase()}`}>{title(h.nivel_riesgo)}</span>
                            <b>{h.descripcion}</b>
                            <em>{title(h.estado)}</em>
                          </header>
                          <p>{h.accion_recomendada || "Sin acción recomendada registrada."}</p>
                          <div className="insp-hallazgo-meta">
                            <span>Responsable: <b>{h.responsable || "Sin responsable"}</b></span>
                            <span>Compromiso: <b>{h.fecha_compromiso || "Sin fecha"}</b></span>
                            <span>Seguimientos: <b>{listaSeg.length}</b></span>
                          </div>
                          <div className="insp-hallazgo-progress"><i style={{ width: `${pct(avance)}%` }} /></div>
                          <div className="insp-seguimiento-form">
                            <input placeholder="Comentario de seguimiento" value={formSeg.comentario || ""} onChange={(e) => setSeguimientoForm({ ...seguimientoForm, [h.id]: { ...formSeg, comentario: e.target.value } })} />
                            <input type="number" min="0" max="100" value={formSeg.porcentaje_avance || 0} onChange={(e) => setSeguimientoForm({ ...seguimientoForm, [h.id]: { ...formSeg, porcentaje_avance: e.target.value } })} />
                            <button className="insp-btn-light" onClick={() => guardarSeguimiento(h)}><Plus size={15} /> Seguimiento</button>
                          </div>
                          <div className="insp-seguimiento-list">
                            {listaSeg.slice(0, 3).map((seg) => (
                              <div key={seg.id}>
                                <span>{new Date(seg.fecha_registro).toLocaleDateString()}</span>
                                <b>{seg.porcentaje_avance}%</b>
                                <p>{seg.comentario}</p>
                                <button onClick={() => borrarSeguimiento(seg)}><Trash2 size={13} /></button>
                              </div>
                            ))}
                          </div>
                          <footer>
                            <button className="insp-btn-light" onClick={() => actualizarAvanceSeguimiento(ultimo, { porcentaje_avance: 100, comentario: ultimo?.comentario })} disabled={!ultimo || String(h.estado) === "CERRADO"}>Avance 100%</button>
                            <button className="insp-btn-light" onClick={() => cerrarHallazgo(h)} disabled={String(h.estado) === "CERRADO"}><CheckCircle2 size={15} /> Cerrar</button>
                            <button className="insp-btn-light" onClick={() => borrarHallazgo(h)}><Trash2 size={15} /> Anular</button>
                          </footer>
                        </article>
                      );
                    })}
                    {!hallazgos.length && <div className="insp-empty-card">No hay hallazgos registrados. Agrega el primer hallazgo para activar el plan de acción.</div>}
                  </div>

                  <aside className="insp-timeline-pro">
                    <h3><Clock3 size={17} /> Timeline correctivo</h3>
                    {timelineHallazgos.map((t, i) => (
                      <div key={`${t.tipo}-${i}`}>
                        <i />
                        <b>{t.titulo}</b>
                        <small>{t.fecha ? new Date(t.fecha).toLocaleString() : "Sin fecha"}</small>
                        <span>{t.texto}</span>
                      </div>
                    ))}
                    {!timelineHallazgos.length && <p>Sin eventos de seguimiento registrados.</p>}
                  </aside>
                </div>
              </section>

              <section className="insp-subpanel insp-workflow-card">
                <h3><ClipboardCheck size={17} /> Workflow, firmas y cierre digital</h3>
                <div className="insp-export-row">
                  <button className="insp-btn-light" disabled={!detail?.id} onClick={() => exportarInspeccionPdfIndividual(detail.id)}><FileText size={15} /> PDF Individual</button>
                  <button className="insp-btn-light" disabled={!detail?.id} onClick={() => exportarInspeccionActaPdf(detail.id)}><FileText size={15} /> Acta PDF</button>
                  {/* ============================================================
                      PDF EJECUTIVO PLATINUM
                      ------------------------------------------------------------
                      Botones de vista previa y descarga del Reporte PDF Ejecutivo
                      Platinum. Este componente consume la ruta backend:
                      GET /inspecciones-exportaciones-platinum/{id}/pdf-platinum
                  ============================================================ */}
                  <InspeccionPdfPlatinumButtons inspeccionId={detail?.id} disabled={!detail?.id} />
                  <button className="insp-btn-primary" disabled={!detail?.id || detail?.cierre_digital} onClick={cierreDigital}><CheckCircle2 size={15} /> Cierre digital</button>
                </div>
                <div className="insp-firmas-status">
                  <span className={detail?.firma_inspector ? "ok" : "pending"}>Inspector: {detail?.firma_inspector_nombre || "Pendiente"}</span>
                  <span className={detail?.firma_responsable_area ? "ok" : "pending"}>Responsable Área: {detail?.firma_responsable_area_nombre || "Pendiente"}</span>
                  <span className={detail?.firma_sst ? "ok" : "pending"}>SST: {detail?.firma_sst_nombre || "Pendiente"}</span>
                  <span className={detail?.cierre_digital ? "ok" : "pending"}>Cierre: {detail?.cierre_digital ? "Cerrada digitalmente" : "Pendiente"}</span>
                </div>
                <div className="insp-firma-form">
                  <select value={firmaForm.rol_firma} onChange={(e) => setFirmaForm({ ...firmaForm, rol_firma: e.target.value })}><option value="INSPECTOR">Inspector</option><option value="RESPONSABLE_AREA">Responsable Área</option><option value="SST">SST</option></select>
                  <input placeholder="Nombre del firmante" value={firmaForm.nombre_firmante} onChange={(e) => setFirmaForm({ ...firmaForm, nombre_firmante: e.target.value })} />
                  <input placeholder="Firma digital/base64 o hash" value={firmaForm.firma_base64} onChange={(e) => setFirmaForm({ ...firmaForm, firma_base64: e.target.value })} />
                  <button className="insp-btn-light" onClick={registrarFirma}>Registrar firma</button>
                </div>
                {detail?.trazabilidad && <pre className="insp-trazabilidad">{detail.trazabilidad}</pre>}
              </section>

              <section className="insp-subpanel">
                <h3><Paperclip size={17} /> Evidencias</h3>
                <div className="insp-upload-row"><select value={uploadType} onChange={(e) => setUploadType(e.target.value)}><option>EVIDENCIA_FOTOGRAFICA</option><option>ACTA_INSPECCION</option><option>SOPORTE_PDF</option><option>OTRO</option></select><input value={uploadDesc} onChange={(e) => setUploadDesc(e.target.value)} /><label className="insp-file-pill"><UploadCloud size={16} /> Archivo<input type="file" onChange={(e) => setUploadFile(e.target.files?.[0] || null)} /></label><button className="insp-btn-primary" onClick={subirEvidencia}>Subir</button></div>
                {uploadFile && <small>Seleccionado: {uploadFile.name}</small>}
                {evidencias.map((a) => (
                  <div className="insp-file-row" key={a.id}>
                    <span className={esImagenEvidencia(a) ? "insp-file-thumb" : ""}>
                      {esImagenEvidencia(a) ? (
                        <img
                          src={urlMiniaturaEvidencia(a)}
                          alt={a.nombre_original || "Miniatura evidencia SST"}
                          onError={(event) => { event.currentTarget.style.display = "none"; }}
                        />
                      ) : (
                        <FileText size={18} />
                      )}
                    </span>
                    <div>
                      <b>{a.nombre_original}</b>
                      <small>{a.descripcion}{a.optimizacion?.thumbnail ? " · Miniatura Enterprise" : ""}</small>
                    </div>
                    <button onClick={() => setPreview({ ...a, preview_src: urlPreviewEvidencia(a) })} title="Ver evidencia">
                      <Eye size={15} />
                    </button>
                    <a href={urlArchivoInspeccionSST(a.url)} target="_blank" rel="noreferrer" title="Descargar evidencia">
                      <Download size={15} />
                    </a>
                    <button className="danger" onClick={() => borrarEvidencia(a)} title="Eliminar evidencia">
                      <Trash2 size={15} />
                    </button>
                  </div>
                ))}
              </section>
            </div>
            <footer className="insp-modal-footer"><button className="insp-btn-light" onClick={() => setModal(false)}>Cerrar</button><button className="insp-btn-primary" onClick={guardarInspeccion}>Guardar inspección</button></footer>
          </section>
        </div>
      )}

      {preview && (
        <div className="insp-preview-backdrop">
          <section className="insp-preview-modal">
            <header>
              <b>{preview.nombre_original}</b>
              <button onClick={() => setPreview(null)}><X size={18} /></button>
            </header>
            {esImagenEvidencia(preview) ? (
              <img src={preview.preview_src || urlPreviewEvidencia(preview)} alt={preview.nombre_original || "Evidencia SST"} />
            ) : (
              <iframe src={preview.preview_src || urlPreviewEvidencia(preview)} title="preview" />
            )}
          </section>
        </div>
      )}
    </main>
  );
}

function ActivityIcon() { return <span style={{ width: 15, height: 15, display: "inline-block" }}>⌁</span>; }
