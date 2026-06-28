// ============================================================
// PORTAL DEL EMPLEADO SST ENTERPRISE - ERP SST PRO
// FASE 1.1.25.2 — FRONTEND PORTAL DEL EMPLEADO SST
// Archivo: frontend/src/pages/portal/PortalEmpleadoPage.jsx
// ============================================================

import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  Archive,
  Award,
  BadgeCheck,
  Bell,
  Camera,
  CheckCircle2,
  ClipboardList,
  Download,
  Eye,
  FileText,
  Filter,
  GraduationCap,
  HardHat,
  HeartPulse,
  Loader2,
  MapPin,
  Megaphone,
  RefreshCcw,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  UserRound,
  X,
} from "lucide-react";

import {
  cambiarEstadoReporteEmpleadoSST,
  crearReporteEmpleadoFormSST,
  dashboardPortalEmpleadoSST,
  esImagenReporteSST,
  esPdfReporteSST,
  esVideoReporteSST,
  listarMisCapacitacionesSST,
  listarMisEPPSST,
  listarMisExamenesSST,
  listarReportesEmpleadoSST,
  urlArchivoPortalEmpleadoSST,
} from "../../api/portalEmpleadoApi";

import "../../styles/portal-empleado-sst.css";

const initialForm = {
  tipo_reporte: "CONDICION_INSEGURA",
  prioridad: "MEDIA",
  titulo: "",
  descripcion: "",
  ubicacion: "",
  accion_inmediata: "",
  observaciones: "",
};

const filtrosIniciales = {
  buscar: "",
  tipo_reporte: "TODOS",
  prioridad: "TODOS",
  estado: "TODOS",
};

const tiposReporte = [
  { value: "ACTO_INSEGURO", label: "Acto inseguro", icon: AlertTriangle },
  { value: "CONDICION_INSEGURA", label: "Condición insegura", icon: ShieldCheck },
  { value: "INCIDENTE", label: "Incidente", icon: Bell },
  { value: "ACCIDENTE", label: "Accidente", icon: HeartPulse },
  { value: "SUGERENCIA", label: "Sugerencia SST", icon: Sparkles },
];

const prioridades = ["BAJA", "MEDIA", "ALTA", "CRITICA"];
const estados = ["REPORTADO", "ASIGNADO", "EN_PROCESO", "CERRADO", "ANULADO"];

const normalizarTexto = (value) => String(value || "").replaceAll("_", " ");

const colorPrioridad = (value) => {
  const v = String(value || "").toUpperCase();
  if (v === "CRITICA") return "red";
  if (v === "ALTA") return "orange";
  if (v === "MEDIA") return "yellow";
  return "green";
};

const colorEstado = (value) => {
  const v = String(value || "").toUpperCase();
  if (v === "CERRADO") return "green";
  if (v === "EN_PROCESO") return "blue";
  if (v === "ASIGNADO") return "purple";
  if (v === "ANULADO") return "gray";
  return "yellow";
};

const fmtFecha = (value) => {
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

const construirMensajeError = (error) => {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((e) => `${e.loc?.join(" → ") || "campo"}: ${e.msg}`).join("\n");
  }
  if (typeof detail === "string") return detail;
  return error?.message || "Error desconocido";
};

function EmptyState({ icon: Icon = Archive, title, text }) {
  return (
    <div className="portal-empty">
      <Icon size={38} />
      <strong>{title}</strong>
      <span>{text}</span>
    </div>
  );
}

function KpiCard({ icon: Icon, label, value, tone }) {
  return (
    <article className="portal-kpi-card">
      <span className={`portal-kpi-icon ${tone || "blue"}`}>
        <Icon size={20} />
      </span>
      <div>
        <small>{label}</small>
        <strong>{value ?? 0}</strong>
      </div>
    </article>
  );
}

function EvidencePreview({ reporte, onClose }) {
  if (!reporte) return null;
  const url = urlArchivoPortalEmpleadoSST(reporte.archivo_url);

  return (
    <div className="portal-modal-backdrop" onClick={onClose}>
      <section className="portal-preview-modal" onClick={(e) => e.stopPropagation()}>
        <header>
          <div>
            <span>Vista previa evidencia SST</span>
            <h2>{reporte.archivo_nombre || reporte.codigo}</h2>
            <p>{reporte.titulo}</p>
          </div>
          <button type="button" onClick={onClose} aria-label="Cerrar">
            <X size={20} />
          </button>
        </header>

        <div className="portal-preview-body">
          {esImagenReporteSST(reporte) ? (
            <img src={url} alt={reporte.archivo_nombre || reporte.titulo} />
          ) : esPdfReporteSST(reporte) ? (
            <iframe src={url} title="Evidencia PDF" />
          ) : esVideoReporteSST(reporte) ? (
            <video src={url} controls />
          ) : (
            <EmptyState icon={FileText} title="Vista previa no disponible" text="Descarga el archivo para revisarlo." />
          )}
        </div>

        <footer>
          <a className="portal-btn secondary" href={url} target="_blank" rel="noreferrer">
            <Download size={16} /> Abrir / descargar
          </a>
          <button className="portal-btn primary" type="button" onClick={onClose}>Cerrar</button>
        </footer>
      </section>
    </div>
  );
}

export default function PortalEmpleadoPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [tab, setTab] = useState("dashboard");
  const [dashboard, setDashboard] = useState(null);
  const [capacitaciones, setCapacitaciones] = useState([]);
  const [epp, setEpp] = useState([]);
  const [examenes, setExamenes] = useState([]);
  const [reportes, setReportes] = useState([]);
  const [filtros, setFiltros] = useState(filtrosIniciales);
  const [form, setForm] = useState(initialForm);
  const [archivo, setArchivo] = useState(null);
  const [preview, setPreview] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [empleadoIdManual, setEmpleadoIdManual] = useState("");
  const msgTimer = useRef(null);

  const empleado = dashboard?.empleado || {};
  const kpis = dashboard?.kpis || {};

  const paramsEmpleado = useMemo(() => {
    const params = {};
    if (empleadoIdManual) params.empleado_id = empleadoIdManual;
    return params;
  }, [empleadoIdManual]);

  const notificar = useCallback((tipo, titulo, texto = "") => {
    if (msgTimer.current) clearTimeout(msgTimer.current);
    setMensaje({ tipo, titulo, texto });
    msgTimer.current = setTimeout(() => setMensaje(null), 5200);
  }, []);

  const cargarDatos = useCallback(async () => {
    setLoading(true);
    try {
      const filtroParams = {
        ...paramsEmpleado,
        tipo_reporte: filtros.tipo_reporte,
        prioridad: filtros.prioridad,
        estado: filtros.estado,
        buscar: filtros.buscar,
      };

      const [dash, caps, epps, exs, reps] = await Promise.all([
        dashboardPortalEmpleadoSST(paramsEmpleado),
        listarMisCapacitacionesSST(paramsEmpleado).catch(() => []),
        listarMisEPPSST(paramsEmpleado).catch(() => []),
        listarMisExamenesSST(paramsEmpleado).catch(() => []),
        listarReportesEmpleadoSST(filtroParams).catch(() => []),
      ]);

      setDashboard(dash);
      setCapacitaciones(caps);
      setEpp(epps);
      setExamenes(exs);
      setReportes(reps);
    } catch (error) {
      console.error("Error cargando Portal Empleado SST", error);
      notificar("error", "No fue posible cargar el portal", construirMensajeError(error));
    } finally {
      setLoading(false);
    }
  }, [filtros, notificar, paramsEmpleado]);

  useEffect(() => {
    cargarDatos();
    return () => {
      if (msgTimer.current) clearTimeout(msgTimer.current);
    };
  }, [cargarDatos]);

  const reportesFiltrados = reportes;

  const actualizarFiltro = (field, value) => {
    setFiltros((prev) => ({ ...prev, [field]: value }));
  };

  const limpiarFiltros = () => {
    setFiltros(filtrosIniciales);
  };

  const guardarReporte = async (event) => {
    event.preventDefault();

    if (!form.titulo.trim() || !form.descripcion.trim()) {
      notificar("error", "Reporte incompleto", "El título y la descripción son obligatorios.");
      return;
    }

    try {
      setSaving(true);
      const formData = new FormData();
      Object.entries(form).forEach(([key, value]) => {
        if (value !== undefined && value !== null && String(value).trim() !== "") {
          formData.append(key, value);
        }
      });
      if (empleadoIdManual) formData.append("empleado_id", empleadoIdManual);
      if (archivo) formData.append("archivo", archivo);

      const creado = await crearReporteEmpleadoFormSST(formData);
      setForm(initialForm);
      setArchivo(null);
      setTab("reportes");
      await cargarDatos();
      notificar("success", "Reporte SST enviado correctamente", `${creado.codigo} · ${creado.titulo}`);
    } catch (error) {
      console.error("Error creando reporte", error);
      notificar("error", "No fue posible enviar el reporte", construirMensajeError(error));
    } finally {
      setSaving(false);
    }
  };

  const cambiarEstado = async (reporte, estado) => {
    try {
      await cambiarEstadoReporteEmpleadoSST(reporte.id, {
        estado,
        observaciones: `Cambio de estado desde Portal Empleado SST a ${estado}.`,
      });
      await cargarDatos();
      notificar("success", "Estado actualizado", `${reporte.codigo} ahora está ${normalizarTexto(estado)}.`);
    } catch (error) {
      console.error("Error actualizando estado", error);
      notificar("error", "No fue posible actualizar el estado", construirMensajeError(error));
    }
  };

  const renderReporte = (reporte) => (
    <article className="portal-report-card" key={reporte.id}>
      <div className={`portal-report-priority ${colorPrioridad(reporte.prioridad)}`}>
        {String(reporte.prioridad || "M").slice(0, 1)}
      </div>

      <div className="portal-report-main">
        <div className="portal-report-title">
          <div>
            <strong>{reporte.titulo}</strong>
            <span>{reporte.codigo} · {normalizarTexto(reporte.tipo_reporte)}</span>
          </div>
          <div className="portal-report-badges">
            <span className={`portal-badge ${colorPrioridad(reporte.prioridad)}`}>{normalizarTexto(reporte.prioridad)}</span>
            <span className={`portal-badge ${colorEstado(reporte.estado)}`}>{normalizarTexto(reporte.estado)}</span>
          </div>
        </div>

        <p>{reporte.descripcion}</p>

        <div className="portal-report-meta">
          <span><MapPin size={14} /> {reporte.ubicacion || "Sin ubicación"}</span>
          <span><UserRound size={14} /> {reporte.empleado_nombre || empleado.nombre_completo || "Empleado"}</span>
          <span><Archive size={14} /> {reporte.area_nombre || "Sin área"}</span>
          <span><Bell size={14} /> {fmtFecha(reporte.fecha_reporte || reporte.fecha_creacion)}</span>
        </div>
      </div>

      <div className="portal-report-actions">
        {reporte.archivo_url && (
          <button type="button" title="Ver evidencia" onClick={() => setPreview(reporte)}>
            <Eye size={17} />
          </button>
        )}
        {reporte.archivo_url && (
          <a title="Descargar evidencia" href={urlArchivoPortalEmpleadoSST(reporte.archivo_url)} target="_blank" rel="noreferrer">
            <Download size={17} />
          </a>
        )}
        {reporte.estado !== "CERRADO" && (
          <button type="button" title="Cerrar reporte" onClick={() => cambiarEstado(reporte, "CERRADO")}>
            <CheckCircle2 size={17} />
          </button>
        )}
      </div>
    </article>
  );

  return (
    <main className="portal-empleado-page">
      <section className="portal-hero">
        <div>
          <span className="portal-tag"><ShieldCheck size={15} /> FASE 1.1.25.2 — Portal Empleado SST</span>
          <h1>Portal del Empleado SST Enterprise</h1>
          <p>
            Participación activa del trabajador: reportes de actos y condiciones inseguras, consulta de EPP, capacitaciones,
            exámenes médicos, evidencias y trazabilidad preventiva del SG-SST.
          </p>
        </div>
        <div className="portal-hero-actions">
          <button className="portal-btn secondary" type="button" onClick={cargarDatos} disabled={loading}>
            {loading ? <Loader2 className="spin" size={16} /> : <RefreshCcw size={16} />}
            Actualizar
          </button>
          <button className="portal-btn primary" type="button" onClick={() => setTab("reportar")}>
            <Megaphone size={16} /> Nuevo reporte
          </button>
        </div>
      </section>

      {mensaje && (
        <div className={`portal-message ${mensaje.tipo}`}>
          <strong>{mensaje.titulo}</strong>
          {mensaje.texto && <span>{mensaje.texto}</span>}
          <button type="button" onClick={() => setMensaje(null)}><X size={16} /></button>
        </div>
      )}

      <section className="portal-profile-card">
        <div className="portal-avatar">{(empleado.nombres || empleado.nombre_completo || "E").slice(0, 1)}</div>
        <div className="portal-profile-info">
          <span>Empleado asociado</span>
          <strong>{empleado.nombre_completo || "Empleado SST"}</strong>
          <p>{empleado.empresa_nombre || "Empresa no identificada"} · {empleado.area_nombre || "Área no identificada"} · {empleado.cargo_nombre || "Cargo no identificado"}</p>
        </div>
        <label className="portal-manual-employee">
          <span>ID empleado para pruebas</span>
          <input
            value={empleadoIdManual}
            onChange={(e) => setEmpleadoIdManual(e.target.value)}
            placeholder="Opcional"
            type="number"
            min="1"
          />
        </label>
      </section>

      <nav className="portal-tabs">
        {[
          ["dashboard", "Resumen", ShieldCheck],
          ["reportar", "Reportar", Megaphone],
          ["reportes", "Mis reportes", ClipboardList],
          ["capacitaciones", "Capacitaciones", GraduationCap],
          ["epp", "EPP", HardHat],
          ["examenes", "Exámenes", HeartPulse],
        ].map(([key, label, Icon]) => (
          <button key={key} className={tab === key ? "active" : ""} type="button" onClick={() => setTab(key)}>
            <Icon size={17} /> {label}
          </button>
        ))}
      </nav>

      {loading && (
        <div className="portal-loading">
          <Loader2 className="spin" size={30} /> Cargando Portal del Empleado SST...
        </div>
      )}

      {!loading && tab === "dashboard" && (
        <section className="portal-dashboard-grid">
          <div className="portal-main-col">
            <div className="portal-kpis">
              <KpiCard icon={GraduationCap} label="Capacitaciones" value={kpis.capacitaciones} tone="blue" />
              <KpiCard icon={HardHat} label="EPP entregados" value={kpis.epp_entregados} tone="green" />
              <KpiCard icon={HeartPulse} label="Exámenes" value={kpis.examenes} tone="purple" />
              <KpiCard icon={ClipboardList} label="Reportes" value={kpis.reportes} tone="orange" />
              <KpiCard icon={AlertTriangle} label="Reportes abiertos" value={kpis.reportes_abiertos} tone="red" />
            </div>

            <section className="portal-panel">
              <header>
                <div>
                  <h2>Reportes recientes</h2>
                  <p>Últimos reportes SST creados desde el portal del empleado.</p>
                </div>
                <button className="portal-btn secondary" type="button" onClick={() => setTab("reportes")}>Ver todos</button>
              </header>

              {(dashboard?.reportes_recientes || []).length ? (
                <div className="portal-report-list">
                  {dashboard.reportes_recientes.map(renderReporte)}
                </div>
              ) : (
                <EmptyState icon={ClipboardList} title="Sin reportes recientes" text="Cuando reportes una condición o acto inseguro aparecerá aquí." />
              )}
            </section>
          </div>

          <aside className="portal-side-col">
            <section className="portal-side-card">
              <h3><Bell size={17} /> Alertas personales SST</h3>
              <ul>
                {(dashboard?.alertas || []).map((a, idx) => <li key={`${a}-${idx}`}>{a}</li>)}
              </ul>
            </section>
            <section className="portal-side-card pro">
              <h3><Sparkles size={17} /> Recomendación PRO</h3>
              <p>Reporta condiciones inseguras con evidencia fotográfica para activar alertas automáticas al Coordinador SST.</p>
            </section>
          </aside>
        </section>
      )}

      {!loading && tab === "reportar" && (
        <section className="portal-form-layout">
          <form className="portal-form-card" onSubmit={guardarReporte}>
            <header>
              <div>
                <span>Nuevo reporte SST</span>
                <h2>Reportar acto o condición insegura</h2>
                <p>El reporte generará una notificación automática para el equipo SST.</p>
              </div>
              <UploadCloud size={34} />
            </header>

            <div className="portal-type-grid">
              {tiposReporte.map(({ value, label, icon: Icon }) => (
                <button
                  key={value}
                  type="button"
                  className={form.tipo_reporte === value ? "active" : ""}
                  onClick={() => setForm((prev) => ({ ...prev, tipo_reporte: value }))}
                >
                  <Icon size={20} />
                  <span>{label}</span>
                </button>
              ))}
            </div>

            <div className="portal-form-grid">
              <label>
                <span>Prioridad</span>
                <select value={form.prioridad} onChange={(e) => setForm({ ...form, prioridad: e.target.value })}>
                  {prioridades.map((p) => <option key={p} value={p}>{normalizarTexto(p)}</option>)}
                </select>
              </label>

              <label>
                <span>Ubicación</span>
                <input value={form.ubicacion} onChange={(e) => setForm({ ...form, ubicacion: e.target.value })} placeholder="Ej: Pasillo principal, bodega, oficina..." />
              </label>

              <label className="full">
                <span>Título del reporte</span>
                <input value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} placeholder="Ej: Cable eléctrico expuesto en zona de tránsito" maxLength={255} />
              </label>

              <label className="full">
                <span>Descripción</span>
                <textarea value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} placeholder="Describe qué ocurrió, dónde ocurrió, quién podría estar expuesto y cuál es la condición observada." />
              </label>

              <label className="full">
                <span>Acción inmediata tomada</span>
                <textarea value={form.accion_inmediata} onChange={(e) => setForm({ ...form, accion_inmediata: e.target.value })} placeholder="Ej: Se señalizó el área y se informó al coordinador SST." />
              </label>

              <label className="full">
                <span>Observaciones</span>
                <textarea value={form.observaciones} onChange={(e) => setForm({ ...form, observaciones: e.target.value })} placeholder="Observaciones adicionales." />
              </label>
            </div>

            <div className="portal-upload-box">
              <Camera size={24} />
              <div>
                <strong>{archivo?.name || "Adjuntar evidencia"}</strong>
                <span>PDF, JPG, PNG, WEBP, MP4 o MOV. Máximo 25 MB.</span>
              </div>
              <input type="file" accept="image/*,application/pdf,video/*" onChange={(e) => setArchivo(e.target.files?.[0] || null)} />
            </div>

            <footer>
              <button className="portal-btn secondary" type="button" onClick={() => setForm(initialForm)}>Limpiar</button>
              <button className="portal-btn primary" type="submit" disabled={saving}>
                {saving ? <Loader2 className="spin" size={16} /> : <Send size={16} />}
                Enviar reporte SST
              </button>
            </footer>
          </form>
        </section>
      )}

      {!loading && tab === "reportes" && (
        <section className="portal-panel">
          <header>
            <div>
              <h2>Mis reportes SST</h2>
              <p>Seguimiento de actos, condiciones inseguras, incidentes, accidentes y sugerencias.</p>
            </div>
            <button className="portal-btn primary" type="button" onClick={() => setTab("reportar")}><Megaphone size={16} /> Nuevo reporte</button>
          </header>

          <div className="portal-filters">
            <div className="portal-search">
              <Search size={16} />
              <input value={filtros.buscar} onChange={(e) => actualizarFiltro("buscar", e.target.value)} placeholder="Buscar por código, título, descripción o ubicación..." />
            </div>
            <select value={filtros.tipo_reporte} onChange={(e) => actualizarFiltro("tipo_reporte", e.target.value)}>
              <option value="TODOS">Todos los tipos</option>
              {tiposReporte.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
            <select value={filtros.prioridad} onChange={(e) => actualizarFiltro("prioridad", e.target.value)}>
              <option value="TODOS">Todas las prioridades</option>
              {prioridades.map((p) => <option key={p} value={p}>{normalizarTexto(p)}</option>)}
            </select>
            <select value={filtros.estado} onChange={(e) => actualizarFiltro("estado", e.target.value)}>
              <option value="TODOS">Todos los estados</option>
              {estados.map((e) => <option key={e} value={e}>{normalizarTexto(e)}</option>)}
            </select>
            <button type="button" className="portal-btn secondary" onClick={limpiarFiltros}><Filter size={16} /> Limpiar</button>
          </div>

          {reportesFiltrados.length ? (
            <div className="portal-report-list">
              {reportesFiltrados.map(renderReporte)}
            </div>
          ) : (
            <EmptyState icon={ClipboardList} title="Sin reportes SST" text="Crea el primer reporte desde el Portal del Empleado." />
          )}
        </section>
      )}

      {!loading && tab === "capacitaciones" && (
        <section className="portal-panel">
          <header>
            <div><h2>Mis capacitaciones</h2><p>Capacitaciones SST asociadas al empleado.</p></div>
          </header>
          {capacitaciones.length ? (
            <div className="portal-simple-grid">
              {capacitaciones.map((c) => (
                <article className="portal-simple-card" key={c.id}>
                  <GraduationCap size={21} />
                  <div>
                    <strong>{c.nombre || c.tema || "Capacitación SST"}</strong>
                    <span>{c.codigo || "Sin código"} · {c.asistio ? "Asistió" : "Pendiente asistencia"}</span>
                    <p>Fecha: {c.fecha_ejecucion || c.fecha_programada || "Sin fecha"} · Evaluación: {c.evaluacion || 0}</p>
                  </div>
                </article>
              ))}
            </div>
          ) : <EmptyState icon={GraduationCap} title="Sin capacitaciones" text="No hay capacitaciones registradas para este empleado." />}
        </section>
      )}

      {!loading && tab === "epp" && (
        <section className="portal-panel">
          <header>
            <div><h2>Mis EPP</h2><p>Entregas de elementos de protección personal registradas.</p></div>
          </header>
          {epp.length ? (
            <div className="portal-simple-grid">
              {epp.map((item) => (
                <article className="portal-simple-card" key={item.id}>
                  <HardHat size={21} />
                  <div>
                    <strong>{item.nombre || "Elemento EPP"}</strong>
                    <span>{item.codigo || "Sin código"} · Cantidad: {item.cantidad || 1}</span>
                    <p>Entrega: {item.fecha_entrega || "Sin fecha"} · Reposición: {item.fecha_reposicion || "Sin fecha"} · {item.recibido_por_empleado ? "Recibido" : "Pendiente firma"}</p>
                  </div>
                </article>
              ))}
            </div>
          ) : <EmptyState icon={HardHat} title="Sin EPP" text="No hay entregas EPP registradas para este empleado." />}
        </section>
      )}

      {!loading && tab === "examenes" && (
        <section className="portal-panel">
          <header>
            <div><h2>Mis exámenes médicos</h2><p>Información básica de exámenes ocupacionales registrados.</p></div>
          </header>
          {examenes.length ? (
            <div className="portal-simple-grid">
              {examenes.map((item) => (
                <article className="portal-simple-card" key={item.id}>
                  <HeartPulse size={21} />
                  <div>
                    <strong>{normalizarTexto(item.tipo_examen) || "Examen médico"}</strong>
                    <span>{item.concepto || "Sin concepto"} · {item.estado || "Sin estado"}</span>
                    <p>Fecha: {item.fecha_examen || "Sin fecha"} · Vence: {item.fecha_vencimiento || "Sin vencimiento"}</p>
                  </div>
                </article>
              ))}
            </div>
          ) : <EmptyState icon={HeartPulse} title="Sin exámenes" text="No hay exámenes médicos registrados para este empleado." />}
        </section>
      )}

      <EvidencePreview reporte={preview} onClose={() => setPreview(null)} />
    </main>
  );
}
