// ============================================================
// KANBAN HALLAZGOS SST
// FASE 1.7.2
// Archivo:
// frontend/src/pages/verificar/HallazgosKanban.jsx
// ============================================================

import React, { useMemo } from "react";
import {
  AlertTriangle,
  Clock3,
  CheckCircle2,
  ShieldAlert,
} from "lucide-react";

import HallazgoCard from "./HallazgoCard";

export default function HallazgosKanban({
  hallazgos = [],
  onEditar,
  onEliminar,
  onGenerarPlan,
}) {
  const columnas = useMemo(() => {
    return {
      ABIERTO: hallazgos.filter(
        (h) => String(h.estado).toUpperCase() === "ABIERTO"
      ),

      EN_PROCESO: hallazgos.filter(
        (h) => String(h.estado).toUpperCase() === "EN_PROCESO"
      ),

      CERRADO: hallazgos.filter(
        (h) => String(h.estado).toUpperCase() === "CERRADO"
      ),
    };
  }, [hallazgos]);

  const total = hallazgos.length || 1;

  const porcentaje = (cantidad) =>
    ((cantidad / total) * 100).toFixed(0);

  return (
    <div className="aud-kanban-container">
      {/* ===================================================== */}
      {/* ABIERTOS */}
      {/* ===================================================== */}

      <div className="aud-kanban-column abierto">
        <div className="aud-kanban-header">
          <div className="aud-kanban-title">
            <AlertTriangle size={18} />
            <h4>ABIERTOS</h4>
          </div>

          <span>{columnas.ABIERTO.length}</span>
        </div>

        <div className="aud-kanban-progress">
          <div
            style={{
              width: `${porcentaje(columnas.ABIERTO.length)}%`,
            }}
          />
        </div>

        <small>
          {porcentaje(columnas.ABIERTO.length)}% del total
        </small>

        <div className="aud-kanban-list">
          {columnas.ABIERTO.length === 0 && (
            <div className="aud-kanban-empty">
              Sin hallazgos abiertos
            </div>
          )}

          {columnas.ABIERTO.map((hallazgo) => (
            <HallazgoCard
              key={hallazgo.id}
              hallazgo={hallazgo}
              onEditar={onEditar}
              onEliminar={onEliminar}
              onGenerarPlan={onGenerarPlan}
            />
          ))}
        </div>
      </div>

      {/* ===================================================== */}
      {/* EN PROCESO */}
      {/* ===================================================== */}

      <div className="aud-kanban-column proceso">
        <div className="aud-kanban-header">
          <div className="aud-kanban-title">
            <Clock3 size={18} />
            <h4>EN PROCESO</h4>
          </div>

          <span>{columnas.EN_PROCESO.length}</span>
        </div>

        <div className="aud-kanban-progress">
          <div
            style={{
              width: `${porcentaje(columnas.EN_PROCESO.length)}%`,
            }}
          />
        </div>

        <small>
          {porcentaje(columnas.EN_PROCESO.length)}% del total
        </small>

        <div className="aud-kanban-list">
          {columnas.EN_PROCESO.length === 0 && (
            <div className="aud-kanban-empty">
              Sin hallazgos en proceso
            </div>
          )}

          {columnas.EN_PROCESO.map((hallazgo) => (
            <HallazgoCard
              key={hallazgo.id}
              hallazgo={hallazgo}
              onEditar={onEditar}
              onEliminar={onEliminar}
              onGenerarPlan={onGenerarPlan}
            />
          ))}
        </div>
      </div>

      {/* ===================================================== */}
      {/* CERRADOS */}
      {/* ===================================================== */}

      <div className="aud-kanban-column cerrado">
        <div className="aud-kanban-header">
          <div className="aud-kanban-title">
            <CheckCircle2 size={18} />
            <h4>CERRADOS</h4>
          </div>

          <span>{columnas.CERRADO.length}</span>
        </div>

        <div className="aud-kanban-progress">
          <div
            style={{
              width: `${porcentaje(columnas.CERRADO.length)}%`,
            }}
          />
        </div>

        <small>
          {porcentaje(columnas.CERRADO.length)}% del total
        </small>

        <div className="aud-kanban-list">
          {columnas.CERRADO.length === 0 && (
            <div className="aud-kanban-empty">
              Sin hallazgos cerrados
            </div>
          )}

          {columnas.CERRADO.map((hallazgo) => (
            <HallazgoCard
              key={hallazgo.id}
              hallazgo={hallazgo}
              onEditar={onEditar}
              onEliminar={onEliminar}
              onGenerarPlan={onGenerarPlan}
            />
          ))}
        </div>
      </div>

      {/* ===================================================== */}
      {/* RESUMEN */}
      {/* ===================================================== */}

      <div className="aud-kanban-summary">
        <div className="aud-kanban-summary-card">
          <ShieldAlert size={22} />
          <strong>{hallazgos.length}</strong>
          <span>Total Hallazgos</span>
        </div>

        <div className="aud-kanban-summary-card">
          <AlertTriangle size={22} />
          <strong>{columnas.ABIERTO.length}</strong>
          <span>Abiertos</span>
        </div>

        <div className="aud-kanban-summary-card">
          <Clock3 size={22} />
          <strong>{columnas.EN_PROCESO.length}</strong>
          <span>En proceso</span>
        </div>

        <div className="aud-kanban-summary-card">
          <CheckCircle2 size={22} />
          <strong>{columnas.CERRADO.length}</strong>
          <span>Cerrados</span>
        </div>
      </div>
    </div>
  );
}