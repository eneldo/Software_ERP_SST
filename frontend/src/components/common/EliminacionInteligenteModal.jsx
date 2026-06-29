// ============================================================
// MODAL ENTERPRISE DE ELIMINACIÓN INTELIGENTE
// ERP SST PRO ENTERPRISE
// FASE 37.1.4 — Modal Enterprise de Eliminación Inteligente
// Archivo: frontend/src/components/common/EliminacionInteligenteModal.jsx
// ============================================================

import {
  AlertTriangle,
  CheckCircle2,
  DatabaseZap,
  Loader2,
  ShieldAlert,
  Trash2,
  X,
} from "lucide-react";

import "../../styles/eliminacion-inteligente-modal.css";

function normalizarDependencias(dependencies = []) {
  if (!Array.isArray(dependencies)) return [];
  return dependencies.filter((item) => Number(item?.count || 0) > 0);
}

function totalDependencias(dependencies = []) {
  return normalizarDependencias(dependencies).reduce(
    (acc, item) => acc + Number(item.count || 0),
    0
  );
}

export default function EliminacionInteligenteModal({
  abierto,
  entidad = "registro",
  registroNombre = "Registro seleccionado",
  validacion = null,
  ejecutando = false,
  onCancelar,
  onEliminar,
  onInactivar,
}) {
  if (!abierto) return null;

  const dependencias = normalizarDependencias(validacion?.dependencies);
  const puedeEliminar = Boolean(validacion?.can_delete);
  const total = totalDependencias(dependencias);

  const modo = puedeEliminar ? "safe" : "blocked";

  return (
    <section className="ei-modal-backdrop" role="dialog" aria-modal="true">
      <div className={`ei-modal ei-modal-${modo}`}>
        <header className="ei-modal-header">
          <div className="ei-modal-title-wrap">
            <span className={`ei-modal-icon ei-icon-${modo}`}>
              {puedeEliminar ? <CheckCircle2 size={25} /> : <ShieldAlert size={25} />}
            </span>

            <div>
              <p className="ei-modal-eyebrow">Eliminación Inteligente Enterprise</p>
              <h2>{puedeEliminar ? `Eliminar ${entidad}` : `No es posible eliminar ${entidad}`}</h2>
            </div>
          </div>

          <button
            type="button"
            className="ei-modal-close"
            onClick={onCancelar}
            disabled={ejecutando}
            aria-label="Cerrar modal"
          >
            <X size={20} />
          </button>
        </header>

        <div className="ei-modal-body">
          <div className="ei-record-card">
            <span>Registro evaluado</span>
            <strong>{registroNombre}</strong>
          </div>

          {puedeEliminar ? (
            <div className="ei-status-card ei-status-ok">
              <CheckCircle2 size={22} />
              <div>
                <strong>No se encontraron dependencias bloqueantes.</strong>
                <p>
                  Este registro puede eliminarse definitivamente de la base de datos.
                </p>
              </div>
            </div>
          ) : (
            <div className="ei-status-card ei-status-warning">
              <AlertTriangle size={23} />
              <div>
                <strong>El registro tiene trazabilidad asociada.</strong>
                <p>
                  Para proteger la integridad del SG-SST se recomienda inactivar el registro
                  en lugar de eliminarlo físicamente.
                </p>
              </div>
            </div>
          )}

          <div className="ei-integrity-panel">
            <div className="ei-integrity-header">
              <DatabaseZap size={18} />
              <span>Validación de integridad</span>
            </div>

            {dependencias.length === 0 ? (
              <p className="ei-empty-dependencies">
                Sin relaciones activas ni registros dependientes detectados.
              </p>
            ) : (
              <div className="ei-dependencies-list">
                {dependencias.map((dep, index) => (
                  <article key={`${dep.table}-${dep.column}-${index}`}>
                    <div>
                      <strong>{dep.label || dep.table}</strong>
                      <span>{dep.message || `${dep.count} registros relacionados`}</span>
                    </div>
                    <em>{dep.count}</em>
                  </article>
                ))}
              </div>
            )}
          </div>

          {!puedeEliminar && (
            <div className="ei-summary-warning">
              <strong>{total}</strong>
              <span>registros relacionados impiden la eliminación física.</span>
            </div>
          )}

          <p className="ei-modal-note">
            {puedeEliminar
              ? "Esta acción es permanente y no se puede deshacer. Confirma únicamente si estás seguro de eliminar este registro."
              : "La inactivación conserva el historial y evita afectar evidencias, reportes, auditorías y trazabilidad documental."}
          </p>
        </div>

        <footer className="ei-modal-actions">
          <button
            type="button"
            className="ei-btn ei-btn-secondary"
            onClick={onCancelar}
            disabled={ejecutando}
          >
            Cancelar
          </button>

          {puedeEliminar ? (
            <button
              type="button"
              className="ei-btn ei-btn-danger"
              onClick={onEliminar}
              disabled={ejecutando}
            >
              {ejecutando ? <Loader2 size={18} className="ei-spin" /> : <Trash2 size={18} />}
              Eliminar definitivamente
            </button>
          ) : (
            <button
              type="button"
              className="ei-btn ei-btn-warning"
              onClick={onInactivar}
              disabled={ejecutando}
            >
              {ejecutando ? <Loader2 size={18} className="ei-spin" /> : <ShieldAlert size={18} />}
              Inactivar registro
            </button>
          )}
        </footer>
      </div>
    </section>
  );
}
