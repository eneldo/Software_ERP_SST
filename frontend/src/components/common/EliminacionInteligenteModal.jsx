// ============================================================
// MODAL ENTERPRISE DE ELIMINACIÓN INTELIGENTE
// ERP SST PRO ENTERPRISE
// FASE 37.3 — Smart Delete Enterprise v2
// Archivo: frontend/src/components/common/EliminacionInteligenteModal.jsx
// ============================================================

import {
  AlertTriangle,
  CheckCircle2,
  DatabaseZap,
  FileWarning,
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

function normalizarMatriz(validacion) {
  const matrix = validacion?.impact_matrix || validacion?.meta?.impact_matrix || [];
  if (Array.isArray(matrix) && matrix.length > 0) return matrix;
  return normalizarDependencias(validacion?.dependencies).map((item) => ({
    ...item,
    has_records: Number(item?.count || 0) > 0,
    severity: item?.severity || "MEDIUM",
    category: item?.category || "general",
    icon: item?.icon || "database",
  }));
}

function obtenerResumen(validacion, matriz, puedeEliminar) {
  return (
    validacion?.impact_summary ||
    validacion?.meta?.impact_summary || {
      total_rules: matriz.length,
      total_related_records: matriz.reduce((acc, item) => acc + Number(item?.count || 0), 0),
      total_blocking_records: matriz
        .filter((item) => item?.blocking && Number(item?.count || 0) > 0)
        .reduce((acc, item) => acc + Number(item?.count || 0), 0),
      blocking_rules: matriz.filter((item) => item?.blocking && Number(item?.count || 0) > 0).length,
      impact_level: puedeEliminar ? "LOW" : "MEDIUM",
      impact_label: puedeEliminar ? "Bajo" : "Medio",
      recommended_action: puedeEliminar ? "DELETE" : "INACTIVATE",
      can_delete: puedeEliminar,
    }
  );
}

function totalDependencias(dependencies = []) {
  return normalizarDependencias(dependencies).reduce(
    (acc, item) => acc + Number(item.count || 0),
    0
  );
}

function etiquetaSeveridad(severity) {
  const value = String(severity || "LOW").toUpperCase();
  if (value === "CRITICAL") return "Crítico";
  if (value === "HIGH") return "Alto";
  if (value === "MEDIUM") return "Medio";
  return "Bajo";
}

function classSeveridad(severity) {
  return `ei-severity-${String(severity || "LOW").toLowerCase()}`;
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
  const matriz = normalizarMatriz(validacion);
  const puedeEliminar = Boolean(validacion?.can_delete);
  const resumen = obtenerResumen(validacion, matriz, puedeEliminar);
  const total = totalDependencias(dependencias);
  const modo = puedeEliminar ? "safe" : "blocked";
  const filasVisibles = matriz.length > 0 ? matriz : dependencias;

  return (
    <section className="ei-modal-backdrop" role="dialog" aria-modal="true">
      <div className={`ei-modal ei-modal-${modo}`}>
        <header className="ei-modal-header">
          <div className="ei-modal-title-wrap">
            <span className={`ei-modal-icon ei-icon-${modo}`}>
              {puedeEliminar ? <CheckCircle2 size={25} /> : <ShieldAlert size={25} />}
            </span>

            <div>
              <p className="ei-modal-eyebrow">Smart Delete Enterprise v2</p>
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

          <div className="ei-impact-grid">
            <article>
              <span>Nivel de impacto</span>
              <strong className={classSeveridad(resumen?.impact_level)}>
                {resumen?.impact_label || etiquetaSeveridad(resumen?.impact_level)}
              </strong>
            </article>
            <article>
              <span>Relaciones evaluadas</span>
              <strong>{resumen?.total_rules ?? filasVisibles.length}</strong>
            </article>
            <article>
              <span>Registros relacionados</span>
              <strong>{resumen?.total_related_records ?? total}</strong>
            </article>
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
              <span>Análisis de dependencias</span>
            </div>

            {filasVisibles.length === 0 ? (
              <p className="ei-empty-dependencies">
                Sin relaciones activas ni registros dependientes detectados.
              </p>
            ) : (
              <div className="ei-dependencies-list ei-impact-list">
                {filasVisibles.map((dep, index) => {
                  const count = Number(dep?.count || 0);
                  const hasRecords = count > 0;
                  return (
                    <article
                      key={`${dep.table}-${dep.column}-${index}`}
                      className={hasRecords ? "ei-row-has-records" : "ei-row-empty"}
                    >
                      <div>
                        <strong>{dep.label || dep.table}</strong>
                        <span>
                          {hasRecords
                            ? dep.message || `${count} registros relacionados`
                            : dep.message || "Sin registros relacionados."}
                        </span>
                      </div>
                      <div className="ei-row-right">
                        <small className={classSeveridad(dep?.severity)}>
                          {etiquetaSeveridad(dep?.severity)}
                        </small>
                        <em>{count}</em>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}
          </div>

          {!puedeEliminar && (
            <div className="ei-summary-warning">
              <FileWarning size={19} />
              <strong>{resumen?.total_blocking_records ?? total}</strong>
              <span>registros relacionados impiden la eliminación física.</span>
            </div>
          )}

          <p className="ei-modal-note">
            {puedeEliminar
              ? "Esta acción es permanente y no se puede deshacer. La operación quedará registrada en auditoría del ERP."
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
