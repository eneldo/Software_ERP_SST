import React, { useEffect, useMemo, useState } from "react";
import {
  Target,
  Plus,
  Save,
  RefreshCcw,
  Edit3,
  Trash2,
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  FileDown,
  FileSpreadsheet,
} from "lucide-react";

import api from "../../api/axios";
import AdminLayout from "../../layouts/AdminLayout";
import "../../styles/objetivos-sst.css";

export default function ObjetivosSSTPage() {
  const [empresas, setEmpresas] = useState([]);
  const [objetivos, setObjetivos] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [empresaExportar, setEmpresaExportar] = useState("");

  const [form, setForm] = useState({
    empresa_id: "",
    objetivo: "",
    meta: "",
    indicador: "",
    responsable: "",
    fecha_inicio: "",
    fecha_fin: "",
    cumplimiento: 0,
    estado: "PLANIFICADO",
    observaciones: "",
  });

  const mostrarError = (error, mensajeBase) => {
    console.error(error);
    const detail = error?.response?.data?.detail;
    alert(`${mensajeBase}${detail ? `\n\nDetalle: ${detail}` : ""}`);
  };

  const cargarDatos = async () => {
    try {
      setLoading(true);

      const [empresasRes, objetivosRes] = await Promise.all([
        api.get("/empresas/"),
        api.get("/planear/objetivos-sst/"),
      ]);

      setEmpresas(empresasRes.data);
      setObjetivos(objetivosRes.data);

      if (!empresaExportar && empresasRes.data.length > 0) {
        setEmpresaExportar(empresasRes.data[0].id);
      }
    } catch (error) {
      mostrarError(error, "No se pudo cargar Objetivos SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const limpiarFormulario = () => {
    setEditandoId(null);
    setForm({
      empresa_id: "",
      objetivo: "",
      meta: "",
      indicador: "",
      responsable: "",
      fecha_inicio: "",
      fecha_fin: "",
      cumplimiento: 0,
      estado: "PLANIFICADO",
      observaciones: "",
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm({
      ...form,
      [name]: name === "cumplimiento" ? Number(value) : value,
    });
  };

  const guardarObjetivo = async (e) => {
    e.preventDefault();

    if (!form.empresa_id) {
      alert("Seleccione una empresa.");
      return;
    }

    if (!form.objetivo.trim() || !form.meta.trim() || !form.indicador.trim()) {
      alert("Objetivo, meta e indicador son obligatorios.");
      return;
    }

    const payload = {
      empresa_id: Number(form.empresa_id),
      objetivo: form.objetivo,
      meta: form.meta,
      indicador: form.indicador,
      responsable: form.responsable || null,
      fecha_inicio: form.fecha_inicio || null,
      fecha_fin: form.fecha_fin || null,
      cumplimiento: Number(form.cumplimiento || 0),
      estado: form.estado,
      observaciones: form.observaciones || null,
    };

    try {
      setLoading(true);

      if (editandoId) {
        await api.put(`/planear/objetivos-sst/${editandoId}`, payload);
      } else {
        await api.post("/planear/objetivos-sst/", payload);
      }

      limpiarFormulario();
      await cargarDatos();
      alert("Objetivo SST guardado correctamente.");
    } catch (error) {
      mostrarError(error, "Error guardando Objetivo SST.");
    } finally {
      setLoading(false);
    }
  };

  const editarObjetivo = (item) => {
    setEditandoId(item.id);
    setForm({
      empresa_id: item.empresa_id || "",
      objetivo: item.objetivo || "",
      meta: item.meta || "",
      indicador: item.indicador || "",
      responsable: item.responsable || "",
      fecha_inicio: item.fecha_inicio || "",
      fecha_fin: item.fecha_fin || "",
      cumplimiento: item.cumplimiento || 0,
      estado: item.estado || "PLANIFICADO",
      observaciones: item.observaciones || "",
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminarObjetivo = async (id) => {
    if (!confirm("¿Desea desactivar este objetivo SST?")) return;

    try {
      await api.delete(`/planear/objetivos-sst/${id}`);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo eliminar el objetivo.");
    }
  };

  const descargarArchivo = async (url, nombreArchivo) => {
    if (!empresaExportar) {
      alert("Seleccione una empresa para exportar.");
      return;
    }

    try {
      const response = await api.get(url, {
        responseType: "blob",
      });

      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = blobUrl;
      link.setAttribute("download", nombreArchivo);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      mostrarError(error, "No se pudo exportar el archivo.");
    }
  };

  const exportarPDF = () => {
    descargarArchivo(
      `/exportaciones-sst/objetivos/pdf/${empresaExportar}`,
      "objetivos_sst.pdf"
    );
  };

  const exportarExcel = () => {
    descargarArchivo(
      `/exportaciones-sst/objetivos/excel/${empresaExportar}`,
      "objetivos_sst.xlsx"
    );
  };

  const kpis = useMemo(() => {
    const activos = objetivos.filter((o) => o.activo !== false);
    const cumplidos = activos.filter((o) => o.estado === "CUMPLIDO").length;
    const proceso = activos.filter((o) => o.estado === "EN_PROCESO").length;
    const vencidos = activos.filter((o) => o.estado === "VENCIDO").length;

    const promedio =
      activos.length > 0
        ? Math.round(
            activos.reduce(
              (acc, item) => acc + Number(item.cumplimiento || 0),
              0
            ) / activos.length
          )
        : 0;

    return {
      total: activos.length,
      cumplidos,
      proceso,
      vencidos,
      promedio,
    };
  }, [objetivos]);

  return (
    <AdminLayout>
      <div className="objetivos-page">
        <section className="objetivos-hero">
          <div>
            <h2>Objetivos SST</h2>
            <p>Gestiona objetivos, metas, indicadores y cumplimiento del SG-SST.</p>
          </div>

          <div className="objetivos-actions">
            <select
              value={empresaExportar}
              onChange={(e) => setEmpresaExportar(e.target.value)}
              className="empresa-export-select"
            >
              <option value="">Empresa para exportar</option>
              {empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>
                  {empresa.nombre}
                </option>
              ))}
            </select>

            <button className="btn-export-pdf" onClick={exportarPDF}>
              <FileDown size={18} />
              Exportar PDF
            </button>

            <button className="btn-export-excel" onClick={exportarExcel}>
              <FileSpreadsheet size={18} />
              Exportar Excel
            </button>

            <button className="objetivos-refresh" onClick={cargarDatos}>
              <RefreshCcw size={18} />
              Actualizar
            </button>
          </div>
        </section>

        <section className="objetivos-kpi-grid">
          <article className="objetivo-kpi-card">
            <Target size={24} />
            <div>
              <span>Total objetivos</span>
              <strong>{kpis.total}</strong>
            </div>
          </article>

          <article className="objetivo-kpi-card">
            <CheckCircle2 size={24} />
            <div>
              <span>Cumplidos</span>
              <strong>{kpis.cumplidos}</strong>
            </div>
          </article>

          <article className="objetivo-kpi-card">
            <BarChart3 size={24} />
            <div>
              <span>En proceso</span>
              <strong>{kpis.proceso}</strong>
            </div>
          </article>

          <article className="objetivo-kpi-card">
            <AlertTriangle size={24} />
            <div>
              <span>Vencidos</span>
              <strong>{kpis.vencidos}</strong>
            </div>
          </article>
        </section>

        <section className="objetivos-main-grid">
          <form className="objetivos-form" onSubmit={guardarObjetivo}>
            <div className="form-title">
              <Target size={22} />
              <div>
                <h3>{editandoId ? "Editar objetivo SST" : "Nuevo objetivo SST"}</h3>
                <p>Defina objetivo, meta, indicador, responsable y cumplimiento.</p>
              </div>
            </div>

            <label>Empresa</label>
            <select name="empresa_id" value={form.empresa_id} onChange={handleChange}>
              <option value="">Seleccione empresa</option>
              {empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>
                  {empresa.nombre}
                </option>
              ))}
            </select>

            <label>Objetivo SST</label>
            <textarea
              name="objetivo"
              value={form.objetivo}
              onChange={handleChange}
              rows={3}
              placeholder="Ej: Reducir los accidentes de trabajo..."
            />

            <label>Meta</label>
            <input
              name="meta"
              value={form.meta}
              onChange={handleChange}
              placeholder="Ej: Disminuir accidentalidad en 20%"
            />

            <label>Indicador</label>
            <input
              name="indicador"
              value={form.indicador}
              onChange={handleChange}
              placeholder="Ej: Tasa de accidentalidad mensual"
            />

            <div className="form-row">
              <div>
                <label>Responsable</label>
                <input
                  name="responsable"
                  value={form.responsable}
                  onChange={handleChange}
                  placeholder="Responsable SST"
                />
              </div>

              <div>
                <label>Estado</label>
                <select name="estado" value={form.estado} onChange={handleChange}>
                  <option value="PLANIFICADO">PLANIFICADO</option>
                  <option value="EN_PROCESO">EN PROCESO</option>
                  <option value="CUMPLIDO">CUMPLIDO</option>
                  <option value="VENCIDO">VENCIDO</option>
                  <option value="CANCELADO">CANCELADO</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div>
                <label>Fecha inicio</label>
                <input
                  type="date"
                  name="fecha_inicio"
                  value={form.fecha_inicio}
                  onChange={handleChange}
                />
              </div>

              <div>
                <label>Fecha fin</label>
                <input
                  type="date"
                  name="fecha_fin"
                  value={form.fecha_fin}
                  onChange={handleChange}
                />
              </div>
            </div>

            <label>Cumplimiento: {form.cumplimiento}%</label>
            <input
              type="range"
              name="cumplimiento"
              min="0"
              max="100"
              value={form.cumplimiento}
              onChange={handleChange}
            />

            <label>Observaciones</label>
            <textarea
              name="observaciones"
              value={form.observaciones}
              onChange={handleChange}
              rows={3}
            />

            <div className="form-actions">
              <button className="btn-primary" type="submit" disabled={loading}>
                <Save size={18} />
                {editandoId ? "Actualizar" : "Guardar"}
              </button>

              <button className="btn-secondary" type="button" onClick={limpiarFormulario}>
                <Plus size={18} />
                Nuevo
              </button>
            </div>
          </form>

          <aside className="objetivos-panel">
            <h3>Resumen de cumplimiento</h3>
            <div className="cumplimiento-ring">
              <strong>{kpis.promedio}%</strong>
              <span>Promedio general</span>
            </div>

            <div className="objetivos-help">
              <h4>Estados sugeridos</h4>
              <p>
                Use <b>PLANIFICADO</b> para objetivos nuevos, <b>EN_PROCESO</b>{" "}
                para seguimiento, <b>CUMPLIDO</b> al alcanzar la meta y{" "}
                <b>VENCIDO</b> si supera la fecha fin sin completar.
              </p>
            </div>
          </aside>
        </section>

        <section className="objetivos-list">
          <h3>Histórico de objetivos SST</h3>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Objetivo</th>
                  <th>Meta</th>
                  <th>Indicador</th>
                  <th>Responsable</th>
                  <th>Estado</th>
                  <th>Cumplimiento</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {objetivos.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.objetivo}</td>
                    <td>{item.meta}</td>
                    <td>{item.indicador}</td>
                    <td>{item.responsable || "Sin asignar"}</td>
                    <td>
                      <span className={`estado estado-${item.estado.toLowerCase()}`}>
                        {item.estado}
                      </span>
                    </td>
                    <td>
                      <div className="progress-cell">
                        <div className="progress-bar">
                          <span style={{ width: `${item.cumplimiento || 0}%` }} />
                        </div>
                        <small>{item.cumplimiento || 0}%</small>
                      </div>
                    </td>
                    <td>
                      <div className="table-actions">
                        <button title="Editar" onClick={() => editarObjetivo(item)}>
                          <Edit3 size={16} />
                        </button>

                        <button title="Eliminar" onClick={() => eliminarObjetivo(item.id)}>
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {objetivos.length === 0 && (
                  <tr>
                    <td colSpan="8" className="empty">
                      No hay objetivos SST registrados.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </AdminLayout>
  );
}
