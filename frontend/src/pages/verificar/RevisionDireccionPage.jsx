// ============================================================
// REVISIÓN POR LA DIRECCIÓN SST ENTERPRISE PRO
// FASE 1.8.4.3.8 - Integración Historial Documental
// Archivo: frontend/src/pages/verificar/RevisionDireccionPage.jsx
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  BarChart3,
  CalendarDays,
  CheckCircle2,
  ClipboardCheck,
  ClipboardList,
  Download,
  Edit3,
  FileText,
  Gauge,
  History,
  Layers3,
  Plus,
  RefreshCcw,
  Save,
  ShieldCheck,
  Trash2,
  Users,
  X,
} from "lucide-react";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Cell,
} from "recharts";

import AdminLayout from "../../layouts/AdminLayout";

import {
  actualizarCompromisoRevision,
  actualizarRevisionDireccion,
  cambiarEstadoRevision,
  crearCompromisoRevision,
  crearRevisionDireccion,
  eliminarCompromisoRevision,
  eliminarRevisionDireccion,
  exportarPdfRevisionDireccion,
  listarRevisionesDireccion,
  obtenerDashboardRevisionDireccion,
} from "../../api/revisionDireccionApi";

import "../../styles/revision-direccion.css";

const ESTADOS = ["BORRADOR", "APROBADA", "CERRADA", "ANULADA"];
const PRIORIDADES = ["BAJA", "MEDIA", "ALTA", "CRITICA"];

const emptyForm = {
  empresa_id: 1,
  titulo: "",
  fecha_revision: "",
  periodo_evaluado: "",
  gerente: "",
  responsable_sst: "",
  participantes: "",
  objetivo: "",
  alcance: "",
  agenda: "",
  resumen_auditorias: "",
  resumen_indicadores: "",
  resumen_planes_mejora: "",
  resumen_accidentes: "",
  resumen_capacitaciones: "",
  resumen_cumplimiento_legal: "",
  conclusiones: "",
  decisiones: "",
  recomendaciones: "",
};

const emptyCompromiso = {
  compromiso: "",
  responsable: "",
  fecha_compromiso: "",
  prioridad: "MEDIA",
  observaciones: "",
};

function fmtDate(value) {
  if (!value) return "Sin fecha";
  return new Date(`${value}T00:00:00`).toLocaleDateString("es-CO");
}

function estadoClass(estado) {
  return String(estado || "").toLowerCase();
}

export default function RevisionDireccionPage() {
  const navigate = useNavigate();
  let rolUsuario = "";
  try {
    rolUsuario = String(JSON.parse(localStorage.getItem("user") || "{}")?.rol || "").toUpperCase();
  } catch {
    rolUsuario = "";
  }
  const puedeEditar = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST"].includes(rolUsuario);
  const puedeAprobar = ["SUPER_ADMIN", "ADMIN_EMPRESA", "ALTA_DIRECCION", "REPRESENTANTE_LEGAL"].includes(rolUsuario);
  const puedeEliminar = ["SUPER_ADMIN", "ADMIN_EMPRESA"].includes(rolUsuario);

  const [dashboard, setDashboard] = useState(null);
  const [revisiones, setRevisiones] = useState([]);
  const [selected, setSelected] = useState(null);

  const [form, setForm] = useState(emptyForm);
  const [compromisoForm, setCompromisoForm] = useState(emptyCompromiso);

  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [exportingPdf, setExportingPdf] = useState(false);

  const [error, setError] = useState("");
  const [ok, setOk] = useState("");

  const cargarDatos = async () => {
    try {
      setLoading(true);
      setError("");

      const [dash, lista] = await Promise.all([
        obtenerDashboardRevisionDireccion(),
        listarRevisionesDireccion(),
      ]);

      setDashboard(dash);
      setRevisiones(lista);

      if (!selected && lista.length > 0) {
        setSelected(lista[0]);
      }
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.userMessage ||
          "No fue posible cargar la revisión por la dirección. Intente nuevamente."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const estadosChart = useMemo(
    () => [
      { name: "Borrador", value: dashboard?.borradores || 0 },
      { name: "Aprobadas", value: dashboard?.aprobadas || 0 },
      { name: "Cerradas", value: dashboard?.cerradas || 0 },
    ],
    [dashboard]
  );

  const compromisosChart = useMemo(
    () => [
      { name: "Pendientes", value: dashboard?.compromisos_pendientes || 0 },
      { name: "Cerrados", value: dashboard?.compromisos_cerrados || 0 },
    ],
    [dashboard]
  );

  const abrirNuevaRevision = () => {
    setForm({
      ...emptyForm,
      fecha_revision: new Date().toISOString().slice(0, 10),
    });
    setSelected(null);
    setShowForm(true);
    setError("");
    setOk("");
  };

  const abrirEditarRevision = (revision) => {
    setForm({
      empresa_id: revision.empresa_id,
      titulo: revision.titulo || "",
      fecha_revision: revision.fecha_revision || "",
      periodo_evaluado: revision.periodo_evaluado || "",
      gerente: revision.gerente || "",
      responsable_sst: revision.responsable_sst || "",
      participantes: revision.participantes || "",
      objetivo: revision.objetivo || "",
      alcance: revision.alcance || "",
      agenda: revision.agenda || "",
      resumen_auditorias: revision.resumen_auditorias || "",
      resumen_indicadores: revision.resumen_indicadores || "",
      resumen_planes_mejora: revision.resumen_planes_mejora || "",
      resumen_accidentes: revision.resumen_accidentes || "",
      resumen_capacitaciones: revision.resumen_capacitaciones || "",
      resumen_cumplimiento_legal: revision.resumen_cumplimiento_legal || "",
      conclusiones: revision.conclusiones || "",
      decisiones: revision.decisiones || "",
      recomendaciones: revision.recomendaciones || "",
    });

    setSelected(revision);
    setShowForm(true);
    setError("");
    setOk("");
  };

  const guardarRevision = async (e) => {
    e.preventDefault();

    if (!form.empresa_id || !form.titulo || !form.fecha_revision) {
      setError("Empresa, título y fecha de revisión son obligatorios.");
      return;
    }

    try {
      setSaving(true);
      setError("");
      setOk("");

      if (selected?.id) {
        const actualizada = await actualizarRevisionDireccion(selected.id, form);
        setSelected(actualizada);
        setOk("Revisión actualizada correctamente.");
      } else {
        const creada = await crearRevisionDireccion(form);
        setSelected(creada);
        setOk("Revisión creada correctamente.");
      }

      setShowForm(false);
      await cargarDatos();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "No fue posible guardar la revisión por la dirección."
      );
    } finally {
      setSaving(false);
    }
  };

  const cambiarEstado = async (revision, estado) => {
    try {
      setError("");
      await cambiarEstadoRevision(revision.id, estado);
      setOk(`Estado cambiado a ${estado}.`);
      await cargarDatos();
    } catch (err) {
      setError(
        err?.response?.data?.detail || "No fue posible cambiar el estado."
      );
    }
  };

  const eliminarRevision = async (revision) => {
    if (!window.confirm(`¿Eliminar la revisión ${revision.codigo}?`)) return;

    try {
      setError("");
      await eliminarRevisionDireccion(revision.id);
      setSelected(null);
      setOk("Revisión eliminada correctamente.");
      await cargarDatos();
    } catch (err) {
      setError(
        err?.response?.data?.detail || "No fue posible eliminar la revisión."
      );
    }
  };

  const exportarActaPdf = async (revision) => {
    if (!revision?.id) {
      setError("Seleccione una revisión antes de exportar el PDF.");
      return;
    }

    try {
      setExportingPdf(true);
      setError("");
      setOk("");

      await exportarPdfRevisionDireccion(revision.id);

      setOk("Acta PDF generada correctamente.");
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "No fue posible exportar el Acta PDF."
      );
    } finally {
      setExportingPdf(false);
    }
  };

  const abrirHistorialVersiones = (revision) => {
    if (!revision?.id) {
      setError("Seleccione una revisión antes de abrir el historial documental.");
      return;
    }

    navigate(`/verificar/revision-direccion/versiones?revision_id=${revision.id}`);
  };

  const guardarCompromiso = async (e) => {
    e.preventDefault();

    if (!selected?.id) {
      setError("Seleccione o cree una revisión primero.");
      return;
    }

    if (!compromisoForm.compromiso) {
      setError("El compromiso es obligatorio.");
      return;
    }

    try {
      setError("");
      await crearCompromisoRevision(selected.id, compromisoForm);
      setCompromisoForm(emptyCompromiso);
      setOk("Compromiso agregado correctamente.");
      await cargarDatos();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "No fue posible crear el compromiso."
      );
    }
  };

  const cerrarCompromiso = async (compromiso) => {
    try {
      setError("");
      await actualizarCompromisoRevision(compromiso.id, {
        estado: "CERRADO",
      });
      setOk("Compromiso cerrado correctamente.");
      await cargarDatos();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "No fue posible cerrar el compromiso."
      );
    }
  };

  const eliminarCompromiso = async (compromiso) => {
    if (!window.confirm("¿Eliminar este compromiso?")) return;

    try {
      setError("");
      await eliminarCompromisoRevision(compromiso.id);
      setOk("Compromiso eliminado correctamente.");
      await cargarDatos();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "No fue posible eliminar el compromiso."
      );
    }
  };

  const selectedCompromisos = selected?.compromisos || [];

  return (
    <AdminLayout>
      <main className="rd-page-pro">
        <section className="rd-hero-pro">
          <div>
            <h1>Revisión por la Dirección SST</h1>
            <p>Consolida resultados, decisiones y compromisos de la alta dirección.</p>
          </div>

          <div className="rd-hero-actions">
            <button title="Actualizar" type="button" onClick={cargarDatos}>
              <RefreshCcw size={17} />
              Actualizar
            </button>

            {puedeEditar && (
              <button title="Nueva revisión" type="button" className="primary" onClick={abrirNuevaRevision}>
                <Plus size={17} />
                Nueva revisión
              </button>
            )}
          </div>
        </section>

        {error && (
          <div className="rd-alert error">
            <AlertTriangle size={18} />
            {error}
          </div>
        )}

        {ok && (
          <div className="rd-alert success">
            <CheckCircle2 size={18} />
            {ok}
          </div>
        )}

        <section className="rd-kpi-grid-pro">
          <article>
            <ShieldCheck />
            <span>Total revisiones</span>
            <strong>{dashboard?.total_revisiones || 0}</strong>
          </article>

          <article>
            <ClipboardList />
            <span>Borradores</span>
            <strong>{dashboard?.borradores || 0}</strong>
          </article>

          <article>
            <CheckCircle2 />
            <span>Cerradas</span>
            <strong>{dashboard?.cerradas || 0}</strong>
          </article>

          <article>
            <Gauge />
            <span>Cumplimiento global</span>
            <strong>{dashboard?.porcentaje_cumplimiento_global || 0}%</strong>
          </article>

          <article>
            <Layers3 />
            <span>Compromisos pendientes</span>
            <strong>{dashboard?.compromisos_pendientes || 0}</strong>
          </article>
        </section>

        <section className="rd-chart-grid-pro">
          <article className="rd-panel-pro">
            <div className="rd-panel-title">
              <BarChart3 size={19} />
              <h2>Estados de revisiones</h2>
            </div>

            <div className="rd-chart">
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={estadosChart}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" name="Cantidad" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="rd-panel-pro">
            <div className="rd-panel-title">
              <ClipboardCheck size={19} />
              <h2>Compromisos gerenciales</h2>
            </div>

            <div className="rd-chart">
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={compromisosChart}
                    dataKey="value"
                    nameKey="name"
                    outerRadius={80}
                    label
                  >
                    {compromisosChart.map((_, index) => (
                      <Cell key={`cell-${index}`} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </article>
        </section>

        <section className="rd-main-grid-pro">
          <article className="rd-panel-pro rd-list-panel">
            <div className="rd-panel-title between">
              <div>
                <h2>Revisiones registradas</h2>
                <p>{revisiones.length} registros activos</p>
              </div>
            </div>

            <div className="rd-list-pro">
              {loading && <p className="rd-muted">Cargando información...</p>}

              {!loading && revisiones.length === 0 && (
                <p className="rd-muted">No hay revisiones registradas.</p>
              )}

              {revisiones.map((revision) => (
                <button
                  key={revision.id}
                  type="button"
                  className={`rd-list-item-pro ${
                    selected?.id === revision.id ? "active" : ""
                  }`}
                  onClick={() => {
                    setSelected(revision);
                    setShowForm(false);
                  }}
                >
                  <div>
                    <strong>{revision.codigo}</strong>
                    <span>{revision.titulo}</span>
                    <small>{fmtDate(revision.fecha_revision)}</small>
                  </div>

                  <em className={`rd-state ${estadoClass(revision.estado)}`}>
                    {revision.estado}
                  </em>
                </button>
              ))}
            </div>
          </article>

          <article className="rd-panel-pro rd-detail-panel">
            {!selected && !showForm && (
              <div className="rd-empty">
                <FileText size={44} />
                <h2>Seleccione una revisión</h2>
                <p>Consulte el acta, indicadores, compromisos y decisiones.</p>
              </div>
            )}

            {showForm && (
              <form className="rd-form-pro" onSubmit={guardarRevision}>
                <div className="rd-panel-title between">
                  <div>
                    <h2>{selected?.id ? "Editar revisión" : "Nueva revisión"}</h2>
                    <p>Complete la información gerencial del SG-SST.</p>
                  </div>

                  <button type="button" className="icon" onClick={() => setShowForm(false)}>
                    <X size={18} />
                  </button>
                </div>

                <div className="rd-form-grid-pro">
                  <label>
                    Empresa ID
                    <input
                      type="number"
                      value={form.empresa_id}
                      onChange={(e) =>
                        setForm({ ...form, empresa_id: Number(e.target.value) })
                      }
                    />
                  </label>

                  <label>
                    Fecha revisión
                    <input
                      type="date"
                      value={form.fecha_revision}
                      onChange={(e) =>
                        setForm({ ...form, fecha_revision: e.target.value })
                      }
                    />
                  </label>

                  <label className="wide">
                    Título
                    <input
                      value={form.titulo}
                      onChange={(e) =>
                        setForm({ ...form, titulo: e.target.value })
                      }
                      placeholder="Revisión por la Dirección 2026"
                    />
                  </label>

                  <label>
                    Periodo evaluado
                    <input
                      value={form.periodo_evaluado}
                      onChange={(e) =>
                        setForm({ ...form, periodo_evaluado: e.target.value })
                      }
                      placeholder="Enero - Junio 2026"
                    />
                  </label>

                  <label>
                    Gerente
                    <input
                      value={form.gerente}
                      onChange={(e) =>
                        setForm({ ...form, gerente: e.target.value })
                      }
                    />
                  </label>

                  <label>
                    Responsable SST
                    <input
                      value={form.responsable_sst}
                      onChange={(e) =>
                        setForm({ ...form, responsable_sst: e.target.value })
                      }
                    />
                  </label>

                  {[
                    ["participantes", "Participantes"],
                    ["objetivo", "Objetivo"],
                    ["alcance", "Alcance"],
                    ["agenda", "Agenda"],
                    ["resumen_auditorias", "Resumen auditorías"],
                    ["resumen_indicadores", "Resumen indicadores"],
                    ["resumen_planes_mejora", "Planes de mejora"],
                    ["resumen_accidentes", "Accidentes"],
                    ["resumen_capacitaciones", "Capacitaciones"],
                    ["resumen_cumplimiento_legal", "Cumplimiento legal"],
                    ["conclusiones", "Conclusiones"],
                    ["decisiones", "Decisiones"],
                    ["recomendaciones", "Recomendaciones"],
                  ].map(([key, label]) => (
                    <label key={key} className="wide">
                      {label}
                      <textarea
                        value={form[key]}
                        onChange={(e) =>
                          setForm({ ...form, [key]: e.target.value })
                        }
                      />
                    </label>
                  ))}
                </div>

                <div className="rd-actions">
                  <button type="submit" className="primary" disabled={saving}>
                    <Save size={18} />
                    {saving ? "Guardando..." : "Guardar revisión"}
                  </button>
                </div>
              </form>
            )}

            {selected && !showForm && (
              <div className="rd-detail-pro">
                <div className="rd-panel-title between">
                  <div>
                    <span className="rd-code">{selected.codigo}</span>
                    <h2>{selected.titulo}</h2>
                    <p>
                      {fmtDate(selected.fecha_revision)} ·{" "}
                      {selected.periodo_evaluado || "Sin periodo"}
                    </p>
                  </div>

                  <div className="rd-detail-actions">
                    <button
                      type="button"
                      onClick={() => exportarActaPdf(selected)}
                      disabled={exportingPdf}
                    >
                      <Download size={16} />
                      {exportingPdf ? "Generando..." : "Exportar PDF Acta"}
                    </button>

                    <button
                      type="button"
                      onClick={() => abrirHistorialVersiones(selected)}
                    >
                      <History size={16} />
                      Historial Versiones
                    </button>

                    {puedeEditar && (
                      <button
                        type="button"
                        onClick={() => abrirEditarRevision(selected)}
                      >
                        <Edit3 size={16} />
                        Editar
                      </button>
                    )}

                    {puedeEliminar && (
                      <button
                        type="button"
                        className="danger"
                        onClick={() => eliminarRevision(selected)}
                      >
                        <Trash2 size={16} />
                        Eliminar
                      </button>
                    )}
                  </div>
                </div>

                <div className="rd-status-row">
                  {ESTADOS.map((estado) => (
                    <button
                      key={estado}
                      type="button"
                      className={selected.estado === estado ? "active" : ""}
                      onClick={() => cambiarEstado(selected, estado)}
                      disabled={!puedeAprobar}
                    >
                      {estado}
                    </button>
                  ))}
                </div>

                <div className="rd-detail-grid-pro">
                  <article>
                    <Users size={18} />
                    <span>Gerente</span>
                    <strong>{selected.gerente || "No registrado"}</strong>
                  </article>

                  <article>
                    <ShieldCheck size={18} />
                    <span>Responsable SST</span>
                    <strong>{selected.responsable_sst || "No registrado"}</strong>
                  </article>

                  <article>
                    <CalendarDays size={18} />
                    <span>Participantes</span>
                    <strong>{selected.participantes || "No registrados"}</strong>
                  </article>
                </div>

                <div className="rd-text-grid-pro">
                  <article>
                    <h3>Objetivo</h3>
                    <p>{selected.objetivo || "Sin objetivo registrado."}</p>
                  </article>

                  <article>
                    <h3>Agenda</h3>
                    <p>{selected.agenda || "Sin agenda registrada."}</p>
                  </article>

                  <article>
                    <h3>Conclusiones</h3>
                    <p>{selected.conclusiones || "Sin conclusiones."}</p>
                  </article>

                  <article>
                    <h3>Decisiones</h3>
                    <p>{selected.decisiones || "Sin decisiones."}</p>
                  </article>
                </div>

                <section className="rd-compromisos-pro">
                  <div className="rd-panel-title">
                    <ClipboardCheck size={20} />
                    <h2>Compromisos gerenciales</h2>
                  </div>

                  {puedeEditar && <form className="rd-compromiso-form-pro" onSubmit={guardarCompromiso}>
                    <input
                      value={compromisoForm.compromiso}
                      onChange={(e) =>
                        setCompromisoForm({
                          ...compromisoForm,
                          compromiso: e.target.value,
                        })
                      }
                      placeholder="Nuevo compromiso gerencial"
                    />

                    <input
                      value={compromisoForm.responsable}
                      onChange={(e) =>
                        setCompromisoForm({
                          ...compromisoForm,
                          responsable: e.target.value,
                        })
                      }
                      placeholder="Responsable"
                    />

                    <input
                      type="date"
                      value={compromisoForm.fecha_compromiso}
                      onChange={(e) =>
                        setCompromisoForm({
                          ...compromisoForm,
                          fecha_compromiso: e.target.value,
                        })
                      }
                    />

                    <select
                      value={compromisoForm.prioridad}
                      onChange={(e) =>
                        setCompromisoForm({
                          ...compromisoForm,
                          prioridad: e.target.value,
                        })
                      }
                    >
                      {PRIORIDADES.map((p) => (
                        <option key={p} value={p}>
                          {p}
                        </option>
                      ))}
                    </select>

                    <button type="submit">
                      <Plus size={16} />
                      Agregar
                    </button>
                  </form>}

                  <div className="rd-compromisos-list">
                    {selectedCompromisos.length === 0 && (
                      <p className="rd-muted">No hay compromisos registrados.</p>
                    )}

                    {selectedCompromisos.map((c) => (
                      <article key={c.id} className="rd-compromiso-card-pro">
                        <div>
                          <strong>{c.compromiso}</strong>
                          <span>
                            {c.responsable || "Sin responsable"} ·{" "}
                            {fmtDate(c.fecha_compromiso)}
                          </span>
                          <small>Prioridad: {c.prioridad}</small>
                        </div>

                        <div className="rd-compromiso-actions">
                          <em className={`rd-state ${estadoClass(c.estado)}`}>
                            {c.estado}
                          </em>

                          {puedeEditar && c.estado !== "CERRADO" && (
                            <button type="button" onClick={() => cerrarCompromiso(c)}>
                              Cerrar
                            </button>
                          )}

                          {puedeEditar && (
                            <button type="button" onClick={() => eliminarCompromiso(c)}>
                              <Trash2 size={15} />
                            </button>
                          )}
                        </div>
                      </article>
                    ))}
                  </div>
                </section>
              </div>
            )}
          </article>
        </section>
      </main>
    </AdminLayout>
  );
}
