// ============================================================
// COMPONENTE: HistorialFirmasPanel
// FASE 1.8.4.3.10.5 - Certificado Oficial y Firma Gerencia
// Ruta: frontend/src/components/documental/HistorialFirmasPanel.jsx
// ============================================================

import React from "react";
import {
  CalendarClock,
  Download,
  Eye,
  Fingerprint,
  Loader2,
  PenLine,
  ShieldCheck,
  UserRoundCheck,
} from "lucide-react";

function formatearFecha(fecha) {
  if (!fecha) return "Sin fecha";
  try {
    return new Intl.DateTimeFormat("es-CO", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(fecha));
  } catch {
    return fecha;
  }
}

function recortarHash(hash = "") {
  if (!hash) return "Sin hash";
  return hash.length > 28 ? `${hash.slice(0, 18)}...${hash.slice(-10)}` : hash;
}

function normalizarRol(rol = "") {
  const value = String(rol || "").toUpperCase();
  if (value === "RESPONSABLE_SST") return "Responsable SST";
  if (["GERENCIA", "GERENTE", "REPRESENTANTE_LEGAL"].includes(value)) return "Gerencia";
  if (value === "REVISOR") return "Revisor";
  return value || "Firmante";
}

function getEstadoClass(estado = "") {
  const value = String(estado || "").toLowerCase();
  if (value.includes("aprob")) return "aprobado";
  if (value.includes("rechaz")) return "rechazado";
  return "firmado";
}

export default function HistorialFirmasPanel({
  historial = [],
  onVerEvidencia,
  onCertificado,
  loadingCertificado = false,
}) {
  const firmas = Array.isArray(historial) ? historial : [];

  if (!firmas.length) {
    return (
      <div className="firma-history-premium-empty">
        <div className="firma-history-premium-empty-icon">
          <PenLine size={24} />
        </div>
        <h4>Sin firmas registradas</h4>
        <p>
          Selecciona un documento o registra una firma para visualizar la trazabilidad certificada.
        </p>
      </div>
    );
  }

  return (
    <div className="firma-history-premium-list">
      {firmas.map((item) => {
        const estadoClass = getEstadoClass(item.estado);

        return (
          <article
            className={`firma-history-premium-card ${estadoClass}`}
            key={item.id || `${item.rol_firmante}-${item.fecha_firma}`}
          >
            <div className="firma-history-premium-top">
              <div className="firma-history-premium-avatar">
                <UserRoundCheck size={22} />
              </div>

              <div className="firma-history-premium-person">
                <h4>{item.nombre_firmante || "Firmante sin nombre"}</h4>
                <p>{item.cargo_firmante || "Cargo no registrado"}</p>
              </div>

              <span className={`firma-history-premium-badge ${estadoClass}`}>
                {normalizarRol(item.rol_firmante)}
              </span>
            </div>

            <div className="firma-history-premium-grid">
              <span>
                <ShieldCheck size={14} /> {item.estado || "FIRMADO"}
              </span>
              <span>
                <CalendarClock size={14} /> {formatearFecha(item.fecha_firma || item.fecha_creacion)}
              </span>
              <span>
                <PenLine size={14} /> {item.tipo_accion || "FIRMA"}
              </span>
            </div>

            {item.observaciones && (
              <div className="firma-history-premium-note">{item.observaciones}</div>
            )}

            <div className="firma-history-premium-hash">
              <Fingerprint size={15} />
              <code title={item.hash_firma || ""}>{recortarHash(item.hash_firma)}</code>
            </div>

            <div className="firma-history-premium-actions">
              <button type="button" onClick={() => onVerEvidencia?.(item)}>
                <Eye size={15} /> Ver evidencia
              </button>

              <button
                type="button"
                className="official"
                onClick={() => onCertificado?.(item)}
                disabled={loadingCertificado}
              >
                {loadingCertificado ? <Loader2 className="spin" size={15} /> : <Download size={15} />}
                Certificado oficial
              </button>
            </div>
          </article>
        );
      })}
    </div>
  );
}
