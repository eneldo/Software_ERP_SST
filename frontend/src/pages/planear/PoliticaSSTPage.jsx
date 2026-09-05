import React, { useEffect, useState, useMemo } from "react";
import {
  FileText,
  Plus,
  Save,
  RefreshCcw,
  CheckCircle2,
  Trash2,
  Edit3,
  Printer,
  LayoutDashboard,
  Sidebar,
  AlertTriangle,
  Clock,
  FileWarning,
  ShieldCheck,
  ClipboardList,
  TrendingUp,
  Eye,
  Users,
  ClipboardCheck,
  FileCheck,
} from "lucide-react";

import api from "../../api/axios";
import { construirUrlLogoEmpresa } from "../../api/empresaSstApi";
import AdminLayout from "../../layouts/AdminLayout";
import "../../styles/politica-sst.css";

export default function PoliticaSSTPage() {
  const [empresas, setEmpresas] = useState([]);
  const [politicas, setPoliticas] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [modalDivulgada, setModalDivulgada] = useState({ open: false, politica: null, accion: null });
  const [modalActa, setModalActa] = useState({ open: false, politica: null, accion: null });

  const [tiposPolitica, setTiposPolitica] = useState([]);

  const [form, setForm] = useState({
    empresa_id: "",
    tipo_politica: "POLITICA_SST",
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

      const [empresasRes, politicasRes, tiposRes] = await Promise.all([
        api.get("/empresas/"),
        api.get("/planear/politica-sst/"),
        api.get("/planear/politica-sst/tipos"),
      ]);

      setEmpresas(empresasRes.data);
      setPoliticas(politicasRes.data);
      setTiposPolitica(tiposRes.data);
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

  const logoUrl = empresaSeleccionada?.logo
    ? construirUrlLogoEmpresa(empresaSeleccionada.logo)
    : null;

  const sidebarStats = useMemo(() => {
    const total = politicas.length;
    const borradores = politicas.filter((p) => p.estado === "BORRADOR").length;
    const aprobadas = politicas.filter((p) => p.estado === "APROBADA").length;
    const obsoletas = politicas.filter((p) => p.estado === "OBSOLETA").length;
    const porcentajeAprobadas = total > 0 ? Math.round((aprobadas / total) * 100) : 0;
    const sinResponsable = politicas.filter((p) => !p.responsable_sst).length;
    const sinVigencia = politicas.filter((p) => !p.fecha_vigencia).length;
    const hoy = new Date();
    const porVencer = politicas.filter((p) => {
      if (!p.fecha_vigencia) return false;
      const anio = Number(p.fecha_vigencia.substring(0, 4));
      const finVigencia = new Date(anio, 11, 31);
      const diff = (finVigencia - hoy) / (1000 * 60 * 60 * 24);
      return diff > 0 && diff <= 90;
    }).length;
    const vencidas = politicas.filter((p) => {
      if (!p.fecha_vigencia) return false;
      const anio = Number(p.fecha_vigencia.substring(0, 4));
      return new Date(anio, 11, 31) < hoy;
    }).length;

    let statusLabel = "Sin políticas";
    let statusTone = "pol-tone-neutral";
    if (total === 0) {
      statusLabel = "Sin políticas registradas";
      statusTone = "pol-tone-neutral";
    } else if (porcentajeAprobadas >= 80) {
      statusLabel = "Gestión documental sólida";
      statusTone = "pol-tone-green";
    } else if (porcentajeAprobadas >= 50) {
      statusLabel = "En proceso de formalización";
      statusTone = "pol-tone-amber";
    } else {
      statusLabel = "Requiere atención urgente";
      statusTone = "pol-tone-red";
    }

    return {
      total,
      borradores,
      aprobadas,
      obsoletas,
      porcentajeAprobadas,
      sinResponsable,
      sinVigencia,
      porVencer,
      vencidas,
      statusLabel,
      statusTone,
    };
  }, [politicas]);

  const limpiarFormulario = () => {
    setEditandoId(null);
    setForm({
      empresa_id: "",
      tipo_politica: "POLITICA_SST",
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
      tipo_politica: form.tipo_politica,
      titulo: form.titulo,
      contenido: form.contenido,
      version: form.version,
      estado: form.estado,
      responsable_sst: form.responsable_sst || null,
      representante_legal: form.representante_legal || null,
      fecha_aprobacion: form.fecha_aprobacion || null,
      fecha_vigencia: form.fecha_vigencia ? `${form.fecha_vigencia}-01-01` : null,
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
      tipo_politica: politica.tipo_politica || "POLITICA_SST",
      titulo: politica.titulo || "",
      contenido: politica.contenido || "",
      version: politica.version || "1.0",
      estado: politica.estado || "BORRADOR",
      responsable_sst: politica.responsable_sst || "",
      representante_legal: politica.representante_legal || "",
      fecha_aprobacion: politica.fecha_aprobacion || "",
      fecha_vigencia: politica.fecha_vigencia ? politica.fecha_vigencia.substring(0, 4) : "",
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

  const abrirModalDivulgada = (politica) => {
    setModalDivulgada({ open: true, politica, accion: politica.divulgada_copasst ? "quitar" : "poner" });
  };

  const confirmarToggleDivulgada = async () => {
    const { politica, accion } = modalDivulgada;
    if (!politica) return;

    try {
      await api.put(`/planear/politica-sst/${politica.id}`, {
        divulgada_copasst: accion === "poner",
      });
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo actualizar divulgación COPASST.");
    } finally {
      setModalDivulgada({ open: false, politica: null, accion: null });
    }
  };

  const abrirModalActa = (politica) => {
    setModalActa({ open: true, politica, accion: politica.tiene_acta_divulgacion ? "quitar" : "poner" });
  };

  const confirmarToggleActa = async () => {
    const { politica, accion } = modalActa;
    if (!politica) return;

    try {
      await api.put(`/planear/politica-sst/${politica.id}`, {
        tiene_acta_divulgacion: accion === "poner",
      });
      await cargarDatos();
    } catch (error) {
      mostrarError(error, "No se pudo actualizar acta de divulgación.");
    } finally {
      setModalActa({ open: false, politica: null, accion: null });
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
            <button
              className="politica-toggle-sidebar"
              title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
              onClick={() => setSidebarVisible((v) => !v)}
            >
              {sidebarVisible ? <Sidebar size={17} /> : <LayoutDashboard size={17} />}
            </button>

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

        <section className={`pol-main-grid ${!sidebarVisible ? "pol-panel-collapsed" : ""}`}>
          <div className="pol-content">
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

            <label>Tipo de Política</label>
            <select
              name="tipo_politica"
              value={form.tipo_politica}
              onChange={handleChange}
            >
              {tiposPolitica.length > 0 ? (
                tiposPolitica.map((tipo) => (
                  <option key={tipo.codigo} value={tipo.codigo}>
                    {tipo.nombre}
                  </option>
                ))
              ) : (
                <>
                  <option value="POLITICA_SST">Política SST</option>
                  <option value="CONVIVENCIA">Convivencia Laboral</option>
                  <option value="ALCOHOL_TABACO">Alcohol, Tabaco y Sustancias</option>
                  <option value="PREVENCION_INCENDIOS">Prevención de Incendios</option>
                  <option value="PROTECCION_DATOS">Protección de Datos</option>
                </>
              )}
            </select>

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
                <label>Vigencia (año)</label>
                <input
                  type="number"
                  name="fecha_vigencia"
                  value={form.fecha_vigencia}
                  onChange={handleChange}
                  placeholder="2026"
                  min="2020"
                  max="2050"
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
                  {logoUrl ? (
                    <img src={logoUrl} alt="Logo empresa" />
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
                  <th>Tipo</th>
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
                    <td>
                      <span className="estado estado-tipo">
                        {(p.tipo_politica || "POLITICA_SST").replace(/_/g, " ")}
                      </span>
                    </td>
                    <td>{p.titulo}</td>
                    <td>{p.version}</td>
                    <td>
                      <span className={`estado estado-${p.estado.toLowerCase()}`}>
                        {p.estado}
                      </span>
                    </td>
                    <td>{p.responsable_sst || "Sin asignar"}</td>
                    <td>{p.fecha_vigencia ? p.fecha_vigencia.substring(0, 4) : "Sin fecha"}</td>
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

                        {p.estado === "APROBADA" && (
                          <>
                            <button
                              title={p.divulgada_copasst ? "Quitar divulgación COPASST" : "Marcar divulgada al COPASST"}
                              onClick={() => abrirModalDivulgada(p)}
                              className={p.divulgada_copasst ? "active" : ""}
                            >
                              <Users size={16} />
                            </button>

                            <button
                              title={p.tiene_acta_divulgacion ? "Quitar acta de divulgación" : "Marcar acta de divulgación"}
                              onClick={() => abrirModalActa(p)}
                              className={p.tiene_acta_divulgacion ? "active" : ""}
                            >
                              <ClipboardCheck size={16} />
                            </button>
                          </>
                        )}
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

          <aside className={`pol-right-panel ${!sidebarVisible ? "pol-panel-hidden" : ""}`}>
            <article className="pol-intel-card">
              <div className="pol-side-title-row">
                <h3>Dashboard inteligente</h3>
                <div className="pol-sidebar-header-actions">
                  <button
                    type="button"
                    className="pol-sidebar-toggle-btn"
                    onClick={() => setSidebarVisible((v) => !v)}
                    title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
                    aria-label={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
                    aria-pressed={!sidebarVisible}
                  >
                    {sidebarVisible ? <Sidebar size={18} /> : <LayoutDashboard size={18} />}
                  </button>
                  <span className="pol-ai-badge">AI</span>
                </div>
              </div>
              <div className="pol-intel-body">
                <div className="pol-ring" style={{ "--pol-ring": `${sidebarStats.porcentajeAprobadas}%` }}>
                  <strong>{sidebarStats.porcentajeAprobadas}%</strong>
                  <span>Aprobadas</span>
                </div>
                <div className="pol-intel-copy">
                  <h4>{sidebarStats.statusLabel}</h4>
                  <p>{sidebarStats.total} políticas registradas en el sistema</p>
                  <em className={sidebarStats.statusTone}>
                    {sidebarStats.total === 0
                      ? "Registre la primera política SST"
                      : sidebarStats.porcentajeAprobadas >= 80
                        ? "Cumplimiento documental alto"
                        : "Mejore la tasa de aprobación"}
                  </em>
                </div>
              </div>
              <div className="pol-intel-mini-stats">
                <div className="pol-mini-stat">
                  <strong>{sidebarStats.total}</strong>
                  <span>Total</span>
                </div>
                <div className="pol-mini-stat pol-mini-green">
                  <strong>{sidebarStats.aprobadas}</strong>
                  <span>Aprobadas</span>
                </div>
                <div className="pol-mini-stat pol-mini-amber">
                  <strong>{sidebarStats.borradores}</strong>
                  <span>Borradores</span>
                </div>
                <div className="pol-mini-stat pol-mini-red">
                  <strong>{sidebarStats.obsoletas}</strong>
                  <span>Obsoletas</span>
                </div>
              </div>
            </article>

            <article className="pol-side-card">
              <div className="pol-side-title-row">
                <h3><AlertTriangle size={16} /> Alertas inteligentes</h3>
              </div>
              <div className="pol-alert-list">
                <div className="pol-alert-row">
                  <span className="pol-alert-dot pol-dot-amber" />
                  <span>{sidebarStats.borradores} políticas en borrador</span>
                  <em>{sidebarStats.borradores > 0 ? "Revisar" : "OK"}</em>
                </div>
                <div className="pol-alert-row">
                  <span className="pol-alert-dot pol-dot-orange" />
                  <span>{sidebarStats.porVencer} por vencer (90 días)</span>
                  <em>{sidebarStats.porVencer > 0 ? "Atención" : "OK"}</em>
                </div>
                <div className="pol-alert-row">
                  <span className="pol-alert-dot pol-dot-red" />
                  <span>{sidebarStats.vencidas} políticas vencidas</span>
                  <em>{sidebarStats.vencidas > 0 ? "Crítico" : "OK"}</em>
                </div>
                <div className="pol-alert-row">
                  <span className="pol-alert-dot pol-dot-gray" />
                  <span>{sidebarStats.obsoletas} políticas obsoletas</span>
                  <em>{sidebarStats.obsoletas > 0 ? "Archivar" : "OK"}</em>
                </div>
                <div className="pol-alert-row">
                  <span className="pol-alert-dot pol-dot-blue" />
                  <span>{sidebarStats.sinResponsable} sin responsable asignado</span>
                  <em>{sidebarStats.sinResponsable > 0 ? "Asignar" : "OK"}</em>
                </div>
                <div className="pol-alert-row">
                  <span className="pol-alert-dot pol-dot-purple" />
                  <span>{sidebarStats.sinVigencia} sin fecha de vigencia</span>
                  <em>{sidebarStats.sinVigencia > 0 ? "Definir" : "OK"}</em>
                </div>
              </div>
            </article>

            <article className="pol-side-card">
              <div className="pol-side-title-row">
                <h3><TrendingUp size={16} /> Distribución por estado</h3>
              </div>
              <div className="pol-distribution">
                <div className="pol-dist-row">
                  <div className="pol-dist-header">
                    <span>Aprobadas</span>
                    <span>{sidebarStats.aprobadas} / {sidebarStats.total}</span>
                  </div>
                  <div className="pol-dist-bar">
                    <div
                      className="pol-dist-fill pol-fill-green"
                      style={{ width: sidebarStats.total > 0 ? `${(sidebarStats.aprobadas / sidebarStats.total) * 100}%` : "0%" }}
                    />
                  </div>
                </div>
                <div className="pol-dist-row">
                  <div className="pol-dist-header">
                    <span>Borradores</span>
                    <span>{sidebarStats.borradores} / {sidebarStats.total}</span>
                  </div>
                  <div className="pol-dist-bar">
                    <div
                      className="pol-dist-fill pol-fill-amber"
                      style={{ width: sidebarStats.total > 0 ? `${(sidebarStats.borradores / sidebarStats.total) * 100}%` : "0%" }}
                    />
                  </div>
                </div>
                <div className="pol-dist-row">
                  <div className="pol-dist-header">
                    <span>Obsoletas</span>
                    <span>{sidebarStats.obsoletas} / {sidebarStats.total}</span>
                  </div>
                  <div className="pol-dist-bar">
                    <div
                      className="pol-dist-fill pol-fill-red"
                      style={{ width: sidebarStats.total > 0 ? `${(sidebarStats.obsoletas / sidebarStats.total) * 100}%` : "0%" }}
                    />
                  </div>
                </div>
              </div>
            </article>

            <article className="pol-side-card">
              <div className="pol-side-title-row">
                <h3><ClipboardList size={16} /> Recomendaciones PRO</h3>
              </div>
              <div className="pol-rec-list">
                {sidebarStats.borradores > 0 && (
                  <div className="pol-rec-row">
                    <span className="pol-rec-num">1</span>
                    <span>Revise y apruebe las {sidebarStats.borradores} políticas en borrador para formalizar la documentación SST.</span>
                  </div>
                )}
                {sidebarStats.vencidas > 0 && (
                  <div className="pol-rec-row">
                    <span className="pol-rec-num">{sidebarStats.borradores > 0 ? 2 : 1}</span>
                    <span>Actualice las {sidebarStats.vencidas} políticas vencidas para mantener la vigencia del SG-SST.</span>
                  </div>
                )}
                {sidebarStats.sinResponsable > 0 && (
                  <div className="pol-rec-row">
                    <span className="pol-rec-num">{(sidebarStats.borradores > 0 ? 1 : 0) + (sidebarStats.vencidas > 0 ? 1 : 0) + 1}</span>
                    <span>Asigne un responsable SST a las {sidebarStats.sinResponsable} políticas que carecen de uno.</span>
                  </div>
                )}
                {sidebarStats.total > 0 && sidebarStats.porcentajeAprobadas < 80 && (
                  <div className="pol-rec-row">
                    <span className="pol-rec-num">{(sidebarStats.borradores > 0 ? 1 : 0) + (sidebarStats.vencidas > 0 ? 1 : 0) + (sidebarStats.sinResponsable > 0 ? 1 : 0) + 1}</span>
                    <span>Mejore la tasa de aprobación actual ({sidebarStats.porcentajeAprobadas}%) para alcanzar el 80% mínimo recomendado.</span>
                  </div>
                )}
                {sidebarStats.total === 0 && (
                  <div className="pol-rec-row">
                    <span className="pol-rec-num">1</span>
                    <span>Comience creando la política SST base para su empresa. Es el primer paso del SG-SST.</span>
                  </div>
                )}
              </div>
            </article>
          </aside>
        </section>
      </div>

      {modalDivulgada.open && modalDivulgada.politica && (
        <div className="modal-overlay" onClick={() => setModalDivulgada({ open: false, politica: null, accion: null })}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3>{modalDivulgada.accion === "poner" ? "Confirmar divulgación al COPASST" : "Quitar divulgación al COPASST"}</h3>
            <p dangerouslySetInnerHTML={{ __html: modalDivulgada.accion === "poner"
              ? `¿Marcar la política <strong>"${modalDivulgada.politica.titulo}"</strong> como divulgada al COPASST?`
              : `¿Quitar la marca de divulgación al COPASST de la política <strong>"${modalDivulgada.politica.titulo}"</strong>?`
            }} />
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setModalDivulgada({ open: false, politica: null, accion: null })}>
                Cancelar
              </button>
              <button className="btn-primary" onClick={confirmarToggleDivulgada}>
                {modalDivulgada.accion === "poner" ? "Confirmar divulgación" : "Quitar divulgación"}
              </button>
            </div>
          </div>
        </div>
      )}

      {modalActa.open && modalActa.politica && (
        <div className="modal-overlay" onClick={() => setModalActa({ open: false, politica: null, accion: null })}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3>{modalActa.accion === "poner" ? "Confirmar acta de divulgación" : "Quitar acta de divulgación"}</h3>
            <p dangerouslySetInnerHTML={{ __html: modalActa.accion === "poner"
              ? `¿Marcar que existe <strong>acta de divulgación</strong> para la política <strong>"${modalActa.politica.titulo}"</strong>?`
              : `¿Quitar la marca de acta de divulgación de la política <strong>"${modalActa.politica.titulo}"</strong>?`
            }} />
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setModalActa({ open: false, politica: null, accion: null })}>
                Cancelar
              </button>
              <button className="btn-primary" onClick={confirmarToggleActa}>
                {modalActa.accion === "poner" ? "Confirmar acta" : "Quitar acta"}
              </button>
            </div>
          </div>
        </div>
      )}

    </AdminLayout>
  );
}
