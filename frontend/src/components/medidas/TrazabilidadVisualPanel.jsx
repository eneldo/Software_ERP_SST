// ============================================================
// TRAZABILIDAD VISUAL - TIMELINE CORPORATIVO VERTICAL
// ERP SST PRO
// FASE 1.1.8.7.5.2
// Archivo: frontend/src/components/medidas/TrazabilidadVisualPanel.jsx
// ============================================================

import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  PlusCircle,
  ShieldCheck,
  UserRound,
} from "lucide-react";

import "../../styles/medidas-timeline-enterprise.css";

function getIcon(icon, tipo) {
  const key = String(icon || tipo || "").toLowerCase();

  if (key.includes("check") || key.includes("cierre")) return <CheckCircle2 size={18} />;
  if (key.includes("clipboard") || key.includes("inspeccion")) return <ClipboardCheck size={18} />;
  if (key.includes("alert") || key.includes("hallazgo")) return <AlertTriangle size={18} />;
  if (key.includes("shield") || key.includes("eficacia")) return <ShieldCheck size={18} />;
  if (key.includes("activity") || key.includes("seguimiento")) return <Activity size={18} />;

  return <PlusCircle size={18} />;
}

function colorClass(value, tipo) {
  const raw = String(value || tipo || "").toLowerCase();

  if (raw.includes("green") || raw.includes("cierre") || raw.includes("cerrada")) return "green";
  if (raw.includes("red") || raw.includes("vencida") || raw.includes("no_efectiva")) return "red";
  if (raw.includes("orange") || raw.includes("hallazgo") || raw.includes("alert")) return "orange";
  if (raw.includes("indigo") || raw.includes("inspeccion")) return "indigo";
  if (raw.includes("yellow") || raw.includes("eficacia")) return "yellow";
  if (raw.includes("purple") || raw.includes("verificacion")) return "purple";

  return "blue";
}

function formatDate(value) {
  if (!value) return "Sin fecha";

  try {
    return new Date(value).toLocaleString("es-CO", {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return String(value);
  }
}

function timeAgo(value) {
  if (!value) return "";

  try {
    const date = new Date(value);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return "Hace unos segundos";

    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `Hace ${minutes} min`;

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `Hace ${hours} h`;

    const days = Math.floor(hours / 24);
    if (days < 30) return `Hace ${days} día(s)`;

    const months = Math.floor(days / 30);
    if (months < 12) return `Hace ${months} mes(es)`;

    const years = Math.floor(months / 12);
    return `Hace ${years} año(s)`;
  } catch {
    return "";
  }
}

function EstadoBadge({ value }) {
  if (!value) return null;

  const cls = colorClass(value, value);

  return (
    <span className={`mct-status ${cls}`}>
      {String(value).replaceAll("_", " ")}
    </span>
  );
}

function TimelineItem({ evento, isLast }) {
  const cls = colorClass(evento?.color, evento?.tipo);

  return (
    <article className={`mct-item ${cls} ${isLast ? "last" : ""}`}>
      <div className="mct-axis">
        <div className="mct-dot">{getIcon(evento?.icono, evento?.tipo)}</div>
        {!isLast && <div className="mct-line" />}
      </div>

      <div className="mct-content">
        <div className="mct-top">
          <div>
            <h4>{evento?.titulo || "Evento SST"}</h4>
            <div className="mct-meta">
              <Clock3 size={14} />
              <span>{formatDate(evento?.fecha)}</span>
              {evento?.fecha && <strong>{timeAgo(evento.fecha)}</strong>}
            </div>
          </div>

          <EstadoBadge value={evento?.estado || evento?.tipo} />
        </div>

        <p>{evento?.descripcion || "Sin descripción registrada."}</p>

        {(evento?.usuario || evento?.tipo) && (
          <div className="mct-footer">
            {evento?.usuario && (
              <span>
                <UserRound size={14} />
                {evento.usuario}
              </span>
            )}

            {evento?.tipo && (
              <span className="mct-type">
                {evento.tipo.replaceAll("_", " ")}
              </span>
            )}
          </div>
        )}
      </div>
    </article>
  );
}

export default function TrazabilidadVisualPanel({ data }) {
  const eventos = data?.trazabilidad_visual || [];

  const ordenados = [...eventos].sort((a, b) => {
    const ordenA = Number(a?.orden || 0);
    const ordenB = Number(b?.orden || 0);
    return ordenA - ordenB;
  });

  return (
    <section className="mct-card">
      <div className="mct-header">
        <div>
          <span>Timeline corporativo SST</span>
          <h3>Trazabilidad visual</h3>
          <p>Ciclo de vida documentado de la medida correctiva.</p>
        </div>

        <strong>{ordenados.length} evento(s)</strong>
      </div>

      <div className="mct-timeline">
        {ordenados.map((evento, index) => (
          <TimelineItem
            key={`${evento?.orden || index}-${evento?.tipo || "evento"}`}
            evento={evento}
            isLast={index === ordenados.length - 1}
          />
        ))}

        {!ordenados.length && (
          <div className="mct-empty">
            No hay trazabilidad visual disponible para esta medida.
          </div>
        )}
      </div>
    </section>
  );
}
