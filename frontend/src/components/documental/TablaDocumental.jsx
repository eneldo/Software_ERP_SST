// ============================================================
// COMPONENTE: TablaDocumental
// FASE 1.8.4.3.9.2
// Tabla ejecutiva Enterprise con acciones documentales.
// ============================================================

import React from "react";
import { Download, Edit3, Eye, FileText, History, SearchX } from "lucide-react";

const formatDate = (date) => {
  if (!date) return "Sin fecha";
  return new Date(`${date}T00:00:00`).toLocaleDateString("es-CO", {
    year: "numeric",
    month: "short",
    day: "2-digit",
  });
};

const getEstadoClass = (estado = "") => {
  const e = estado.toUpperCase();
  if (e === "VIGENTE" || e === "APROBADO") return "success";
  if (e === "VENCIDO" || e === "OBSOLETO") return "danger";
  if (e === "BORRADOR") return "muted";
  return "warning";
};

export default function TablaDocumental({ documentos = [], onHistorial, onVer, onEditar }) {
  return (
    <article className="ccd-panel ccd-document-table-panel">
      <div className="ccd-panel-title">
        <div>
          <h3>Tabla documental inteligente</h3>
          <p>Inventario ejecutivo con revisión, vigencia, versión y acciones.</p>
        </div>
        <FileText size={22} />
      </div>

      {documentos.length === 0 ? (
        <div className="ccd-empty"><SearchX size={18} /> No se encontraron documentos con los filtros aplicados.</div>
      ) : (
        <div className="ccd-table-wrap enterprise">
          <table className="ccd-table ccd-document-table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Documento</th>
                <th>Categoría</th>
                <th>Versión</th>
                <th>Estado</th>
                <th>Revisión</th>
                <th>Responsable</th>
                <th>Vencimiento</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {documentos.map((doc) => (
                <tr key={doc.id}>
                  <td><strong>{doc.codigo_documental || "S/C"}</strong></td>
                  <td>
                    <div className="ccd-doc-title">
                      <strong>{doc.titulo || "Documento SST"}</strong>
                      <small>{doc.tipo_documento || "DOCUMENTO"}</small>
                    </div>
                  </td>
                  <td>{doc.categoria || "General"}</td>
                  <td><span className="ccd-pill info">v{doc.version || "1.0"}</span></td>
                  <td><span className={`ccd-pill ${getEstadoClass(doc.estado)}`}>{doc.estado || "BORRADOR"}</span></td>
                  <td><span className={`ccd-pill ${getEstadoClass(doc.estado_revision)}`}>{doc.estado_revision || "PENDIENTE"}</span></td>
                  <td>{doc.responsable || "Sin responsable"}</td>
                  <td>{formatDate(doc.fecha_vencimiento)}</td>
                  <td>
                    <div className="ccd-row-actions">
                      <button type="button" title="Ver" onClick={() => onVer?.(doc)}><Eye size={15} /></button>
                      <button type="button" title="Editar" onClick={() => onEditar?.(doc)}><Edit3 size={15} /></button>
                      <button type="button" title="Historial" onClick={() => onHistorial?.(doc)}><History size={15} /></button>
                      {doc.archivo_url ? (
                        <a title="Descargar" href={doc.archivo_url} target="_blank" rel="noreferrer"><Download size={15} /></a>
                      ) : (
                        <button type="button" title="Sin archivo" disabled><Download size={15} /></button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </article>
  );
}
