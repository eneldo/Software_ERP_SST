import React, { useEffect, useState, useMemo } from "react";
import {
  Shield, Plus, RefreshCcw, Trash2, Database, Eye, Edit3,
  FileSpreadsheet, FileText, Table2, ChevronDown, Search,
  AlertTriangle, TrendingUp, BarChart3, PieChart, Activity
} from "lucide-react";
import { PieChart as RePieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import AdminLayout from "../../layouts/AdminLayout";
import MatrizIPERForm from "../../components/matriziper/MatrizIPERForm";
import MatrizIPERDetail from "../../components/matriziper/MatrizIPERDetail";
import MatrizIPERTable from "../../components/matriziper/MatrizIPERTable";
import { matrizIperApi } from "../../api/matrizIperApi";
import api from "../../api/axios";
import "../../styles/matriz-iper.css";

const CLASIFICACION_LABELS = {
  FISICO: "Físico",
  QUIMICO: "Químico",
  BIOLOGICO: "Biológico",
  BIOMECANICO: "Biomecánico",
  PSICOSOCIAL: "Psicosocial",
  CONDICIONES_SEGURIDAD: "Condiciones de Seguridad",
  FENOMENOS_NATURALES: "Fenómenos Naturales",
};

const CLASIFICACIONES = [
  "FISICO", "QUIMICO", "BIOLOGICO", "BIOMECANICO",
  "PSICOSOCIAL", "CONDICIONES_SEGURIDAD", "FENOMENOS_NATURALES"
];

export default function MatrizIPERPage() {
  const [empresas, setEmpresas] = useState([]);
  const [empresaId, setEmpresaId] = useState("");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mostrarForm, setMostrarForm] = useState(false);
  const [editarFila, setEditarFila] = useState(null);
  const [verDetalle, setVerDetalle] = useState(null);
  const [verMatriz, setVerMatriz] = useState(false);

  // Filtros
  const [filtroBusqueda, setFiltroBusqueda] = useState("");
  const [filtroClasificacion, setFiltroClasificacion] = useState("");
  const [filtroRiesgo, setFiltroRiesgo] = useState("");

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const [empresasRes] = await Promise.all([api.get("/empresas/")]);
      setEmpresas(empresasRes.data);
      if (empresasRes.data.length > 0 && !empresaId) {
        setEmpresaId(empresasRes.data[0].id);
      }
    } catch (error) {
      console.error("Error cargando datos:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargarDatos(); }, []);

  const cargarMatriz = async () => {
    if (!empresaId) return;
    try {
      setLoading(true);
      const res = await matrizIperApi.listar({ empresa_id: empresaId });
      setItems(res.data);
    } catch (error) {
      console.error("Error cargando matriz IPER:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { if (empresaId) cargarMatriz(); }, [empresaId]);

  // Filtrado
  const itemsFiltrados = useMemo(() => {
    return items.filter((item) => {
      const busqueda = filtroBusqueda.toLowerCase();
      const matchBusqueda = !busqueda ||
        (item.proceso || "").toLowerCase().includes(busqueda) ||
        (item.descripcion_peligro || "").toLowerCase().includes(busqueda) ||
        (item.riesgo || "").toLowerCase().includes(busqueda) ||
        (item.efectos_posibles || "").toLowerCase().includes(busqueda);

      const matchClasificacion = !filtroClasificacion ||
        item.clasificacion_peligro === filtroClasificacion;

      const nivelRiesgoBackend = item.nivel_riesgo || "";
      const matchRiesgo = !filtroRiesgo || nivelRiesgoBackend === filtroRiesgo;

      return matchBusqueda && matchClasificacion && matchRiesgo;
    });
  }, [items, filtroBusqueda, filtroClasificacion, filtroRiesgo]);

  // Estadísticas - usando valores reales del backend
  const stats = useMemo(() => {
    const porProbabilidad = {};
    items.forEach((i) => {
      const key = i.interpretacion_np || "Sin definir";
      porProbabilidad[key] = (porProbabilidad[key] || 0) + 1;
    });

    const porNivelRiesgo = { "I": 0, "II": 0, "III": 0, "IV": 0 };
    items.forEach((i) => {
      const key = i.nivel_riesgo;
      if (key && porNivelRiesgo.hasOwnProperty(key)) porNivelRiesgo[key]++;
    });

    const porAceptabilidad = {};
    items.forEach((i) => {
      const key = i.aceptabilidad || "Sin definir";
      porAceptabilidad[key] = (porAceptabilidad[key] || 0) + 1;
    });

    return { total: items.length, porProbabilidad, porNivelRiesgo, porAceptabilidad };
  }, [items]);

  // Datos para gráficas - Nivel de Riesgo GTC45
  const chartData = useMemo(() => {
    const riskDistribution = [
      { name: "IV — Aceptable", value: stats.porNivelRiesgo["IV"] || 0, color: "#22c55e" },
      { name: "III — Mejorable", value: stats.porNivelRiesgo["III"] || 0, color: "#f59e0b" },
      { name: "II — Control Específico", value: stats.porNivelRiesgo["II"] || 0, color: "#f97316" },
      { name: "I — No Aceptable", value: stats.porNivelRiesgo["I"] || 0, color: "#ef4444" },
    ].filter((d) => d.value > 0);

    const clasificacionData = CLASIFICACIONES
      .map((c) => ({
        name: CLASIFICACION_LABELS[c],
        value: items.filter((i) => i.clasificacion_peligro === c).length,
      }))
      .filter((d) => d.value > 0);

    return { riskDistribution, clasificacionData };
  }, [items, stats]);

  const handleGuardar = async (datos) => {
    if (!empresaId) { alert("Seleccione una empresa."); return; }
    try {
      setLoading(true);
      const filasConEmpresa = datos.map((d) => ({ ...d, empresa_id: Number(empresaId) }));
      await matrizIperApi.crearLote(filasConEmpresa);
      alert(`${datos.length} peligro(s) guardado(s) correctamente.`);
      setMostrarForm(false);
      await cargarMatriz();
    } catch (error) {
      console.error("Error guardando:", error);
      const detail = error?.response?.data?.detail;
      alert(`Error al guardar.${detail ? `\n\nDetalle: ${detail}` : ""}`);
    } finally { setLoading(false); }
  };

  const handleGuardarAvances = async (datos) => {
    if (!empresaId) { alert("Seleccione una empresa."); return; }
    try {
      setLoading(true);
      const filasConEmpresa = datos.map((d) => ({ ...d, empresa_id: Number(empresaId) }));
      await matrizIperApi.crearLote(filasConEmpresa);
      alert(`${datos.length} peligro(s) guardado(s) como avance.`);
      await cargarMatriz();
    } catch (error) {
      console.error("Error guardando avances:", error);
      const detail = error?.response?.data?.detail;
      alert(`Error al guardar avances.${detail ? `\n\nDetalle: ${detail}` : ""}`);
    } finally { setLoading(false); }
  };

  const handleActualizarFila = async (datos) => {
    if (!empresaId) { alert("Seleccione una empresa."); return; }
    try {
      setLoading(true);
      await matrizIperApi.actualizar(editarFila.id, { ...datos, empresa_id: Number(empresaId) });
      alert("Peligro actualizado correctamente.");
      setEditarFila(null);
      setMostrarForm(false);
      await cargarMatriz();
    } catch (error) {
      console.error("Error actualizando:", error);
      const detail = error?.response?.data?.detail;
      alert(`Error al actualizar.${detail ? `\n\nDetalle: ${detail}` : ""}`);
    } finally { setLoading(false); }
  };

  const eliminar = async (id) => {
    if (!confirm("¿Desea eliminar este peligro de la matriz IPER?")) return;
    try { await matrizIperApi.eliminar(id); await cargarMatriz(); }
    catch (error) { console.error("Error eliminando:", error); }
  };

  const iniciarEdicion = (item) => { setEditarFila(item); setMostrarForm(true); };

  const handleNuevoPeligro = () => {
    if (!empresaId) {
      alert("Primero debe seleccionar una Empresa antes de agregar un nuevo peligro.");
      return;
    }
    setEditarFila(null);
    setMostrarForm(true);
  };

  const exportarExcel = async () => {
    if (!empresaId) { alert("Seleccione una empresa."); return; }
    try {
      setLoading(true);
      const response = await matrizIperApi.exportarExcel(empresaId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `Matriz_IPER_${empresaId}.xlsx`);
      document.body.appendChild(link); link.click(); link.remove();
    } catch (error) { console.error("Error exportando Excel:", error); alert("Error al exportar a Excel."); }
    finally { setLoading(false); }
  };

  const exportarPDF = async () => {
    if (!empresaId) { alert("Seleccione una empresa."); return; }
    try {
      setLoading(true);
      const response = await matrizIperApi.exportarPDF(empresaId);
      const url = window.URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `Matriz_IPER_${empresaId}.pdf`);
      document.body.appendChild(link); link.click(); link.remove();
    } catch (error) { console.error("Error exportando PDF:", error); alert("Error al exportar a PDF."); }
    finally { setLoading(false); }
  };

  const formInitialData = editarFila ? {
    proceso: editarFila.proceso || "", zona_lugar: editarFila.zona_lugar || "",
    actividades: editarFila.actividades || "", tareas: editarFila.tareas || "",
    rutinaria: editarFila.rutinaria || "SI", clasificacion_peligro: editarFila.clasificacion_peligro || "FISICO",
    descripcion_peligro: editarFila.descripcion_peligro || "", riesgo: editarFila.riesgo || "",
    efectos_posibles: editarFila.efectos_posibles || "", fuente: editarFila.fuente || "",
    medio: editarFila.medio || "", individuo: editarFila.individuo || "",
    nd: editarFila.nd || 0, ne: editarFila.ne || 1, nc: editarFila.nc || 10,
    expuestos_hombres: editarFila.expuestos_hombres || 0, expuestos_mujeres: editarFila.expuestos_mujeres || 0,
    expuestos_gestantes: editarFila.expuestos_gestantes || 0, peor_consecuencia: editarFila.peor_consecuencia || "",
    eliminacion: editarFila.eliminacion || "", control_ingenieria: editarFila.control_ingenieria || "",
    sustitucion: editarFila.sustitucion || "", senalizacion_admin: editarFila.senalizacion_admin || "",
    epp: editarFila.epp || "", responsable: editarFila.responsable || "",
    fecha_proyectada: editarFila.fecha_proyectada || "", fecha_ejecucion: editarFila.fecha_ejecucion || "",
    evidencias: editarFila.evidencias || "", realizado: editarFila.realizado || "NO",
  } : null;

  const limpiarFiltros = () => {
    setFiltroBusqueda("");
    setFiltroClasificacion("");
    setFiltroRiesgo("");
  };

  const hayFiltros = filtroBusqueda || filtroClasificacion || filtroRiesgo;

  return (
    <AdminLayout>
      <div className="matriz-legal-page">
        {/* HERO */}
        <section className="ml-hero ml-hero-enterprise">
          <div>
            <h2>
              <Shield size={22} style={{ marginRight: 8, verticalAlign: "middle" }} />
              Matriz IPER — GTC 45
            </h2>
            <p>
              Identificación de Peligros, Evaluación y Valoración de Riesgos según
              Guía Técnica Colombiana GTC 45 (Segunda actualización).
            </p>
          </div>
          <div className="ml-actions iper-actions">
            <div className="iper-select-wrapper">
              <select value={empresaId} onChange={(e) => setEmpresaId(e.target.value)}>
                <option value="">Seleccionar empresa</option>
                {empresas.map((empresa) => (
                  <option key={empresa.id} value={empresa.id}>{empresa.nombre}</option>
                ))}
              </select>
              <ChevronDown size={16} className="iper-select-icon" />
            </div>
            <button type="button" onClick={cargarMatriz} className="iper-btn-hero iper-btn-refresh">
              <RefreshCcw size={16} /> Actualizar
            </button>
            <button type="button" onClick={handleNuevoPeligro} className="iper-btn-hero iper-btn-primary">
              <Plus size={16} /> Nuevo Peligro
            </button>
            {items.length > 0 && (
              <>
                <button type="button" onClick={() => setVerMatriz(true)} className="iper-btn-hero iper-btn-info">
                  <Table2 size={16} /> Ver Matriz
                </button>
                <button type="button" onClick={exportarExcel} className="iper-btn-hero iper-btn-success">
                  <FileSpreadsheet size={16} /> Excel
                </button>
                <button type="button" onClick={exportarPDF} className="iper-btn-hero iper-btn-danger">
                  <FileText size={16} /> PDF
                </button>
              </>
            )}
          </div>
        </section>

        {/* KPIs */}
        {items.length > 0 && (
          <section className="iper-kpis-row">
            <div className="iper-kpi-card iper-kpi-total">
              <div className="iper-kpi-icon"><BarChart3 size={14} /></div>
              <div className="iper-kpi-info">
                <span className="iper-kpi-label">Total peligros</span>
                <span className="iper-kpi-value">{stats.total}</span>
              </div>
            </div>
            {Object.entries(stats.porProbabilidad).map(([key, count]) => (
              <div key={`prob-${key}`} className="iper-kpi-card iper-kpi-medio">
                <div className="iper-kpi-icon"><AlertTriangle size={14} /></div>
                <div className="iper-kpi-info">
                  <span className="iper-kpi-label">{key}</span>
                  <span className="iper-kpi-value">{count}</span>
                </div>
              </div>
            ))}
            {Object.entries(stats.porNivelRiesgo).filter(([, v]) => v > 0).map(([key, count]) => {
              const colors = { "I": "#ef4444", "II": "#f97316", "III": "#f59e0b", "IV": "#22c55e" };
              const labels = { "I": "No Aceptable", "II": "Control Específico", "III": "Mejorable", "IV": "Aceptable" };
              return (
                <div key={`nivel-${key}`} className="iper-kpi-card" style={{ borderLeft: `4px solid ${colors[key]}` }}>
                  <div className="iper-kpi-icon"><TrendingUp size={14} style={{ color: colors[key] }} /></div>
                  <div className="iper-kpi-info">
                    <span className="iper-kpi-label">Nivel {key} — {labels[key]}</span>
                    <span className="iper-kpi-value">{count}</span>
                  </div>
                </div>
              );
            })}
            {Object.entries(stats.porAceptabilidad).filter(([, v]) => v > 0).map(([key, count]) => (
              <div key={`acept-${key}`} className="iper-kpi-card iper-kpi-bajo">
                <div className="iper-kpi-icon"><Shield size={14} /></div>
                <div className="iper-kpi-info">
                  <span className="iper-kpi-label">{key}</span>
                  <span className="iper-kpi-value">{count}</span>
                </div>
              </div>
            ))}
          </section>
        )}

        {/* GRÁFICAS */}
        {items.length > 0 && (
          <section className="iper-charts-row">
            <div className="iper-chart-card">
              <h4><PieChart size={16} /> Mapa de Riesgo</h4>
              <div className="iper-chart-container">
                <ResponsiveContainer width="100%" height={220}>
                  <RePieChart>
                    <Pie
                      data={chartData.riskDistribution}
                      cx="50%" cy="50%" innerRadius={55} outerRadius={85}
                      paddingAngle={3} dataKey="value"
                    >
                      {chartData.riskDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value, name) => [`${value} peligro(s)`, name]} />
                    <Legend />
                  </RePieChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="iper-chart-card">
              <h4><BarChart3 size={16} /> Peligros por Clasificación</h4>
              <div className="iper-chart-container">
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={chartData.clasificacionData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip formatter={(value) => [`${value} peligro(s)`]} />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                      {chartData.clasificacionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={`hsl(${210 + index * 25}, 70%, 55%)`} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </section>
        )}

        {/* FILTROS */}
        {items.length > 0 && (
          <section className="iper-filtros">
            <div className="iper-filtros-search">
              <Search size={16} className="iper-filtros-search-icon" />
              <input
                type="text"
                placeholder="Buscar proceso, actividad, peligro o código..."
                value={filtroBusqueda}
                onChange={(e) => setFiltroBusqueda(e.target.value)}
              />
            </div>
            <select value={filtroClasificacion} onChange={(e) => setFiltroClasificacion(e.target.value)}>
              <option value="">Todas las clasificaciones</option>
              {CLASIFICACIONES.map((c) => (
                <option key={c} value={c}>{CLASIFICACION_LABELS[c]}</option>
              ))}
            </select>
            <select value={filtroRiesgo} onChange={(e) => setFiltroRiesgo(e.target.value)}>
              <option value="">Todos los niveles de riesgo</option>
              <option value="I">Nivel I — No Aceptable</option>
              <option value="II">Nivel II — Control Específico</option>
              <option value="III">Nivel III — Mejorable</option>
              <option value="IV">Nivel IV — Aceptable</option>
            </select>
            {hayFiltros && (
              <button type="button" className="iper-btn-limpiar" onClick={limpiarFiltros}>
                Limpiar filtros
              </button>
            )}
          </section>
        )}

        {/* FORMULARIO */}
        {mostrarForm && (
          <MatrizIPERForm
            onGuardar={editarFila ? handleActualizarFila : handleGuardar}
            onGuardarAvances={handleGuardarAvances}
            initialData={formInitialData}
            editMode={!!editarFila}
          />
        )}

        {/* TABLA */}
        {itemsFiltrados.length > 0 && (
          <section className="ml-list" style={{ marginTop: 24 }}>
            <div className="iper-table-header">
              <h3>
                Registros IPER ({itemsFiltrados.length} de {items.length} peligro{items.length !== 1 ? "s" : ""})
              </h3>
            </div>
            <div className="table-wrap ml-table-wrap">
              <table className="ml-table iper-main-table">
                <thead>
                  <tr>
                    <th style={{ width: 50 }}>#</th>
                    <th>Proceso</th>
                    <th>Peligro</th>
                    <th style={{ minWidth: 200 }}>Descripción</th>
                    <th style={{ textAlign: "center" }}>NP</th>
                    <th style={{ textAlign: "center" }}>Probabilidad</th>
                    <th style={{ textAlign: "center" }}>NR</th>
                    <th style={{ textAlign: "center" }}>Nivel de Riesgo</th>
                    <th>Aceptabilidad</th>
                    <th style={{ width: 120, textAlign: "center" }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {itemsFiltrados.map((item, idx) => {
                    return (
                      <tr key={item.id}>
                        <td style={{ fontWeight: 600, color: "#64748b" }}>{idx + 1}</td>
                        <td style={{ fontWeight: 600, color: "#1e293b", fontSize: "0.85rem" }}>{item.proceso}</td>
                        <td>
                          <span className="ml-pill" style={{ fontSize: "0.7rem" }}>
                            {CLASIFICACION_LABELS[item.clasificacion_peligro] || item.clasificacion_peligro}
                          </span>
                        </td>
                        <td style={{ maxWidth: 250, fontSize: "0.82rem", color: "#475569" }}>{item.descripcion_peligro}</td>
                        <td style={{ textAlign: "center" }}>
                          <strong style={{ fontSize: "0.9rem" }}>{item.np}</strong>
                        </td>
                        <td style={{ textAlign: "center" }}>
                          <span style={{ fontSize: "0.78rem", color: "#64748b" }}>{item.interpretacion_np || "—"}</span>
                        </td>
                        <td style={{ textAlign: "center" }}>
                          <strong style={{ fontSize: "1rem" }}>{item.nr}</strong>
                        </td>
                        <td style={{ textAlign: "center" }}>
                          <span className={`iper-nivel-badge iper-nivel-${(item.interpretacion_nr || "").includes("No Aceptable") ? (item.nr >= 600 ? "critico" : "alto") : (item.nr >= 40 ? "medio" : "bajo")}`}>
                            {item.nivel_riesgo || "—"}
                          </span>
                        </td>
                        <td>
                          <span className={`ml-pill ${item.aceptabilidad === "ACEPTABLE" ? "cumple" : item.aceptabilidad === "NO ACEPTABLE" ? "no_cumple" : "pendiente"}`}>
                            {item.aceptabilidad}
                          </span>
                        </td>
                        <td style={{ textAlign: "center" }}>
                          <div className="iper-row-actions">
                            <button type="button" className="iper-action-btn iper-action-view" onClick={() => setVerDetalle(item)} title="Ver detalle">
                              <Eye size={15} />
                            </button>
                            <button type="button" className="iper-action-btn iper-action-edit" onClick={() => iniciarEdicion(item)} title="Editar">
                              <Edit3 size={15} />
                            </button>
                            <button type="button" className="iper-action-btn iper-action-delete" onClick={() => eliminar(item.id)} title="Eliminar">
                              <Trash2 size={15} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* Sin resultados de filtro */}
        {items.length > 0 && itemsFiltrados.length === 0 && hayFiltros && (
          <section className="iper-empty-filters">
            <Search size={40} />
            <p>No se encontraron resultados con los filtros aplicados.</p>
            <button type="button" className="iper-btn-limpiar" onClick={limpiarFiltros}>Limpiar filtros</button>
          </section>
        )}

        {/* Sin registros */}
        {!mostrarForm && items.length === 0 && !loading && (
          <section className="iper-empty-state">
            <Database size={48} />
            <p>No hay peligros registrados para esta empresa.</p>
            <p>Haga clic en "Nuevo Peligro" para comenzar a identificar peligros.</p>
          </section>
        )}

        {/* MODALES */}
        {verDetalle && <MatrizIPERDetail item={verDetalle} onClose={() => setVerDetalle(null)} />}
        {verMatriz && (
          <MatrizIPERTable
            items={items}
            onClose={() => setVerMatriz(false)}
            onVerDetalle={(item) => { setVerMatriz(false); setVerDetalle(item); }}
          />
        )}
      </div>
    </AdminLayout>
  );
}
