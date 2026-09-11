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
  Sidebar,
  LayoutDashboard,
  ChevronRight,
  ChevronLeft,
  X,
  Loader2,
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

const PASOS = [
  { key: "empresa", label: "1. Empresa", icon: "🏢" },
  { key: "cabecera", label: "2. Cabecera", icon: "📋" },
  { key: "actividades", label: "3. Actividades", icon: "📝" },
];

export default function PlanAnualPage() {
  const [empresas, setEmpresas] = useState([]);
  const [cabeceras, setCabeceras] = useState([]);
  const [items, setItems] = useState([]);
  const [editandoId, setEditandoId] = useState(null);
  const [empresaExportar, setEmpresaExportar] = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebarVisible, setSidebarVisible] = useState(true);

  const [pagina, setPagina] = useState(1);
  const [porPagina, setPorPagina] = useState(10);

  const [filtros, setFiltros] = useState({
    buscar: "",
    estado: "",
    responsable: "",
  });

  const [pasoActual, setPasoActual] = useState("empresa");
  const [empresaSeleccionada, setEmpresaSeleccionada] = useState(null);
  const [cabeceraSeleccionada, setCabeceraSeleccionada] = useState(null);

  const [formCabecera, setFormCabecera] = useState({
    vigencia: new Date().getFullYear().toString(),
    alcance: "",
    objetivo_general: "",
    meta_general: "",
    representante_legal_nombre: "",
    representante_legal_cargo: "",
    responsable_sst_nombre: "",
    responsable_sst_cargo: "",
  });

  const [form, setForm] = useState({
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

  const cargarEmpresas = async () => {
    try {
      const res = await api.get("/empresas/");
      setEmpresas(res.data);
      if (res.data.length > 0 && !empresaSeleccionada) {
        setEmpresaSeleccionada(res.data[0].id);
        setPasoActual("cabecera");
        await cargarCabeceras(res.data[0].id);
      }
    } catch (error) {
      mostrarError(error, "No se pudieron cargar las empresas.");
    }
  };

  const cargarCabeceras = async (empresaId) => {
    try {
      const res = await api.get(`/planear/plan-anual/cabeceras/${empresaId}`);
      setCabeceras(res.data);
      if (res.data.length > 0 && !cabeceraSeleccionada) {
        setCabeceraSeleccionada(res.data[0].id);
        setPasoActual("actividades");
        await cargarActividades(res.data[0].id);
      }
    } catch (error) {
      mostrarError(error, "No se pudieron cargar las cabeceras del Plan Anual.");
    }
  };

  const cargarActividades = async (cabeceraId) => {
    try {
      setLoading(true);
      const params = {};
      Object.entries(filtros).forEach(([key, value]) => {
        if (value) params[key] = value;
      });
      const res = await api.get(`/planear/plan-anual/cabecera/${cabeceraId}/actividades/`, { params });
      setItems(res.data);
      setPagina(1);
    } catch (error) {
      mostrarError(error, "No se pudieron cargar las actividades.");
    } finally {
      setLoading(false);
    }
  };

  const cargarDatosCompletos = async () => {
    if (!empresaSeleccionada) return;
    try {
      setLoading(true);
      await Promise.all([
        api.get("/empresas/").then(r => setEmpresas(r.data)),
        api.get(`/planear/plan-anual/cabeceras/${empresaSeleccionada}`).then(r => setCabeceras(r.data)),
      ]);
      if (cabeceras.length > 0 && !cabeceraSeleccionada) {
        setCabeceraSeleccionada(cabeceras[0].id);
        await cargarActividades(cabeceras[0].id);
      }
    } catch (error) {
      mostrarError(error, "No se pudo cargar el Plan Anual SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarEmpresas();
  }, []);

  useEffect(() => {
    if (cabeceraSeleccionada) {
      cargarActividades(cabeceraSeleccionada);
    }
  }, [cabeceraSeleccionada, filtros]);

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

  const limpiarFormActividad = () => {
    setEditandoId(null);
    setForm({
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
      [name]: name === "presupuesto" || name === "porcentaje_avance" ? Number(value) : value,
    });
  };

  const handleFormCabecera = (e) => {
    const { name, value } = e.target;
    setFormCabecera({ ...formCabecera, [name]: value });
  };

  const handleFiltro = (e) => {
    setFiltros({ ...filtros, [e.target.name]: e.target.value });
  };

  const guardarCabecera = async (e) => {
    e.preventDefault();
    if (!empresaSeleccionada || !formCabecera.vigencia) {
      alert("Empresa y vigencia son obligatorias.");
      return;
    }
    try {
      setLoading(true);
      if (cabeceraSeleccionada) {
        await api.put(`/planear/plan-anual/cabecera/${cabeceraSeleccionada}`, formCabecera);
        alert("Cabecera actualizada correctamente.");
      } else {
        const res = await api.post("/planear/plan-anual/cabecera/", {
          ...formCabecera,
          empresa_id: Number(empresaSeleccionada),
        });
        setCabeceraSeleccionada(res.data.id);
        setCabeceras((prev) => [...prev, res.data]);
        alert("Cabecera creada correctamente.");
      }
      setPasoActual("actividades");
      await cargarActividades(cabeceraSeleccionada);
    } catch (error) {
      mostrarError(error, "No se pudo guardar la cabecera.");
    } finally {
      setLoading(false);
    }
  };

  const nuevaCabecera = () => {
    setCabeceraSeleccionada(null);
    setFormCabecera({
      vigencia: new Date().getFullYear().toString(),
      alcance: "",
      objetivo_general: "",
      meta_general: "",
      representante_legal_nombre: "",
      representante_legal_cargo: "",
      responsable_sst_nombre: "",
      responsable_sst_cargo: "",
    });
  };

  const seleccionarCabecera = async (cabecera) => {
    setCabeceraSeleccionada(cabecera.id);
    setFormCabecera({
      vigencia: cabecera.vigencia,
      alcance: cabecera.alcance || "",
      objetivo_general: cabecera.objetivo_general || "",
      meta_general: cabecera.meta_general || "",
      representante_legal_nombre: cabecera.representante_legal_nombre || "",
      representante_legal_cargo: cabecera.representante_legal_cargo || "",
      responsable_sst_nombre: cabecera.responsable_sst_nombre || "",
      responsable_sst_cargo: cabecera.responsable_sst_cargo || "",
    });
    setPasoActual("actividades");
    await cargarActividades(cabecera.id);
  };

  const volverAEmpresa = () => {
    setPasoActual("empresa");
    setEmpresaSeleccionada(null);
    setCabeceras([]);
    setCabeceraSeleccionada(null);
    setItems([]);
  };

  const volverACabecera = () => {
    setPasoActual("cabecera");
    setCabeceraSeleccionada(null);
    setItems([]);
  };

  const guardar = async (e) => {
    e.preventDefault();
    if (!cabeceraSeleccionada || !form.actividad) {
      alert("Cabecera y actividad son obligatorias.");
      return;
    }
    const payload = {
      ...form,
      plan_anual_cabecera_id: cabeceraSeleccionada,
      presupuesto: Number(form.presupuesto || 0),
      porcentaje_avance: Number(form.porcentaje_avance || 0),
      fecha_inicio: form.fecha_inicio || null,
      fecha_fin: form.fecha_fin || null,
    };
    try {
      setLoading(true);
      if (editandoId) {
        await api.put(`/planear/plan-anual/actividades/${editandoId}`, payload);
      } else {
        await api.post(`/planear/plan-anual/cabecera/${cabeceraSeleccionada}/actividades/`, payload);
      }
      limpiarFormActividad();
      await cargarActividades(cabeceraSeleccionada);
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
      await api.delete(`/planear/plan-anual/actividades/${id}`);
      await cargarActividades(cabeceraSeleccionada);
    } catch (error) {
      mostrarError(error, "No se pudo eliminar la actividad.");
    }
  };

  const finalizar = async (id) => {
    if (!confirm("¿Desea finalizar esta actividad?")) return;
    try {
      await api.patch(`/planear/plan-anual/actividades/${id}/finalizar`);
      await cargarActividades(cabeceraSeleccionada);
    } catch (error) {
      mostrarError(error, "No se pudo finalizar la actividad.");
    }
  };

  const cargarBase = async () => {
    if (!empresaSeleccionada) {
      alert("Seleccione empresa.");
      return;
    }
    try {
      await api.post(`/planear/plan-anual/cargar-base/${empresaSeleccionada}`);
      await cargarDatosCompletos();
      alert("Base del Plan Anual SST cargada correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo cargar la base del Plan Anual SST.");
    }
  };

  const descargar = async (url, nombre) => {
    if (!empresaSeleccionada) {
      alert("Seleccione empresa para exportar.");
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
      `/exportaciones-sst/plan-anual/pdf/${empresaSeleccionada}`,
      "plan_anual_sst.pdf"
    );

  const exportarExcel = () =>
    descargar(
      `/exportaciones-sst/plan-anual/excel/${empresaSeleccionada}`,
      "plan_anual_sst.xlsx"
    );

  const subirEvidencia = async (item, file) => {
    if (!file) return;
    const data = new FormData();
    data.append("descripcion", `Evidencia Plan Anual SST ${item.codigo}`);
    data.append("file", file);
    try {
      await api.post(`/planear/plan-anual/actividades/${item.id}/evidencia`, data, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await cargarActividades(cabeceraSeleccionada);
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

  const pasoCompletado = (paso) => {
    const indices = { empresa: 0, cabecera: 1, actividades: 2 };
    return indices[paso] < indices[pasoActual];
  };

  const pasoActivo = (paso) => paso === pasoActual;

  return (
    <AdminLayout>
      <div className="plan-anual-page">
        <section className="pa-hero">
          <div>
            <h2>Plan Anual SST</h2>
            <p>Programa actividades, responsables, presupuesto y seguimiento del SG-SST.</p>
          </div>

          <nav className="pa-stepper" aria-label="Pasos del Plan Anual">
            {PASOS.map((paso, idx) => (
              <button
                key={paso.key}
                type="button"
                className={`pa-step ${pasoActivo(paso.key) ? "active" : ""} ${pasoCompletado(paso.key) ? "completed" : ""} ${idx > 0 ? "disabled" : ""}`}
                onClick={() => {
                  if (idx === 0) volverAEmpresa();
                  else if (idx === 1 && empresaSeleccionada) volverACabecera();
                }}
                disabled={idx > 0 && !pasoCompletado(paso.key)}
              >
                <span className="pa-step-icon">{paso.icon}</span>
                <span className="pa-step-label">{paso.label}</span>
                {idx < PASOS.length - 1 && <ChevronRight className="pa-step-sep" size={16} />}
              </button>
            ))}
          </nav>

          <div className="pa-actions">
            <button
              type="button"
              className="pa-toggle-sidebar"
              title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
              onClick={() => setSidebarVisible((v) => !v)}
            >
              {sidebarVisible ? <Sidebar size={17} /> : <LayoutDashboard size={17} />}
            </button>

            {pasoActual === "empresa" && (
              <select
                value={empresaSeleccionada}
                onChange={(e) => {
                  setEmpresaSeleccionada(Number(e.target.value));
                  if (e.target.value) {
                    setPasoActual("cabecera");
                    cargarCabeceras(Number(e.target.value));
                  }
                }}
              >
                <option value="">Seleccionar empresa</option>
                {empresas.map((empresa) => (
                  <option key={empresa.id} value={empresa.id}>
                    {empresa.nombre}
                  </option>
                ))}
              </select>
            )}

            {pasoActual === "cabecera" && empresaSeleccionada && (
              <>
                <select
                  value={cabeceraSeleccionada || ""}
                  onChange={(e) => {
                    if (e.target.value) {
                      const cab = cabeceras.find((c) => c.id === Number(e.target.value));
                      if (cab) seleccionarCabecera(cab);
                    } else {
                      setCabeceraSeleccionada(null);
                    }
                  }}
                >
                  <option value="">Seleccionar vigencia</option>
                  {cabeceras.map((cab) => (
                    <option key={cab.id} value={cab.id}>
                      {cab.vigencia} - {cab.objetivo_general?.substring(0, 50) || "Sin objetivo"}
                    </option>
                  ))}
                </select>
                <button type="button" onClick={nuevaCabecera} className="btn-nueva-cabecera">
                  <Plus size={17} /> Nueva vigencia
                </button>
              </>
            )}

            {pasoActual === "actividades" && cabeceraSeleccionada && (
              <>
                <select
                  value={empresaExportar || cabeceraSeleccionada}
                  onChange={(e) => setEmpresaExportar(e.target.value)}
                >
                  <option value="">Empresa para exportar</option>
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
              </>
            )}

            <button type="button" onClick={cargarDatosCompletos} className="btn-refresh" disabled={loading}>
              {loading ? <Loader2 size={17} className="spinning" /> : <RefreshCcw size={17} />} Actualizar
            </button>
          </div>
        </section>

        {pasoActual === "cabecera" && empresaSeleccionada && !cabeceraSeleccionada && (
          <section className="pa-cabecera-form">
            <h3>Nueva Cabecera del Plan Anual - Vigencia {formCabecera.vigencia}</h3>
            <form className="pa-form" onSubmit={guardarCabecera}>
              <div className="pa-form-section">
                <h4>Información General (Decreto 1072/2015)</h4>
                <div className="form-row">
                  <label>
                    Vigencia (Año)
                    <input
                      name="vigencia"
                      value={formCabecera.vigencia}
                      onChange={handleFormCabecera}
                      placeholder="Ej: 2026"
                      maxLength="4"
                      pattern="\\d{4}"
                    />
                  </label>
                </div>

                <label>
                  Alcance del Plan
                  <textarea
                    name="alcance"
                    value={formCabecera.alcance}
                    onChange={handleFormCabecera}
                    placeholder="Ej: Este plan contempla las actividades de Seguridad y Salud en el Trabajo para la vigencia 2026, aplicable a toda la empresa, sus sedes, contratistas y personal en misión."
                    rows={3}
                  />
                </label>

                <label>
                  Objetivo General del Plan
                  <textarea
                    name="objetivo_general"
                    value={formCabecera.objetivo_general}
                    onChange={handleFormCabecera}
                    placeholder="Ej: Garantizar la implementación efectiva y la mejora continua del Sistema de Gestión de la Seguridad y Salud en el Trabajo (SG-SST)."
                    rows={3}
                  />
                </label>

                <label>
                  Meta General del Plan
                  <textarea
                    name="meta_general"
                    value={formCabecera.meta_general}
                    onChange={handleFormCabecera}
                    placeholder="Ej: Cumplir 100% de las actividades programadas, reducir los indicadores de accidentalidad en un 20% y lograr la certificación del SG-SST."
                    rows={3}
                  />
                </label>
              </div>

              <div className="pa-form-section">
                <h4>Firmas (Decreto 1072/2015)</h4>
                <div className="form-row two-signatures">
                  <div className="pa-signature-block">
                    <strong>Representante Legal / Empleador</strong>
                    <input
                      name="representante_legal_nombre"
                      value={formCabecera.representante_legal_nombre}
                      onChange={handleFormCabecera}
                      placeholder="Nombre completo"
                    />
                    <input
                      name="representante_legal_cargo"
                      value={formCabecera.representante_legal_cargo}
                      onChange={handleFormCabecera}
                      placeholder="Cargo"
                    />
                  </div>

                  <div className="pa-signature-block">
                    <strong>Responsable SG-SST</strong>
                    <input
                      name="responsable_sst_nombre"
                      value={formCabecera.responsable_sst_nombre}
                      onChange={handleFormCabecera}
                      placeholder="Nombre completo"
                    />
                    <input
                      name="responsable_sst_cargo"
                      value={formCabecera.responsable_sst_cargo}
                      onChange={handleFormCabecera}
                      placeholder="Cargo"
                    />
                  </div>
                </div>
              </div>

              <div className="form-actions">
                <button className="btn-primary" type="submit" disabled={loading}>
                  <Save size={17} /> {cabeceraSeleccionada ? "Actualizar Cabecera" : "Crear Cabecera"}
                </button>
                <button type="button" className="btn-secondary" onClick={volverAEmpresa}>
                  <ChevronLeft size={17} /> Volver a Empresa
                </button>
              </div>
            </form>
          </section>
        )}

        {pasoActual === "actividades" && cabeceraSeleccionada && (
          <>
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

            <section className={`pa-grid ${!sidebarVisible ? "pa-panel-collapsed" : ""}`}>
              <form className="pa-form" onSubmit={guardar}>
                <h3>{editandoId ? "Editar actividad" : "Nueva actividad"}</h3>

                <div className="pa-cabecera-info">
                  <strong>Vigencia: {cabeceras.find(c => c.id === cabeceraSeleccionada)?.vigencia || "N/A"}</strong>
                  <span>{cabeceras.find(c => c.id === cabeceraSeleccionada)?.objetivo_general || ""}</span>
                </div>

                <label>Código</label>
                <input
                  name="codigo"
                  value={form.codigo}
                  onChange={handleForm}
                  placeholder="Código (ej: PA-SST-001)"
                />

                <textarea
                  name="actividad"
                  value={form.actividad}
                  onChange={handleForm}
                  placeholder="Actividad del Plan Anual SST"
                  required
                />

                <textarea
                  name="objetivo"
                  value={form.objetivo}
                  onChange={handleForm}
                  placeholder="Objetivo específico de la actividad"
                />

                <div className="form-row">
                  <input
                    name="responsable"
                    value={form.responsable}
                    onChange={handleForm}
                    placeholder="Responsable"
                  />
                  <input
                    type="number"
                    name="presupuesto"
                    value={form.presupuesto}
                    onChange={handleForm}
                    placeholder="Presupuesto"
                    min="0"
                  />
                </div>

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
                    name="indicador"
                    value={form.indicador}
                    onChange={handleForm}
                    placeholder="Indicador de gestión"
                  />
                  <input
                    name="meta"
                    value={form.meta}
                    onChange={handleForm}
                    placeholder="Meta (ej: 100%)"
                  />
                </div>

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
                  <button type="button" className="btn-secondary" onClick={limpiarFormActividad}>
                    <Plus size={17} /> Nuevo
                  </button>
                </div>
              </form>

              <aside className={`pa-panel ${!sidebarVisible ? "pa-panel-hidden" : ""}`}>
                <div className="pa-panel-header">
                  <h3>Resumen del Plan Anual</h3>
                  <button
                    type="button"
                    className="pa-sidebar-toggle-btn"
                    onClick={() => setSidebarVisible((v) => !v)}
                    title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
                    aria-label={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
                    aria-pressed={!sidebarVisible}
                  >
                    {sidebarVisible ? <Sidebar size={18} /> : <LayoutDashboard size={18} />}
                  </button>
                </div>
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
                                <Eye size={14} /> Ver
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
                                <Download size={14} /> Descargar
                              </button>
                              <label className="btn-upload-mini">
                                <Upload size={14} /> Reemplazar
                                <input
                                  type="file"
                                  hidden
                                  onChange={(e) => subirEvidencia(item, e.target.files[0])}
                                />
                              </label>
                            </div>
                          ) : (
                            <label className="btn-upload-mini">
                              <Upload size={14} /> Cargar
                              <input
                                type="file"
                                hidden
                                onChange={(e) => subirEvidencia(item, e.target.files[0])}
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
                          No hay actividades registradas para esta cabecera.{" "}
                          <button type="button" onClick={limpiarFormActividad} className="btn-link">
                            Crear la primera actividad
                          </button>
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
          </>
        )}
      </div>
    </AdminLayout>
  );
}