import { useState, useEffect } from "react";
import {
  listarTiposEvaluacion,
  crearTipoEvaluacion,
  actualizarTipoEvaluacion,
  eliminarTipoEvaluacion,
  listarExamenesCatalogo,
  crearExamenCatalogo,
  actualizarExamenCatalogo,
  eliminarExamenCatalogo,
  listarProfesiogramas,
  obtenerProfesiograma,
  eliminarProfesiograma,
} from "../../api/profesiogramaApi";
import { listarCargosSST } from "../../api/cargoSstApi";
import { listarEmpresasParaCargosSST } from "../../api/cargoSstApi";
import { Eye, Pencil, Trash2, Plus, X, ClipboardList } from "lucide-react";
import "../../styles/profesiograma.css";

const RIESGOS_OPCIONES = [
  "Radiación ionizante",
  "Biológico",
  "Biomecánico",
  "Psicosocial",
  "Exigencia visual",
  "Químico",
  "Físico",
  "Eléctrico",
  "Altura",
  "Espacios confinados",
];

export default function ProfesiogramaPage() {
  const [tipos, setTipos] = useState([]);
  const [examenes, setExamenes] = useState([]);
  const [profesiogramas, setProfesiogramas] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [empresaFilter, setEmpresaFilter] = useState("");
  const [loading, setLoading] = useState(false);
  const [modalTipo, setModalTipo] = useState(null);
  const [modalExamen, setModalExamen] = useState(null);
  const [modalDetalle, setModalDetalle] = useState(null);
  const [formTipo, setFormTipo] = useState({ codigo: "", nombre: "", descripcion: "" });
  const [formExamen, setFormExamen] = useState({ codigo: "", nombre: "", descripcion: "" });

  useEffect(() => {
    cargarDatos();
  }, []);

  useEffect(() => {
    cargarProfesiogramas();
  }, [empresaFilter]);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const [t, e, emp] = await Promise.all([
        listarTiposEvaluacion(),
        listarExamenesCatalogo(),
        listarEmpresasParaCargosSST(),
      ]);
      setTipos(t);
      setExamenes(e);
      setEmpresas(Array.isArray(emp) ? emp : []);
      await cargarProfesiogramas();
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const cargarProfesiogramas = async () => {
    try {
      const params = {};
      if (empresaFilter) params.empresa_id = empresaFilter;
      const data = await listarProfesiogramas(params);
      setProfesiogramas(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error(error);
    }
  };

  const guardarTipo = async () => {
    if (!formTipo.codigo || !formTipo.nombre) {
      alert("Código y nombre son obligatorios");
      return;
    }
    try {
      if (modalTipo?.id) {
        await actualizarTipoEvaluacion(modalTipo.id, formTipo);
      } else {
        await crearTipoEvaluacion(formTipo);
      }
      setModalTipo(null);
      setFormTipo({ codigo: "", nombre: "", descripcion: "" });
      const data = await listarTiposEvaluacion();
      setTipos(data);
    } catch (error) {
      alert(error.response?.data?.detail || "Error al guardar");
    }
  };

  const guardarExamen = async () => {
    if (!formExamen.codigo || !formExamen.nombre) {
      alert("Código y nombre son obligatorios");
      return;
    }
    try {
      if (modalExamen?.id) {
        await actualizarExamenCatalogo(modalExamen.id, formExamen);
      } else {
        await crearExamenCatalogo(formExamen);
      }
      setModalExamen(null);
      setFormExamen({ codigo: "", nombre: "", descripcion: "" });
      const data = await listarExamenesCatalogo();
      setExamenes(data);
    } catch (error) {
      alert(error.response?.data?.detail || "Error al guardar");
    }
  };

  const handleEliminarTipo = async (id) => {
    if (!confirm("¿Inactivar este tipo de evaluación?")) return;
    await eliminarTipoEvaluacion(id);
    const data = await listarTiposEvaluacion();
    setTipos(data);
  };

  const handleEliminarExamen = async (id) => {
    if (!confirm("¿Inactivar este examen del catálogo?")) return;
    await eliminarExamenCatalogo(id);
    const data = await listarExamenesCatalogo();
    setExamenes(data);
  };

  const handleEliminarProfesiograma = async (id) => {
    if (!confirm("¿Eliminar este profesiograma?")) return;
    await eliminarProfesiograma(id);
    cargarProfesiogramas();
  };

  const verDetalle = async (cargoId) => {
    try {
      const data = await obtenerProfesiograma(cargoId);
      setModalDetalle(data);
    } catch (error) {
      alert("No se encontró profesiograma para este cargo");
    }
  };

  const parseJSON = (str) => {
    try { return JSON.parse(str); } catch { return []; }
  };

  return (
    <div className="profesiograma-page">
      <div className="profesiograma-hero">
        <div>
          <h1><ClipboardList size={22} style={{ marginRight: 8, verticalAlign: "middle" }} />Profesiograma / Evaluaciones Médicas</h1>
          <p>Resolución 1843 de 2025 — Vigilancia médica ocupacional por cargo</p>
        </div>
        <div className="prof-hero-actions">
          <button className="prof-btn prof-btn-secondary" onClick={() => setModalTipo({})}>+ Tipo Evaluación</button>
          <button className="prof-btn prof-btn-secondary" onClick={() => setModalExamen({})}>+ Examen Catálogo</button>
        </div>
      </div>

      {/* KPIs */}
      <div className="prof-kpi-grid">
        <div className="prof-kpi">
          <div className="prof-kpi-value">{tipos.filter(t => t.activo).length}</div>
          <div className="prof-kpi-label">Tipos de Evaluación</div>
        </div>
        <div className="prof-kpi">
          <div className="prof-kpi-value">{examenes.filter(e => e.activo).length}</div>
          <div className="prof-kpi-label">Exámenes en Catálogo</div>
        </div>
        <div className="prof-kpi">
          <div className="prof-kpi-value">{profesiogramas.length}</div>
          <div className="prof-kpi-label">Profesiogramas Activos</div>
        </div>
      </div>

      <div className="prof-layout">
        <div className="prof-main">
          {/* Profesiogramas */}
          <div className="prof-card">
            <div className="prof-card-header">
              <h3>Profesiogramas Registrados</h3>
              <select className="prof-form-select" style={{ width: 200 }} value={empresaFilter} onChange={(e) => setEmpresaFilter(e.target.value)}>
                <option value="">Todas las empresas</option>
                {empresas.map((emp) => (
                  <option key={emp.id} value={emp.id}>{emp.nombre}</option>
                ))}
              </select>
            </div>
            <div className="prof-table-wrap">
              <table className="prof-table">
                <thead>
                  <tr>
                    <th>Cargo</th>
                    <th>Empresa</th>
                    <th>Riesgos</th>
                    <th>Evaluaciones</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {profesiogramas.length === 0 ? (
                    <tr><td colSpan={6} style={{ textAlign: "center", padding: 30, color: "#94a3b8" }}>No hay profesiogramas registrados</td></tr>
                  ) : profesiogramas.map((prof) => (
                    <tr key={prof.id}>
                      <td><b>{prof.cargo_nombre || `Cargo #${prof.cargo_id}`}</b></td>
                      <td>{prof.empresa_nombre || "-"}</td>
                      <td>{parseJSON(prof.riesgos_asociados).length} riesgos</td>
                      <td>{prof.evaluaciones?.length || 0} tipos</td>
                      <td><span className={`prof-pill ${prof.activo ? "prof-pill-active" : "prof-pill-inactive"}`}>{prof.activo ? "Activo" : "Inactivo"}</span></td>
                      <td className="actions">
                        <button className="prof-icon-btn" title="Ver detalle" onClick={() => verDetalle(prof.cargo_id)}><Eye size={14} /></button>
                        <button className="prof-icon-btn danger" title="Eliminar" onClick={() => handleEliminarProfesiograma(prof.id)}><Trash2 size={14} /></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Sidebar: Catálogos */}
        <div className="prof-sidebar">
          {/* Tipos de evaluación */}
          <div className="prof-card">
            <div className="prof-card-header">
              <h3>Tipos de Evaluación</h3>
              <button className="prof-btn prof-btn-outline prof-btn-sm" onClick={() => setModalTipo({})}>+ Nuevo</button>
            </div>
            <div className="prof-card-body">
              {tipos.length === 0 ? (
                <p className="prof-empty">No hay tipos registrados</p>
              ) : tipos.map((t) => (
                <div key={t.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "6px 0", borderBottom: "1px solid #f1f5f9" }}>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "#1e293b" }}>{t.nombre}</div>
                    <div style={{ fontSize: 11, color: "#94a3b8" }}>{t.codigo}</div>
                  </div>
                  <div className="actions">
                    <button className="prof-icon-btn" onClick={() => { setModalTipo(t); setFormTipo({ codigo: t.codigo, nombre: t.nombre, descripcion: t.descripcion || "" }); }}><Pencil size={12} /></button>
                    <button className="prof-icon-btn danger" onClick={() => handleEliminarTipo(t.id)}><Trash2 size={12} /></button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Catálogo de exámenes */}
          <div className="prof-card">
            <div className="prof-card-header">
              <h3>Catálogo de Exámenes</h3>
              <button className="prof-btn prof-btn-outline prof-btn-sm" onClick={() => setModalExamen({})}>+ Nuevo</button>
            </div>
            <div className="prof-card-body" style={{ maxHeight: 400, overflowY: "auto" }}>
              {examenes.length === 0 ? (
                <p className="prof-empty">No hay exámenes registrados</p>
              ) : examenes.map((e) => (
                <div key={e.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "6px 0", borderBottom: "1px solid #f1f5f9" }}>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "#1e293b" }}>{e.nombre}</div>
                    <div style={{ fontSize: 11, color: "#94a3b8" }}>{e.codigo}</div>
                  </div>
                  <div className="actions">
                    <button className="prof-icon-btn" onClick={() => { setModalExamen(e); setFormExamen({ codigo: e.codigo, nombre: e.nombre, descripcion: e.descripcion || "" }); }}><Pencil size={12} /></button>
                    <button className="prof-icon-btn danger" onClick={() => handleEliminarExamen(e.id)}><Trash2 size={12} /></button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Modal Tipo Evaluación */}
      {modalTipo && (
        <div className="prof-modal-backdrop" onClick={() => setModalTipo(null)}>
          <div className="prof-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 450 }}>
            <div className="prof-modal-header">
              <h2>{modalTipo.id ? "Editar" : "Nuevo"} Tipo de Evaluación</h2>
              <button className="prof-modal-close" onClick={() => setModalTipo(null)}><X size={18} /></button>
            </div>
            <div className="prof-modal-body">
              <div className="prof-form-group">
                <label>Código</label>
                <input className="prof-form-input" value={formTipo.codigo} onChange={(e) => setFormTipo({ ...formTipo, codigo: e.target.value })} placeholder="PRE_INGRESO" />
              </div>
              <div className="prof-form-group">
                <label>Nombre</label>
                <input className="prof-form-input" value={formTipo.nombre} onChange={(e) => setFormTipo({ ...formTipo, nombre: e.target.value })} placeholder="Pre-Ingreso" />
              </div>
              <div className="prof-form-group">
                <label>Descripción</label>
                <textarea className="prof-form-input" rows={3} value={formTipo.descripcion} onChange={(e) => setFormTipo({ ...formTipo, descripcion: e.target.value })} />
              </div>
            </div>
            <div className="prof-modal-footer">
              <button className="prof-btn prof-btn-outline" onClick={() => setModalTipo(null)}>Cancelar</button>
              <button className="prof-btn prof-btn-primary" onClick={guardarTipo}>Guardar</button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Examen Catálogo */}
      {modalExamen && (
        <div className="prof-modal-backdrop" onClick={() => setModalExamen(null)}>
          <div className="prof-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 450 }}>
            <div className="prof-modal-header">
              <h2>{modalExamen.id ? "Editar" : "Nuevo"} Examen del Catálogo</h2>
              <button className="prof-modal-close" onClick={() => setModalExamen(null)}><X size={18} /></button>
            </div>
            <div className="prof-modal-body">
              <div className="prof-form-group">
                <label>Código</label>
                <input className="prof-form-input" value={formExamen.codigo} onChange={(e) => setFormExamen({ ...formExamen, codigo: e.target.value })} placeholder="VISIOMETRIA" />
              </div>
              <div className="prof-form-group">
                <label>Nombre</label>
                <input className="prof-form-input" value={formExamen.nombre} onChange={(e) => setFormExamen({ ...formExamen, nombre: e.target.value })} placeholder="Visiometría / Optometría" />
              </div>
              <div className="prof-form-group">
                <label>Descripción</label>
                <textarea className="prof-form-input" rows={3} value={formExamen.descripcion} onChange={(e) => setFormExamen({ ...formExamen, descripcion: e.target.value })} />
              </div>
            </div>
            <div className="prof-modal-footer">
              <button className="prof-btn prof-btn-outline" onClick={() => setModalExamen(null)}>Cancelar</button>
              <button className="prof-btn prof-btn-primary" onClick={guardarExamen}>Guardar</button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Detalle Profesiograma */}
      {modalDetalle && (
        <div className="prof-modal-backdrop" onClick={() => setModalDetalle(null)}>
          <div className="prof-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 650 }}>
            <div className="prof-modal-header">
              <h2>Profesiograma del Cargo</h2>
              <button className="prof-modal-close" onClick={() => setModalDetalle(null)}><X size={18} /></button>
            </div>
            <div className="prof-modal-body">
              <div className="prof-detail-field">
                <label>Cargo</label>
                <div style={{ fontSize: 15, fontWeight: 700, color: "#1e293b" }}>{modalDetalle.cargo_nombre || `Cargo #${modalDetalle.cargo_id}`}</div>
              </div>

              <div className="prof-detail-field">
                <label>Riesgos Asociados</label>
                <div className="prof-risk-tags">
                  {parseJSON(modalDetalle.riesgos_asociados).map((r, i) => (
                    <span key={i} className="prof-risk-tag selected">{r}</span>
                  ))}
                  {parseJSON(modalDetalle.riesgos_asociados).length === 0 && (
                    <span style={{ fontSize: 12, color: "#94a3b8" }}>Sin riesgos configurados</span>
                  )}
                </div>
              </div>

              <div className="prof-detail-field">
                <label>Evaluaciones Médicas</label>
                {modalDetalle.evaluaciones?.length === 0 ? (
                  <p style={{ fontSize: 12, color: "#94a3b8" }}>Sin evaluaciones configuradas</p>
                ) : modalDetalle.evaluaciones?.map((ev) => (
                  <div key={ev.id} className="prof-eval-group">
                    <div className="prof-eval-group-header">
                      <h5>{ev.tipo_evaluacion_nombre || `Tipo #${ev.tipo_evaluacion_id}`}</h5>
                      <span className="prof-pill prof-pill-active">{parseJSON(ev.examenes_requeridos).length} exámenes</span>
                    </div>
                    <div className="prof-eval-group-body">
                      {parseJSON(ev.examenes_requeridos).map((exId) => {
                        const examen = examenes.find((e) => e.id === exId);
                        return (
                          <span key={exId} className="prof-check-item checked">
                            {examen?.nombre || `Examen #${exId}`}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="prof-modal-footer">
              <button className="prof-btn prof-btn-outline" onClick={() => setModalDetalle(null)}>Cerrar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
