// ============================================================
// COMPONENTE: ModalEvidenciaFirma
// FASE 1.8.4.3.10.4 - Evidencia certificada de firma digital
// Ruta: frontend/src/components/documental/ModalEvidenciaFirma.jsx
// ============================================================

import React from "react";
import {
  BadgeCheck,
  CalendarClock,
  Download,
  Fingerprint,
  Globe2,
  MonitorSmartphone,
  ShieldCheck,
  UserRoundCheck,
  X,
} from "lucide-react";

function formatearFecha(fecha) {
  if (!fecha) return "Sin fecha";
  try {
    return new Intl.DateTimeFormat("es-CO", {
      day: "2-digit",
      month: "long",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(fecha));
  } catch {
    return fecha;
  }
}

function safe(valor, fallback = "No registrado") {
  return valor || fallback;
}

export default function ModalEvidenciaFirma({ open, firma, documento, onClose, onCertificado }) {
  if (!open || !firma) return null;

  const codigo = documento?.codigo_documental || documento?.codigo || firma.codigo_documental || `DOC-${firma.documento_id}`;
  const titulo = documento?.titulo || firma.titulo || "Documento SST";

  return (
    <div className="firma-modal-backdrop" role="dialog" aria-modal="true">
      <div className="firma-modal firma-evidence-modal">
        <header className="firma-modal-header">
          <div>
            <span>evidencia certificada</span>
            <h2>Constancia de firma digital SST</h2>
            <p>{codigo} · {titulo}</p>
          </div>

          <button className="firma-icon-button" type="button" onClick={onClose} title="Cerrar">
            <X size={18} />
          </button>
        </header>

        <section className="firma-evidence-hero">
          <div className="firma-evidence-seal">
            <ShieldCheck size={36} />
          </div>
          <div>
            <h3>Firma verificada en el ERP SST PRO</h3>
            <p>
              Esta evidencia registra el acto documental realizado, el rol del firmante,
              la fecha, la trazabilidad técnica y el hash SHA-256 asociado.
            </p>
          </div>
          <strong>{safe(firma.estado, "FIRMADO")}</strong>
        </section>

        <section className="firma-evidence-grid">
          <article>
            <UserRoundCheck size={18} />
            <span>Firmante</span>
            <strong>{safe(firma.nombre_firmante)}</strong>
            <small>{safe(firma.cargo_firmante)}</small>
          </article>

          <article>
            <BadgeCheck size={18} />
            <span>Rol / Acción</span>
            <strong>{safe(firma.rol_firmante)}</strong>
            <small>{safe(firma.tipo_accion)}</small>
          </article>

          <article>
            <CalendarClock size={18} />
            <span>Fecha firma</span>
            <strong>{formatearFecha(firma.fecha_firma || firma.fecha_creacion)}</strong>
            <small>Registro auditable</small>
          </article>

          <article>
            <Globe2 size={18} />
            <span>IP origen</span>
            <strong>{safe(firma.ip_origen)}</strong>
            <small>Origen técnico</small>
          </article>
        </section>

        <section className="firma-evidence-section">
          <h4><MonitorSmartphone size={17} /> Navegador / dispositivo</h4>
          <p>{safe(firma.user_agent)}</p>
        </section>

        {(firma.observaciones || firma.motivo_rechazo) && (
          <section className="firma-evidence-section">
            <h4><BadgeCheck size={17} /> Observaciones</h4>
            <p>{firma.observaciones || firma.motivo_rechazo}</p>
          </section>
        )}

        <section className="firma-evidence-section firma-evidence-hash-box">
          <h4><Fingerprint size={17} /> Hash SHA-256</h4>
          <code>{safe(firma.hash_firma, "Sin hash registrado")}</code>
        </section>

        <footer className="firma-evidence-actions">
          <button className="firma-btn secondary" type="button" onClick={onClose}>Cerrar</button>
          <button className="firma-btn primary" type="button" onClick={() => onCertificado?.(firma)}>
            <Download size={17} /> Descargar certificado
          </button>
        </footer>
      </div>
    </div>
  );
}
