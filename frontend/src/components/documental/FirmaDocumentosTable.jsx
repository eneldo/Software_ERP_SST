// ============================================================
// COMPONENTE: FirmaDocumentosTable
// Tabla enterprise para firma, aprobación, rechazo e historial.
// ============================================================

import React from "react";
import { CheckCheck, Eye, History, PenLine, ShieldCheck, XCircle } from "lucide-react";
import EstadoFirmaBadge from "./EstadoFirmaBadge";

function formatDate(value) {
  if (!value) return "Sin fecha";
  return new Date(value).toLocaleDateString("es-CO", {
    year: "numeric",
    month: "short",
    day: "2-digit",
  });
}

export default function FirmaDocumentosTable({
  documentos = [],
  onFirmar,
  onHistorial,
  onAprobar,
  onRechazar,
  onVer,
}) {
  return (
    <section className="firma-panel firma-table-panel">
      <div className="firma-panel-title">
        <div>
          <h3>Documentos para firma y aprobación</h3>
          <p>Control ejecutivo de firmas, aprobaciones y trazabilidad documental SST.</p>
        </div>
      </div>

      <div className="firma-table-wrapper">
        <table className="firma-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Documento</th>
              <th>Versión</th>
              <th>Estado</th>
              <th>Firma SST</th>
              <th>Gerencia</th>
              <th>Responsable</th>
              <th>Vencimiento</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            {documentos.length === 0 ? (
              <tr>
                <td colSpan="9" className="firma-table-empty">
                  No hay documentos disponibles para firma.
                </td>
              </tr>
            ) : (
              documentos.map((doc) => (
                <tr key={doc.id}>
                  <td>
                    <strong>{doc.codigo_documental || doc.codigo}</strong>
                  </td>
                  <td>
                    <div className="firma-doc-title">
                      <strong>{doc.titulo}</strong>
                      <small>{doc.categoria || "Sin categoría"}</small>
                    </div>
                  </td>
                  <td>{doc.version || "1.0"}</td>
                  <td><EstadoFirmaBadge estado={doc.estado_revision || doc.estado || "PENDIENTE"} /></td>
                  <td>{doc.firmado_responsable_sst ? "Sí" : "No"}</td>
                  <td>{doc.firmado_gerencia ? "Sí" : "No"}</td>
                  <td>{doc.responsable || "Sin responsable"}</td>
                  <td>{formatDate(doc.fecha_vencimiento)}</td>
                  <td>
                    <div className="firma-action-group">
                      <button title="Ver" onClick={() => onVer?.(doc)}><Eye size={15} /></button>
                      <button title="Firmar" onClick={() => onFirmar?.(doc)}><PenLine size={15} /></button>
                      <button title="Historial" onClick={() => onHistorial?.(doc)}><History size={15} /></button>
                      <button title="Aprobar" onClick={() => onAprobar?.(doc)}><ShieldCheck size={15} /></button>
                      <button title="Rechazar" onClick={() => onRechazar?.(doc)}><XCircle size={15} /></button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
