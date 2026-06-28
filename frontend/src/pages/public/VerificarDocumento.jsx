// ============================================================
// PORTAL PÚBLICO DE VERIFICACIÓN DOCUMENTAL SST
// FASE 1.7.4.2.5.3
// Archivo: frontend/src/pages/public/VerificarDocumento.jsx
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

import {
  AlertTriangle,
  Building2,
  CalendarClock,
  CheckCircle2,
  Download,
  FileCheck2,
  FileSearch,
  Fingerprint,
  Hash,
  QrCode,
  Search,
  ShieldCheck,
  Upload,
  XCircle,
} from "lucide-react";

import "../../styles/verificacion-documental.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function VerificarDocumento() {
  const { codigo } = useParams();

  const [codigoValidacion, setCodigoValidacion] = useState(codigo || "");
  const [documento, setDocumento] = useState(null);
  const [archivo, setArchivo] = useState(null);
  const [verificacionArchivo, setVerificacionArchivo] = useState(null);

  const [loading, setLoading] = useState(false);
  const [subiendo, setSubiendo] = useState(false);
  const [error, setError] = useState("");

  const documentoValido = documento?.estado === "VALIDO";

  const logoUrl = useMemo(() => {
    if (!documento?.empresa_logo) return null;

    if (
      documento.empresa_logo.startsWith("http://") ||
      documento.empresa_logo.startsWith("https://")
    ) {
      return documento.empresa_logo;
    }

    return `${API_URL}${documento.empresa_logo}`;
  }, [documento]);

  const urlValidacion = useMemo(() => {
    if (!documento?.codigo_validacion) return "";
    return `${window.location.origin}/verificar-documento/${documento.codigo_validacion}`;
  }, [documento]);

  const qrUrl = useMemo(() => {
    if (!urlValidacion) return "";
    return `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(
      urlValidacion
    )}`;
  }, [urlValidacion]);

  const verificarCodigo = async (codigoBuscar = codigoValidacion) => {
    const codigoLimpio = String(codigoBuscar || "").trim();

    if (!codigoLimpio) {
      setError("Ingrese un código de validación.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setDocumento(null);
      setVerificacionArchivo(null);

      const res = await axios.get(
        `${API_URL}/validar/documento/${encodeURIComponent(codigoLimpio)}`
      );

      setDocumento(res.data);
      setCodigoValidacion(codigoLimpio);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "No se encontró un documento con este código de validación."
      );
    } finally {
      setLoading(false);
    }
  };

  const verificarArchivo = async () => {
    if (!documento?.codigo_validacion) {
      setError("Primero valide el código del documento.");
      return;
    }

    if (!archivo) {
      setError("Seleccione el archivo PDF que desea verificar.");
      return;
    }

    try {
      setSubiendo(true);
      setError("");
      setVerificacionArchivo(null);

      const formData = new FormData();
      formData.append("file", archivo);

      const res = await axios.post(
        `${API_URL}/validar/documento/${encodeURIComponent(
          documento.codigo_validacion
        )}/verificar-archivo`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setVerificacionArchivo(res.data);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "No fue posible verificar el archivo seleccionado."
      );
    } finally {
      setSubiendo(false);
    }
  };

  const descargarPDF = () => {
    if (!documento?.url_archivo) return;

    const url = documento.url_archivo.startsWith("http")
      ? documento.url_archivo
      : `${API_URL}${documento.url_archivo}`;

    window.open(url, "_blank");
  };

  const copiarCodigo = async () => {
    if (!documento?.codigo_validacion) return;

    try {
      await navigator.clipboard.writeText(documento.codigo_validacion);
      alert("Código copiado al portapapeles.");
    } catch {
      alert("No fue posible copiar el código.");
    }
  };

  useEffect(() => {
    if (codigo) {
      verificarCodigo(codigo);
    }
  }, [codigo]);

  return (
    <main className="vd-page">
      <section className="vd-card">
        <header className="vd-header">
          <div className="vd-brand">
            {logoUrl ? (
              <img src={logoUrl} alt="Logo empresa" />
            ) : (
              <div className="vd-logo-fallback">
                <ShieldCheck size={34} />
              </div>
            )}

            <div>
              <span>ERP SST PRO</span>
              <h1>Verificación Documental SST</h1>
              <p>
                Portal público para consultar autenticidad, trazabilidad,
                estado y huella digital SHA256 de documentos generados.
              </p>
            </div>
          </div>

          <div className={`vd-status-pill ${documentoValido ? "ok" : "neutral"}`}>
            <ShieldCheck size={18} />
            {documento ? documento.estado : "Sin validar"}
          </div>
        </header>

        <section className="vd-search">
          <label>Código único de validación</label>

          <div className="vd-search-row">
            <input
              value={codigoValidacion}
              onChange={(e) => setCodigoValidacion(e.target.value)}
              placeholder="Ej: VAL-AUDITORIA_SST-000001-20260603-16C069F9"
            />

            <button type="button" onClick={() => verificarCodigo()}>
              <Search size={18} />
              {loading ? "Verificando..." : "Verificar"}
            </button>
          </div>
        </section>

        {error && (
          <div className="vd-alert error">
            <AlertTriangle size={19} />
            <span>{error}</span>
          </div>
        )}

        {documento && (
          <section className={`vd-result ${documentoValido ? "ok" : "bad"}`}>
            <div className="vd-result-main">
              <div className="vd-result-title">
                {documentoValido ? (
                  <CheckCircle2 size={34} />
                ) : (
                  <XCircle size={34} />
                )}

                <div>
                  <h2>
                    {documentoValido
                      ? "Documento válido"
                      : "Documento no válido"}
                  </h2>
                  <p>
                    Registro encontrado en la base documental del ERP SST PRO.
                  </p>
                </div>
              </div>

              <div className="vd-company-card">
                <div>
                  <Building2 size={22} />
                </div>

                <div>
                  <span>Empresa</span>
                  <strong>
                    {documento.empresa_nombre || "Empresa no registrada"}
                  </strong>
                  <small>NIT: {documento.empresa_nit || "No registrado"}</small>
                </div>
              </div>
            </div>

            <aside className="vd-qr-panel">
              <img src={qrUrl} alt="QR de validación" />
              <span>QR de validación</span>
            </aside>

            <div className="vd-grid">
              <article className="wide">
                <span>
                  <Fingerprint size={15} />
                  Código validación
                </span>
                <strong>{documento.codigo_validacion}</strong>
              </article>

              <article>
                <span>
                  <FileSearch size={15} />
                  Tipo documento
                </span>
                <strong>{documento.tipo_documento}</strong>
              </article>

              <article>
                <span>Referencia</span>
                <strong>{documento.referencia_id}</strong>
              </article>

              <article>
                <span>Estado</span>
                <strong className={documentoValido ? "state-ok" : "state-bad"}>
                  {documento.estado}
                </strong>
              </article>

              <article>
                <span>
                  <CalendarClock size={15} />
                  Fecha generación
                </span>
                <strong>
                  {documento.fecha_generacion
                    ? new Date(documento.fecha_generacion).toLocaleString()
                    : "Sin fecha"}
                </strong>
              </article>

              <article className="wide">
                <span>
                  <Hash size={15} />
                  Hash SHA256
                </span>
                <strong className="hash-text">{documento.hash_sha256}</strong>
              </article>

              <article className="wide">
                <span>Observación</span>
                <strong>{documento.observacion || "Sin observación"}</strong>
              </article>
            </div>

            <div className="vd-actions">
              <button type="button" onClick={copiarCodigo}>
                <QrCode size={18} />
                Copiar código
              </button>

              <button
                type="button"
                onClick={descargarPDF}
                disabled={!documento.url_archivo}
                title={
                  documento.url_archivo
                    ? "Descargar PDF original"
                    : "PDF original no almacenado todavía"
                }
              >
                <Download size={18} />
                Descargar PDF
              </button>
            </div>

            <section className="vd-file-check">
              <h3>
                <FileCheck2 size={21} />
                Verificar archivo PDF
              </h3>

              <p>
                Suba el PDF para comparar su huella SHA256 contra el registro
                oficial. Si coincide, el archivo no ha sido alterado.
              </p>

              <div className="vd-upload-row">
                <input
                  type="file"
                  accept="application/pdf"
                  onChange={(e) => setArchivo(e.target.files?.[0] || null)}
                />

                <button type="button" onClick={verificarArchivo}>
                  <Upload size={18} />
                  {subiendo ? "Verificando..." : "Verificar PDF"}
                </button>
              </div>

              {verificacionArchivo && (
                <div
                  className={`vd-alert ${
                    verificacionArchivo.coincide ? "success" : "error"
                  }`}
                >
                  {verificacionArchivo.coincide ? (
                    <CheckCircle2 size={20} />
                  ) : (
                    <XCircle size={20} />
                  )}

                  <span>
                    {verificacionArchivo.coincide
                      ? "El archivo coincide con el documento original registrado."
                      : "El archivo NO coincide. Puede haber sido modificado."}
                  </span>
                </div>
              )}
            </section>
          </section>
        )}

        <footer className="vd-footer">
          <p>
            ERP SST PRO · Validación documental con SHA256, QR y trazabilidad.
          </p>
        </footer>
      </section>
    </main>
  );
}