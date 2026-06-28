// ============================================================
// COMPONENTE: EvidenciaFirmaModal
// FASE 1.8.4.3.10.4.1 - Evidencia Visual PRO
// Ruta: frontend/src/components/documental/EvidenciaFirmaModal.jsx
// ============================================================

import React from "react";
import { Fingerprint, MonitorSmartphone, ShieldCheck, X } from "lucide-react";

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

export default function EvidenciaFirmaModal({ open, firma, onClose }) {
  if (!open || !firma) return null;

  return (
    <div className="firma-evidencia-backdrop" role="dialog" aria-modal="true">
      <section className="firma-evidencia-modal">
        <header className="firma-evidencia-header">
          <div>
            <span>Certificación documental SST</span>
            <h2>Evidencia de firma digital</h2>
            <p>Registro auditable para trazabilidad de aprobación documental.</p>
          </div>
          <button type="button" onClick={onClose} aria-label="Cerrar">
            <X size={20} />
          </button>
        </header>

        <div className="firma-evidencia-body">
          <div className="firma-evidencia-seal">
            <ShieldCheck size={42} />
            <strong>{firma.estado || "FIRMADO"}</strong>
            <small>{firma.tipo_accion || "FIRMA"}</small>
          </div>

          <div className="firma-evidencia-grid">
            <div>
              <label>Firmante</label>
              <strong>{firma.nombre_firmante || "No registrado"}</strong>
            </div>
            <div>
              <label>Cargo</label>
              <strong>{firma.cargo_firmante || "No registrado"}</strong>
            </div>
            <div>
              <label>Rol</label>
              <strong>{firma.rol_firmante || "FIRMANTE"}</strong>
            </div>
            <div>
              <label>Fecha</label>
              <strong>{formatearFecha(firma.fecha_firma || firma.fecha_creacion)}</strong>
            </div>
          </div>

          <div className="firma-evidencia-tech">
            <h3><Fingerprint size={18} /> Hash SHA256</h3>
            <code>{firma.hash_firma || "Sin hash registrado"}</code>
          </div>

          <div className="firma-evidencia-tech muted">
            <h3><MonitorSmartphone size={18} /> Origen técnico</h3>
            <p>IP: {firma.ip_origen || "No registrada"}</p>
            <p>User Agent: {firma.user_agent || "No registrado"}</p>
          </div>

          {firma.observaciones && (
            <div className="firma-evidencia-note">
              <label>Observaciones</label>
              <p>{firma.observaciones}</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
