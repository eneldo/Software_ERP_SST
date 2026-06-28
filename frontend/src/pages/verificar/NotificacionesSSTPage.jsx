// ============================================================
// CENTRO DE NOTIFICACIONES SST ENTERPRISE - ERP SST PRO
// FASE 1.1.24.2 — Frontend Centro de Notificaciones SST
// Archivo: frontend/src/pages/verificar/NotificacionesSSTPage.jsx
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Bell,
  BellRing,
  CheckCircle2,
  Clock,
  Eye,
  Filter,
  Inbox,
  RefreshCcw,
  Search,
  ShieldAlert,
  Trash2,
  X,
  Zap,
} from "lucide-react";

import {
  dashboardNotificacionesSST,
  eliminarNotificacionSST,
  generarNotificacionesSST,
  listarNotificacionesSST,
  marcarNotificacionLeidaSST,
  marcarTodasNotificacionesLeidasSST,
} from "../../api/notificacionesSstApi";

import { listarEmpresasSST } from "../../api/empresaSstApi";
import { listarSedesSST } from "../../api/sedeSstApi";
import { listarAreasSST } from "../../api/areaSstApi";
import "../../styles/notificaciones-sst.css";

const initialFilters = {
  empresa_id: "",
  sede_id: "",
  area_id: "",
  modulo: "TODOS",
  tipo: "TODOS",
  prioridad: "TODOS",
  estado: "TODOS",
  q: "",
};

const PRIORIDADES = ["TODOS", "CRITICA", "ALTA", "MEDIA", "BAJA"];
const ESTADOS = ["TODOS", "NO_LEIDA", "LEIDA"];
const MODULOS = [
  "TODOS",
  "CAPA",
  "INSPECCIONES",
  "HALLAZGOS",
  "INCIDENTES",
  "ACCIDENTES",
  "EXAMENES",
  "EPP",
  "CAPACITACIONES",
  "AUDITORIAS",
  "PLAN_MEJORAMIENTO",
];
const TIPOS = ["TODOS", "VENCIMIENTO", "PENDIENTE", "CRITICO", "SEGUIMIENTO", "DOCUMENTAL", "SISTEMA"];

const fmt = (value) => {
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
    return String(value);
  }
};

const badgeClass = (value) => String(value || "MEDIA").toLowerCase().replace("critica", "crítica");

const normalizarError = (error) => {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((x) => x.msg || JSON.stringify(x)).join("\n");
  if (typeof detail === "string") return detail;
  return error?.message || "Error desconocido";
};

export default function NotificacionesSSTPage() {
  const [notificaciones, setNotificaciones] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [areas, setAreas] = useState([]);
  const [filters, setFilters] = useState(initialFilters);
  const [loading, setLoading] = useState(false);
  const [alerta, setAlerta] = useState(null);
  const [detalle, setDetalle] = useState(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const params = useMemo(() => {
    const estadoMap = {
      NO_LEIDA: false,
      LEIDA: true,
    };

    return {
      empresa_id: filters.empresa_id,
      sede_id: filters.sede_id,
      area_id: filters.area_id,
      modulo: filters.modulo,
      tipo: filters.tipo,
      prioridad: filters.prioridad,
      leida: estadoMap[filters.estado],
      q: filters.q,
    };
  }, [filters]);

  const mostrarAlerta = (tipo, mensaje) => {
    setAlerta({ tipo, mensaje });
    setTimeout(() => setAlerta(null), 4200);
  };

  const cargarCatalogos = async () => {
    try {
      const [emp, sed, are] = await Promise.all([
        listarEmpresasSST().catch(() => []),
        listarSedesSST().catch(() => []),
        listarAreasSST().catch(() => []),
      ]);
      setEmpresas(Array.isArray(emp) ? emp : []);
      setSedes(Array.isArray(sed) ? sed : []);
      setAreas(Array.isArray(are) ? are : []);
    } catch (error) {
      console.error("Error cargando catálogos", error);
    }
  };

  const cargarDatos = async () => {
    setLoading(true);
    try {
      const [items, dash] = await Promise.all([
        listarNotificacionesSST(params),
        dashboardNotificacionesSST(params),
      ]);
      setNotificaciones(Array.isArray(items) ? items : []);
      setDashboard(dash || null);
    } catch (error) {
      console.error("Error cargando notificaciones", error);
      mostrarAlerta("error", normalizarError(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarCatalogos();
  }, []);

  useEffect(() => {
    cargarDatos();
    setPage(1);
  }, [params]);

  const generarAlertas = async () => {
    setLoading(true);
    try {
      const result = await generarNotificacionesSST({ empresa_id: filters.empresa_id });
      mostrarAlerta("success", result?.mensaje || "Alertas SST generadas correctamente.");
      await cargarDatos();
    } catch (error) {
      mostrarAlerta("error", normalizarError(error));
    } finally {
      setLoading(false);
    }
  };

  const marcarLeida = async (item) => {
    try {
      await marcarNotificacionLeidaSST(item.id);
      mostrarAlerta("success", "Notificación marcada como leída.");
      await cargarDatos();
    } catch (error) {
      mostrarAlerta("error", normalizarError(error));
    }
  };

  const leerTodas = async () => {
    try {
      await marcarTodasNotificacionesLeidasSST({ empresa_id: filters.empresa_id });
      mostrarAlerta("success", "Todas las notificaciones fueron marcadas como leídas.");
      await cargarDatos();
    } catch (error) {
      mostrarAlerta("error", normalizarError(error));
    }
  };

  const eliminar = async (item) => {
    if (!window.confirm("¿Eliminar esta notificación del centro SST?")) return;
    try {
      await eliminarNotificacionSST(item.id);
      mostrarAlerta("success", "Notificación eliminada correctamente.");
      await cargarDatos();
    } catch (error) {
      mostrarAlerta("error", normalizarError(error));
    }
  };

  const filtered = useMemo(() => {
    const q = filters.q.trim().toLowerCase();
    if (!q) return notificaciones;
    return notificaciones.filter((n) =>
      [n.titulo, n.descripcion, n.modulo, n.tipo, n.prioridad]
        .filter(Boolean)
        .some((x) => String(x).toLowerCase().includes(q))
    );
  }, [notificaciones, filters.q]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const pageItems = filtered.slice((page - 1) * pageSize, page * pageSize);

  const kpis = dashboard || {};
  const porModulo = kpis.por_modulo || {};
  const recomendaciones = kpis.recomendaciones || [];

  return (
    <section className="notificaciones-page">
      <div className="notificaciones-hero">
        <div>
          <span className="notificaciones-tag"><BellRing size={16} /> FASE 1.1.24 — ALERTAS SST</span>
          <h1>Centro de Notificaciones SST Enterprise</h1>
          <p>Alertas inteligentes para vencimientos, acciones críticas, seguimiento, gestión documental y control preventivo del SG-SST.</p>
        </div>

        <div className="notificaciones-hero-actions">
          <button className="btn-noti secondary" onClick={cargarDatos} disabled={loading}>
            <RefreshCcw size={16} className={loading ? "spin" : ""} /> Actualizar
          </button>
          <button className="btn-noti secondary" onClick={leerTodas} disabled={loading}>
            <CheckCircle2 size={16} /> Leer todas
          </button>
          <button className="btn-noti primary" onClick={generarAlertas} disabled={loading}>
            <Zap size={16} /> Generar alertas
          </button>
        </div>
      </div>

      {alerta && (
        <div className={`notificaciones-alert ${alerta.tipo}`}>
          {alerta.tipo === "error" ? <AlertTriangle size={18} /> : <CheckCircle2 size={18} />}
          <span>{alerta.mensaje}</span>
          <button onClick={() => setAlerta(null)}><X size={16} /></button>
        </div>
      )}

      <div className="notificaciones-kpis">
        <article className="noti-kpi-card critical"><ShieldAlert size={22} /><span>Críticas</span><strong>{kpis.criticas || 0}</strong></article>
        <article className="noti-kpi-card high"><AlertTriangle size={22} /><span>Altas</span><strong>{kpis.altas || 0}</strong></article>
        <article className="noti-kpi-card medium"><Clock size={22} /><span>Medias</span><strong>{kpis.medias || 0}</strong></article>
        <article className="noti-kpi-card low"><Bell size={22} /><span>Bajas</span><strong>{kpis.bajas || 0}</strong></article>
        <article className="noti-kpi-card unread"><Inbox size={22} /><span>No leídas</span><strong>{kpis.no_leidas || 0}</strong></article>
        <article className="noti-kpi-card read"><CheckCircle2 size={22} /><span>Leídas</span><strong>{kpis.leidas || 0}</strong></article>
      </div>

      <div className="notificaciones-grid">
        <main className="notificaciones-main">
          <div className="notificaciones-panel">
            <div className="notificaciones-toolbar">
              <div className="notificaciones-search">
                <Search size={17} />
                <input
                  value={filters.q}
                  onChange={(e) => setFilters({ ...filters, q: e.target.value })}
                  placeholder="Buscar por título, descripción, módulo o prioridad..."
                />
              </div>
              <button className="btn-noti secondary" onClick={() => setFilters(initialFilters)}><Filter size={16} /> Limpiar</button>
            </div>

            <div className="notificaciones-filters">
              <select value={filters.empresa_id} onChange={(e) => setFilters({ ...filters, empresa_id: e.target.value })}>
                <option value="">Todas las empresas</option>
                {empresas.map((e) => <option key={e.id} value={e.id}>{e.nombre || e.razon_social}</option>)}
              </select>
              <select value={filters.sede_id} onChange={(e) => setFilters({ ...filters, sede_id: e.target.value })}>
                <option value="">Todas las sedes</option>
                {sedes.map((s) => <option key={s.id} value={s.id}>{s.nombre}</option>)}
              </select>
              <select value={filters.area_id} onChange={(e) => setFilters({ ...filters, area_id: e.target.value })}>
                <option value="">Todas las áreas</option>
                {areas.map((a) => <option key={a.id} value={a.id}>{a.nombre}</option>)}
              </select>
              <select value={filters.modulo} onChange={(e) => setFilters({ ...filters, modulo: e.target.value })}>
                {MODULOS.map((m) => <option key={m} value={m}>{m}</option>)}
              </select>
              <select value={filters.prioridad} onChange={(e) => setFilters({ ...filters, prioridad: e.target.value })}>
                {PRIORIDADES.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
              <select value={filters.tipo} onChange={(e) => setFilters({ ...filters, tipo: e.target.value })}>
                {TIPOS.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
              <select value={filters.estado} onChange={(e) => setFilters({ ...filters, estado: e.target.value })}>
                {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
              </select>
            </div>

            <div className="notificaciones-list">
              {pageItems.length ? pageItems.map((n) => (
                <article key={n.id} className={`notificacion-item ${n.leida ? "read" : "unread"}`}>
                  <div className={`notificacion-priority ${badgeClass(n.prioridad)}`}>
                    {String(n.prioridad || "MEDIA").slice(0, 1)}
                  </div>
                  <div className="notificacion-body">
                    <div className="notificacion-head">
                      <strong>{n.titulo}</strong>
                      <span className={`notificacion-badge ${badgeClass(n.prioridad)}`}>{n.prioridad || "MEDIA"}</span>
                    </div>
                    <p>{n.descripcion}</p>
                    <div className="notificacion-meta">
                      <span>{n.modulo || "SST"}</span>
                      <span>{n.tipo || "ALERTA"}</span>
                      <span>{fmt(n.fecha_evento || n.fecha_creacion)}</span>
                      {n.leida ? <span>Leída</span> : <span>No leída</span>}
                    </div>
                  </div>
                  <div className="notificacion-actions">
                    <button title="Ver detalle" onClick={() => setDetalle(n)}><Eye size={16} /></button>
                    {!n.leida && <button title="Marcar leída" onClick={() => marcarLeida(n)}><CheckCircle2 size={16} /></button>}
                    <button title="Eliminar" onClick={() => eliminar(n)}><Trash2 size={16} /></button>
                  </div>
                </article>
              )) : (
                <div className="notificaciones-empty">
                  <Inbox size={36} />
                  <strong>Sin notificaciones SST</strong>
                  <span>Genera alertas o ajusta los filtros para ver resultados.</span>
                </div>
              )}
            </div>

            <div className="notificaciones-pagination">
              <span>Mostrando {pageItems.length} de {filtered.length} notificaciones</span>
              <div>
                <select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}>
                  {[10, 20, 50].map((n) => <option key={n} value={n}>{n}</option>)}
                </select>
                <button disabled={page <= 1} onClick={() => setPage(page - 1)}>‹</button>
                <span>Página {page} / {totalPages}</span>
                <button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>›</button>
              </div>
            </div>
          </div>
        </main>

        <aside className="notificaciones-side">
          <article className="notificaciones-side-card">
            <h3>Distribución por módulo</h3>
            {Object.entries(porModulo).length ? Object.entries(porModulo).map(([mod, value]) => (
              <div className="noti-bar-row" key={mod}>
                <div><span>{mod}</span><strong>{value}</strong></div>
                <i><b style={{ width: `${Math.min(100, Number(value) * 12)}%` }} /></i>
              </div>
            )) : <p className="notificaciones-empty-text">Sin datos por módulo.</p>}
          </article>

          <article className="notificaciones-side-card">
            <h3>Recomendaciones PRO</h3>
            <ul>
              {recomendaciones.length ? recomendaciones.map((r, idx) => <li key={idx}>{r}</li>) : <li>Gestión de alertas estable.</li>}
            </ul>
          </article>
        </aside>
      </div>

      {detalle && (
        <div className="noti-modal-backdrop" onClick={() => setDetalle(null)}>
          <div className="noti-detail-modal" onClick={(e) => e.stopPropagation()}>
            <header>
              <div>
                <span>Detalle de notificación SST</span>
                <h2>{detalle.titulo}</h2>
                <p>{detalle.modulo} · {detalle.tipo}</p>
              </div>
              <button onClick={() => setDetalle(null)}><X size={22} /></button>
            </header>
            <div className="noti-detail-grid">
              <article><span>Prioridad</span><strong>{detalle.prioridad}</strong></article>
              <article><span>Estado</span><strong>{detalle.leida ? "Leída" : "No leída"}</strong></article>
              <article><span>Fecha evento</span><strong>{fmt(detalle.fecha_evento)}</strong></article>
              <article className="wide"><span>Descripción</span><strong>{detalle.descripcion}</strong></article>
              <article><span>Empresa</span><strong>{detalle.empresa_nombre || detalle.empresa_id || "Sin empresa"}</strong></article>
              <article><span>Sede</span><strong>{detalle.sede_nombre || detalle.sede_id || "Sin sede"}</strong></article>
              <article><span>Área</span><strong>{detalle.area_nombre || detalle.area_id || "Sin área"}</strong></article>
              <article className="wide"><span>URL destino</span><strong>{detalle.url_destino || "Sin ruta asociada"}</strong></article>
            </div>
            <footer>
              {!detalle.leida && <button className="btn-noti secondary" onClick={() => marcarLeida(detalle)}>Marcar leída</button>}
              <button className="btn-noti primary" onClick={() => setDetalle(null)}>Cerrar</button>
            </footer>
          </div>
        </div>
      )}
    </section>
  );
}
