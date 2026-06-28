// ============================================================
// CENTRO DE MEDIDAS CORRECTIVAS ENTERPRISE — FRONTEND PRO
// ERP SST PRO
// FASE 1.1.8.7.4 — Workflow + Eficacia + Alertas Visual
// Archivo: frontend/src/pages/sst/MedidasCorrectivasPage.jsx
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Download,
  Eye,
  FileUp,
  Plus,
  RefreshCcw,
  Save,
  ShieldCheck,
  Target,
  TrendingUp,
  X,
} from "lucide-react";

import {
  crearMedidaCorrectiva,
  crearSeguimientoMedida,
  getMedidasCorrectivasExcelUrl,
  listarEvidenciasMedida,
  listarMedidasCorrectivas,
  listarSeguimientosMedida,
  obtenerDashboardMedidasCorrectivas,
  subirEvidenciaMedida,
} from "../../api/medidasCorrectivasApi";

import {
  archivarAlertaMedida,
  avanzarWorkflowMedida,
  evaluarEficaciaMedida,
  generarAlertasMedidas,
  listarAlertasMedidas,
  marcarAlertaMedidaLeida,
  obtenerWorkflowMedida,
} from "../../api/alertasMedidasApi";

import WorkflowTimeline from "../../components/medidas/WorkflowTimeline";
import EficaciaCard from "../../components/medidas/EficaciaCard";
import AlertasCard from "../../components/medidas/AlertasCard";
import { obtenerEvidenciasInteligentesMedida } from "../../api/medidasEvidenciasInteligentesApi";
import EvidenciasInteligentesPanel from "../../components/medidas/EvidenciasInteligentesPanel";
import TrazabilidadVisualPanel from "../../components/medidas/TrazabilidadVisualPanel";
import SemaforoEjecutivoPanel from "../../components/medidas/SemaforoEjecutivoPanel";
import EficaciaIndicadorTabla from "../../components/medidas/EficaciaIndicadorTabla";
import EficaciaResumenKpis from "../../components/medidas/EficaciaResumenKpis";
import MedidasCorrectivasBIDashboard from "../../components/medidas/MedidasCorrectivasBIDashboard";
import "../../styles/medidas-correctivas-enterprise.css";

import ExportacionesMedidaEnterprise from "../../components/medidas/ExportacionesMedidaEnterprise";
const DEFAULT_FILTERS = {
  empresa_id: "",
  estado: "",
  prioridad: "",
  tipo_accion: "",
  origen: "",
  q: "",
};

const DEFAULT_FORM = {
  empresa_id: 1,
  codigo: "",
  titulo: "",
  descripcion: "",
  tipo_accion: "CORRECTIVA",
  origen: "MANUAL",
  prioridad: "MEDIA",
  estado: "ABIERTA",
  responsable: "",
  fecha_compromiso: "",
  avance: 0,
  causa_raiz: "",
  porque_1: "",
  porque_2: "",
  porque_3: "",
  porque_4: "",
  porque_5: "",
  accion_inmediata: "",
  accion_correctiva: "",
  accion_preventiva: "",
  costo_estimado: 0,
  costo_real: 0,
  requiere_aprobacion: false,
  observaciones: "",
};

function badgeClass(value) {
  const v = String(value || "").toUpperCase();
  if (["CERRADA", "CERRADO"].includes(v)) return "ok";
  if (["VENCIDA", "CRITICA", "CRÍTICA", "ALTA"].includes(v)) return "danger";
  if (["VERIFICACION", "EN_EJECUCION", "PLANIFICADA", "PENDIENTE_APROBACION"].includes(v)) return "warn";
  return "info";
}

function todayCode() {
  const d = new Date();
  const stamp = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, "0")}${String(d.getDate()).padStart(2, "0")}${String(d.getHours()).padStart(2, "0")}${String(d.getMinutes()).padStart(2, "0")}`;
  return `MC-SST-${stamp}`;
}

function formatMoney(value) {
  return Number(value || 0).toLocaleString("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  });
}

export default function MedidasCorrectivasPage() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [dashboard, setDashboard] = useState({ kpis: {}, charts: {}, alertas: {}, recomendaciones: [] });
  const [alertasData, setAlertasData] = useState({ resumen: {}, alertas: [] });
  const [medidas, setMedidas] = useState([]);
  const [selected, setSelected] = useState(null);
  const [workflow, setWorkflow] = useState(null);
  const [inteligencia, setInteligencia] = useState(null);
  const [seguimientos, setSeguimientos] = useState([]);
  const [evidencias, setEvidencias] = useState([]);
  const [form, setForm] = useState({ ...DEFAULT_FORM, codigo: todayCode() });
  const [seguimientoForm, setSeguimientoForm] = useState({ avance: 0, responsable: "", resultado: "", comentario: "" });
  const [fileForm, setFileForm] = useState({ tipo_evidencia: "EVIDENCIA_DESPUES", descripcion: "", archivo: null });
  const [modal, setModal] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [mostrarBI, setMostrarBI] = useState(false);

  const kpis = dashboard?.kpis || {};
  const recomendaciones = dashboard?.recomendaciones || [];

  const semaforo = useMemo(() => {
    const score = Number(kpis.riesgo_score || 0);
    if (score >= 60) return { label: "Crítico", className: "danger" };
    if (score >= 25) return { label: "Atención", className: "warn" };
    return { label: "Controlado", className: "ok" };
  }, [kpis]);

  async function cargar(customFilters = filters) {
    setLoading(true);
    setError("");
    try {
      const [dash, list, alertas] = await Promise.all([
        obtenerDashboardMedidasCorrectivas(customFilters),
        listarMedidasCorrectivas(customFilters),
        listarAlertasMedidas({ empresa_id: customFilters.empresa_id, solo_pendientes: true, limit: 50 }),
      ]);
      setDashboard(dash);
      setMedidas(list);
      setAlertasData(alertas);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "No fue posible cargar el Centro de Medidas Correctivas.");
    } finally {
      setLoading(false);
    }
  }

  async function recargarAlertas() {
    try {
      const data = await listarAlertasMedidas({ empresa_id: filters.empresa_id, solo_pendientes: true, limit: 50 });
      setAlertasData(data);
    } catch (err) {
      console.error(err);
    }
  }

  async function regenerarAlertas() {
    setLoading(true);
    try {
      await generarAlertasMedidas({ empresa_id: filters.empresa_id });
      await cargar();
    } catch (err) {
      console.error(err);
      alert(err?.response?.data?.detail || "No fue posible generar alertas.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    cargar(DEFAULT_FILTERS);
  }, []);

  function updateForm(name, value) {
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function abrirDetalle(item) {
    setSelected(item);
    setModal("detalle");
    setWorkflow(null);
    setInteligencia(null);
    try {
      const [seg, evi, wf, intel] = await Promise.all([
        listarSeguimientosMedida(item.id),
        listarEvidenciasMedida(item.id),
        obtenerWorkflowMedida(item.id),
        obtenerEvidenciasInteligentesMedida(item.id),
      ]);
      setSeguimientos(seg);
      setEvidencias(evi);
      setWorkflow(wf);
      setInteligencia(intel);
    } catch (err) {
      console.error(err);
      alert(err?.response?.data?.detail || "No fue posible abrir el detalle de la medida.");
    }
  }

  async function refrescarWorkflow() {
    if (!selected) return;
    try {
      const wf = await obtenerWorkflowMedida(selected.id);
      setWorkflow(wf);
    } catch (err) {
      console.error(err);
    }
  }


  async function refrescarInteligencia() {
    if (!selected) return;
    try {
      const intel = await obtenerEvidenciasInteligentesMedida(selected.id);
      setInteligencia(intel);
    } catch (err) {
      console.error(err);
    }
  }

  async function avanzarWorkflow(siguienteEstado) {
    if (!selected || !siguienteEstado) return;
    setSaving(true);
    try {
      const wf = await avanzarWorkflowMedida(selected.id, {
        nuevo_estado: siguienteEstado,
        observacion: "Avance desde Centro de Medidas Correctivas Enterprise.",
      });
      setWorkflow(wf);
      await cargar();
    } catch (err) {
      console.error(err);
      alert(err?.response?.data?.detail || "No fue posible avanzar el workflow.");
    } finally {
      setSaving(false);
    }
  }

  async function guardarEficacia(payload) {
    if (!selected) return;
    setSaving(true);
    try {
      const wf = await evaluarEficaciaMedida(selected.id, payload);
      setWorkflow(wf);
      await cargar();
      const refreshed = await listarMedidasCorrectivas({ q: selected.codigo });
      setSelected(refreshed?.[0] || selected);
    } catch (err) {
      console.error(err);
      alert(err?.response?.data?.detail || "No fue posible guardar la eficacia.");
    } finally {
      setSaving(false);
    }
  }

  async function guardarMedida(event) {
    event.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...form,
        empresa_id: Number(form.empresa_id),
        avance: Number(form.avance || 0),
        costo_estimado: Number(form.costo_estimado || 0),
        costo_real: Number(form.costo_real || 0),
        fecha_compromiso: form.fecha_compromiso || null,
      };
      await crearMedidaCorrectiva(payload);
      setModal(null);
      setForm({ ...DEFAULT_FORM, codigo: todayCode() });
      await cargar();
    } catch (err) {
      console.error(err);
      alert(err?.response?.data?.detail || "No fue posible guardar la medida.");
    } finally {
      setSaving(false);
    }
  }

  async function guardarSeguimiento(event) {
    event.preventDefault();
    if (!selected) return;
    setSaving(true);
    try {
      await crearSeguimientoMedida(selected.id, {
        ...seguimientoForm,
        avance: Number(seguimientoForm.avance || 0),
      });
      await abrirDetalle(selected);
      await cargar();
      setSeguimientoForm({ avance: 0, responsable: "", resultado: "", comentario: "" });
    } catch (err) {
      console.error(err);
      alert(err?.response?.data?.detail || "No fue posible guardar el seguimiento.");
    } finally {
      setSaving(false);
    }
  }

  async function guardarEvidencia(event) {
    event.preventDefault();
    if (!selected || !fileForm.archivo) return;
    setSaving(true);
    try {
      const fd = new FormData();
      fd.append("tipo_evidencia", fileForm.tipo_evidencia);
      fd.append("descripcion", fileForm.descripcion);
      fd.append("archivo", fileForm.archivo);
      await subirEvidenciaMedida(selected.id, fd);
      await abrirDetalle(selected);
      await refrescarInteligencia();
      setFileForm({ tipo_evidencia: "EVIDENCIA_DESPUES", descripcion: "", archivo: null });
    } catch (err) {
      console.error(err);
      alert(err?.response?.data?.detail || "No fue posible subir la evidencia.");
    } finally {
      setSaving(false);
    }
  }

  async function marcarAlerta(id) {
    await marcarAlertaMedidaLeida(id);
    await recargarAlertas();
  }

  async function archivarAlerta(id) {
    await archivarAlertaMedida(id);
    await recargarAlertas();
  }

  function exportarExcel() {
    window.open(getMedidasCorrectivasExcelUrl(filters), "_blank", "noopener,noreferrer");
  }

  return (
    <section className="medidas-enterprise-page">
      <div className="mc-hero">
        <div>
          <span></span>
          <h1>Centro de Medidas Correctivas</h1>
          <p>
            Gestión ejecutiva de acciones correctivas, preventivas y de mejora con workflow, eficacia,
            alertas inteligentes, seguimiento, evidencias, costos y trazabilidad.
          </p>
        </div>

        <div className="mc-actions">
          <button className="mc-btn ghost" onClick={exportarExcel}>
            <Download size={17} /> Excel
          </button>
          <button className="mc-btn ghost" onClick={regenerarAlertas} disabled={loading}>
            <AlertTriangle size={17} /> Generar alertas
          </button>
          <button className="mc-btn ghost" onClick={() => cargar()} disabled={loading}>
            <RefreshCcw size={17} /> Actualizar
          </button>
          <button className="mc-btn primary" onClick={() => setModal("crear")}>
            <Plus size={17} /> Nueva medida
          </button>
        </div>
      </div>

      
      {mostrarBI && (
        <MedidasCorrectivasBIDashboard empresaId={filters?.empresa_id || ""} />
      )}

      {error && <div className="mc-error"><AlertTriangle size={18} /> {error}</div>}

      <div className="mc-kpis">
        <article><Target size={22} /><span>Total medidas</span><strong>{kpis.total || 0}</strong></article>
        <article><TrendingUp size={22} /><span>Abiertas</span><strong>{kpis.abiertas || 0}</strong></article>
        <article className="danger"><AlertTriangle size={22} /><span>Vencidas</span><strong>{kpis.vencidas || 0}</strong></article>
        <article><CheckCircle2 size={22} /><span>Cerradas</span><strong>{kpis.cerradas || 0}</strong></article>
        <article className={semaforo.className}><ShieldCheck size={22} /><span>Semáforo</span><strong>{semaforo.label}</strong></article>
        <article><BarChart3 size={22} /><span>Costo real</span><strong>{formatMoney(kpis.costo_real || 0)}</strong></article>
      </div>

      <div className="mc-enterprise-grid">
        <AlertasCard
          data={alertasData}
          loading={loading}
          onRefresh={recargarAlertas}
          onRead={marcarAlerta}
          onArchive={archivarAlerta}
        />

        <section className="mc-enterprise-card">
          <div className="mc-enterprise-card-header">
            <div>
              <span>Recomendaciones ejecutivas</span>
              <h3>Plan de acción inmediato</h3>
            </div>
          </div>
          <div className="mc-recs">
            {recomendaciones.map((rec) => <div key={rec}><AlertTriangle size={17} /> {rec}</div>)}
            {!recomendaciones.length && <div><CheckCircle2 size={17} /> Sin recomendaciones críticas.</div>}
          </div>
        </section>
      </div>

      <EficaciaResumenKpis medidas={medidas} />

      <form className="mc-filters" onSubmit={(e) => { e.preventDefault(); cargar(filters); }}>
        <input placeholder="Empresa ID" value={filters.empresa_id} onChange={(e) => setFilters({ ...filters, empresa_id: e.target.value })} />
        <select value={filters.estado} onChange={(e) => setFilters({ ...filters, estado: e.target.value })}>
          <option value="">Todos los estados</option>
          <option value="ABIERTA">Abierta</option>
          <option value="PLANIFICADA">Planificada</option>
          <option value="EN_EJECUCION">En ejecución</option>
          <option value="VERIFICACION">Verificación</option>
          <option value="PENDIENTE_APROBACION">Pendiente aprobación</option>
          <option value="CERRADA">Cerrada</option>
        </select>
        <select value={filters.prioridad} onChange={(e) => setFilters({ ...filters, prioridad: e.target.value })}>
          <option value="">Todas las prioridades</option>
          <option value="BAJA">Baja</option>
          <option value="MEDIA">Media</option>
          <option value="ALTA">Alta</option>
          <option value="CRITICA">Crítica</option>
        </select>
        <select value={filters.origen} onChange={(e) => setFilters({ ...filters, origen: e.target.value })}>
          <option value="">Todos los orígenes</option>
          <option value="MANUAL">Manual</option>
          <option value="INSPECCION_SST">Inspección SST</option>
          <option value="HALLAZGO_SST">Hallazgo SST</option>
          <option value="INCIDENTE">Incidente</option>
          <option value="AUDITORIA">Auditoría</option>
          <option value="REPORTE_ANONIMO_SST">Reporte Anónimo SST</option>
        </select>
        <input placeholder="Buscar..." value={filters.q} onChange={(e) => setFilters({ ...filters, q: e.target.value })} />
        <button className="mc-btn primary" type="submit">Filtrar</button>
      </form>

      <div className="mc-table-card">
        <table>
          <thead>
            <tr>
              <th>Código</th><th>Medida</th><th>Origen</th><th>Prioridad</th><th>Estado</th>
              <th>Responsable</th><th>Compromiso</th><th>Avance</th><th>Eficacia</th><th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {medidas.map((item) => (
              <tr key={item.id} className={item.vencida ? "row-danger" : ""}>
                <td><strong>{item.codigo}</strong><small>ID #{item.id}</small></td>
                <td><strong>{item.titulo}</strong><small>{item.descripcion}</small></td>
                <td><span className="mc-badge info">{item.origen || "MANUAL"}</span></td>
                <td><span className={`mc-badge ${badgeClass(item.prioridad)}`}>{item.prioridad}</span></td>
                <td><span className={`mc-badge ${badgeClass(item.estado)}`}>{item.estado}</span></td>
                <td>{item.responsable || "Sin responsable"}</td>
                <td>{item.fecha_compromiso || "Sin fecha"}{item.vencida && <small className="danger-text">Vencida</small>}</td>
                <td><div className="mc-progress"><span style={{ width: `${Math.min(Number(item.avance || 0), 100)}%` }} /></div><small>{item.avance || 0}%</small></td>
                <td><EficaciaIndicadorTabla medida={item} /></td>
                <td className="mc-row-actions"><button onClick={() => abrirDetalle(item)}><Eye size={16} /></button></td>
              </tr>
            ))}
            {!medidas.length && <tr><td colSpan="10" className="mc-empty">{loading ? "Cargando..." : "No hay medidas correctivas."}</td></tr>}
          </tbody>
        </table>
      </div>

      {modal === "crear" && (
        <div className="mc-modal-backdrop">
          <div className="mc-modal wide">
            <div className="mc-modal-header"><h2>Nueva Medida Correctiva</h2><button onClick={() => setModal(null)}><X size={18} /></button></div>
            <form onSubmit={guardarMedida} className="mc-form">
              <input placeholder="Empresa ID" value={form.empresa_id} onChange={(e) => updateForm("empresa_id", e.target.value)} />
              <input placeholder="Código" value={form.codigo} onChange={(e) => updateForm("codigo", e.target.value)} />
              <input placeholder="Título" value={form.titulo} onChange={(e) => updateForm("titulo", e.target.value)} />
              <select value={form.tipo_accion} onChange={(e) => updateForm("tipo_accion", e.target.value)}><option value="CORRECTIVA">Correctiva</option><option value="PREVENTIVA">Preventiva</option><option value="MEJORA">Mejora</option></select>
              <select value={form.origen} onChange={(e) => updateForm("origen", e.target.value)}><option value="MANUAL">Manual</option><option value="INSPECCION_SST">Inspección SST</option><option value="HALLAZGO_SST">Hallazgo SST</option><option value="INCIDENTE">Incidente</option><option value="AUDITORIA">Auditoría</option><option value="REPORTE_ANONIMO_SST">Reporte Anónimo SST</option></select>
              <select value={form.prioridad} onChange={(e) => updateForm("prioridad", e.target.value)}><option value="BAJA">Baja</option><option value="MEDIA">Media</option><option value="ALTA">Alta</option><option value="CRITICA">Crítica</option></select>
              <input placeholder="Responsable" value={form.responsable} onChange={(e) => updateForm("responsable", e.target.value)} />
              <input type="date" value={form.fecha_compromiso} onChange={(e) => updateForm("fecha_compromiso", e.target.value)} />
              <textarea className="full" placeholder="Descripción del problema" value={form.descripcion} onChange={(e) => updateForm("descripcion", e.target.value)} />
              <textarea placeholder="Causa raíz" value={form.causa_raiz} onChange={(e) => updateForm("causa_raiz", e.target.value)} />
              <textarea placeholder="Acción inmediata" value={form.accion_inmediata} onChange={(e) => updateForm("accion_inmediata", e.target.value)} />
              <textarea placeholder="Acción correctiva" value={form.accion_correctiva} onChange={(e) => updateForm("accion_correctiva", e.target.value)} />
              <textarea placeholder="Acción preventiva" value={form.accion_preventiva} onChange={(e) => updateForm("accion_preventiva", e.target.value)} />
              <input type="number" placeholder="Costo estimado" value={form.costo_estimado} onChange={(e) => updateForm("costo_estimado", e.target.value)} />
              <input type="number" placeholder="Costo real" value={form.costo_real} onChange={(e) => updateForm("costo_real", e.target.value)} />
              <label className="mc-check"><input type="checkbox" checked={form.requiere_aprobacion} onChange={(e) => updateForm("requiere_aprobacion", e.target.checked)} /> Requiere aprobación</label>
              <button className="mc-btn primary full" disabled={saving}><Save size={17} /> Guardar medida</button>
            </form>
          </div>
        </div>
      )}

      {modal === "detalle" && selected && (
        <div className="mc-modal-backdrop">
          <div className="mc-modal detail enterprise-detail">
            <div className="mc-modal-header">
              <div>
                <h2>{selected.codigo}</h2>
                <p>{selected.titulo}</p>
              </div>

              {/* ============================================================
                  FASE 1.1.8.7.6.1 — Exportaciones Enterprise dentro del modal
                  Exporta la medida correctiva abierta en PDF y Excel.
              ============================================================ */}
              <div className="mc-modal-header-actions">
                <ExportacionesMedidaEnterprise medida={selected} />
                <button onClick={() => setModal(null)} title="Cerrar">
                  <X size={18} />
                </button>
              </div>
            </div>
            <div className="mc-detail-enterprise-grid">
              <WorkflowTimeline workflow={workflow} loading={saving} onRefresh={refrescarWorkflow} onAdvance={avanzarWorkflow} />
              <EficaciaCard medida={selected} loading={saving} onSubmit={guardarEficacia} />
              <SemaforoEjecutivoPanel data={inteligencia} />
              <EvidenciasInteligentesPanel data={inteligencia} loading={saving} onRefresh={refrescarInteligencia} />
              <TrazabilidadVisualPanel data={inteligencia} />
              <section className="mc-enterprise-card mc-detail-main">
                <div className="mc-enterprise-card-header"><div><span>Detalle técnico</span><h3>Resumen y causa raíz</h3></div></div>
                <p>{selected.descripcion}</p>
                <p><strong>Causa raíz:</strong> {selected.causa_raiz || "Sin registrar"}</p>
                <p><strong>Acción correctiva:</strong> {selected.accion_correctiva || "Sin registrar"}</p>
                <p><strong>Trazabilidad:</strong></p>
                <pre>{selected.trazabilidad || "Sin trazabilidad"}</pre>
              </section>
              <section className="mc-enterprise-card">
                <div className="mc-enterprise-card-header"><div><span>Seguimientos</span><h3>{seguimientos.length} registro(s)</h3></div></div>
                <form onSubmit={guardarSeguimiento} className="mc-mini-form">
                  <input type="number" placeholder="Avance %" value={seguimientoForm.avance} onChange={(e) => setSeguimientoForm({ ...seguimientoForm, avance: e.target.value })} />
                  <input placeholder="Responsable" value={seguimientoForm.responsable} onChange={(e) => setSeguimientoForm({ ...seguimientoForm, responsable: e.target.value })} />
                  <input placeholder="Resultado" value={seguimientoForm.resultado} onChange={(e) => setSeguimientoForm({ ...seguimientoForm, resultado: e.target.value })} />
                  <textarea placeholder="Comentario" value={seguimientoForm.comentario} onChange={(e) => setSeguimientoForm({ ...seguimientoForm, comentario: e.target.value })} />
                  <button className="mc-btn primary" disabled={saving}>Agregar seguimiento</button>
                </form>
                <div className="mc-list">{seguimientos.map((s) => <div key={s.id}><strong>{s.avance}%</strong> — {s.comentario || s.resultado || "Seguimiento"}</div>)}</div>
              </section>
              <section className="mc-enterprise-card">
                <div className="mc-enterprise-card-header"><div><span>Evidencias</span><h3>{evidencias.length} archivo(s)</h3></div></div>
                <form onSubmit={guardarEvidencia} className="mc-mini-form">
                  <select value={fileForm.tipo_evidencia} onChange={(e) => setFileForm({ ...fileForm, tipo_evidencia: e.target.value })}><option value="EVIDENCIA_ANTES">Antes</option><option value="EVIDENCIA_DURANTE">Durante</option><option value="EVIDENCIA_DESPUES">Después</option><option value="SOPORTE_DOCUMENTAL">Soporte documental</option></select>
                  <input placeholder="Descripción" value={fileForm.descripcion} onChange={(e) => setFileForm({ ...fileForm, descripcion: e.target.value })} />
                  <input type="file" onChange={(e) => setFileForm({ ...fileForm, archivo: e.target.files?.[0] || null })} />
                  <button className="mc-btn primary" disabled={saving}><FileUp size={16} /> Subir evidencia</button>
                </form>
                <div className="mc-evidencias">{evidencias.map((e) => <a key={e.id} href={e.url} target="_blank" rel="noreferrer">{e.nombre_original}</a>)}</div>
              </section>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
