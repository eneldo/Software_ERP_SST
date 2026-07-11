// ============================================================
// PÁGINA: CentroControlDocumentalPage
// Archivo: frontend/src/pages/documental/CentroControlDocumentalPage.jsx
// FASE 1.8.4.3.9.2 - Centro Documental Enterprise Visual PRO
// ------------------------------------------------------------
// Centro operativo para control documental SST: KPIs, gráficos,
// tabla inteligente, versiones, alertas, responsables y vigencias.
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  Download,
  FileText,
  Filter,
  RefreshCcw,
  Search,
  SlidersHorizontal,
} from "lucide-react";

import AdminLayout from "../../layouts/AdminLayout";
import api from "../../api/axios";
import dashboardDocumentalApi from "../../api/dashboardDocumentalApi";

import DocumentalKPIs from "../../components/documental/DocumentalKPIs";
import EstadoDocumentalChart from "../../components/documental/EstadoDocumentalChart";
import CategoriasDocumentalesChart from "../../components/documental/CategoriasDocumentalesChart";
import DocumentalTimelinePro from "../../components/documental/DocumentalTimelinePro";
import DocumentosPorVencer from "../../components/documental/DocumentosPorVencer";
import RevisionPendienteTable from "../../components/documental/RevisionPendienteTable";
import DocumentalAlertas from "../../components/documental/DocumentalAlertas";
import DocumentalComplianceCard from "../../components/documental/DocumentalComplianceCard";
import TablaDocumental from "../../components/documental/TablaDocumental";
import HistorialVersionesModal from "../../components/documental/HistorialVersionesModal";

import "../../styles/documental/centro-control-documental.css";

const normalizarEstados = (items = []) =>
  items.map((item) => ({
    name: item.nombre || "SIN_ESTADO",
    value: Number(item.total || 0),
  }));

const normalizarCategorias = (items = []) =>
  items.slice(0, 8).map((item) => ({
    categoria: item.nombre || "Sin categoría",
    total: Number(item.total || 0),
  }));

function getEmpresaIdUsuario() {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    return user?.empresa_id || "";
  } catch {
    return "";
  }
}

function filtrarPorKpi(documentos, filtroActivo) {
  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);

  return documentos.filter((doc) => {
    const estado = String(doc.estado || "").toUpperCase();
    const revision = String(doc.estado_revision || "").toUpperCase();
    const dias = Number(doc.dias_restantes);

    if (filtroActivo === "vigentes") return estado === "VIGENTE";
    if (filtroActivo === "vencidos") return estado === "VENCIDO" || dias < 0;
    if (filtroActivo === "proximos_vencer") return !Number.isNaN(dias) && dias >= 0 && dias <= 90;
    if (filtroActivo === "pendientes_revision") return ["PENDIENTE", "EN_REVISION"].includes(revision);
    if (filtroActivo === "versiones") return true;
    if (filtroActivo === "cumplimiento") return estado === "VIGENTE" || estado === "APROBADO";
    return true;
  });
}

export default function CentroControlDocumentalPage() {
  const navigate = useNavigate();

  const [empresas, setEmpresas] = useState([]);
  const [empresaId, setEmpresaId] = useState(getEmpresaIdUsuario());
  const [dias, setDias] = useState(30);
  const [filtroActivo, setFiltroActivo] = useState("total");
  const [busqueda, setBusqueda] = useState("");
  const [estadoFiltro, setEstadoFiltro] = useState("");
  const [categoriaFiltro, setCategoriaFiltro] = useState("");

  const [resumen, setResumen] = useState(null);
  const [vencimientos, setVencimientos] = useState([]);
  const [indicadores, setIndicadores] = useState(null);
  const [documentos, setDocumentos] = useState([]);
  const [alertas, setAlertas] = useState(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [documentoSeleccionado, setDocumentoSeleccionado] = useState(null);
  const [versiones, setVersiones] = useState([]);
  const [loadingVersiones, setLoadingVersiones] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const cargarEmpresas = async () => {
    try {
      const res = await api.get("/empresas/");
      setEmpresas(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.warn("No se pudieron cargar empresas", err);
    }
  };

  const cargarDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const params = {};
      if (empresaId) params.empresa_id = empresaId;

      const docsParams = {
        ...params,
        buscar: busqueda || undefined,
        estado: estadoFiltro || undefined,
        categoria: categoriaFiltro || undefined,
        limite: 500,
      };

      const vencimientoParams = { ...params, dias };

      const [resumenRes, indicadoresRes, vencimientosRes, documentosRes, alertasRes] = await Promise.all([
        dashboardDocumentalApi.resumen(params),
        dashboardDocumentalApi.indicadores(params),
        dashboardDocumentalApi.vencimientos(vencimientoParams),
        dashboardDocumentalApi.documentosEnterprise(docsParams),
        dashboardDocumentalApi.alertasEnterprise(vencimientoParams),
      ]);

      setResumen(resumenRes.data || null);
      setIndicadores(indicadoresRes.data || null);
      setVencimientos(Array.isArray(vencimientosRes.data) ? vencimientosRes.data : []);
      setDocumentos(Array.isArray(documentosRes.data) ? documentosRes.data : []);
      setAlertas(alertasRes.data || null);
    } catch (err) {
      console.error(err);
      const detail = err?.response?.data?.detail;
      setError(detail || "No se pudo cargar el Centro Documental Enterprise SST.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarEmpresas();
  }, []);

  useEffect(() => {
    cargarDashboard();
  }, [empresaId, dias, estadoFiltro, categoriaFiltro]);

  const kpis = resumen?.kpis || indicadores || {};

  const estadoData = useMemo(() => normalizarEstados(resumen?.estados || []), [resumen]);
  const categoriaData = useMemo(() => normalizarCategorias(resumen?.categorias || []), [resumen]);
  const responsables = resumen?.responsables || [];

  const categoriasDisponibles = useMemo(() => {
    const set = new Set(documentos.map((doc) => doc.categoria).filter(Boolean));
    return Array.from(set).sort();
  }, [documentos]);

  const documentosFiltrados = useMemo(() => {
    const q = busqueda.trim().toLowerCase();
    let docs = filtrarPorKpi(documentos, filtroActivo);

    if (q) {
      docs = docs.filter((doc) =>
        [
          doc.codigo_documental,
          doc.titulo,
          doc.categoria,
          doc.responsable,
          doc.estado,
          doc.estado_revision,
          doc.version,
        ]
          .join(" ")
          .toLowerCase()
          .includes(q)
      );
    }

    return docs;
  }, [busqueda, documentos, filtroActivo]);

  const vencimientosFiltrados = useMemo(() => {
    if (!busqueda.trim()) return vencimientos;
    const q = busqueda.toLowerCase();
    return vencimientos.filter((doc) =>
      [doc.codigo_documental, doc.titulo, doc.categoria, doc.responsable]
        .join(" ")
        .toLowerCase()
        .includes(q)
    );
  }, [busqueda, vencimientos]);

  const nombreEmpresa = empresaId
    ? empresas.find((empresa) => String(empresa.id) === String(empresaId))?.nombre || `Empresa ID ${empresaId}`
    : "Todas las empresas";

  const abrirHistorial = async (doc) => {
    try {
      setDocumentoSeleccionado(doc);
      setModalOpen(true);
      setLoadingVersiones(true);
      const res = await dashboardDocumentalApi.historialEnterprise(doc.id);
      setVersiones(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error(err);
      setVersiones([]);
    } finally {
      setLoadingVersiones(false);
    }
  };

  const exportarCSV = () => {
    const rows = [
      ["codigo", "titulo", "categoria", "version", "estado", "revision", "responsable", "fecha_vencimiento", "dias_restantes"],
      ...documentosFiltrados.map((doc) => [
        doc.codigo_documental || "",
        doc.titulo || "",
        doc.categoria || "",
        doc.version || "",
        doc.estado || "",
        doc.estado_revision || "",
        doc.responsable || "",
        doc.fecha_vencimiento || "",
        doc.dias_restantes ?? "",
      ]),
    ];

    const csv = rows
      .map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "centro_documental_enterprise_sst.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <AdminLayout>
      <div className="ccd-page">
        <section className="ccd-hero">
          <div className="ccd-hero-copy">
            <span className="ccd-badge">CENTRO DOCUMENTAL VISUAL PRO</span>
            <h2>Centro Documental Enterprise SST</h2>
            <p>
              Centro operativo para controlar documentos vigentes, vencidos,
              próximos a vencer, revisiones, versiones, aprobadores,
              responsables y cumplimiento documental del SG-SST.
            </p>
            <div className="ccd-hero-meta">
              <span>Empresa: <strong>{nombreEmpresa}</strong></span>
              <span>Rango vencimientos: <strong>{dias} días</strong></span>
              <span>Documentos visibles: <strong>{documentosFiltrados.length}</strong></span>
            </div>
          </div>

          <div className="ccd-actions">
            <select value={empresaId} onChange={(e) => setEmpresaId(e.target.value)}>
              <option value="">Todas las empresas</option>
              {empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>{empresa.nombre}</option>
              ))}
            </select>

            <select value={dias} onChange={(e) => setDias(Number(e.target.value))}>
              <option value={15}>15 días</option>
              <option value={30}>30 días</option>
              <option value={60}>60 días</option>
              <option value={90}>90 días</option>
              <option value={365}>365 días</option>
            </select>

            <button onClick={cargarDashboard} disabled={loading}>
              <RefreshCcw size={18} className={loading ? "spin" : ""} />
              Actualizar
            </button>

            <button className="secondary" onClick={() => navigate("/documental/biblioteca")}>
              <FileText size={18} /> Biblioteca
            </button>
          </div>
        </section>

        {error && (
          <section className="ccd-error">
            <AlertTriangle size={20} />
            <span>{error}</span>
          </section>
        )}

        <DocumentalKPIs kpis={kpis} filtroActivo={filtroActivo} onFilter={setFiltroActivo} />

        <section className="ccd-toolbar enterprise">
          <div className="ccd-toolbar-left">
            <SlidersHorizontal size={18} />
            <span>Filtro KPI:</span>
            <strong>{filtroActivo.replaceAll("_", " ").toUpperCase()}</strong>
          </div>

          <div className="ccd-search-box">
            <Search size={17} />
            <input
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && cargarDashboard()}
              placeholder="Buscar código, título, responsable, estado o versión..."
            />
          </div>

          <div className="ccd-filter-group">
            <Filter size={16} />
            <select value={estadoFiltro} onChange={(e) => setEstadoFiltro(e.target.value)}>
              <option value="">Todos los estados</option>
              <option value="VIGENTE">Vigente</option>
              <option value="BORRADOR">Borrador</option>
              <option value="OBSOLETO">Obsoleto</option>
              <option value="VENCIDO">Vencido</option>
            </select>
            <select value={categoriaFiltro} onChange={(e) => setCategoriaFiltro(e.target.value)}>
              <option value="">Todas las categorías</option>
              {categoriasDisponibles.map((categoria) => (
                <option key={categoria} value={categoria}>{categoria}</option>
              ))}
            </select>
          </div>

          <button className="ccd-export-btn" onClick={exportarCSV}>
            <Download size={17} /> Exportar CSV
          </button>
        </section>

        <section className="ccd-main-grid">
          <EstadoDocumentalChart data={estadoData} />
          <CategoriasDocumentalesChart data={categoriaData} />
        </section>

        <section className="ccd-executive-grid">
          <DocumentalTimelinePro kpis={kpis} />
          <DocumentalAlertas kpis={kpis} alertas={alertas || {}} />
        </section>

        <section className="ccd-main-grid wide-left">
          <DocumentosPorVencer documentos={vencimientosFiltrados} />
          <DocumentalComplianceCard value={kpis.cumplimiento_documental} />
        </section>

        <TablaDocumental
          documentos={documentosFiltrados}
          onHistorial={abrirHistorial}
          onVer={(doc) => doc.archivo_url ? window.open(doc.archivo_url, "_blank") : abrirHistorial(doc)}
          onEditar={(doc) => navigate(`/documental/biblioteca?documento=${doc.id}`)}
        />

        <RevisionPendienteTable responsables={responsables} />

        <HistorialVersionesModal
          open={modalOpen}
          documento={documentoSeleccionado}
          versiones={versiones}
          loading={loadingVersiones}
          onClose={() => setModalOpen(false)}
        />
      </div>
    </AdminLayout>
  );
}
