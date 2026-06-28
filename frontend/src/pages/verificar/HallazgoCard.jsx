// ============================================================
// COMPONENTE
// HALLAZGO CARD SST
// FASE 1.7.2 - TIMELINE + KANBAN
// Archivo: frontend/src/pages/verificar/HallazgoCard.jsx
// ============================================================

import React from "react";
import {
  CalendarClock,
  CheckCircle2,
  Edit3,
  FileWarning,
  ShieldAlert,
  Trash2,
  UserRound,
  Wand2,
} from "lucide-react";

const tipoHallazgoLabel = {
  NO_CONFORMIDAD: "No conformidad",
  OBSERVACION: "Observación",
  OPORTUNIDAD_MEJORA: "Oportunidad de mejora",
};

const estadoHallazgoLabel = {
  ABIERTO: "Abierto",
  EN_PROCESO: "En proceso",
  CERRADO: "Cerrado",
};

const getTipoIcon = (tipo) => {
  if (tipo === "NO_CONFORMIDAD") return <ShieldAlert size={15} />;
  if (tipo === "OPORTUNIDAD_MEJORA") return <CheckCircle2 size={15} />;
  return <FileWarning size={15} />;
};

export default function HallazgoCard({
  hallazgo,
  onEditar,
  onEliminar,
  onGenerarPlan,
}) {
  if (!hallazgo) return null;

  const tipo = hallazgo.tipo_hallazgo || "OBSERVACION";
  const estado = hallazgo.estado || "ABIERTO";
  const tienePlan = !!hallazgo.plan_mejoramiento_id;

  return (
    <article className="aud-kanban-card">
      <div className="aud-kanban-card-head">
        <div>
          <strong>{hallazgo.codigo || `HALL-${hallazgo.id}`}</strong>
          <span>{tipoHallazgoLabel[tipo] || tipo}</span>
        </div>

        <span className={`aud-kanban-state ${String(estado).toLowerCase()}`}>
          {estadoHallazgoLabel[estado] || estado}
        </span>
      </div>

      <div className="aud-kanban-type-row">
        <span className={`aud-kanban-type ${String(tipo).toLowerCase()}`}>
          {getTipoIcon(tipo)}
          {tipoHallazgoLabel[tipo] || tipo}
        </span>

        {tienePlan && (
          <span className="aud-kanban-plan-ok">
            <CheckCircle2 size={14} />
            Plan PM #{hallazgo.plan_mejoramiento_id}
          </span>
        )}
      </div>

      {hallazgo.requisito && (
        <div className="aud-kanban-requisito">
          <b>Requisito:</b> {hallazgo.requisito}
        </div>
      )}

      <p className="aud-kanban-desc">
        {hallazgo.descripcion || "Sin descripción registrada."}
      </p>

      {hallazgo.accion_recomendada && (
        <div className="aud-kanban-action">
          <strong>Acción recomendada</strong>
          <span>{hallazgo.accion_recomendada}</span>
        </div>
      )}

      <div className="aud-kanban-meta">
        <span>
          <UserRound size={14} />
          {hallazgo.responsable || "Sin responsable"}
        </span>

        <span>
          <CalendarClock size={14} />
          {hallazgo.fecha_compromiso || "Sin fecha"}
        </span>
      </div>

      <div className="aud-kanban-actions">
        <button
          type="button"
          onClick={() => onEditar && onEditar(hallazgo)}
          title="Editar hallazgo"
        >
          <Edit3 size={15} />
        </button>

        <button
          type="button"
          onClick={() => onGenerarPlan && onGenerarPlan(hallazgo)}
          disabled={tienePlan}
          title={tienePlan ? "Ya tiene plan asociado" : "Generar plan"}
        >
          <Wand2 size={15} />
        </button>

        <button
          type="button"
          onClick={() => onEliminar && onEliminar(hallazgo.id)}
          title="Eliminar hallazgo"
        >
          <Trash2 size={15} />
        </button>
      </div>
    </article>
  );
}