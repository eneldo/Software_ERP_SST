// ============================================================
// MIS CASOS SST — REPORTES ASIGNADOS
// ERP SST PRO
// FASE 1.1.25.5 — WORKFLOW INTELIGENTE REPORTES SST
// Archivo: frontend/src/pages/verificar/MisCasosSSTPage.jsx
// ============================================================

import React, { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, Eye, Loader2, RefreshCw, Search, X, Zap } from "lucide-react";

import {
  cerrarReporteAnonimoSST,
  crearCAPADesdeReporteSST,
  crearHallazgoDesdeReporteSST,
  crearInspeccionDesdeReporteSST,
  listarMisCasosSST,
  listarResponsablesSST,
  marcarReporteAnonimoEnProcesoSST,
} from "../../api/reportesAnonimosAdminApi";
import "../../styles/reportes-anonimos-admin.css";

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

const fechaHumana = (value) => {
  if (!value) return "Sin fecha";
  try {
    return new Date(value).toLocaleString("es-CO", { year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
  } catch {
    return value;
  }
};

const mostrarError = (error, fallback = "Ocurrió un error") => {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((e) => `${e.loc?.join(" → ")}: ${e.msg}`).join("\n");
  if (typeof detail === "string") return detail;
  return error?.message || fallback;
};

export default function MisCasosSSTPage() {
  const [loading, setLoading] = useState(false);
  const [accionLoading, setAccionLoading] = useState(false);
  const [responsables, setResponsables] = useState([]);
  const [responsable, setResponsable] = useState("");
  const [casos, setCasos] = useState([]);
  const [detalle, setDetalle] = useState(null);
  const [alerta, setAlerta] = useState(null);
  const [incluirCerrados, setIncluirCerrados] = useState(false);

  const cargarResponsables = async () => {
    const data = await listarResponsablesSST().catch(() => []);
    setResponsables(Array.isArray(data) ? data : []);
  };

  const cargarCasos = async () => {
    setLoading(true);
    try {
      const data = await listarMisCasosSST({ responsable, incluir_cerrados: incluirCerrados });
      setCasos(Array.isArray(data?.casos) ? data.casos : []);
    } catch (error) {
      setAlerta({ type: "error", text: mostrarError(error, "No fue posible cargar mis casos SST") });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarResponsables();
  }, []);

  useEffect(() => {
    cargarCasos();
  }, [responsable, incluirCerrados]);

  const ejecutar = async (fn, okMsg) => {
    setAccionLoading(true);
    try {
      const res = await fn();
      setAlerta({ type: "success", text: okMsg || res?.mensaje || "Acción completada." });
      await cargarCasos();
    } catch (error) {
      setAlerta({ type: "error", text: mostrarError(error, "No fue posible completar la acción") });
    } finally {
      setAccionLoading(false);
    }
  };

  return (
    <section className="ra-page">
      <div className="ra-hero">
        <div>
          <h1>Mis Casos SST</h1>
          <p>Consulta y gestiona los reportes asignados a tu responsabilidad.</p>
        </div>
        <button title="Actualizar" className="ra-btn secondary" onClick={cargarCasos} disabled={loading}>{loading ? <Loader2 className="spin" size={17} /> : <RefreshCw size={17} />} Actualizar</button>
      </div>

      {alerta && <div className={`ra-alert ${alerta.type}`}><span>{alerta.text}</span><button onClick={() => setAlerta(null)}><X size={16} /></button></div>}

      <div className="ra-panel">
        <div className="ra-toolbar">
          <label className="ra-search"><Search size={18} /><select value={responsable} onChange={(e) => setResponsable(e.target.value)}><option value="">Todos los responsables SST</option>{responsables.map((r) => <option key={r.id} value={r.nombre}>{r.nombre} — {r.area_nombre || "Sin área"}</option>)}</select></label>
          <label className="ra-check"><input type="checkbox" checked={incluirCerrados} onChange={(e) => setIncluirCerrados(e.target.checked)} /> Incluir cerrados</label>
        </div>

        <div className="ra-list">
          {loading ? <div className="ra-empty"><Loader2 className="spin" /> Cargando casos...</div> : casos.length === 0 ? <div className="ra-empty">No hay casos asignados con los filtros actuales.</div> : casos.map((item) => (
            <article key={item.id} className={`ra-item estado-${String(item.estado).toLowerCase()}`}>
              <div className={`ra-letter prioridad-${String(item.prioridad).toLowerCase()}`}>{String(item.prioridad || "M").slice(0, 1)}</div>
              <div className="ra-item-body">
                <header><div><strong>{item.titulo}</strong><p>{tipoLabel[item.tipo_reporte] || item.tipo_reporte} · {item.ubicacion || "Sin ubicación"}</p></div><span className={`ra-pill prioridad-${String(item.prioridad).toLowerCase()}`}>{item.prioridad}</span></header>
                <p className="ra-desc">{item.descripcion}</p>
                <div className="ra-meta"><span>{item.codigo}</span><span>{estadoLabel[item.estado] || item.estado}</span><span>{item.responsable_asignado || "Sin responsable"}</span><span>{fechaHumana(item.fecha_reporte)}</span>{item.inspeccion_id && <span>INSP #{item.inspeccion_id}</span>}{item.capa_id && <span>CAPA #{item.capa_id}</span>}</div>
              </div>
              <div className="ra-actions"><button onClick={() => setDetalle(item)}><Eye size={17} /></button><button onClick={() => ejecutar(() => marcarReporteAnonimoEnProcesoSST(item.id), "Caso marcado en proceso.")} disabled={accionLoading}><Zap size={17} /></button><button onClick={() => ejecutar(() => cerrarReporteAnonimoSST(item.id, { accion_cierre: "Caso cerrado desde Mis Casos SST." }), "Caso cerrado.")} disabled={accionLoading}><CheckCircle2 size={17} /></button></div>
            </article>
          ))}
        </div>
      </div>

      {detalle && <div className="ra-modal-backdrop"><div className="ra-modal"><header><div><span>Detalle caso asignado</span><h2>{detalle.titulo}</h2><p>{detalle.codigo} · {estadoLabel[detalle.estado] || detalle.estado}</p></div><button onClick={() => setDetalle(null)}><X size={22} /></button></header><div className="ra-detail-grid"><article><span>Responsable</span><strong>{detalle.responsable_asignado || "Sin responsable"}</strong></article><article><span>Prioridad</span><strong>{detalle.prioridad}</strong></article><article><span>Estado</span><strong>{estadoLabel[detalle.estado] || detalle.estado}</strong></article><article className="wide"><span>Descripción</span><strong>{detalle.descripcion}</strong></article><article className="wide"><span>Trazabilidad</span><pre>{detalle.trazabilidad || "Sin trazabilidad"}</pre></article></div><footer><button className="ra-btn secondary" onClick={() => ejecutar(() => crearInspeccionDesdeReporteSST(detalle.id, { responsable: detalle.responsable_asignado }), "Inspección creada.")}><ClipboardCheck size={16} /> Crear inspección</button><button className="ra-btn secondary" onClick={() => ejecutar(() => crearHallazgoDesdeReporteSST(detalle.id, { responsable: detalle.responsable_asignado }), "Hallazgo creado.")}><AlertTriangle size={16} /> Crear hallazgo</button><button className="ra-btn secondary" onClick={() => ejecutar(() => crearCAPADesdeReporteSST(detalle.id, { responsable: detalle.responsable_asignado }), "CAPA creada.")}><AlertTriangle size={16} /> Crear CAPA</button><button className="ra-btn secondary" onClick={() => setDetalle(null)}>Cerrar</button></footer></div></div>}
    </section>
  );
}
