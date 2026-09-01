import React, { useEffect, useMemo, useState } from "react";
import {
  CalendarCheck,
  Database,
  Edit3,
  Eye,
  FileDown,
  FileSpreadsheet,
  Plus,
  RefreshCcw,
  Save,
  Trash2,
  Upload,
  CheckCircle2,
  Download,
} from "lucide-react";

import AdminLayout from "../../layouts/AdminLayout";
import api from "../../api/axios";
import { resolveFileUrl } from "../../utils/fileUrl";
import "../../styles/plan-anual.css";

const API_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const ESTADOS = [
  "PLANIFICADO",
  "EN_PROCESO",
  "EJECUTADO",
  "CANCELADO",
  "VENCIDO",
];

export default function PlanAnualPage() {
  const [empresas, setEmpresas] = useState([]);
  const [items, setItems] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [empresaExportar, setEmpresaExportar] = useState("");
  const [loading, setLoading] = useState(false);

  const [pagina, setPagina] = useState(1);
  const [porPagina, setPorPagina] = useState(10);

  const [filtros, setFiltros] = useState({
    empresa_id: "",
    buscar: "",
    estado: "",
    responsable: "",
  });

  const [form, setForm] = useState({
    empresa_id: "",
    codigo: "PA-SST-001",
    actividad: "",
    objetivo: "",
    responsable: "",
    recurso_humano: "",
    recurso_fisico: "",
    recurso_financiero: "",
    presupuesto: 0,
    indicador: "",
    meta: "",
    fecha_inicio: "",
    fecha_fin: "",
    estado: "PLANIFICADO",
    porcentaje_avance: 0,
    evidencia: "",
    observaciones: "",
  });

  const mostrarError = (error, mensaje) => {
    console.error(error);
    const detail = error?.response?.data?.detail;
    alert(`${mensaje}${detail ? `\n\nDetalle: ${detail}` : ""}`);
  };

  const cargarDatos = async () => {
    try {
      setLoading(true);

      const params = {};
      Object.entries(filtros).forEach(([key, value]) => {
        if (value) params[key] = value;
      });

      const [empresasRes, planRes] = await Promise.all([
        api.get("/empresas/"),
        api.get("/planear/plan-anual/", { params }),
      ]);

      setEmpresas(empresasRes.data);
      setItems(planRes.data);
      setPagina(1);

      if (!empresaExportar && empresasRes.data.length > 0) {
        setEmpresaExportar(empresasRes.data[0].id);
      }
    } catch (error) {
      mostrarError(error, "No se pudo cargar el Plan Anual SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const kpis = useMemo(() => {
    const total = items.length;
    const planificados = items.filter((i) => i.estado === "PLANIFICADO").length;
    const enProceso = items.filter((i) => i.estado === "EN_PROCESO").length;
    const ejecutados = items.filter((i) => i.estado === "EJECUTADO").length;
    const vencidos = items.filter((i) => i.estado === "VENCIDO").length;
    const cancelados = items.filter((i) => i.estado === "CANCELADO").length;
    const cumplimiento = total > 0 ? Math.round((ejecutados / total) * 100) : 0;
    const presupuesto = items.reduce(
      (acc, item) => acc + Number(item.presupuesto || 0),
      0
    );

    return {
      total,
      planificados,
      enProceso,
      ejecutados,
      vencidos,
      cancelados,
      cumplimiento,
      presupuesto,
    };
  }, [items]);

  const totalPaginas = Math.max(1, Math.ceil(items.length / porPagina));
  const inicio = (pagina - 1) * porPagina;
  const fin = inicio + porPagina;
  const itemsPaginados = items.slice(inicio, fin);

  const limpiar = () => {
    setEditandoId(null);
    setForm({
      empresa_id: "",
      codigo: "PA-SST-001",
      actividad: "",
      objetivo: "",
      responsable: "",
      recurso_humano: "",
      recurso_fisico: "",
      recurso_financiero: "",
      presupuesto: 0,
      indicador: "",
      meta: "",
      fecha_inicio: "",
      fecha_fin: "",
      estado: "PLANIFICADO",
      porcentaje_avance: 0,
      evidencia: "",
      observaciones: "",
    });
  };

  const handleForm = (e) => {
    const { name, value } = e.target;

    setForm({
      ...form,
      [name]:
        name === "presupuesto" || name === "porcentaje_avance"
          ? Number(value)
          : value,
    });
  };

  const handleFiltro = (e) => {
    setFiltros({ ...filtros, [e.target.name]: e.target.value });
  };

  const guardar = async (e) => {
    e.preventDefault();

    if (!form.empresa_id || !form.actividad) {
      alert("Empresa y actividad son obligatorias.");
      return;
    }

    const payload = {
      ...form,
      empresa_id: Number(form.empresa_id),
      presupuesto: Number(form.presupuesto || 0),
      porcentaje_avance: Number(form.porcentaje_avance || 0),
      fecha_inicio: form.fecha_inicio || null,
      fecha_fin: form.fecha_fin || null,
    };

    try {
      setLoading(true);

      if (editandoId) {
        await api.put(`/planear/plan-anual/${editandoId}`, payload);
      } else {
        await api.post("/planear/plan-anual/", payload);
      }

      limpiar();
      await cargarDatos();
      alert("Actividad guardada correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo guardar la actividad.");
    } finally {
      setLoading(false);
    }
  };

  const editar = (item) => {
    setEditandoId(item.id);

    setForm({
      empresa_id: item.empresa_id || "",
      codigo: item.codigo || "PA-SST-001",
      actividad: item.actividad || "",
      objetivo: item.objetivo || "",
      responsable: item.responsable || "",
      recurso_humano: item.recurso_humano || "",
      recurso_fisico: item.recurso_fisico || "",
      recurso_financiero: item.recurso_financiero || "",
      presupuesto: Number(item.presupuesto || 0),
      indicador: item.indicador || "",
      meta: item.meta || "",
      fecha_inicio: item.fecha_inicio || "",
      fecha_fin: item.fecha_fin || "",
      estado: item.estado || "PLANIFICADO",
      porcentaje_avance: Number(item.porcentaje_avance || 0),
      evidencia: item.evidencia || "",
      observaciones: item.observaciones || "",
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminar = async (id) => {
    if (!confirm("¿Desea eliminar esta actividad del Plan Anual SST?")) return;

    try {
      await api.delete(`/planear/plan-anual/${id}`);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo eliminar la actividad.");
    }
  };

  const finalizar = async (id) => {
    if (!confirm("¿Desea finalizar esta actividad?")) return;

    try {
      await api.patch(`/planear/plan-anual/${id}/finalizar`);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo finalizar la actividad.");
    }
  };

  const cargarBase = async () => {
    if (!empresaExportar) {
      alert("Seleccione empresa.");
      return;
    }

    try {
      await api.post(`/planear/plan-anual/cargar-base/${empresaExportar}`);
      await cargarDatos();
      alert("Base del Plan Anual SST cargada correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo cargar la base del Plan Anual SST.");
    }
  };

  const descargar = async (url, nombre) => {
    if (!empresaExportar) {
      alert("Seleccione empresa para exportar.");
      return;
    }

    try {
      const res = await api.get(url, { responseType: "blob" });
      const blobUrl = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");

      link.href = blobUrl;
      link.setAttribute("download", nombre);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      mostrarError(error, "No se pudo descargar el archivo.");
    }
  };

  const exportarPDF = () =>
    descargar(
      `/exportaciones-sst/plan-anual/pdf/${empresaExportar}`,
      "plan_anual_sst.pdf"
    );

  const exportarExcel = () =>
    descargar(
      `/exportaciones-sst/plan-anual/excel/${empresaExportar}`,
      "plan_anual_sst.xlsx"
    );

  const subirEvidencia = async (item, file) => {
    if (!file) return;

    const data = new FormData();
    data.append("descripcion", `Evidencia Plan Anual SST ${item.codigo}`);
    data.append("file", file);

    try {
      await api.post(`/planear/plan-anual/${item.id}/evidencia`, data, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await cargarDatos();
      alert("Evidencia cargada correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo subir la evidencia.");
    }
  };

  const abrirArchivo = (url) => {
    if (url) window.open(resolveFileUrl(url), "_blank");
  };

  const descargarArchivo = (url, nombre = "evidencia") => {
    if (!url) return;

    const link = document.createElement("a");
    link.href = resolveFileUrl(url);
    link.setAttribute("download", nombre);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const cambiarPorPagina = (e) => {
    setPorPagina(Number(e.target.value));
    setPagina(1);
  };

  return (
    <AdminLayout>
      <div className="plan-anual-page">
        <section className="pa-hero">
          <div>
            <h2>Plan Anual SST</h2>
            <p>Programa actividades, responsables, presupuesto y seguimiento del SG-SST.</p>
          </div>

          <div className="pa-actions">
            <select
              value={empresaExportar}
              onChange={(e) => setEmpresaExportar(e.target.value)}
            >
              <option value="">Empresa</option>
              {empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>
                  {empresa.nombre}
                </option>
              ))}
            </select>

            <button type="button" onClick={cargarBase} className="btn-base">
              <Database size={17} /> Base
            </button>

            <button type="button" onClick={exportarPDF} className="btn-pdf">
              <FileDown size={17} /> PDF
            </button>

            <button type="button" onClick={exportarExcel} className="btn-excel">
              <FileSpreadsheet size={17} /> Excel
            </button>

            <button type="button" onClick={cargarDatos} className="btn-refresh">
              <RefreshCcw size={17} /> Actualizar
            </button>
          </div>
        </section>

        <section className="pa-kpis">
          <article>
            <CalendarCheck />
            <span>Total actividades</span>
            <strong>{kpis.total}</strong>
          </article>

          <article>
            <CalendarCheck />
            <span>Planificadas</span>
            <strong>{kpis.planificados}</strong>
          </article>

          <article>
            <CalendarCheck />
            <span>En proceso</span>
            <strong>{kpis.enProceso}</strong>
          </article>

          <article>
            <CheckCircle2 />
            <span>Ejecutadas</span>
            <strong>{kpis.ejecutados}</strong>
          </article>

          <article>
            <CalendarCheck />
            <span>Vencidas</span>
            <strong>{kpis.vencidos}</strong>
          </article>
        </section>

        <section className="pa-grid">
          <form className="pa-form" onSubmit={guardar}>
            <h3>{editandoId ? "Editar actividad" : "Nueva actividad"}</h3>

            <label>Empresa</label>
            <select name="empresa_id" value={form.empresa_id} onChange={handleForm}>
              <option value="">Seleccione empresa</option>
              {empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>
                  {empresa.nombre}
                </option>
              ))}
            </select>

            <div className="form-row">
              <input
                name="codigo"
                value={form.codigo}
                onChange={handleForm}
                placeholder="Código"
              />

              <input
                name="responsable"
                value={form.responsable}
                onChange={handleForm}
                placeholder="Responsable"
              />
            </div>

            <textarea
              name="actividad"
              value={form.actividad}
              onChange={handleForm}
              placeholder="Actividad del Plan Anual SST"
            />

            <textarea
              name="objetivo"
              value={form.objetivo}
              onChange={handleForm}
              placeholder="Objetivo"
            />

            <div className="form-row three">
              <textarea
                name="recurso_humano"
                value={form.recurso_humano}
                onChange={handleForm}
                placeholder="Recurso humano"
              />

              <textarea
                name="recurso_fisico"
                value={form.recurso_fisico}
                onChange={handleForm}
                placeholder="Recurso físico"
              />

              <textarea
                name="recurso_financiero"
                value={form.recurso_financiero}
                onChange={handleForm}
                placeholder="Recurso financiero"
              />
            </div>

            <div className="form-row">
              <input
                type="number"
                name="presupuesto"
                value={form.presupuesto}
                onChange={handleForm}
                placeholder="Presupuesto"
                min="0"
              />

              <input
                name="indicador"
                value={form.indicador}
                onChange={handleForm}
                placeholder="Indicador"
              />
            </div>

            <input
              name="meta"
              value={form.meta}
              onChange={handleForm}
              placeholder="Meta"
            />

            <div className="form-row">
              <input
                type="date"
                name="fecha_inicio"
                value={form.fecha_inicio}
                onChange={handleForm}
              />

              <input
                type="date"
                name="fecha_fin"
                value={form.fecha_fin}
                onChange={handleForm}
              />
            </div>

            <div className="form-row">
              <select name="estado" value={form.estado} onChange={handleForm}>
                {ESTADOS.map((estado) => (
                  <option key={estado} value={estado}>
                    {estado}
                  </option>
                ))}
              </select>

              <div>
                <label>Avance: {form.porcentaje_avance}%</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  name="porcentaje_avance"
                  value={form.porcentaje_avance}
                  onChange={handleForm}
                />
              </div>
            </div>

            <div className={`pa-progress-preview ${form.estado.toLowerCase()}`}>
              <span>Avance de actividad</span>
              <strong>{form.porcentaje_avance}%</strong>
              <div>
                <b style={{ width: `${form.porcentaje_avance}%` }} />
              </div>
            </div>

            <textarea
              name="observaciones"
              value={form.observaciones}
              onChange={handleForm}
              placeholder="Observaciones"
            />

            <div className="form-actions">
              <button className="btn-primary" type="submit" disabled={loading}>
                <Save size={17} /> {editandoId ? "Actualizar" : "Guardar"}
              </button>

              <button type="button" className="btn-secondary" onClick={limpiar}>
                <Plus size={17} /> Nuevo
              </button>
            </div>
          </form>

          <aside className="pa-panel">
            <h3>Resumen del Plan Anual</h3>
            <strong>{kpis.cumplimiento}%</strong>
            <p>Cumplimiento general del Plan Anual SST.</p>

            <div className="pa-progress">
              <span style={{ width: `${kpis.cumplimiento}%` }} />
            </div>

            <div className="pa-mini-grid">
              <div>
                <span>Presupuesto</span>
                <strong>
                  {kpis.presupuesto.toLocaleString("es-CO", {
                    style: "currency",
                    currency: "COP",
                    maximumFractionDigits: 0,
                  })}
                </strong>
              </div>

              <div>
                <span>Canceladas</span>
                <strong>{kpis.cancelados}</strong>
              </div>
            </div>
          </aside>
        </section>

        <section className="pa-list">
          <div className="pa-filters">
            <input
              name="buscar"
              value={filtros.buscar}
              onChange={handleFiltro}
              placeholder="Buscar código, actividad, objetivo..."
            />

            <input
              name="responsable"
              value={filtros.responsable}
              onChange={handleFiltro}
              placeholder="Responsable"
            />

            <select name="estado" value={filtros.estado} onChange={handleFiltro}>
              <option value="">Todos los estados</option>
              {ESTADOS.map((estado) => (
                <option key={estado} value={estado}>
                  {estado}
                </option>
              ))}
            </select>

            <button type="button" onClick={cargarDatos}>
              Filtrar
            </button>
          </div>

          <div className="pa-toolbar">
            <span>
              Mostrando {itemsPaginados.length} de {items.length} registros
            </span>

            <div className="pa-page-size">
              <label>Registros por página</label>
              <select value={porPagina} onChange={cambiarPorPagina}>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
          </div>

          <div className="table-wrap pa-table-wrap">
            <table className="pa-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Actividad</th>
                  <th>Responsable</th>
                  <th>Estado</th>
                  <th>Avance</th>
                  <th>Presupuesto</th>
                  <th>Inicio</th>
                  <th>Fin</th>
                  <th>Evidencia</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {itemsPaginados.map((item) => (
                  <tr key={item.id}>
                    <td>{item.codigo}</td>
                    <td>{item.actividad}</td>
                    <td>{item.responsable || "No definido"}</td>
                    <td>
                      <span className={`pa-pill ${String(item.estado).toLowerCase()}`}>
                        {item.estado}
                      </span>
                    </td>
                    <td>
                      <div className="pa-table-progress">
                        <span>{item.porcentaje_avance}%</span>
                        <b style={{ width: `${item.porcentaje_avance}%` }} />
                      </div>
                    </td>
                    <td>
                      {Number(item.presupuesto || 0).toLocaleString("es-CO", {
                        style: "currency",
                        currency: "COP",
                        maximumFractionDigits: 0,
                      })}
                    </td>
                    <td>{item.fecha_inicio || "Sin fecha"}</td>
                    <td>{item.fecha_fin || "Sin fecha"}</td>
                    <td>
                      {item.archivo_url ? (
                        <div className="pa-evidence-group">
                          <span className="pa-evidencia-ok">✓ Evidencia</span>

                          <button
                            type="button"
                            className="btn-mini"
                            onClick={() => abrirArchivo(item.archivo_url)}
                          >
                            <Eye size={14} />
                            Ver
                          </button>

                          <button
                            type="button"
                            className="btn-mini"
                            onClick={() =>
                              descargarArchivo(
                                item.archivo_url,
                                item.archivo_nombre || "evidencia"
                              )
                            }
                          >
                            <Download size={14} />
                            Descargar
                          </button>

                          <label className="btn-upload-mini">
                            <Upload size={14} />
                            Reemplazar
                            <input
                              type="file"
                              hidden
                              onChange={(e) =>
                                subirEvidencia(item, e.target.files[0])
                              }
                            />
                          </label>
                        </div>
                      ) : (
                        <label className="btn-upload-mini">
                          <Upload size={14} />
                          Cargar
                          <input
                            type="file"
                            hidden
                            onChange={(e) =>
                              subirEvidencia(item, e.target.files[0])
                            }
                          />
                        </label>
                      )}
                    </td>
                    <td>
                      <div className="pa-row-actions">
                        <button
                          type="button"
                          onClick={() => editar(item)}
                          title="Editar"
                        >
                          <Edit3 size={15} />
                        </button>

                        <button
                          type="button"
                          onClick={() => finalizar(item.id)}
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

                {itemsPaginados.length === 0 && (
                  <tr>
                    <td colSpan="10" className="empty">
                      No hay actividades registradas en el Plan Anual SST.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="pa-pagination">
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
              onClick={() => setPagina((prev) => Math.min(totalPaginas, prev + 1))}
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
      </div>
    </AdminLayout>
  );
}
