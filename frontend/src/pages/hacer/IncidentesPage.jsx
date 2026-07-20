// ============================================================
// INCIDENTES Y ACCIDENTES SST ENTERPRISE
// FASE 1.1.8.8.5 — DASHBOARD Y EXPORTACIONES
// Archivo: frontend/src/pages/hacer/IncidentesPage.jsx
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Calendar,
  CheckCircle2,
  Download,
  Edit3,
  Eye,
  FileText,
  FileWarning,
  Filter,
  Image as ImageIcon,
  Paperclip,
  Plus,
  RefreshCw,
  Search,
  ShieldAlert,
  Target,
  Trash2,
  UploadCloud,
  UserRound,
  Users,
  X,
} from "lucide-react";

import {
  actualizarIncidenteSST,
  actualizarInvestigacionIncidenteSST,
  cerrarInvestigacionIncidenteSST,
  crearIncidenteSST,
  dashboardIncidentesSST,
  eliminarEvidenciaIncidenteSST,
  eliminarIncidenteSST,
  generarCapaDesdeIncidenteSST,
  listarEvidenciasIncidenteSST,
  listarIncidentesSST,
  listarLesionadosIncidenteSST,
  listarTestigosIncidenteSST,
  crearLesionadoIncidenteSST,
  crearTestigoIncidenteSST,
  eliminarLesionadoIncidenteSST,
  eliminarTestigoIncidenteSST,
  exportarActaInvestigacionPdf,
  exportarDashboardEjecutivoIncidentesPdf,
  exportarIncidentePdfIndividual,
  exportarIncidentesExcelGeneral,
  exportarIncidentesPdfGeneral,
  exportarInformeAccidentePdf,
  exportarInformeIncidentePdf,
  subirEvidenciaIncidenteSST,
  urlArchivoIncidenteSST,
} from "../../api/incidenteApi";
import { listarEmpresasSST } from "../../api/empresaSstApi";
import { listarSedesSST } from "../../api/sedeSstApi";
import { listarAreasSST } from "../../api/areaSstApi";
import { listarCargosSST } from "../../api/cargoSstApi";
import { listarEmpleados } from "../../api/empleadoSstApi";
import "../../styles/incidentes.css";

const hoyISO = () => new Date().toISOString().slice(0, 10);

const inicialForm = {
  empresa_id: "",
  sede_id: "",
  area_id: "",
  cargo_id: "",
  empleado_id: "",
  codigo: "",
  tipo_evento: "INCIDENTE",
  clasificacion: "INCIDENTE",
  titulo: "",
  descripcion: "",
  lugar: "",
  fecha_evento: hoyISO(),
  hora_evento: "",
  fecha_reporte: hoyISO(),
  estado: "REPORTADO",
  severidad: "BAJA",
  consecuencia: "SIN_LESION",
  dias_incapacidad: 0,
  requiere_investigacion: true,
  requiere_capa: false,
  acto_inseguro: "",
  condicion_insegura: "",
  causa_inmediata: "",
  causa_basica: "",
  causa_raiz: "",
  accion_inmediata: "",

  // FASE 1.1.8.8.3 — Investigación y Árbol de Causas
  equipo_investigador: "",
  investigador_lider: "",
  fecha_investigacion: hoyISO(),
  metodologia_investigacion: "5_PORQUES",
  estado_investigacion: "PENDIENTE",
  descripcion_hechos: "",
  agente_material: "",
  mecanismo_evento: "",
  tipo_contacto: "",
  porque_1: "",
  porque_2: "",
  porque_3: "",
  porque_4: "",
  porque_5: "",
  factores_personales: "",
  factores_trabajo: "",
  factores_organizacionales: "",
  causas_directas: "",
  causas_indirectas: "",
  arbol_causas: "",
  controles_existentes: "",
  controles_recomendados: "",
  plan_investigacion: "",
  conclusion_investigacion: "",
  recomendaciones_investigacion: "",
  investigacion_cerrada: false,
  observaciones: "",
  activo: true,
};

const filtroInicial = {
  empresa_id: "TODOS",
  sede_id: "TODOS",
  area_id: "TODOS",
  tipo_evento: "TODOS",
  clasificacion: "TODOS",
  estado: "TODOS",
  severidad: "TODOS",
  q: "",
};

const inicialLesionado = {
  nombre: "",
  documento: "",
  cargo: "",
  parte_cuerpo_afectada: "",
  tipo_lesion: "",
  gravedad: "LEVE",
  dias_incapacidad: 0,
  atencion_medica: false,
  descripcion_lesion: "",
};

const inicialTestigo = {
  nombre: "",
  documento: "",
  cargo: "",
  telefono: "",
  correo: "",
  declaracion: "",
};

const getErrorMessage = (error) => {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((e) => `${e.loc?.join(".")}: ${e.msg}`).join("\n");
  if (typeof detail === "object" && detail) return JSON.stringify(detail, null, 2);
  if (detail) return String(detail);
  return error?.message || "Error procesando la solicitud";
};

const limpiarPayload = (form) => {
  const toNum = (v) => (v === "" || v === null || v === undefined ? null : Number(v));
  return {
    ...form,
    empresa_id: Number(form.empresa_id),
    sede_id: toNum(form.sede_id),
    area_id: toNum(form.area_id),
    cargo_id: toNum(form.cargo_id),
    empleado_id: toNum(form.empleado_id),
    dias_incapacidad: Number(form.dias_incapacidad || 0),
    capa_id: null,
    requiere_investigacion: Boolean(form.requiere_investigacion),
    requiere_capa: Boolean(form.requiere_capa),
    activo: true,
  };
};

function KPI({ icon: Icon, label, value, tone = "blue" }) {
  return (
    <article className={`inc-kpi inc-tone-${tone}`}>
      <span><Icon size={18} /></span>
      <div><small>{label}</small><strong>{value ?? 0}</strong></div>
    </article>
  );
}

function Bars({ title, icon: Icon, data = [] }) {
  const max = Math.max(...data.map((d) => Number(d.value || 0)), 1);
  return (
    <article className="inc-chart-card">
      <h3><Icon size={15} /> {title}</h3>
      {!data.length ? <small>Sin información registrada.</small> : (
        <div className="inc-bar-list">
          {data.map((item) => (
            <div className="inc-bar-row" key={item.name}>
              <div className="inc-bar-meta"><span>{item.name}</span><b>{item.value}</b></div>
              <div className="inc-bar-track"><i style={{ width: `${(Number(item.value || 0) / max) * 100}%` }} /></div>
            </div>
          ))}
        </div>
      )}
    </article>
  );
}

export default function IncidentesPage({ tipoInicial = "TODOS" }) {
  const [items, setItems] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [areas, setAreas] = useState([]);
  const [cargos, setCargos] = useState([]);
  const [empleados, setEmpleados] = useState([]);
  const [filtros, setFiltros] = useState(() => ({ ...filtroInicial, tipo_evento: tipoInicial }));
  const [loading, setLoading] = useState(false);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState(inicialForm);
  const [viewMode, setViewMode] = useState(false);
  const [pagina, setPagina] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const [lesionados, setLesionados] = useState([]);
  const [testigos, setTestigos] = useState([]);
  const [evidencias, setEvidencias] = useState([]);
  const [lesionadoForm, setLesionadoForm] = useState(inicialLesionado);
  const [testigoForm, setTestigoForm] = useState(inicialTestigo);
  const [evidenciaTipo, setEvidenciaTipo] = useState("EVIDENCIA_EVENTO");
  const [evidenciaDescripcion, setEvidenciaDescripcion] = useState("Evidencia incidente/accidente SST");
  const [evidenciaArchivo, setEvidenciaArchivo] = useState(null);
  const [preview, setPreview] = useState(null);

  const cargarCatalogos = async () => {
    try {
      const [emp, sed, are, car, empl] = await Promise.allSettled([
        listarEmpresasSST(), listarSedesSST(), listarAreasSST(), listarCargosSST(), listarEmpleados(),
      ]);
      if (emp.status === "fulfilled") setEmpresas(emp.value || []);
      if (sed.status === "fulfilled") setSedes(sed.value || []);
      if (are.status === "fulfilled") setAreas(are.value || []);
      if (car.status === "fulfilled") setCargos(car.value || []);
      if (empl.status === "fulfilled") setEmpleados(empl.value || []);
    } catch (error) { console.error(error); }
  };

  const cargar = async (filtrosAplicados = filtros) => {
    setLoading(true);
    try {
      const params = { ...filtrosAplicados };
      const [lista, dash] = await Promise.all([listarIncidentesSST(params), dashboardIncidentesSST(params)]);
      setItems(lista || []);
      setDashboard(dash || null);
      setPagina(1);
    } catch (error) { alert(getErrorMessage(error)); }
    finally { setLoading(false); }
  };

  const cargarDetalle = async (incidenteId) => {
    if (!incidenteId) {
      setLesionados([]); setTestigos([]); setEvidencias([]);
      return;
    }
    try {
      const [les, tes, evi] = await Promise.all([
        listarLesionadosIncidenteSST(incidenteId),
        listarTestigosIncidenteSST(incidenteId),
        listarEvidenciasIncidenteSST(incidenteId),
      ]);
      setLesionados(les || []);
      setTestigos(tes || []);
      setEvidencias(evi || []);
    } catch (error) { alert(getErrorMessage(error)); }
  };

  useEffect(() => { cargarCatalogos(); cargar(); }, []);

  const kpis = dashboard?.kpis || {};
  const charts = dashboard?.charts || {};
  const alertas = dashboard?.alertas || {};
  const recomendaciones = dashboard?.recomendaciones || [];

  const filtrados = useMemo(() => items, [items]);
  const totalPaginas = Math.max(Math.ceil(filtrados.length / pageSize), 1);
  const paginaItems = filtrados.slice((pagina - 1) * pageSize, pagina * pageSize);

  const abrirNuevo = () => {
    setViewMode(false);
    setForm({ ...inicialForm, codigo: `EVT-SST-${String((items?.length || 0) + 1).padStart(3, "0")}` });
    setLesionados([]); setTestigos([]); setEvidencias([]);
    setModal(true);
  };

  const abrirEditar = async (item, soloVer = false) => {
    setViewMode(soloVer);
    setForm({ ...inicialForm, ...item });
    setModal(true);
    await cargarDetalle(item.id);
  };

  const guardar = async () => {
    try {
      if (!form.empresa_id) return alert("Selecciona una empresa.");
      if (!form.codigo?.trim()) return alert("El código es obligatorio.");
      if (!form.titulo?.trim()) return alert("El título es obligatorio.");
      if (!form.descripcion?.trim()) return alert("La descripción es obligatoria.");
      const payload = limpiarPayload(form);
      let saved;
      if (form.id) saved = await actualizarIncidenteSST(form.id, payload);
      else saved = await crearIncidenteSST(payload);
      setForm({ ...form, ...saved, id: saved.id });
      await cargarDetalle(saved.id);
      await cargar();
      alert("Evento SST guardado correctamente.");
    } catch (error) { alert(getErrorMessage(error)); }
  };

  const anular = async (id) => {
    if (!window.confirm("¿Anular este incidente/accidente SST?")) return;
    try { await eliminarIncidenteSST(id); await cargar(); }
    catch (error) { alert(getErrorMessage(error)); }
  };

  const agregarLesionado = async () => {
    try {
      if (!form.id) return alert("Primero guarda el evento para registrar lesionados.");
      if (!lesionadoForm.nombre?.trim()) return alert("El nombre del lesionado es obligatorio.");
      await crearLesionadoIncidenteSST(form.id, {
        ...lesionadoForm,
        incidente_id: form.id,
        empresa_id: Number(form.empresa_id),
        dias_incapacidad: Number(lesionadoForm.dias_incapacidad || 0),
      });
      setLesionadoForm(inicialLesionado);
      await cargarDetalle(form.id);
      await cargar();
    } catch (error) { alert(getErrorMessage(error)); }
  };

  const agregarTestigo = async () => {
    try {
      if (!form.id) return alert("Primero guarda el evento para registrar testigos.");
      if (!testigoForm.nombre?.trim()) return alert("El nombre del testigo es obligatorio.");
      await crearTestigoIncidenteSST(form.id, { ...testigoForm, incidente_id: form.id, empresa_id: Number(form.empresa_id) });
      setTestigoForm(inicialTestigo);
      await cargarDetalle(form.id);
      await cargar();
    } catch (error) { alert(getErrorMessage(error)); }
  };

  const subirEvidencia = async () => {
    try {
      if (!form.id) return alert("Primero guarda el evento para subir evidencias.");
      if (!evidenciaArchivo) return alert("Selecciona un archivo.");
      const fd = new FormData();
      fd.append("tipo_evidencia", evidenciaTipo);
      fd.append("descripcion", evidenciaDescripcion || "Evidencia incidente/accidente SST");
      fd.append("archivo", evidenciaArchivo);
      await subirEvidenciaIncidenteSST(form.id, fd);
      setEvidenciaArchivo(null);
      await cargarDetalle(form.id);
      await cargar();
    } catch (error) { alert(getErrorMessage(error)); }
  };

  const guardarInvestigacion = async () => {
    try {
      if (!form.id) return alert("Primero guarda el evento para registrar la investigación.");
      const payload = {
        equipo_investigador: form.equipo_investigador || "",
        investigador_lider: form.investigador_lider || "",
        fecha_investigacion: form.fecha_investigacion || hoyISO(),
        metodologia_investigacion: form.metodologia_investigacion || "5_PORQUES",
        estado_investigacion: form.estado_investigacion || "EN_PROCESO",
        descripcion_hechos: form.descripcion_hechos || "",
        agente_material: form.agente_material || "",
        mecanismo_evento: form.mecanismo_evento || "",
        tipo_contacto: form.tipo_contacto || "",
        acto_inseguro: form.acto_inseguro || "",
        condicion_insegura: form.condicion_insegura || "",
        causa_inmediata: form.causa_inmediata || "",
        causa_basica: form.causa_basica || "",
        causa_raiz: form.causa_raiz || "",
        porque_1: form.porque_1 || "",
        porque_2: form.porque_2 || "",
        porque_3: form.porque_3 || "",
        porque_4: form.porque_4 || "",
        porque_5: form.porque_5 || "",
        factores_personales: form.factores_personales || "",
        factores_trabajo: form.factores_trabajo || "",
        factores_organizacionales: form.factores_organizacionales || "",
        causas_directas: form.causas_directas || "",
        causas_indirectas: form.causas_indirectas || "",
        arbol_causas: form.arbol_causas || "",
        controles_existentes: form.controles_existentes || "",
        controles_recomendados: form.controles_recomendados || "",
        plan_investigacion: form.plan_investigacion || "",
        conclusion_investigacion: form.conclusion_investigacion || "",
        recomendaciones_investigacion: form.recomendaciones_investigacion || "",
      };
      const updated = await actualizarInvestigacionIncidenteSST(form.id, payload);
      setForm({ ...form, ...updated });
      await cargar();
      alert("Investigación y árbol de causas guardados correctamente.");
    } catch (error) { alert(getErrorMessage(error)); }
  };

  const cerrarInvestigacion = async () => {
    try {
      if (!form.id) return alert("Primero guarda el evento.");
      if (!form.causa_raiz?.trim()) return alert("Registra la causa raíz antes de cerrar la investigación.");
      if (!form.conclusion_investigacion?.trim()) return alert("Registra la conclusión de la investigación.");
      const updated = await cerrarInvestigacionIncidenteSST(form.id, {
        conclusion_investigacion: form.conclusion_investigacion,
        recomendaciones_investigacion: form.recomendaciones_investigacion || "",
        requiere_capa: Boolean(form.requiere_capa),
        observacion: "Cierre de investigación desde frontend.",
      });
      setForm({ ...form, ...updated });
      await cargar();
      alert("Investigación cerrada correctamente.");
    } catch (error) { alert(getErrorMessage(error)); }
  };



  const generarCapa = async (incidente = form) => {
    try {
      if (!incidente?.id) return alert("Primero guarda el evento para generar CAPA.");
      if (incidente.capa_id) return alert(`Este evento ya tiene CAPA vinculada: #${incidente.capa_id}`);
      if (!window.confirm("¿Generar CAPA automática desde este incidente/accidente?")) return;
      const updated = await generarCapaDesdeIncidenteSST(incidente.id);
      if (form?.id === incidente.id) setForm({ ...form, ...updated });
      await cargar();
      alert(`CAPA generada y vinculada correctamente. CAPA ID: ${updated.capa_id || "ver módulo CAPA"}`);
    } catch (error) { alert(getErrorMessage(error)); }
  };


  const exportarGeneralExcel = async () => {
    try { await exportarIncidentesExcelGeneral(filtros); }
    catch (error) { alert(getErrorMessage(error)); }
  };

  const exportarGeneralPdf = async () => {
    try { await exportarIncidentesPdfGeneral(filtros); }
    catch (error) { alert(getErrorMessage(error)); }
  };

  const exportarDashboardPdf = async () => {
    try { await exportarDashboardEjecutivoIncidentesPdf(filtros); }
    catch (error) { alert(getErrorMessage(error)); }
  };

  const exportarPdfIndividual = async (item) => {
    try { await exportarIncidentePdfIndividual(item.id); }
    catch (error) { alert(getErrorMessage(error)); }
  };

  const exportarActaPdf = async (item) => {
    try { await exportarActaInvestigacionPdf(item.id); }
    catch (error) { alert(getErrorMessage(error)); }
  };

  const exportarInformePdf = async (item) => {
    try {
      if (item.tipo_evento === "ACCIDENTE") await exportarInformeAccidentePdf(item.id);
      else await exportarInformeIncidentePdf(item.id);
    } catch (error) { alert(getErrorMessage(error)); }
  };

  const limpiarFiltros = () => {
    const siguientes = { ...filtroInicial, tipo_evento: tipoInicial };
    setFiltros(siguientes);
    cargar(siguientes);
  };

  return (
    <main className="incidentes-page">
      <section className="inc-hero">
        <div>
          <h1>Incidentes y Accidentes SST</h1>
          <p>Registra eventos, investigaciones, evidencias y acciones CAPA.</p>
        </div>
        <div className="inc-hero-actions">
          <button className="inc-btn-light" title="Actualizar datos" onClick={cargar} disabled={loading}><RefreshCw size={16} /> Actualizar</button>
          <button className="inc-btn-light" title="Exportar Excel" onClick={exportarGeneralExcel}><Download size={16} /> Excel</button>
          <button className="inc-btn-light" title="Exportar PDF" onClick={exportarGeneralPdf}><FileText size={16} /> PDF</button>
          <button className="inc-btn-light" title="Exportar dashboard PDF" onClick={exportarDashboardPdf}><BarChart3 size={16} /> Dashboard PDF</button>
          <button className="inc-btn-primary" title="Registrar nuevo evento" onClick={abrirNuevo}><Plus size={16} /> Nuevo evento</button>
        </div>
      </section>

      <section className="inc-layout">
        <div className="inc-content">
          <section className="inc-kpis-grid">
            <KPI icon={FileWarning} label="Total eventos" value={kpis.total} />
            <KPI icon={AlertTriangle} label="Incidentes" value={kpis.incidentes} tone="yellow" />
            <KPI icon={ShieldAlert} label="Accidentes" value={kpis.accidentes} tone="red" />
            <KPI icon={Users} label="Lesionados" value={kpis.lesionados} tone="purple" />
            <KPI icon={Paperclip} label="Evidencias" value={kpis.evidencias} tone="green" />
          </section>

          <section className="inc-indicators-grid">
            <article><small>Cumplimiento</small><strong>{kpis.cumplimiento || 0}%</strong><div><span style={{ width: `${kpis.cumplimiento || 0}%` }} /></div></article>
            <article><small>Abiertos</small><strong>{kpis.abiertos || 0}</strong><div><span style={{ width: `${Math.min((kpis.abiertos || 0) * 20, 100)}%` }} /></div></article>
            <article><small>Graves</small><strong>{kpis.graves || 0}</strong><div><span style={{ width: `${Math.min((kpis.graves || 0) * 30, 100)}%` }} /></div></article>
            <article><small>Testigos</small><strong>{kpis.testigos || 0}</strong><div><span style={{ width: `${Math.min((kpis.testigos || 0) * 20, 100)}%` }} /></div></article>
          </section>

          <section className="inc-charts-grid">
            <Bars title="Por tipo" icon={BarChart3} data={charts.por_tipo || []} />
            <Bars title="Por clasificación" icon={ShieldAlert} data={charts.por_clasificacion || []} />
            <Bars title="Por estado" icon={CheckCircle2} data={charts.por_estado || []} />
            <Bars title="Por severidad" icon={AlertTriangle} data={charts.por_severidad || []} />
            <Bars title="Por área" icon={Activity} data={charts.por_area || []} />
            <Bars title="Por consecuencia" icon={FileText} data={charts.por_consecuencia || []} />
          </section>

          <section className={`inc-semaforo inc-semaforo-${String(kpis.semaforo || "verde").toLowerCase()}`}>
            <div><span>Semáforo incidentes y accidentes SST</span><h3>{kpis.semaforo || "VERDE"}</h3><p>Cumplimiento: {kpis.cumplimiento || 0}% · Abiertos: {kpis.abiertos || 0}</p></div><strong>{kpis.score_riesgo || 0}</strong>
          </section>

          <section className="inc-table-card">
            <div className="inc-filter-top">
              <label className="inc-search"><Search size={16} /><input value={filtros.q} onChange={(e) => setFiltros({ ...filtros, q: e.target.value })} placeholder="Buscar por código, título, lugar o descripción..." /></label>
              <button className="inc-btn-light" onClick={limpiarFiltros}><Filter size={15} /> Limpiar</button>
              <button className="inc-btn-light" onClick={cargar}><RefreshCw size={15} /> Actualizar</button>
            </div>
            <div className="inc-filters-grid">
              <select value={filtros.empresa_id} onChange={(e) => setFiltros({ ...filtros, empresa_id: e.target.value })}><option value="TODOS">Todas las empresas</option>{empresas.map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}</select>
              <select value={filtros.tipo_evento} onChange={(e) => setFiltros({ ...filtros, tipo_evento: e.target.value })}><option value="TODOS">Todos los tipos</option><option value="INCIDENTE">Incidente</option><option value="ACCIDENTE">Accidente</option></select>
              <select value={filtros.clasificacion} onChange={(e) => setFiltros({ ...filtros, clasificacion: e.target.value })}><option value="TODOS">Todas las clasificaciones</option><option value="INCIDENTE">Incidente</option><option value="ACCIDENTE_LEVE">Accidente leve</option><option value="ACCIDENTE_GRAVE">Accidente grave</option><option value="ACCIDENTE_MORTAL">Accidente mortal</option></select>
              <select value={filtros.estado} onChange={(e) => setFiltros({ ...filtros, estado: e.target.value })}><option value="TODOS">Todos los estados</option><option value="REPORTADO">Reportado</option><option value="EN_INVESTIGACION">En investigación</option><option value="CON_CAPA">Con CAPA</option><option value="CERRADO">Cerrado</option></select>
              <select value={filtros.severidad} onChange={(e) => setFiltros({ ...filtros, severidad: e.target.value })}><option value="TODOS">Todas las severidades</option><option value="BAJA">Baja</option><option value="MEDIA">Media</option><option value="ALTA">Alta</option><option value="CRITICA">Crítica</option></select>
            </div>
            <div className="inc-table-wrap">
              <table>
                <thead><tr><th>Código</th><th>Evento</th><th>Empresa</th><th>Fecha</th><th>Tipo</th><th>Clasificación</th><th>Les/Test/Evid</th><th>Estado</th><th>Acciones</th></tr></thead>
                <tbody>
                  {!paginaItems.length && <tr><td colSpan="9" className="inc-empty">No hay incidentes o accidentes registrados.</td></tr>}
                  {paginaItems.map((item) => (
                    <tr key={item.id}>
                      <td><b>{item.codigo}</b></td>
                      <td><b>{item.titulo}</b><small>{item.lugar || "Sin lugar"}</small></td>
                      <td>{item.empresa_nombre || "-"}</td>
                      <td>{item.fecha_evento}</td>
                      <td><span className={`inc-pill ${String(item.tipo_evento).toLowerCase()}`}>{item.tipo_evento}</span></td>
                      <td>{item.clasificacion}</td>
                      <td>{item.total_lesionados || 0}/{item.total_testigos || 0}/{item.total_evidencias || 0}</td>
                      <td><span className={`inc-status ${String(item.estado).toLowerCase()}`}>{item.estado}</span></td>
                      <td><div className="inc-actions"><button onClick={() => abrirEditar(item, true)} title="Ver"><Eye size={15} /></button><button onClick={() => abrirEditar(item)} title="Editar"><Edit3 size={15} /></button><button onClick={() => generarCapa(item)} title={item.capa_id ? `CAPA #${item.capa_id}` : "Generar CAPA"}><Target size={15} /></button><button onClick={() => anular(item.id)} title="Anular"><Trash2 size={15} /></button></div></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <footer className="inc-pagination"><span>Mostrando {paginaItems.length} de {filtrados.length} eventos</span><div><select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPagina(1); }}><option value="10">10</option><option value="25">25</option><option value="50">50</option></select><button disabled={pagina <= 1} onClick={() => setPagina(pagina - 1)}>‹</button><b>Página {pagina}/{totalPaginas}</b><button disabled={pagina >= totalPaginas} onClick={() => setPagina(pagina + 1)}>›</button></div></footer>
          </section>
        </div>

        <aside className="inc-right-panel">
          <article className="inc-intel-card"><h3>Dashboard inteligente</h3><div className="inc-ring" style={{ "--inc-ring": `${Math.min(kpis.cumplimiento || 0, 100)}%` }}><strong>{kpis.cumplimiento || 0}%</strong><span>Índice gestión</span></div><h4>{kpis.semaforo === "VERDE" ? "Gestión estable" : "Revisión requerida"}</h4><p>Control de investigación, clasificación, lesionados, testigos y evidencias.</p></article>
          <article><h3>Alertas SST</h3><p><span>Abiertos</span><strong>{alertas.abiertos || 0}</strong></p><p><span>Graves</span><strong>{alertas.graves || 0}</strong></p><p><span>Mortales</span><strong>{alertas.mortales || 0}</strong></p><p><span>Vencidos</span><strong>{alertas.vencidos || 0}</strong></p></article>
          <article><h3>Recomendaciones PRO</h3><ul>{recomendaciones.map((r, idx) => <li key={idx}>{r}</li>)}</ul></article>
        </aside>
      </section>

      {modal && (
        <div className="inc-modal-backdrop">
          <section className="inc-form-modal">
            <header className="inc-modal-header"><div><span>{viewMode ? "Ver evento SST" : form.id ? "Editar evento SST" : "Nuevo evento SST"}</span><h2>{form.titulo || "Incidente / Accidente SST"}</h2><p>Registro con lesionados, testigos, evidencias y trazabilidad.</p></div><button onClick={() => setModal(false)}><X size={20} /></button></header>
            <div className="inc-modal-body">
              <div className="inc-form-grid">
                <label>Empresa<select disabled={viewMode} value={form.empresa_id || ""} onChange={(e) => setForm({ ...form, empresa_id: e.target.value })}><option value="">Seleccione...</option>{empresas.map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}</select></label>
                <label>Código<input disabled={viewMode} value={form.codigo || ""} onChange={(e) => setForm({ ...form, codigo: e.target.value })} /></label>
                <label>Tipo evento<select disabled={viewMode} value={form.tipo_evento || "INCIDENTE"} onChange={(e) => setForm({ ...form, tipo_evento: e.target.value, clasificacion: e.target.value === "INCIDENTE" ? "INCIDENTE" : "ACCIDENTE_LEVE" })}><option value="INCIDENTE">Incidente</option><option value="ACCIDENTE">Accidente</option></select></label>
                <label>Clasificación<select disabled={viewMode} value={form.clasificacion || "INCIDENTE"} onChange={(e) => setForm({ ...form, clasificacion: e.target.value })}><option value="INCIDENTE">Incidente</option><option value="ACCIDENTE_LEVE">Accidente leve</option><option value="ACCIDENTE_GRAVE">Accidente grave</option><option value="ACCIDENTE_MORTAL">Accidente mortal</option></select></label>
                <label className="inc-full">Título<input disabled={viewMode} value={form.titulo || ""} onChange={(e) => setForm({ ...form, titulo: e.target.value })} /></label>
                <label className="inc-full">Descripción<textarea disabled={viewMode} value={form.descripcion || ""} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} /></label>
                <label>Sede<select disabled={viewMode} value={form.sede_id || ""} onChange={(e) => setForm({ ...form, sede_id: e.target.value })}><option value="">Sin sede</option>{sedes.map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}</select></label>
                <label>Área<select disabled={viewMode} value={form.area_id || ""} onChange={(e) => setForm({ ...form, area_id: e.target.value })}><option value="">Sin área</option>{areas.map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}</select></label>
                <label>Cargo<select disabled={viewMode} value={form.cargo_id || ""} onChange={(e) => setForm({ ...form, cargo_id: e.target.value })}><option value="">Sin cargo</option>{cargos.map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}</select></label>
                <label>Empleado<select disabled={viewMode} value={form.empleado_id || ""} onChange={(e) => setForm({ ...form, empleado_id: e.target.value })}><option value="">Sin empleado</option>{empleados.map((e) => <option key={e.id} value={e.id}>{e.nombres} {e.apellidos}</option>)}</select></label>
                <label>Lugar<input disabled={viewMode} value={form.lugar || ""} onChange={(e) => setForm({ ...form, lugar: e.target.value })} /></label>
                <label>Fecha evento<input disabled={viewMode} type="date" value={form.fecha_evento || hoyISO()} onChange={(e) => setForm({ ...form, fecha_evento: e.target.value })} /></label>
                <label>Hora evento<input disabled={viewMode} type="time" value={form.hora_evento || ""} onChange={(e) => setForm({ ...form, hora_evento: e.target.value })} /></label>
                <label>Fecha reporte<input disabled={viewMode} type="date" value={form.fecha_reporte || hoyISO()} onChange={(e) => setForm({ ...form, fecha_reporte: e.target.value })} /></label>
                <label>Estado<select disabled={viewMode} value={form.estado || "REPORTADO"} onChange={(e) => setForm({ ...form, estado: e.target.value })}><option value="REPORTADO">Reportado</option><option value="EN_INVESTIGACION">En investigación</option><option value="CON_CAPA">Con CAPA</option><option value="CERRADO">Cerrado</option><option value="ANULADO">Anulado</option></select></label>
                <label>Severidad<select disabled={viewMode} value={form.severidad || "BAJA"} onChange={(e) => setForm({ ...form, severidad: e.target.value })}><option value="BAJA">Baja</option><option value="MEDIA">Media</option><option value="ALTA">Alta</option><option value="CRITICA">Crítica</option></select></label>
                <label>Consecuencia<input disabled={viewMode} value={form.consecuencia || ""} onChange={(e) => setForm({ ...form, consecuencia: e.target.value })} /></label>
                <label>Días incapacidad<input disabled={viewMode} type="number" min="0" value={form.dias_incapacidad || 0} onChange={(e) => setForm({ ...form, dias_incapacidad: e.target.value })} /></label>
                <label className="inc-check"><input disabled={viewMode} type="checkbox" checked={!!form.requiere_investigacion} onChange={(e) => setForm({ ...form, requiere_investigacion: e.target.checked })} /> Requiere investigación</label>
                <label className="inc-check"><input disabled={viewMode} type="checkbox" checked={!!form.requiere_capa} onChange={(e) => setForm({ ...form, requiere_capa: e.target.checked })} /> Requiere CAPA</label>
                <label className="inc-full">Acto inseguro<textarea disabled={viewMode} value={form.acto_inseguro || ""} onChange={(e) => setForm({ ...form, acto_inseguro: e.target.value })} /></label>
                <label className="inc-full">Condición insegura<textarea disabled={viewMode} value={form.condicion_insegura || ""} onChange={(e) => setForm({ ...form, condicion_insegura: e.target.value })} /></label>
                <label>Causa inmediata<textarea disabled={viewMode} value={form.causa_inmediata || ""} onChange={(e) => setForm({ ...form, causa_inmediata: e.target.value })} /></label>
                <label>Causa básica<textarea disabled={viewMode} value={form.causa_basica || ""} onChange={(e) => setForm({ ...form, causa_basica: e.target.value })} /></label>
                <label className="inc-full">Causa raíz<textarea disabled={viewMode} value={form.causa_raiz || ""} onChange={(e) => setForm({ ...form, causa_raiz: e.target.value })} /></label>
                <label className="inc-full">Acción inmediata<textarea disabled={viewMode} value={form.accion_inmediata || ""} onChange={(e) => setForm({ ...form, accion_inmediata: e.target.value })} /></label>

                <section className="inc-subpanel inc-full inc-investigation-panel">
                  <div className="inc-panel-head">
                    <div>
                      <h3><Activity size={18} /> Investigación y árbol de causas</h3>
                      <p>Documenta el equipo investigador, hechos, 5 Porqués, causas directas/indirectas, controles y cierre de investigación.</p>
                    </div>
                    <span className={`inc-investigation-status ${form.investigacion_cerrada ? "cerrada" : "pendiente"}`}>
                      {form.investigacion_cerrada ? "Investigación cerrada" : (form.estado_investigacion || "PENDIENTE")}
                    </span>
                  </div>

                  <div className="inc-investigation-grid">
                    <label>Investigador líder<input disabled={viewMode} value={form.investigador_lider || ""} onChange={(e) => setForm({ ...form, investigador_lider: e.target.value })} /></label>
                    <label>Fecha investigación<input disabled={viewMode} type="date" value={form.fecha_investigacion || hoyISO()} onChange={(e) => setForm({ ...form, fecha_investigacion: e.target.value })} /></label>
                    <label>Metodología<select disabled={viewMode} value={form.metodologia_investigacion || "5_PORQUES"} onChange={(e) => setForm({ ...form, metodologia_investigacion: e.target.value })}><option value="5_PORQUES">5 Porqués</option><option value="ARBOL_CAUSAS">Árbol de causas</option><option value="ISHIKAWA">Ishikawa</option><option value="MIXTA">Mixta</option></select></label>
                    <label>Estado investigación<select disabled={viewMode} value={form.estado_investigacion || "PENDIENTE"} onChange={(e) => setForm({ ...form, estado_investigacion: e.target.value })}><option value="PENDIENTE">Pendiente</option><option value="EN_PROCESO">En proceso</option><option value="ANALISIS_CAUSAL">Análisis causal</option><option value="PLAN_ACCION">Plan de acción</option><option value="CERRADA">Cerrada</option></select></label>
                    <label className="inc-full">Equipo investigador<textarea disabled={viewMode} value={form.equipo_investigador || ""} onChange={(e) => setForm({ ...form, equipo_investigador: e.target.value })} placeholder="Responsable SST, jefe de área, testigo, COPASST, etc." /></label>
                    <label className="inc-full">Descripción ampliada de los hechos<textarea disabled={viewMode} value={form.descripcion_hechos || ""} onChange={(e) => setForm({ ...form, descripcion_hechos: e.target.value })} /></label>
                    <label>Agente material<input disabled={viewMode} value={form.agente_material || ""} onChange={(e) => setForm({ ...form, agente_material: e.target.value })} placeholder="Máquina, herramienta, superficie, cable, escalera..." /></label>
                    <label>Mecanismo del evento<input disabled={viewMode} value={form.mecanismo_evento || ""} onChange={(e) => setForm({ ...form, mecanismo_evento: e.target.value })} placeholder="Caída, golpe, atrapamiento, contacto eléctrico..." /></label>
                    <label className="inc-full">Tipo de contacto<input disabled={viewMode} value={form.tipo_contacto || ""} onChange={(e) => setForm({ ...form, tipo_contacto: e.target.value })} /></label>
                  </div>

                  <div className="inc-five-whys">
                    {[1,2,3,4,5].map((n) => (
                      <label key={n}>¿Por qué {n}?<textarea disabled={viewMode} value={form[`porque_${n}`] || ""} onChange={(e) => setForm({ ...form, [`porque_${n}`]: e.target.value })} /></label>
                    ))}
                  </div>

                  <div className="inc-investigation-grid">
                    <label>Factores personales<textarea disabled={viewMode} value={form.factores_personales || ""} onChange={(e) => setForm({ ...form, factores_personales: e.target.value })} /></label>
                    <label>Factores del trabajo<textarea disabled={viewMode} value={form.factores_trabajo || ""} onChange={(e) => setForm({ ...form, factores_trabajo: e.target.value })} /></label>
                    <label className="inc-full">Factores organizacionales<textarea disabled={viewMode} value={form.factores_organizacionales || ""} onChange={(e) => setForm({ ...form, factores_organizacionales: e.target.value })} /></label>
                    <label>Causas directas<textarea disabled={viewMode} value={form.causas_directas || ""} onChange={(e) => setForm({ ...form, causas_directas: e.target.value })} /></label>
                    <label>Causas indirectas<textarea disabled={viewMode} value={form.causas_indirectas || ""} onChange={(e) => setForm({ ...form, causas_indirectas: e.target.value })} /></label>
                    <label className="inc-full">Árbol de causas<textarea disabled={viewMode} value={form.arbol_causas || ""} onChange={(e) => setForm({ ...form, arbol_causas: e.target.value })} placeholder="Evento → condición/acto → causa inmediata → causa básica → causa raíz" /></label>
                    <label>Controles existentes<textarea disabled={viewMode} value={form.controles_existentes || ""} onChange={(e) => setForm({ ...form, controles_existentes: e.target.value })} /></label>
                    <label>Controles recomendados<textarea disabled={viewMode} value={form.controles_recomendados || ""} onChange={(e) => setForm({ ...form, controles_recomendados: e.target.value })} /></label>
                    <label className="inc-full">Plan de investigación<textarea disabled={viewMode} value={form.plan_investigacion || ""} onChange={(e) => setForm({ ...form, plan_investigacion: e.target.value })} /></label>
                    <label className="inc-full">Conclusión investigación<textarea disabled={viewMode} value={form.conclusion_investigacion || ""} onChange={(e) => setForm({ ...form, conclusion_investigacion: e.target.value })} /></label>
                    <label className="inc-full">Recomendaciones investigación<textarea disabled={viewMode} value={form.recomendaciones_investigacion || ""} onChange={(e) => setForm({ ...form, recomendaciones_investigacion: e.target.value })} /></label>
                  </div>

                  {!viewMode && form.id && (
                    <div className="inc-investigation-actions">
                      <button className="inc-btn-light" onClick={guardarInvestigacion}><FileText size={16}/> Guardar investigación</button>
                      <button className="inc-btn-primary" onClick={cerrarInvestigacion}><CheckCircle2 size={16}/> Cerrar investigación</button>
                    </div>
                  )}
                </section>

                {form.id && (
                  <section className="inc-subpanel inc-full inc-capa-panel">
                    <h3><Target size={18} /> Integración automática CAPA</h3>
                    <p>
                      {form.capa_id
                        ? `Evento vinculado a CAPA #${form.capa_id}. Consulta el módulo CAPA para seguimiento y cierre.`
                        : "Genera una acción correctiva/preventiva desde la investigación, usando causa raíz, controles y recomendaciones."}
                    </p>
                    {!viewMode && !form.capa_id && (
                      <button className="inc-btn-primary" onClick={() => generarCapa(form)}>
                        <Target size={16} /> Generar CAPA automática
                      </button>
                    )}
                  </section>
                )}


                <label className="inc-full">Observaciones<textarea disabled={viewMode} value={form.observaciones || ""} onChange={(e) => setForm({ ...form, observaciones: e.target.value })} /></label>
              </div>

              <section className="inc-subpanel inc-full">
                <h3><UserRound size={18} /> Lesionados</h3>
                {!viewMode && <div className="inc-lesionado-form"><input placeholder="Nombre" value={lesionadoForm.nombre} onChange={(e) => setLesionadoForm({ ...lesionadoForm, nombre: e.target.value })} /><input placeholder="Documento" value={lesionadoForm.documento} onChange={(e) => setLesionadoForm({ ...lesionadoForm, documento: e.target.value })} /><input placeholder="Parte afectada" value={lesionadoForm.parte_cuerpo_afectada} onChange={(e) => setLesionadoForm({ ...lesionadoForm, parte_cuerpo_afectada: e.target.value })} /><select value={lesionadoForm.gravedad} onChange={(e) => setLesionadoForm({ ...lesionadoForm, gravedad: e.target.value })}><option value="LEVE">Leve</option><option value="MODERADA">Moderada</option><option value="GRAVE">Grave</option><option value="MORTAL">Mortal</option></select><button className="inc-btn-primary" onClick={agregarLesionado}><Plus size={16}/> Agregar</button><textarea placeholder="Descripción lesión" value={lesionadoForm.descripcion_lesion} onChange={(e) => setLesionadoForm({ ...lesionadoForm, descripcion_lesion: e.target.value })} /></div>}
                <div className="inc-list-pro">{!lesionados.length && <p className="inc-empty-card">Sin lesionados registrados.</p>}{lesionados.map((l) => <div className="inc-row-pro" key={l.id}><span><UserRound size={18}/></span><div><b>{l.nombre}</b><small>{l.documento || "Sin documento"} · {l.parte_cuerpo_afectada || "Sin parte afectada"} · {l.gravedad}</small></div>{!viewMode && <button onClick={async()=>{await eliminarLesionadoIncidenteSST(l.id); await cargarDetalle(form.id); await cargar();}}><Trash2 size={15}/></button>}</div>)}</div>
              </section>

              <section className="inc-subpanel inc-full">
                <h3><Users size={18} /> Testigos</h3>
                {!viewMode && <div className="inc-testigo-form"><input placeholder="Nombre" value={testigoForm.nombre} onChange={(e) => setTestigoForm({ ...testigoForm, nombre: e.target.value })} /><input placeholder="Documento" value={testigoForm.documento} onChange={(e) => setTestigoForm({ ...testigoForm, documento: e.target.value })} /><input placeholder="Cargo" value={testigoForm.cargo} onChange={(e) => setTestigoForm({ ...testigoForm, cargo: e.target.value })} /><input placeholder="Teléfono" value={testigoForm.telefono} onChange={(e) => setTestigoForm({ ...testigoForm, telefono: e.target.value })} /><button className="inc-btn-primary" onClick={agregarTestigo}><Plus size={16}/> Agregar</button><textarea placeholder="Declaración" value={testigoForm.declaracion} onChange={(e) => setTestigoForm({ ...testigoForm, declaracion: e.target.value })} /></div>}
                <div className="inc-list-pro">{!testigos.length && <p className="inc-empty-card">Sin testigos registrados.</p>}{testigos.map((t) => <div className="inc-row-pro" key={t.id}><span><Users size={18}/></span><div><b>{t.nombre}</b><small>{t.documento || "Sin documento"} · {t.cargo || "Sin cargo"}</small><small>{t.declaracion || "Sin declaración"}</small></div>{!viewMode && <button onClick={async()=>{await eliminarTestigoIncidenteSST(t.id); await cargarDetalle(form.id); await cargar();}}><Trash2 size={15}/></button>}</div>)}</div>
              </section>

              <section className="inc-subpanel inc-full">
                <h3><Paperclip size={18} /> Evidencias del evento</h3>
                {!viewMode && <div className="inc-evidencia-form"><select value={evidenciaTipo} onChange={(e)=>setEvidenciaTipo(e.target.value)}><option value="EVIDENCIA_EVENTO">Evidencia evento</option><option value="FOTO_LUGAR">Foto lugar</option><option value="SOPORTE_MEDICO">Soporte médico</option><option value="DECLARACION">Declaración</option><option value="ACTA">Acta</option></select><input value={evidenciaDescripcion} onChange={(e)=>setEvidenciaDescripcion(e.target.value)} placeholder="Descripción"/><label className="inc-file-pill"><UploadCloud size={16}/> Archivo<input type="file" onChange={(e)=>setEvidenciaArchivo(e.target.files?.[0] || null)} /></label><button className="inc-btn-primary" onClick={subirEvidencia}>Subir</button></div>}
                {evidenciaArchivo && <small>Seleccionado: {evidenciaArchivo.name}</small>}
                <div className="inc-list-pro">{!evidencias.length && <p className="inc-empty-card">Sin evidencias registradas.</p>}{evidencias.map((a) => <div className="inc-row-pro inc-file-row-pro" key={a.id}><span>{a.mime_type?.includes("image") ? <img src={urlArchivoIncidenteSST(a.thumb_url || a.url)} alt="thumb"/> : <FileText size={18}/>}</span><div><b>{a.nombre_original}</b><small>{a.descripcion || "Evidencia"}</small><small>{a.tamano_bytes ? `${Math.round(a.tamano_bytes/1024)} KB` : ""} · {a.mime_type}</small></div><button onClick={()=>setPreview(a)}><Eye size={15}/></button><a href={urlArchivoIncidenteSST(a.url)} download={a.nombre_original}><Download size={15}/></a>{!viewMode && <button onClick={async()=>{await eliminarEvidenciaIncidenteSST(form.id, a.id); await cargarDetalle(form.id); await cargar();}}><Trash2 size={15}/></button>}</div>)}</div>
              </section>

              {form.trazabilidad && <div className="inc-full inc-trazabilidad"><b>Trazabilidad</b><pre>{form.trazabilidad}</pre></div>}
            </div>
            <footer className="inc-modal-footer"><button className="inc-btn-light" onClick={() => setModal(false)}>Cerrar</button>{!viewMode && <button className="inc-btn-primary" onClick={guardar}>Guardar evento</button>}</footer>
          </section>
        </div>
      )}

      {preview && <div className="inc-preview-backdrop"><section className="inc-preview-modal"><header><b>{preview.nombre_original}</b><button onClick={() => setPreview(null)}><X size={18}/></button></header>{preview.mime_type?.includes("image") ? <img src={urlArchivoIncidenteSST(preview.preview_url || preview.url)} alt={preview.nombre_original}/> : <iframe src={urlArchivoIncidenteSST(preview.url)} title="preview" />}</section></div>}
    </main>
  );
}
