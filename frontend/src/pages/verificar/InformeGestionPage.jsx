// ============================================================
// INFORME DE GESTIÓN SG-SST — Enterprise UI
// Archivo: frontend/src/pages/verificar/InformeGestionPage.jsx
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  Calendar,
  CheckCircle2,
  ClipboardList,
  Clock,
  Download,
  Eye,
  FileText,
  FileUp,
  History,
  ListChecks,
  Loader2,
  PenLine,
  Plus,
  RefreshCcw,
  Send,
  Shield,
  TrendingUp,
  Users,
  X,
  ArrowLeft,
  Pencil,
} from "lucide-react";

import AdminLayout from "../../layouts/AdminLayout";
import informeGestionApi from "../../api/informeGestionApi";
import "../../styles/informe-gestion.css";

const ESTADOS_INFORME = [
  "BORRADOR", "EN_REVISION", "PRESENTADO", "APROBADO",
  "APROBADO_CON_OBSERVACIONES", "DEVUELTO", "CERRADO",
];

const estadoLabel = {
  BORRADOR: "Borrador", EN_REVISION: "En Revisión", PRESENTADO: "Presentado",
  APROBADO: "Aprobado", APROBADO_CON_OBSERVACIONES: "Aprob. con Observ.",
  DEVUELTO: "Devuelto", CERRADO: "Cerrado",
};

const estadoClass = {
  BORRADOR: "ig-status-borrador", EN_REVISION: "ig-status-enrevision",
  PRESENTADO: "ig-status-presentado", APROBADO: "ig-status-aprobado",
  APROBADO_CON_OBSERVACIONES: "ig-status-aprobadoobs",
  DEVUELTO: "ig-status-devuelto", CERRADO: "ig-status-cerrado",
};

const SEMAFORO = { VERDE: "#10b981", AMARILLO: "#f59e0b", ROJO: "#ef4444" };

function semaforoColor(valor) {
  if (valor >= 90) return SEMAFORO.VERDE;
  if (valor >= 60) return SEMAFORO.AMARILLO;
  return SEMAFORO.ROJO;
}

function initials(name) {
  return (name || "?").split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
}

export default function InformeGestionPage() {
  const [informes, setInformes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [consolidando, setConsolidando] = useState(false);

  const [filtroAnio, setFiltroAnio] = useState(new Date().getFullYear());
  const [filtroEstado, setFiltroEstado] = useState("");

  const [informeActivo, setInformeActivo] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [secciones, setSecciones] = useState([]);
  const [versiones, setVersiones] = useState([]);
  const [recomendaciones, setRecomendaciones] = useState([]);
  const [rendiciones, setRendiciones] = useState([]);

  const [vistaActiva, setVistaActiva] = useState("lista");
  const [tabActiva, setTabActiva] = useState("resumen");

  const [modalCrear, setModalCrear] = useState(false);
  const [modalRecomendacion, setModalRecomendacion] = useState(false);
  const [modalRendicion, setModalRendicion] = useState(false);

  const [formInforme, setFormInforme] = useState({
    anio: new Date().getFullYear(),
    titulo: "INFORME ANUAL DE GESTIÓN SG-SST",
    responsable_sst_nombre: "",
    representante_legal_nombre: "",
  });

  const [formRecomendacion, setFormRecomendacion] = useState({
    hallazgo: "", riesgo: "", recomendacion: "", prioridad: "MEDIA",
    accion_propuesta: "", responsable_sugerido: "",
  });

  const [formRendicion, setFormRendicion] = useState({
    persona_nombre: "", cargo: "", rol_sgsst: "",
    responsabilidad_asignada: "", actividades: "", meta: "", resultado: "",
  });

  const cargarInformes = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filtroAnio) params.anio = filtroAnio;
      if (filtroEstado) params.estado = filtroEstado;
      const data = await informeGestionApi.listar(params);
      setInformes(data);
    } catch (e) {
      console.error("Error cargando informes:", e);
    } finally {
      setLoading(false);
    }
  };

  const cargarDetalle = async (id) => {
    try {
      const [inf, dash, secs, vers, recs, rends] = await Promise.all([
        informeGestionApi.obtener(id),
        informeGestionApi.dashboard(id),
        informeGestionApi.listarSecciones(id),
        informeGestionApi.listarVersiones(id),
        informeGestionApi.listarRecomendaciones(id),
        informeGestionApi.listarRendiciones(id),
      ]);
      setInformeActivo(inf);
      setDashboard(dash);
      setSecciones(secs);
      setVersiones(vers);
      setRecomendaciones(recs);
      setRendiciones(rends);
      setTabActiva("resumen");
      setVistaActiva("detalle");
    } catch (e) {
      console.error("Error cargando detalle:", e);
    }
  };

  useEffect(() => { cargarInformes(); }, [filtroAnio, filtroEstado]);

  const crearInforme = async () => {
    setGuardando(true);
    try {
      const nuevo = await informeGestionApi.crear(formInforme);
      setModalCrear(false);
      await cargarDetalle(nuevo.id);
    } catch (e) { console.error("Error creando:", e); }
    finally { setGuardando(false); }
  };

  const consolidarDatos = async () => {
    if (!informeActivo) return;
    setConsolidando(true);
    try {
      await informeGestionApi.consolidar(informeActivo.id);
      await cargarDetalle(informeActivo.id);
    } catch (e) { console.error("Error consolidando:", e); }
    finally { setConsolidando(false); }
  };

  const presentarInforme = async () => {
    if (!informeActivo) return;
    try { await informeGestionApi.presentar(informeActivo.id); await cargarDetalle(informeActivo.id); }
    catch (e) { console.error("Error presentando:", e); }
  };

  const aprobarInforme = async (resultado) => {
    if (!informeActivo) return;
    try { await informeGestionApi.aprobar(informeActivo.id, resultado); await cargarDetalle(informeActivo.id); }
    catch (e) { console.error("Error aprobando:", e); }
  };

  const cerrarInforme = async () => {
    if (!informeActivo) return;
    try { await informeGestionApi.cerrar(informeActivo.id); await cargarDetalle(informeActivo.id); }
    catch (e) { console.error("Error cerrando:", e); }
  };

  const crearRecomendacion = async () => {
    if (!informeActivo) return;
    try {
      await informeGestionApi.crearRecomendacion(informeActivo.id, formRecomendacion);
      setModalRecomendacion(false);
      setFormRecomendacion({ hallazgo: "", riesgo: "", recomendacion: "", prioridad: "MEDIA", accion_propuesta: "", responsable_sugerido: "" });
      const recs = await informeGestionApi.listarRecomendaciones(informeActivo.id);
      setRecomendaciones(recs);
    } catch (e) { console.error("Error:", e); }
  };

  const crearRendicion = async () => {
    if (!informeActivo) return;
    try {
      await informeGestionApi.crearRendicion(informeActivo.id, formRendicion);
      setModalRendicion(false);
      setFormRendicion({ persona_nombre: "", cargo: "", rol_sgsst: "", responsabilidad_asignada: "", actividades: "", meta: "", resultado: "" });
      const rends = await informeGestionApi.listarRendiciones(informeActivo.id);
      setRendiciones(rends);
    } catch (e) { console.error("Error:", e); }
  };

  const anios = useMemo(() => {
    const actual = new Date().getFullYear();
    return Array.from({ length: 5 }, (_, i) => actual - i);
  }, []);

  const puedeAccionar = (inf) => ["BORRADOR", "DEVUELTO"].includes(inf?.estado);
  const puedeAprobar = (inf) => inf?.estado === "PRESENTADO";
  const puedeCerrar = (inf) => ["APROBADO", "APROBADO_CON_OBSERVACIONES"].includes(inf?.estado);

  const datos = dashboard?.informe || {};
  const indicadores = dashboard?.indicadores_calculados || {};

  // ============================================================
  // VISTA: LISTA
  // ============================================================
  if (vistaActiva === "lista") {
    return (
      <AdminLayout>
        <div className="ig-page">
          {/* Header */}
          <div className="ig-page-header">
            <div className="ig-page-header-left">
              <div className="ig-page-icon"><FileText size={26} /></div>
              <div className="ig-page-title">
                <h1>Informe de Gestión SG-SST</h1>
                <p className="ig-page-subtitle">Consolidación anual del Sistema de Gestión de Seguridad y Salud en el Trabajo</p>
              </div>
            </div>
            <div className="ig-page-header-right">
              <button onClick={() => setModalCrear(true)} className="ig-btn ig-btn-primary">
                <Plus size={16} /> Nuevo Informe
              </button>
            </div>
          </div>

          {/* Toolbar */}
          <div className="ig-toolbar">
            <div className="ig-filters">
              <select value={filtroAnio} onChange={(e) => setFiltroAnio(Number(e.target.value))} className="ig-select">
                {anios.map((a) => <option key={a} value={a}>{a}</option>)}
              </select>
              <select value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)} className="ig-select">
                <option value="">Todos los estados</option>
                {ESTADOS_INFORME.map((e) => <option key={e} value={e}>{estadoLabel[e]}</option>)}
              </select>
              <button onClick={cargarInformes} className="ig-btn ig-btn-outline ig-btn-sm" disabled={loading}>
                <RefreshCcw size={14} className={loading ? "ig-spin" : ""} /> Actualizar
              </button>
            </div>
          </div>

          {/* Table */}
          {loading ? (
            <div className="ig-loading"><Loader2 size={32} className="ig-spin" /><p>Cargando informes...</p></div>
          ) : informes.length === 0 ? (
            <div className="ig-empty">
              <FileText size={52} />
              <h3>No hay informes para este periodo</h3>
              <p>Crea un nuevo informe para comenzar la consolidación anual del SG-SST.</p>
              <button onClick={() => setModalCrear(true)} className="ig-btn ig-btn-primary"><Plus size={16} /> Crear Primer Informe</button>
            </div>
          ) : (
            <div className="ig-table-panel">
              <div className="ig-table-scroll">
                <table className="ig-table">
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Informe</th>
                      <th>Año</th>
                      <th>Estado</th>
                      <th>Versión</th>
                      <th>Cumplimiento</th>
                      <th>Responsable</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {informes.map((inf) => (
                      <tr key={inf.id}>
                        <td><span className="ig-code-pill">{inf.codigo}</span></td>
                        <td>
                          <div className="ig-name-cell">
                            <strong>{inf.titulo}</strong>
                            <span>{inf.responsable_sst_nombre || "Sin responsable asignado"}</span>
                          </div>
                        </td>
                        <td><strong>{inf.anio}</strong></td>
                        <td><span className={`ig-status-pill ${estadoClass[inf.estado] || ""}`}>{estadoLabel[inf.estado]}</span></td>
                        <td><strong>v{inf.version}</strong></td>
                        <td>
                          <div className="ig-progress">
                            <div className="ig-progress-bar">
                              <div className="ig-progress-fill" style={{ width: `${inf.cumplimiento_global || 0}%`, backgroundColor: semaforoColor(inf.cumplimiento_global || 0) }} />
                            </div>
                            <span className="ig-progress-label">{inf.cumplimiento_global || 0}%</span>
                          </div>
                        </td>
                        <td>{inf.responsable_sst_nombre || "—"}</td>
                        <td>
                          <div className="ig-actions">
                            <button className="ig-icon-btn view" onClick={() => cargarDetalle(inf.id)} title="Ver detalle"><Eye size={16} /></button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Modal Crear */}
          {modalCrear && (
            <div className="ig-modal-overlay" onClick={() => setModalCrear(false)}>
              <div className="ig-modal" onClick={(e) => e.stopPropagation()}>
                <div className="ig-modal-header">
                  <h2>Nuevo Informe de Gestión</h2>
                  <button onClick={() => setModalCrear(false)}><X size={20} /></button>
                </div>
                <div className="ig-modal-body">
                  <label>Año del informe</label>
                  <select value={formInforme.anio} onChange={(e) => setFormInforme({ ...formInforme, anio: Number(e.target.value) })}>
                    {anios.map((a) => <option key={a} value={a}>{a}</option>)}
                  </select>
                  <label>Título</label>
                  <input type="text" value={formInforme.titulo} onChange={(e) => setFormInforme({ ...formInforme, titulo: e.target.value })} />
                  <label>Responsable SST</label>
                  <input type="text" value={formInforme.responsable_sst_nombre} onChange={(e) => setFormInforme({ ...formInforme, responsable_sst_nombre: e.target.value })} placeholder="Nombre del responsable" />
                  <label>Representante Legal</label>
                  <input type="text" value={formInforme.representante_legal_nombre} onChange={(e) => setFormInforme({ ...formInforme, representante_legal_nombre: e.target.value })} placeholder="Nombre del representante legal" />
                </div>
                <div className="ig-modal-footer">
                  <button onClick={() => setModalCrear(false)} className="ig-btn ig-btn-outline">Cancelar</button>
                  <button onClick={crearInforme} className="ig-btn ig-btn-primary" disabled={guardando}>
                    {guardando ? <Loader2 size={16} className="ig-spin" /> : <Plus size={16} />} Crear Informe
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </AdminLayout>
    );
  }

  // ============================================================
  // VISTA: DETALLE
  // ============================================================
  return (
    <AdminLayout>
      <div className="ig-page">
        {/* Header */}
        <div className="ig-page-header">
          <div className="ig-page-header-left">
            <button onClick={() => setVistaActiva("lista")} className="ig-btn-back"><ArrowLeft size={16} /> Volver</button>
            <div className="ig-page-icon"><FileText size={26} /></div>
            <div className="ig-page-title">
              <h1>{datos.titulo || "Informe de Gestión"}</h1>
              <p className="ig-page-subtitle">{datos.codigo} · v{datos.version} · {estadoLabel[datos.estado]}</p>
            </div>
          </div>
          <div className="ig-page-header-right">
            {puedeAccionar(informeActivo) && (
              <button onClick={consolidarDatos} className="ig-btn ig-btn-primary" disabled={consolidando}>
                {consolidando ? <Loader2 size={16} className="ig-spin" /> : <ClipboardList size={16} />} Consolidar
              </button>
            )}
            {puedeAccionar(informeActivo) && (
              <button onClick={presentarInforme} className="ig-btn ig-btn-success"><Send size={16} /> Presentar</button>
            )}
            {puedeAprobar(informeActivo) && (
              <>
                <button onClick={() => aprobarInforme("APROBADO")} className="ig-btn ig-btn-success"><CheckCircle2 size={16} /> Aprobar</button>
                <button onClick={() => aprobarInforme("DEVUELTO")} className="ig-btn ig-btn-danger"><X size={16} /> Devolver</button>
              </>
            )}
            {puedeCerrar(informeActivo) && (
              <button onClick={cerrarInforme} className="ig-btn ig-btn-outline"><Shield size={16} /> Cerrar</button>
            )}
          </div>
        </div>

        {/* KPIs */}
        <div className="ig-kpi-grid">
          <div className="ig-kpi-card">
            <div className="ig-kpi-icon" style={{ backgroundColor: "#10b98120", color: "#10b981" }}><TrendingUp size={24} /></div>
            <div className="ig-kpi-info"><span className="ig-kpi-value">{datos.cumplimiento_global || 0}%</span><span className="ig-kpi-label">Cumplimiento Global</span></div>
          </div>
          <div className="ig-kpi-card">
            <div className="ig-kpi-icon" style={{ backgroundColor: "#3b82f620", color: "#3b82f6" }}><Calendar size={24} /></div>
            <div className="ig-kpi-info"><span className="ig-kpi-value">{indicadores.cumplimiento_plan_anual || 0}%</span><span className="ig-kpi-label">Plan Anual</span></div>
          </div>
          <div className="ig-kpi-card">
            <div className="ig-kpi-icon" style={{ backgroundColor: "#f59e0b20", color: "#f59e0b" }}><Shield size={24} /></div>
            <div className="ig-kpi-info"><span className="ig-kpi-value">{indicadores.cumplimiento_legal || 0}%</span><span className="ig-kpi-label">Cumplimiento Legal</span></div>
          </div>
          <div className="ig-kpi-card">
            <div className="ig-kpi-icon" style={{ backgroundColor: "#6366f120", color: "#6366f1" }}><FileText size={24} /></div>
            <div className="ig-kpi-info"><span className="ig-kpi-value">{secciones.length}</span><span className="ig-kpi-label">Secciones</span></div>
          </div>
        </div>

        {/* Tabs */}
        <div className="ig-tabs">
          <button className={`ig-tab ${tabActiva === "resumen" ? "active" : ""}`} onClick={() => setTabActiva("resumen")}><Eye size={15} /> Resumen</button>
          <button className={`ig-tab ${tabActiva === "secciones" ? "active" : ""}`} onClick={() => setTabActiva("secciones")}><ListChecks size={15} /> Secciones</button>
          <button className={`ig-tab ${tabActiva === "recomendaciones" ? "active" : ""}`} onClick={() => setTabActiva("recomendaciones")}><PenLine size={15} /> Recomendaciones</button>
          <button className={`ig-tab ${tabActiva === "rendiciones" ? "active" : ""}`} onClick={() => setTabActiva("rendiciones")}><Users size={15} /> Rendición Cuentas</button>
          <button className={`ig-tab ${tabActiva === "versiones" ? "active" : ""}`} onClick={() => setTabActiva("versiones")}><History size={15} /> Historial</button>
        </div>

        {/* Content */}
        <div className="ig-content">
          {/* Resumen */}
          {tabActiva === "resumen" && (
            <div className="ig-detail-grid">
              <div className="ig-detail-card">
                <h3>Resumen Ejecutivo</h3>
                <p>{informeActivo?.resumen_ejecutivo || "Sin datos consolidados aún. Haz clic en 'Consolidar' para generar el resumen."}</p>
              </div>
              <div className="ig-detail-card">
                <h3>Indicadores Clave</h3>
                <div className="ig-semaforo-grid">
                  <div className="ig-semaforo-item">
                    <div className="ig-semaforo-dot" style={{ backgroundColor: semaforoColor(indicadores.cumplimiento_plan_anual || 0) }} />
                    <span className="ig-semaforo-label">Plan Anual</span>
                  </div>
                  <div className="ig-semaforo-item">
                    <div className="ig-semaforo-dot" style={{ backgroundColor: semaforoColor(indicadores.cumplimiento_objetivos || 0) }} />
                    <span className="ig-semaforo-label">Objetivos</span>
                  </div>
                  <div className="ig-semaforo-item">
                    <div className="ig-semaforo-dot" style={{ backgroundColor: semaforoColor(indicadores.cumplimiento_legal || 0) }} />
                    <span className="ig-semaforo-label">Legal</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Secciones */}
          {tabActiva === "secciones" && (
            <div className="ig-secciones-grid">
              {secciones.map((sec) => (
                <div key={sec.id} className="ig-seccion-card">
                  <div className="ig-seccion-header">
                    <span className="ig-seccion-code">{sec.codigo_seccion}</span>
                    <span className={`ig-status-pill ${sec.estado_seccion === "CONSOLIDADA" ? "ig-status-aprobado" : "ig-status-presentado"}`}>{sec.estado_seccion}</span>
                  </div>
                  <h4>{sec.nombre_seccion}</h4>
                  {sec.observaciones && <p>{sec.observaciones}</p>}
                </div>
              ))}
            </div>
          )}

          {/* Recomendaciones */}
          {tabActiva === "recomendaciones" && (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <h3 style={{ margin: 0, fontSize: 15, fontWeight: 800, color: "var(--ig-slate-800)" }}>Recomendaciones del Responsable SG-SST</h3>
                <button onClick={() => setModalRecomendacion(true)} className="ig-btn ig-btn-primary ig-btn-sm"><Plus size={14} /> Nueva</button>
              </div>
              {recomendaciones.length === 0 ? (
                <div className="ig-empty"><PenLine size={40} /><h3>Sin recomendaciones</h3><p>Registra recomendaciones para mejorar el SG-SST.</p></div>
              ) : (
                <div className="ig-table-panel"><div className="ig-table-scroll">
                  <table className="ig-table">
                    <thead><tr><th>Hallazgo</th><th>Prioridad</th><th>Recomendación</th><th>Estado</th></tr></thead>
                    <tbody>
                      {recomendaciones.map((rec) => (
                        <tr key={rec.id}>
                          <td><div className="ig-name-cell"><strong>{rec.hallazgo}</strong></div></td>
                          <td><span className={`ig-priority-pill ig-priority-${rec.prioridad?.toLowerCase() || "media"}`}>{rec.prioridad}</span></td>
                          <td>{rec.recomendacion}</td>
                          <td><span className={`ig-status-pill ${rec.estado === "CUMPLIDA" ? "ig-status-aprobado" : "ig-status-presentado"}`}>{rec.estado}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div></div>
              )}
            </div>
          )}

          {/* Rendiciones */}
          {tabActiva === "rendiciones" && (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <h3 style={{ margin: 0, fontSize: 15, fontWeight: 800, color: "var(--ig-slate-800)" }}>Rendición de Cuentas</h3>
                <button onClick={() => setModalRendicion(true)} className="ig-btn ig-btn-primary ig-btn-sm"><Plus size={14} /> Nueva</button>
              </div>
              {rendiciones.length === 0 ? (
                <div className="ig-empty"><Users size={40} /><h3>Sin rendiciones</h3><p>Registra la rendición de cuentas del SG-SST.</p></div>
              ) : (
                <div className="ig-table-panel"><div className="ig-table-scroll">
                  <table className="ig-table">
                    <thead><tr><th>Persona</th><th>Cargo</th><th>Rol SG-SST</th><th>Responsabilidad</th><th>% Cumplimiento</th><th>Estado</th></tr></thead>
                    <tbody>
                      {rendiciones.map((ren) => (
                        <tr key={ren.id}>
                          <td><div className="ig-name-cell"><strong>{ren.persona_nombre}</strong><span>{ren.cargo}</span></div></td>
                          <td>{ren.rol_sgsst || "—"}</td>
                          <td>{ren.responsabilidad_asignada}</td>
                          <td>
                            <div className="ig-progress">
                              <div className="ig-progress-bar"><div className="ig-progress-fill" style={{ width: `${ren.porcentaje_cumplimiento || 0}%`, backgroundColor: semaforoColor(ren.porcentaje_cumplimiento || 0) }} /></div>
                              <span className="ig-progress-label">{ren.porcentaje_cumplimiento || 0}%</span>
                            </div>
                          </td>
                          <td><span className={`ig-status-pill ${ren.estado === "APROBADO" ? "ig-status-aprobado" : "ig-status-presentado"}`}>{ren.estado}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div></div>
              )}
            </div>
          )}

          {/* Versiones */}
          {tabActiva === "versiones" && (
            <div>
              <h3 style={{ margin: "0 0 16px", fontSize: 15, fontWeight: 800, color: "var(--ig-slate-800)" }}>Historial de Versiones</h3>
              {versiones.length === 0 ? (
                <div className="ig-empty"><History size={40} /><h3>Sin versiones</h3><p>El historial se genera automáticamente al consolidar.</p></div>
              ) : (
                <div className="ig-timeline">
                  {versiones.map((ver) => (
                    <div key={ver.id} className="ig-timeline-item">
                      <div className="ig-timeline-dot" />
                      <div className="ig-timeline-content">
                        <span className="ig-timeline-version">v{ver.version_numero}</span>
                        <span className="ig-timeline-estado">{ver.estado_nuevo}</span>
                        {ver.motivo_cambio && <span className="ig-timeline-motivo">{ver.motivo_cambio}</span>}
                        <span className="ig-timeline-fecha">{ver.fecha_creacion}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modal Recomendación */}
        {modalRecomendacion && (
          <div className="ig-modal-overlay" onClick={() => setModalRecomendacion(false)}>
            <div className="ig-modal" onClick={(e) => e.stopPropagation()}>
              <div className="ig-modal-header"><h2>Nueva Recomendación</h2><button onClick={() => setModalRecomendacion(false)}><X size={20} /></button></div>
              <div className="ig-modal-body">
                <label>Hallazgo</label>
                <textarea value={formRecomendacion.hallazgo} onChange={(e) => setFormRecomendacion({ ...formRecomendacion, hallazgo: e.target.value })} rows={3} />
                <label>Riesgo</label>
                <textarea value={formRecomendacion.riesgo} onChange={(e) => setFormRecomendacion({ ...formRecomendacion, riesgo: e.target.value })} rows={2} />
                <label>Recomendación</label>
                <textarea value={formRecomendacion.recomendacion} onChange={(e) => setFormRecomendacion({ ...formRecomendacion, recomendacion: e.target.value })} rows={3} />
                <label>Prioridad</label>
                <select value={formRecomendacion.prioridad} onChange={(e) => setFormRecomendacion({ ...formRecomendacion, prioridad: e.target.value })}>
                  <option value="BAJA">Baja</option><option value="MEDIA">Media</option><option value="ALTA">Alta</option><option value="CRITICA">Crítica</option>
                </select>
                <label>Responsable Sugerido</label>
                <input type="text" value={formRecomendacion.responsable_sugerido} onChange={(e) => setFormRecomendacion({ ...formRecomendacion, responsable_sugerido: e.target.value })} />
              </div>
              <div className="ig-modal-footer">
                <button onClick={() => setModalRecomendacion(false)} className="ig-btn ig-btn-outline">Cancelar</button>
                <button onClick={crearRecomendacion} className="ig-btn ig-btn-primary"><Plus size={16} /> Crear</button>
              </div>
            </div>
          </div>
        )}

        {/* Modal Rendición */}
        {modalRendicion && (
          <div className="ig-modal-overlay" onClick={() => setModalRendicion(false)}>
            <div className="ig-modal" onClick={(e) => e.stopPropagation()}>
              <div className="ig-modal-header"><h2>Nueva Rendición de Cuentas</h2><button onClick={() => setModalRendicion(false)}><X size={20} /></button></div>
              <div className="ig-modal-body">
                <label>Persona</label>
                <input type="text" value={formRendicion.persona_nombre} onChange={(e) => setFormRendicion({ ...formRendicion, persona_nombre: e.target.value })} />
                <label>Cargo</label>
                <input type="text" value={formRendicion.cargo} onChange={(e) => setFormRendicion({ ...formRendicion, cargo: e.target.value })} />
                <label>Rol SG-SST</label>
                <input type="text" value={formRendicion.rol_sgsst} onChange={(e) => setFormRendicion({ ...formRendicion, rol_sgsst: e.target.value })} />
                <label>Responsabilidad Asignada</label>
                <textarea value={formRendicion.responsabilidad_asignada} onChange={(e) => setFormRendicion({ ...formRendicion, responsabilidad_asignada: e.target.value })} rows={3} />
                <label>Actividades</label>
                <textarea value={formRendicion.actividades} onChange={(e) => setFormRendicion({ ...formRendicion, actividades: e.target.value })} rows={3} />
              </div>
              <div className="ig-modal-footer">
                <button onClick={() => setModalRendicion(false)} className="ig-btn ig-btn-outline">Cancelar</button>
                <button onClick={crearRendicion} className="ig-btn ig-btn-primary"><Plus size={16} /> Crear</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
