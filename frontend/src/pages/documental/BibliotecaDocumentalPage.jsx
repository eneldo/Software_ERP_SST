import React, { useEffect, useMemo, useState } from "react";
import {
  Archive,
  Upload,
  RefreshCcw,
  Search,
  FileText,
  Download,
  Eye,
  Edit3,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  XCircle,
} from "lucide-react";

import AdminLayout from "../../layouts/AdminLayout";
import api from "../../api/axios";
import { bibliotecaDocumentalApi } from "../../api/bibliotecaDocumentalApi";
import { toastSuccess, toastError, toastWarning, confirmAction } from "../../utils/toast";
import "../../styles/biblioteca-documental.css";

import { API_BASE_URL } from "../../config/env";

const CATEGORIAS = [
  "POLITICAS",
  "OBJETIVOS",
  "MATRIZ_LEGAL",
  "MATRIZ_PELIGROS",
  "PLAN_ANUAL",
  "PROCEDIMIENTOS",
  "FORMATOS",
  "ACTAS",
  "AUDITORIAS",
  "CAPACITACIONES",
  "INDICADORES",
  "OTROS",
];

const ESTADOS = ["BORRADOR", "VIGENTE", "OBSOLETO"];

export default function BibliotecaDocumentalPage() {
  const [empresas, setEmpresas] = useState([]);
  const [documentos, setDocumentos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState("");
  const [errorMensaje, setErrorMensaje] = useState("");

  const [filtros, setFiltros] = useState({
    empresa_id: "",
    categoria: "",
    estado: "",
    buscar: "",
  });

  const [form, setForm] = useState({
    empresa_id: "",
    codigo_documental: "",
    titulo: "",
    categoria: "OTROS",
    tipo_documento: "PDF",
    modulo_origen: "BIBLIOTECA_DOCUMENTAL",
    version: "1.0",
    estado: "BORRADOR",
    responsable: "",
    descripcion: "",
    palabras_clave: "",
    fecha_aprobacion: "",
    fecha_vencimiento: "",
    file: null,
  });

  const mostrarError = (error, mensaje) => {
    console.error(error);
    const detail = error?.response?.data?.detail;
    setErrorMensaje(`${mensaje}${detail ? ` Detalle: ${detail}` : ""}`);
  };

  const cargarDatos = async () => {
    try {
      setLoading(true);
      setErrorMensaje("");

      const params = {};
      if (filtros.empresa_id) params.empresa_id = filtros.empresa_id;
      if (filtros.categoria) params.categoria = filtros.categoria;
      if (filtros.estado) params.estado = filtros.estado;
      if (filtros.buscar) params.buscar = filtros.buscar;

      const [empresasRes, documentosRes] = await Promise.all([
        api.get("/empresas/"),
        bibliotecaDocumentalApi.listar(params),
      ]);

      setEmpresas(empresasRes.data);
      setDocumentos(documentosRes.data);
    } catch (error) {
      mostrarError(error, "No se pudo cargar la biblioteca documental.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const kpis = useMemo(() => {
    return {
      total: documentos.length,
      vigentes: documentos.filter((d) => d.estado === "VIGENTE").length,
      borradores: documentos.filter((d) => d.estado === "BORRADOR").length,
      obsoletos: documentos.filter((d) => d.estado === "OBSOLETO").length,
    };
  }, [documentos]);

  const handleFiltro = (e) => {
    setFiltros({ ...filtros, [e.target.name]: e.target.value });
  };

  const handleForm = (e) => {
    const { name, value, files } = e.target;

    setForm({
      ...form,
      [name]: files ? files[0] : value,
    });
  };

  const limpiarFormulario = () => {
    setForm({
      empresa_id: "",
      codigo_documental: "",
      titulo: "",
      categoria: "OTROS",
      tipo_documento: "PDF",
      modulo_origen: "BIBLIOTECA_DOCUMENTAL",
      version: "1.0",
      estado: "BORRADOR",
      responsable: "",
      descripcion: "",
      palabras_clave: "",
      fecha_aprobacion: "",
      fecha_vencimiento: "",
      file: null,
    });
  };

  const subirDocumento = async (e) => {
    e.preventDefault();

    if (!form.empresa_id || !form.codigo_documental || !form.titulo || !form.file) {
      toastWarning("Advertencia", "Empresa, código documental, título y archivo son obligatorios.");
      return;
    }

    const data = new FormData();
    data.append("empresa_id", form.empresa_id);
    data.append("codigo_documental", form.codigo_documental);
    data.append("titulo", form.titulo);
    data.append("categoria", form.categoria);
    data.append("tipo_documento", form.tipo_documento);
    data.append("modulo_origen", form.modulo_origen);
    data.append("version", form.version);
    data.append("estado", form.estado);
    data.append("responsable", form.responsable || "");
    data.append("descripcion", form.descripcion || "");
    data.append("palabras_clave", form.palabras_clave || "");
    data.append("fecha_aprobacion", form.fecha_aprobacion || "");
    data.append("fecha_vencimiento", form.fecha_vencimiento || "");
    data.append("file", form.file);

    try {
      setLoading(true);
      await bibliotecaDocumentalApi.subir(data);
      limpiarFormulario();
      await cargarDatos();
      toastSuccess("Éxito", "Documento subido correctamente.");
    } catch (error) {
      mostrarError(error, "Error subiendo documento.");
    } finally {
      setLoading(false);
    }
  };

  const marcarVigente = async (id) => {
    try {
      await bibliotecaDocumentalApi.marcarVigente(id);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo marcar como vigente.");
    }
  };

  const marcarObsoleto = async (id) => {
    try {
      await bibliotecaDocumentalApi.marcarObsoleto(id);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo marcar como obsoleto.");
    }
  };

  const eliminarDocumento = async (id) => {
    if (!confirmAction("¿Desea desactivar este documento?")) return;

    try {
      await bibliotecaDocumentalApi.eliminar(id);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo eliminar el documento.");
    }
  };

  const abrirArchivo = (url) => {
    if (!url) return;
    window.open(`${API_BASE_URL}${url}`, "_blank");
  };

  const vistaPrevia = (doc) => {
    if (!doc.archivo_url) return;
    setPreviewUrl(`${API_BASE_URL}${doc.archivo_url}`);
  };

  return (
    <AdminLayout>
      <div className="biblioteca-page">
        <section className="biblioteca-hero">
          <div>
            <h2>Biblioteca Documental SST</h2>
            <p>
              Consulta y administra los documentos y registros del SG-SST.
            </p>
          </div>

          <button className="btn-refresh" onClick={cargarDatos}>
            <RefreshCcw size={18} />
            Actualizar
          </button>
        </section>

        {errorMensaje && (
          <section className="biblioteca-error" role="alert">
            <AlertTriangle size={17} />
            <span>{errorMensaje}</span>
            <button type="button" onClick={cargarDatos} disabled={loading}>
              <RefreshCcw size={15} /> {loading ? "Reintentando..." : "Reintentar"}
            </button>
          </section>
        )}

        <section className="biblioteca-kpis">
          <article>
            <Archive size={24} />
            <div>
              <span>Total documentos</span>
              <strong>{kpis.total}</strong>
            </div>
          </article>

          <article>
            <CheckCircle2 size={24} />
            <div>
              <span>Vigentes</span>
              <strong>{kpis.vigentes}</strong>
            </div>
          </article>

          <article>
            <AlertTriangle size={24} />
            <div>
              <span>Borradores</span>
              <strong>{kpis.borradores}</strong>
            </div>
          </article>

          <article>
            <XCircle size={24} />
            <div>
              <span>Obsoletos</span>
              <strong>{kpis.obsoletos}</strong>
            </div>
          </article>
        </section>

        <section className="biblioteca-grid">
          <form className="biblioteca-form" onSubmit={subirDocumento}>
            <div className="form-title">
              <Upload size={22} />
              <div>
                <h3>Subir documento</h3>
                <p>Cargue documentos PDF, Word, Excel o imágenes.</p>
              </div>
            </div>

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
              <div>
                <label>Código documental</label>
                <input
                  name="codigo_documental"
                  value={form.codigo_documental}
                  onChange={handleForm}
                  placeholder="SGSST-DOC-001"
                />
              </div>

              <div>
                <label>Versión</label>
                <input name="version" value={form.version} onChange={handleForm} />
              </div>
            </div>

            <label>Título</label>
            <input
              name="titulo"
              value={form.titulo}
              onChange={handleForm}
              placeholder="Nombre del documento"
            />

            <div className="form-row">
              <div>
                <label>Categoría</label>
                <select name="categoria" value={form.categoria} onChange={handleForm}>
                  {CATEGORIAS.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label>Estado</label>
                <select name="estado" value={form.estado} onChange={handleForm}>
                  {ESTADOS.map((estado) => (
                    <option key={estado} value={estado}>
                      {estado}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-row">
              <div>
                <label>Tipo documento</label>
                <input
                  name="tipo_documento"
                  value={form.tipo_documento}
                  onChange={handleForm}
                />
              </div>

              <div>
                <label>Responsable</label>
                <input
                  name="responsable"
                  value={form.responsable}
                  onChange={handleForm}
                />
              </div>
            </div>

            <div className="form-row">
              <div>
                <label>Fecha aprobación</label>
                <input
                  type="date"
                  name="fecha_aprobacion"
                  value={form.fecha_aprobacion}
                  onChange={handleForm}
                />
              </div>

              <div>
                <label>Fecha vencimiento</label>
                <input
                  type="date"
                  name="fecha_vencimiento"
                  value={form.fecha_vencimiento}
                  onChange={handleForm}
                />
              </div>
            </div>

            <label>Palabras clave</label>
            <input
              name="palabras_clave"
              value={form.palabras_clave}
              onChange={handleForm}
              placeholder="sst, auditoría, matriz, acta"
            />

            <label>Descripción</label>
            <textarea
              name="descripcion"
              value={form.descripcion}
              onChange={handleForm}
              rows={3}
            />

            <label>Archivo</label>
            <input type="file" name="file" onChange={handleForm} />

            <button className="btn-primary" type="submit" disabled={loading}>
              <Upload size={18} />
              Subir documento
            </button>
          </form>

          <aside className="preview-panel">
            <h3>Vista previa</h3>

            {previewUrl ? (
              <iframe src={previewUrl} title="Vista previa documental" />
            ) : (
              <div className="empty-preview">
                <FileText size={48} />
                <p>Seleccione un PDF para previsualizarlo.</p>
              </div>
            )}
          </aside>
        </section>

        <section className="biblioteca-list">
          <div className="list-header">
            <h3>Repositorio documental</h3>

            <div className="filters">
              <div className="search-box">
                <Search size={16} />
                <input
                  name="buscar"
                  value={filtros.buscar}
                  onChange={handleFiltro}
                  placeholder="Buscar documento..."
                />
              </div>

              <select name="empresa_id" value={filtros.empresa_id} onChange={handleFiltro}>
                <option value="">Todas las empresas</option>
                {empresas.map((empresa) => (
                  <option key={empresa.id} value={empresa.id}>
                    {empresa.nombre}
                  </option>
                ))}
              </select>

              <select name="categoria" value={filtros.categoria} onChange={handleFiltro}>
                <option value="">Todas las categorías</option>
                {CATEGORIAS.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>

              <select name="estado" value={filtros.estado} onChange={handleFiltro}>
                <option value="">Todos los estados</option>
                {ESTADOS.map((estado) => (
                  <option key={estado} value={estado}>
                    {estado}
                  </option>
                ))}
              </select>

              <button onClick={cargarDatos}>Filtrar</button>
            </div>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Título</th>
                  <th>Categoría</th>
                  <th>Versión</th>
                  <th>Estado</th>
                  <th>Responsable</th>
                  <th>Vencimiento</th>
                  <th>Archivo</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {documentos.map((doc) => (
                  <tr key={doc.id}>
                    <td>{doc.codigo_documental}</td>
                    <td>
                      <strong>{doc.titulo}</strong>
                      <small>{doc.descripcion}</small>
                    </td>
                    <td>{doc.categoria}</td>
                    <td>{doc.version}</td>
                    <td>
                      <span className={`estado estado-${doc.estado.toLowerCase()}`}>
                        {doc.estado}
                      </span>
                    </td>
                    <td>{doc.responsable || "Sin asignar"}</td>
                    <td>{doc.fecha_vencimiento || "No definido"}</td>
                    <td>{doc.archivo_nombre || "Sin archivo"}</td>
                    <td>
                      <div className="table-actions">
                        <button title="Vista previa" onClick={() => vistaPrevia(doc)}>
                          <Eye size={16} />
                        </button>

                        <button title="Descargar" onClick={() => abrirArchivo(doc.archivo_url)}>
                          <Download size={16} />
                        </button>

                        <button title="Marcar vigente" onClick={() => marcarVigente(doc.id)}>
                          <CheckCircle2 size={16} />
                        </button>

                        <button title="Marcar obsoleto" onClick={() => marcarObsoleto(doc.id)}>
                          <XCircle size={16} />
                        </button>

                        <button title="Eliminar" onClick={() => eliminarDocumento(doc.id)}>
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {documentos.length === 0 && (
                  <tr>
                    <td colSpan="9" className="empty">
                      No hay documentos registrados.
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
