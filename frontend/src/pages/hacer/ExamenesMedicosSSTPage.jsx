// ============================================================
// EXÁMENES MÉDICOS SST ENTERPRISE - ERP SST PRO
// FASE 1.1.6.4 — ANALYTICS, ALERTAS Y EXPORTACIÓN PDF / EXCEL
// Archivo: frontend/src/pages/hacer/ExamenesMedicosPage.jsx
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Building2,
  CalendarClock,
  CheckCircle2,
  Download,
  FileText,
  Edit3,
  Eye,
  Filter,
  HeartPulse,
  History,
  LayoutDashboard,
  MapPin,
  Network,
  Paperclip,
  Plus,
  RefreshCcw,
  Search,
  ShieldAlert,
  Sidebar,
  Stethoscope,
  Trash2,
  UploadCloud,
  UserRound,
  X,
} from "lucide-react";
import {
  Bar,
  BarChart,
  Line,
  LineChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  actualizarExamenMedicoSST,
  crearExamenMedicoSST,
  dashboardExamenesMedicosSST,
  exportarExamenesMedicosExcelSST,
  exportarExamenesMedicosPdfSST,
  exportarFichaExamenMedicoPdfSST,
  exportarRestriccionesExamenesPdfSST,
  exportarVencimientosExamenesPdfSST,
  listarExamenesMedicosSST,
  listarEvidenciasExamenMedicoSST,
  subirEvidenciaExamenMedicoSST,
  eliminarEvidenciaExamenMedicoSST,
  abrirArchivoSST,
  obtenerUrlArchivoSST,
} from "../../api/examenMedicoSstApi";
import { listarEmpleados } from "../../api/empleadoSstApi";
import { listarEmpresasSST } from "../../api/empresaSstApi";
import { listarSedesSST } from "../../api/sedeSstApi";
import { listarExamenesCatalogo } from "../../api/profesiogramaApi";
import { listarAreasSST } from "../../api/areaSstApi";
import { listarCargosSST } from "../../api/cargoSstApi";

// FASE 37.2.2.B — Framework Global de Eliminación Inteligente
// En próximos módulos: importar el hook y crear la instancia dentro del componente.
import { toastSuccess, toastError, toastWarning } from "../../utils/toast";
import useSmartDelete from "../../hooks/useSmartDelete";
import "../../styles/examenes-medicos-sst.css";

const hoyISO = () => new Date().toISOString().slice(0, 10);

const sumarDias = (dias) => {
  const fecha = new Date();
  fecha.setDate(fecha.getDate() + dias);
  return fecha.toISOString().slice(0, 10);
};

const initialForm = {
  empleado_id: "",
  tipo_examen: "INGRESO",
  fecha_examen: hoyISO(),
  fecha_vencimiento: sumarDias(365),
  concepto: "APTO",
  medico_ocupacional: "",
  entidad_salud: "",
  restricciones: "",
  observaciones: "",
  examenes_aplicados: [],
  estado: "VIGENTE",
  activo: true,
};

const emptyDashboard = {
  kpis: {
    total: 0,
    vigentes: 0,
    proximos_vencer: 0,
    vencidos: 0,
    aptos: 0,
    con_restricciones: 0,
    no_aptos: 0,
    indice_cumplimiento: 100,
    pendientes_criticos: 0,
    vencen_7: 0,
    vencen_15: 0,
    vencen_30: 0,
    sin_vencimiento: 0,
    empleados_activos: 0,
    empleados_con_examen: 0,
    cobertura_poblacion: 100,
    indice_aptitud: 100,
    indice_restricciones: 0,
    riesgo_medico: "BAJO",
  },
  charts: {
    por_tipo: [],
    por_concepto: [],
    por_estado: [],
    por_empresa: [],
    por_sede: [],
    por_area: [],
    por_cargo: [],
    tendencia_mensual: [],
    vencimientos_mensuales: [],
  },
  alertas: {
    proximos_vencer: 0,
    vencidos: 0,
    con_restricciones: 0,
    no_aptos: 0,
    vencen_7: 0,
    vencen_15: 0,
    vencen_30: 0,
    sin_vencimiento: 0,
    timeline: [],
  },
  indicadores: {
    cobertura_poblacion: 100,
    cumplimiento_ocupacional: 100,
    aptitud_laboral: 100,
    restricciones_activas: 0,
    riesgo_medico: "BAJO",
  },
  recomendaciones: [],
};

const limpiarPayload = (form) => ({
  empleado_id: Number(form.empleado_id),
  tipo_examen: form.tipo_examen,
  fecha_examen: form.fecha_examen,
  fecha_vencimiento: form.fecha_vencimiento || null,
  concepto: form.concepto,
  medico_ocupacional: form.medico_ocupacional || null,
  entidad_salud: form.entidad_salud || null,
  restricciones: form.restricciones || null,
  observaciones: form.observaciones || null,
  examenes_aplicados: form.examenes_aplicados || [],
  estado: form.estado || "VIGENTE",
  activo: Boolean(form.activo),
});

const labelTipo = (value) =>
  ({
    INGRESO: "Ingreso",
    PERIODICO: "Periódico",
    RETIRO: "Retiro",
    POST_INCAPACIDAD: "Post incapacidad",
    RETORNO_LABORAL: "Retorno laboral",
  }[value] || value || "Sin tipo");

const labelConcepto = (value) =>
  ({
    APTO: "Sin Restricciones",
    APTO_CON_RESTRICCIONES: "Con Restricciones Médicas",
    NO_APTO: "No apto",
  }[value] || value || "Sin concepto");

const labelEstado = (value) =>
  ({
    VIGENTE: "Vigente",
    PROXIMO_VENCER: "Próximo a vencer",
    VENCIDO: "Vencido",
  }[value] || value || "Sin estado");

const iniciales = (nombre = "") =>
  nombre
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase())
    .join("") || "EM";


const TIPOS_EVAL_1843 = [
  { codigo: "INGRESO", nombre: "Pre-Ingreso", icon: "🩺" },
  { codigo: "PERIODICO", nombre: "Periódica Programada", icon: "📅" },
  { codigo: "PERIODICO_OCUPACION", nombre: "Periódica por Cambio de Ocupación", icon: "🔄" },
  { codigo: "RETIRO", nombre: "Egreso / Retiro", icon: "🚪" },
  { codigo: "POST_INCAPACIDAD", nombre: "Post-Incapacidad", icon: "🏥" },
  { codigo: "RETORNO_LABORAL", nombre: "Retorno Laboral", icon: "🔙" },
];

const TIPOS_EVIDENCIA = [
  { value: "EXAMEN_OCUPACIONAL", label: "Examen ocupacional" },
  { value: "CONCEPTO_MEDICO", label: "Recomendación médica" },
  { value: "CERTIFICADO_APTITUD", label: "Certificado de aptitud" },
  { value: "RESTRICCIONES_MEDICAS", label: "Restricciones médicas" },
  { value: "OTRO", label: "Otro soporte" },
];

const labelTipoEvidencia = (value) =>
  TIPOS_EVIDENCIA.find((item) => item.value === value)?.label || "Evidencia médica";

const parseDescripcionEvidencia = (descripcion = "") => {
  const raw = String(descripcion || "").trim();
  const match = raw.match(/^\[([^\]]+)\]\s*(.*)$/);
  if (!match) {
    return { tipo: "OTRO", texto: raw || "Evidencia médica ocupacional" };
  }
  return {
    tipo: match[1] || "OTRO",
    texto: match[2] || labelTipoEvidencia(match[1]),
  };
};

const extensionEsPdf = (item) => String(item?.extension || "").toLowerCase() === "pdf" || String(item?.mime_type || "").toLowerCase().includes("pdf");

const formatoBytes = (bytes = 0) => {
  const n = Number(bytes || 0);
  if (!n) return "0 KB";
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
};

function KpiCard({ icon: Icon, label, value, tone = "blue" }) {
  return (
    <article className={`exam-kpi-card exam-tone-${tone}`}>
      <span className="exam-kpi-icon"><Icon size={19} /></span>
      <div>
        <small>{label}</small>
        <strong>{value ?? 0}</strong>
      </div>
    </article>
  );
}

function MiniBars({ title, icon: Icon, data = [] }) {
  const max = Math.max(...data.map((i) => Number(i.value || 0)), 1);
  return (
    <article className="exam-chart-card">
      <h3><Icon size={16} /> {title}</h3>
      <div className="exam-bar-list">
        {data.length === 0 ? <small>Sin información registrada.</small> : null}
        {data.slice(0, 5).map((item) => (
          <div className="exam-bar-row" key={`${title}-${item.name}`}>
            <div className="exam-bar-meta">
              <span>{item.name}</span>
              <b>{item.value}</b>
            </div>
            <div className="exam-bar-track">
              <i style={{ width: `${Math.max(8, (Number(item.value || 0) / max) * 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

function ExamenModal({ modo, form, setForm, empleados, examCatalogo = [], onClose, onSubmit, selected }) {
  const lectura = modo === "ver";
  const titulo = modo === "crear" ? "Nuevo examen médico" : modo === "editar" ? "Editar examen médico" : "Detalle examen médico";

  const update = (field, value) => setForm((prev) => ({ ...prev, [field]: value }));

  const toggleExamenCatalogo = (examen) => {
    const actual = form.examenes_aplicados || [];
    const existe = actual.find((e) => e.id === examen.id);
    if (existe) {
      update("examenes_aplicados", actual.filter((e) => e.id !== examen.id));
    } else {
      update("examenes_aplicados", [...actual, { id: examen.id, codigo: examen.codigo, nombre: examen.nombre }]);
    }
  };

  return (
    <div className="exam-modal-backdrop">
      <section className="exam-form-modal">
        <header className="exam-modal-header">
          <div>
            <span>Evidencias Médicas Enterprise</span>
            <h2>{titulo}</h2>
            <p>Gestión ocupacional conectada con empleados, empresa, sede, área y cargo.</p>
          </div>
          <button type="button" className="exam-close" onClick={onClose}><X size={21} /></button>
        </header>

        <div className="exam-modal-body">
          {lectura ? (
            <div className="exam-detail-grid">
              <article>
                <h3>Empleado</h3>
                <p><b>Nombre:</b> {selected?.empleado_nombre || "Sin dato"}</p>
                <p><b>Documento:</b> {selected?.empleado_documento || "Sin dato"}</p>
                <p><b>Empresa:</b> {selected?.empresa_nombre || "Sin empresa"}</p>
                <p><b>Sede:</b> {selected?.sede_nombre || "Sin sede"}</p>
                <p><b>Área:</b> {selected?.area_nombre || "Sin área"}</p>
                <p><b>Cargo:</b> {selected?.cargo_nombre || "Sin cargo"}</p>
              </article>
              <article>
                <h3>Examen</h3>
                <p><b>Tipo:</b> {labelTipo(selected?.tipo_examen)}</p>
                <p><b>Concepto:</b> {labelConcepto(selected?.concepto)}</p>
                <p><b>Estado:</b> {labelEstado(selected?.estado)}</p>
                <p><b>Fecha examen:</b> {selected?.fecha_examen || "Sin dato"}</p>
                <p><b>Vencimiento:</b> {selected?.fecha_vencimiento || "Sin dato"}</p>
              </article>
              <article>
                <h3>Concepto médico ocupacional</h3>
                <p><b>Médico:</b> {selected?.medico_ocupacional || "Sin dato"}</p>
                <p><b>Entidad:</b> {selected?.entidad_salud || "Sin dato"}</p>
                <p><b>Restricciones:</b> {selected?.restricciones || "Sin restricciones"}</p>
                <p><b>Observaciones:</b> {selected?.observaciones || "Sin observaciones"}</p>
              </article>
              {selected?.examenes_aplicados && selected.examenes_aplicados.length > 0 && (
                <article className="exam-full-width">
                  <h3>Exámenes realizados</h3>
                  <div className="exam-aplicados-list">
                    {selected.examenes_aplicados.map((ex, idx) => (
                      <span key={ex.id || idx} className="exam-aplicado-chip">
                        {ex.nombre || ex.codigo || `Examen ${idx + 1}`}
                      </span>
                    ))}
                  </div>
                </article>
              )}
            </div>
          ) : (
            <form className="exam-form-grid" onSubmit={onSubmit}>
              <label className="exam-full">
                Empleado *
                <select value={form.empleado_id} onChange={(e) => update("empleado_id", e.target.value)} required>
                  <option value="">Seleccione empleado</option>
                  {empleados.map((empleado) => (
                    <option key={empleado.id} value={empleado.id}>
                      {empleado.documento} · {empleado.nombres} {empleado.apellidos} · {empleado.cargo_nombre || "Sin cargo"}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Tipo de examen *
                <select value={form.tipo_examen} onChange={(e) => update("tipo_examen", e.target.value)} required>
                  <option value="INGRESO">Ingreso</option>
                  <option value="PERIODICO">Periódico</option>
                  <option value="RETIRO">Retiro</option>
                  <option value="POST_INCAPACIDAD">Post incapacidad</option>
                  <option value="RETORNO_LABORAL">Retorno laboral</option>
                </select>
              </label>

              <label>
                Recomendación médica *
                <select value={form.concepto} onChange={(e) => update("concepto", e.target.value)} required>
                  <option value="APTO">Sin Restricciones</option>
                  <option value="APTO_CON_RESTRICCIONES"><b>Con Restricciones Médicas</b></option>
                </select>
              </label>

              <label>
                Fecha examen *
                <input type="date" value={form.fecha_examen} onChange={(e) => update("fecha_examen", e.target.value)} required />
              </label>

              <label>
                Fecha vencimiento
                <input type="date" value={form.fecha_vencimiento || ""} onChange={(e) => update("fecha_vencimiento", e.target.value)} />
              </label>

              <label>
                Médico ocupacional
                <input value={form.medico_ocupacional || ""} onChange={(e) => update("medico_ocupacional", e.target.value)} placeholder="Ej. Dra. María Pérez" />
              </label>

              <label>
                Entidad / IPS
                <input value={form.entidad_salud || ""} onChange={(e) => update("entidad_salud", e.target.value)} placeholder="Ej. IPS Salud Ocupacional SAS" />
              </label>

              <label className="exam-full">
                Restricciones médicas
                <textarea value={form.restricciones || ""} onChange={(e) => update("restricciones", e.target.value)} placeholder="Registre restricciones, recomendaciones o limitaciones." />
              </label>

              <label className="exam-full">
                Observaciones
                <textarea value={form.observaciones || ""} onChange={(e) => update("observaciones", e.target.value)} placeholder="Observaciones generales del concepto médico ocupacional." />
              </label>

              <div className="exam-full">
                <b>Exámenes realizados</b>
                <div className="exam-catalogo-grid">
                  {examCatalogo.length === 0 && <small>No hay exámenes en el catálogo.</small>}
                  {examCatalogo.map((ex) => {
                    const seleccionado = (form.examenes_aplicados || []).some((e) => e.id === ex.id);
                    return (
                      <button
                        key={ex.id}
                        type="button"
                        className={`exam-catalogo-chip ${seleccionado ? "seleccionado" : ""}`}
                        onClick={() => toggleExamenCatalogo(ex)}
                      >
                        {ex.nombre}
                      </button>
                    );
                  })}
                </div>
              </div>
            </form>
          )}
        </div>

        <footer className="exam-modal-footer">
          <button type="button" className="exam-btn-light" onClick={onClose}>Cerrar</button>
          {!lectura && <button type="button" className="exam-btn-primary" onClick={onSubmit}>Guardar examen</button>}
        </footer>
      </section>
    </div>
  );
}


function EvidenciasModal({
  examen,
  evidencias,
  file,
  setFile,
  descripcion,
  setDescripcion,
  tipoEvidencia,
  setTipoEvidencia,
  uploading,
  onClose,
  onUpload,
  onDelete,
  onOpen,
  onPreview,
}) {
  const empleado = examen?.empleado_nombre || "Empleado sin nombre";
  const total = evidencias.length;
  const totalPdf = evidencias.filter(extensionEsPdf).length;
  const conceptos = evidencias.filter((item) => parseDescripcionEvidencia(item.descripcion).tipo === "CONCEPTO_MEDICO").length;
  const certificados = evidencias.filter((item) => parseDescripcionEvidencia(item.descripcion).tipo === "CERTIFICADO_APTITUD").length;
  const restricciones = evidencias.filter((item) => parseDescripcionEvidencia(item.descripcion).tipo === "RESTRICCIONES_MEDICAS").length;

  const handleDrop = (event) => {
    event.preventDefault();
    const dropped = event.dataTransfer?.files?.[0];
    if (dropped) setFile(dropped);
  };

  return (
    <div className="exam-modal-backdrop">
      <section className="exam-form-modal exam-evidence-modal-enterprise">
        <header className="exam-modal-header">
          <div>
            <span>Evidencias Médicas Enterprise</span>
            <h2>Evidencias médicas 360°</h2>
            <p>{empleado} · {labelTipo(examen?.tipo_examen)} · {labelConcepto(examen?.concepto)}</p>
          </div>
          <button type="button" className="exam-close" onClick={onClose}><X size={21} /></button>
        </header>

        <div className="exam-modal-body exam-evidence-enterprise-body">
          <section className="exam-evidence-top-grid">
            <article className="exam-evidence-drop-card">
              <div className="exam-evidence-drop-zone" onDrop={handleDrop} onDragOver={(event) => event.preventDefault()}>
                <UploadCloud size={38} />
                <h3>Arrastra y suelta la evidencia</h3>
                <p>PDF del examen, concepto ocupacional, certificado médico o imagen soporte.</p>
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/png,image/jpeg,image/webp"
                  onChange={(event) => setFile(event.target.files?.[0] || null)}
                />
                <strong>{file ? file.name : "Seleccionar archivo PDF / imagen"}</strong>
                {file ? <small>{formatoBytes(file.size)} · {file.type || "archivo"}</small> : null}
              </div>
            </article>

            <article className="exam-evidence-form-card">
              <h3><FileText size={18} /> Clasificación documental</h3>
              <label>
                Tipo de evidencia
                <select value={tipoEvidencia} onChange={(event) => setTipoEvidencia(event.target.value)}>
                  {TIPOS_EVIDENCIA.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
                </select>
              </label>
              <label>
                Descripción
                <input value={descripcion} onChange={(event) => setDescripcion(event.target.value)} placeholder="Ej. Concepto médico ocupacional" />
              </label>
              <button type="button" className="exam-btn-primary" disabled={uploading || !file} onClick={onUpload}>
                <UploadCloud size={17} /> {uploading ? "Subiendo evidencia..." : "Subir evidencia"}
              </button>
            </article>

            <article className="exam-evidence-dashboard-card">
              <div className="exam-side-title-row">
                <h3><Paperclip size={18} /> Dashboard documental</h3>
                <span>{total} archivos</span>
              </div>
              <div className="exam-evidence-doc-kpis">
                <div><b>{totalPdf}</b><span>PDF</span></div>
                <div><b>{conceptos}</b><span>Conceptos</span></div>
                <div><b>{certificados}</b><span>Certificados</span></div>
                <div><b>{restricciones}</b><span>Restricciones</span></div>
              </div>
              <p>Repositorio centralizado en <b>archivos_sst</b> con trazabilidad por examen médico.</p>
            </article>
          </section>

          <section className="exam-evidence-content-grid">
            <article className="exam-evidence-list-card">
              <h3><Paperclip size={18} /> Evidencias registradas</h3>
              {evidencias.length === 0 ? (
                <div className="exam-evidence-empty">
                  <FileText size={34} />
                  <b>Sin evidencias médicas cargadas</b>
                  <p>Cuando cargues archivos aparecerán en este panel con opción de vista previa, descarga y eliminación.</p>
                </div>
              ) : (
                <div className="exam-evidence-list-pro">
                  {evidencias.map((item) => {
                    const parsed = parseDescripcionEvidencia(item.descripcion);
                    return (
                      <article className="exam-evidence-item-pro" key={item.id}>
                        <span><FileText size={20} /></span>
                        <div>
                          <b>{item.nombre_original}</b>
                          <small>{labelTipoEvidencia(parsed.tipo)} · {String(item.extension || "archivo").toUpperCase()} · {formatoBytes(item.tamano_bytes)}</small>
                          <small>{parsed.texto}</small>
                        </div>
                        <button type="button" className="exam-evidence-action" onClick={() => onPreview(item)} title="Vista previa"><Eye size={16} /></button>
                        <button type="button" className="exam-evidence-action" onClick={() => onOpen(item.url)} title="Descargar / abrir"><Download size={16} /></button>
                        <button type="button" className="exam-evidence-action danger" onClick={() => onDelete(item)} title="Eliminar evidencia"><Trash2 size={16} /></button>
                      </article>
                    );
                  })}
                </div>
              )}
            </article>

            <article className="exam-evidence-timeline-card">
              <h3><Activity size={18} /> Timeline documental</h3>
              {evidencias.length === 0 ? (
                <p className="exam-muted-text">Sin trazabilidad documental registrada.</p>
              ) : (
                <div className="exam-evidence-timeline">
                  {evidencias.map((item) => {
                    const parsed = parseDescripcionEvidencia(item.descripcion);
                    return (
                      <div className="exam-timeline-row" key={`timeline-${item.id}`}>
                        <span />
                        <div>
                          <b>{labelTipoEvidencia(parsed.tipo)}</b>
                          <small>{item.fecha_creacion ? new Date(item.fecha_creacion).toLocaleString() : "Sin fecha"}</small>
                          <p>{parsed.texto}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </article>
          </section>
        </div>

        <footer className="exam-modal-footer">
          <button type="button" className="exam-btn-light" onClick={onClose}>Cerrar</button>
        </footer>
      </section>
    </div>
  );
}

function VisorEvidenciaModal({ archivo, onClose, onOpen }) {
  if (!archivo) return null;
  const url = obtenerUrlArchivoSST(archivo.url);
  const parsed = parseDescripcionEvidencia(archivo.descripcion);
  const esPdf = extensionEsPdf(archivo);

  return (
    <div className="exam-modal-backdrop exam-preview-backdrop">
      <section className="exam-preview-modal">
        <header className="exam-modal-header">
          <div>
            <span>Vista previa documental</span>
            <h2>{archivo.nombre_original}</h2>
            <p>{labelTipoEvidencia(parsed.tipo)} · {parsed.texto}</p>
          </div>
          <button type="button" className="exam-close" onClick={onClose}><X size={21} /></button>
        </header>
        <div className="exam-preview-body">
          {esPdf ? (
            <iframe src={url} title={archivo.nombre_original} />
          ) : (
            <img src={url} alt={archivo.nombre_original} />
          )}
        </div>
        <footer className="exam-modal-footer">
          <button type="button" className="exam-btn-light" onClick={() => onOpen(archivo.url)}><Download size={16} /> Abrir / descargar</button>
          <button type="button" className="exam-btn-primary" onClick={onClose}>Cerrar vista previa</button>
        </footer>
      </section>
    </div>
  );
}

export default function ExamenesMedicosSSTPage() {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [examenes, setExamenes] = useState([]);
  const [dashboard, setDashboard] = useState(emptyDashboard);
  const [empleados, setEmpleados] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [areas, setAreas] = useState([]);
  const [cargos, setCargos] = useState([]);
  const [modal, setModal] = useState({ open: false, modo: "crear", item: null });
  const [evidenciasModal, setEvidenciasModal] = useState({ open: false, item: null });
  const [evidencias, setEvidencias] = useState([]);
  const [evidenciaFile, setEvidenciaFile] = useState(null);
  const [evidenciaDescripcion, setEvidenciaDescripcion] = useState("Concepto médico ocupacional");
  const [tipoEvidencia, setTipoEvidencia] = useState("CONCEPTO_MEDICO");
  const [previewArchivo, setPreviewArchivo] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [historialModal, setHistorialModal] = useState({ open: false, empleado: null, examenes: [] });
  const [examCatalogo, setExamCatalogo] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [filters, setFilters] = useState({
    q: "",
    empresa_id: "",
    sede_id: "",
    area_id: "",
    cargo_id: "",
    empleado_id: "",
    tipo_examen: "",
    concepto: "",
    estado: "",
  });

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const params = useMemo(() => ({ ...filters }), [filters]);

  const cargarCatalogos = async () => {
    const [emps, sds, ars, cgs, empleadosData, examCatalogoData] = await Promise.all([
      listarEmpresasSST(),
      listarSedesSST(),
      listarAreasSST(),
      listarCargosSST(),
      listarEmpleados(),
      listarExamenesCatalogo().catch(() => []),
    ]);
    setEmpresas(Array.isArray(emps) ? emps : []);
    setSedes(Array.isArray(sds) ? sds : []);
    setAreas(Array.isArray(ars) ? ars : []);
    setCargos(Array.isArray(cgs) ? cgs : []);
    setEmpleados(Array.isArray(empleadosData) ? empleadosData : []);
    setExamCatalogo(Array.isArray(examCatalogoData) ? examCatalogoData : []);
  };

  const cargarDatos = async () => {
    setLoading(true);
    try {
      const [lista, dash] = await Promise.all([
        listarExamenesMedicosSST(params),
        dashboardExamenesMedicosSST(params),
      ]);
      setExamenes(Array.isArray(lista) ? lista : []);
      setDashboard({ ...emptyDashboard, ...(dash || {}) });
      setPage(1);
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No se pudo cargar exámenes médicos SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarCatalogos();
  }, []);

  useEffect(() => {
    cargarDatos();
  }, [params]);

  const paginated = useMemo(() => {
    const start = (page - 1) * pageSize;
    return examenes.slice(start, start + pageSize);
  }, [examenes, page, pageSize]);

  const totalPages = Math.max(1, Math.ceil(examenes.length / pageSize));

  const setFilter = (field, value) => setFilters((prev) => ({ ...prev, [field]: value }));

  const limpiarFiltros = () => {
    setFilters({ q: "", empresa_id: "", sede_id: "", area_id: "", cargo_id: "", empleado_id: "", tipo_examen: "", concepto: "", estado: "" });
  };

  const abrirCrear = () => {
    setForm(initialForm);
    setModal({ open: true, modo: "crear", item: null });
  };

  const abrirEditar = (item) => {
    setForm({
      empleado_id: item.empleado_id || "",
      tipo_examen: item.tipo_examen || "INGRESO",
      fecha_examen: item.fecha_examen || hoyISO(),
      fecha_vencimiento: item.fecha_vencimiento || "",
      concepto: item.concepto || "APTO",
      medico_ocupacional: item.medico_ocupacional || "",
      entidad_salud: item.entidad_salud || "",
      restricciones: item.restricciones || "",
      observaciones: item.observaciones || "",
      examenes_aplicados: item.examenes_aplicados || [],
      estado: item.estado || "VIGENTE",
      activo: item.activo ?? true,
    });
    setModal({ open: true, modo: "editar", item });
  };

  const abrirVer = (item) => setModal({ open: true, modo: "ver", item });
  const cerrarModal = () => setModal({ open: false, modo: "crear", item: null });

  const abrirHistorialEmpleado = async (item) => {
    try {
      setHistorialModal({ open: true, empleado: item, examenes: [] });
      const params = { empleado_id: item.empleado_id };
      const data = await listarExamenesMedicosSST(params);
      const examenesEmpleado = Array.isArray(data) ? data : (data?.items || []);
      examenesEmpleado.sort((a, b) => new Date(b.fecha_examen) - new Date(a.fecha_examen));
      setHistorialModal({ open: true, empleado: item, examenes: examenesEmpleado });
    } catch (error) {
      console.error(error);
      toastError("Error", "No fue posible cargar el historial del empleado.");
    }
  };

  const cerrarHistorialModal = () => setHistorialModal({ open: false, empleado: null, examenes: [] });

  const guardar = async (event) => {
    event?.preventDefault?.();
    if (!form.empleado_id) {
      toastWarning("Advertencia", "Seleccione un empleado.");
      return;
    }
    if (!form.fecha_examen) {
      toastWarning("Advertencia", "La fecha del examen es obligatoria.");
      return;
    }

    setSaving(true);
    try {
      const payload = limpiarPayload(form);
      if (modal.modo === "editar" && modal.item?.id) {
        await actualizarExamenMedicoSST(modal.item.id, payload);
      } else {
        await crearExamenMedicoSST(payload);
      }
      cerrarModal();
      await cargarDatos();
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No se pudo guardar el examen médico.");
    } finally {
      setSaving(false);
    }
  };

  // ============================================================
  // FASE 37.2.2.B — Eliminación Inteligente Enterprise
  // Módulo: Exámenes Médicos SST
  //
  // GUÍA PARA PRÓXIMOS MÓDULOS:
  // 1. Importar useSmartDelete.
  // 2. Crear una instancia con entidad, etiquetaEntidad, getNombre y onSuccess.
  // 3. Reemplazar el antiguo window.confirm()/DELETE directo por smartDelete.open(registro).
  // 4. Renderizar {smartDelete.modal} al final del componente.
  //
  // Importante: no se toca la eliminación de evidencias médicas; esa acción
  // sigue siendo interna del modal de evidencias y conserva su flujo actual.
  // ============================================================
  const smartDelete = useSmartDelete({
    entidad: "examen_medico",
    etiquetaEntidad: "examen médico",
    getNombre: (item) => {
      const empleado = item?.empleado_nombre || "Empleado sin nombre";
      const tipo = labelTipo(item?.tipo_examen || "");
      const fecha = item?.fecha_examen || "sin fecha";
      return `${empleado} • ${tipo} • ${fecha}`;
    },
    onSuccess: async () => {
      await cargarDatos();
    },
  });

  const eliminar = (item) => {
    smartDelete.open(item);
  };



  const exportarExcel = async () => {
    try {
      await exportarExamenesMedicosExcelSST(params);
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No se pudo exportar el listado general a Excel.");
    }
  };

  const exportarPdf = async () => {
    try {
      await exportarExamenesMedicosPdfSST(params);
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No se pudo exportar el listado general a PDF.");
    }
  };

  const exportarVencimientos = async () => {
    try {
      await exportarVencimientosExamenesPdfSST(params);
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No se pudo exportar el reporte de vencimientos.");
    }
  };

  const exportarRestricciones = async () => {
    try {
      await exportarRestriccionesExamenesPdfSST(params);
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No se pudo exportar el reporte de restricciones.");
    }
  };

  const exportarFicha = async (item) => {
    if (!item?.id) return;
    try {
      await exportarFichaExamenMedicoPdfSST(item.id);
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No se pudo exportar la ficha individual del examen médico.");
    }
  };


  const cargarEvidencias = async (examenId) => {
    if (!examenId) return;
    try {
      const data = await listarEvidenciasExamenMedicoSST(examenId);
      setEvidencias(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No se pudieron cargar las evidencias médicas.");
    }
  };

  const abrirEvidencias = async (item) => {
    setEvidenciasModal({ open: true, item });
    setEvidencias([]);
    setEvidenciaFile(null);
    setEvidenciaDescripcion("Concepto médico ocupacional");
    setTipoEvidencia("CONCEPTO_MEDICO");
    await cargarEvidencias(item.id);
  };

  const cerrarEvidencias = () => {
    setEvidenciasModal({ open: false, item: null });
    setEvidencias([]);
    setEvidenciaFile(null);
    setEvidenciaDescripcion("Concepto médico ocupacional");
    setTipoEvidencia("CONCEPTO_MEDICO");
    setPreviewArchivo(null);
  };

  const subirEvidencia = async () => {
    if (!evidenciasModal.item?.id) return;
    if (!evidenciaFile) {
      toastWarning("Advertencia", "Seleccione un archivo PDF o imagen.");
      return;
    }
    setUploading(true);
    try {
      await subirEvidenciaExamenMedicoSST(evidenciasModal.item.id, evidenciaFile, evidenciaDescripcion, tipoEvidencia);
      setEvidenciaFile(null);
      setEvidenciaDescripcion("Concepto médico ocupacional");
      setTipoEvidencia("CONCEPTO_MEDICO");
      await cargarEvidencias(evidenciasModal.item.id);
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No se pudo subir la evidencia médica.");
    } finally {
      setUploading(false);
    }
  };

  const eliminarEvidencia = async (archivo) => {
    if (!evidenciasModal.item?.id || !archivo?.id) return;
    if (!window.confirm(`¿Eliminar la evidencia ${archivo.nombre_original}?`)) return;
    try {
      await eliminarEvidenciaExamenMedicoSST(evidenciasModal.item.id, archivo.id);
      await cargarEvidencias(evidenciasModal.item.id);
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No se pudo eliminar la evidencia médica.");
    }
  };

  const kpis = dashboard.kpis || emptyDashboard.kpis;
  const charts = dashboard.charts || emptyDashboard.charts;
  const alertas = dashboard.alertas || emptyDashboard.alertas;
  const recomendaciones = dashboard.recomendaciones || emptyDashboard.recomendaciones;
  const indicadores = dashboard.indicadores || emptyDashboard.indicadores;
  const pieData = charts.por_concepto?.length ? charts.por_concepto : [{ name: "Sin datos", value: 1 }];
  const tendenciaData = charts.tendencia_mensual?.length ? charts.tendencia_mensual : [];
  const alertaTimeline = alertas.timeline || [];
  const riesgoMedico = kpis.riesgo_medico || indicadores.riesgo_medico || "BAJO";

  return (
    <main className="examenes-sst-page">
      <section className="exam-hero">
        <div>
          <h1>Exámenes Médicos SST</h1>
          <p>Controla evaluaciones, vencimientos, restricciones y aptitud laboral.</p>
        </div>
        <div className="exam-hero-actions">
          <button className="exam-btn-light" onClick={exportarExcel} title="Exportar listado general a Excel">
            <Download size={17} /> Excel
          </button>
          <button className="exam-btn-light" onClick={exportarPdf} title="Exportar listado general a PDF">
            <FileText size={17} /> PDF
          </button>
          <button className="exam-btn-light exam-btn-secondary" onClick={exportarVencimientos} title="Exportar reporte de vencimientos">
            <CalendarClock size={17} /> Vencimientos
          </button>
          <button className="exam-btn-light exam-btn-secondary" onClick={exportarRestricciones} title="Exportar reporte de restricciones">
            <ShieldAlert size={17} /> Restricciones
          </button>
          <button className="exam-btn-light" title="Actualizar datos" onClick={cargarDatos} disabled={loading}>
            <RefreshCcw size={17} /> Actualizar
          </button>
          <button
            className="exam-btn-light"
            title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
            onClick={() => setSidebarVisible((v) => !v)}
          >
            {sidebarVisible ? <Sidebar size={17} /> : <LayoutDashboard size={17} />}
          </button>
          <button className="exam-btn-primary" title="Registrar nuevo examen" onClick={abrirCrear}>
            <Plus size={17} /> Nuevo examen
          </button>
        </div>
      </section>

      <section className={`exam-main-grid ${!sidebarVisible ? "exam-panel-collapsed" : ""}`}>
        <div className="exam-content">
          <div className="exam-kpis-grid">
            <KpiCard icon={HeartPulse} label="Total exámenes" value={kpis.total} />
            <KpiCard icon={CheckCircle2} label="Vigentes" value={kpis.vigentes} tone="green" />
            <KpiCard icon={CalendarClock} label="Próx. vencer" value={kpis.proximos_vencer} tone="yellow" />
            <KpiCard icon={AlertTriangle} label="Vencidos" value={kpis.vencidos} tone="red" />
            <KpiCard icon={ShieldAlert} label="Restricciones" value={kpis.con_restricciones} tone="purple" />
            <KpiCard icon={UserRound} label="Cobertura" value={`${kpis.cobertura_poblacion ?? 100}%`} />
            <KpiCard icon={Activity} label="Riesgo médico" value={riesgoMedico} tone={riesgoMedico === "CRITICO" ? "red" : riesgoMedico === "MEDIO" ? "yellow" : "green"} />
          </div>

          <div className="exam-indicators-grid">
            <article>
              <small>Cumplimiento ocupacional</small>
              <strong>{indicadores.cumplimiento_ocupacional ?? kpis.indice_cumplimiento ?? 100}%</strong>
              <div><span style={{ width: `${Math.min(100, kpis.indice_cumplimiento ?? 100)}%` }} /></div>
            </article>
            <article>
              <small>Aptitud laboral</small>
              <strong>{indicadores.aptitud_laboral ?? kpis.indice_aptitud ?? 100}%</strong>
              <div><span style={{ width: `${Math.min(100, indicadores.aptitud_laboral ?? kpis.indice_aptitud ?? 100)}%` }} /></div>
            </article>
            <article>
              <small>Vencen en 30 días</small>
              <strong>{alertas.vencen_30 || 0}</strong>
              <div><span style={{ width: `${kpis.total ? Math.min(100, ((alertas.vencen_30 || 0) / kpis.total) * 100) : 0}%` }} /></div>
            </article>
            <article>
              <small>Pendientes críticos</small>
              <strong>{kpis.pendientes_criticos || 0}</strong>
              <div><span style={{ width: `${kpis.total ? Math.min(100, (kpis.pendientes_criticos / kpis.total) * 100) : 0}%` }} /></div>
            </article>
          </div>

          <div className="exam-charts-grid">
            <MiniBars title="Exámenes por tipo" icon={Stethoscope} data={charts.por_tipo || []} />
            <MiniBars title="Por estado" icon={Activity} data={charts.por_estado || []} />
            <MiniBars title="Por empresa" icon={Building2} data={charts.por_empresa || []} />
            <MiniBars title="Por área" icon={Network} data={charts.por_area || []} />
            <MiniBars title="Vencimientos por mes" icon={CalendarClock} data={charts.vencimientos_mensuales || []} />
            <article className="exam-chart-card exam-chart-tall">
              <h3><HeartPulse size={16} /> Concepto médico</h3>
              <ResponsiveContainer width="100%" height={170}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={42} outerRadius={66} paddingAngle={3}>
                    {pieData.map((_, index) => (
                      <Cell key={`cell-${index}`} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value, name) => [value, labelConcepto(name)]} />
                </PieChart>
              </ResponsiveContainer>
            </article>
            <article className="exam-chart-card exam-chart-tall exam-chart-wide">
              <h3><UserRound size={16} /> Exámenes por cargo</h3>
              <ResponsiveContainer width="100%" height={170}>
                <BarChart data={charts.por_cargo || []}>
                  <CartesianGrid vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </article>
          </div>

          <div className="exam-analytics-pro-grid">
            <article className="exam-chart-card exam-chart-wide exam-chart-tall">
              <h3><Activity size={16} /> Tendencia mensual de exámenes</h3>
              <ResponsiveContainer width="100%" height={180}>
                <LineChart data={tendenciaData}>
                  <CartesianGrid vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </article>
            <article className="exam-medical-risk-card">
              <h3><ShieldAlert size={16} /> Semáforo médico SST</h3>
              <div className={`exam-risk-pill exam-risk-${String(riesgoMedico).toLowerCase()}`}>{riesgoMedico}</div>
              <p>Cobertura: <b>{kpis.empleados_con_examen || 0}</b> de <b>{kpis.empleados_activos || 0}</b> empleados activos.</p>
              <p>Restricciones activas: <b>{kpis.con_restricciones || 0}</b></p>
              <p>No aptos: <b>{kpis.no_aptos || 0}</b></p>
            </article>
          </div>

          <section className="exam-table-card">
            <div className="exam-filter-top">
              <div className="exam-search">
                <Search size={17} />
                <input value={filters.q} onChange={(e) => setFilter("q", e.target.value)} placeholder="Buscar por empleado, documento, médico o entidad..." />
              </div>
              <button className="exam-btn-light" onClick={limpiarFiltros}><Filter size={16} /> Limpiar</button>
              <button className="exam-btn-light" onClick={cargarDatos}><RefreshCcw size={16} /> Actualizar</button>
            </div>

            <div className="exam-filters-grid">
              <select value={filters.empresa_id} onChange={(e) => setFilter("empresa_id", e.target.value)}>
                <option value="">Todas las empresas</option>
                {empresas.map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}
              </select>
              <select value={filters.sede_id} onChange={(e) => setFilter("sede_id", e.target.value)}>
                <option value="">Todas las sedes</option>
                {sedes.map((s) => <option key={s.id} value={s.id}>{s.nombre}</option>)}
              </select>
              <select value={filters.area_id} onChange={(e) => setFilter("area_id", e.target.value)}>
                <option value="">Todas las áreas</option>
                {areas.map((a) => <option key={a.id} value={a.id}>{a.nombre}</option>)}
              </select>
              <select value={filters.cargo_id} onChange={(e) => setFilter("cargo_id", e.target.value)}>
                <option value="">Todos los cargos</option>
                {cargos.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
              </select>
              <select value={filters.estado} onChange={(e) => setFilter("estado", e.target.value)}>
                <option value="">Todos los estados</option>
                <option value="VIGENTE">Vigente</option>
                <option value="PROXIMO_VENCER">Próximo a vencer</option>
                <option value="VENCIDO">Vencido</option>
              </select>
            </div>

            <div className="exam-filters-grid exam-filters-grid-small">
              <select value={filters.empleado_id} onChange={(e) => setFilter("empleado_id", e.target.value)}>
                <option value="">Todos los empleados</option>
                {empleados.map((e) => <option key={e.id} value={e.id}>{e.documento} · {e.nombres} {e.apellidos}</option>)}
              </select>
              <select value={filters.tipo_examen} onChange={(e) => setFilter("tipo_examen", e.target.value)}>
                <option value="">Todos los tipos</option>
                <option value="INGRESO">Ingreso</option>
                <option value="PERIODICO">Periódico</option>
                <option value="RETIRO">Retiro</option>
                <option value="POST_INCAPACIDAD">Post incapacidad</option>
                <option value="RETORNO_LABORAL">Retorno laboral</option>
              </select>
              <select value={filters.concepto} onChange={(e) => setFilter("concepto", e.target.value)}>
                <option value="">Todos los conceptos</option>
                <option value="APTO">Apto</option>
                <option value="APTO_CON_RESTRICCIONES">Apto con restricciones</option>
                <option value="NO_APTO">No apto</option>
              </select>
            </div>

            <div className="exam-table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Empleado</th>
                    <th>Empresa</th>
                    <th>Tipo</th>
                    <th>Concepto</th>
                    <th>Médico</th>
                    <th>Fecha</th>
                    <th>Vencimiento</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {paginated.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <div className="exam-person">
                          <span>{iniciales(item.empleado_nombre)}</span>
                          <div>
                            <b>{item.empleado_nombre || "Sin empleado"}</b>
                            <small>{item.empleado_documento || "Sin documento"}</small>
                          </div>
                        </div>
                      </td>
                      <td>{item.empresa_nombre || "Sin empresa"}<small>{item.sede_nombre || "Sin sede"}</small></td>
                      <td>{labelTipo(item.tipo_examen)}</td>
                      <td><span className={`exam-concept ${String(item.concepto || "").toLowerCase()}`}>{labelConcepto(item.concepto)}</span></td>
                      <td>{item.medico_ocupacional || "Sin médico"}<small>{item.entidad_salud || "Sin entidad"}</small></td>
                      <td>{item.fecha_examen}</td>
                      <td>{item.fecha_vencimiento || "Sin vencimiento"}<small>{item.dias_vencimiento !== null && item.dias_vencimiento !== undefined ? `${item.dias_vencimiento} días` : ""}</small></td>
                      <td><span className={`exam-status ${String(item.estado || "").toLowerCase()}`}>{labelEstado(item.estado)}</span></td>
                      <td>
                        <div className="exam-actions">
                          <button onClick={() => abrirVer(item)} title="Ver"><Eye size={15} /></button>
                          <button onClick={() => abrirHistorialEmpleado(item)} title="Historial del empleado"><History size={15} /></button>
                          <button onClick={() => abrirEditar(item)} title="Editar"><Edit3 size={15} /></button>
                          <button onClick={() => exportarFicha(item)} title="Ficha PDF"><Download size={15} /></button>
                          <button onClick={() => abrirEvidencias(item)} title="Evidencias"><Paperclip size={15} /></button>
                          <button onClick={() => eliminar(item)} title="Eliminar"><Trash2 size={15} /></button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {paginated.length === 0 && (
                    <tr><td className="exam-empty" colSpan="9">No hay exámenes médicos registrados.</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="exam-pagination">
              <span>Mostrando <b>{paginated.length}</b> de <b>{examenes.length}</b> registros</span>
              <div className="exam-page-controls">
                <label>Registros
                  <select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}>
                    <option value={10}>10</option>
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                  </select>
                </label>
                <button disabled={page === 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>‹</button>
                <span>Página {page} / {totalPages}</span>
                <button disabled={page === totalPages} onClick={() => setPage((p) => Math.min(totalPages, p + 1))}>›</button>
              </div>
            </div>
          </section>
        </div>

        <aside className={`exam-right-panel exam-right-panel-pro ${!sidebarVisible ? "exam-panel-hidden" : ""}`}>
          <article className="exam-intel-card exam-intel-pro">
            <div className="exam-side-title-row">
              <h3>Dashboard inteligente</h3>
              <span className="exam-ai-badge">AI</span>
              <div className="exam-sidebar-header-actions">
                <button
                  type="button"
                  className="exam-sidebar-toggle-btn"
                  onClick={() => setSidebarVisible((v) => !v)}
                  title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
                  aria-label={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
                  aria-pressed={!sidebarVisible}
                >
                  {sidebarVisible ? <Sidebar size={18} /> : <LayoutDashboard size={18} />}
                </button>
              </div>
            </div>
            <div className="exam-intel-body">
              <div className="exam-ring exam-ring-pro" style={{ "--exam-ring": `${Math.min(100, kpis.indice_cumplimiento ?? 100)}%` }}>
                <strong>{kpis.indice_cumplimiento ?? 100}%</strong>
                <span>Índice médico</span>
              </div>
              <div className="exam-intel-copy">
                <h4>{(kpis.pendientes_criticos || 0) > 0 ? "Gestión con pendientes" : "Gestión estable y óptima"}</h4>
                <p>Seguimiento de aptitud, restricciones, vencimientos y trazabilidad médica ocupacional.</p>
                <em className={(kpis.pendientes_criticos || 0) > 0 ? "warn" : "ok"}>{(kpis.pendientes_criticos || 0) > 0 ? "Revisar" : "Excelente"}</em>
              </div>
            </div>
            <div className="exam-intel-mini-stats">
              <div><HeartPulse size={18} /><span>Total</span><b>{kpis.total || 0}</b></div>
              <div><CheckCircle2 size={18} /><span>Vigentes</span><b>{kpis.vigentes || 0}</b></div>
              <div><ShieldAlert size={18} /><span>Restric.</span><b>{kpis.con_restricciones || 0}</b></div>
              <div><AlertTriangle size={18} /><span>Críticos</span><b>{kpis.pendientes_criticos || 0}</b></div>
            </div>
          </article>

          <article className="exam-side-card exam-alert-card">
            <div className="exam-side-title-row">
              <h3><AlertTriangle size={18} /> Alertas médicas</h3>
              <b className={(kpis.pendientes_criticos || 0) > 0 ? "warn" : ""}>{kpis.pendientes_criticos || 0} críticas</b>
            </div>
            <div className="exam-alert-list">
              <div className="exam-alert-row exam-alert-red">
                <span><CalendarClock size={18} /></span>
                <div><b>Vencen en 7 días</b><small>Intervención inmediata</small></div>
                <strong>{alertas.vencen_7 || 0}</strong>
                <em className={(alertas.vencen_7 || 0) > 0 ? "warn" : "ok"}>{(alertas.vencen_7 || 0) > 0 ? "Urgente" : "Óptimo"}</em>
              </div>
              <div className="exam-alert-row exam-alert-yellow">
                <span><CalendarClock size={18} /></span>
                <div><b>Vencen en 15 días</b><small>Programación prioritaria</small></div>
                <strong>{alertas.vencen_15 || 0}</strong>
                <em className={(alertas.vencen_15 || 0) > 0 ? "warn" : "ok"}>{(alertas.vencen_15 || 0) > 0 ? "Agendar" : "Óptimo"}</em>
              </div>
              <div className="exam-alert-row exam-alert-yellow">
                <span><CalendarClock size={18} /></span>
                <div><b>Próximos a vencer</b><small>Seguimiento preventivo</small></div>
                <strong>{alertas.proximos_vencer || 0}</strong>
                <em className={(alertas.proximos_vencer || 0) > 0 ? "warn" : "ok"}>{(alertas.proximos_vencer || 0) > 0 ? "Revisar" : "Óptimo"}</em>
              </div>
              <div className="exam-alert-row exam-alert-red">
                <span><AlertTriangle size={18} /></span>
                <div><b>Vencidos</b><small>Exámenes fuera de vigencia</small></div>
                <strong>{alertas.vencidos || 0}</strong>
                <em className={(alertas.vencidos || 0) > 0 ? "warn" : "ok"}>{(alertas.vencidos || 0) > 0 ? "Crítico" : "Óptimo"}</em>
              </div>
              <div className="exam-alert-row exam-alert-purple">
                <span><ShieldAlert size={18} /></span>
                <div><b>Con restricciones</b><small>Conceptos con seguimiento</small></div>
                <strong>{alertas.con_restricciones || 0}</strong>
                <em className={(alertas.con_restricciones || 0) > 0 ? "warn" : "ok"}>{(alertas.con_restricciones || 0) > 0 ? "Gestionar" : "Óptimo"}</em>
              </div>
              <div className="exam-alert-row exam-alert-blue">
                <span><HeartPulse size={18} /></span>
                <div><b>No aptos</b><small>Casos de atención prioritaria</small></div>
                <strong>{alertas.no_aptos || 0}</strong>
                <em className={(alertas.no_aptos || 0) > 0 ? "warn" : "ok"}>{(alertas.no_aptos || 0) > 0 ? "Crítico" : "Óptimo"}</em>
              </div>
            </div>
          </article>

          <article className="exam-side-card exam-alert-timeline-card">
            <div className="exam-side-title-row">
              <h3><CalendarClock size={18} /> Vencimientos críticos</h3>
              <span className="exam-detail-badge">30 días</span>
            </div>
            <div className="exam-alert-timeline">
              {alertaTimeline.length === 0 ? (
                <p className="exam-timeline-empty">Sin vencimientos críticos en los próximos 30 días.</p>
              ) : alertaTimeline.map((row) => (
                <div className={`exam-timeline-row ${Number(row.dias_vencimiento) <= 7 ? "danger" : "warn"}`} key={`alerta-${row.id}`}>
                  <span>{row.dias_vencimiento}d</span>
                  <div>
                    <b>{row.empleado}</b>
                    <small>{labelTipo(row.tipo_examen)} · {row.fecha_vencimiento}</small>
                  </div>
                </div>
              ))}
            </div>
          </article>

          <article className="exam-side-card exam-distribution-card">
            <div className="exam-side-title-row">
              <h3><Activity size={18} /> Distribución base</h3>
              <span className="exam-detail-badge">Ver detalle</span>
            </div>
            <div className="exam-distribution-pro">
              {[
                { label: "Cobertura", value: kpis.empleados_con_examen || 0, total: kpis.empleados_activos || 0, tone: "blue", icon: UserRound },
                { label: "Vigentes", value: kpis.vigentes || 0, total: kpis.total || 0, tone: "green", icon: CheckCircle2 },
                { label: "Aptos", value: kpis.aptos || 0, total: kpis.total || 0, tone: "blue", icon: HeartPulse },
                { label: "Restricciones", value: kpis.con_restricciones || 0, total: kpis.total || 0, tone: "purple", icon: ShieldAlert },
                { label: "No aptos", value: kpis.no_aptos || 0, total: kpis.total || 0, tone: "red", icon: AlertTriangle },
              ].map((row) => {
                const Icon = row.icon;
                const percent = row.total ? Math.round((row.value / row.total) * 100) : 0;
                return (
                  <div className={`exam-dist-row exam-dist-${row.tone}`} key={row.label}>
                    <span className="exam-dist-icon"><Icon size={18} /></span>
                    <div className="exam-dist-main">
                      <div><b>{row.label}</b><strong>{row.value}</strong><em>{percent}%</em></div>
                      <div className="exam-dist-track"><span style={{ width: `${Math.max(row.value > 0 ? 8 : 0, percent)}%` }} /></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </article>

          <article className="exam-side-card exam-rec-card">
            <div className="exam-side-title-row">
              <h3><CheckCircle2 size={18} /> Recomendaciones PRO</h3>
              <span className="exam-pro-badge">PRO</span>
            </div>
            <div className="exam-rec-list">
              {(recomendaciones.length ? recomendaciones : [
                "Gestión médica ocupacional estable. Mantén seguimiento periódico.",
                "Actualiza vencimientos y conceptos médicos después de cada valoración.",
                "Controla restricciones médicas con trazabilidad por empleado.",
              ]).slice(0, 4).map((rec, index) => (
                <div className={`exam-rec-row exam-rec-${["blue", "purple", "green", "orange"][index % 4]}`} key={`rec-${index}`}>
                  <span>{index + 1}</span>
                  <div><b>{index === 0 ? "Seguimiento médico" : index === 1 ? "Actualización periódica" : index === 2 ? "Restricciones" : "Auditoría SST"}</b><small>{rec}</small></div>
                </div>
              ))}
            </div>
          </article>
        </aside>
      </section>

      {modal.open && (
        <ExamenModal
          modo={modal.modo}
          form={form}
          setForm={setForm}
          empleados={empleados}
          examCatalogo={examCatalogo}
          selected={modal.item}
          onClose={cerrarModal}
          onSubmit={guardar}
        />
      )}

      {evidenciasModal.open && (
        <EvidenciasModal
          examen={evidenciasModal.item}
          evidencias={evidencias}
          file={evidenciaFile}
          setFile={setEvidenciaFile}
          descripcion={evidenciaDescripcion}
          setDescripcion={setEvidenciaDescripcion}
          tipoEvidencia={tipoEvidencia}
          setTipoEvidencia={setTipoEvidencia}
          uploading={uploading}
          onClose={cerrarEvidencias}
          onUpload={subirEvidencia}
          onDelete={eliminarEvidencia}
          onOpen={abrirArchivoSST}
          onPreview={setPreviewArchivo}
        />
      )}

      {previewArchivo && (
        <VisorEvidenciaModal
          archivo={previewArchivo}
          onClose={() => setPreviewArchivo(null)}
          onOpen={abrirArchivoSST}
        />
      )}

      {/* ============================================================
          FASE 37.2.2.B — MODAL GLOBAL DE ELIMINACIÓN INTELIGENTE
          IMPORTANTE PARA PRÓXIMOS MÓDULOS:
          Este render es obligatorio.
          Si se llama smartDelete.open(registro) pero NO se renderiza
          {smartDelete.modal}, el botón eliminar parece no hacer nada.
          ============================================================ */}
      {smartDelete.modal}

      {saving && <div className="exam-saving">Guardando examen médico...</div>}

      {historialModal.open && historialModal.empleado && (
        <div className="exam-modal-backdrop" onClick={cerrarHistorialModal}>
          <div className="exam-modal exam-modal-lg" onClick={(e) => e.stopPropagation()}>
            <header className="exam-modal-header">
              <div>
                <h2><History size={20} style={{ marginRight: 8 }} />Historial de Exámenes — Resolución 1843/2025</h2>
                <p style={{ margin: "4px 0 0", color: "#64748b" }}>
                  {historialModal.empleado.empleado_nombre} · {historialModal.empleado.empleado_documento} · {historialModal.empleado.cargo_nombre || "Sin cargo"}
                </p>
              </div>
              <button className="exam-close" onClick={cerrarHistorialModal}><X size={21} /></button>
            </header>
            <div className="exam-modal-body" style={{ maxHeight: "60vh", overflowY: "auto" }}>
              {historialModal.examenes.length === 0 ? (
                <p className="exam-empty" style={{ textAlign: "center", padding: 40, color: "#94a3b8" }}>
                  No hay exámenes registrados para este empleado.
                </p>
              ) : (
                <>
                  {TIPOS_EVAL_1843.map((tipo) => {
                    const examenesTipo = historialModal.examenes.filter((e) => e.tipo_examen === tipo.codigo);
                    if (examenesTipo.length === 0) return null;
                    return (
                      <div key={tipo.codigo} className="historial-tipo-group">
                        <div className="historial-tipo-header">
                          <h4 style={{ margin: 0, display: "flex", alignItems: "center", gap: 8 }}>
                            <span style={{ fontSize: 18 }}>{tipo.icon}</span>
                            {tipo.nombre}
                          </h4>
                          <span className="exam-count">{examenesTipo.length} examen{examenesTipo.length > 1 ? "es" : ""}</span>
                        </div>
                        <div className="historial-examenes-list">
                          {examenesTipo.map((ex) => (
                            <article key={ex.id} className="historial-examen-card">
                              <div className="historial-examen-main">
                                <div>
                                  <strong>{labelConcepto(ex.concepto)}</strong>
                                  <span className={`exam-concept-badge ${String(ex.concepto || "").toLowerCase()}`}>{labelConcepto(ex.concepto)}</span>
                                </div>
                                <div className="historial-examen-meta">
                                  <span>📅 {ex.fecha_examen}</span>
                                  <span>🏥 {ex.medico_ocupacional || "Sin médico"}</span>
                                  <span>🏢 {ex.entidad_salud || "Sin entidad"}</span>
                                  {ex.fecha_vencimiento && <span>⏳ Vence: {ex.fecha_vencimiento}</span>}
                                  <span className={`exam-status ${String(ex.estado || "").toLowerCase()}`}>{labelEstado(ex.estado)}</span>
                                </div>
                              </div>
                              {(ex.restricciones || ex.observaciones) && (
                                <div className="historial-examen-detalle">
                                  {ex.restricciones && <p><b>Restricciones:</b> {ex.restricciones}</p>}
                                  {ex.observaciones && <p><b>Observaciones:</b> {ex.observaciones}</p>}
                                </div>
                              )}
                              {ex.examenes_aplicados && ex.examenes_aplicados.length > 0 && (
                                <div className="historial-examen-detalle">
                                  <p><b>Exámenes realizados:</b></p>
                                  <div className="exam-aplicados-list">
                                    {ex.examenes_aplicados.map((ea, idx) => (
                                      <span key={ea.id || idx} className="exam-aplicado-chip">{ea.nombre || ea.codigo}</span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </article>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                  {historialModal.examenes.length > 0 && historialModal.examenes.filter(e => !TIPOS_EVAL_1843.find(t => t.codigo === e.tipo_examen)).length > 0 && (
                    <div className="historial-tipo-group">
                      <div className="historial-tipo-header">
                        <h4 style={{ margin: 0, display: "flex", alignItems: "center", gap: 8 }}>📋 Otros</h4>
                        <span className="exam-count">
                          {historialModal.examenes.filter(e => !TIPOS_EVAL_1843.find(t => t.codigo === e.tipo_examen)).length} examen{historialModal.examenes.filter(e => !TIPOS_EVAL_1843.find(t => t.codigo === e.tipo_examen)).length > 1 ? "es" : ""}
                        </span>
                      </div>
                      <div className="historial-examenes-list">
                        {historialModal.examenes.filter(e => !TIPOS_EVAL_1843.find(t => t.codigo === e.tipo_examen)).map((ex) => (
                          <article key={ex.id} className="historial-examen-card">
                            <div className="historial-examen-main">
                              <div>
                                <strong>{labelTipo(ex.tipo_examen)}</strong>
                                <span className={`exam-concept-badge ${String(ex.concepto || "").toLowerCase()}`}>{labelConcepto(ex.concepto)}</span>
                              </div>
                              <div className="historial-examen-meta">
                                <span>📅 {ex.fecha_examen}</span>
                                <span>🏥 {ex.medico_ocupacional || "Sin médico"}</span>
                                <span>🏢 {ex.entidad_salud || "Sin entidad"}</span>
                                {ex.fecha_vencimiento && <span>⏳ Vence: {ex.fecha_vencimiento}</span>}
                                <span className={`exam-status ${String(ex.estado || "").toLowerCase()}`}>{labelEstado(ex.estado)}</span>
                              </div>
                            </div>
                            {(ex.restricciones || ex.observaciones) && (
                              <div className="historial-examen-detalle">
                                {ex.restricciones && <p><b>Restricciones:</b> {ex.restricciones}</p>}
                                {ex.observaciones && <p><b>Observaciones:</b> {ex.observaciones}</p>}
                              </div>
                            )}
                            {ex.examenes_aplicados && ex.examenes_aplicados.length > 0 && (
                              <div className="historial-examen-detalle">
                                <p><b>Exámenes realizados:</b></p>
                                <div className="exam-aplicados-list">
                                  {ex.examenes_aplicados.map((ea, idx) => (
                                    <span key={ea.id || idx} className="exam-aplicado-chip">{ea.nombre || ea.codigo}</span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </article>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
            <footer className="exam-modal-footer">
              <button className="exam-btn-secondary" onClick={cerrarHistorialModal}>Cerrar</button>
            </footer>
          </div>
        </div>
      )}
    </main>
  );
}
