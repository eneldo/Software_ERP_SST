// ============================================================
// TIMELINE AUDITORÍA SST
// FASE 1.7.2
// Archivo:
// frontend/src/pages/verificar/AuditoriaTimeline.jsx
// ============================================================

import React, { useMemo } from "react";
import {
  AlertTriangle,
  CalendarCheck,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  FileWarning,
  ShieldAlert,
  Wand2,
} from "lucide-react";

const estadoAuditoriaLabel = {
  PROGRAMADA: "Programada",
  EN_PROCESO: "En proceso",
  CERRADA: "Cerrada",
  CANCELADA: "Cancelada",
};

export default function AuditoriaTimeline({ auditoria }) {
  const hallazgos = auditoria?.hallazgos || [];

  const resumen = useMemo(() => {
    const totalHallazgos = hallazgos.length;

    const noConformidades = hallazgos.filter(
      (h) => h.tipo_hallazgo === "NO_CONFORMIDAD"
    ).length;

    const observaciones = hallazgos.filter(
      (h) => h.tipo_hallazgo === "OBSERVACION"
    ).length;

    const oportunidades = hallazgos.filter(
      (h) => h.tipo_hallazgo === "OPORTUNIDAD_MEJORA"
    ).length;

    const abiertos = hallazgos.filter(
      (h) => h.estado === "ABIERTO"
    ).length;

    const enProceso = hallazgos.filter(
      (h) => h.estado === "EN_PROCESO"
    ).length;

    const cerrados = hallazgos.filter(
      (h) => h.estado === "CERRADO"
    ).length;

    const planesGenerados = hallazgos.filter(
      (h) => !!h.plan_mejoramiento_id
    ).length;

    const porcentajeCierre =
      totalHallazgos > 0 ? Math.round((cerrados / totalHallazgos) * 100) : 0;

    let riesgo = "BAJO";

    if (noConformidades > 0 || abiertos >= 3) {
      riesgo = "ALTO";
    } else if (observaciones > 0 || abiertos > 0 || enProceso > 0) {
      riesgo = "MEDIO";
    }

    return {
      totalHallazgos,
      noConformidades,
      observaciones,
      oportunidades,
      abiertos,
      enProceso,
      cerrados,
      planesGenerados,
      porcentajeCierre,
      riesgo,
    };
  }, [hallazgos]);

  const pasos = useMemo(() => {
    const estado = auditoria?.estado || "PROGRAMADA";

    return [
      {
        key: "PROGRAMADA",
        titulo: "Programada",
        descripcion: auditoria?.fecha_programada || "Sin fecha programada",
        icon: <CalendarCheck size={18} />,
        activo: ["PROGRAMADA", "EN_PROCESO", "CERRADA"].includes(estado),
        completado: ["EN_PROCESO", "CERRADA"].includes(estado),
      },
      {
        key: "EN_PROCESO",
        titulo: "En ejecución",
        descripcion: auditoria?.fecha_inicio || "Pendiente de inicio",
        icon: <Clock3 size={18} />,
        activo: ["EN_PROCESO", "CERRADA"].includes(estado),
        completado: ["CERRADA"].includes(estado),
      },
      {
        key: "HALLAZGOS",
        titulo: "Hallazgos",
        descripcion: `${resumen.totalHallazgos} registrados`,
        icon: <FileWarning size={18} />,
        activo: resumen.totalHallazgos > 0,
        completado: resumen.totalHallazgos > 0,
      },
      {
        key: "PLANES",
        titulo: "Planes",
        descripcion: `${resumen.planesGenerados} generados`,
        icon: <Wand2 size={18} />,
        activo: resumen.planesGenerados > 0,
        completado:
          resumen.totalHallazgos > 0 &&
          resumen.planesGenerados >= resumen.totalHallazgos,
      },
      {
        key: "CIERRE",
        titulo: "Cierre",
        descripcion: `${resumen.porcentajeCierre}% hallazgos cerrados`,
        icon: <CheckCircle2 size={18} />,
        activo: estado === "CERRADA" || resumen.porcentajeCierre === 100,
        completado: estado === "CERRADA" || resumen.porcentajeCierre === 100,
      },
    ];
  }, [auditoria, resumen]);

  if (!auditoria) {
    return null;
  }

  return (
    <section className="aud-timeline-panel">
      <div className="aud-timeline-header">
        <div>
          <span>Timeline auditoría</span>
          <h4>{auditoria.codigo}</h4>
          <p>{auditoria.nombre}</p>
        </div>

        <div className={`aud-risk ${String(resumen.riesgo).toLowerCase()}`}>
          {resumen.riesgo === "ALTO" && <ShieldAlert size={18} />}
          {resumen.riesgo === "MEDIO" && <AlertTriangle size={18} />}
          {resumen.riesgo === "BAJO" && <CheckCircle2 size={18} />}
          Riesgo {resumen.riesgo}
        </div>
      </div>

      <div className="aud-timeline-steps">
        {pasos.map((paso, index) => (
          <div
            key={paso.key}
            className={[
              "aud-timeline-step",
              paso.activo ? "active" : "",
              paso.completado ? "done" : "",
            ].join(" ")}
          >
            <div className="aud-timeline-icon">{paso.icon}</div>

            {index < pasos.length - 1 && (
              <div
                className={[
                  "aud-timeline-line",
                  pasos[index + 1]?.activo ? "active" : "",
                ].join(" ")}
              />
            )}

            <strong>{paso.titulo}</strong>
            <span>{paso.descripcion}</span>
          </div>
        ))}
      </div>

      <div className="aud-timeline-kpis">
        <article>
          <ClipboardCheck size={18} />
          <strong>{estadoAuditoriaLabel[auditoria.estado] || auditoria.estado}</strong>
          <span>Estado auditoría</span>
        </article>

        <article>
          <FileWarning size={18} />
          <strong>{resumen.totalHallazgos}</strong>
          <span>Total hallazgos</span>
        </article>

        <article>
          <ShieldAlert size={18} />
          <strong>{resumen.noConformidades}</strong>
          <span>No conformidades</span>
        </article>

        <article>
          <AlertTriangle size={18} />
          <strong>{resumen.abiertos}</strong>
          <span>Abiertos</span>
        </article>

        <article>
          <Clock3 size={18} />
          <strong>{resumen.enProceso}</strong>
          <span>En proceso</span>
        </article>

        <article>
          <CheckCircle2 size={18} />
          <strong>{resumen.cerrados}</strong>
          <span>Cerrados</span>
        </article>

        <article>
          <Wand2 size={18} />
          <strong>{resumen.planesGenerados}</strong>
          <span>Planes generados</span>
        </article>

        <article>
          <CheckCircle2 size={18} />
          <strong>{resumen.porcentajeCierre}%</strong>
          <span>Cierre hallazgos</span>
        </article>
      </div>
    </section>
  );
}