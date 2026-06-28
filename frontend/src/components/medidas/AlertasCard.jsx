// ============================================================
// ALERTAS CARD — MEDIDAS CORRECTIVAS ENTERPRISE
// ERP SST PRO
// FASE 1.1.8.7.4
// Archivo: frontend/src/components/medidas/AlertasCard.jsx
// ============================================================

import { AlertTriangle, Archive, BellRing, CheckCircle2, RefreshCcw } from "lucide-react";

function prioridadClass(value) {
  const v = String(value || "").toUpperCase();
  if (v === "CRITICA" || v === "CRÍTICA") return "critica";
  if (v === "ALTA") return "alta";
  if (v === "MEDIA") return "media";
  return "baja";
}

export default function AlertasCard({ data, loading, onRefresh, onRead, onArchive }) {
  const resumen = data?.resumen || {};
  const alertas = data?.alertas || [];

  return (
    <section className="mc-enterprise-card mc-alertas-card">
      <div className="mc-enterprise-card-header">
        <div>
          <span>Alertas inteligentes</span>
          <h3>{resumen.total || 0} alerta(s)</h3>
        </div>
        <button className="mc-icon-btn" type="button" onClick={onRefresh} disabled={loading}>
          <RefreshCcw size={16} />
        </button>
      </div>

      <div className="mc-alert-kpis">
        <span><BellRing size={15} /> Pendientes: {resumen.pendientes || 0}</span>
        <span><AlertTriangle size={15} /> Críticas: {resumen.criticas || 0}</span>
        <span><CheckCircle2 size={15} /> Altas: {resumen.altas || 0}</span>
      </div>

      <div className="mc-alert-list">
        {alertas.map((alerta) => (
          <article key={alerta.id} className={`mc-alert-item ${prioridadClass(alerta.prioridad)} ${alerta.leida ? "read" : ""}`}>
            <div>
              <strong>{alerta.titulo}</strong>
              <p>{alerta.mensaje}</p>
              <small>{alerta.capa_codigo} · {alerta.tipo_alerta} · {alerta.prioridad}</small>
            </div>
            <div className="mc-alert-actions">
              {!alerta.leida && (
                <button type="button" onClick={() => onRead?.(alerta.id)} title="Marcar como leída">
                  <CheckCircle2 size={15} />
                </button>
              )}
              <button type="button" onClick={() => onArchive?.(alerta.id)} title="Archivar">
                <Archive size={15} />
              </button>
            </div>
          </article>
        ))}

        {!alertas.length && <div className="mc-empty-alerts">No hay alertas pendientes.</div>}
      </div>
    </section>
  );
}
