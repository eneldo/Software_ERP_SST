// ============================================================
// GESTIÓN ADMINISTRATIVA REPORTES ANÓNIMOS SST
// ERP SST PRO
// FASE 1.1.25.5 — WORKFLOW INTELIGENTE REPORTES SST
// Archivo: frontend/src/pages/verificar/ReportesAnonimosSSTPage.jsx
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Archive,
  Bell,
  CheckCircle2,
  ClipboardCheck,
  Download,
  Eye,
  FileImage,
  Filter,
  Loader2,
  RefreshCw,
  Search,
  ShieldAlert,
  UserCheck,
  X,
  XCircle,
  Zap,
  Target,
  GitBranch,
  Wrench,
  Users,
} from "lucide-react";

import {
  anularReporteAnonimoSST,
  asignarReporteAnonimoSST,
  cerrarReporteAnonimoSST,
  crearCAPADesdeReporteSST,
  crearHallazgoDesdeReporteSST,
  crearInspeccionDesdeReporteSST,
  dashboardReportesAnonimosSST,
  listarReportesAnonimosSST,
  listarResponsablesSST,
  marcarReporteAnonimoEnProcesoSST,
  listarEvidenciasReporteSST,
  subirEvidenciasReporteSST,
  eliminarEvidenciaReporteSST,
  timelineReporteSST,
} from "../../api/reportesAnonimosAdminApi";
import { listarEmpresasSST } from "../../api/empresaSstApi";
import { listarAreasSST } from "../../api/areaSstApi";
import ReporteGaleriaEvidencias from "../../components/reportes/ReporteGaleriaEvidencias";
import ReporteUploader from "../../components/reportes/ReporteUploader";
import ReporteTimeline from "../../components/reportes/ReporteTimeline";
import "../../styles/reportes-anonimos-admin.css";
import "../../styles/reportes-evidencias.css";

const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const initialDashboard = {
  total: 0,
  reportados: 0,
  asignados: 0,
  en_proceso: 0,
  cerrados: 0,
  anulados: 0,
  criticos: 0,
  altos: 0,
  medios: 0,
  bajos: 0,
  con_evidencia: 0,
  pendientes: 0,
  sin_asignar: 0,
  gestionados_inspeccion: 0,
  gestionados_capa: 0,
  por_tipo: {},
  por_prioridad: {},
  por_estado: {},
  por_area: {},
  por_responsable: {},
  recomendaciones: [],
};

const estadoLabel = {
  REPORTADO: "Reportado",
  ASIGNADO: "Asignado",
  EN_PROCESO: "En proceso",
  CERRADO: "Cerrado",
  ANULADO: "Anulado",
};

const tipoLabel = {
  ACTO_INSEGURO: "Acto inseguro",
  CONDICION_INSEGURA: "Condición insegura",
  INCIDENTE: "Incidente",
  ACCIDENTE: "Accidente",
  SUGERENCIA: "Sugerencia SST",
};

const limpiarParams = (params = {}) =>
  Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== "" && v !== null && v !== undefined && v !== "TODOS")
  );

const safeList = (data) => {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.data)) return data.data;
  if (Array.isArray(data?.casos)) return data.casos;
  return [];
};

const fechaHumana = (value) => {
  if (!value) return "Sin fecha";
  try {
    return new Date(value).toLocaleString("es-CO", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return value;
  }
};

const assetUrl = (url) => {
  if (!url) return "";
  if (/^https?:\/\//i.test(url)) return url;
  return `${API_BASE}${url.startsWith("/") ? url : `/${url}`}`;
};

const esImagen = (reporte = {}) => {
  const mime = String(reporte.archivo_mime_type || "").toLowerCase();
  const url = String(reporte.archivo_url || reporte.archivo_nombre || "").toLowerCase();
  return mime.includes("image") || /\.(jpg|jpeg|png|webp|gif)$/i.test(url);
};

const mostrarError = (error, fallback = "Ocurrió un error") => {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((e) => `${e.loc?.join(" → ")}: ${e.msg}`).join("\n");
  if (typeof detail === "string") return detail;
  return error?.message || fallback;
};

export default function ReportesAnonimosSSTPage() {
  const [loading, setLoading] = useState(true);
  const [accionLoading, setAccionLoading] = useState(false);
  const [reportes, setReportes] = useState([]);
  const [dashboard, setDashboard] = useState(initialDashboard);
  const [empresas, setEmpresas] = useState([]);
  const [areas, setAreas] = useState([]);
  const [responsables, setResponsables] = useState([]);
  const [detalle, setDetalle] = useState(null);
  const [evidenciasDetalle, setEvidenciasDetalle] = useState([]);
  const [timelineDetalle, setTimelineDetalle] = useState([]);
  const [subiendoEvidencias, setSubiendoEvidencias] = useState(false);
  const [alerta, setAlerta] = useState(null);
  const [pageSize, setPageSize] = useState(10);
  const [page, setPage] = useState(1);
  const [filtros, setFiltros] = useState({
    empresa_id: "TODOS",
    area_id: "TODOS",
    tipo_reporte: "TODOS",
    prioridad: "TODOS",
    estado: "TODOS",
    responsable: "TODOS",
    con_evidencia: "TODOS",
    buscar: "",
  });
  const [asignacion, setAsignacion] = useState({ responsable_empleado_id: "", responsable_asignado: "", observaciones: "" });
  const [cierre, setCierre] = useState({ accion_cierre: "", observaciones: "" });
  const [workflow, setWorkflow] = useState({ fecha_compromiso_dias: 15, observaciones: "" });

  const params = useMemo(() => {
    const data = { ...filtros };
    if (data.con_evidencia === "SI") data.con_evidencia = true;
    if (data.con_evidencia === "NO") data.con_evidencia = false;
    return limpiarParams(data);
  }, [filtros]);

  const totalPages = Math.max(1, Math.ceil(reportes.length / pageSize));
  const visible = reportes.slice((page - 1) * pageSize, page * pageSize);

  const cargarCatalogos = async () => {
    try {
      const [emp, ar, resp] = await Promise.all([
        listarEmpresasSST().catch(() => []),
        listarAreasSST().catch(() => []),
        listarResponsablesSST().catch(() => []),
      ]);
      setEmpresas(safeList(emp));
      setAreas(safeList(ar));
      setResponsables(safeList(resp));
    } catch (error) {
      console.warn("No se pudieron cargar catálogos", error);
    }
  };

  const cargarDatos = async () => {
    setLoading(true);
    try {
      const [dash, list] = await Promise.all([
        dashboardReportesAnonimosSST(params),
        listarReportesAnonimosSST(params),
      ]);
      setDashboard({ ...initialDashboard, ...(dash || {}) });
      setReportes(safeList(list));
      setPage(1);
    } catch (error) {
      setAlerta({ type: "error", text: mostrarError(error, "No fue posible cargar reportes anónimos SST") });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarCatalogos();
  }, []);

  useEffect(() => {
    cargarDatos();
  }, [params.empresa_id, params.area_id, params.tipo_reporte, params.prioridad, params.estado, params.responsable, params.con_evidencia]);

  const onBuscar = (e) => {
    e.preventDefault();
    cargarDatos();
  };

  const limpiarFiltros = () => {
    setFiltros({
      empresa_id: "TODOS",
      area_id: "TODOS",
      tipo_reporte: "TODOS",
      prioridad: "TODOS",
      estado: "TODOS",
      responsable: "TODOS",
      con_evidencia: "TODOS",
      buscar: "",
    });
  };

  const abrirDetalle = async (item) => {
    setDetalle(item);
    setEvidenciasDetalle(item.evidencias || []);
    try {
      const [evs, tl] = await Promise.all([listarEvidenciasReporteSST(item.id), timelineReporteSST(item.id)]);
      setEvidenciasDetalle(evs);
      setTimelineDetalle(tl);
    } catch (error) {
      console.error(error);
    }
    const match = responsables.find((r) => r.nombre === item.responsable_asignado);
    setAsignacion({
      responsable_empleado_id: match?.id || "",
      responsable_asignado: item.responsable_asignado || "",
      observaciones: "",
    });
    setCierre({ accion_cierre: "", observaciones: "" });
    setWorkflow({ fecha_compromiso_dias: 15, observaciones: "" });
  };

  const ejecutar = async (fn, okMsg) => {
    setAccionLoading(true);
    try {
      const actualizado = await fn();
      setAlerta({ type: "success", text: okMsg || actualizado?.mensaje || "Acción realizada correctamente." });
      if (actualizado?.id) setDetalle(actualizado);
      await cargarDatos();
    } catch (error) {
      setAlerta({ type: "error", text: mostrarError(error, "No fue posible completar la acción") });
    } finally {
      setAccionLoading(false);
    }
  };

  const asignar = () => {
    if (!detalle?.id) return;
    if (!asignacion.responsable_empleado_id && !asignacion.responsable_asignado.trim()) {
      setAlerta({ type: "error", text: "Debe seleccionar o escribir el responsable SST." });
      return;
    }
    ejecutar(() => asignarReporteAnonimoSST(detalle.id, {
      responsable_empleado_id: asignacion.responsable_empleado_id || null,
      responsable_asignado: asignacion.responsable_asignado || null,
      observaciones: asignacion.observaciones,
    }), "Reporte asignado correctamente.");
  };

  const cerrar = () => {
    if (!detalle?.id) return;
    ejecutar(() => cerrarReporteAnonimoSST(detalle.id, cierre), "Reporte cerrado correctamente.");
  };

  const enProceso = (item) => ejecutar(() => marcarReporteAnonimoEnProcesoSST(item.id), "Reporte marcado en proceso.");
  const crearInspeccion = (item) => ejecutar(() => crearInspeccionDesdeReporteSST(item.id, { ...workflow, responsable: item.responsable_asignado }), "Inspección SST creada desde el reporte.");
  const crearHallazgo = (item) => ejecutar(() => crearHallazgoDesdeReporteSST(item.id, { ...workflow, responsable: item.responsable_asignado }), "Hallazgo SST creado desde el reporte.");
  const crearCAPA = (item) => ejecutar(() => crearCAPADesdeReporteSST(item.id, { ...workflow, responsable: item.responsable_asignado }), "CAPA creada desde el reporte.");

  const anular = (item) => {
    const motivo = window.prompt("Motivo de anulación del reporte SST:");
    if (motivo === null) return;
    ejecutar(() => anularReporteAnonimoSST(item.id, motivo || "Anulado desde administración"), "Reporte anulado correctamente.");
  };


  const subirEvidenciasDetalle = async (files) => {
    if (!detalle?.id) return;
    try {
      setSubiendoEvidencias(true);
      const nuevas = await subirEvidenciasReporteSST(detalle.id, files);
      const evs = await listarEvidenciasReporteSST(detalle.id);
      const tl = await timelineReporteSST(detalle.id);
      setEvidenciasDetalle(evs);
      setTimelineDetalle(tl);
      setDetalle((prev) => prev ? { ...prev, evidencias: evs, total_evidencias: evs.length, archivo_url: prev.archivo_url || nuevas?.[0]?.archivo_url } : prev);
      await cargarDatos();
    } catch (error) {
      alert(mostrarError(error, "No fue posible subir las evidencias"));
    } finally {
      setSubiendoEvidencias(false);
    }
  };

  const eliminarEvidenciaDetalle = async (ev) => {
    if (!ev?.id || !confirm("¿Eliminar esta evidencia del reporte?")) return;
    try {
      await eliminarEvidenciaReporteSST(ev.id);
      const evs = await listarEvidenciasReporteSST(detalle.id);
      const tl = await timelineReporteSST(detalle.id);
      setEvidenciasDetalle(evs);
      setTimelineDetalle(tl);
      setDetalle((prev) => prev ? { ...prev, evidencias: evs, total_evidencias: evs.length } : prev);
      await cargarDatos();
    } catch (error) {
      alert(mostrarError(error, "No fue posible eliminar la evidencia"));
    }
  };

  const kpis = [
    { label: "Total", value: dashboard.total, icon: Bell, cls: "blue" },
    { label: "Sin asignar", value: dashboard.sin_asignar, icon: ShieldAlert, cls: "amber" },
    { label: "Asignados", value: dashboard.asignados, icon: UserCheck, cls: "green" },
    { label: "En proceso", value: dashboard.en_proceso, icon: Zap, cls: "purple" },
    { label: "Inspección", value: dashboard.gestionados_inspeccion, icon: ClipboardCheck, cls: "blue" },
    { label: "CAPA", value: dashboard.gestionados_capa, icon: Target, cls: "red" },
    { label: "Con evidencia", value: dashboard.con_evidencia, icon: FileImage, cls: "purple" },
    { label: "Total evidencias", value: dashboard.total_evidencias || 0, icon: FileImage, cls: "green" },
    { label: "Ahorro MB", value: dashboard.ahorro_evidencias_mb || 0, icon: Download, cls: "blue" },
    { label: "Cerrados", value: dashboard.cerrados, icon: CheckCircle2, cls: "green" },
  ];

  return (
    <section className="ra-page">
      <div className="ra-hero">
        <div>
          <span className="ra-tag"><ShieldAlert size={16} /> Evidencias Inteligentes</span>
          <h1>Evidencias Inteligentes de Reportes SST</h1>
          <p>Galería multi-evidencia, compresión automática de imágenes, timeline, clasificación SST y trazabilidad completa.</p>
        </div>
        <div className="ra-hero-actions">
          <button className="ra-btn secondary" onClick={cargarDatos} disabled={loading}>{loading ? <Loader2 className="spin" size={17} /> : <RefreshCw size={17} />} Actualizar</button>
        </div>
      </div>

      {alerta && <div className={`ra-alert ${alerta.type}`}><span>{alerta.text}</span><button onClick={() => setAlerta(null)}><X size={16} /></button></div>}

      <div className="ra-kpis ra-kpis-8">
        {kpis.map((kpi) => { const Icon = kpi.icon; return (
          <article key={kpi.label} className="ra-kpi-card"><span className={`ra-kpi-icon ${kpi.cls}`}><Icon size={20} /></span><small>{kpi.label}</small><strong>{kpi.value || 0}</strong></article>
        );})}
      </div>

      <div className="ra-grid">
        <main className="ra-main">
          <div className="ra-panel">
            <form className="ra-toolbar" onSubmit={onBuscar}>
              <label className="ra-search"><Search size={18} /><input value={filtros.buscar} onChange={(e) => setFiltros((p) => ({ ...p, buscar: e.target.value }))} placeholder="Buscar por código, título, descripción, ubicación o responsable..." /></label>
              <button className="ra-btn secondary" type="submit"><Search size={16} /> Buscar</button>
              <button className="ra-btn secondary" type="button" onClick={limpiarFiltros}><Filter size={16} /> Limpiar</button>
            </form>

            <div className="ra-filters">
              <select value={filtros.empresa_id} onChange={(e) => setFiltros((p) => ({ ...p, empresa_id: e.target.value }))}><option value="TODOS">Todas las empresas</option>{empresas.map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}</select>
              <select value={filtros.area_id} onChange={(e) => setFiltros((p) => ({ ...p, area_id: e.target.value }))}><option value="TODOS">Todas las áreas</option>{areas.map((a) => <option key={a.id} value={a.id}>{a.nombre}</option>)}</select>
              <select value={filtros.responsable} onChange={(e) => setFiltros((p) => ({ ...p, responsable: e.target.value }))}><option value="TODOS">Todos los responsables</option>{responsables.map((r) => <option key={r.id} value={r.nombre}>{r.nombre}</option>)}</select>
              <select value={filtros.tipo_reporte} onChange={(e) => setFiltros((p) => ({ ...p, tipo_reporte: e.target.value }))}><option value="TODOS">Todos los tipos</option><option value="ACTO_INSEGURO">Acto inseguro</option><option value="CONDICION_INSEGURA">Condición insegura</option><option value="INCIDENTE">Incidente</option><option value="ACCIDENTE">Accidente</option><option value="SUGERENCIA">Sugerencia</option></select>
              <select value={filtros.prioridad} onChange={(e) => setFiltros((p) => ({ ...p, prioridad: e.target.value }))}><option value="TODOS">Todas las prioridades</option><option value="CRITICA">Crítica</option><option value="ALTA">Alta</option><option value="MEDIA">Media</option><option value="BAJA">Baja</option></select>
              <select value={filtros.estado} onChange={(e) => setFiltros((p) => ({ ...p, estado: e.target.value }))}><option value="TODOS">Todos los estados</option><option value="REPORTADO">Reportado</option><option value="ASIGNADO">Asignado</option><option value="EN_PROCESO">En proceso</option><option value="CERRADO">Cerrado</option><option value="ANULADO">Anulado</option></select>
              <select value={filtros.con_evidencia} onChange={(e) => setFiltros((p) => ({ ...p, con_evidencia: e.target.value }))}><option value="TODOS">Todas las evidencias</option><option value="SI">Con evidencia</option><option value="NO">Sin evidencia</option></select>
            </div>

            <div className="ra-list">
              {loading ? <div className="ra-empty"><Loader2 className="spin" /> Cargando reportes...</div> : visible.length === 0 ? <div className="ra-empty"><Archive size={34} /> No hay reportes con los filtros actuales.</div> : visible.map((item) => (
                <article key={item.id} className={`ra-item estado-${String(item.estado).toLowerCase()}`}>
                  <div className={`ra-letter prioridad-${String(item.prioridad).toLowerCase()}`}>{String(item.prioridad || "M").slice(0, 1)}</div>
                  <div className="ra-item-body">
                    <header><div><strong>{item.titulo}</strong><p>{tipoLabel[item.tipo_reporte] || item.tipo_reporte} · {item.ubicacion || "Sin ubicación"}</p></div><span className={`ra-pill prioridad-${String(item.prioridad).toLowerCase()}`}>{item.prioridad}</span></header>
                    <p className="ra-desc">{item.descripcion}</p>
                    <div className="ra-meta"><span>{item.codigo}</span><span>{estadoLabel[item.estado] || item.estado}</span><span>{item.responsable_asignado || "Sin responsable"}</span><span>{item.area_nombre || "Sin área"}</span><span>{fechaHumana(item.fecha_reporte)}</span>{(item.archivo_url || item.total_evidencias > 0) && <span className="has-file">{item.total_evidencias || 1} Evidencia(s)</span>}{item.inspeccion_id && <span>INSP #{item.inspeccion_id}</span>}{item.capa_id && <span>CAPA #{item.capa_id}</span>}</div>
                  </div>
                  <div className="ra-actions"><button title="Ver detalle" onClick={() => abrirDetalle(item)}><Eye size={17} /></button><button title="Marcar en proceso" onClick={() => enProceso(item)} disabled={accionLoading}><Zap size={17} /></button><button title="Anular" className="danger" onClick={() => anular(item)} disabled={accionLoading}><XCircle size={17} /></button></div>
                </article>
              ))}
            </div>

            <footer className="ra-pagination"><span>Mostrando {visible.length} de {reportes.length} reportes.</span><div><select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}><option value={10}>10</option><option value={20}>20</option><option value={50}>50</option></select><button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>‹</button><span>Página {page} / {totalPages}</span><button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>›</button></div></footer>
          </div>
        </main>

        <aside className="ra-side">
          <article><h3>Por responsable</h3>{Object.entries(dashboard.por_responsable || {}).length === 0 ? <p>Sin datos.</p> : Object.entries(dashboard.por_responsable).map(([k, v]) => <div className="ra-bar" key={k}><span>{k === "SIN_DATO" ? "Sin responsable" : k}</span><b>{v}</b><i><em style={{ width: `${Math.min(100, (v / Math.max(1, dashboard.total)) * 100)}%` }} /></i></div>)}</article>
          <article><h3>Distribución por estado</h3>{Object.entries(dashboard.por_estado || {}).length === 0 ? <p>Sin datos.</p> : Object.entries(dashboard.por_estado).map(([k, v]) => <div className="ra-bar" key={k}><span>{estadoLabel[k] || k}</span><b>{v}</b><i><em style={{ width: `${Math.min(100, (v / Math.max(1, dashboard.total)) * 100)}%` }} /></i></div>)}</article>
          <article><h3>Recomendaciones PRO</h3><ul>{(dashboard.recomendaciones || []).map((r, idx) => <li key={idx}>{r}</li>)}</ul></article>
        </aside>
      </div>

      {detalle && <div className="ra-modal-backdrop"><div className="ra-modal"><header><div><span>Workflow reporte anónimo SST</span><h2>{detalle.titulo}</h2><p>{detalle.codigo} · {estadoLabel[detalle.estado] || detalle.estado}</p></div><button onClick={() => setDetalle(null)}><X size={22} /></button></header>
        <div className="ra-detail-grid"><article><span>Tipo</span><strong>{tipoLabel[detalle.tipo_reporte] || detalle.tipo_reporte}</strong></article><article><span>Prioridad</span><strong>{detalle.prioridad}</strong></article><article><span>Estado</span><strong>{estadoLabel[detalle.estado] || detalle.estado}</strong></article><article><span>Responsable</span><strong>{detalle.responsable_asignado || "Sin responsable"}</strong></article><article><span>Área</span><strong>{detalle.area_nombre || "Sin área"}</strong></article><article><span>Ubicación</span><strong>{detalle.ubicacion || "Sin ubicación"}</strong></article><article className="wide"><span>Descripción</span><strong>{detalle.descripcion}</strong></article><article className="wide"><span>Acción inmediata</span><strong>{detalle.accion_inmediata || "Sin acción inmediata registrada"}</strong></article><article className="wide"><span>Observaciones</span><strong>{detalle.observaciones || "Sin observaciones"}</strong></article><article className="wide"><span>Trazabilidad</span><pre>{detalle.trazabilidad || "Sin trazabilidad adicional"}</pre></article></div>
        <section className="ra-evidence"><h3><FileImage size={18} /> Evidencias inteligentes</h3><ReporteUploader loading={subiendoEvidencias} onUpload={subirEvidenciasDetalle} /><ReporteGaleriaEvidencias evidencias={evidenciasDetalle} onDelete={eliminarEvidenciaDetalle} /></section>
        <section className="ra-evidence"><h3><GitBranch size={18} /> Timeline del reporte</h3><ReporteTimeline items={timelineDetalle} /></section>
        <section className="ra-workflow"><div><h3><Users size={18} /> Asignar responsable SST</h3><select value={asignacion.responsable_empleado_id} onChange={(e) => { const emp = responsables.find((r) => String(r.id) === e.target.value); setAsignacion((p) => ({ ...p, responsable_empleado_id: e.target.value, responsable_asignado: emp?.nombre || "" })); }}><option value="">Seleccionar responsable SST</option>{responsables.map((r) => <option key={r.id} value={r.id}>{r.nombre} — {r.area_nombre || "Sin área"} / {r.cargo_nombre || "Sin cargo"}</option>)}</select><input value={asignacion.responsable_asignado} onChange={(e) => setAsignacion((p) => ({ ...p, responsable_asignado: e.target.value, responsable_empleado_id: "" }))} placeholder="O escribir responsable manualmente" /><textarea value={asignacion.observaciones} onChange={(e) => setAsignacion((p) => ({ ...p, observaciones: e.target.value }))} placeholder="Observaciones de asignación" /><button className="ra-btn primary" onClick={asignar} disabled={accionLoading}><UserCheck size={16} /> Asignar</button></div>
          <div><h3><GitBranch size={18} /> Gestión SST</h3><input type="number" min="1" max="365" value={workflow.fecha_compromiso_dias} onChange={(e) => setWorkflow((p) => ({ ...p, fecha_compromiso_dias: Number(e.target.value || 15) }))} placeholder="Días compromiso" /><textarea value={workflow.observaciones} onChange={(e) => setWorkflow((p) => ({ ...p, observaciones: e.target.value }))} placeholder="Observaciones para la gestión" /><button className="ra-btn secondary" onClick={() => enProceso(detalle)} disabled={accionLoading}><Zap size={16} /> En proceso</button><button className="ra-btn secondary" onClick={() => crearInspeccion(detalle)} disabled={accionLoading}><ClipboardCheck size={16} /> Crear inspección</button><button className="ra-btn secondary" onClick={() => crearHallazgo(detalle)} disabled={accionLoading}><Wrench size={16} /> Crear hallazgo</button><button className="ra-btn secondary" onClick={() => crearCAPA(detalle)} disabled={accionLoading}><AlertTriangle size={16} /> Crear CAPA</button></div>
          <div><h3>Cierre / gestión</h3><textarea value={cierre.accion_cierre} onChange={(e) => setCierre((p) => ({ ...p, accion_cierre: e.target.value }))} placeholder="Acción de cierre realizada" /><textarea value={cierre.observaciones} onChange={(e) => setCierre((p) => ({ ...p, observaciones: e.target.value }))} placeholder="Observaciones de cierre" /><button className="ra-btn success" onClick={cerrar} disabled={accionLoading}><CheckCircle2 size={16} /> Cerrar reporte</button></div></section>
        <footer><button className="ra-btn secondary" onClick={() => setDetalle(null)}>Cerrar</button></footer></div></div>}
    </section>
  );
}
