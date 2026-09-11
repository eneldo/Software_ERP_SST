// ============================================================
// EPP SST ENTERPRISE - ERP SST PRO
// FASE 1.1.7.3 — ANALYTICS Y ALERTAS EPP
// Archivo: frontend/src/pages/hacer/EPPPage.jsx
// ============================================================

import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BriefcaseMedical,
  CalendarDays,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
  Edit3,
  Eye,
  Filter,
  FileText,
  Download,
  Image as ImageIcon,
  LayoutDashboard,
  UploadCloud,
  PenLine,
  Save,
  Eraser,
  HardHat,
  PackageCheck,
  Plus,
  RefreshCcw,
  Search,
  ShieldCheck,
  Sidebar,
  Trash2,
  UserCheck,
  X,
  Paperclip,
} from "lucide-react";

import {
  actualizarCatalogoEPP,
  actualizarEntregaEPP,
  crearCatalogoEPP,
  crearEntregaEPP,
  crearEntregaLoteEPP,
  consolidadoEntregasEPP,
  dashboardEPP,
  eliminarCatalogoEPP,
  eliminarEntregaEPP,
  listarCatalogoEPP,
  listarEntregasEPP,
  marcarRecibidoEPP,
  listarEvidenciasEPP,
  subirEvidenciaEPP,
  eliminarEvidenciaEPP,
  firmarEntregaEPP,
  subirFichaTecnicaEPP,
  eliminarFichaTecnicaEPP,
  exportarCatalogoEPPExcel,
  exportarEntregasEPPExcel,
  exportarEntregasEPPPDF,
  exportarFichaEntregaEPPPDF,
  exportarReposicionesEPPExcel,
  exportarReposicionesEPPPDF,
  exportarPendientesFirmaEPPExcel,
  exportarPendientesFirmaEPPPDF,
} from "../../api/eppApi";
import { listarEmpresasSST } from "../../api/empresaSstApi";
import { listarSedesSST } from "../../api/sedeSstApi";
import { listarAreasSST } from "../../api/areaSstApi";
import { listarCargosSST } from "../../api/cargoSstApi";
import { listarEmpleados } from "../../api/empleadoSstApi";
import { toastSuccess, toastError, toastWarning } from "../../utils/toast";
import "../../styles/epp-sst.css";

const hoyISO = () => new Date().toISOString().slice(0, 10);
const sumarDiasISO = (fecha, dias = 365) => {
  const base = fecha ? new Date(`${fecha}T00:00:00`) : new Date();
  base.setDate(base.getDate() + Number(dias || 0));
  return base.toISOString().slice(0, 10);
};

const entregaInicial = {
  empresa_id: "",
  empleado_id: "",
  epp_id: "",
  cantidad: 1,
  fecha_entrega: hoyISO(),
  fecha_reposicion: "",
  talla: "",
  marca: "",
  modelo: "",
  serial: "",
  estado: "ENTREGADO",
  recibido_por_empleado: false,
  observaciones: "",
  activo: true,
};

const catalogoInicial = {
  empresa_id: "",
  codigo: "",
  nombre: "",
  categoria: "",
  descripcion: "",
  vida_util_dias: 365,
  requiere_reposicion: true,
  requiere_firma: true,
  requiere_evidencia: false,
  estado: "ACTIVO",
  activo: true,
};

const estadoLabel = (estado) =>
  ({
    ENTREGADO: "Entregado",
    VIGENTE: "Vigente",
    PROXIMO_REPOSICION: "Próx. reposición",
    VENCIDO: "Vencido",
    REEMPLAZADO: "Reemplazado",
    DEVUELTO: "Devuelto",
    ANULADO: "Anulado",
  }[estado] || estado || "Sin estado");

const moneyDate = (value) => (value ? String(value).slice(0, 10) : "Sin fecha");
const toInt = (value) => (value === "" || value === null || value === undefined ? null : Number(value));
const bytesToSize = (bytes = 0) => {
  const n = Number(bytes || 0);
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(2)} MB`;
};
const evidenciaLabel = (tipo) => ({
  ACTA_ENTREGA: "Acta entrega",
  FIRMA_EMPLEADO: "Firma empleado",
  FOTO_ENTREGA: "Foto entrega",
  EPP_RECIBIDO: "EPP recibido",
  SOPORTE: "Soporte",
}[tipo] || tipo || "Soporte");

function BarList({ title, icon: Icon, data = [], empty = "Sin información registrada." }) {
  const max = Math.max(...data.map((x) => Number(x.value || 0)), 1);
  return (
    <article className="epp-chart-card">
      <h3>{Icon && <Icon size={16} />} {title}</h3>
      <div className="epp-bar-list">
        {data.length === 0 ? (
          <small>{empty}</small>
        ) : (
          data.map((item, idx) => (
            <div className="epp-bar-row" key={`${item.name}-${idx}`}>
              <div className="epp-bar-meta">
                <span>{item.name}</span>
                <b>{item.value}</b>
              </div>
              <div className="epp-bar-track">
                <i style={{ width: `${Math.max((Number(item.value || 0) / max) * 100, 6)}%` }} />
              </div>
            </div>
          ))
        )}
      </div>
    </article>
  );
}


function SignaturePad({ value, onChange }) {
  const canvasRef = React.useRef(null);
  const drawing = React.useRef(false);

  const getPoint = (event) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const source = event.touches?.[0] || event;
    return { x: source.clientX - rect.left, y: source.clientY - rect.top };
  };

  const start = (event) => {
    event.preventDefault();
    drawing.current = true;
    const ctx = canvasRef.current.getContext("2d");
    const p = getPoint(event);
    ctx.beginPath();
    ctx.moveTo(p.x, p.y);
  };

  const move = (event) => {
    if (!drawing.current) return;
    event.preventDefault();
    const ctx = canvasRef.current.getContext("2d");
    const p = getPoint(event);
    ctx.lineTo(p.x, p.y);
    ctx.strokeStyle = "#0f172a";
    ctx.lineWidth = 2.5;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.stroke();
    onChange(canvasRef.current.toDataURL("image/png"));
  };

  const end = () => {
    drawing.current = false;
    if (canvasRef.current) onChange(canvasRef.current.toDataURL("image/png"));
  };

  const clear = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    onChange("");
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }, []);

  return (
    <div className="epp-signature-box">
      <canvas
        ref={canvasRef}
        width={620}
        height={190}
        onMouseDown={start}
        onMouseMove={move}
        onMouseUp={end}
        onMouseLeave={end}
        onTouchStart={start}
        onTouchMove={move}
        onTouchEnd={end}
      />
      {!value && <span>Firma del trabajador aquí</span>}
      <button type="button" className="epp-btn-light" onClick={clear}><Eraser size={15} /> Limpiar firma</button>
    </div>
  );
}

export default function EPPPage() {
  const [entregas, setEntregas] = useState([]);
  const [catalogo, setCatalogo] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [areas, setAreas] = useState([]);
  const [cargos, setCargos] = useState([]);
  const [empleados, setEmpleados] = useState([]);
  const [dashboard, setDashboard] = useState({ kpis: {}, charts: {}, alertas: {}, recomendaciones: [] });

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [modoModal, setModoModal] = useState(null); // entrega | catalogo | detalle
  const [tab, setTab] = useState("entregas");
  const [editando, setEditando] = useState(null);
  const [formEntrega, setFormEntrega] = useState(entregaInicial);
  const [formCatalogo, setFormCatalogo] = useState(catalogoInicial);
  const [detalle, setDetalle] = useState(null);
  const [evidenciaEntrega, setEvidenciaEntrega] = useState(null);
  const [evidencias, setEvidencias] = useState([]);
  const [preview, setPreview] = useState(null);
  const [formEvidencia, setFormEvidencia] = useState({ tipo_evidencia: "ACTA_ENTREGA", descripcion: "Acta de entrega EPP", archivo: null });
  const [firmaData, setFirmaData] = useState("");
  const [firmando, setFirmando] = useState(false);
  const [fichaTecnicaFile, setFichaTecnicaFile] = useState(null);
  const [fichaTecnicaPreview, setFichaTecnicaPreview] = useState(null);
  const [fichaTecnicaModal, setFichaTecnicaModal] = useState(null);
  const [modoEntrega, setModoEntrega] = useState("individual"); // individual | lote
  const [itemsLote, setItemsLote] = useState([]);
  const [consolidado, setConsolidado] = useState([]);
  const [subTab, setSubTab] = useState("tabla"); // tabla | consolidado
  const [empleadoConsolidado, setEmpleadoConsolidado] = useState(null);

  const [filtros, setFiltros] = useState({
    q: "",
    empresa_id: "",
    sede_id: "",
    area_id: "",
    cargo_id: "",
    empleado_id: "",
    epp_id: "",
    estado: "",
  });
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const gestionEppRef = useRef(null);

  const abrirGestionEpp = () => {
    setTab("catalogo");
    gestionEppRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const [emp, sed, ar, car, empl, cat, ent, dash] = await Promise.all([
        listarEmpresasSST(),
        listarSedesSST(),
        listarAreasSST(),
        listarCargosSST(),
        listarEmpleados(),
        listarCatalogoEPP(),
        listarEntregasEPP(filtros),
        dashboardEPP(filtros),
      ]);
      setEmpresas(Array.isArray(emp) ? emp : []);
      setSedes(Array.isArray(sed) ? sed : []);
      setAreas(Array.isArray(ar) ? ar : []);
      setCargos(Array.isArray(car) ? car : []);
      setEmpleados(Array.isArray(empl) ? empl : []);
      setCatalogo(Array.isArray(cat) ? cat : []);
      setEntregas(Array.isArray(ent) ? ent : []);
      setDashboard(dash || { kpis: {}, charts: {}, alertas: {}, recomendaciones: [] });
    } catch (error) {
      console.error(error);
      toastError("Error", "No fue posible cargar EPP SST. Revisa backend y permisos.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  useEffect(() => {
    setPage(1);
    const timer = setTimeout(() => cargarDatos(), 250);
    return () => clearTimeout(timer);
  }, [filtros.empresa_id, filtros.sede_id, filtros.area_id, filtros.cargo_id, filtros.empleado_id, filtros.epp_id, filtros.estado]);

  const empleadosFiltrados = useMemo(() => {
    return empleados.filter((e) => {
      if (formEntrega.empresa_id && Number(e.empresa_id) !== Number(formEntrega.empresa_id)) return false;
      return true;
    });
  }, [empleados, formEntrega.empresa_id]);

  const catalogoFiltrado = useMemo(() => {
    return catalogo.filter((epp) => {
      if (formEntrega.empresa_id && Number(epp.empresa_id) !== Number(formEntrega.empresa_id)) return false;
      return epp.activo !== false;
    });
  }, [catalogo, formEntrega.empresa_id]);

  const totalPages = Math.max(Math.ceil(entregas.length / pageSize), 1);
  const entregasPagina = entregas.slice((page - 1) * pageSize, page * pageSize);

  const abrirEntrega = (item = null) => {
    setEditando(item);
    setFormEntrega(
      item
        ? {
            empresa_id: item.empresa_id || "",
            empleado_id: item.empleado_id || "",
            epp_id: item.epp_id || "",
            cantidad: item.cantidad || 1,
            fecha_entrega: item.fecha_entrega || hoyISO(),
            fecha_reposicion: item.fecha_reposicion || "",
            talla: item.talla || "",
            marca: item.marca || "",
            modelo: item.modelo || "",
            serial: item.serial || "",
            estado: item.estado || "ENTREGADO",
            recibido_por_empleado: Boolean(item.recibido_por_empleado),
            observaciones: item.observaciones || "",
            activo: item.activo !== false,
          }
        : entregaInicial
    );
    setModoModal("entrega");
  };

  const abrirEntregaLote = () => {
    setEditando(null);
    setFormEntrega({
      empresa_id: "",
      empleado_id: "",
      epp_id: "",
      cantidad: 1,
      fecha_entrega: hoyISO(),
      fecha_reposicion: "",
      talla: "",
      marca: "",
      modelo: "",
      serial: "",
      estado: "ENTREGADO",
      recibido_por_empleado: false,
      observaciones: "",
      activo: true,
    });
    setItemsLote([]);
    setModoEntrega("lote");
    setModoModal("entrega");
  };

  const agregarItemLote = () => {
    setItemsLote((prev) => [
      ...prev,
      { epp_id: "", cantidad: 1, talla: "", marca: "", modelo: "", serial: "", observaciones: "" },
    ]);
  };

  const actualizarItemLote = (index, campo, valor) => {
    setItemsLote((prev) => {
      const copia = [...prev];
      copia[index] = { ...copia[index], [campo]: valor };
      return copia;
    });
  };

  const eliminarItemLote = (index) => {
    setItemsLote((prev) => prev.filter((_, i) => i !== index));
  };

  const cargarConsolidado = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filtros.empresa_id) params.empresa_id = filtros.empresa_id;
      const data = await consolidadoEntregasEPP(params);
      setConsolidado(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error(error);
      toastError("Error", "No fue posible cargar el consolidado.");
    } finally {
      setLoading(false);
    }
  };

  const abrirCatalogo = (item = null) => {
    setEditando(item);
    setFormCatalogo(
      item
        ? {
            empresa_id: item.empresa_id || "",
            codigo: item.codigo || "",
            nombre: item.nombre || "",
            categoria: item.categoria || "",
            descripcion: item.descripcion || "",
            vida_util_dias: item.vida_util_dias || 365,
            requiere_reposicion: item.requiere_reposicion !== false,
            requiere_firma: item.requiere_firma !== false,
            requiere_evidencia: Boolean(item.requiere_evidencia),
            estado: item.estado || "ACTIVO",
            activo: item.activo !== false,
          }
        : catalogoInicial
    );
    setModoModal("catalogo");
  };

  const cerrarModal = () => {
    setModoModal(null);
    setEditando(null);
    setDetalle(null);
    setEvidenciaEntrega(null);
    setEvidencias([]);
    setPreview(null);
    setFichaTecnicaFile(null);
    setFichaTecnicaPreview(null);
    setModoEntrega("individual");
    setItemsLote([]);
  };

  const subirFichaTecnica = async (catalogoId) => {
    if (!fichaTecnicaFile) {
      toastWarning("Advertencia", "Seleccione un archivo PDF para la ficha técnica.");
      return;
    }
    try {
      setSaving(true);
      const fd = new FormData();
      fd.append("archivo", fichaTecnicaFile);
      await subirFichaTecnicaEPP(catalogoId, fd);
      setFichaTecnicaFile(null);
      await cargarDatos();
      toastSuccess("Éxito", "Ficha técnica cargada correctamente.");
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No fue posible cargar la ficha técnica.");
    } finally {
      setSaving(false);
    }
  };

  const eliminarFichaTecnica = async (catalogoId) => {
    if (!confirm("¿Desea eliminar la ficha técnica de este EPP?")) return;
    try {
      setSaving(true);
      await eliminarFichaTecnicaEPP(catalogoId);
      await cargarDatos();
      toastSuccess("Éxito", "Ficha técnica eliminada.");
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No fue posible eliminar la ficha técnica.");
    } finally {
      setSaving(false);
    }
  };

  const abrirFichaTecnica = (item) => {
    setFichaTecnicaModal(item);
  };


  const filtrosExportacion = () => ({
    q: filtros.q,
    empresa_id: filtros.empresa_id,
    sede_id: filtros.sede_id,
    area_id: filtros.area_id,
    cargo_id: filtros.cargo_id,
    empleado_id: filtros.empleado_id,
    epp_id: filtros.epp_id,
    estado: filtros.estado,
  });

  const manejarExportacion = async (tipo) => {
    try {
      setSaving(true);
      const params = filtrosExportacion();
      if (tipo === "catalogo_excel") await exportarCatalogoEPPExcel(params);
      if (tipo === "entregas_excel") await exportarEntregasEPPExcel(params);
      if (tipo === "entregas_pdf") await exportarEntregasEPPPDF(params);
      if (tipo === "reposiciones_excel") await exportarReposicionesEPPExcel(30);
      if (tipo === "reposiciones_pdf") await exportarReposicionesEPPPDF(30);
      if (tipo === "firmas_excel") await exportarPendientesFirmaEPPExcel();
      if (tipo === "firmas_pdf") await exportarPendientesFirmaEPPPDF();
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No fue posible generar la exportación EPP.");
    } finally {
      setSaving(false);
    }
  };

  const exportarFichaEntrega = async (item) => {
    try {
      setSaving(true);
      await exportarFichaEntregaEPPPDF(item.id);
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No fue posible generar la ficha PDF de la entrega.");
    } finally {
      setSaving(false);
    }
  };


  const guardarEntrega = async (event) => {
    event.preventDefault();
    try {
      setSaving(true);

      if (modoEntrega === "lote") {
        if (!formEntrega.empresa_id || !formEntrega.empleado_id || !formEntrega.fecha_entrega) {
          toastWarning("Advertencia", "Empresa, empleado y fecha de entrega son obligatorios.");
          return;
        }
        if (itemsLote.length === 0) {
          toastWarning("Advertencia", "Agregue al menos un EPP a la entrega.");
          return;
        }
        const itemsInvalidos = itemsLote.filter((it) => !it.epp_id);
        if (itemsInvalidos.length > 0) {
          toastWarning("Advertencia", "Todos los elementos deben tener un EPP seleccionado.");
          return;
        }
        const payloadLote = {
          empresa_id: toInt(formEntrega.empresa_id),
          empleado_id: toInt(formEntrega.empleado_id),
          fecha_entrega: formEntrega.fecha_entrega,
          items: itemsLote.map((it) => ({
            epp_id: toInt(it.epp_id),
            cantidad: Number(it.cantidad || 1),
            talla: it.talla || null,
            marca: it.marca || null,
            modelo: it.modelo || null,
            serial: it.serial || null,
            observaciones: it.observaciones || null,
          })),
        };
        const resultado = await crearEntregaLoteEPP(payloadLote);
        toastSuccess("Éxito", `Se entregaron ${resultado.entregas_creadas} elementos EPP a ${resultado.empleado_nombre}.`);
      } else {
        const payload = {
          ...formEntrega,
          empresa_id: toInt(formEntrega.empresa_id),
          empleado_id: toInt(formEntrega.empleado_id),
          epp_id: toInt(formEntrega.epp_id),
          cantidad: Number(formEntrega.cantidad || 1),
          fecha_reposicion: formEntrega.fecha_reposicion || null,
          talla: formEntrega.talla || null,
          marca: formEntrega.marca || null,
          modelo: formEntrega.modelo || null,
          serial: formEntrega.serial || null,
        };
        if (!payload.empresa_id || !payload.empleado_id || !payload.epp_id || !payload.fecha_entrega) {
          toastWarning("Advertencia", "Empresa, empleado, EPP y fecha de entrega son obligatorios.");
          return;
        }
        if (editando?.id) await actualizarEntregaEPP(editando.id, payload);
        else await crearEntregaEPP(payload);
      }

      await cargarDatos();
      cerrarModal();
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No fue posible guardar la entrega EPP.");
    } finally {
      setSaving(false);
    }
  };

  const guardarCatalogo = async (event) => {
    event.preventDefault();
    try {
      setSaving(true);
      const payload = {
        ...formCatalogo,
        empresa_id: toInt(formCatalogo.empresa_id),
        vida_util_dias: Number(formCatalogo.vida_util_dias || 0),
      };
      if (!payload.empresa_id || !payload.codigo || !payload.nombre) {
        toastWarning("Advertencia", "Empresa, código y nombre son obligatorios.");
        return;
      }
      let resultado;
      if (editando?.id) {
        resultado = await actualizarCatalogoEPP(editando.id, payload);
      } else {
        resultado = await crearCatalogoEPP(payload);
      }

      if (fichaTecnicaFile && resultado?.id) {
        const fd = new FormData();
        fd.append("archivo", fichaTecnicaFile);
        await subirFichaTecnicaEPP(resultado.id, fd);
      }

      await cargarDatos();
      cerrarModal();
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No fue posible guardar el EPP del catálogo.");
    } finally {
      setSaving(false);
    }
  };

  const abrirEvidencias = async (item) => {
    try {
      setEvidenciaEntrega(item);
      setModoModal("evidencias");
      setPreview(null);
      setFormEvidencia({ tipo_evidencia: "ACTA_ENTREGA", descripcion: "Acta de entrega EPP", archivo: null });
      setFirmaData("");
      const data = await listarEvidenciasEPP(item.id);
      setEvidencias(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error(error);
      toastError("Error", "No fue posible cargar evidencias EPP.");
    }
  };

  const refrescarEvidencias = async () => {
    if (!evidenciaEntrega?.id) return;
    const data = await listarEvidenciasEPP(evidenciaEntrega.id);
    setEvidencias(Array.isArray(data) ? data : []);
  };

  const subirEvidencia = async (event) => {
    event.preventDefault();
    if (!evidenciaEntrega?.id || !formEvidencia.archivo) {
      toastWarning("Advertencia", "Selecciona un archivo PDF o imagen.");
      return;
    }
    try {
      setSaving(true);
      const fd = new FormData();
      fd.append("tipo_evidencia", formEvidencia.tipo_evidencia);
      fd.append("descripcion", formEvidencia.descripcion || evidenciaLabel(formEvidencia.tipo_evidencia));
      fd.append("archivo", formEvidencia.archivo);
      await subirEvidenciaEPP(evidenciaEntrega.id, fd);
      setFormEvidencia({ tipo_evidencia: "ACTA_ENTREGA", descripcion: "Acta de entrega EPP", archivo: null });
      await refrescarEvidencias();
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No fue posible subir la evidencia.");
    } finally {
      setSaving(false);
    }
  };

  const eliminarEvidencia = async (archivo) => {
    if (!window.confirm(`¿Eliminar evidencia ${archivo.nombre_original}?`)) return;
    await eliminarEvidenciaEPP(evidenciaEntrega.id, archivo.id);
    await refrescarEvidencias();
  };

  const firmarEntrega = async () => {
    if (!firmaData) {
      toastWarning("Advertencia", "Primero dibuja la firma del empleado.");
      return;
    }
    try {
      setFirmando(true);
      await firmarEntregaEPP(evidenciaEntrega.id, {
        firma_base64: firmaData,
        nombre_firmante: evidenciaEntrega.empleado_nombre,
        descripcion: `Firma recibido EPP - ${evidenciaEntrega.empleado_nombre || "Empleado"}`,
      });
      await refrescarEvidencias();
      await cargarDatos();
      setFirmaData("");
    } catch (error) {
      console.error(error);
      toastError("Error", error?.response?.data?.detail || "No fue posible guardar la firma.");
    } finally {
      setFirmando(false);
    }
  };

  const eliminarEntrega = async (item) => {
    if (!window.confirm(`¿Anular entrega de ${item.epp_nombre || "EPP"}?`)) return;
    await eliminarEntregaEPP(item.id);
    await cargarDatos();
  };

  const eliminarCatalogo = async (item) => {
    if (!window.confirm(`¿Desactivar ${item.nombre}?`)) return;
    await eliminarCatalogoEPP(item.id);
    await cargarDatos();
  };

  const marcarRecibido = async (item) => {
    await marcarRecibidoEPP(item.id, !item.recibido_por_empleado);
    await cargarDatos();
  };

  const onChangeEntrega = (key, value) => {
    const next = { ...formEntrega, [key]: value };
    if (key === "empresa_id") {
      next.empleado_id = "";
      next.epp_id = "";
    }
    if (key === "epp_id") {
      const selected = catalogo.find((x) => Number(x.id) === Number(value));
      if (selected?.vida_util_dias && next.fecha_entrega) {
        next.fecha_reposicion = sumarDiasISO(next.fecha_entrega, selected.vida_util_dias);
      }
    }
    if (key === "fecha_entrega" && next.epp_id) {
      const selected = catalogo.find((x) => Number(x.id) === Number(next.epp_id));
      if (selected?.vida_util_dias) next.fecha_reposicion = sumarDiasISO(value, selected.vida_util_dias);
    }
    setFormEntrega(next);
  };

  const kpis = dashboard?.kpis || {};
  const charts = dashboard?.charts || {};
  const alertas = dashboard?.alertas || {};
  const eppCriticas = Number(alertas.vencen_7_dias || 0) + Number(alertas.vencidos || 0) + Number(alertas.sin_firma || 0) + Number(alertas.sin_evidencia || 0) + Number(alertas.empleados_sin_epp || 0);
  const coberturaEpp = Number(kpis.cobertura || 0);
  const cumplimientoIntegral = Number(kpis.cumplimiento_integral ?? kpis.cumplimiento_firma ?? 0);
  const estadoInteligente = eppCriticas > 0 || (kpis.riesgo_epp && kpis.riesgo_epp !== "BAJO");
  const distribucionBase = [
    { label: "Cobertura", value: `${kpis.cobertura || 0}%`, pct: Math.round(Number(kpis.cobertura || 0)), tone: "blue", icon: UserCheck },
    { label: "Vigentes", value: kpis.vigentes || 0, pct: kpis.total_entregas ? Math.round(((kpis.vigentes || 0) / kpis.total_entregas) * 100) : 0, tone: "green", icon: ShieldCheck },
    { label: "Firmados", value: kpis.firmados || 0, pct: kpis.total_entregas ? Math.round(((kpis.firmados || 0) / kpis.total_entregas) * 100) : 0, tone: "purple", icon: ClipboardCheck },
    { label: "Evidencias", value: kpis.entregas_con_evidencia || 0, pct: Math.round(Number(kpis.cumplimiento_evidencia || 0)), tone: "orange", icon: Paperclip },
    { label: "Vencidos", value: kpis.vencidos || 0, pct: kpis.total_entregas ? Math.round(((kpis.vencidos || 0) / kpis.total_entregas) * 100) : 0, tone: "red", icon: AlertTriangle },
  ];
  const recomendacionesPRO = (dashboard.recomendaciones || []).length
    ? dashboard.recomendaciones
    : [
        "Asignar EPP a empleados sin entregas registradas.",
        "Validar firma de recibido para trazabilidad legal.",
        "Adjuntar evidencia documental a las entregas pendientes.",
        "Programar reposiciones antes de la fecha de vencimiento.",
      ];

  return (
    <main className="epp-sst-page">
      <section className="epp-hero">
        <div>
          <h1>Elementos de Protección Personal</h1>
          <p>Controla entregas, reposiciones, firmas y evidencias de EPP.</p>
        </div>
        <div className="epp-hero-actions epp-hero-actions-export">
          <button className="epp-btn-light" title="Exportar Excel" onClick={() => manejarExportacion(tab === "catalogo" ? "catalogo_excel" : "entregas_excel")} disabled={saving}>
            <Download size={16} /> Excel
          </button>
          <button className="epp-btn-light" title="Exportar PDF" onClick={() => manejarExportacion("entregas_pdf")} disabled={saving}>
            <FileText size={16} /> PDF
          </button>
          <button className="epp-btn-light" title="Reporte de reposiciones" onClick={() => manejarExportacion("reposiciones_pdf")} disabled={saving}>
            <CalendarDays size={16} /> Reposiciones
          </button>
          <button className="epp-btn-light" title="Reporte de firmas" onClick={() => manejarExportacion("firmas_pdf")} disabled={saving}>
            <PenLine size={16} /> Firmas
          </button>
          <button className="epp-btn-light" title="Actualizar datos" onClick={cargarDatos} disabled={loading || saving}>
            <RefreshCcw size={16} /> Actualizar
          </button>
          <button className="epp-btn-light" title="Ver y gestionar EPP" onClick={abrirGestionEpp}>
            <HardHat size={16} /> EPP
          </button>
          <button className="epp-btn-light" title="Registrar nuevo EPP" onClick={() => abrirCatalogo()}>
            <PackageCheck size={16} /> Nuevo EPP
          </button>
          <button className="epp-btn-primary" title="Registrar nueva entrega" onClick={() => abrirEntrega()}>
            <Plus size={16} /> Nueva entrega
          </button>
          <button className="epp-btn-primary" title="Entrega múltiple a un empleado" onClick={abrirEntregaLote} style={{ background: "linear-gradient(135deg, #7c3aed, #2563eb)" }}>
            <PackageCheck size={16} /> Entrega múltiple
          </button>
        </div>
      </section>

      <section className={`epp-main-grid ${!sidebarVisible ? "epp-panel-collapsed" : ""}`}>
        <div className="epp-content">
          <section className="epp-kpis-grid">
            <article className="epp-kpi-card"><div className="epp-kpi-icon"><ClipboardCheck size={19} /></div><div><small>Total entregas</small><strong>{kpis.total_entregas || 0}</strong></div></article>
            <article className="epp-kpi-card epp-tone-green"><div className="epp-kpi-icon"><CheckCircle2 size={19} /></div><div><small>Vigentes</small><strong>{kpis.vigentes || 0}</strong></div></article>
            <article className="epp-kpi-card epp-tone-yellow"><div className="epp-kpi-icon"><CalendarDays size={19} /></div><div><small>Próx. reposición</small><strong>{kpis.proximos_reposicion || 0}</strong></div></article>
            <article className="epp-kpi-card epp-tone-red"><div className="epp-kpi-icon"><AlertTriangle size={19} /></div><div><small>Vencidos</small><strong>{kpis.vencidos || 0}</strong></div></article>
            <article className="epp-kpi-card epp-tone-purple"><div className="epp-kpi-icon"><HardHat size={19} /></div><div><small>Catálogo</small><strong>{kpis.catalogo || 0}</strong></div></article>
          </section>

          <section className="epp-indicators-grid">
            <article><small>Cobertura EPP</small><strong>{kpis.cobertura || 0}%</strong><div><span style={{ width: `${Math.min(kpis.cobertura || 0, 100)}%` }} /></div></article>
            <article><small>Cumplimiento firma</small><strong>{kpis.cumplimiento_firma || 0}%</strong><div><span style={{ width: `${Math.min(kpis.cumplimiento_firma || 0, 100)}%` }} /></div></article>
            <article><small>Cumplimiento evidencia</small><strong>{kpis.cumplimiento_evidencia || 0}%</strong><div><span style={{ width: `${Math.min(kpis.cumplimiento_evidencia || 0, 100)}%` }} /></div></article>
            <article><small>Integral EPP</small><strong>{cumplimientoIntegral}%</strong><div><span style={{ width: `${Math.min(cumplimientoIntegral, 100)}%` }} /></div></article>
          </section>

          <section className="epp-charts-grid">
            <BarList title="Entregas por EPP" icon={HardHat} data={charts.por_epp || []} />
            <BarList title="Por categoría" icon={BriefcaseMedical} data={charts.por_categoria || []} />
            <BarList title="Por estado" icon={Activity} data={charts.por_estado || []} />
            <BarList title="Por cargo" icon={UserCheck} data={charts.por_cargo || []} />
            <BarList title="Reposiciones críticas" icon={CalendarDays} data={charts.por_reposicion || []} />
          </section>


          <section className={`epp-semaforo-card epp-semaforo-${String(kpis.semaforo || "VERDE").toLowerCase()}`}>
            <div>
              <span>Semáforo EPP SST</span>
              <h3>{kpis.riesgo_epp || "BAJO"}</h3>
              <p>Cobertura: {kpis.cobertura || 0}% · Firma: {kpis.cumplimiento_firma || 0}% · Evidencia: {kpis.cumplimiento_evidencia || 0}%</p>
            </div>
            <strong>{kpis.riesgo_score || 0}</strong>
          </section>

          <section className="epp-table-card" ref={gestionEppRef}>
            <div className="epp-tabs-inline">
              <button className={tab === "entregas" ? "active" : ""} onClick={() => setTab("entregas")}>Entregas</button>
              <button className={tab === "catalogo" ? "active" : ""} onClick={() => setTab("catalogo")}>Catálogo EPP</button>
              <button
                type="button"
                className="epp-sidebar-toolbar-btn"
                onClick={() => setSidebarVisible((visible) => !visible)}
                title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
                aria-label={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
                aria-pressed={!sidebarVisible}
              >
                {sidebarVisible ? <Sidebar size={17} /> : <LayoutDashboard size={17} />}
              </button>
            </div>

            {tab === "entregas" ? (
              <>
                <div className="epp-subtabs">
                  <button className={subTab === "tabla" ? "active" : ""} onClick={() => setSubTab("tabla")}>Tabla entregas</button>
                  <button className={subTab === "consolidado" ? "active" : ""} onClick={() => { setSubTab("consolidado"); setEmpleadoConsolidado(null); cargarConsolidado(); }}>Consolidado por empleado</button>
                </div>

                {subTab === "tabla" ? (
                <>
                <div className="epp-filter-top">
                  <label className="epp-search"><Search size={16} /><input placeholder="Buscar por empleado, documento, EPP, marca o serial..." value={filtros.q} onChange={(e) => setFiltros((f) => ({ ...f, q: e.target.value }))} onKeyDown={(e) => e.key === "Enter" && cargarDatos()} /></label>
                  <button className="epp-btn-light" onClick={() => setFiltros({ q: "", empresa_id: "", sede_id: "", area_id: "", cargo_id: "", empleado_id: "", epp_id: "", estado: "" })}><Filter size={16} /> Limpiar</button>
                  <button className="epp-btn-light" onClick={cargarDatos}><RefreshCcw size={16} /> Actualizar</button>
                </div>

                <div className="epp-filters-grid">
                  <select value={filtros.empresa_id} onChange={(e) => setFiltros((f) => ({ ...f, empresa_id: e.target.value }))}><option value="">Todas las empresas</option>{empresas.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select>
                  <select value={filtros.sede_id} onChange={(e) => setFiltros((f) => ({ ...f, sede_id: e.target.value }))}><option value="">Todas las sedes</option>{sedes.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select>
                  <select value={filtros.area_id} onChange={(e) => setFiltros((f) => ({ ...f, area_id: e.target.value }))}><option value="">Todas las áreas</option>{areas.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select>
                  <select value={filtros.cargo_id} onChange={(e) => setFiltros((f) => ({ ...f, cargo_id: e.target.value }))}><option value="">Todos los cargos</option>{cargos.map((x) => <option key={x.id} value={x.id}>{x.nombre || x.nombre_cargo}</option>)}</select>
                  <select value={filtros.estado} onChange={(e) => setFiltros((f) => ({ ...f, estado: e.target.value }))}><option value="">Todos los estados</option><option value="VIGENTE">Vigente</option><option value="PROXIMO_REPOSICION">Próx. reposición</option><option value="VENCIDO">Vencido</option><option value="REEMPLAZADO">Reemplazado</option><option value="DEVUELTO">Devuelto</option><option value="ANULADO">Anulado</option></select>
                </div>
                <div className="epp-filters-grid epp-filters-grid-small">
                  <select value={filtros.empleado_id} onChange={(e) => setFiltros((f) => ({ ...f, empleado_id: e.target.value }))}><option value="">Todos los empleados</option>{empleados.map((x) => <option key={x.id} value={x.id}>{x.nombres} {x.apellidos}</option>)}</select>
                  <select value={filtros.epp_id} onChange={(e) => setFiltros((f) => ({ ...f, epp_id: e.target.value }))}><option value="">Todos los EPP</option>{catalogo.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select>
                </div>

                <div className="epp-table-wrap">
                  <table>
                    <thead><tr><th>Empleado</th><th>Empresa</th><th>EPP</th><th>Categoría</th><th>Cant.</th><th>Talla</th><th>Entrega</th><th>Reposición</th><th>Estado</th><th>Firma</th><th>Acciones</th></tr></thead>
                    <tbody>
                      {entregasPagina.length === 0 ? <tr><td colSpan="11" className="epp-empty">No hay entregas de EPP registradas.</td></tr> : entregasPagina.map((item) => (
                        <tr key={item.id}>
                          <td><div className="epp-person"><span>{(item.empleado_nombre || "EP").slice(0, 2).toUpperCase()}</span><div><b>{item.empleado_nombre}</b><small>{item.empleado_documento}</small></div></div></td>
                          <td>{item.empresa_nombre}<small>{item.sede_nombre || "Sin sede"}</small></td>
                          <td><b>{item.epp_nombre}</b><small>{item.epp_codigo}</small></td>
                          <td>{item.epp_categoria || "Sin categoría"}</td>
                          <td>{item.cantidad}</td>
                          <td>{item.talla || "-"}</td>
                          <td>{moneyDate(item.fecha_entrega)}</td>
                          <td>{moneyDate(item.fecha_reposicion)}<small>{item.dias_reposicion !== null && item.dias_reposicion !== undefined ? `${item.dias_reposicion} días` : ""}</small></td>
                          <td><span className={`epp-status ${(item.estado || "").toLowerCase()}`}>{estadoLabel(item.estado)}</span></td>
                          <td><button className={`epp-sign ${item.recibido_por_empleado ? "ok" : ""}`} onClick={() => marcarRecibido(item)}>{item.recibido_por_empleado ? "Firmado" : "Pendiente"}</button></td>
                          <td><div className="epp-actions"><button title="Ver" onClick={() => { setDetalle(item); setModoModal("detalle"); }}><Eye size={15} /></button><button title="Editar" onClick={() => abrirEntrega(item)}><Edit3 size={15} /></button><button title="Evidencias y firma" onClick={() => abrirEvidencias(item)}><UploadCloud size={15} /></button><button title="Ficha PDF" onClick={() => exportarFichaEntrega(item)}><FileText size={15} /></button><button title="Eliminar" onClick={() => eliminarEntrega(item)}><Trash2 size={15} /></button></div></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="epp-pagination"><span>Mostrando <b>{entregas.length ? (page - 1) * pageSize + 1 : 0}</b> - <b>{Math.min(page * pageSize, entregas.length)}</b> de <b>{entregas.length}</b> entregas</span><div className="epp-page-controls"><label>Registros <select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}><option>10</option><option>25</option><option>50</option></select></label><button disabled={page <= 1} onClick={() => setPage((p) => Math.max(p - 1, 1))}><ChevronLeft size={16} /></button><b>Página {page} / {totalPages}</b><button disabled={page >= totalPages} onClick={() => setPage((p) => Math.min(p + 1, totalPages))}><ChevronRight size={16} /></button></div></div>
                </>
                ) : (
                <div className="epp-consolidado">
                  {empleadoConsolidado ? (
                    <>
                      <button className="epp-btn epp-btn-secondary" style={{ marginBottom: 12 }} onClick={() => setEmpleadoConsolidado(null)}>
                        ← Volver a la lista
                      </button>
                      <div className="epp-consolidado-card">
                        <div className="epp-consolidado-header">
                          <div className="epp-person">
                            <span>{(empleadoConsolidado.empleado_nombre || "EP").slice(0, 2).toUpperCase()}</span>
                            <div>
                              <b>{empleadoConsolidado.empleado_nombre}</b>
                              <small>{empleadoConsolidado.empleado_documento} · {empleadoConsolidado.cargo_nombre || "Sin cargo"}</small>
                            </div>
                          </div>
                          <span className="epp-consolidado-badge">{empleadoConsolidado.total_epp} EPP</span>
                        </div>
                        <div className="epp-consolidado-meta">
                          <span>{empleadoConsolidado.empresa_nombre || "Sin empresa"}</span>
                          <span>{empleadoConsolidado.sede_nombre || "Sin sede"}</span>
                          <span>{empleadoConsolidado.area_nombre || "Sin área"}</span>
                        </div>
                        <div className="epp-consolidado-items">
                          {empleadoConsolidado.epp_entregados.map((epp, idx) => (
                            <div key={idx} className="epp-consolidado-item">
                              <div className="epp-consolidado-item-info">
                                <b>{epp.epp_nombre}</b>
                                <small>{epp.epp_codigo} · {epp.epp_categoria || "Sin categoría"}</small>
                              </div>
                              <div className="epp-consolidado-item-details">
                                {epp.talla && <span>Talla: {epp.talla}</span>}
                                {epp.marca && <span>Marca: {epp.marca}</span>}
                                {epp.serial && <span>Serial: {epp.serial}</span>}
                              </div>
                              <div className="epp-consolidado-item-dates">
                                <span>Entrega: {epp.fecha_entrega}</span>
                                {epp.fecha_reposicion && <span>Reposición: {epp.fecha_reposicion}</span>}
                              </div>
                              <span className={`epp-status ${epp.estado === "VIGENTE" ? "vigente" : epp.estado === "VENCIDO" ? "anulado" : ""}`}>{epp.estado}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  ) : consolidado.length === 0 ? (
                    <p className="epp-empty">No hay empleados con entregas de EPP registradas.</p>
                  ) : consolidado.map((emp) => (
                    <div key={emp.empleado_id} className="epp-consolidado-card epp-consolidado-selectable" onClick={() => setEmpleadoConsolidado(emp)}>
                      <div className="epp-consolidado-header">
                        <div className="epp-person">
                          <span>{(emp.empleado_nombre || "EP").slice(0, 2).toUpperCase()}</span>
                          <div>
                            <b>{emp.empleado_nombre}</b>
                            <small>{emp.empleado_documento} · {emp.cargo_nombre || "Sin cargo"}</small>
                          </div>
                        </div>
                        <span className="epp-consolidado-badge">{emp.total_epp} EPP</span>
                      </div>
                      <div className="epp-consolidado-meta">
                        <span>{emp.empresa_nombre || "Sin empresa"}</span>
                        <span>{emp.sede_nombre || "Sin sede"}</span>
                        <span>{emp.area_nombre || "Sin área"}</span>
                      </div>
                    </div>
                  ))}
                </div>
                )}
              </>
            ) : (
              <div className="epp-table-wrap epp-catalog-table-wrap">
                <table className="epp-catalog-table">
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Elemento de protección</th>
                      <th>Categoría</th>
                      <th>Vida útil</th>
                      <th>Requisitos</th>
                      <th>Estado</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {catalogo.length === 0 ? (
                      <tr><td colSpan="7" className="epp-empty">No hay elementos de protección registrados.</td></tr>
                    ) : catalogo.map((item) => (
                      <tr key={item.id}>
                        <td><b>{item.codigo || "Sin código"}</b></td>
                        <td>
                          <div className="epp-catalog-name">
                            <span><HardHat size={16} /></span>
                            <div><b>{item.nombre}</b><small>{item.descripcion || "Sin descripción"}</small></div>
                          </div>
                        </td>
                        <td>{item.categoria || "Sin categoría"}</td>
                        <td>{item.vida_util_dias || 0} días</td>
                        <td>
                          <div className="epp-requirements">
                            {item.requiere_firma && <span>Firma</span>}
                            {item.requiere_reposicion && <span>Reposición</span>}
                            {item.requiere_evidencia && <span>Evidencia</span>}
                            {!item.requiere_firma && !item.requiere_reposicion && !item.requiere_evidencia && <small>Sin requisitos</small>}
                          </div>
                        </td>
                        <td><span className={`epp-status ${item.activo === false ? "anulado" : "vigente"}`}>{item.activo === false ? "Inactivo" : item.estado || "Activo"}</span></td>
                        <td>
                          <div className="epp-actions">
                            <button type="button" title="Ver ficha técnica" className="epp-action-ficha" onClick={() => abrirFichaTecnica(item)}>
                              <FileText size={15} />
                            </button>
                            <button type="button" title="Editar EPP" onClick={() => abrirCatalogo(item)}><Edit3 size={15} /></button>
                            <button type="button" title="Eliminar EPP" onClick={() => eliminarCatalogo(item)}><Trash2 size={15} /></button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>

        <aside className={`epp-right-panel epp-right-panel-pro ${!sidebarVisible ? "epp-panel-hidden" : ""}`} aria-label="Dashboard lateral inteligente de EPP SST">
          <article className="epp-intel-card epp-intel-pro">
            <div className="epp-side-title-row">
              <h3>Dashboard inteligente</h3>
              <div className="epp-sidebar-header-actions">
                <button
                  type="button"
                  className="epp-sidebar-toggle-btn"
                  onClick={() => setSidebarVisible((visible) => !visible)}
                  title={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
                  aria-label={sidebarVisible ? "Ocultar panel lateral" : "Mostrar panel lateral"}
                  aria-pressed={!sidebarVisible}
                >
                  {sidebarVisible ? <Sidebar size={18} /> : <LayoutDashboard size={18} />}
                </button>
                <span className="epp-ai-badge">AI</span>
              </div>
            </div>
            <div className="epp-intel-body">
              <div className="epp-ring epp-ring-pro" style={{ "--epp-ring": `${Math.min(coberturaEpp, 100)}%` }}>
                <strong>{coberturaEpp}%</strong>
                <span>Índice EPP</span>
              </div>
              <div className="epp-intel-copy">
                <h4>{estadoInteligente ? "Gestión con pendientes" : "Gestión estable y óptima"}</h4>
                <p>Control de cobertura, firmas, evidencias, reposición y riesgo EPP por trabajador.</p>
                <em className={estadoInteligente ? "warn" : "ok"}>{estadoInteligente ? "Revisar" : "Excelente"}</em>
              </div>
            </div>
            <div className="epp-intel-mini-stats">
              <div><ClipboardCheck size={18} /><span>Entregas</span><b>{kpis.total_entregas || 0}</b></div>
              <div><ShieldCheck size={18} /><span>Vigentes</span><b>{kpis.vigentes || 0}</b></div>
              <div><UserCheck size={18} /><span>Firmados</span><b>{kpis.firmados || 0}</b></div>
              <div><Paperclip size={18} /><span>Evidencias</span><b>{kpis.entregas_con_evidencia || 0}</b></div>
              <div><AlertTriangle size={18} /><span>Críticos</span><b>{eppCriticas}</b></div>
            </div>
          </article>

          <article className="epp-side-card epp-alert-card">
            <div className="epp-side-title-row">
              <h3><AlertTriangle size={18} /> Alertas EPP</h3>
              <b className={eppCriticas > 0 ? "warn" : ""}>{eppCriticas} críticas</b>
            </div>
            <div className="epp-alert-list">
              {[
                ["Vencen en 7 días", alertas.vencen_7_dias || 0, CalendarDays, "orange", "Reposición inmediata"],
                ["Vencen en 30 días", alertas.vencen_30_dias || 0, CalendarDays, "orange", "Seguimiento preventivo"],
                ["Vencidos", alertas.vencidos || 0, AlertTriangle, "red", "Reposición inmediata"],
                ["Sin firma", alertas.sin_firma || 0, ClipboardCheck, "purple", "Firma pendiente"],
                ["Sin evidencia", alertas.sin_evidencia || 0, Paperclip, "orange", "Soporte documental"],
                ["Empleados sin EPP", alertas.empleados_sin_epp || 0, UserCheck, "blue", "Asignación pendiente"],
              ].map(([label, value, Icon, tone, help]) => (
                <div className={`epp-alert-row epp-alert-${tone}`} key={label}>
                  <span className="epp-alert-icon"><Icon size={17} /></span>
                  <div><b>{label}</b><small>{help}</small></div>
                  <strong>{value}</strong>
                  <em className={value > 0 ? "warn" : "ok"}>{value > 0 ? "Revisar" : "Óptimo"}</em>
                </div>
              ))}
            </div>
          </article>

          <article className="epp-side-card epp-dist-card">
            <div className="epp-side-title-row">
              <h3><ShieldCheck size={18} /> Distribución base</h3>
              <span className="epp-detail-badge">Ver detalle</span>
            </div>
            <div className="epp-distribution-pro">
              {distribucionBase.map(({ label, value, pct, tone, icon: Icon }) => (
                <div className={`epp-dist-row epp-dist-${tone}`} key={label}>
                  <span className="epp-dist-icon"><Icon size={17} /></span>
                  <div className="epp-dist-main">
                    <div><b>{label}</b><strong>{value}</strong><em>{pct}%</em></div>
                    <div className="epp-dist-track"><span style={{ width: `${Math.min(pct, 100)}%` }} /></div>
                  </div>
                </div>
              ))}
            </div>
          </article>

          <article className="epp-side-card epp-rec-card">
            <div className="epp-side-title-row">
              <h3><Activity size={18} /> Recomendaciones PRO</h3>
              <span className="epp-pro-badge">PRO</span>
            </div>
            <div className="epp-rec-list">
              {recomendacionesPRO.map((r, i) => (
                <div className="epp-rec-row" key={`${r}-${i}`}>
                  <span>{i + 1}</span>
                  <div><b>{i === 0 ? "Gestión EPP" : i === 1 ? "Trazabilidad" : "Reposición"}</b><small>{r}</small></div>
                </div>
              ))}
            </div>
          </article>
        </aside>
      </section>


      {modoModal === "evidencias" && evidenciaEntrega && (
        <div className="epp-modal-backdrop">
          <section className="epp-form-modal epp-evidence-modal">
            <header className="epp-modal-header">
              <div>
                <span>Evidencias y Firma EPP Enterprise</span>
                <h2>Evidencias y firma 360°</h2>
                <p>{evidenciaEntrega.empleado_nombre} · {evidenciaEntrega.epp_nombre} · {estadoLabel(evidenciaEntrega.estado)}</p>
              </div>
              <button type="button" className="epp-close" onClick={cerrarModal}><X size={20} /></button>
            </header>

            <section className="epp-modal-body epp-evidence-body">
              <article className="epp-drop-zone"
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  const file = e.dataTransfer.files?.[0];
                  if (file) setFormEvidencia((f) => ({ ...f, archivo: file }));
                }}>
                <UploadCloud size={44} />
                <h3>Arrastra y suelta la evidencia EPP</h3>
                <p>PDF, JPG, PNG o WEBP. El backend optimiza imágenes a WEBP y comprime PDF cuando es posible.</p>
                <label className="epp-upload-pill">
                  Seleccionar archivo
                  <input type="file" accept=".pdf,image/*" onChange={(e) => setFormEvidencia((f) => ({ ...f, archivo: e.target.files?.[0] || null }))} />
                </label>
                {formEvidencia.archivo && <strong>{formEvidencia.archivo.name} · {bytesToSize(formEvidencia.archivo.size)}</strong>}
              </article>

              <form className="epp-evidence-form" onSubmit={subirEvidencia}>
                <h3><FileText size={18} /> Clasificación documental</h3>
                <label>Tipo evidencia
                  <select value={formEvidencia.tipo_evidencia} onChange={(e) => setFormEvidencia((f) => ({ ...f, tipo_evidencia: e.target.value, descripcion: evidenciaLabel(e.target.value) }))}>
                    <option value="ACTA_ENTREGA">Acta entrega</option>
                    <option value="FOTO_ENTREGA">Foto entrega</option>
                    <option value="EPP_RECIBIDO">EPP recibido</option>
                    <option value="FIRMA_EMPLEADO">Firma empleado</option>
                    <option value="SOPORTE">Otro soporte</option>
                  </select>
                </label>
                <label>Descripción
                  <input value={formEvidencia.descripcion} onChange={(e) => setFormEvidencia((f) => ({ ...f, descripcion: e.target.value }))} />
                </label>
                <button type="submit" className="epp-btn-primary" disabled={saving}><UploadCloud size={16} /> {saving ? "Subiendo..." : "Subir evidencia"}</button>
              </form>

              <aside className="epp-doc-dashboard">
                <h3>Dashboard documental</h3>
                <div><strong>{evidencias.length}</strong><span>Archivos</span></div>
                <div><strong>{evidencias.filter((x) => x.extension === "pdf").length}</strong><span>PDF</span></div>
                <div><strong>{evidencias.filter((x) => String(x.mime_type || "").startsWith("image/")).length}</strong><span>Imágenes</span></div>
                <div><strong>{evidencias.filter((x) => x.tipo === "FIRMA_EMPLEADO").length}</strong><span>Firmas</span></div>
              </aside>

              <section className="epp-signature-panel">
                <h3><PenLine size={18} /> Firma digital de recibido</h3>
                <p>Captura la firma del trabajador para dejar trazabilidad de recibido.</p>
                <SignaturePad value={firmaData} onChange={setFirmaData} />
                <button type="button" className="epp-btn-primary" onClick={firmarEntrega} disabled={firmando}><Save size={16} /> {firmando ? "Guardando firma..." : "Guardar firma"}</button>
              </section>

              <section className="epp-evidence-list">
                <h3><Paperclip size={18} /> Evidencias registradas</h3>
                {evidencias.length === 0 ? <div className="epp-empty-card">No hay evidencias registradas para esta entrega.</div> : evidencias.map((archivo) => (
                  <article key={archivo.id} className="epp-file-row">
                    <span>{archivo.extension === "pdf" ? <FileText size={20} /> : <ImageIcon size={20} />}</span>
                    <div>
                      <b>{archivo.nombre_original}</b>
                      <small>{evidenciaLabel(archivo.tipo)} · {String(archivo.extension || "").toUpperCase()} · {bytesToSize(archivo.tamano_bytes)}</small>
                      <small>{archivo.descripcion || "Sin descripción"}</small>
                    </div>
                    <button type="button" title="Ver" onClick={() => setPreview(archivo)}><Eye size={16} /></button>
                    <a title="Descargar" href={archivo.url} target="_blank" rel="noreferrer"><Download size={16} /></a>
                    <button type="button" className="danger" title="Eliminar" onClick={() => eliminarEvidencia(archivo)}><Trash2 size={16} /></button>
                  </article>
                ))}
              </section>

              <section className="epp-doc-timeline">
                <h3><Activity size={18} /> Timeline documental</h3>
                {evidencias.length === 0 ? <p>Sin movimientos documentales.</p> : evidencias.map((archivo) => (
                  <div key={`time-${archivo.id}`}>
                    <i />
                    <b>{evidenciaLabel(archivo.tipo)}</b>
                    <small>{archivo.fecha_creacion ? new Date(archivo.fecha_creacion).toLocaleString() : "Sin fecha"}</small>
                    <span>{archivo.nombre_original}</span>
                  </div>
                ))}
              </section>
            </section>
            <footer className="epp-modal-footer"><button className="epp-btn-light" onClick={cerrarModal}>Cerrar</button></footer>
          </section>

          {preview && (
            <div className="epp-preview-backdrop" onClick={() => setPreview(null)}>
              <section className="epp-preview-modal" onClick={(e) => e.stopPropagation()}>
                <header><b>{preview.nombre_original}</b><button onClick={() => setPreview(null)}><X size={18} /></button></header>
                {String(preview.mime_type || "").includes("pdf") ? (
                  <iframe src={preview.url} title={preview.nombre_original} />
                ) : (
                  <img src={preview.url} alt={preview.nombre_original} />
                )}
              </section>
            </div>
          )}
        </div>
      )}

      {modoModal === "entrega" && (

        <div className="epp-modal-backdrop">
          <form className="epp-form-modal" onSubmit={guardarEntrega}>
            <header className="epp-modal-header"><div><span>{editando ? "Editar entrega" : modoEntrega === "lote" ? "Entrega múltiple" : "Nueva entrega"}</span><h2>{modoEntrega === "lote" ? "Entrega Múltiple EPP" : "Entrega EPP Enterprise 360°"}</h2><p>{modoEntrega === "lote" ? "Seleccione múltiples EPP para entregar a un empleado." : "Registro de dotación, reposición y trazabilidad por empleado."}</p></div><button type="button" className="epp-close" onClick={cerrarModal}><X size={20} /></button></header>
            <section className="epp-modal-body"><div className="epp-form-grid">
              <label>Empresa *<select value={formEntrega.empresa_id} onChange={(e) => onChangeEntrega("empresa_id", e.target.value)} required><option value="">Seleccionar empresa</option>{empresas.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select></label>
              <label>Empleado *<select value={formEntrega.empleado_id} onChange={(e) => onChangeEntrega("empleado_id", e.target.value)} required><option value="">Seleccionar empleado</option>{empleadosFiltrados.map((x) => <option key={x.id} value={x.id}>{x.nombres} {x.apellidos} · {x.documento}</option>)}</select></label>
              <label>Fecha entrega *<input type="date" value={formEntrega.fecha_entrega} onChange={(e) => onChangeEntrega("fecha_entrega", e.target.value)} required /></label>

              {modoEntrega === "lote" ? (
                <div className="epp-full epp-lote-section">
                  <div className="epp-lote-header">
                    <strong>Elementos EPP a entregar</strong>
                    <button type="button" className="epp-btn-light" onClick={agregarItemLote}>
                      <Plus size={15} /> Agregar EPP
                    </button>
                  </div>
                  {itemsLote.length === 0 && (
                    <p className="epp-lote-empty">Haga clic en "Agregar EPP" para seleccionar los elementos a entregar.</p>
                  )}
                  {itemsLote.map((item, idx) => (
                    <div key={idx} className="epp-lote-item">
                      <div className="epp-lote-item-fields">
                        <select value={item.epp_id} onChange={(e) => actualizarItemLote(idx, "epp_id", e.target.value)} required>
                          <option value="">Seleccionar EPP</option>
                          {catalogoFiltrado.map((x) => <option key={x.id} value={x.id}>{x.nombre} · {x.codigo}</option>)}
                        </select>
                        <input type="number" min="1" placeholder="Cant." value={item.cantidad} onChange={(e) => actualizarItemLote(idx, "cantidad", e.target.value)} />
                        <input placeholder="Talla" value={item.talla} onChange={(e) => actualizarItemLote(idx, "talla", e.target.value)} />
                        <input placeholder="Marca" value={item.marca} onChange={(e) => actualizarItemLote(idx, "marca", e.target.value)} />
                        <input placeholder="Modelo" value={item.modelo} onChange={(e) => actualizarItemLote(idx, "modelo", e.target.value)} />
                        <input placeholder="Serial" value={item.serial} onChange={(e) => actualizarItemLote(idx, "serial", e.target.value)} />
                      </div>
                      <button type="button" className="epp-lote-remove" onClick={() => eliminarItemLote(idx)} title="Eliminar">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <>
                  <label>EPP *<select value={formEntrega.epp_id} onChange={(e) => onChangeEntrega("epp_id", e.target.value)} required><option value="">Seleccionar EPP</option>{catalogoFiltrado.map((x) => <option key={x.id} value={x.id}>{x.nombre} · {x.codigo}</option>)}</select></label>
                  <label>Cantidad *<input type="number" min="1" value={formEntrega.cantidad} onChange={(e) => onChangeEntrega("cantidad", e.target.value)} required /></label>
                  <label>Fecha reposición<input type="date" value={formEntrega.fecha_reposicion || ""} onChange={(e) => onChangeEntrega("fecha_reposicion", e.target.value)} /></label>
                  <label>Talla<input value={formEntrega.talla} onChange={(e) => onChangeEntrega("talla", e.target.value)} placeholder="M, L, 40, universal..." /></label>
                  <label>Marca<input value={formEntrega.marca} onChange={(e) => onChangeEntrega("marca", e.target.value)} /></label>
                  <label>Modelo<input value={formEntrega.modelo} onChange={(e) => onChangeEntrega("modelo", e.target.value)} /></label>
                  <label>Serial<input value={formEntrega.serial} onChange={(e) => onChangeEntrega("serial", e.target.value)} /></label>
                  <label>Estado<select value={formEntrega.estado} onChange={(e) => onChangeEntrega("estado", e.target.value)}><option value="ENTREGADO">Entregado</option><option value="VIGENTE">Vigente</option><option value="PROXIMO_REPOSICION">Próx. reposición</option><option value="VENCIDO">Vencido</option><option value="REEMPLAZADO">Reemplazado</option><option value="DEVUELTO">Devuelto</option><option value="ANULADO">Anulado</option></select></label>
                  <label className="epp-check"><input type="checkbox" checked={formEntrega.recibido_por_empleado} onChange={(e) => onChangeEntrega("recibido_por_empleado", e.target.checked)} /> Recibido por empleado</label>
                  <label className="epp-full">Observaciones<textarea value={formEntrega.observaciones} onChange={(e) => onChangeEntrega("observaciones", e.target.value)} /></label>
                </>
              )}
            </div></section>
            <footer className="epp-modal-footer"><button type="button" className="epp-btn-light" onClick={cerrarModal}>Cancelar</button><button type="submit" className="epp-btn-primary" disabled={saving}>{saving ? "Guardando..." : modoEntrega === "lote" ? "Entregar todo" : "Guardar entrega"}</button></footer>
          </form>
        </div>
      )}

      {modoModal === "catalogo" && (
        <div className="epp-modal-backdrop">
          <form className="epp-form-modal epp-form-modal-small" onSubmit={guardarCatalogo}>
            <header className="epp-modal-header"><div><span>{editando ? "Editar catálogo" : "Nuevo EPP"}</span><h2>Catálogo EPP</h2><p>Administración de elementos de protección personal.</p></div><button type="button" className="epp-close" onClick={cerrarModal}><X size={20} /></button></header>
            <section className="epp-modal-body"><div className="epp-form-grid">
              <label>Empresa *<select value={formCatalogo.empresa_id} onChange={(e) => setFormCatalogo((f) => ({ ...f, empresa_id: e.target.value }))} required><option value="">Seleccionar empresa</option>{empresas.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}</select></label>
              <label>Código *<input value={formCatalogo.codigo} onChange={(e) => setFormCatalogo((f) => ({ ...f, codigo: e.target.value }))} required /></label>
              <label>Nombre *<input value={formCatalogo.nombre} onChange={(e) => setFormCatalogo((f) => ({ ...f, nombre: e.target.value }))} required /></label>
              <label>Categoría<input value={formCatalogo.categoria} onChange={(e) => setFormCatalogo((f) => ({ ...f, categoria: e.target.value }))} /></label>
              <label>Vida útil días<input type="number" min="0" value={formCatalogo.vida_util_dias} onChange={(e) => setFormCatalogo((f) => ({ ...f, vida_util_dias: e.target.value }))} /></label>
              <label>Estado<select value={formCatalogo.estado} onChange={(e) => setFormCatalogo((f) => ({ ...f, estado: e.target.value }))}><option value="ACTIVO">Activo</option><option value="INACTIVO">Inactivo</option></select></label>
              <label className="epp-check"><input type="checkbox" checked={formCatalogo.requiere_reposicion} onChange={(e) => setFormCatalogo((f) => ({ ...f, requiere_reposicion: e.target.checked }))} /> Requiere reposición</label>
              <label className="epp-check"><input type="checkbox" checked={formCatalogo.requiere_firma} onChange={(e) => setFormCatalogo((f) => ({ ...f, requiere_firma: e.target.checked }))} /> Requiere firma</label>
              <label className="epp-check"><input type="checkbox" checked={formCatalogo.requiere_evidencia} onChange={(e) => setFormCatalogo((f) => ({ ...f, requiere_evidencia: e.target.checked }))} /> Requiere evidencia</label>
              <label className="epp-full">Descripción<textarea value={formCatalogo.descripcion} onChange={(e) => setFormCatalogo((f) => ({ ...f, descripcion: e.target.value }))} /></label>

              <div className="epp-full epp-ficha-tecnica-section">
                <label className="epp-ficha-label">Ficha Técnica (PDF)</label>
                {editando?.ficha_tecnica_url ? (
                  <div className="epp-ficha-existing">
                    <span className="epp-ficha-name">{editando.ficha_tecnica_nombre || "Ficha técnica cargada"}</span>
                    <button type="button" className="epp-btn-view" onClick={() => abrirFichaTecnica(editando)}>
                      <Eye size={15} /> Ver
                    </button>
                    <button type="button" className="epp-btn-danger-sm" onClick={() => eliminarFichaTecnica(editando.id)} disabled={saving}>
                      <Trash2 size={15} /> Eliminar
                    </button>
                  </div>
                ) : (
                  <div className="epp-ficha-upload">
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={(e) => setFichaTecnicaFile(e.target.files?.[0] || null)}
                      id="ficha-tecnica-input"
                      style={{ display: "none" }}
                    />
                    <label htmlFor="ficha-tecnica-input" className="epp-ficha-btn">
                      <UploadCloud size={16} /> Seleccionar PDF
                    </label>
                    {fichaTecnicaFile && (
                      <span className="epp-ficha-name">{fichaTecnicaFile.name}</span>
                    )}
                  </div>
                )}
              </div>
            </div></section>
            <footer className="epp-modal-footer"><button type="button" className="epp-btn-light" onClick={cerrarModal}>Cancelar</button><button type="submit" className="epp-btn-primary" disabled={saving}>{saving ? "Guardando..." : "Guardar EPP"}</button></footer>
          </form>
        </div>
      )}

      {modoModal === "detalle" && detalle && (
        <div className="epp-modal-backdrop">
          <section className="epp-form-modal epp-form-modal-small">
            <header className="epp-modal-header"><div><span>Vista detalle</span><h2>{detalle.epp_nombre}</h2><p>{detalle.empleado_nombre} · {detalle.empleado_documento}</p></div><button type="button" className="epp-close" onClick={cerrarModal}><X size={20} /></button></header>
            <section className="epp-modal-body"><div className="epp-detail-grid">
              <article><h3>Empleado</h3><p><b>Nombre:</b> {detalle.empleado_nombre}</p><p><b>Empresa:</b> {detalle.empresa_nombre}</p><p><b>Sede:</b> {detalle.sede_nombre || "Sin sede"}</p><p><b>Área:</b> {detalle.area_nombre || "Sin área"}</p><p><b>Cargo:</b> {detalle.cargo_nombre || "Sin cargo"}</p></article>
              <article><h3>EPP</h3><p><b>Elemento:</b> {detalle.epp_nombre}</p><p><b>Código:</b> {detalle.epp_codigo}</p><p><b>Categoría:</b> {detalle.epp_categoria}</p><p><b>Cantidad:</b> {detalle.cantidad}</p><p><b>Talla:</b> {detalle.talla || "Sin dato"}</p></article>
              <article><h3>Trazabilidad</h3><p><b>Entrega:</b> {moneyDate(detalle.fecha_entrega)}</p><p><b>Reposición:</b> {moneyDate(detalle.fecha_reposicion)}</p><p><b>Estado:</b> {estadoLabel(detalle.estado)}</p><p><b>Firma:</b> {detalle.recibido_por_empleado ? "Recibido por empleado" : "Pendiente"}</p><p><b>Observaciones:</b> {detalle.observaciones || "Sin observaciones"}</p></article>
            </div></section>
            <footer className="epp-modal-footer"><button className="epp-btn-light" onClick={cerrarModal}>Cerrar</button></footer>
          </section>
        </div>
      )}

      {fichaTecnicaModal && (
        <div className="epp-modal-backdrop" onClick={() => setFichaTecnicaModal(null)}>
          <section className="epp-form-modal epp-ficha-modal" onClick={(e) => e.stopPropagation()}>
            <header className="epp-modal-header">
              <div>
                <span>Ficha Técnica</span>
                <h2>{fichaTecnicaModal.nombre}</h2>
                <p>{fichaTecnicaModal.ficha_tecnica_nombre || "Documento PDF"}</p>
              </div>
              <button type="button" className="epp-close" onClick={() => setFichaTecnicaModal(null)}>
                <X size={20} />
              </button>
            </header>
            <section className="epp-modal-body epp-ficha-body">
              {fichaTecnicaModal.ficha_tecnica_url ? (
                <iframe
                  src={fichaTecnicaModal.ficha_tecnica_url}
                  title={`Ficha técnica - ${fichaTecnicaModal.nombre}`}
                  className="epp-ficha-iframe"
                />
              ) : (
                <div className="epp-ficha-empty">
                  <FileText size={48} />
                  <p>No cuenta con ficha técnica</p>
                  <small>Suba una ficha técnica desde la edición del EPP.</small>
                </div>
              )}
            </section>
            <footer className="epp-modal-footer">
              {fichaTecnicaModal.ficha_tecnica_url && (
                <a href={fichaTecnicaModal.ficha_tecnica_url} target="_blank" rel="noopener noreferrer" className="epp-btn-primary">
                  <Download size={15} /> Descargar
                </a>
              )}
              <button className="epp-btn-light" onClick={() => setFichaTecnicaModal(null)}>Cerrar</button>
            </footer>
          </section>
        </div>
      )}
    </main>
  );
}
