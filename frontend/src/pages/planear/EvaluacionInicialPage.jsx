import React, { useEffect, useMemo, useState } from "react";
import {
  ClipboardList,
  RefreshCcw,
  Plus,
  Save,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Eye,
  Trash2,
  Flag,
  FileDown,
  FileSpreadsheet,
} from "lucide-react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

import AdminLayout from "../../layouts/AdminLayout";
import api from "../../api/axios";
import { toastSuccess, toastError, toastWarning, confirmAction } from "../../utils/toast";
import { evaluacionInicialApi } from "../../api/evaluacionInicialApi";
import "../../styles/evaluacion-inicial.css";

const RESPUESTAS = ["CUMPLE", "NO_CUMPLE", "NO_APLICA"];

export default function EvaluacionInicialPage() {
  const [empresas, setEmpresas] = useState([]);
  const [evaluaciones, setEvaluaciones] = useState([]);
  const [seleccionada, setSeleccionada] = useState(null);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    empresa_id: "",
    codigo: "EVAL-SST-001",
    nombre: "Evaluación Inicial SG-SST 2026",
    fecha_evaluacion: "",
    responsable: "",
    observaciones_generales: "",
    items: null,
  });

  const mostrarError = (error, mensaje) => {
    console.error(error);
    const detail = error?.response?.data?.detail;
    toastError("Error", `${mensaje}${detail ? `\n\nDetalle: ${detail}` : ""}`);
  };

  const descargarArchivo = async (url, nombreArchivo) => {
    if (!seleccionada?.id) {
      toastWarning("Advertencia", "Seleccione una evaluación inicial.");
      return;
    }

    try {
      const response = await api.get(url, { responseType: "blob" });

      const contentType = response?.headers?.["content-type"] || "application/octet-stream";
      const arrayBuffer = response.data instanceof Blob ? await response.data.arrayBuffer() : response.data;
      const bytes = new Uint8Array(arrayBuffer);
      let binary = "";
      for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
      const base64 = btoa(binary);
      const dataUrl = `data:${contentType};base64,${base64}`;
      const link = document.createElement("a");
      link.href = dataUrl;
      link.setAttribute("download", nombreArchivo);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      mostrarError(error, "No se pudo exportar el archivo.");
    }
  };

  const exportarPDF = () => {
    descargarArchivo(
      `/exportaciones-sst/evaluacion-inicial/pdf/${seleccionada.id}`,
      `evaluacion_inicial_${seleccionada.id}.pdf`
    );
  };

  const exportarExcel = () => {
    descargarArchivo(
      `/exportaciones-sst/evaluacion-inicial/excel/${seleccionada.id}`,
      `evaluacion_inicial_${seleccionada.id}.xlsx`
    );
  };

  const cargarDatos = async () => {
    try {
      setLoading(true);

      const [empresasRes, evaluacionesRes] = await Promise.all([
        api.get("/empresas/"),
        evaluacionInicialApi.listar(),
      ]);

      setEmpresas(empresasRes.data);
      setEvaluaciones(evaluacionesRes.data);

      if (!seleccionada && evaluacionesRes.data.length > 0) {
        setSeleccionada(evaluacionesRes.data[0]);
      }
    } catch (error) {
      mostrarError(error, "No se pudo cargar Evaluación Inicial SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const crearEvaluacion = async (e) => {
    e.preventDefault();

    if (!form.empresa_id) {
      toastWarning("Advertencia", "Seleccione una empresa.");
      return;
    }

    try {
      setLoading(true);

      const payload = {
        ...form,
        empresa_id: Number(form.empresa_id),
        fecha_evaluacion: form.fecha_evaluacion || null,
        items: null,
      };

      const res = await evaluacionInicialApi.crear(payload);

      setSeleccionada(res.data);
      await cargarDatos();

      toastSuccess("Éxito", "Evaluación Inicial SST creada correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo crear la evaluación inicial.");
    } finally {
      setLoading(false);
    }
  };

  const actualizarItem = async (item, campo, valor) => {
    try {
      const payload = {
        [campo]: campo === "puntaje" ? Number(valor) : valor,
      };

      await evaluacionInicialApi.actualizarItem(item.id, payload);

      const res = await evaluacionInicialApi.obtener(seleccionada.id);
      setSeleccionada(res.data);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo actualizar el ítem.");
    }
  };

  const finalizarEvaluacion = async () => {
    if (!seleccionada) {
      toastWarning("Advertencia", "Seleccione una evaluación inicial.");
      return;
    }

    if (!confirmAction("¿Desea finalizar esta evaluación inicial?")) return;

    try {
      const res = await evaluacionInicialApi.finalizar(seleccionada.id);
      setSeleccionada(res.data);
      await cargarDatos();
      toastSuccess("Éxito", "Evaluación finalizada correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo finalizar la evaluación.");
    }
  };

  const eliminarEvaluacion = async (id) => {
    if (!confirmAction("¿Desea desactivar esta evaluación?")) return;

    try {
      await evaluacionInicialApi.eliminar(id);
      setSeleccionada(null);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo eliminar la evaluación.");
    }
  };

  const kpis = useMemo(() => {
    if (!seleccionada) {
      return {
        total: 0,
        cumple: 0,
        noCumple: 0,
        noAplica: 0,
        porcentaje: 0,
        nivel: "SIN DATOS",
      };
    }

    return {
      total: seleccionada.total_items || 0,
      cumple: seleccionada.items_cumplen || 0,
      noCumple: seleccionada.items_no_cumplen || 0,
      noAplica: seleccionada.items_no_aplican || 0,
      porcentaje: seleccionada.porcentaje_cumplimiento || 0,
      nivel: seleccionada.nivel || "CRITICO",
    };
  }, [seleccionada]);

  const chartData = [
    { name: "Cumple", value: kpis.cumple },
    { name: "No cumple", value: kpis.noCumple },
    { name: "No aplica", value: kpis.noAplica },
  ];

  const colorNivel =
    kpis.nivel === "ACEPTABLE"
      ? "nivel-aceptable"
      : kpis.nivel === "MODERADO"
      ? "nivel-moderado"
      : "nivel-critico";

  return (
    <AdminLayout>
      <div className="eval-page">
        <section className="eval-hero">
          <div>
            <h2>Evaluación Inicial SST</h2>
            <p>Evalúa los estándares mínimos del SG-SST conforme a la Resolución 0312.</p>
          </div>

          <div className="eval-actions">
            <button
              className="btn-pdf"
              type="button"
              onClick={exportarPDF}
              disabled={!seleccionada}
            >
              <FileDown size={18} />
              Exportar PDF
            </button>

            <button
              className="btn-excel"
              type="button"
              onClick={exportarExcel}
              disabled={!seleccionada}
            >
              <FileSpreadsheet size={18} />
              Exportar Excel
            </button>

            <button className="btn-refresh" type="button" onClick={cargarDatos}>
              <RefreshCcw size={18} />
              Actualizar
            </button>

            <button className="btn-finalizar" type="button" onClick={finalizarEvaluacion}>
              <Flag size={18} />
              Finalizar
            </button>
          </div>
        </section>

        <section className="eval-kpis">
          <article>
            <ClipboardList size={24} />
            <div>
              <span>Total criterios</span>
              <strong>{kpis.total}</strong>
            </div>
          </article>

          <article>
            <CheckCircle2 size={24} />
            <div>
              <span>Cumplen</span>
              <strong>{kpis.cumple}</strong>
            </div>
          </article>

          <article>
            <XCircle size={24} />
            <div>
              <span>No cumplen</span>
              <strong>{kpis.noCumple}</strong>
            </div>
          </article>

          <article>
            <AlertTriangle size={24} />
            <div>
              <span>No aplican</span>
              <strong>{kpis.noAplica}</strong>
            </div>
          </article>
        </section>

        <section className="eval-grid">
          <form className="eval-form" onSubmit={crearEvaluacion}>
            <div className="form-title">
              <Plus size={22} />
              <div>
                <h3>Nueva evaluación</h3>
                <p>Al crearla se cargan automáticamente los criterios base.</p>
              </div>
            </div>

            <label>Empresa</label>
            <select
              name="empresa_id"
              value={form.empresa_id}
              onChange={(e) => setForm({ ...form, empresa_id: e.target.value })}
            >
              <option value="">Seleccione empresa</option>
              {empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>
                  {empresa.nombre}
                </option>
              ))}
            </select>

            <label>Código</label>
            <input
              value={form.codigo}
              onChange={(e) => setForm({ ...form, codigo: e.target.value })}
            />

            <label>Nombre</label>
            <input
              value={form.nombre}
              onChange={(e) => setForm({ ...form, nombre: e.target.value })}
            />

            <div className="form-row">
              <div>
                <label>Fecha evaluación</label>
                <input
                  type="date"
                  value={form.fecha_evaluacion}
                  onChange={(e) =>
                    setForm({ ...form, fecha_evaluacion: e.target.value })
                  }
                />
              </div>

              <div>
                <label>Responsable</label>
                <input
                  value={form.responsable}
                  onChange={(e) =>
                    setForm({ ...form, responsable: e.target.value })
                  }
                />
              </div>
            </div>

            <label>Observaciones generales</label>
            <textarea
              rows={3}
              value={form.observaciones_generales}
              onChange={(e) =>
                setForm({ ...form, observaciones_generales: e.target.value })
              }
            />

            <button className="btn-primary" disabled={loading}>
              <Save size={18} />
              Crear evaluación
            </button>
          </form>

          <aside className="eval-panel">
            <h3>Resumen de cumplimiento</h3>

            <div className={`eval-score ${colorNivel}`}>
              <strong>{kpis.porcentaje}%</strong>
              <span>{kpis.nivel}</span>
            </div>

            <div className="eval-progress-wrap">
              <div className="eval-progress-info">
                <span>Cumplimiento general SG-SST</span>
                <strong>{kpis.porcentaje}%</strong>
              </div>
              <div className="eval-progress-bar">
                <span style={{ width: `${kpis.porcentaje}%` }} />
              </div>
            </div>

            <div className="eval-chart">
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={chartData}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={70}
                    outerRadius={100}
                    paddingAngle={4}
                  >
                    <Cell fill="#22c55e" />
                    <Cell fill="#ef4444" />
                    <Cell fill="#f59e0b" />
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </aside>
        </section>

        <section className="eval-list">
          <h3>Histórico de evaluaciones</h3>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Código</th>
                  <th>Nombre</th>
                  <th>Responsable</th>
                  <th>Estado</th>
                  <th>%</th>
                  <th>Nivel</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {evaluaciones.map((ev) => (
                  <tr key={ev.id}>
                    <td>{ev.id}</td>
                    <td>{ev.codigo}</td>
                    <td>{ev.nombre}</td>
                    <td>{ev.responsable || "Sin responsable"}</td>
                    <td>
                      <span className={`estado estado-${ev.estado.toLowerCase()}`}>
                        {ev.estado}
                      </span>
                    </td>
                    <td>{ev.porcentaje_cumplimiento}%</td>
                    <td>
                      <span className={`nivel-pill ${ev.nivel.toLowerCase()}`}>
                        {ev.nivel}
                      </span>
                    </td>
                    <td>
                      <div className="table-actions">
                        <button onClick={() => setSeleccionada(ev)} title="Ver">
                          <Eye size={16} />
                        </button>

                        <button onClick={() => eliminarEvaluacion(ev.id)} title="Eliminar">
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {evaluaciones.length === 0 && (
                  <tr>
                    <td colSpan="8" className="empty">
                      No hay evaluaciones registradas.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {seleccionada && (
          <section className="eval-items">
            <div className="items-header">
              <div>
                <h3>{seleccionada.nombre}</h3>
                <p>
                  Código: {seleccionada.codigo} · Estado: {seleccionada.estado}
                </p>
              </div>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Numeral</th>
                    <th>Estándar</th>
                    <th>Criterio</th>
                    <th>Respuesta</th>
                    <th>Puntaje</th>
                    <th>Evidencia</th>
                    <th>Observaciones</th>
                  </tr>
                </thead>

                <tbody>
                  {seleccionada.items?.map((item) => (
                    <tr key={item.id}>
                      <td>{item.numeral}</td>
                      <td>{item.estandar}</td>
                      <td>{item.criterio}</td>
                      <td>
                        <select
                          className={`respuesta-select respuesta-${item.respuesta.toLowerCase()}`}
                          value={item.respuesta}
                          onChange={(e) =>
                            actualizarItem(item, "respuesta", e.target.value)
                          }
                        >
                          {RESPUESTAS.map((r) => (
                            <option key={r} value={r}>
                              {r}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <input
                          type="number"
                          value={item.puntaje}
                          onChange={(e) =>
                            actualizarItem(item, "puntaje", e.target.value)
                          }
                        />
                      </td>
                      <td>
                        <textarea
                          value={item.evidencia || ""}
                          onChange={(e) =>
                            actualizarItem(item, "evidencia", e.target.value)
                          }
                        />
                      </td>
                      <td>
                        <textarea
                          value={item.observaciones || ""}
                          onChange={(e) =>
                            actualizarItem(item, "observaciones", e.target.value)
                          }
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </div>
    </AdminLayout>
  );
}
