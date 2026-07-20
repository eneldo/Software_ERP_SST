import React, { useEffect, useState } from "react";
import {
  FileText,
  Plus,
  Save,
  RefreshCcw,
  CheckCircle2,
  Trash2,
  Edit3,
  Printer,
  Image,
} from "lucide-react";

import api from "../../api/axios";
import AdminLayout from "../../layouts/AdminLayout";
import "../../styles/politica-sst.css";

export default function PoliticaSSTPage() {
  const [empresas, setEmpresas] = useState([]);
  const [politicas, setPoliticas] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    empresa_id: "",
    logo_url: "",
    titulo: "Política de Seguridad y Salud en el Trabajo",
    contenido:
      "La empresa se compromete con la protección y promoción de la salud de los trabajadores, procurando su integridad física, mental y social mediante la identificación de peligros, evaluación y valoración de riesgos, cumplimiento de la normatividad vigente y mejora continua del Sistema de Gestión de Seguridad y Salud en el Trabajo.",
    version: "1.0",
    estado: "BORRADOR",
    responsable_sst: "",
    representante_legal: "",
    fecha_aprobacion: "",
    fecha_vigencia: "",
    observaciones: "",
  });

  const mostrarError = (error, mensajeBase) => {
    console.error(error);

    const detail = error?.response?.data?.detail;

    if (Array.isArray(detail)) {
      alert(
        `${mensajeBase}\n\nDetalle:\n${detail
          .map((e) => `${e.loc?.join(".")}: ${e.msg}`)
          .join("\n")}`
      );
      return;
    }

    if (typeof detail === "string") {
      alert(`${mensajeBase}\n\nDetalle: ${detail}`);
      return;
    }

    alert(`${mensajeBase}\n\nRevisa la consola del navegador y la terminal del backend.`);
  };

  const cargarDatos = async () => {
    try {
      setLoading(true);

      const [empresasRes, politicasRes] = await Promise.all([
        api.get("/empresas/"),
        api.get("/planear/politica-sst/"),
      ]);

      setEmpresas(empresasRes.data);
      setPoliticas(politicasRes.data);
    } catch (error) {
      mostrarError(error, "No se pudo cargar Política SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const empresaSeleccionada = empresas.find(
    (empresa) => Number(empresa.id) === Number(form.empresa_id)
  );

  const limpiarFormulario = () => {
    setEditandoId(null);
    setForm({
      empresa_id: "",
      logo_url: "",
      titulo: "Política de Seguridad y Salud en el Trabajo",
      contenido:
        "La empresa se compromete con la protección y promoción de la salud de los trabajadores, procurando su integridad física, mental y social mediante la identificación de peligros, evaluación y valoración de riesgos, cumplimiento de la normatividad vigente y mejora continua del Sistema de Gestión de Seguridad y Salud en el Trabajo.",
      version: "1.0",
      estado: "BORRADOR",
      responsable_sst: "",
      representante_legal: "",
      fecha_aprobacion: "",
      fecha_vigencia: "",
      observaciones: "",
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm({
      ...form,
      [name]: value,
    });
  };

  const guardarPolitica = async (e) => {
    e.preventDefault();

    if (!form.empresa_id) {
      alert("Seleccione una empresa.");
      return;
    }

    const payload = {
      empresa_id: Number(form.empresa_id),
      titulo: form.titulo,
      contenido: form.contenido,
      version: form.version,
      estado: form.estado,
      responsable_sst: form.responsable_sst || null,
      representante_legal: form.representante_legal || null,
      fecha_aprobacion: form.fecha_aprobacion || null,
      fecha_vigencia: form.fecha_vigencia || null,
      observaciones: form.observaciones || null,
    };

    try {
      setLoading(true);

      if (editandoId) {
        await api.put(`/planear/politica-sst/${editandoId}`, payload);
      } else {
        await api.post("/planear/politica-sst/", payload);
      }

      limpiarFormulario();
      await cargarDatos();
      alert("Política SST guardada correctamente.");
    } catch (error) {
      mostrarError(error, "Error guardando Política SST.");
    } finally {
      setLoading(false);
    }
  };

  const editarPolitica = (politica) => {
    setEditandoId(politica.id);

    setForm({
      empresa_id: politica.empresa_id || "",
      logo_url: form.logo_url || "",
      titulo: politica.titulo || "",
      contenido: politica.contenido || "",
      version: politica.version || "1.0",
      estado: politica.estado || "BORRADOR",
      responsable_sst: politica.responsable_sst || "",
      representante_legal: politica.representante_legal || "",
      fecha_aprobacion: politica.fecha_aprobacion || "",
      fecha_vigencia: politica.fecha_vigencia || "",
      observaciones: politica.observaciones || "",
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const aprobarPolitica = async (id) => {
    if (!confirm("¿Desea aprobar esta Política SST?")) return;

    try {
      await api.patch(`/planear/politica-sst/${id}/aprobar`);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo aprobar la política.");
    }
  };

  const eliminarPolitica = async (id) => {
    if (!confirm("¿Desea desactivar esta Política SST?")) return;

    try {
      await api.delete(`/planear/politica-sst/${id}`);
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo eliminar la política.");
    }
  };

  const imprimirPDF = () => {
    if (!form.empresa_id) {
      alert("Seleccione una empresa antes de imprimir.");
      return;
    }

    setTimeout(() => {
      window.print();
    }, 200);
  };

  return (
    <AdminLayout>
      <div className="politica-page">
        <section className="politica-hero no-print">
          <div>
            <h2>Política SST</h2>
            <p>Crea, actualiza e imprime la política de Seguridad y Salud en el Trabajo.</p>
          </div>

          <div className="hero-actions">
            <button className="politica-print" onClick={imprimirPDF}>
              <Printer size={18} />
              Imprimir PDF
            </button>

            <button className="politica-refresh" onClick={cargarDatos}>
              <RefreshCcw size={18} />
              Actualizar
            </button>
          </div>
        </section>

        <section className="politica-grid">
          <form className="politica-form no-print" onSubmit={guardarPolitica}>
            <div className="form-title">
              <FileText size={22} />
              <div>
                <h3>{editandoId ? "Editar política" : "Nueva política"}</h3>
                <p>Complete la información documental de la política SST.</p>
              </div>
            </div>

            <label>Empresa</label>
            <select
              name="empresa_id"
              value={form.empresa_id}
              onChange={handleChange}
            >
              <option value="">Seleccione empresa</option>
              {empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>
                  {empresa.nombre}
                </option>
              ))}
            </select>

            <label>Logo empresa URL</label>
            <div className="logo-url-row">
              <Image size={18} />
              <input
                name="logo_url"
                value={form.logo_url}
                onChange={handleChange}
                placeholder="https://midominio.com/logo.png"
              />
            </div>

            <label>Título</label>
            <input name="titulo" value={form.titulo} onChange={handleChange} />

            <label>Contenido de la política</label>
            <textarea
              name="contenido"
              value={form.contenido}
              onChange={handleChange}
              rows={10}
            />

            <div className="form-row">
              <div>
                <label>Versión</label>
                <input
                  name="version"
                  value={form.version}
                  onChange={handleChange}
                />
              </div>

              <div>
                <label>Estado</label>
                <select name="estado" value={form.estado} onChange={handleChange}>
                  <option value="BORRADOR">BORRADOR</option>
                  <option value="APROBADA">APROBADA</option>
                  <option value="OBSOLETA">OBSOLETA</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div>
                <label>Responsable SST</label>
                <input
                  name="responsable_sst"
                  value={form.responsable_sst}
                  onChange={handleChange}
                />
              </div>

              <div>
                <label>Representante legal</label>
                <input
                  name="representante_legal"
                  value={form.representante_legal}
                  onChange={handleChange}
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
                  onChange={handleChange}
                />
              </div>

              <div>
                <label>Fecha vigencia</label>
                <input
                  type="date"
                  name="fecha_vigencia"
                  value={form.fecha_vigencia}
                  onChange={handleChange}
                />
              </div>
            </div>

            <label>Observaciones</label>
            <textarea
              name="observaciones"
              value={form.observaciones}
              onChange={handleChange}
              rows={3}
            />

            <div className="form-actions">
              <button type="submit" className="btn-primary" disabled={loading}>
                <Save size={18} />
                {editandoId ? "Actualizar" : "Guardar"}
              </button>

              <button type="button" className="btn-secondary" onClick={limpiarFormulario}>
                <Plus size={18} />
                Nueva
              </button>

              <button type="button" className="btn-print" onClick={imprimirPDF}>
                <Printer size={18} />
                Imprimir PDF
              </button>
            </div>
          </form>

          <div className="politica-preview print-area">
            <div className="screen-title no-print">
              <h3>Vista previa documental</h3>
              <p>Así se verá el documento impreso.</p>
            </div>

            <div className="document-card">
              <div className="print-header-pro">
                <div className="print-logo-box">
                  {form.logo_url ? (
                    <img src={form.logo_url} alt="Logo empresa" />
                  ) : (
                    <div className="logo-placeholder">LOGO</div>
                  )}
                </div>

                <div className="print-company">
                  <h2>{empresaSeleccionada?.nombre || "Empresa no seleccionada"}</h2>
                  <p>NIT: {empresaSeleccionada?.nit || "N/A"}</p>
                  <p>Dirección: {empresaSeleccionada?.direccion || "N/A"}</p>
                  <p>Teléfono: {empresaSeleccionada?.telefono || "N/A"}</p>
                </div>

                <div className="print-doc-code">
                  <strong>SG-SST</strong>
                  <span>POL-SST-{form.version}</span>
                  <small>Versión {form.version}</small>
                </div>
              </div>

              <div className="document-meta">
                <span>{form.estado}</span>
                <span>Vigencia: {form.fecha_vigencia || "Sin definir"}</span>
                <span>Aprobación: {form.fecha_aprobacion || "Sin definir"}</span>
              </div>

              <h4>{form.titulo}</h4>

              <p>{form.contenido}</p>

              {form.observaciones && (
                <div className="observaciones-print">
                  <strong>Observaciones:</strong>
                  <p>{form.observaciones}</p>
                </div>
              )}

              <div className="signature-grid">
                <div>
                  <strong>Responsable SST</strong>
                  <small>{form.responsable_sst || "Pendiente"}</small>
                </div>

                <div>
                  <strong>Representante legal</strong>
                  <small>{form.representante_legal || "Pendiente"}</small>
                </div>
              </div>

              <div className="print-footer">
                <p>
                  Documento generado desde ERP SST PRO · Sistema de Gestión de
                  Seguridad y Salud en el Trabajo.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="politica-list no-print">
          <h3>Histórico de políticas SST</h3>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Título</th>
                  <th>Versión</th>
                  <th>Estado</th>
                  <th>Responsable</th>
                  <th>Vigencia</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {politicas.map((p) => (
                  <tr key={p.id}>
                    <td>{p.id}</td>
                    <td>{p.titulo}</td>
                    <td>{p.version}</td>
                    <td>
                      <span className={`estado estado-${p.estado.toLowerCase()}`}>
                        {p.estado}
                      </span>
                    </td>
                    <td>{p.responsable_sst || "Sin asignar"}</td>
                    <td>{p.fecha_vigencia || "Sin fecha"}</td>
                    <td>
                      <div className="table-actions">
                        <button title="Editar" onClick={() => editarPolitica(p)}>
                          <Edit3 size={16} />
                        </button>

                        <button title="Aprobar" onClick={() => aprobarPolitica(p.id)}>
                          <CheckCircle2 size={16} />
                        </button>

                        <button title="Eliminar" onClick={() => eliminarPolitica(p.id)}>
                          <Trash2 size={16} />
                        </button>

                        <button
                          title="Cargar para imprimir"
                          onClick={() => {
                            editarPolitica(p);
                            setTimeout(() => window.print(), 300);
                          }}
                        >
                          <Printer size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {politicas.length === 0 && (
                  <tr>
                    <td colSpan="7" className="empty">
                      No hay políticas SST registradas.
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
