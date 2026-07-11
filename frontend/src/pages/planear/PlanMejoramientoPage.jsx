import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  Download,
  Edit3,
  Eye,
  FileText,
  Filter,
  ListChecks,
  Paperclip,
  Plus,
  RefreshCcw,
  Save,
  Search,
  Target,
  Trash2,
  TrendingUp,
  Upload,
  Wand2,
  X,
  CalendarClock,
  History,
  ClipboardList,
} from "lucide-react";

import AdminLayout from "../../layouts/AdminLayout";
import api from "../../api/axios";
import { validarArchivoAntesDeSubir } from "../../utils/fileValidation";
import PlanMejoramientoSeguimientosModal from "./PlanMejoramientoSeguimientosModal";
import "../../styles/plan-mejoramiento.css";

const API_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const ESTADOS = ["PENDIENTE", "EN_PROCESO", "VENCIDO", "FINALIZADO"];
const PRIORIDADES = ["ALTA", "MEDIA", "BAJA"];

const estadoLabel = {
  PENDIENTE: "Pendiente",
  EN_PROCESO: "En proceso",
  VENCIDO: "Vencido",
  FINALIZADO: "Finalizado",
};

export default function PlanMejoramientoPage() {
  const [empresas, setEmpresas] = useState([]);
  const [evaluaciones, setEvaluaciones] = useState([]);
  const [acciones, setAcciones] = useState([]);
  const [dashboard, setDashboard] = useState(null);

  const [loading, setLoading] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [editandoId, setEditandoId] = useState(null);

  const [pagina, setPagina] = useState(1);
  const [porPagina, setPorPagina] = useState(10);

  const [filtros, setFiltros] = useState({
    empresa_id: "",
    estado: "",
    prioridad: "",
    responsable: "",
    buscar: "",
  });

  const [form, setForm] = useState({
    empresa_id: "",
    evaluacion_id: "",
    item_evaluacion_id: "",
    titulo: "",
    descripcion: "",
    causa: "",
    accion_correctiva: "",
    responsable: "",
    prioridad: "MEDIA",
    estado: "PENDIENTE",
    fecha_apertura: "",
    fecha_compromiso: "",
    fecha_cierre: "",
    porcentaje_avance: 0,
    evidencia: "",
    observaciones: "",
  });

  const [generar, setGenerar] = useState({
    evaluacion_id: "",
  });

  const [modalSeguimientos, setModalSeguimientos] = useState({
    abierto: false,
    plan: null,
  });

  const [modalEvidencias, setModalEvidencias] = useState({
    abierto: false,
    plan: null,
    evidencias: [],
    descripcion: "",
    tipo_evidencia: "CIERRE",
    archivo: null,
    loading: false,
  });

  const mostrarError = (error, mensaje) => {
    console.error(error);

    const detail = error?.response?.data?.detail;
    let detalle = "";

    if (Array.isArray(detail)) {
      detalle = detail
        .map((item) => {
          const campo = Array.isArray(item.loc) ? item.loc.join(".") : "";
          return `${campo}: ${item.msg}`;
        })
        .join("\n");
    } else if (typeof detail === "object" && detail !== null) {
      detalle = JSON.stringify(detail, null, 2);
    } else if (detail) {
      detalle = detail;
    } else if (error?.message) {
      detalle = error.message;
    }

    alert(`${mensaje}${detalle ? `\n\nDetalle:\n${detalle}` : ""}`);
  };

  const normalizarPayload = () => ({
    ...form,
    empresa_id: Number(form.empresa_id),
    evaluacion_id: form.evaluacion_id ? Number(form.evaluacion_id) : null,
    item_evaluacion_id: form.item_evaluacion_id
      ? Number(form.item_evaluacion_id)
      : null,
    fecha_apertura: form.fecha_apertura || null,
    fecha_compromiso: form.fecha_compromiso || null,
    fecha_cierre: form.fecha_cierre || null,
    porcentaje_avance: Number(form.porcentaje_avance || 0),
    evidencia: form.evidencia || null,
  });

  const cargarEmpresas = async () => {
    const res = await api.get("/empresas/");
    setEmpresas(res.data || []);
  };

  const cargarEvaluaciones = async () => {
    const params = {};

    if (filtros.empresa_id) {
      params.empresa_id = Number(filtros.empresa_id);
    }

    const res = await api.get("/planear/evaluacion-inicial/", { params });
    setEvaluaciones(res.data || []);
  };

  const cargarDashboard = async () => {
    const params = {};

    if (filtros.empresa_id) {
      params.empresa_id = Number(filtros.empresa_id);
    }

    const res = await api.get("/planear/plan-mejoramiento/dashboard", {
      params,
    });

    setDashboard(res.data);
  };

  const cargarAcciones = async () => {
    const params = {};

    Object.entries(filtros).forEach(([key, value]) => {
      if (value) params[key] = value;
    });

    if (params.empresa_id) {
      params.empresa_id = Number(params.empresa_id);
    }

    const res = await api.get("/planear/plan-mejoramiento/", { params });
    setAcciones(res.data || []);
    setPagina(1);
  };

  const cargarTodo = async () => {
    try {
      setLoading(true);
      await cargarEmpresas();
      await cargarEvaluaciones();
      await cargarDashboard();
      await cargarAcciones();
    } catch (error) {
      mostrarError(error, "No se pudo cargar el Plan de Mejoramiento SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarTodo();
  }, []);

  const kpis = useMemo(() => {
    if (!dashboard) {
      return {
        total_acciones: 0,
        pendientes: 0,
        en_proceso: 0,
        vencidas: 0,
        finalizadas: 0,
        cumplimiento: 0,
      };
    }

    return dashboard;
  }, [dashboard]);

  const totalPaginas = Math.max(1, Math.ceil(acciones.length / porPagina));
  const inicio = (pagina - 1) * porPagina;
  const accionesPaginadas = acciones.slice(inicio, inicio + porPagina);

  const limpiar = () => {
    setEditandoId(null);

    setForm({
      empresa_id: filtros.empresa_id || "",
      evaluacion_id: "",
      item_evaluacion_id: "",
      titulo: "",
      descripcion: "",
      causa: "",
      accion_correctiva: "",
      responsable: "",
      prioridad: "MEDIA",
      estado: "PENDIENTE",
      fecha_apertura: "",
      fecha_compromiso: "",
      fecha_cierre: "",
      porcentaje_avance: 0,
      evidencia: "",
      observaciones: "",
    });
  };

  const handleFiltro = (e) => {
    const { name, value } = e.target;
    setFiltros((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleForm = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: name === "porcentaje_avance" ? Number(value) : value,
    }));
  };

  const guardar = async (e) => {
    e.preventDefault();

    if (!form.empresa_id || !form.titulo || !form.accion_correctiva) {
      alert("Empresa, título y acción correctiva son obligatorios.");
      return;
    }

    try {
      setGuardando(true);

      const payload = normalizarPayload();

      if (editandoId) {
        await api.put(`/planear/plan-mejoramiento/${editandoId}`, payload);
      } else {
        await api.post("/planear/plan-mejoramiento/", payload);
      }

      limpiar();
      await cargarDashboard();
      await cargarAcciones();

      alert("Acción de mejoramiento guardada correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo guardar la acción de mejoramiento.");
    } finally {
      setGuardando(false);
    }
  };

  const editar = (item) => {
    setEditandoId(item.id);

    setForm({
      empresa_id: item.empresa_id || "",
      evaluacion_id: item.evaluacion_id || "",
      item_evaluacion_id: item.item_evaluacion_id || "",
      titulo: item.titulo || "",
      descripcion: item.descripcion || "",
      causa: item.causa || "",
      accion_correctiva: item.accion_correctiva || "",
      responsable: item.responsable || "",
      prioridad: item.prioridad || "MEDIA",
      estado: item.estado || "PENDIENTE",
      fecha_apertura: item.fecha_apertura || "",
      fecha_compromiso: item.fecha_compromiso || "",
      fecha_cierre: item.fecha_cierre || "",
      porcentaje_avance: Number(item.porcentaje_avance || 0),
      evidencia: item.evidencia || "",
      observaciones: item.observaciones || "",
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminar = async (id) => {
    if (!confirm("¿Desea eliminar esta acción de mejoramiento?")) return;

    try {
      await api.delete(`/planear/plan-mejoramiento/${id}`);
      await cargarDashboard();
      await cargarAcciones();
    } catch (error) {
      mostrarError(error, "No se pudo eliminar la acción.");
    }
  };

  const cambiarEstado = async (item, estado) => {
    try {
      await api.patch(`/planear/plan-mejoramiento/${item.id}/estado`, {
        estado,
      });

      await cargarDashboard();
      await cargarAcciones();
    } catch (error) {
      mostrarError(error, "No se pudo cambiar el estado.");
    }
  };

  const cambiarAvance = async (item, porcentaje_avance) => {
    try {
      await api.patch(`/planear/plan-mejoramiento/${item.id}/avance`, {
        porcentaje_avance: Number(porcentaje_avance),
      });

      await cargarDashboard();
      await cargarAcciones();
    } catch (error) {
      mostrarError(error, "No se pudo cambiar el avance.");
    }
  };

  const cerrarAccion = async (item) => {
    if (!confirm("¿Desea finalizar esta acción de mejoramiento?")) return;

    try {
      await api.patch(`/planear/plan-mejoramiento/${item.id}/cerrar`, {
        observaciones: item.observaciones || "Acción finalizada desde el panel.",
      });

      await cargarDashboard();
      await cargarAcciones();
    } catch (error) {
      mostrarError(error, "No se pudo finalizar la acción.");
    }
  };

  const generarDesdeEvaluacion = async () => {
    if (!generar.evaluacion_id) {
      alert("Seleccione una evaluación inicial.");
      return;
    }

    try {
      setGuardando(true);

      const res = await api.post(
        "/planear/plan-mejoramiento/generar-desde-evaluacion",
        {
          evaluacion_id: Number(generar.evaluacion_id),
        }
      );

      await cargarDashboard();
      await cargarAcciones();

      alert(
        `Plan generado correctamente.\nCreados: ${res.data.creados}\nOmitidos: ${res.data.omitidos}`
      );
    } catch (error) {
      mostrarError(error, "No se pudo generar el plan automático.");
    } finally {
      setGuardando(false);
    }
  };

  const aplicarFiltros = async () => {
    try {
      setLoading(true);
      await cargarEvaluaciones();
      await cargarDashboard();
      await cargarAcciones();
    } catch (error) {
      mostrarError(error, "No se pudieron aplicar los filtros.");
    } finally {
      setLoading(false);
    }
  };

  const nombreEmpresa = (id) => {
    const empresa = empresas.find((item) => Number(item.id) === Number(id));
    return empresa?.nombre || `Empresa ${id}`;
  };

  const abrirArchivo = (url) => {
    if (!url) return;
    window.open(`${API_URL}${url}`, "_blank", "noopener,noreferrer");
  };

  const descargarArchivo = (url, nombre = "evidencia") => {
    if (!url) return;

    const link = document.createElement("a");
    link.href = `${API_URL}${url}`;
    link.setAttribute("download", nombre);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const abrirModalSeguimientos = (plan) => {
    setModalSeguimientos({
      abierto: true,
      plan,
    });
  };

  const cerrarModalSeguimientos = () => {
    setModalSeguimientos({
      abierto: false,
      plan: null,
    });
  };

  const cargarEvidenciasPlan = async (plan) => {
    if (!plan?.id) return;

    try {
      setModalEvidencias((prev) => ({
        ...prev,
        loading: true,
      }));

      const res = await api.get(
        `/planear/plan-mejoramiento-evidencias/${plan.id}`
      );

      setModalEvidencias((prev) => ({
        ...prev,
        evidencias: res.data || [],
        loading: false,
      }));
    } catch (error) {
      setModalEvidencias((prev) => ({
        ...prev,
        loading: false,
      }));
      mostrarError(error, "No se pudieron cargar las evidencias.");
    }
  };

  const abrirModalEvidencias = async (plan) => {
    setModalEvidencias({
      abierto: true,
      plan,
      evidencias: [],
      descripcion: "",
      tipo_evidencia: "CIERRE",
      archivo: null,
      loading: true,
    });

    try {
      const res = await api.get(
        `/planear/plan-mejoramiento-evidencias/${plan.id}`
      );

      setModalEvidencias((prev) => ({
        ...prev,
        evidencias: res.data || [],
        loading: false,
      }));
    } catch (error) {
      setModalEvidencias((prev) => ({
        ...prev,
        loading: false,
      }));
      mostrarError(error, "No se pudieron cargar las evidencias.");
    }
  };

  const cerrarModalEvidencias = () => {
    setModalEvidencias({
      abierto: false,
      plan: null,
      evidencias: [],
      descripcion: "",
      tipo_evidencia: "CIERRE",
      archivo: null,
      loading: false,
    });
  };

  const seleccionarArchivoEvidencia = (file) => {
    if (!file) return;

    const validacion = validarArchivoAntesDeSubir(file);

    if (!validacion.ok) {
      alert(validacion.mensaje);
      return;
    }

    setModalEvidencias((prev) => ({
      ...prev,
      archivo: file,
    }));
  };

  const subirEvidenciaPlan = async () => {
    if (!modalEvidencias.plan?.id) {
      alert("No hay acción seleccionada.");
      return;
    }

    if (!modalEvidencias.archivo) {
      alert("Seleccione un archivo de evidencia.");
      return;
    }

    const validacion = validarArchivoAntesDeSubir(modalEvidencias.archivo);

    if (!validacion.ok) {
      alert(validacion.mensaje);
      return;
    }

    const data = new FormData();
    data.append("descripcion", modalEvidencias.descripcion || "");
    data.append("tipo_evidencia", modalEvidencias.tipo_evidencia || "CIERRE");
    data.append("file", modalEvidencias.archivo);

    try {
      setModalEvidencias((prev) => ({
        ...prev,
        loading: true,
      }));

      await api.post(
        `/planear/plan-mejoramiento-evidencias/${modalEvidencias.plan.id}/upload`,
        data,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setModalEvidencias((prev) => ({
        ...prev,
        descripcion: "",
        tipo_evidencia: "CIERRE",
        archivo: null,
      }));

      await cargarEvidenciasPlan(modalEvidencias.plan);
      alert("Evidencia cargada correctamente.");
    } catch (error) {
      setModalEvidencias((prev) => ({
        ...prev,
        loading: false,
      }));
      mostrarError(error, "No se pudo subir la evidencia.");
    }
  };

  const eliminarEvidenciaPlan = async (evidenciaId) => {
    if (!confirm("¿Desea eliminar esta evidencia?")) return;

    try {
      await api.delete(`/planear/plan-mejoramiento-evidencias/${evidenciaId}`);
      await cargarEvidenciasPlan(modalEvidencias.plan);
    } catch (error) {
      mostrarError(error, "No se pudo eliminar la evidencia.");
    }
  };

  const esImagen = (extension) => {
    const ext = String(extension || "").toLowerCase();
    return [".jpg", ".jpeg", ".png", ".webp", ".bmp"].includes(ext);
  };

  return (
    <AdminLayout>
      <div className="pm-page">
        <section className="pm-hero">
          <div>
            <span className="pm-badge">PLAN DE MEJORAMIENTO</span>
            <h2>Plan de Mejoramiento SST Inteligente</h2>
            <p>
              Gestión de acciones correctivas, seguimientos, evidencias y cierre
              del ciclo de mejora continua SG-SST.
            </p>
          </div>

          <div className="pm-hero-actions">
            <button type="button" onClick={cargarTodo} disabled={loading}>
              <RefreshCcw size={17} />
              {loading ? "Actualizando..." : "Actualizar"}
            </button>
          </div>
        </section>

        <section className="pm-kpis pm-kpis-extended">
          <article className="pm-kpi blue">
            <ClipboardCheck />
            <span>Total acciones</span>
            <strong>{kpis.total_acciones}</strong>
          </article>

          <article className="pm-kpi orange">
            <AlertTriangle />
            <span>Pendientes</span>
            <strong>{kpis.pendientes}</strong>
          </article>

          <article className="pm-kpi purple">
            <TrendingUp />
            <span>En proceso</span>
            <strong>{kpis.en_proceso}</strong>
          </article>

          <article className="pm-kpi red">
            <Target />
            <span>Vencidas</span>
            <strong>{kpis.vencidas}</strong>
          </article>

          <article className="pm-kpi green">
            <CheckCircle2 />
            <span>Finalizadas</span>
            <strong>{kpis.finalizadas}</strong>
          </article>

          <article className="pm-kpi dark">
            <TrendingUp />
            <span>Cumplimiento</span>
            <strong>{kpis.cumplimiento}%</strong>
          </article>

          <article className="pm-kpi cyan">
            <History />
            <span>Total seguimientos</span>
            <strong>{kpis.total_seguimientos || 0}</strong>
          </article>

          <article className="pm-kpi teal">
            <ClipboardList />
            <span>Con seguimiento</span>
            <strong>{kpis.acciones_con_seguimiento || 0}</strong>
          </article>

          <article className="pm-kpi gray">
            <ClipboardList />
            <span>Sin seguimiento</span>
            <strong>{kpis.acciones_sin_seguimiento || 0}</strong>
          </article>

          <article className="pm-kpi yellow">
            <CalendarClock />
            <span>Próximos</span>
            <strong>{kpis.seguimientos_proximos || 0}</strong>
          </article>

          <article className="pm-kpi rose">
            <AlertTriangle />
            <span>Seg. vencidos</span>
            <strong>{kpis.seguimientos_vencidos || 0}</strong>
          </article>
        </section>

        <section className="pm-workspace">
          <form className="pm-form" onSubmit={guardar}>
            <div className="pm-section-title">
              <h3>{editandoId ? "Editar acción" : "Nueva acción"}</h3>
              {editandoId && (
                <button type="button" className="pm-clear" onClick={limpiar}>
                  <X size={15} /> Cancelar
                </button>
              )}
            </div>

            <label>Empresa</label>
            <select
              name="empresa_id"
              value={form.empresa_id}
              onChange={handleForm}
            >
              <option value="">Seleccione empresa</option>
              {empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>
                  {empresa.nombre}
                </option>
              ))}
            </select>

            <div className="pm-row">
              <input
                name="titulo"
                value={form.titulo}
                onChange={handleForm}
                placeholder="Título de la acción"
              />

              <input
                name="responsable"
                value={form.responsable}
                onChange={handleForm}
                placeholder="Responsable"
              />
            </div>

            <textarea
              name="descripcion"
              value={form.descripcion}
              onChange={handleForm}
              placeholder="Descripción / hallazgo"
            />

            <textarea
              name="causa"
              value={form.causa}
              onChange={handleForm}
              placeholder="Causa raíz"
            />

            <textarea
              name="accion_correctiva"
              value={form.accion_correctiva}
              onChange={handleForm}
              placeholder="Acción correctiva o de mejora"
            />

            <div className="pm-row three">
              <select
                name="prioridad"
                value={form.prioridad}
                onChange={handleForm}
              >
                {PRIORIDADES.map((prioridad) => (
                  <option key={prioridad} value={prioridad}>
                    {prioridad}
                  </option>
                ))}
              </select>

              <select name="estado" value={form.estado} onChange={handleForm}>
                {ESTADOS.map((estado) => (
                  <option key={estado} value={estado}>
                    {estadoLabel[estado] || estado}
                  </option>
                ))}
              </select>

              <input
                type="number"
                min="0"
                max="100"
                name="porcentaje_avance"
                value={form.porcentaje_avance}
                onChange={handleForm}
                placeholder="% avance"
              />
            </div>

            <div className="pm-row">
              <div>
                <label>Fecha apertura</label>
                <input
                  type="date"
                  name="fecha_apertura"
                  value={form.fecha_apertura}
                  onChange={handleForm}
                />
              </div>

              <div>
                <label>Fecha compromiso</label>
                <input
                  type="date"
                  name="fecha_compromiso"
                  value={form.fecha_compromiso}
                  onChange={handleForm}
                />
              </div>
            </div>

            <textarea
              name="observaciones"
              value={form.observaciones}
              onChange={handleForm}
              placeholder="Observaciones"
            />

            <div className="pm-progress-preview">
              <span>Avance: {form.porcentaje_avance}%</span>
              <div>
                <b style={{ width: `${form.porcentaje_avance}%` }} />
              </div>
            </div>

            <div className="pm-form-actions">
              <button type="submit" disabled={guardando}>
                <Save size={17} />
                {editandoId ? "Actualizar" : "Guardar"}
              </button>

              <button type="button" onClick={limpiar}>
                <Plus size={17} />
                Nuevo
              </button>
            </div>
          </form>

          <aside className="pm-auto-panel">
            <div className="pm-section-title">
              <h3>Generación automática</h3>
            </div>

            <p>
              Genera acciones correctivas automáticamente desde los criterios
              marcados como <strong>NO CUMPLE</strong> en la Evaluación Inicial.
            </p>

            <label>Evaluación inicial</label>
            <select
              value={generar.evaluacion_id}
              onChange={(e) => setGenerar({ evaluacion_id: e.target.value })}
            >
              <option value="">Seleccione evaluación</option>
              {evaluaciones.map((evalItem) => (
                <option key={evalItem.id} value={evalItem.id}>
                  {evalItem.codigo} · {nombreEmpresa(evalItem.empresa_id)} ·{" "}
                  {evalItem.total_items} criterios
                </option>
              ))}
            </select>

            <button
              type="button"
              className="pm-generate"
              onClick={generarDesdeEvaluacion}
              disabled={guardando}
            >
              <Wand2 size={18} />
              Generar Plan Automático
            </button>

            <div className="pm-help">
              <strong>Regla automática</strong>
              <span>
                Cada criterio NO_CUMPLE genera una acción de mejoramiento con
                prioridad y fecha compromiso sugerida.
              </span>
            </div>
          </aside>
        </section>

        <section className="pm-list">
          <div className="pm-filters">
            <div className="pm-filter-title">
              <Filter size={18} />
              <strong>Filtros</strong>
            </div>

            <select
              name="empresa_id"
              value={filtros.empresa_id}
              onChange={handleFiltro}
            >
              <option value="">Todas las empresas</option>
              {empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>
                  {empresa.nombre}
                </option>
              ))}
            </select>

            <select
              name="estado"
              value={filtros.estado}
              onChange={handleFiltro}
            >
              <option value="">Todos los estados</option>
              {ESTADOS.map((estado) => (
                <option key={estado} value={estado}>
                  {estadoLabel[estado] || estado}
                </option>
              ))}
            </select>

            <select
              name="prioridad"
              value={filtros.prioridad}
              onChange={handleFiltro}
            >
              <option value="">Todas las prioridades</option>
              {PRIORIDADES.map((prioridad) => (
                <option key={prioridad} value={prioridad}>
                  {prioridad}
                </option>
              ))}
            </select>

            <input
              name="buscar"
              value={filtros.buscar}
              onChange={handleFiltro}
              placeholder="Buscar acción..."
            />

            <button type="button" onClick={aplicarFiltros}>
              <Search size={16} />
              Filtrar
            </button>
          </div>

          <div className="pm-toolbar">
            <span>
              Mostrando {accionesPaginadas.length} de {acciones.length} acciones
            </span>

            <select
              value={porPagina}
              onChange={(e) => {
                setPorPagina(Number(e.target.value));
                setPagina(1);
              }}
            >
              <option value={10}>10 por página</option>
              <option value={25}>25 por página</option>
              <option value={50}>50 por página</option>
            </select>
          </div>

          <div className="pm-table-wrap">
            <table className="pm-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Empresa</th>
                  <th>Acción</th>
                  <th>Prioridad</th>
                  <th>Estado</th>
                  <th>Compromiso</th>
                  <th>Avance</th>
                  <th>Evidencias</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {accionesPaginadas.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <strong>{item.codigo}</strong>
                    </td>

                    <td>{nombreEmpresa(item.empresa_id)}</td>

                    <td>
                      <div className="pm-action-cell">
                        <strong>{item.titulo}</strong>
                        <span>{item.accion_correctiva}</span>
                      </div>
                    </td>

                    <td>
                      <span
                        className={`pm-priority ${String(
                          item.prioridad,
                        ).toLowerCase()}`}
                      >
                        {item.prioridad}
                      </span>
                    </td>

                    <td>
                      <select
                        className={`pm-status ${String(
                          item.estado,
                        ).toLowerCase()}`}
                        value={item.estado}
                        onChange={(e) => cambiarEstado(item, e.target.value)}
                      >
                        {ESTADOS.map((estado) => (
                          <option key={estado} value={estado}>
                            {estadoLabel[estado] || estado}
                          </option>
                        ))}
                      </select>
                    </td>

                    <td>{item.fecha_compromiso || "Sin fecha"}</td>

                    <td>
                      <div className="pm-table-progress">
                        <span>{item.porcentaje_avance}%</span>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          value={item.porcentaje_avance || 0}
                          onChange={(e) => cambiarAvance(item, e.target.value)}
                        />
                      </div>
                    </td>

                    <td>
                      <button
                        type="button"
                        className="pm-evidence-btn"
                        onClick={() => abrirModalEvidencias(item)}
                      >
                        <Paperclip size={15} />
                        Evidencias
                      </button>
                    </td>

                    <td>
                      <div className="pm-row-actions">
                        <button
                          type="button"
                          onClick={() => abrirModalSeguimientos(item)}
                          title="Seguimientos"
                        >
                          <ListChecks size={15} />
                        </button>

                        <button
                          type="button"
                          onClick={() => editar(item)}
                          title="Editar"
                        >
                          <Edit3 size={15} />
                        </button>

                        <button
                          type="button"
                          onClick={() => cerrarAccion(item)}
                          title="Finalizar"
                        >
                          <CheckCircle2 size={15} />
                        </button>

                        <button
                          type="button"
                          onClick={() => eliminar(item.id)}
                          title="Eliminar"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {accionesPaginadas.length === 0 && (
                  <tr>
                    <td colSpan="9" className="pm-empty">
                      No hay acciones de mejoramiento registradas.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="pm-pagination">
            <button
              type="button"
              disabled={pagina === 1}
              onClick={() => setPagina(1)}
            >
              « Primera
            </button>

            <button
              type="button"
              disabled={pagina === 1}
              onClick={() => setPagina((prev) => Math.max(1, prev - 1))}
            >
              ‹ Anterior
            </button>

            <span>
              Página {pagina} de {totalPaginas}
            </span>

            <button
              type="button"
              disabled={pagina >= totalPaginas}
              onClick={() =>
                setPagina((prev) => Math.min(totalPaginas, prev + 1))
              }
            >
              Siguiente ›
            </button>

            <button
              type="button"
              disabled={pagina >= totalPaginas}
              onClick={() => setPagina(totalPaginas)}
            >
              Última »
            </button>
          </div>
        </section>

        {modalEvidencias.abierto && (
          <div className="pm-modal-overlay">
            <div className="pm-evidence-modal">
              <div className="pm-modal-header">
                <div>
                  <span>Acción correctiva</span>
                  <h3>
                    {modalEvidencias.plan?.codigo} ·{" "}
                    {modalEvidencias.plan?.titulo}
                  </h3>
                </div>

                <button type="button" onClick={cerrarModalEvidencias}>
                  <X size={20} />
                </button>
              </div>

              <div className="pm-modal-grid">
                <section className="pm-upload-box">
                  <h4>Subir evidencia</h4>

                  <label>Tipo de evidencia</label>
                  <select
                    value={modalEvidencias.tipo_evidencia}
                    onChange={(e) =>
                      setModalEvidencias((prev) => ({
                        ...prev,
                        tipo_evidencia: e.target.value,
                      }))
                    }
                  >
                    <option value="CIERRE">Cierre</option>
                    <option value="SEGUIMIENTO">Seguimiento</option>
                    <option value="ANTES">Antes</option>
                    <option value="DESPUES">Después</option>
                    <option value="SOPORTE">Soporte</option>
                  </select>

                  <label>Descripción</label>
                  <textarea
                    value={modalEvidencias.descripcion}
                    onChange={(e) =>
                      setModalEvidencias((prev) => ({
                        ...prev,
                        descripcion: e.target.value,
                      }))
                    }
                    placeholder="Descripción breve de la evidencia"
                  />

                  <label className="pm-upload-drop">
                    <Upload size={28} />
                    <strong>
                      {modalEvidencias.archivo
                        ? modalEvidencias.archivo.name
                        : "Seleccionar archivo"}
                    </strong>
                    <span>PDF, Word, Excel o imagen hasta 10 MB</span>

                    <input
                      type="file"
                      hidden
                      onChange={(e) =>
                        seleccionarArchivoEvidencia(e.target.files?.[0])
                      }
                    />
                  </label>

                  <button
                    type="button"
                    className="pm-upload-submit"
                    onClick={subirEvidenciaPlan}
                    disabled={modalEvidencias.loading}
                  >
                    <Upload size={17} />
                    {modalEvidencias.loading
                      ? "Procesando..."
                      : "Subir evidencia"}
                  </button>
                </section>

                <section className="pm-evidence-list-box">
                  <div className="pm-evidence-title">
                    <h4>Evidencias cargadas</h4>
                    <span>{modalEvidencias.evidencias.length}</span>
                  </div>

                  {modalEvidencias.loading && (
                    <div className="pm-evidence-empty">
                      Cargando evidencias...
                    </div>
                  )}

                  {!modalEvidencias.loading &&
                    modalEvidencias.evidencias.length === 0 && (
                      <div className="pm-evidence-empty">
                        No hay evidencias cargadas para esta acción.
                      </div>
                    )}

                  {!modalEvidencias.loading &&
                    modalEvidencias.evidencias.map((ev) => (
                      <article className="pm-evidence-card" key={ev.id}>
                        <div className="pm-evidence-preview">
                          {esImagen(ev.extension) ? (
                            <img
                              src={`${API_URL}${ev.url}`}
                              alt={ev.nombre_original}
                            />
                          ) : (
                            <FileText size={34} />
                          )}
                        </div>

                        <div className="pm-evidence-info">
                          <strong>{ev.nombre_original || "Evidencia"}</strong>
                          <span>
                            {ev.tipo_evidencia || "CIERRE"} ·{" "}
                            {ev.extension || "archivo"} ·{" "}
                            {Math.round(Number(ev.tamano_bytes || 0) / 1024)} KB
                          </span>
                          {ev.descripcion && <p>{ev.descripcion}</p>}
                        </div>

                        <div className="pm-evidence-actions">
                          <button
                            type="button"
                            onClick={() => abrirArchivo(ev.url)}
                          >
                            <Eye size={15} />
                          </button>

                          <button
                            type="button"
                            onClick={() =>
                              descargarArchivo(
                                ev.url,
                                ev.nombre_original || "evidencia",
                              )
                            }
                          >
                            <Download size={15} />
                          </button>

                          <button
                            type="button"
                            onClick={() => eliminarEvidenciaPlan(ev.id)}
                          >
                            <Trash2 size={15} />
                          </button>
                        </div>
                      </article>
                    ))}
                </section>
              </div>
            </div>
          </div>
        )}

        <PlanMejoramientoSeguimientosModal
          abierto={modalSeguimientos.abierto}
          plan={modalSeguimientos.plan}
          onClose={cerrarModalSeguimientos}
          onUpdated={async () => {
            await cargarDashboard();
            await cargarAcciones();
          }}
        />
      </div>
    </AdminLayout>
  );
}
