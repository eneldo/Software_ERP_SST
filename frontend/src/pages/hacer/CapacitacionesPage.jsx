import React, { useEffect, useMemo, useState } from "react";
import {
  BookOpenCheck,
  CalendarCheck,
  CheckCircle2,
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
  Users,
} from "lucide-react";

import AdminLayout from "../../layouts/AdminLayout";
import api from "../../api/axios";
import { validarArchivoAntesDeSubir } from "../../utils/fileValidation";
import "../../styles/capacitaciones.css";

const API_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const ESTADOS = ["PROGRAMADA", "EJECUTADA", "CANCELADA", "VENCIDA"];
const TIPOS = ["INTERNA", "EXTERNA"];
const MODALIDADES = ["PRESENCIAL", "VIRTUAL", "MIXTA"];

export default function CapacitacionesPage() {
  const [empresas, setEmpresas] = useState([]);
  const [items, setItems] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [empresaSeleccionada, setEmpresaSeleccionada] = useState("");
  const [loading, setLoading] = useState(false);

  const [pagina, setPagina] = useState(1);
  const [porPagina, setPorPagina] = useState(10);

  const [filtros, setFiltros] = useState({
    empresa_id: "",
    buscar: "",
    estado: "",
  });

  const [form, setForm] = useState({
    empresa_id: "",
    codigo: "CAP-SST-001",
    nombre: "",
    tema: "",
    objetivo: "",
    tipo: "INTERNA",
    modalidad: "PRESENCIAL",
    capacitador: "",
    responsable: "",
    fecha_programada: "",
    fecha_ejecucion: "",
    duracion_horas: 0,
    lugar: "",
    poblacion_objetivo: "",
    total_asistentes: 0,
    estado: "PROGRAMADA",
    cumplimiento: 0,
    evidencia: "",
    observaciones: "",
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

  const cargarDatos = async () => {
    try {
      setLoading(true);

      /*
        Corrección FASE 2.7.2:
        Primero cargamos empresas y después llamamos capacitaciones
        con empresa_id obligatorio. Así evitamos el error 422 cuando
        la pantalla abre por primera vez y todavía no hay empresa seleccionada.
      */
      const empresasRes = await api.get("/empresas/");
      const empresasData = empresasRes.data || [];

      setEmpresas(empresasData);

      const params = {};
      Object.entries(filtros).forEach(([key, value]) => {
        if (value) params[key] = value;
      });

      const empresaId =
        filtros.empresa_id ||
        empresaSeleccionada ||
        empresasData?.[0]?.id;

      if (!empresaId) {
        setItems([]);
        setPagina(1);
        return;
      }

      params.empresa_id = Number(empresaId);

      if (!empresaSeleccionada) {
        setEmpresaSeleccionada(empresaId);
      }

      const capacitacionesRes = await api.get("/hacer/capacitaciones/", {
        params,
      });

      setItems(capacitacionesRes.data || []);
      setPagina(1);
    } catch (error) {
      mostrarError(error, "No se pudo cargar Capacitaciones SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const kpis = useMemo(() => {
    const total = items.length;
    const programadas = items.filter((i) => i.estado === "PROGRAMADA").length;
    const ejecutadas = items.filter((i) => i.estado === "EJECUTADA").length;
    const canceladas = items.filter((i) => i.estado === "CANCELADA").length;
    const vencidas = items.filter((i) => i.estado === "VENCIDA").length;
    const asistentes = items.reduce(
      (acc, item) => acc + Number(item.total_asistentes || 0),
      0
    );
    const cumplimiento = total > 0 ? Math.round((ejecutadas / total) * 100) : 0;

    return {
      total,
      programadas,
      ejecutadas,
      canceladas,
      vencidas,
      asistentes,
      cumplimiento,
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
      codigo: "CAP-SST-001",
      nombre: "",
      tema: "",
      objetivo: "",
      tipo: "INTERNA",
      modalidad: "PRESENCIAL",
      capacitador: "",
      responsable: "",
      fecha_programada: "",
      fecha_ejecucion: "",
      duracion_horas: 0,
      lugar: "",
      poblacion_objetivo: "",
      total_asistentes: 0,
      estado: "PROGRAMADA",
      cumplimiento: 0,
      evidencia: "",
      observaciones: "",
    });
  };

  const handleForm = (e) => {
    const { name, value } = e.target;

    setForm({
      ...form,
      [name]:
        name === "duracion_horas" ||
        name === "total_asistentes" ||
        name === "cumplimiento"
          ? Number(value)
          : value,
    });
  };

  const handleFiltro = (e) => {
    setFiltros({ ...filtros, [e.target.name]: e.target.value });
  };

  const guardar = async (e) => {
    e.preventDefault();

    if (!form.empresa_id || !form.nombre || !form.tema) {
      alert("Empresa, nombre y tema son obligatorios.");
      return;
    }

    const payload = {
      ...form,
      empresa_id: Number(form.empresa_id),
      duracion_horas: Number(form.duracion_horas || 0),
      total_asistentes: Number(form.total_asistentes || 0),
      cumplimiento: Number(form.cumplimiento || 0),
      fecha_programada: form.fecha_programada || null,
      fecha_ejecucion: form.fecha_ejecucion || null,
    };

    try {
      setLoading(true);

      if (editandoId) {
        await api.put(`/hacer/capacitaciones/${editandoId}`, payload);
      } else {
        await api.post("/hacer/capacitaciones/", payload);
      }

      limpiar();
      await cargarDatos();
      alert("Capacitación guardada correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo guardar la capacitación.");
    } finally {
      setLoading(false);
    }
  };

  const editar = (item) => {
    setEditandoId(item.id);

    setForm({
      empresa_id: item.empresa_id || "",
      codigo: item.codigo || "CAP-SST-001",
      nombre: item.nombre || "",
      tema: item.tema || "",
      objetivo: item.objetivo || "",
      tipo: item.tipo || "INTERNA",
      modalidad: item.modalidad || "PRESENCIAL",
      capacitador: item.capacitador || "",
      responsable: item.responsable || "",
      fecha_programada: item.fecha_programada || "",
      fecha_ejecucion: item.fecha_ejecucion || "",
      duracion_horas: Number(item.duracion_horas || 0),
      lugar: item.lugar || "",
      poblacion_objetivo: item.poblacion_objetivo || "",
      total_asistentes: Number(item.total_asistentes || 0),
      estado: item.estado || "PROGRAMADA",
      cumplimiento: Number(item.cumplimiento || 0),
      evidencia: item.evidencia || "",
      observaciones: item.observaciones || "",
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminar = async (id) => {
    if (!confirm("¿Desea eliminar esta capacitación?")) return;

    try {
      await api.delete(`/hacer/capacitaciones/${id}`);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo eliminar la capacitación.");
    }
  };

  const finalizar = async (id) => {
    if (!confirm("¿Desea finalizar esta capacitación?")) return;

    try {
      await api.patch(`/hacer/capacitaciones/${id}/finalizar`);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo finalizar la capacitación.");
    }
  };

  const cargarBase = async () => {
    if (!empresaSeleccionada) {
      alert("Seleccione empresa.");
      return;
    }

    try {
      await api.post(`/hacer/capacitaciones/cargar-base/${empresaSeleccionada}`);
      await cargarDatos();
      alert("Base de capacitaciones cargada correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo cargar la base de capacitaciones.");
    }
  };

  

const subirEvidencia = async (item, file) => {
  const validacion = validarArchivoAntesDeSubir(file);

  if (!validacion.ok) {
    alert(validacion.mensaje);
    return;
  }

  

  const data = new FormData();
  data.append("archivo", file);

  try {
    await api.post(`/hacer/capacitaciones/${item.id}/evidencia`, data, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    await cargarDatos();
    alert("Evidencia cargada y optimizada correctamente.");
  } catch (error) {
    mostrarError(error, "No se pudo subir la evidencia.");
  }
};


  const abrirArchivo = (url) => {
    if (url) window.open(`${API_URL}${url}`, "_blank");
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

  const descargar = async (url, nombre) => {
  if (!empresaSeleccionada) {
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
    `/exportaciones-sst/capacitaciones/pdf/${empresaSeleccionada}`,
    "capacitaciones_sst.pdf"
  );

const exportarExcel = () =>
  descargar(
    `/exportaciones-sst/capacitaciones/excel/${empresaSeleccionada}`,
    "capacitaciones_sst.xlsx"
  );

  const cambiarPorPagina = (e) => {
    setPorPagina(Number(e.target.value));
    setPagina(1);
  };

  return (
    <AdminLayout>
      <div className="cap-page">
        <section className="cap-hero">
          <div>
            <span className="cap-badge">CAPACITACIONES SST</span>
            <h2>Capacitaciones SST PRO</h2>
            <p>
              Programa de formación, asistencia, evidencias y seguimiento de
              capacitaciones del SG-SST.
            </p>
          </div>

          <div className="cap-actions">
            <select
              value={empresaSeleccionada}
              onChange={(e) => setEmpresaSeleccionada(e.target.value)}
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

        <section className="cap-kpis">
          <article>
            <BookOpenCheck />
            <span>Total</span>
            <strong>{kpis.total}</strong>
          </article>

          <article>
            <CalendarCheck />
            <span>Programadas</span>
            <strong>{kpis.programadas}</strong>
          </article>

          <article>
            <CheckCircle2 />
            <span>Ejecutadas</span>
            <strong>{kpis.ejecutadas}</strong>
          </article>

          <article>
            <Users />
            <span>Asistentes</span>
            <strong>{kpis.asistentes}</strong>
          </article>

          <article>
            <BookOpenCheck />
            <span>Cumplimiento</span>
            <strong>{kpis.cumplimiento}%</strong>
          </article>
        </section>

        <section className="cap-grid">
          <form className="cap-form" onSubmit={guardar}>
            <h3>{editandoId ? "Editar capacitación" : "Nueva capacitación"}</h3>

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
                name="nombre"
                value={form.nombre}
                onChange={handleForm}
                placeholder="Nombre de la capacitación"
              />
            </div>

            <input
              name="tema"
              value={form.tema}
              onChange={handleForm}
              placeholder="Tema"
            />

            <textarea
              name="objetivo"
              value={form.objetivo}
              onChange={handleForm}
              placeholder="Objetivo"
            />

            <div className="form-row three">
              <select name="tipo" value={form.tipo} onChange={handleForm}>
                {TIPOS.map((tipo) => (
                  <option key={tipo} value={tipo}>
                    {tipo}
                  </option>
                ))}
              </select>

              <select
                name="modalidad"
                value={form.modalidad}
                onChange={handleForm}
              >
                {MODALIDADES.map((modalidad) => (
                  <option key={modalidad} value={modalidad}>
                    {modalidad}
                  </option>
                ))}
              </select>

              <input
                type="number"
                name="duracion_horas"
                value={form.duracion_horas}
                onChange={handleForm}
                placeholder="Duración horas"
                min="0"
                step="0.5"
              />
            </div>

            <div className="form-row">
              <input
                name="capacitador"
                value={form.capacitador}
                onChange={handleForm}
                placeholder="Capacitador"
              />

              <input
                name="responsable"
                value={form.responsable}
                onChange={handleForm}
                placeholder="Responsable"
              />
            </div>

            <div className="form-row">
              <input
                type="date"
                name="fecha_programada"
                value={form.fecha_programada}
                onChange={handleForm}
              />

              <input
                type="date"
                name="fecha_ejecucion"
                value={form.fecha_ejecucion}
                onChange={handleForm}
              />
            </div>

            <input
              name="lugar"
              value={form.lugar}
              onChange={handleForm}
              placeholder="Lugar"
            />

            <textarea
              name="poblacion_objetivo"
              value={form.poblacion_objetivo}
              onChange={handleForm}
              placeholder="Población objetivo"
            />

            <div className="form-row">
              <select name="estado" value={form.estado} onChange={handleForm}>
                {ESTADOS.map((estado) => (
                  <option key={estado} value={estado}>
                    {estado}
                  </option>
                ))}
              </select>

              <input
                type="number"
                name="total_asistentes"
                value={form.total_asistentes}
                onChange={handleForm}
                placeholder="Total asistentes"
                min="0"
              />
            </div>

            <div>
              <label>Cumplimiento: {form.cumplimiento}%</label>
              <input
                type="range"
                min="0"
                max="100"
                name="cumplimiento"
                value={form.cumplimiento}
                onChange={handleForm}
              />
            </div>

            <div className={`cap-progress-preview ${form.estado.toLowerCase()}`}>
              <span>Avance de capacitación</span>
              <strong>{form.cumplimiento}%</strong>
              <div>
                <b style={{ width: `${form.cumplimiento}%` }} />
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

          <aside className="cap-panel">
            <h3>Resumen capacitaciones</h3>
            <strong>{kpis.cumplimiento}%</strong>
            <p>Cumplimiento general del programa de capacitación SST.</p>

            <div className="cap-progress">
              <span style={{ width: `${kpis.cumplimiento}%` }} />
            </div>

            <div className="cap-mini-grid">
              <div>
                <span>Canceladas</span>
                <strong>{kpis.canceladas}</strong>
              </div>
              <div>
                <span>Vencidas</span>
                <strong>{kpis.vencidas}</strong>
              </div>
            </div>
          </aside>
        </section>

        <section className="cap-list">
          <div className="cap-filters">
            <input
              name="buscar"
              value={filtros.buscar}
              onChange={handleFiltro}
              placeholder="Buscar capacitación, tema..."
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

          <div className="cap-toolbar">
            <span>
              Mostrando {itemsPaginados.length} de {items.length} registros
            </span>

            <div className="cap-page-size">
              <label>Registros por página</label>
              <select value={porPagina} onChange={cambiarPorPagina}>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
          </div>

          <div className="table-wrap cap-table-wrap">
            <table className="cap-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Nombre</th>
                  <th>Tema</th>
                  <th>Modalidad</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                  <th>Asistentes</th>
                  <th>Cumplimiento</th>
                  <th>Evidencia</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {itemsPaginados.map((item) => (
                  <tr key={item.id}>
                    <td>{item.codigo}</td>
                    <td>{item.nombre}</td>
                    <td>{item.tema}</td>
                    <td>{item.modalidad}</td>
                    <td>
                      <span className={`cap-pill ${String(item.estado).toLowerCase()}`}>
                        {item.estado}
                      </span>
                    </td>
                    <td>{item.fecha_programada || "Sin fecha"}</td>
                    <td>{item.total_asistentes || 0}</td>
                    <td>
                      <div className="cap-table-progress">
                        <span>{item.cumplimiento}%</span>
                        <b style={{ width: `${item.cumplimiento}%` }} />
                      </div>
                    </td>
                    <td>
                      {item.evidencia ? (
                        <div className="cap-evidence-group">
                          <span className="cap-evidencia-ok">✓ Evidencia</span>

                          <button
                            type="button"
                            className="btn-mini"
                            onClick={() => abrirArchivo(item.evidencia)}
                          >
                            <Eye size={14} />
                            Ver
                          </button>

                          <button
                            type="button"
                            className="btn-mini"
                            onClick={() =>
                              descargarArchivo(item.evidencia, "evidencia")
                            }
                          >
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
                      <div className="cap-row-actions">
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
                      No hay capacitaciones registradas.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="cap-pagination">
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
