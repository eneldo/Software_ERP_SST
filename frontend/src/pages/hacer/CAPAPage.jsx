// ============================================================
// CAPA SST ENTERPRISE - ERP SST PRO
// FASE 1.1.8.7 — Centro de Acciones Correctivas, Preventivas y de Mejora
// Archivo: frontend/src/pages/hacer/CAPAPage.jsx
// ============================================================

import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  ClipboardCheck,
  Download,
  Eye,
  FileText,
  Filter,
  Image as ImageIcon,
  Plus,
  RefreshCcw,
  Save,
  Search,
  ShieldCheck,
  Target,
  Trash2,
  UploadCloud,
  X,
} from "lucide-react";
import capaApi, { urlArchivoCAPA } from "../../api/capaApi";
import { listarEmpresasSST } from "../../api/empresaSstApi";
import "../../styles/capa.css";

const initialForm = {
  empresa_id: "",
  sede_id: null,
  area_id: null,
  cargo_id: null,
  empleado_id: null,
  inspeccion_id: null,
  hallazgo_id: null,
  codigo: "",
  titulo: "",
  descripcion: "",
  tipo_accion: "CORRECTIVA",
  origen: "INSPECCION_SST",
  prioridad: "MEDIA",
  estado: "ABIERTA",
  responsable: "",
  fecha_apertura: new Date().toISOString().slice(0, 10),
  fecha_compromiso: "",
  avance: 0,
  causa_raiz: "",
  porque_1: "",
  porque_2: "",
  porque_3: "",
  porque_4: "",
  porque_5: "",
  ishikawa_metodo: "",
  ishikawa_mano_obra: "",
  ishikawa_maquinaria: "",
  ishikawa_materiales: "",
  ishikawa_medio_ambiente: "",
  ishikawa_medicion: "",
  accion_inmediata: "",
  accion_correctiva: "",
  accion_preventiva: "",
  verificacion_eficacia: "",
  observaciones: "",
  activo: true,
};

const initialSeguimiento = {
  fecha_seguimiento: new Date().toISOString().slice(0, 10),
  responsable: "",
  avance: 0,
  resultado: "EN_SEGUIMIENTO",
  comentario: "",
  proximo_seguimiento: "",
};

const estadoClass = (estado = "") => estado.toLowerCase().replaceAll("_", "-");
const prioridadClass = (prioridad = "") => prioridad.toLowerCase();

function BarList({ data = [] }) {
  const max = Math.max(...data.map((d) => Number(d.value || 0)), 1);
  if (!data.length) return <small>Sin información registrada.</small>;
  return (
    <div className="capa-bar-list">
      {data.map((item) => (
        <div className="capa-bar-row" key={item.name}>
          <div className="capa-bar-meta">
            <span>{item.name}</span>
            <b>{item.value}</b>
          </div>
          <div className="capa-bar-track"><i style={{ width: `${(Number(item.value || 0) / max) * 100}%` }} /></div>
        </div>
      ))}
    </div>
  );
}

export default function CAPAPage() {
  const [items, setItems] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [empresas, setEmpresas] = useState([]);
  const [filtros, setFiltros] = useState({ empresa_id: "", estado: "", prioridad: "", tipo_accion: "", origen: "", q: "" });
  const [modal, setModal] = useState(false);
  const [editando, setEditando] = useState(null);
  const [form, setForm] = useState(initialForm);
  const [seguimientos, setSeguimientos] = useState([]);
  const [evidencias, setEvidencias] = useState([]);
  const [seguimientoForm, setSeguimientoForm] = useState(initialSeguimiento);
  const [archivo, setArchivo] = useState(null);
  const [descripcionArchivo, setDescripcionArchivo] = useState("Evidencia CAPA");
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);

  const cargarDatos = useCallback(async () => {
    setLoading(true);
    try {
      const [lista, dash, emps] = await Promise.all([
        capaApi.listar(filtros),
        capaApi.dashboard(filtros),
        listarEmpresasSST().catch(() => []),
      ]);
      setItems(lista);
      setDashboard(dash);
      setEmpresas(emps || []);
    } catch (error) {
      console.error(error);
      alert(error?.response?.data?.detail || "No se pudo cargar CAPA SST");
    } finally {
      setLoading(false);
    }
  }, [filtros]);

  useEffect(() => { cargarDatos(); }, [cargarDatos]);

  const kpis = dashboard?.kpis || {};
  const charts = dashboard?.charts || {};
  const alertas = dashboard?.alertas || {};
  const recomendaciones = dashboard?.recomendaciones || [];

  const semaforoClass = useMemo(() => {
    const s = String(kpis.semaforo || "VERDE").toLowerCase();
    return `capa-semaforo-${s}`;
  }, [kpis.semaforo]);

  const limpiar = () => {
    setEditando(null);
    setForm({ ...initialForm, codigo: `CAPA-${String(Date.now()).slice(-5)}` });
    setSeguimientos([]);
    setEvidencias([]);
    setSeguimientoForm(initialSeguimiento);
    setArchivo(null);
    setDescripcionArchivo("Evidencia CAPA");
  };

  const abrirNuevo = () => {
    limpiar();
    setModal(true);
  };

  const abrirEditar = async (item) => {
    setEditando(item);
    setForm({ ...initialForm, ...item, empresa_id: item.empresa_id || "", fecha_apertura: item.fecha_apertura || "", fecha_compromiso: item.fecha_compromiso || "" });
    setModal(true);
    try {
      const [seg, ev] = await Promise.all([capaApi.listarSeguimientos(item.id), capaApi.listarEvidencias(item.id)]);
      setSeguimientos(seg);
      setEvidencias(ev);
    } catch (error) {
      console.error(error);
    }
  };

  const guardar = async () => {
    try {
      const payload = { ...form, empresa_id: Number(form.empresa_id), avance: Number(form.avance || 0) };
      if (!payload.empresa_id) return alert("Selecciona una empresa");
      if (editando) await capaApi.actualizar(editando.id, payload);
      else await capaApi.crear(payload);
      setModal(false);
      cargarDatos();
    } catch (error) {
      console.error(error);
      alert(error?.response?.data?.detail || "No se pudo guardar CAPA");
    }
  };

  const eliminar = async (item) => {
    if (!window.confirm(`¿Anular CAPA ${item.codigo}?`)) return;
    await capaApi.eliminar(item.id);
    cargarDatos();
  };

  const agregarSeguimiento = async () => {
    if (!editando?.id) return alert("Primero guarda la CAPA para registrar seguimientos");
    if (!seguimientoForm.comentario.trim()) return alert("Escribe el comentario del seguimiento");
    try {
      await capaApi.crearSeguimiento(editando.id, {
        ...seguimientoForm,
        capa_id: editando.id,
        empresa_id: editando.empresa_id,
        avance: Number(seguimientoForm.avance || 0),
      });
      const [seg, capaActualizada] = await Promise.all([capaApi.listarSeguimientos(editando.id), capaApi.obtener(editando.id)]);
      setSeguimientos(seg);
      setEditando(capaActualizada);
      setForm({ ...form, avance: capaActualizada.avance, estado: capaActualizada.estado, trazabilidad: capaActualizada.trazabilidad });
      setSeguimientoForm(initialSeguimiento);
      cargarDatos();
    } catch (error) {
      alert(error?.response?.data?.detail || "No se pudo registrar seguimiento");
    }
  };

  const subirEvidencia = async () => {
    if (!editando?.id) return alert("Primero guarda la CAPA para subir evidencias");
    if (!archivo) return alert("Selecciona un archivo");
    const fd = new FormData();
    fd.append("tipo_evidencia", "EVIDENCIA_CAPA");
    fd.append("descripcion", descripcionArchivo || "Evidencia CAPA");
    fd.append("archivo", archivo);
    try {
      await capaApi.subirEvidencia(editando.id, fd);
      setEvidencias(await capaApi.listarEvidencias(editando.id));
      setArchivo(null);
      cargarDatos();
    } catch (error) {
      alert(error?.response?.data?.detail || "No se pudo subir evidencia CAPA");
    }
  };

  const cerrarCapa = async () => {
    if (!editando?.id) return;
    const verificacion = window.prompt("Verificación de eficacia para cierre CAPA:", form.verificacion_eficacia || "Acción ejecutada, verificada y efectiva.");
    if (!verificacion) return;
    try {
      const cerrada = await capaApi.cerrar(editando.id, { efectiva: true, verificacion_eficacia: verificacion, observacion: "Cierre digital CAPA desde frontend." });
      setEditando(cerrada);
      setForm({ ...form, ...cerrada });
      cargarDatos();
      alert("CAPA cerrada correctamente");
    } catch (error) {
      alert(error?.response?.data?.detail || "No se pudo cerrar CAPA");
    }
  };

  return (
    <main className="capa-page">
      <section className="capa-hero">
        <div>
          <span><ShieldCheck size={15} /> CAPA ENTERPRISE</span>
          <h1>Centro CAPA SST Enterprise</h1>
          <p>Acciones correctivas, preventivas y de mejora con análisis causa raíz, seguimiento, evidencias y trazabilidad.</p>
        </div>
        <div className="capa-hero-actions">
          <button className="capa-btn-light" onClick={cargarDatos}><RefreshCcw size={16} /> Actualizar</button>
          <button className="capa-btn-light" onClick={() => capaApi.excel(filtros)}><Download size={16} /> Excel</button>
          <button className="capa-btn-light" onClick={() => capaApi.pdf(filtros)}><FileText size={16} /> PDF</button>
          <button className="capa-btn-light" onClick={() => capaApi.dashboardPdf(filtros)}><BarChart3 size={16} /> Dashboard PDF</button>
          <button className="capa-btn-primary" onClick={abrirNuevo}><Plus size={16} /> Nueva CAPA</button>
        </div>
      </section>

      <section className="capa-main-grid">
        <div className="capa-content">
          <div className="capa-kpis-grid">
            <article><ClipboardCheck /><small>Total CAPA</small><strong>{kpis.total || 0}</strong></article>
            <article><AlertTriangle /><small>Abiertas</small><strong>{kpis.abiertas || 0}</strong></article>
            <article><Target /><small>En ejecución</small><strong>{kpis.en_ejecucion || 0}</strong></article>
            <article><CheckCircle2 /><small>Cerradas</small><strong>{kpis.cerradas || 0}</strong></article>
            <article><AlertTriangle /><small>Vencidas</small><strong>{kpis.vencidas || 0}</strong></article>
          </div>

          <div className="capa-indicators-grid">
            <article><small>Cumplimiento</small><strong>{kpis.cumplimiento || 0}%</strong><div><span style={{ width: `${kpis.cumplimiento || 0}%` }} /></div></article>
            <article><small>Avance promedio</small><strong>{kpis.avance_promedio || 0}%</strong><div><span style={{ width: `${kpis.avance_promedio || 0}%` }} /></div></article>
            <article><small>Críticas</small><strong>{kpis.criticas || 0}</strong><div><span style={{ width: `${Math.min((kpis.criticas || 0) * 20, 100)}%` }} /></div></article>
            <article><small>Score riesgo</small><strong>{kpis.riesgo_score || 0}</strong><div><span style={{ width: `${Math.min(kpis.riesgo_score || 0, 100)}%` }} /></div></article>
          </div>

          <div className="capa-charts-grid">
            <article><h3>Por tipo</h3><BarList data={charts.por_tipo} /></article>
            <article><h3>Por estado</h3><BarList data={charts.por_estado} /></article>
            <article><h3>Por prioridad</h3><BarList data={charts.por_prioridad} /></article>
            <article><h3>Por origen</h3><BarList data={charts.por_origen} /></article>
            <article><h3>Por área</h3><BarList data={charts.por_area} /></article>
          </div>

          <article className={`capa-semaforo-card ${semaforoClass}`}>
            <div><span>Semáforo CAPA SST</span><h3>{kpis.semaforo || "VERDE"}</h3><p>Cumplimiento: {kpis.cumplimiento || 0}% · Vencidas: {kpis.vencidas || 0}</p></div>
            <strong>{kpis.riesgo_score || 0}</strong>
          </article>

          <section className="capa-table-card">
            <div className="capa-filter-top">
              <label className="capa-search"><Search size={16} /><input placeholder="Buscar por código, título, responsable o descripción..." value={filtros.q} onChange={(e) => setFiltros({ ...filtros, q: e.target.value })} /></label>
              <button className="capa-btn-light" onClick={() => setFiltros({ empresa_id: "", estado: "", prioridad: "", tipo_accion: "", origen: "", q: "" })}><Filter size={15} /> Limpiar</button>
              <button className="capa-btn-light" onClick={cargarDatos}><RefreshCcw size={15} /> Actualizar</button>
            </div>
            <div className="capa-filters-grid">
              <select value={filtros.empresa_id} onChange={(e) => setFiltros({ ...filtros, empresa_id: e.target.value })}><option value="">Todas las empresas</option>{empresas.map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}</select>
              <select value={filtros.estado} onChange={(e) => setFiltros({ ...filtros, estado: e.target.value })}><option value="">Todos los estados</option>{["ABIERTA", "EN_ANALISIS", "PLANIFICADA", "EN_EJECUCION", "VERIFICACION", "CERRADA"].map((x) => <option key={x}>{x}</option>)}</select>
              <select value={filtros.prioridad} onChange={(e) => setFiltros({ ...filtros, prioridad: e.target.value })}><option value="">Todas las prioridades</option>{["BAJA", "MEDIA", "ALTA", "CRITICA"].map((x) => <option key={x}>{x}</option>)}</select>
              <select value={filtros.tipo_accion} onChange={(e) => setFiltros({ ...filtros, tipo_accion: e.target.value })}><option value="">Todos los tipos</option>{["CORRECTIVA", "PREVENTIVA", "MEJORA"].map((x) => <option key={x}>{x}</option>)}</select>
              <select value={filtros.origen} onChange={(e) => setFiltros({ ...filtros, origen: e.target.value })}><option value="">Todos los orígenes</option>{["INSPECCION_SST", "HALLAZGO_SST", "ACCIDENTE", "INCIDENTE", "AUDITORIA", "MATRIZ_LEGAL", "OBSERVACION_SST", "OTRO"].map((x) => <option key={x}>{x}</option>)}</select>
            </div>
            <div className="capa-table-wrap">
              <table>
                <thead><tr><th>Código</th><th>CAPA</th><th>Empresa</th><th>Tipo</th><th>Prioridad</th><th>Estado</th><th>Avance</th><th>Compromiso</th><th>Acciones</th></tr></thead>
                <tbody>
                  {items.length ? items.map((item) => (
                    <tr key={item.id}>
                      <td><b>{item.codigo}</b></td>
                      <td>{item.titulo}<small>{item.origen}</small></td>
                      <td>{item.empresa_nombre || "-"}</td>
                      <td>{item.tipo_accion}</td>
                      <td><span className={`capa-priority ${prioridadClass(item.prioridad)}`}>{item.prioridad}</span></td>
                      <td><span className={`capa-status ${estadoClass(item.estado)}`}>{item.estado}</span></td>
                      <td><div className="capa-mini-progress"><i style={{ width: `${Number(item.avance || 0)}%` }} /></div><small>{Number(item.avance || 0)}%</small></td>
                      <td>{item.fecha_compromiso || "-"}{item.vencida && <small className="danger">Vencida</small>}</td>
                      <td className="capa-actions"><button onClick={() => abrirEditar(item)} title="Ver / Editar"><Eye size={15} /></button><button onClick={() => capaApi.actaPdf(item.id)} title="Acta PDF"><FileText size={15} /></button><button onClick={() => eliminar(item)} title="Anular"><Trash2 size={15} /></button></td>
                    </tr>
                  )) : <tr><td colSpan="9" className="capa-empty">{loading ? "Cargando..." : "No hay CAPA registradas."}</td></tr>}
                </tbody>
              </table>
            </div>
          </section>
        </div>

        <aside className="capa-right-panel">
          <article><h3>Dashboard inteligente</h3><div className="capa-ring" style={{ "--capa-ring": `${Math.min(kpis.cumplimiento || 0, 100)}%` }}><strong>{kpis.cumplimiento || 0}%</strong><span>Cumplimiento</span></div><p>{kpis.semaforo || "VERDE"}: seguimiento de acciones correctivas, preventivas y de mejora.</p></article>
          <article><h3>Alertas CAPA</h3><p>Vencidas <strong>{alertas.vencidas || 0}</strong></p><p>Críticas <strong>{alertas.criticas || 0}</strong></p><p>Abiertas <strong>{alertas.abiertas || 0}</strong></p></article>
          <article><h3>Recomendaciones PRO</h3><ul>{recomendaciones.map((r, i) => <li key={i}>{r}</li>)}</ul></article>
        </aside>
      </section>

      {modal && (
        <div className="capa-modal-backdrop">
          <section className="capa-form-modal">
            <header className="capa-modal-header"><div><span>{editando ? "Editar CAPA" : "Nueva CAPA"}</span><h2>{form.titulo || "Centro CAPA SST"}</h2><p>Gestión ISO 45001 con trazabilidad, evidencias y cierre controlado.</p></div><button className="capa-close" onClick={() => setModal(false)}><X /></button></header>
            <div className="capa-modal-body">
              <div className="capa-form-grid">
                <label>Empresa<select value={form.empresa_id || ""} onChange={(e) => setForm({ ...form, empresa_id: e.target.value })}><option value="">Seleccionar</option>{empresas.map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}</select></label>
                <label>Código<input value={form.codigo || ""} onChange={(e) => setForm({ ...form, codigo: e.target.value })} /></label>
                <label className="capa-full">Título<input value={form.titulo || ""} onChange={(e) => setForm({ ...form, titulo: e.target.value })} /></label>
                <label className="capa-full">Descripción<textarea value={form.descripcion || ""} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} /></label>
                <label>Tipo<select value={form.tipo_accion} onChange={(e) => setForm({ ...form, tipo_accion: e.target.value })}>{["CORRECTIVA", "PREVENTIVA", "MEJORA"].map((x) => <option key={x}>{x}</option>)}</select></label>
                <label>Origen<select value={form.origen} onChange={(e) => setForm({ ...form, origen: e.target.value })}>{["INSPECCION_SST", "HALLAZGO_SST", "ACCIDENTE", "INCIDENTE", "AUDITORIA", "MATRIZ_LEGAL", "OBSERVACION_SST", "OTRO"].map((x) => <option key={x}>{x}</option>)}</select></label>
                <label>Prioridad<select value={form.prioridad} onChange={(e) => setForm({ ...form, prioridad: e.target.value })}>{["BAJA", "MEDIA", "ALTA", "CRITICA"].map((x) => <option key={x}>{x}</option>)}</select></label>
                <label>Estado<select value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })}>{["ABIERTA", "EN_ANALISIS", "PLANIFICADA", "EN_EJECUCION", "VERIFICACION", "CERRADA"].map((x) => <option key={x}>{x}</option>)}</select></label>
                <label>Responsable<input value={form.responsable || ""} onChange={(e) => setForm({ ...form, responsable: e.target.value })} /></label>
                <label>Fecha compromiso<input type="date" value={form.fecha_compromiso || ""} onChange={(e) => setForm({ ...form, fecha_compromiso: e.target.value })} /></label>
                <label>Avance %<input type="number" min="0" max="100" value={form.avance || 0} onChange={(e) => setForm({ ...form, avance: e.target.value })} /></label>
                <label>Causa raíz<input value={form.causa_raiz || ""} onChange={(e) => setForm({ ...form, causa_raiz: e.target.value })} /></label>
                <label>¿Por qué 1?<input value={form.porque_1 || ""} onChange={(e) => setForm({ ...form, porque_1: e.target.value })} /></label>
                <label>¿Por qué 2?<input value={form.porque_2 || ""} onChange={(e) => setForm({ ...form, porque_2: e.target.value })} /></label>
                <label>¿Por qué 3?<input value={form.porque_3 || ""} onChange={(e) => setForm({ ...form, porque_3: e.target.value })} /></label>
                <label>¿Por qué 4?<input value={form.porque_4 || ""} onChange={(e) => setForm({ ...form, porque_4: e.target.value })} /></label>
                <label>¿Por qué 5?<input value={form.porque_5 || ""} onChange={(e) => setForm({ ...form, porque_5: e.target.value })} /></label>
                <label className="capa-full">Acción correctiva<textarea value={form.accion_correctiva || ""} onChange={(e) => setForm({ ...form, accion_correctiva: e.target.value })} /></label>
                <label className="capa-full">Acción preventiva / mejora<textarea value={form.accion_preventiva || ""} onChange={(e) => setForm({ ...form, accion_preventiva: e.target.value })} /></label>
              </div>

              {editando && (
                <>
                  <section className="capa-subpanel">
                    <h3><Target size={18} /> Seguimientos</h3>
                    <div className="capa-seguimiento-form">
                      <input type="date" value={seguimientoForm.fecha_seguimiento} onChange={(e) => setSeguimientoForm({ ...seguimientoForm, fecha_seguimiento: e.target.value })} />
                      <input placeholder="Responsable" value={seguimientoForm.responsable} onChange={(e) => setSeguimientoForm({ ...seguimientoForm, responsable: e.target.value })} />
                      <input type="number" min="0" max="100" placeholder="Avance" value={seguimientoForm.avance} onChange={(e) => setSeguimientoForm({ ...seguimientoForm, avance: e.target.value })} />
                      <input placeholder="Comentario" value={seguimientoForm.comentario} onChange={(e) => setSeguimientoForm({ ...seguimientoForm, comentario: e.target.value })} />
                      <button className="capa-btn-primary" onClick={agregarSeguimiento}><Plus size={15} /> Agregar</button>
                    </div>
                    <div className="capa-timeline">
                      {seguimientos.length ? seguimientos.map((s) => <div key={s.id}><i /><b>{s.fecha_seguimiento} · {s.avance}%</b><small>{s.responsable || "Sin responsable"} · {s.resultado}</small><span>{s.comentario}</span></div>) : <p>Sin seguimientos registrados.</p>}
                    </div>
                  </section>

                  <section className="capa-subpanel">
                    <h3><UploadCloud size={18} /> Evidencias CAPA</h3>
                    <div className="capa-upload-row">
                      <input value={descripcionArchivo} onChange={(e) => setDescripcionArchivo(e.target.value)} />
                      <label className="capa-file-pill"><UploadCloud size={16} /> Archivo<input type="file" onChange={(e) => setArchivo(e.target.files?.[0] || null)} /></label>
                      <button className="capa-btn-primary" onClick={subirEvidencia}>Subir</button>
                    </div>
                    {archivo && <small>Seleccionado: {archivo.name}</small>}
                    <div className="capa-file-list">
                      {evidencias.map((a) => <div className="capa-file-row" key={a.id}><span><ImageIcon size={18} /></span><div><b>{a.nombre_original}</b><small>{a.descripcion}</small></div><button onClick={() => setPreview(a)}><Eye size={15} /></button><a href={urlArchivoCAPA(a.url)} download><Download size={15} /></a></div>)}
                    </div>
                  </section>

                  <section className="capa-subpanel dark"><h3>Trazabilidad</h3><pre>{form.trazabilidad || "Sin trazabilidad"}</pre></section>
                </>
              )}
            </div>
            <footer className="capa-modal-footer">
              <button className="capa-btn-light" onClick={() => setModal(false)}>Cerrar</button>
              {editando && form.estado !== "CERRADA" && <button className="capa-btn-light" onClick={cerrarCapa}><ShieldCheck size={16} /> Cerrar CAPA</button>}
              <button className="capa-btn-primary" onClick={guardar} disabled={form.estado === "CERRADA"}><Save size={16} /> Guardar CAPA</button>
            </footer>
          </section>
        </div>
      )}

      {preview && (
        <div className="capa-preview-backdrop">
          <section className="capa-preview-modal">
            <header><b>{preview.nombre_original}</b><button onClick={() => setPreview(null)}><X size={18} /></button></header>
            {preview.mime_type?.includes("image") ? <img src={urlArchivoCAPA(preview.url)} alt={preview.nombre_original} /> : <iframe src={urlArchivoCAPA(preview.url)} title="preview" />}
          </section>
        </div>
      )}
    </main>
  );
}
