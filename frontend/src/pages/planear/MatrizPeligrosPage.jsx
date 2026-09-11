import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Database,
  Edit3,
  Eye,
  FileDown,
  FileSpreadsheet,
  Plus,
  RefreshCcw,
  Save,
  ShieldAlert,
  Trash2,
  Upload,
} from "lucide-react";

import AdminLayout from "../../layouts/AdminLayout";
import api from "../../api/axios";
import { toastSuccess, toastError, toastWarning, confirmAction } from "../../utils/toast";
import { resolveFileUrl } from "../../utils/fileUrl";
import "../../styles/matriz-peligros.css";

import { API_BASE_URL } from "../../config/env";

const CLASIFICACIONES = [
  "Biomecánico",
  "Químico",
  "Físico",
  "Biológico",
  "Psicosocial",
  "Eléctrico",
  "Mecánico",
  "Locativo",
  "Tecnológico",
  "Natural",
  "Público",
  "Seguridad",
];

const ESTADOS = ["PENDIENTE", "CONTROLADO", "EN_SEGUIMIENTO", "CERRADO"];

export default function MatrizPeligrosPage() {
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
    clasificacion_peligro: "",
    interpretacion_riesgo: "",
    estado: "",
  });

  const [form, setForm] = useState({
    empresa_id: "",
    codigo: "MP-SST-001",
    proceso: "",
    actividad: "",
    tarea: "",
    peligro: "",
    clasificacion_peligro: "Biomecánico",
    efectos_posibles: "",
    controles_fuente: "",
    controles_medio: "",
    controles_individuo: "",
    probabilidad: 1,
    consecuencia: 1,
    medidas_intervencion: "",
    responsable: "",
    fecha_revision: "",
    fecha_vencimiento: "",
    estado: "PENDIENTE",
    evidencia: "",
    observaciones: "",
  });

  const mostrarError = (error, mensaje) => {
    console.error(error);
    const detail = error?.response?.data?.detail;
    toastError("Error", `${mensaje}${detail ? `\n\nDetalle: ${detail}` : ""}`);
  };

  const calcularPreview = useMemo(() => {
    const probabilidad = Number(form.probabilidad || 1);
    const consecuencia = Number(form.consecuencia || 1);
    const nivel = probabilidad * consecuencia;

    if (nivel <= 4) {
      return {
        nivel,
        interpretacion: "BAJO",
        aceptabilidad: "ACEPTABLE",
        clase: "bajo",
      };
    }

    if (nivel <= 9) {
      return {
        nivel,
        interpretacion: "MEDIO",
        aceptabilidad: "MEJORABLE",
        clase: "medio",
      };
    }

    if (nivel <= 16) {
      return {
        nivel,
        interpretacion: "ALTO",
        aceptabilidad: "NO ACEPTABLE",
        clase: "alto",
      };
    }

    return {
      nivel,
      interpretacion: "CRITICO",
      aceptabilidad: "NO ACEPTABLE CRÍTICO",
      clase: "critico",
    };
  }, [form.probabilidad, form.consecuencia]);

  const cargarDatos = async () => {
    try {
      setLoading(true);

      const params = {};
      Object.entries(filtros).forEach(([key, value]) => {
        if (value) params[key] = value;
      });

      const [empresasRes, peligrosRes] = await Promise.all([
        api.get("/empresas/"),
        api.get("/planear/matriz-peligros/", { params }),
      ]);

      setEmpresas(empresasRes.data);
      setItems(peligrosRes.data);
      setPagina(1);

      if (!empresaExportar && empresasRes.data.length > 0) {
        setEmpresaExportar(empresasRes.data[0].id);
      }
    } catch (error) {
      mostrarError(error, "No se pudo cargar la Matriz de Peligros.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const kpis = useMemo(() => {
    const total = items.length;
    const bajos = items.filter((i) => i.interpretacion_riesgo === "BAJO").length;
    const medios = items.filter((i) => i.interpretacion_riesgo === "MEDIO").length;
    const altos = items.filter((i) => i.interpretacion_riesgo === "ALTO").length;
    const criticos = items.filter((i) => i.interpretacion_riesgo === "CRITICO").length;
    const pendientes = items.filter((i) => i.estado === "PENDIENTE").length;
    const porcentajeCritico = total > 0 ? Math.round((criticos / total) * 100) : 0;

    return {
      total,
      bajos,
      medios,
      altos,
      criticos,
      pendientes,
      porcentajeCritico,
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
      codigo: "MP-SST-001",
      proceso: "",
      actividad: "",
      tarea: "",
      peligro: "",
      clasificacion_peligro: "Biomecánico",
      efectos_posibles: "",
      controles_fuente: "",
      controles_medio: "",
      controles_individuo: "",
      probabilidad: 1,
      consecuencia: 1,
      medidas_intervencion: "",
      responsable: "",
      fecha_revision: "",
      fecha_vencimiento: "",
      estado: "PENDIENTE",
      evidencia: "",
      observaciones: "",
    });
  };

  const handleForm = (e) => {
    const { name, value } = e.target;

    setForm({
      ...form,
      [name]: name === "probabilidad" || name === "consecuencia" ? Number(value) : value,
    });
  };

  const handleFiltro = (e) => {
    setFiltros({ ...filtros, [e.target.name]: e.target.value });
  };

  const guardar = async (e) => {
    e.preventDefault();

    if (!form.empresa_id || !form.proceso || !form.actividad || !form.peligro) {
      toastWarning("Advertencia", "Empresa, proceso, actividad y peligro son obligatorios.");
      return;
    }

    const payload = {
      ...form,
      empresa_id: Number(form.empresa_id),
      probabilidad: Number(form.probabilidad || 1),
      consecuencia: Number(form.consecuencia || 1),
      fecha_revision: form.fecha_revision || null,
      fecha_vencimiento: form.fecha_vencimiento || null,
    };

    try {
      setLoading(true);

      if (editandoId) {
        await api.put(`/planear/matriz-peligros/${editandoId}`, payload);
      } else {
        await api.post("/planear/matriz-peligros/", payload);
      }

      limpiar();
      await cargarDatos();
      toastSuccess("Éxito", "Peligro guardado correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo guardar el peligro.");
    } finally {
      setLoading(false);
    }
  };

  const editar = (item) => {
    setEditandoId(item.id);

    setForm({
      empresa_id: item.empresa_id || "",
      codigo: item.codigo || "MP-SST-001",
      proceso: item.proceso || "",
      actividad: item.actividad || "",
      tarea: item.tarea || "",
      peligro: item.peligro || "",
      clasificacion_peligro: item.clasificacion_peligro || "Biomecánico",
      efectos_posibles: item.efectos_posibles || "",
      controles_fuente: item.controles_fuente || "",
      controles_medio: item.controles_medio || "",
      controles_individuo: item.controles_individuo || "",
      probabilidad: item.probabilidad || 1,
      consecuencia: item.consecuencia || 1,
      medidas_intervencion: item.medidas_intervencion || "",
      responsable: item.responsable || "",
      fecha_revision: item.fecha_revision || "",
      fecha_vencimiento: item.fecha_vencimiento || "",
      estado: item.estado || "PENDIENTE",
      evidencia: item.evidencia || "",
      observaciones: item.observaciones || "",
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminar = async (id) => {
    if (!confirmAction("¿Desea eliminar este peligro?")) return;

    try {
      await api.delete(`/planear/matriz-peligros/${id}`);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo eliminar el peligro.");
    }
  };

  const cargarBase = async () => {
    if (!empresaExportar) {
      toastWarning("Advertencia", "Seleccione empresa.");
      return;
    }

    try {
      await api.post(`/planear/matriz-peligros/cargar-base/${empresaExportar}`);
      await cargarDatos();
      toastSuccess("Éxito", "Base de peligros cargada correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo cargar la base de peligros.");
    }
  };

  const descargar = async (url, nombre) => {
    if (!empresaExportar) {
      toastWarning("Advertencia", "Seleccione empresa para exportar.");
      return;
    }

    try {
      const res = await api.get(url, { responseType: "blob" });
      const contentType = res?.headers?.["content-type"] || "application/octet-stream";
      const arrayBuffer = res.data instanceof Blob ? await res.data.arrayBuffer() : res.data;
      const bytes = new Uint8Array(arrayBuffer);
      let binary = "";
      for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
      const base64 = btoa(binary);
      const dataUrl = `data:${contentType};base64,${base64}`;
      const link = document.createElement("a");
      link.href = dataUrl;
      link.setAttribute("download", nombre);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      mostrarError(error, "No se pudo descargar el archivo.");
    }
  };

  const exportarPDF = () =>
    descargar(
      `/exportaciones-sst/matriz-peligros/pdf/${empresaExportar}`,
      "matriz_peligros_sst.pdf"
    );

  const exportarExcel = () =>
    descargar(
      `/exportaciones-sst/matriz-peligros/excel/${empresaExportar}`,
      "matriz_peligros_sst.xlsx"
    );

  const subirEvidencia = async (item, file) => {
    if (!file) return;

    const data = new FormData();
    data.append("descripcion", `Evidencia matriz de peligros ${item.codigo}`);
    data.append("file", file);

    try {
      await api.post(`/planear/matriz-peligros/${item.id}/evidencia`, data, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await cargarDatos();
      toastSuccess("Éxito", "Evidencia cargada correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo subir la evidencia.");
    }
  };

  const eliminarEvidencia = async (item) => {
    if (!item?.archivo_url && !item?.archivo_id) {
      toastWarning("Advertencia", "Este peligro no tiene evidencia asociada.");
      return;
    }

    if (!confirmAction("¿Desea quitar la evidencia asociada a este peligro?")) return;

    try {
      await api.delete(`/planear/matriz-peligros/${item.id}/evidencia`);
      await cargarDatos();
      toastSuccess("Éxito", "Evidencia retirada correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo retirar la evidencia.");
    }
  };


  const abrirArchivo = (url) => {
    if (url) window.open(resolveFileUrl(url), "_blank");
  };

  const cambiarPorPagina = (e) => {
    setPorPagina(Number(e.target.value));
    setPagina(1);
  };

  return (
    <AdminLayout>
      <div className="matriz-peligros-page">
        <section className="mp-hero">
          <div>
            <h2>Matriz de Peligros SST</h2>
            <p>Identifica peligros, valora riesgos y controla las medidas preventivas.</p>
          </div>

          <div className="mp-actions">
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

        <section className="mp-kpis">
          <article>
            <ShieldAlert />
            <span>Total peligros</span>
            <strong>{kpis.total}</strong>
          </article>

          <article>
            <ShieldAlert />
            <span>Bajos</span>
            <strong>{kpis.bajos}</strong>
          </article>

          <article>
            <ShieldAlert />
            <span>Medios</span>
            <strong>{kpis.medios}</strong>
          </article>

          <article>
            <ShieldAlert />
            <span>Altos</span>
            <strong>{kpis.altos}</strong>
          </article>

          <article>
            <AlertTriangle />
            <span>Críticos</span>
            <strong>{kpis.criticos}</strong>
          </article>
        </section>

        <section className="mp-grid">
          <form className="mp-form" onSubmit={guardar}>
            <h3>{editandoId ? "Editar peligro" : "Nuevo peligro"}</h3>

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

              <select
                name="clasificacion_peligro"
                value={form.clasificacion_peligro}
                onChange={handleForm}
              >
                {CLASIFICACIONES.map((clasificacion) => (
                  <option key={clasificacion} value={clasificacion}>
                    {clasificacion}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-row">
              <input
                name="proceso"
                value={form.proceso}
                onChange={handleForm}
                placeholder="Proceso"
              />

              <input
                name="actividad"
                value={form.actividad}
                onChange={handleForm}
                placeholder="Actividad"
              />
            </div>

            <input
              name="tarea"
              value={form.tarea}
              onChange={handleForm}
              placeholder="Tarea"
            />

            <textarea
              name="peligro"
              value={form.peligro}
              onChange={handleForm}
              placeholder="Descripción del peligro"
            />

            <textarea
              name="efectos_posibles"
              value={form.efectos_posibles}
              onChange={handleForm}
              placeholder="Efectos posibles"
            />

            <div className="form-row three">
              <textarea
                name="controles_fuente"
                value={form.controles_fuente}
                onChange={handleForm}
                placeholder="Controles en la fuente"
              />

              <textarea
                name="controles_medio"
                value={form.controles_medio}
                onChange={handleForm}
                placeholder="Controles en el medio"
              />

              <textarea
                name="controles_individuo"
                value={form.controles_individuo}
                onChange={handleForm}
                placeholder="Controles en el individuo"
              />
            </div>

            <div className="form-row">
              <div>
                <label>Probabilidad</label>
                <select
                  name="probabilidad"
                  value={form.probabilidad}
                  onChange={handleForm}
                >
                  {[1, 2, 3, 4, 5].map((valor) => (
                    <option key={valor} value={valor}>
                      {valor}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label>Consecuencia</label>
                <select
                  name="consecuencia"
                  value={form.consecuencia}
                  onChange={handleForm}
                >
                  {[1, 2, 3, 4, 5].map((valor) => (
                    <option key={valor} value={valor}>
                      {valor}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className={`mp-risk-preview ${calcularPreview.clase}`}>
              <span>Nivel de riesgo</span>
              <strong>{calcularPreview.nivel}</strong>
              <b>{calcularPreview.interpretacion}</b>
              <small>{calcularPreview.aceptabilidad}</small>
            </div>

            <textarea
              name="medidas_intervencion"
              value={form.medidas_intervencion}
              onChange={handleForm}
              placeholder="Medidas de intervención"
            />

            <input
              name="responsable"
              value={form.responsable}
              onChange={handleForm}
              placeholder="Responsable"
            />

            <div className="form-row">
              <input
                type="date"
                name="fecha_revision"
                value={form.fecha_revision}
                onChange={handleForm}
              />

              <input
                type="date"
                name="fecha_vencimiento"
                value={form.fecha_vencimiento}
                onChange={handleForm}
              />
            </div>

            <select name="estado" value={form.estado} onChange={handleForm}>
              {ESTADOS.map((estado) => (
                <option key={estado} value={estado}>
                  {estado}
                </option>
              ))}
            </select>

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

          <aside className="mp-panel">
            <h3>Mapa de riesgo</h3>
            <strong>{kpis.porcentajeCritico}%</strong>
            <p>Porcentaje de riesgos críticos registrados.</p>

            <div className="mp-progress">
              <span style={{ width: `${kpis.porcentajeCritico}%` }} />
            </div>

            <div className="mp-risk-legend">
              <span className="bajo">Bajo: {kpis.bajos}</span>
              <span className="medio">Medio: {kpis.medios}</span>
              <span className="alto">Alto: {kpis.altos}</span>
              <span className="critico">Crítico: {kpis.criticos}</span>
            </div>

            <div className="mp-panel-alerts">
              <div>
                <small>Pendientes</small>
                <b>{kpis.pendientes}</b>
              </div>
              <div>
                <small>Total</small>
                <b>{kpis.total}</b>
              </div>
            </div>
          </aside>
        </section>

        <section className="mp-list">
          <div className="mp-filters">
            <input
              name="buscar"
              value={filtros.buscar}
              onChange={handleFiltro}
              placeholder="Buscar proceso, actividad, peligro o código..."
            />

            <select
              name="clasificacion_peligro"
              value={filtros.clasificacion_peligro}
              onChange={handleFiltro}
            >
              <option value="">Todas las clasificaciones</option>
              {CLASIFICACIONES.map((clasificacion) => (
                <option key={clasificacion} value={clasificacion}>
                  {clasificacion}
                </option>
              ))}
            </select>

            <select
              name="interpretacion_riesgo"
              value={filtros.interpretacion_riesgo}
              onChange={handleFiltro}
            >
              <option value="">Todos los riesgos</option>
              <option value="BAJO">Bajo</option>
              <option value="MEDIO">Medio</option>
              <option value="ALTO">Alto</option>
              <option value="CRITICO">Crítico</option>
            </select>

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

          <div className="mp-toolbar">
            <span>
              Mostrando {itemsPaginados.length} de {items.length} registros
            </span>

            <div className="mp-page-size">
              <label>Registros por página</label>
              <select value={porPagina} onChange={cambiarPorPagina}>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
          </div>

          <div className="table-wrap mp-table-wrap">
            <table className="mp-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Proceso</th>
                  <th>Actividad</th>
                  <th>Peligro</th>
                  <th>Clasificación</th>
                  <th>NP</th>
                  <th>NC</th>
                  <th>Nivel</th>
                  <th>Riesgo</th>
                  <th>Aceptabilidad</th>
                  <th>Evidencia</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {itemsPaginados.map((item) => (
                  <tr key={item.id}>
                    <td>{item.codigo}</td>
                    <td>{item.proceso}</td>
                    <td>{item.actividad}</td>
                    <td>{item.peligro}</td>
                    <td>{item.clasificacion_peligro}</td>
                    <td>{item.probabilidad}</td>
                    <td>{item.consecuencia}</td>
                    <td>
                      <strong>{item.nivel_riesgo}</strong>
                    </td>
                    <td>
                      <span
                        className={`mp-pill ${String(
                          item.interpretacion_riesgo
                        ).toLowerCase()}`}
                      >
                        {item.interpretacion_riesgo}
                      </span>
                    </td>
                    <td>{item.aceptabilidad}</td>
                    <td>
                      {item.archivo_url ? (
                        <div className="mp-evidence-group">
                          <span className="mp-evidencia-ok">✓ Evidencia</span>

                          <button
                            type="button"
                            className="btn-mini"
                            onClick={() => abrirArchivo(item.archivo_url)}
                            title="Ver evidencia"
                          >
                            <Eye size={14} />
                            Ver
                          </button>

                          <a
                            className="btn-mini btn-download-mini"
                            href={resolveFileUrl(item.archivo_url)}
                            target="_blank"
                            rel="noreferrer"
                            title="Descargar evidencia"
                          >
                            <FileDown size={14} />
                            Descargar
                          </a>

                          <label className="btn-upload-mini" title="Reemplazar evidencia">
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

                          <button
                            type="button"
                            className="btn-evidence-delete"
                            onClick={() => eliminarEvidencia(item)}
                            title="Quitar evidencia"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      ) : (
                        <label className="btn-upload-mini">
                          <Upload size={14} />
                          Cargar evidencia
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
                      <div className="mp-row-actions">
                        <button type="button" onClick={() => editar(item)} title="Editar">
                          <Edit3 size={15} />
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
                    <td colSpan="12" className="empty">
                      No hay peligros registrados.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="mp-pagination">
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
