// ============================================================
// COMPONENTE: TimelineFirmaDigital
// FASE 1.8.4.3.10.4.1 - Timeline Premium
// Ruta: frontend/src/components/documental/TimelineFirmaDigital.jsx
// ============================================================

import React from "react";
import {
  CalendarClock,
  CheckCircle2,
  Clock3,
  FileText,
  PenLine,
  ShieldCheck,
} from "lucide-react";

function formatearFecha(fecha) {
  if (!fecha) return "Pendiente";
  try {
    return new Intl.DateTimeFormat("es-CO", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: String(fecha).includes("T") ? "2-digit" : undefined,
      minute: String(fecha).includes("T") ? "2-digit" : undefined,
    }).format(new Date(fecha));
  } catch {
    return fecha;
  }
}

function normalizar(valor = "") {
  return String(valor || "").trim().toUpperCase();
}

export default function TimelineFirmaDigital({ documento = {}, historial = [] }) {
  const firmas = Array.isArray(historial) ? historial : [];

  const firmaSst = firmas.find((item) => normalizar(item.rol_firmante) === "RESPONSABLE_SST");
  const firmaGerencia = firmas.find((item) =>
    ["GERENCIA", "GERENTE", "REPRESENTANTE_LEGAL"].includes(normalizar(item.rol_firmante))
  );

  const revisionAprobada = ["APROBADO", "EN_REVISION", "RECHAZADO"].includes(
    normalizar(documento.estado_revision)
  );

  const eventos = [
    {
      title: "Documento creado",
      description: documento.codigo_documental || documento.codigo || "Registro documental SG-SST",
      date: documento.fecha_creacion,
      complete: true,
      icon: FileText,
    },
    {
      title: "Revisión SST",
      description: documento.estado_revision || "Pendiente de revisión documental",
      date: documento.ultima_revision,
      complete: revisionAprobada || Boolean(firmaSst),
      icon: CalendarClock,
    },
    {
      title: "Firma Responsable SST",
      description: firmaSst?.nombre_firmante || "Firma del responsable SST pendiente",
      date: firmaSst?.fecha_firma || firmaSst?.fecha_creacion,
      complete: Boolean(firmaSst),
      icon: PenLine,
    },
    {
      title: "Aprobación Gerencia",
      description: firmaGerencia?.nombre_firmante || "Aprobación gerencial pendiente",
      date: firmaGerencia?.fecha_firma || firmaGerencia?.fecha_creacion,
      complete: Boolean(firmaGerencia),
      icon: ShieldCheck,
    },
    {
      title: "Vigencia documental",
      description: normalizar(documento.estado) === "VIGENTE" ? "Documento vigente y controlado" : "Pendiente de vigencia",
      date: documento.fecha_vencimiento,
      complete: normalizar(documento.estado) === "VIGENTE",
      icon: Clock3,
    },
  ];

  return (
    <div className="firma-timeline-premium">
      {eventos.map((evento, index) => {
        const Icon = evento.icon;
        return (
          <article className={`firma-timeline-premium-item ${evento.complete ? "complete" : "pending"}`} key={evento.title}>
            <div className="firma-timeline-premium-left">
              <div className="firma-timeline-premium-marker">
                {evento.complete ? <CheckCircle2 size={18} /> : <Icon size={18} />}
              </div>
              {index < eventos.length - 1 && <span className="firma-timeline-premium-rail" />}
            </div>

            <div className="firma-timeline-premium-card">
              <div>
                <h4>{evento.title}</h4>
                <p>{evento.description}</p>
              </div>
              <span>{formatearFecha(evento.date)}</span>
            </div>
          </article>
        );
      })}
    </div>
  );
}
