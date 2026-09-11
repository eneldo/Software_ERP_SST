// ============================================================
// AUDITORÍAS SST ENTERPRISE
// FASE 1.7.3 - FRONTEND
// Dashboard Ejecutivo de Hallazgos SST
// Archivo: frontend/src/pages/verificar/AuditoriasPage.jsx
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  ClipboardCheck,
  Edit3,
  Eye,
  FileWarning,
  Filter,
  Plus,
  RefreshCcw,
  Save,
  Search,
  ShieldAlert,
  Trash2,
  Wand2,
  X,
} from "lucide-react";

import AdminLayout from "../../layouts/AdminLayout";
import api from "../../api/axios";
import { toastSuccess, toastError, toastWarning, confirmAction } from "../../utils/toast";
import AuditoriaHallazgosModal from "./AuditoriaHallazgosModal";

import "../../styles/auditorias-sst.css";
import "../../styles/auditorias-kanban.css";

const ESTADOS_AUDITORIA = ["PROGRAMADA", "EN_PROCESO", "CERRADA", "CANCELADA"];
const TIPOS_AUDITORIA = ["INTERNA", "EXTERNA", "LEGAL", "SEGUIMIENTO"];

const estadoAuditoriaLabel = {
  PROGRAMADA: "Programada",
  EN_PROCESO: "En proceso",
  CERRADA: "Cerrada",
  CANCELADA: "Cancelada",
};

export default function AuditoriasPage() {
  const [empresas, setEmpresas] = useState([]);
  const [auditorias, setAuditorias] = useState([]);
  const [dashboard, setDashboard] = useState(null);

  const [loading, setLoading] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [editandoId, setEditandoId] = useState(null);

  const [pagina, setPagina] = useState(1);
  const [porPagina, setPorPagina] = useState(10);

  const [filtros, setFiltros] = useState({
    empresa_id: "",
    estado: "",
    buscar: "",
  });

  const [form, setForm] = useState({
    empresa_id: "",
    nombre: "",
    tipo_auditoria: "INTERNA",
    estado: "PROGRAMADA",
    objetivo: "",
    alcance: "",
    criterio: "",
    auditor_lider: "",
    equipo_auditor: "",
    fecha_programada: "",
    fecha_inicio: "",
    fecha_cierre: "",
    conclusiones: "",
    recomendaciones: "",
  });

  const [modalHallazgos, setModalHallazgos] = useState({
    abierto: false,
    auditoria: null,
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

    toastError("Error", `${mensaje}${detalle ? `\n\nDetalle:\n${detalle}` : ""}`);
  };

  const cargarEmpresas = async () => {
    const res = await api.get("/empresas/");
    setEmpresas(res.data || []);
  };

  const cargarDashboard = async () => {
    const params = {};

    if (filtros.empresa_id) {
      params.empresa_id = Number(filtros.empresa_id);
    }

    const res = await api.get("/verificar/auditorias-sst/dashboard", {
      params,
    });

    setDashboard(res.data);
  };

  const cargarAuditorias = async () => {
    const params = {};

    if (filtros.empresa_id) params.empresa_id = Number(filtros.empresa_id);
    if (filtros.estado) params.estado = filtros.estado;
    if (filtros.buscar) params.buscar = filtros.buscar;

    const res = await api.get("/verificar/auditorias-sst/", { params });
    setAuditorias(res.data || []);
    setPagina(1);
  };

  const cargarTodo = async () => {
    try {
      setLoading(true);
      await cargarEmpresas();
      await cargarDashboard();
      await cargarAuditorias();
    } catch (error) {
      mostrarError(error, "No se pudo cargar el módulo de Auditorías SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarTodo();
  }, []);

  const kpis = useMemo(() => {
    return {
      total_auditorias: dashboard?.total_auditorias || 0,
      programadas: dashboard?.programadas || 0,
      en_proceso: dashboard?.en_proceso || 0,
      cerradas: dashboard?.cerradas || 0,

      total_hallazgos: dashboard?.total_hallazgos || 0,
      no_conformidades: dashboard?.no_conformidades || 0,
      observaciones: dashboard?.observaciones || 0,
      oportunidades_mejora: dashboard?.oportunidades_mejora || 0,

      hallazgos_abiertos: dashboard?.hallazgos_abiertos || 0,
      hallazgos_en_proceso: dashboard?.hallazgos_en_proceso || 0,
      hallazgos_cerrados: dashboard?.hallazgos_cerrados || 0,

      no_conformidades_abiertas: dashboard?.no_conformidades_abiertas || 0,

      planes_generados: dashboard?.planes_generados || 0,
      planes_pendientes: dashboard?.planes_pendientes || 0,

      riesgo_alto: dashboard?.riesgo_alto || 0,
      riesgo_medio: dashboard?.riesgo_medio || 0,
      riesgo_bajo: dashboard?.riesgo_bajo || 0,

      porcentaje_cierre_general: dashboard?.porcentaje_cierre_general || 0,
      cumplimiento_hallazgos: dashboard?.cumplimiento_hallazgos || 0,
    };
  }, [dashboard]);

  const totalPaginas = Math.max(1, Math.ceil(auditorias.length / porPagina));
  const inicio = (pagina - 1) * porPagina;
  const auditoriasPaginadas = auditorias.slice(inicio, inicio + porPagina);

  const nombreEmpresa = (id) => {
    const empresa = empresas.find((item) => Number(item.id) === Number(id));
    return empresa?.nombre || `Empresa ${id}`;
  };

  const limpiar = () => {
    setEditandoId(null);
    setForm({
      empresa_id: filtros.empresa_id || "",
      nombre: "",
      tipo_auditoria: "INTERNA",
      estado: "PROGRAMADA",
      objetivo: "",
      alcance: "",
      criterio: "",
      auditor_lider: "",
      equipo_auditor: "",
      fecha_programada: "",
      fecha_inicio: "",
      fecha_cierre: "",
      conclusiones: "",
      recomendaciones: "",
    });
  };

  const normalizarPayload = () => ({
    ...form,
    empresa_id: Number(form.empresa_id),
    fecha_programada: form.fecha_programada || null,
    fecha_inicio: form.fecha_inicio || null,
    fecha_cierre: form.fecha_cierre || null,
  });

  const handleForm = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleFiltro = (e) => {
    const { name, value } = e.target;
    setFiltros((prev) => ({ ...prev, [name]: value }));
  };

  const guardarAuditoria = async (e) => {
    e.preventDefault();

    if (!form.empresa_id || !form.nombre) {
      toastWarning("Advertencia", "Empresa y nombre de auditoría son obligatorios.");
      return;
    }

    try {
      setGuardando(true);
      const payload = normalizarPayload();

      if (editandoId) {
        await api.put(`/verificar/auditorias-sst/${editandoId}`, payload);
      } else {
        await api.post("/verificar/auditorias-sst/", payload);
      }

      limpiar();
      await cargarDashboard();
      await cargarAuditorias();

      toastSuccess("Éxito", "Auditoría guardada correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo guardar la auditoría.");
    } finally {
      setGuardando(false);
    }
  };

  const editarAuditoria = (auditoria) => {
    setEditandoId(auditoria.id);

    setForm({
      empresa_id: auditoria.empresa_id || "",
      nombre: auditoria.nombre || "",
      tipo_auditoria: auditoria.tipo_auditoria || "INTERNA",
      estado: auditoria.estado || "PROGRAMADA",
      objetivo: auditoria.objetivo || "",
      alcance: auditoria.alcance || "",
      criterio: auditoria.criterio || "",
      auditor_lider: auditoria.auditor_lider || "",
      equipo_auditor: auditoria.equipo_auditor || "",
      fecha_programada: auditoria.fecha_programada || "",
      fecha_inicio: auditoria.fecha_inicio || "",
      fecha_cierre: auditoria.fecha_cierre || "",
      conclusiones: auditoria.conclusiones || "",
      recomendaciones: auditoria.recomendaciones || "",
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminarAuditoria = async (id) => {
    if (!confirmAction("¿Desea eliminar esta auditoría?")) return;

    try {
      await api.delete(`/verificar/auditorias-sst/${id}`);
      await cargarDashboard();
      await cargarAuditorias();
    } catch (error) {
      mostrarError(error, "No se pudo eliminar la auditoría.");
    }
  };

  const aplicarFiltros = async () => {
    try {
      setLoading(true);
      await cargarDashboard();
      await cargarAuditorias();
    } catch (error) {
      mostrarError(error, "No se pudieron aplicar los filtros.");
    } finally {
      setLoading(false);
    }
  };

  const abrirModalHallazgos = (auditoria) => {
    setModalHallazgos({
      abierto: true,
      auditoria,
    });
  };

  const cerrarModalHallazgos = () => {
    setModalHallazgos({
      abierto: false,
      auditoria: null,
    });
  };

  return (
    <AdminLayout>
      <div className="aud-page">
        <section className="aud-hero">
          <div>
            <h2>Auditorías SST</h2>
            <p>Programa auditorías, registra hallazgos y controla planes de mejoramiento.</p>
          </div>

          <button type="button" onClick={cargarTodo} disabled={loading}>
            <RefreshCcw size={17} />
            {loading ? "Actualizando..." : "Actualizar"}
          </button>
        </section>

        <section className="aud-kpis aud-kpis-executive">
          <article className="aud-kpi blue">
            <ClipboardCheck />
            <span>Total auditorías</span>
            <strong>{kpis.total_auditorias}</strong>
          </article>

          <article className="aud-kpi yellow">
            <BarChart3 />
            <span>Programadas</span>
            <strong>{kpis.programadas}</strong>
          </article>

          <article className="aud-kpi purple">
            <Search />
            <span>En proceso</span>
            <strong>{kpis.en_proceso}</strong>
          </article>

          <article className="aud-kpi green">
            <CheckCircle2 />
            <span>Cerradas</span>
            <strong>{kpis.cerradas}</strong>
          </article>

          <article className="aud-kpi red">
            <FileWarning />
            <span>Total hallazgos</span>
            <strong>{kpis.total_hallazgos}</strong>
          </article>

          <article className="aud-kpi danger">
            <AlertTriangle />
            <span>Hallazgos abiertos</span>
            <strong>{kpis.hallazgos_abiertos}</strong>
          </article>

          <article className="aud-kpi warning">
            <BarChart3 />
            <span>Hallazgos en proceso</span>
            <strong>{kpis.hallazgos_en_proceso}</strong>
          </article>

          <article className="aud-kpi success">
            <CheckCircle2 />
            <span>Hallazgos cerrados</span>
            <strong>{kpis.hallazgos_cerrados}</strong>
          </article>

          <article className="aud-kpi rose">
            <ShieldAlert />
            <span>No conformidades</span>
            <strong>{kpis.no_conformidades}</strong>
          </article>

          <article className="aud-kpi danger">
            <ShieldAlert />
            <span>NC abiertas</span>
            <strong>{kpis.no_conformidades_abiertas}</strong>
          </article>

          <article className="aud-kpi gray">
            <AlertTriangle />
            <span>Observaciones</span>
            <strong>{kpis.observaciones}</strong>
          </article>

          <article className="aud-kpi teal">
            <Wand2 />
            <span>Oportunidades</span>
            <strong>{kpis.oportunidades_mejora}</strong>
          </article>

          <article className="aud-kpi info">
            <Wand2 />
            <span>Planes generados</span>
            <strong>{kpis.planes_generados}</strong>
          </article>

          <article className="aud-kpi secondary">
            <ClipboardCheck />
            <span>Planes pendientes</span>
            <strong>{kpis.planes_pendientes}</strong>
          </article>

          <article className="aud-kpi danger">
            <AlertTriangle />
            <span>Riesgo alto</span>
            <strong>{kpis.riesgo_alto}</strong>
          </article>

          <article className="aud-kpi warning">
            <AlertTriangle />
            <span>Riesgo medio</span>
            <strong>{kpis.riesgo_medio}</strong>
          </article>

          <article className="aud-kpi success">
            <CheckCircle2 />
            <span>Riesgo bajo</span>
            <strong>{kpis.riesgo_bajo}</strong>
          </article>

          <article className="aud-kpi dark">
            <BarChart3 />
            <span>Cumplimiento hallazgos</span>
            <strong>{kpis.cumplimiento_hallazgos}%</strong>
          </article>

          <article className="aud-kpi dark">
            <CheckCircle2 />
            <span>Cierre general</span>
            <strong>{kpis.porcentaje_cierre_general}%</strong>
          </article>
        </section>

        <section className="aud-workspace">
          <form className="aud-form" onSubmit={guardarAuditoria}>
            <div className="aud-section-title">
              <h3>{editandoId ? "Editar auditoría" : "Nueva auditoría"}</h3>

              {editandoId && (
                <button type="button" className="aud-clear" onClick={limpiar}>
                  <X size={15} />
                  Cancelar
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

            <input
              name="nombre"
              value={form.nombre}
              onChange={handleForm}
              placeholder="Nombre de la auditoría"
            />

            <div className="aud-row three">
              <select
                name="tipo_auditoria"
                value={form.tipo_auditoria}
                onChange={handleForm}
              >
                {TIPOS_AUDITORIA.map((tipo) => (
                  <option key={tipo} value={tipo}>
                    {tipo}
                  </option>
                ))}
              </select>

              <select name="estado" value={form.estado} onChange={handleForm}>
                {ESTADOS_AUDITORIA.map((estado) => (
                  <option key={estado} value={estado}>
                    {estadoAuditoriaLabel[estado]}
                  </option>
                ))}
              </select>

              <input
                name="auditor_lider"
                value={form.auditor_lider}
                onChange={handleForm}
                placeholder="Auditor líder"
              />
            </div>

            <textarea
              name="objetivo"
              value={form.objetivo}
              onChange={handleForm}
              placeholder="Objetivo de la auditoría"
            />

            <textarea
              name="alcance"
              value={form.alcance}
              onChange={handleForm}
              placeholder="Alcance"
            />

            <textarea
              name="criterio"
              value={form.criterio}
              onChange={handleForm}
              placeholder="Criterio de auditoría"
            />

            <textarea
              name="equipo_auditor"
              value={form.equipo_auditor}
              onChange={handleForm}
              placeholder="Equipo auditor"
            />

            <div className="aud-row three">
              <div>
                <label>Fecha programada</label>
                <input
                  type="date"
                  name="fecha_programada"
                  value={form.fecha_programada}
                  onChange={handleForm}
                />
              </div>

              <div>
                <label>Fecha inicio</label>
                <input
                  type="date"
                  name="fecha_inicio"
                  value={form.fecha_inicio}
                  onChange={handleForm}
                />
              </div>

              <div>
                <label>Fecha cierre</label>
                <input
                  type="date"
                  name="fecha_cierre"
                  value={form.fecha_cierre}
                  onChange={handleForm}
                />
              </div>
            </div>

            <textarea
              name="conclusiones"
              value={form.conclusiones}
              onChange={handleForm}
              placeholder="Conclusiones"
            />

            <textarea
              name="recomendaciones"
              value={form.recomendaciones}
              onChange={handleForm}
              placeholder="Recomendaciones"
            />

            <div className="aud-form-actions">
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

          <aside className="aud-info-panel">
            <h3>Ciclo Auditoría SST</h3>

            <div className="aud-timeline-mini">
              <span>1. Programar auditoría</span>
              <span>2. Ejecutar revisión</span>
              <span>3. Registrar hallazgos</span>
              <span>4. Generar plan de mejora</span>
              <span>5. Cerrar hallazgos</span>
            </div>

            <p>
              Los hallazgos tipo <strong>NO CONFORMIDAD</strong> pueden generar
              automáticamente una acción en el Plan de Mejoramiento SST.
            </p>
          </aside>
        </section>

        <section className="aud-list">
          <div className="aud-filters">
            <div className="aud-filter-title">
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

            <select name="estado" value={filtros.estado} onChange={handleFiltro}>
              <option value="">Todos los estados</option>
              {ESTADOS_AUDITORIA.map((estado) => (
                <option key={estado} value={estado}>
                  {estadoAuditoriaLabel[estado]}
                </option>
              ))}
            </select>

            <input
              name="buscar"
              value={filtros.buscar}
              onChange={handleFiltro}
              placeholder="Buscar auditoría..."
            />

            <button type="button" onClick={aplicarFiltros}>
              <Search size={16} />
              Filtrar
            </button>
          </div>

          <div className="aud-toolbar">
            <span>
              Mostrando {auditoriasPaginadas.length} de {auditorias.length}{" "}
              auditorías
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

          <div className="aud-table-wrap">
            <table className="aud-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Empresa</th>
                  <th>Auditoría</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                  <th>Hallazgos</th>
                  <th>Cierre</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {auditoriasPaginadas.map((auditoria) => (
                  <tr key={auditoria.id}>
                    <td>
                      <strong>{auditoria.codigo}</strong>
                    </td>

                    <td>{nombreEmpresa(auditoria.empresa_id)}</td>

                    <td>
                      <div className="aud-cell-main">
                        <strong>{auditoria.nombre}</strong>
                        <span>
                          {auditoria.tipo_auditoria} ·{" "}
                          {auditoria.auditor_lider || "Sin auditor"}
                        </span>
                      </div>
                    </td>

                    <td>
                      <span
                        className={`aud-status ${String(
                          auditoria.estado
                        ).toLowerCase()}`}
                      >
                        {estadoAuditoriaLabel[auditoria.estado] ||
                          auditoria.estado}
                      </span>
                    </td>

                    <td>{auditoria.fecha_programada || "Sin fecha"}</td>

                    <td>
                      <div className="aud-hallazgos-mini">
                        <span>Total: {auditoria.total_hallazgos}</span>
                        <span>NC: {auditoria.no_conformidades}</span>
                      </div>
                    </td>

                    <td>
                      <div className="aud-progress">
                        <span>{auditoria.porcentaje_cierre}%</span>
                        <div>
                          <b
                            style={{
                              width: `${auditoria.porcentaje_cierre}%`,
                            }}
                          />
                        </div>
                      </div>
                    </td>

                    <td>
                      <div className="aud-row-actions">
                        <button
                          type="button"
                          onClick={() => abrirModalHallazgos(auditoria)}
                          title="Timeline + Kanban de Hallazgos"
                        >
                          <Eye size={15} />
                        </button>

                        <button
                          type="button"
                          onClick={() => editarAuditoria(auditoria)}
                          title="Editar"
                        >
                          <Edit3 size={15} />
                        </button>

                        <button
                          type="button"
                          onClick={() => eliminarAuditoria(auditoria.id)}
                          title="Eliminar"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {auditoriasPaginadas.length === 0 && (
                  <tr>
                    <td colSpan="8" className="aud-empty">
                      No hay auditorías registradas.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="aud-pagination">
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

        <AuditoriaHallazgosModal
          abierto={modalHallazgos.abierto}
          auditoria={modalHallazgos.auditoria}
          onClose={cerrarModalHallazgos}
          onUpdated={async () => {
            await cargarDashboard();
            await cargarAuditorias();
          }}
        />
      </div>
    </AdminLayout>
  );
}
