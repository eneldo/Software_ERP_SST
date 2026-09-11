// ============================================================
// MODAL HALLAZGOS AUDITORÍA SST ENTERPRISE
// FASE 1.7.2 - TIMELINE + KANBAN
// Archivo: frontend/src/pages/verificar/AuditoriaHallazgosModal.jsx
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Edit3,
  FileWarning,
  Plus,
  Save,
  Trash2,
  Wand2,
  X,
} from "lucide-react";

import api from "../../api/axios";
import { toastSuccess, toastError, toastWarning, toastInfo, confirmAction } from "../../utils/toast";
import AuditoriaTimeline from "./AuditoriaTimeline";
import HallazgosKanban from "./HallazgosKanban";
import "../../styles/auditorias-kanban.css";

const TIPOS_HALLAZGO = ["NO_CONFORMIDAD", "OBSERVACION", "OPORTUNIDAD_MEJORA"];
const ESTADOS_HALLAZGO = ["ABIERTO", "EN_PROCESO", "CERRADO"];

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

export default function AuditoriaHallazgosModal({
  abierto,
  auditoria,
  onClose,
  onUpdated,
}) {
  const [auditoriaDetalle, setAuditoriaDetalle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [hallazgoEditandoId, setHallazgoEditandoId] = useState(null);

  const [form, setForm] = useState({
    tipo_hallazgo: "OBSERVACION",
    requisito: "",
    descripcion: "",
    evidencia: "",
    causa: "",
    accion_recomendada: "",
    responsable: "",
    fecha_compromiso: "",
    estado: "ABIERTO",
  });

  const hallazgos = auditoriaDetalle?.hallazgos || [];

  const resumen = useMemo(() => {
    const total = hallazgos.length;
    const abiertos = hallazgos.filter((h) => h.estado === "ABIERTO").length;
    const enProceso = hallazgos.filter((h) => h.estado === "EN_PROCESO").length;
    const cerrados = hallazgos.filter((h) => h.estado === "CERRADO").length;
    const noConformidades = hallazgos.filter(
      (h) => h.tipo_hallazgo === "NO_CONFORMIDAD"
    ).length;
    const planesGenerados = hallazgos.filter(
      (h) => !!h.plan_mejoramiento_id
    ).length;

    const porcentajeCierre =
      total > 0 ? Math.round((cerrados / total) * 100) : 0;

    return {
      total,
      abiertos,
      enProceso,
      cerrados,
      noConformidades,
      planesGenerados,
      porcentajeCierre,
    };
  }, [hallazgos]);

  const mostrarError = (error, mensaje) => {
    console.error(error);

    const detail = error?.response?.data?.detail;
    let detalle = "";

    if (Array.isArray(detail)) {
      detalle = detail
        .map((item) => {
          const campo = Array.isArray(item.loc) ? item.loc.join(".") : "";
          return `${campo}: ${item.msg}`;
        })
        .join("\n");
    } else if (typeof detail === "object" && detail !== null) {
      detalle = JSON.stringify(detail, null, 2);
    } else if (detail) {
      detalle = detail;
    } else if (error?.message) {
      detalle = error.message;
    }

    toastError("Error", `${mensaje}${detalle ? `\n\nDetalle:\n${detalle}` : ""}`);
  };

  const limpiar = () => {
    setHallazgoEditandoId(null);
    setForm({
      tipo_hallazgo: "OBSERVACION",
      requisito: "",
      descripcion: "",
      evidencia: "",
      causa: "",
      accion_recomendada: "",
      responsable: "",
      fecha_compromiso: "",
      estado: "ABIERTO",
    });
  };

  const cargarAuditoria = async () => {
    if (!auditoria?.id) return;

    try {
      setLoading(true);

      const res = await api.get(`/verificar/auditorias-sst/${auditoria.id}`);
      setAuditoriaDetalle(res.data);
    } catch (error) {
      mostrarError(error, "No se pudo cargar el detalle de la auditoría.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (abierto && auditoria?.id) {
      limpiar();
      cargarAuditoria();
    }
  }, [abierto, auditoria?.id]);

  if (!abierto) return null;

  const handleForm = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const guardarHallazgo = async (e) => {
    e.preventDefault();

    if (!auditoriaDetalle?.id) {
      toastWarning("Advertencia", "No hay auditoría seleccionada.");
      return;
    }

    if (!form.descripcion.trim()) {
      toastWarning("Advertencia", "La descripción del hallazgo es obligatoria.");
      return;
    }

    const payload = {
      ...form,
      fecha_compromiso: form.fecha_compromiso || null,
    };

    try {
      setGuardando(true);

      if (hallazgoEditandoId) {
        await api.put(
          `/verificar/auditorias-sst/hallazgos/${hallazgoEditandoId}`,
          payload
        );
      } else {
        await api.post(
          `/verificar/auditorias-sst/${auditoriaDetalle.id}/hallazgos`,
          payload
        );
      }

      limpiar();
      await cargarAuditoria();

      if (onUpdated) await onUpdated();

      toastSuccess("Éxito", "Hallazgo guardado correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo guardar el hallazgo.");
    } finally {
      setGuardando(false);
    }
  };

  const editarHallazgo = (hallazgo) => {
    setHallazgoEditandoId(hallazgo.id);

    setForm({
      tipo_hallazgo: hallazgo.tipo_hallazgo || "OBSERVACION",
      requisito: hallazgo.requisito || "",
      descripcion: hallazgo.descripcion || "",
      evidencia: hallazgo.evidencia || "",
      causa: hallazgo.causa || "",
      accion_recomendada: hallazgo.accion_recomendada || "",
      responsable: hallazgo.responsable || "",
      fecha_compromiso: hallazgo.fecha_compromiso || "",
      estado: hallazgo.estado || "ABIERTO",
    });

    const formEl = document.querySelector(".aud-hallazgo-form");
    if (formEl) {
      formEl.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  const eliminarHallazgo = async (hallazgoId) => {
    if (!confirmAction("¿Desea eliminar este hallazgo?")) return;

    try {
      await api.delete(`/verificar/auditorias-sst/hallazgos/${hallazgoId}`);

      await cargarAuditoria();

      if (onUpdated) await onUpdated();
    } catch (error) {
      mostrarError(error, "No se pudo eliminar el hallazgo.");
    }
  };

  const generarPlanDesdeHallazgo = async (hallazgo) => {
    if (hallazgo.plan_mejoramiento_id) {
      toastInfo("Info", `Este hallazgo ya tiene plan asociado: ${hallazgo.plan_mejoramiento_id}`);
      return;
    }

    if (!confirmAction("¿Generar plan de mejoramiento desde este hallazgo?")) return;

    try {
      const res = await api.post(
        `/verificar/auditorias-sst/hallazgos/${hallazgo.id}/generar-plan`
      );

      await cargarAuditoria();

      if (onUpdated) await onUpdated();

      toastSuccess(
        "Éxito",
        `Plan generado correctamente.\nCódigo: ${res.data.codigo_plan}\nID: ${res.data.plan_mejoramiento_id}`
      );
    } catch (error) {
      mostrarError(error, "No se pudo generar el plan de mejoramiento.");
    }
  };

  return (
    <div className="aud-modal-overlay">
      <div className="aud-modal aud-modal-enterprise">
        <div className="aud-modal-header">
          <div>
            <span>Auditoría SST · Timeline + Kanban</span>
            <h3>
              {auditoriaDetalle?.codigo || auditoria?.codigo} ·{" "}
              {auditoriaDetalle?.nombre || auditoria?.nombre}
            </h3>
            <p>
              Total hallazgos: <strong>{resumen.total}</strong> · No
              conformidades: <strong>{resumen.noConformidades}</strong> ·
              Cierre: <strong>{resumen.porcentajeCierre}%</strong>
            </p>
          </div>

          <button type="button" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="aud-modal-enterprise-body">
          {loading && (
            <div className="aud-empty-card">
              <AlertTriangle size={18} />
              Cargando auditoría y hallazgos...
            </div>
          )}

          {!loading && auditoriaDetalle && (
            <>
              <AuditoriaTimeline auditoria={auditoriaDetalle} />

              <section className="aud-modal-resumen">
                <article>
                  <FileWarning size={20} />
                  <strong>{resumen.total}</strong>
                  <span>Total hallazgos</span>
                </article>

                <article>
                  <AlertTriangle size={20} />
                  <strong>{resumen.abiertos}</strong>
                  <span>Abiertos</span>
                </article>

                <article>
                  <BarChart3 size={20} />
                  <strong>{resumen.enProceso}</strong>
                  <span>En proceso</span>
                </article>

                <article>
                  <CheckCircle2 size={20} />
                  <strong>{resumen.cerrados}</strong>
                  <span>Cerrados</span>
                </article>

                <article>
                  <Wand2 size={20} />
                  <strong>{resumen.planesGenerados}</strong>
                  <span>Planes generados</span>
                </article>
              </section>

              <div className="aud-modal-grid aud-modal-grid-enterprise">
                <form className="aud-hallazgo-form" onSubmit={guardarHallazgo}>
                  <div className="aud-form-head">
                    <h4>
                      {hallazgoEditandoId ? "Editar hallazgo" : "Nuevo hallazgo"}
                    </h4>

                    {hallazgoEditandoId && (
                      <button
                        type="button"
                        className="aud-clear-mini"
                        onClick={limpiar}
                      >
                        <X size={14} />
                        Cancelar
                      </button>
                    )}
                  </div>

                  <label>Tipo de hallazgo</label>
                  <select
                    name="tipo_hallazgo"
                    value={form.tipo_hallazgo}
                    onChange={handleForm}
                  >
                    {TIPOS_HALLAZGO.map((tipo) => (
                      <option key={tipo} value={tipo}>
                        {tipoHallazgoLabel[tipo]}
                      </option>
                    ))}
                  </select>

                  <label>Requisito</label>
                  <input
                    name="requisito"
                    value={form.requisito}
                    onChange={handleForm}
                    placeholder="Ej: 2.4.1 Plan Anual SST"
                  />

                  <label>Descripción</label>
                  <textarea
                    name="descripcion"
                    value={form.descripcion}
                    onChange={handleForm}
                    placeholder="Descripción del hallazgo"
                  />

                  <label>Evidencia</label>
                  <textarea
                    name="evidencia"
                    value={form.evidencia}
                    onChange={handleForm}
                    placeholder="Evidencia encontrada durante auditoría"
                  />

                  <label>Causa</label>
                  <textarea
                    name="causa"
                    value={form.causa}
                    onChange={handleForm}
                    placeholder="Causa raíz"
                  />

                  <label>Acción recomendada</label>
                  <textarea
                    name="accion_recomendada"
                    value={form.accion_recomendada}
                    onChange={handleForm}
                    placeholder="Acción recomendada para cerrar el hallazgo"
                  />

                  <div className="aud-row">
                    <input
                      name="responsable"
                      value={form.responsable}
                      onChange={handleForm}
                      placeholder="Responsable"
                    />

                    <input
                      type="date"
                      name="fecha_compromiso"
                      value={form.fecha_compromiso}
                      onChange={handleForm}
                    />
                  </div>

                  <label>Estado</label>
                  <select name="estado" value={form.estado} onChange={handleForm}>
                    {ESTADOS_HALLAZGO.map((estado) => (
                      <option key={estado} value={estado}>
                        {estadoHallazgoLabel[estado]}
                      </option>
                    ))}
                  </select>

                  <div className="aud-form-actions">
                    <button type="submit" disabled={guardando}>
                      <Save size={17} />
                      {guardando
                        ? "Guardando..."
                        : hallazgoEditandoId
                        ? "Actualizar hallazgo"
                        : "Guardar hallazgo"}
                    </button>

                    <button type="button" onClick={limpiar}>
                      <Plus size={17} />
                      Nuevo
                    </button>
                  </div>
                </form>

                <section className="aud-hallazgos-kanban-panel">
                  <div className="aud-hallazgos-title aud-hallazgos-title-pro">
                    <div>
                      <h4>Kanban de Hallazgos SST</h4>
                      <p>
                        Clasificación por estado, riesgo y generación automática
                        de planes de mejoramiento.
                      </p>
                    </div>

                    <span>{hallazgos.length}</span>
                  </div>

                  {hallazgos.length === 0 ? (
                    <div className="aud-empty-card">
                      <AlertTriangle size={18} />
                      No hay hallazgos registrados para esta auditoría.
                    </div>
                  ) : (
                    <HallazgosKanban
                      hallazgos={hallazgos}
                      onEditar={editarHallazgo}
                      onEliminar={eliminarHallazgo}
                      onGenerarPlan={generarPlanDesdeHallazgo}
                    />
                  )}
                </section>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}