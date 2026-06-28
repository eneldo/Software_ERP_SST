// ============================================================
// REPORTE ANÓNIMO SST PÚBLICO - ERP SST PRO
// FASE 1.1.25.3 — Versión simplificada sin Empresa/Sede + QR
// Archivo: frontend/src/pages/public/ReporteAnonimoSSTPage.jsx
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Copy,
  Download,
  FileUp,
  Link as LinkIcon,
  MapPin,
  QrCode,
  ShieldAlert,
  Send,
  UserRound,
  XCircle,
} from "lucide-react";
import {
  crearReporteAnonimoSST,
  obtenerOpcionesReporteAnonimoSST,
} from "../../api/reporteAnonimoSstApi";
import "../../styles/reporte-anonimo-sst.css";
import "../../styles/reportes-evidencias.css";

const initialForm = {
  area_id: "",
  tipo: "CONDICION_INSEGURA",
  prioridad: "MEDIA",
  ubicacion: "",
  titulo: "",
  descripcion: "",
  accion_inmediata: "",
  observaciones: "",
  nombre_reportante: "",
  telefono_reportante: "",
  correo_reportante: "",
};

const tipos = [
  ["ACTO_INSEGURO", "Acto inseguro"],
  ["CONDICION_INSEGURA", "Condición insegura"],
  ["INCIDENTE", "Incidente"],
  ["ACCIDENTE", "Accidente"],
  ["SUGERENCIA", "Sugerencia SST"],
];

const prioridades = ["BAJA", "MEDIA", "ALTA", "CRITICA"];

const mensajeError = (error) => {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((e) => `${e.loc?.join(" → ")}: ${e.msg}`).join("\n");
  }
  if (typeof detail === "string") return detail;
  return error?.message || "No fue posible enviar el reporte.";
};

const urlActualReporte = () => {
  if (typeof window === "undefined") return "/reporte-sst";
  return window.location.href.split("?")[0];
};

const urlQR = (url) =>
  `https://api.qrserver.com/v1/create-qr-code/?size=260x260&margin=12&data=${encodeURIComponent(url)}`;

export default function ReporteAnonimoSSTPage() {
  const [form, setForm] = useState(initialForm);
  const [opciones, setOpciones] = useState({ areas: [], empresa_default: null });
  const [archivos, setArchivos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [alerta, setAlerta] = useState(null);
  const [mostrarQR, setMostrarQR] = useState(false);

  const publicUrl = useMemo(() => urlActualReporte(), []);
  const qrImageUrl = useMemo(() => urlQR(publicUrl), [publicUrl]);

  useEffect(() => {
    obtenerOpcionesReporteAnonimoSST()
      .then((data) => setOpciones(data || { areas: [] }))
      .catch(() =>
        setAlerta({
          tipo: "error",
          texto: "No fue posible cargar las áreas. Aun así puedes enviar el reporte sin seleccionar área.",
        })
      );
  }, []);

  const areas = useMemo(() => opciones.areas || [], [opciones.areas]);

  const setValue = (field, value) => setForm((prev) => ({ ...prev, [field]: value }));

  const limpiar = () => {
    setForm(initialForm);
    setArchivos([]);
    setAlerta(null);
  };

  const copiarLink = async () => {
    try {
      await navigator.clipboard.writeText(publicUrl);
      setAlerta({ tipo: "success", texto: "Link público copiado al portapapeles." });
    } catch {
      setAlerta({ tipo: "error", texto: `No fue posible copiar. Link: ${publicUrl}` });
    }
  };

  const descargarQR = async () => {
    const link = document.createElement("a");
    link.href = qrImageUrl;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.download = "qr_reporte_anonimo_sst.png";
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const enviar = async (event) => {
    event.preventDefault();
    setAlerta(null);

    if (!form.ubicacion.trim() || !form.titulo.trim() || form.descripcion.trim().length < 10) {
      setAlerta({
        tipo: "error",
        texto: "Ubicación, título y descripción son obligatorios. La descripción debe tener mínimo 10 caracteres.",
      });
      return;
    }

    try {
      setLoading(true);
      const fd = new FormData();
      Object.entries(form).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") fd.append(key, value);
      });
      archivos.forEach((file) => fd.append("archivos", file));

      const resp = await crearReporteAnonimoSST(fd);
      setAlerta({ tipo: "success", texto: `${resp.mensaje} Código: ${resp.codigo}` });
      setForm(initialForm);
      setArchivos([]);
    } catch (error) {
      setAlerta({ tipo: "error", texto: mensajeError(error) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="reporte-anonimo-page">
      <section className="reporte-public-hero">
        <div>
          <span className="reporte-public-tag">
            <ShieldAlert size={16} /> Reporte público SG-SST
          </span>
          <h1>Reporte Anónimo SST</h1>
          <p>
            Informa actos inseguros, condiciones inseguras, incidentes, accidentes o sugerencias sin usuario ni contraseña.
          </p>
        </div>
        <div className="reporte-public-badge">
          <UserRound size={26} />
          <strong>Confidencial</strong>
          <small>Datos del reportante opcionales</small>
        </div>
      </section>

      <section className="reporte-qr-panel">
        <div>
          <h2>
            <QrCode size={20} /> Link público y QR SST
          </h2>
          <p>Comparte este enlace o imprime el QR en carteleras, áreas comunes, recepción, taller o bodega.</p>
          <code>{publicUrl}</code>
        </div>
        <div className="reporte-qr-actions">
          <button type="button" onClick={() => setMostrarQR((v) => !v)}>
            <QrCode size={17} /> {mostrarQR ? "Ocultar QR" : "Generar QR"}
          </button>
          <button type="button" onClick={copiarLink}>
            <Copy size={17} /> Copiar link
          </button>
        </div>
        {mostrarQR && (
          <div className="reporte-qr-box">
            <img src={qrImageUrl} alt="QR Reporte Anónimo SST" />
            <button type="button" onClick={descargarQR}>
              <Download size={16} /> Descargar / abrir QR
            </button>
            <small>El QR apunta al formulario público actual.</small>
          </div>
        )}
      </section>

      {alerta && (
        <div className={`reporte-alert ${alerta.tipo}`}>
          {alerta.tipo === "success" ? <CheckCircle2 /> : <XCircle />}
          <span>{alerta.texto}</span>
        </div>
      )}

      <form className="reporte-public-card" onSubmit={enviar}>
        <header>
          <h2>Registrar reporte SST</h2>
          <p>Tu reporte genera una alerta automática para el equipo SST.</p>
        </header>

        <div className="tipo-grid">
          {tipos.map(([value, label]) => (
            <button
              type="button"
              key={value}
              className={form.tipo === value ? "active" : ""}
              onClick={() => setValue("tipo", value)}
            >
              <AlertTriangle size={18} /> {label}
            </button>
          ))}
        </div>

        <div className="reporte-form-grid simplified">
          <label>
            <span>Área relacionada</span>
            <select value={form.area_id} onChange={(e) => setValue("area_id", e.target.value)}>
              <option value="">No aplica / No sé</option>
              {areas.map((a) => (
                <option key={a.id} value={a.id}>{a.nombre}</option>
              ))}
            </select>
          </label>

          <label>
            <span>Prioridad</span>
            <select value={form.prioridad} onChange={(e) => setValue("prioridad", e.target.value)}>
              {prioridades.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </label>

          <label className="wide">
            <span><MapPin size={15} /> Ubicación *</span>
            <input
              value={form.ubicacion}
              onChange={(e) => setValue("ubicacion", e.target.value)}
              placeholder="Ej: pasillo principal, bodega, oficina, taller, parqueadero..."
              required
            />
          </label>

          <label className="wide">
            <span>Título del reporte *</span>
            <input
              value={form.titulo}
              onChange={(e) => setValue("titulo", e.target.value)}
              placeholder="Ej: Cable eléctrico expuesto en zona de tránsito"
              required
            />
          </label>

          <label className="wide">
            <span>Descripción *</span>
            <textarea
              value={form.descripcion}
              onChange={(e) => setValue("descripcion", e.target.value)}
              placeholder="Describe qué ocurrió, dónde ocurrió, qué personas podrían estar expuestas y cuál es la condición observada."
              required
            />
          </label>

          <label className="wide">
            <span>Acción inmediata tomada</span>
            <textarea
              value={form.accion_inmediata}
              onChange={(e) => setValue("accion_inmediata", e.target.value)}
              placeholder="Ej: Se señalizó el área y se informó al coordinador SST."
            />
          </label>

          <label className="wide">
            <span>Observaciones</span>
            <textarea
              value={form.observaciones}
              onChange={(e) => setValue("observaciones", e.target.value)}
              placeholder="Observaciones adicionales."
            />
          </label>
        </div>

        <section className="reporte-opcional">
          <h3>Datos opcionales del reportante</h3>
          <p>Puedes dejar estos campos vacíos para mantener el reporte anónimo.</p>
          <div className="reporte-form-grid three">
            <input
              value={form.nombre_reportante}
              onChange={(e) => setValue("nombre_reportante", e.target.value)}
              placeholder="Nombre opcional"
            />
            <input
              value={form.telefono_reportante}
              onChange={(e) => setValue("telefono_reportante", e.target.value)}
              placeholder="Teléfono opcional"
            />
            <input
              value={form.correo_reportante}
              onChange={(e) => setValue("correo_reportante", e.target.value)}
              placeholder="Correo opcional"
            />
          </div>
        </section>

        <label className="reporte-upload">
          <FileUp size={18} />
          <div>
            <strong>{archivos.length ? `${archivos.length} evidencia(s) seleccionada(s)` : "Adjuntar evidencias"}</strong>
            <span>PDF, JPG, PNG, WEBP, MP4 o MOV. Máximo 25 MB.</span>
          </div>
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png,.webp,.mp4,.mov"
            multiple
            onChange={(e) => setArchivos(Array.from(e.target.files || []))}
          />
        </label>

        <footer>
          <button type="button" className="secondary" onClick={limpiar} disabled={loading}>Limpiar</button>
          <button type="submit" className="primary" disabled={loading}>
            <Send size={17} /> {loading ? "Enviando..." : "Enviar reporte SST"}
          </button>
        </footer>
      </form>

      <section className="reporte-public-note">
        <LinkIcon size={18} />
        <p>
          Este formulario no solicita usuario, contraseña, empresa ni sede. Solo registra la ubicación y el área si la persona la conoce.
        </p>
      </section>
    </main>
  );
}
