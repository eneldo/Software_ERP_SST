/* ============================================================
   FASE 1.8.5.2 - MATRIZ LEGAL SST BI EXECUTIVE
   Archivo: frontend/src/pages/planear/MatrizLegalPage.jsx

   Mantiene:
   - CRUD completo
   - Evidencias
   - PDF / Excel
   - Filtros
   - Paginación

   Agrega:
   - Dashboard Enterprise
   - BI Executive Recharts
   - Riesgo legal
   - Top responsables
   - Próximas revisiones
   ============================================================ */

import React, { useEffect, useMemo, useState } from "react";
import {
  Scale,
  Plus,
  Save,
  RefreshCcw,
  FileDown,
  FileSpreadsheet,
  Eye,
  Trash2,
  Edit3,
  Database,
  Upload,
} from "lucide-react";

import AdminLayout from "../../layouts/AdminLayout";
import api from "../../api/axios";
import { matrizLegalApi } from "../../api/matrizLegalApi";
import { resolveFileUrl } from "../../utils/fileUrl";

import MatrizLegalDashboard from "../../components/matrizlegal/MatrizLegalDashboard";
import MatrizLegalAlertas from "../../components/matrizlegal/MatrizLegalAlertas";
import MatrizLegalIndicadores from "../../components/matrizlegal/MatrizLegalIndicadores";
import MatrizLegalBI from "../../components/matrizlegal/MatrizLegalBI";
import MatrizLegalRiesgo from "../../components/matrizlegal/MatrizLegalRiesgo";
import MatrizLegalResponsables from "../../components/matrizlegal/MatrizLegalResponsables";
import MatrizLegalRevisiones from "../../components/matrizlegal/MatrizLegalRevisiones";

import "../../styles/matriz-legal.css";

const API_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function MatrizLegalPage() {
  const [empresas, setEmpresas] = useState([]);
  const [items, setItems] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [empresaExportar, setEmpresaExportar] = useState("");
  const [dashboardLegal, setDashboardLegal] = useState(null);

  const [pagina, setPagina] = useState(1);
  const [porPagina, setPorPagina] = useState(10);

  const [filtros, setFiltros] = useState({
    empresa_id: "",
    buscar: "",
    estado_cumplimiento: "",
    estado_norma: "",
  });

  const [form, setForm] = useState({
    empresa_id: "",
    codigo: "ML-SST-001",
    norma: "",
    tipo_norma: "",
    numero_norma: "",
    anio: "",
    articulo: "",
    requisito_legal: "",
    tema: "",
    entidad_emisora: "",
    aplicabilidad: "APLICA",
    estado_cumplimiento: "PENDIENTE",
    estado_norma: "VIGENTE",
    responsable: "",
    fecha_revision: "",
    fecha_vencimiento: "",
    evidencia: "",
    observaciones: "",
  });

  const mostrarError = (error, mensaje) => {
    console.error(error);
    const detail = error?.response?.data?.detail;
    alert(`${mensaje}${detail ? `\n\nDetalle: ${detail}` : ""}`);
  };

  const cargarDashboardLegal = async (empresaId) => {
    if (!empresaId) {
      setDashboardLegal(null);
      return;
    }

    try {
      const res = await matrizLegalApi.bi(empresaId);
      setDashboardLegal(res.data);
    } catch (error) {
      console.error("No se pudo cargar BI legal:", error);
      setDashboardLegal(null);
    }
  };

  const cargarDatos = async () => {
    try {
      setLoading(true);

      const params = {};
      Object.entries(filtros).forEach(([key, value]) => {
        if (value) params[key] = value;
      });

      const [empresasRes, matrizRes] = await Promise.all([
        api.get("/empresas/"),
        matrizLegalApi.listar(params),
      ]);

      setEmpresas(empresasRes.data);
      setItems(matrizRes.data);
      setPagina(1);

      const empresaPreferida =
        filtros.empresa_id ||
        empresaExportar ||
        (empresasRes.data.length > 0 ? empresasRes.data[0].id : "");

      if (!empresaExportar && empresaPreferida) {
        setEmpresaExportar(empresaPreferida);
      }

      await cargarDashboardLegal(empresaPreferida);
    } catch (error) {
      mostrarError(error, "No se pudo cargar Matriz Legal.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const kpis = useMemo(() => {
    const total = items.length;
    const cumplen = items.filter((i) => i.estado_cumplimiento === "CUMPLE").length;
    const pendientes = items.filter((i) => i.estado_cumplimiento === "PENDIENTE").length;
    const noCumplen = items.filter((i) => i.estado_cumplimiento === "NO_CUMPLE").length;
    const porcentaje = total > 0 ? Math.round((cumplen / total) * 100) : 0;

    return { total, cumplen, pendientes, noCumplen, porcentaje };
  }, [items]);

  const totalPaginas = Math.max(1, Math.ceil(items.length / porPagina));
  const inicio = (pagina - 1) * porPagina;
  const fin = inicio + porPagina;
  const itemsPaginados = items.slice(inicio, fin);

  const limpiar = () => {
    setEditandoId(null);
    setForm({
      empresa_id: "",
      codigo: "ML-SST-001",
      norma: "",
      tipo_norma: "",
      numero_norma: "",
      anio: "",
      articulo: "",
      requisito_legal: "",
      tema: "",
      entidad_emisora: "",
      aplicabilidad: "APLICA",
      estado_cumplimiento: "PENDIENTE",
      estado_norma: "VIGENTE",
      responsable: "",
      fecha_revision: "",
      fecha_vencimiento: "",
      evidencia: "",
      observaciones: "",
    });
  };

  const handleForm = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleFiltro = (e) => {
    setFiltros({ ...filtros, [e.target.name]: e.target.value });
  };

  const guardar = async (e) => {
    e.preventDefault();

    if (!form.empresa_id || !form.norma || !form.requisito_legal) {
      alert("Empresa, norma y requisito legal son obligatorios.");
      return;
    }

    const payload = {
      ...form,
      empresa_id: Number(form.empresa_id),
      fecha_revision: form.fecha_revision || null,
      fecha_vencimiento: form.fecha_vencimiento || null,
    };

    try {
      if (editandoId) {
        await matrizLegalApi.actualizar(editandoId, payload);
      } else {
        await matrizLegalApi.crear(payload);
      }

      limpiar();
      await cargarDatos();
      alert("Requisito legal guardado correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo guardar el requisito legal.");
    }
  };

  const editar = (item) => {
    setEditandoId(item.id);

    setForm({
      empresa_id: item.empresa_id || "",
      codigo: item.codigo || "",
      norma: item.norma || "",
      tipo_norma: item.tipo_norma || "",
      numero_norma: item.numero_norma || "",
      anio: item.anio || "",
      articulo: item.articulo || "",
      requisito_legal: item.requisito_legal || "",
      tema: item.tema || "",
      entidad_emisora: item.entidad_emisora || "",
      aplicabilidad: item.aplicabilidad || "APLICA",
      estado_cumplimiento: item.estado_cumplimiento || "PENDIENTE",
      estado_norma: item.estado_norma || "VIGENTE",
      responsable: item.responsable || "",
      fecha_revision: item.fecha_revision || "",
      fecha_vencimiento: item.fecha_vencimiento || "",
      evidencia: item.evidencia || "",
      observaciones: item.observaciones || "",
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const eliminar = async (id) => {
    if (!confirm("¿Desea eliminar este requisito legal?")) return;

    try {
      await matrizLegalApi.eliminar(id);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo eliminar.");
    }
  };

  const cargarBase = async () => {
    if (!empresaExportar) {
      alert("Seleccione empresa.");
      return;
    }

    try {
      await matrizLegalApi.cargarBase(empresaExportar);
      await cargarDatos();
      alert("Base normativa cargada.");
    } catch (error) {
      mostrarError(error, "No se pudo cargar la base normativa.");
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
      `/exportaciones-sst/matriz-legal/pdf/${empresaExportar}`,
      "matriz_legal_sst.pdf"
    );

  const exportarExcel = () =>
    descargar(
      `/exportaciones-sst/matriz-legal/excel/${empresaExportar}`,
      "matriz_legal_sst.xlsx"
    );

  const subirEvidencia = async (item, file) => {
    if (!file) return;

    const data = new FormData();
    data.append("descripcion", `Evidencia ${item.codigo}`);
    data.append("file", file);

    try {
      await matrizLegalApi.subirEvidencia(item.id, data);
      await cargarDatos();
      alert("Evidencia cargada.");
    } catch (error) {
      mostrarError(error, "No se pudo subir la evidencia.");
    }
  };

  const abrirArchivo = (url) => {
    if (url) window.open(resolveFileUrl(url), "_blank");
  };

  const cambiarPorPagina = (e) => {
    setPorPagina(Number(e.target.value));
    setPagina(1);
  };

  const aplicarFiltros = async () => {
    await cargarDatos();
  };

  const cambiarEmpresaBI = async (e) => {
    const value = e.target.value;
    setEmpresaExportar(value);
    await cargarDashboardLegal(value);
  };

  return (
    <AdminLayout>
      <div className="matriz-legal-page">
        <section className="ml-hero ml-hero-enterprise">
          <div>
            <h2>Matriz Legal SST</h2>
            <p>Controla requisitos normativos, responsables, evidencias y cumplimiento.</p>
          </div>

          <div className="ml-actions">
            <select value={empresaExportar} onChange={cambiarEmpresaBI}>
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

        <section className="ml-kpis">
          <article>
            <Scale />
            <span>Total</span>
            <strong>{kpis.total}</strong>
          </article>

          <article>
            <Scale />
            <span>Cumplen</span>
            <strong>{kpis.cumplen}</strong>
          </article>

          <article>
            <Scale />
            <span>Pendientes</span>
            <strong>{kpis.pendientes}</strong>
          </article>

          <article>
            <Scale />
            <span>No cumplen</span>
            <strong>{kpis.noCumplen}</strong>
          </article>

          <article>
            <Scale />
            <span>Cumplimiento</span>
            <strong>{kpis.porcentaje}%</strong>
          </article>
        </section>

        <MatrizLegalDashboard dashboard={dashboardLegal || {}} kpis={kpis} />
        <MatrizLegalIndicadores dashboard={dashboardLegal || {}} />

        <section className="ml-bi-layout">
          <div className="ml-bi-main">
            <MatrizLegalBI dashboard={dashboardLegal || {}} />
          </div>

          <aside className="ml-bi-side">
            <MatrizLegalRiesgo dashboard={dashboardLegal || {}} />
            <MatrizLegalResponsables dashboard={dashboardLegal || {}} />
            <MatrizLegalRevisiones dashboard={dashboardLegal || {}} />
          </aside>
        </section>

        <MatrizLegalAlertas dashboard={dashboardLegal || {}} />

        <section className="ml-grid">
          <form className="ml-form" onSubmit={guardar}>
            <h3>{editandoId ? "Editar requisito legal" : "Nuevo requisito legal"}</h3>

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
                name="norma"
                value={form.norma}
                onChange={handleForm}
                placeholder="Norma"
              />
            </div>

            <div className="form-row three">
              <input
                name="tipo_norma"
                value={form.tipo_norma}
                onChange={handleForm}
                placeholder="Tipo norma"
              />
              <input
                name="numero_norma"
                value={form.numero_norma}
                onChange={handleForm}
                placeholder="Número"
              />
              <input
                name="anio"
                value={form.anio}
                onChange={handleForm}
                placeholder="Año"
              />
            </div>

            <input
              name="articulo"
              value={form.articulo}
              onChange={handleForm}
              placeholder="Artículo"
            />

            <input
              name="tema"
              value={form.tema}
              onChange={handleForm}
              placeholder="Tema"
            />

            <input
              name="entidad_emisora"
              value={form.entidad_emisora}
              onChange={handleForm}
              placeholder="Entidad emisora"
            />

            <textarea
              name="requisito_legal"
              value={form.requisito_legal}
              onChange={handleForm}
              placeholder="Requisito legal"
            />

            <div className="form-row">
              <select
                name="estado_cumplimiento"
                value={form.estado_cumplimiento}
                onChange={handleForm}
              >
                <option value="CUMPLE">CUMPLE</option>
                <option value="PENDIENTE">PENDIENTE</option>
                <option value="NO_CUMPLE">NO CUMPLE</option>
              </select>

              <select
                name="estado_norma"
                value={form.estado_norma}
                onChange={handleForm}
              >
                <option value="VIGENTE">VIGENTE</option>
                <option value="DEROGADA">DEROGADA</option>
                <option value="MODIFICADA">MODIFICADA</option>
              </select>
            </div>

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

          <aside className="ml-panel ml-compliance-panel">
            <h3>Compliance Score Legal</h3>
            <strong>{kpis.porcentaje}%</strong>
            <p>Cumplimiento de requisitos legales registrados.</p>
            <div className="ml-progress">
              <span style={{ width: `${kpis.porcentaje}%` }} />
            </div>

            <div className="ml-compliance-extra">
              <div>
                <span>Evidencias</span>
                <b>{dashboardLegal?.porcentaje_evidencias || 0}%</b>
              </div>
              <div>
                <span>Riesgo</span>
                <b>{dashboardLegal?.riesgo_legal || "BAJO"}</b>
              </div>
            </div>
          </aside>
        </section>

        <section className="ml-list">
          <div className="ml-filters">
            <input
              name="buscar"
              value={filtros.buscar}
              onChange={handleFiltro}
              placeholder="Buscar norma, requisito, tema o código..."
            />

            <select
              name="estado_cumplimiento"
              value={filtros.estado_cumplimiento}
              onChange={handleFiltro}
            >
              <option value="">Todos los cumplimientos</option>
              <option value="CUMPLE">Cumple</option>
              <option value="PENDIENTE">Pendiente</option>
              <option value="NO_CUMPLE">No cumple</option>
            </select>

            <select
              name="estado_norma"
              value={filtros.estado_norma}
              onChange={handleFiltro}
            >
              <option value="">Todos los estados</option>
              <option value="VIGENTE">Vigente</option>
              <option value="DEROGADA">Derogada</option>
              <option value="MODIFICADA">Modificada</option>
            </select>

            <button type="button" onClick={aplicarFiltros}>
              Filtrar
            </button>
          </div>

          <div className="ml-toolbar">
            <span>
              Mostrando {itemsPaginados.length} de {items.length} registros
            </span>

            <div className="ml-page-size">
              <label>Registros por página</label>
              <select value={porPagina} onChange={cambiarPorPagina}>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </div>
          </div>

          <div className="table-wrap ml-table-wrap">
            <table className="ml-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Norma</th>
                  <th>Requisito</th>
                  <th>Tema</th>
                  <th>Cumplimiento</th>
                  <th>Estado norma</th>
                  <th>Evidencia</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {itemsPaginados.map((item) => (
                  <tr key={item.id}>
                    <td>{item.codigo}</td>
                    <td>{item.norma}</td>
                    <td>{item.requisito_legal}</td>
                    <td>{item.tema || "Sin tema"}</td>
                    <td>
                      <span
                        className={`ml-pill ${item.estado_cumplimiento.toLowerCase()}`}
                      >
                        {item.estado_cumplimiento}
                      </span>
                    </td>
                    <td>
                      <span className={`ml-pill-norma ${item.estado_norma.toLowerCase()}`}>
                        {item.estado_norma}
                      </span>
                    </td>
                    <td>
                      {item.archivo_url ? (
                        <div className="ml-evidencia-actions">
                          <span className="ml-evidencia-ok">✓ Evidencia</span>

                          <button
                            type="button"
                            className="btn-mini"
                            onClick={() => abrirArchivo(item.archivo_url)}
                          >
                            <Eye size={14} />
                            Ver
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
                      <div className="ml-row-actions">
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
                    <td colSpan="8" className="empty">
                      No hay requisitos legales registrados.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="ml-pagination">
            <button
              type="button"
              disabled={pagina === 1}
              onClick={() => setPagina((prev) => Math.max(1, prev - 1))}
            >
              Anterior
            </button>

            <span>
              Página {pagina} de {totalPaginas}
            </span>

            <button
              type="button"
              disabled={pagina >= totalPaginas}
              onClick={() => setPagina((prev) => Math.min(totalPaginas, prev + 1))}
            >
              Siguiente
            </button>
          </div>
        </section>
      </div>
    </AdminLayout>
  );
}
