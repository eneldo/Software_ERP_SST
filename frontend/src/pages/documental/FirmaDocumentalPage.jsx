// ============================================================
// PÁGINA: FirmaDocumentalPage
// Ruta sugerida: /documental/firma-digital
// FASE 1.8.4.3.10.5 - Firma Gerencia + Certificado PDF Oficial
// ============================================================

import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  FileSignature,
  Loader2,
  RefreshCcw,
  Search,
  ShieldCheck,
} from "lucide-react";

import AdminLayout from "../../layouts/AdminLayout";
import firmaDocumentalApi from "../../api/firmaDocumentalApi";

import FirmaResumenCards from "../../components/documental/FirmaResumenCards";
import FirmaDocumentosTable from "../../components/documental/FirmaDocumentosTable";
import FirmaDocumentalModal from "../../components/documental/FirmaDocumentalModal";
import HistorialFirmasModal from "../../components/documental/HistorialFirmasModal";
import WorkflowAprobacion from "../../components/documental/WorkflowAprobacion";
import WorkflowAprobacionVisual from "../../components/documental/WorkflowAprobacionVisual";
import TimelineFirmaDigital from "../../components/documental/TimelineFirmaDigital";
import HistorialFirmasPanel from "../../components/documental/HistorialFirmasPanel";
import EvidenciaFirmaModal from "../../components/documental/EvidenciaFirmaModal";
import CertificadoFirmaModal from "../../components/documental/CertificadoFirmaModal";

import "../../styles/documental/firma-documental.css";
import "../../styles/documental/firma-certificado-oficial.css";
import "../../styles/documental/firma-certificado-oficial.css";

function getEmpresaIdFromStorage() {
  try {
    const rawUser = localStorage.getItem("user");
    const user = rawUser ? JSON.parse(rawUser) : null;
    return user?.empresa_id || localStorage.getItem("empresa_id") || "";
  } catch {
    return localStorage.getItem("empresa_id") || "";
  }
}

export default function FirmaDocumentalPage() {
  const [empresaId, setEmpresaId] = useState(getEmpresaIdFromStorage());
  const [estadoRevision, setEstadoRevision] = useState("");
  const [busqueda, setBusqueda] = useState("");

  const [resumen, setResumen] = useState({});
  const [documentos, setDocumentos] = useState([]);
  const [documentoSeleccionado, setDocumentoSeleccionado] = useState(null);
  const [historial, setHistorial] = useState([]);

  const [loading, setLoading] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  const [modalFirmaOpen, setModalFirmaOpen] = useState(false);
  const [modalHistorialOpen, setModalHistorialOpen] = useState(false);
  const [evidenciaSeleccionada, setEvidenciaSeleccionada] = useState(null);
  const [certificadoSeleccionado, setCertificadoSeleccionado] = useState(null);
  const [cargandoCertificado, setCargandoCertificado] = useState(false);

  const params = useMemo(() => {
    const query = {};
    if (empresaId) query.empresa_id = empresaId;
    if (estadoRevision) query.estado_revision = estadoRevision;
    return query;
  }, [empresaId, estadoRevision]);

  const cargarDatos = useCallback(async () => {
    setLoading(true);
    setError("");
    setMensaje("");

    try {
      const [resumenResp, documentosResp] = await Promise.all([
        firmaDocumentalApi.resumen(empresaId ? { empresa_id: empresaId } : {}),
        firmaDocumentalApi.documentos(params),
      ]);

      setResumen(resumenResp.data || {});
      setDocumentos(Array.isArray(documentosResp.data) ? documentosResp.data : []);
    } catch (err) {
      console.error(err);
      setError("No fue posible cargar el módulo de firma documental.");
    } finally {
      setLoading(false);
    }
  }, [empresaId, params]);

  useEffect(() => {
    cargarDatos();
  }, [cargarDatos]);

  const documentosFiltrados = useMemo(() => {
    const term = busqueda.trim().toLowerCase();
    if (!term) return documentos;

    return documentos.filter((doc) => {
      const values = [
        doc.codigo_documental,
        doc.codigo,
        doc.titulo,
        doc.categoria,
        doc.responsable,
        doc.estado,
        doc.estado_revision,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return values.includes(term);
    });
  }, [busqueda, documentos]);

  const abrirFirma = (doc) => {
    setDocumentoSeleccionado(doc);
    setModalFirmaOpen(true);
  };

  const cargarHistorialDocumento = async (doc) => {
    if (!doc?.id) return [];

    try {
      const resp = await firmaDocumentalApi.historial(doc.id);

      // El backend puede responder como arreglo o como objeto:
      // { documento_id, total, firmas: [...] }
      const data = Array.isArray(resp.data)
        ? resp.data
        : Array.isArray(resp.data?.firmas)
          ? resp.data.firmas
          : [];

      setHistorial(data);
      return data;
    } catch (err) {
      console.error(err);
      setError("No fue posible cargar el historial de firmas.");
      return [];
    }
  };

  const abrirHistorial = async (doc) => {
    setDocumentoSeleccionado(doc);
    setModalHistorialOpen(true);
    setHistorial([]);
    await cargarHistorialDocumento(doc);
  };

  const registrarFirma = async (payload) => {
    setGuardando(true);
    setError("");
    setMensaje("");

    try {
      await firmaDocumentalApi.firmar(payload);
      setMensaje("Firma registrada correctamente.");
      setModalFirmaOpen(false);
      await cargarDatos();
    } catch (err) {
      console.error(err);
      setError("No fue posible registrar la firma. Verifica los campos obligatorios.");
    } finally {
      setGuardando(false);
    }
  };

  const aprobarDocumento = async (doc) => {
    const confirmar = window.confirm(`¿Deseas aprobar el documento ${doc.codigo_documental || doc.codigo}?`);
    if (!confirmar) return;

    setGuardando(true);
    setError("");
    setMensaje("");

    try {
      await firmaDocumentalApi.aprobar(doc.id, {
        observaciones: "Documento aprobado desde el Centro de Firma Digital SST.",
      });
      setMensaje("Documento aprobado correctamente.");
      await cargarDatos();
    } catch (err) {
      console.error(err);
      setError("No fue posible aprobar el documento.");
    } finally {
      setGuardando(false);
    }
  };

  const rechazarDocumento = async (doc) => {
    const observaciones = window.prompt(
      `Motivo de rechazo para ${doc.codigo_documental || doc.codigo}:`,
      "Requiere ajustes antes de aprobación."
    );

    if (observaciones === null) return;

    setGuardando(true);
    setError("");
    setMensaje("");

    try {
      await firmaDocumentalApi.rechazar(doc.id, { observaciones });
      setMensaje("Documento rechazado correctamente.");
      await cargarDatos();
    } catch (err) {
      console.error(err);
      setError("No fue posible rechazar el documento.");
    } finally {
      setGuardando(false);
    }
  };

  const verDocumento = async (doc) => {
    setDocumentoSeleccionado(doc);
    setMensaje(`Documento seleccionado: ${doc.titulo}`);
    setHistorial([]);
    await cargarHistorialDocumento(doc);
  };


  const abrirCertificado = async (firma) => {
    if (!firma?.id) {
      setError("No fue posible identificar la firma para generar el certificado.");
      return;
    }

    setCargandoCertificado(true);
    setError("");

    try {
      const resp = await firmaDocumentalApi.certificado(firma.id);
      setCertificadoSeleccionado(resp.data || null);
    } catch (err) {
      console.error(err);
      setError("No fue posible generar el certificado oficial de firma.");
    } finally {
      setCargandoCertificado(false);
    }
  };

  const documentoActivo = documentoSeleccionado || documentosFiltrados[0] || null;

  useEffect(() => {
    if (documentoActivo?.id) {
      cargarHistorialDocumento(documentoActivo);
    }
  }, [documentoActivo?.id]);

  return (
    
      <main className="firma-page">
        <section className="firma-hero">
          <div className="firma-hero-copy">
            <span className="firma-badge-hero">GERENCIA + CERTIFICADO OFICIAL</span>
            <h1>Firma Electrónica y Aprobación Digital SST</h1>
            <p>
              Centro de gobierno documental para firmar, aprobar, rechazar y auditar
              documentos del SG-SST con trazabilidad completa.
            </p>
          </div>

          <div className="firma-hero-actions">
            <input
              value={empresaId}
              onChange={(e) => setEmpresaId(e.target.value)}
              placeholder="Empresa ID"
            />

            <select value={estadoRevision} onChange={(e) => setEstadoRevision(e.target.value)}>
              <option value="">Todos los estados</option>
              <option value="PENDIENTE">Pendiente</option>
              <option value="APROBADO">Aprobado</option>
              <option value="RECHAZADO">Rechazado</option>
            </select>

            <button onClick={cargarDatos} disabled={loading || guardando}>
              {loading ? <Loader2 className="spin" size={18} /> : <RefreshCcw size={18} />}
              Actualizar
            </button>
          </div>
        </section>

        {error && (
          <div className="firma-alert error">
            <AlertTriangle size={18} />
            {error}
          </div>
        )}

        {mensaje && (
          <div className="firma-alert success">
            <CheckCircle2 size={18} />
            {mensaje}
          </div>
        )}

        <FirmaResumenCards resumen={resumen} />

        <section className="firma-toolbar">
          <div className="firma-search-box">
            <Search size={18} />
            <input
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Buscar por código, título, responsable, estado..."
            />
          </div>

          <div className="firma-toolbar-status">
            <FileSignature size={17} />
            Documentos visibles: <strong>{documentosFiltrados.length}</strong>
          </div>
        </section>

        {documentoActivo && (
          <section className="firma-panel firma-workflow-enterprise-panel">
            <div className="firma-panel-title">
              <div>
                <h3>Workflow visual de aprobación digital</h3>
                <p>
                  {documentoActivo.codigo_documental || documentoActivo.codigo} · {documentoActivo.titulo}
                </p>
              </div>
              <ShieldCheck size={22} />
            </div>

            <WorkflowAprobacionVisual documento={documentoActivo} />
          </section>
        )}

        {documentoActivo && (
          <section className="firma-executive-grid">
            <div className="firma-panel">
              <div className="firma-panel-title">
                <div>
                  <h3>Timeline de aprobación digital</h3>
                  <p>Creación, revisión, firma SST, gerencia y vigencia documental.</p>
                </div>
                <FileSignature size={22} />
              </div>

              <TimelineFirmaDigital documento={documentoActivo} historial={historial} />
            </div>

            <div className="firma-panel">
              <div className="firma-panel-title">
                <div>
                  <h3>Trazabilidad de firmas</h3>
                  <p>Historial auditable del documento seleccionado.</p>
                </div>
                <ShieldCheck size={22} />
              </div>

              <HistorialFirmasPanel
                historial={historial}
                onVerEvidencia={(firma) => setEvidenciaSeleccionada(firma)}
                onCertificado={(firma) => abrirCertificado(firma)}
                loadingCertificado={cargandoCertificado}
              />
            </div>
          </section>
        )}

        <FirmaDocumentosTable
          documentos={documentosFiltrados}
          onFirmar={abrirFirma}
          onHistorial={abrirHistorial}
          onAprobar={aprobarDocumento}
          onRechazar={rechazarDocumento}
          onVer={verDocumento}
        />

        <FirmaDocumentalModal
          open={modalFirmaOpen}
          documento={documentoSeleccionado}
          onClose={() => setModalFirmaOpen(false)}
          onSubmit={registrarFirma}
          loading={guardando}
        />

        <HistorialFirmasModal
          open={modalHistorialOpen}
          documento={documentoSeleccionado}
          historial={historial}
          onClose={() => setModalHistorialOpen(false)}
        />

        <EvidenciaFirmaModal
          open={Boolean(evidenciaSeleccionada)}
          firma={evidenciaSeleccionada}
          onClose={() => setEvidenciaSeleccionada(null)}
        />

        <CertificadoFirmaModal
          open={Boolean(certificadoSeleccionado)}
          certificado={certificadoSeleccionado}
          onClose={() => setCertificadoSeleccionado(null)}
        />
      </main>
    
  );
}
