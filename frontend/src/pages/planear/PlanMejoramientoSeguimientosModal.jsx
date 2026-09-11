import React, { useEffect, useState } from "react";
import {
  AlertTriangle,
  CalendarClock,
  CheckCircle2,
  Clock3,
  History,
  Plus,
  Save,
  Trash2,
  TrendingUp,
  X,
} from "lucide-react";

import api from "../../api/axios";
import { toastSuccess, toastError, toastWarning, confirmAction } from "../../utils/toast";
import "../../styles/plan-mejoramiento-seguimientos.css";

const ESTADOS = ["PENDIENTE", "EN_PROCESO", "VENCIDO", "FINALIZADO"];

const estadoLabel = {
  PENDIENTE: "Pendiente",
  EN_PROCESO: "En proceso",
  VENCIDO: "Vencido",
  FINALIZADO: "Finalizado",
};

export default function PlanMejoramientoSeguimientosModal({
  abierto,
  plan,
  onClose,
  onUpdated,
}) {
  const [seguimientos, setSeguimientos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [guardando, setGuardando] = useState(false);

  const [form, setForm] = useState({
    observacion: "",
    recomendacion: "",
    tipo_seguimiento: "SEGUIMIENTO",
    estado_nuevo: "",
    porcentaje_avance_nuevo: "",
    fecha_seguimiento: "",
    proxima_fecha: "",
  });

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
    setForm({
      observacion: "",
      recomendacion: "",
      tipo_seguimiento: "SEGUIMIENTO",
      estado_nuevo: plan?.estado || "",
      porcentaje_avance_nuevo: plan?.porcentaje_avance ?? "",
      fecha_seguimiento: "",
      proxima_fecha: "",
    });
  };

  const cargarSeguimientos = async () => {
    if (!plan?.id) return;

    try {
      setLoading(true);

      const res = await api.get(
        `/planear/plan-mejoramiento-seguimientos/${plan.id}`
      );

      setSeguimientos(res.data || []);
    } catch (error) {
      mostrarError(error, "No se pudieron cargar los seguimientos.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (abierto && plan?.id) {
      limpiar();
      cargarSeguimientos();
    }
  }, [abierto, plan?.id]);

  if (!abierto) return null;

  const handleForm = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const crearSeguimiento = async (e) => {
    e.preventDefault();

    if (!form.observacion.trim()) {
      toastWarning("Advertencia", "La observación del seguimiento es obligatoria.");
      return;
    }

    const payload = {
      observacion: form.observacion,
      recomendacion: form.recomendacion || null,
      tipo_seguimiento: form.tipo_seguimiento || "SEGUIMIENTO",
      estado_nuevo: form.estado_nuevo || plan?.estado || null,
      porcentaje_avance_nuevo:
        form.porcentaje_avance_nuevo === ""
          ? null
          : Number(form.porcentaje_avance_nuevo),
      fecha_seguimiento: form.fecha_seguimiento || null,
      proxima_fecha: form.proxima_fecha || null,
    };

    try {
      setGuardando(true);

      await api.post(
        `/planear/plan-mejoramiento-seguimientos/${plan.id}`,
        payload
      );

      limpiar();
      await cargarSeguimientos();

      if (onUpdated) await onUpdated();

      toastSuccess("Éxito", "Seguimiento registrado correctamente.");
    } catch (error) {
      mostrarError(error, "No se pudo registrar el seguimiento.");
    } finally {
      setGuardando(false);
    }
  };

  const eliminarSeguimiento = async (seguimientoId) => {
    if (!confirmAction("¿Desea eliminar este seguimiento?")) return;

    try {
      await api.delete(
        `/planear/plan-mejoramiento-seguimientos/${seguimientoId}`
      );

      await cargarSeguimientos();

      if (onUpdated) await onUpdated();
    } catch (error) {
      mostrarError(error, "No se pudo eliminar el seguimiento.");
    }
  };

  const calcularCambioAvance = (item) => {
    const anterior = Number(item.porcentaje_avance_anterior || 0);
    const nuevo = Number(item.porcentaje_avance_nuevo || 0);
    return nuevo - anterior;
  };

  return (
    <div className="pm-seg-overlay">
      <div className="pm-seg-modal">
        <header className="pm-seg-header">
          <div>
            <span>Seguimiento de acción correctiva</span>
            <h3>
              {plan?.codigo} · {plan?.titulo}
            </h3>
            <p>
              Estado actual: <strong>{estadoLabel[plan?.estado] || plan?.estado}</strong>{" "}
              · Avance actual: <strong>{plan?.porcentaje_avance || 0}%</strong>
            </p>
          </div>

          <button type="button" onClick={onClose}>
            <X size={22} />
          </button>
        </header>

        <div className="pm-seg-grid">
          <form className="pm-seg-form" onSubmit={crearSeguimiento}>
            <div className="pm-seg-title">
              <Plus size={18} />
              <h4>Nuevo seguimiento</h4>
            </div>

            <label>Tipo de seguimiento</label>
            <select
              name="tipo_seguimiento"
              value={form.tipo_seguimiento}
              onChange={handleForm}
            >
              <option value="SEGUIMIENTO">Seguimiento</option>
              <option value="REVISION">Revisión</option>
              <option value="AUDITORIA">Auditoría</option>
              <option value="CIERRE">Cierre</option>
            </select>

            <div className="pm-seg-row">
              <div>
                <label>Nuevo estado</label>
                <select
                  name="estado_nuevo"
                  value={form.estado_nuevo}
                  onChange={handleForm}
                >
                  <option value="">Mantener estado actual</option>
                  {ESTADOS.map((estado) => (
                    <option key={estado} value={estado}>
                      {estadoLabel[estado]}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label>Nuevo avance %</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  name="porcentaje_avance_nuevo"
                  value={form.porcentaje_avance_nuevo}
                  onChange={handleForm}
                  placeholder="0 - 100"
                />
              </div>
            </div>

            <div className="pm-seg-row">
              <div>
                <label>Fecha seguimiento</label>
                <input
                  type="date"
                  name="fecha_seguimiento"
                  value={form.fecha_seguimiento}
                  onChange={handleForm}
                />
              </div>

              <div>
                <label>Próxima fecha</label>
                <input
                  type="date"
                  name="proxima_fecha"
                  value={form.proxima_fecha}
                  onChange={handleForm}
                />
              </div>
            </div>

            <label>Observación</label>
            <textarea
              name="observacion"
              value={form.observacion}
              onChange={handleForm}
              placeholder="Describe el avance, hallazgo o gestión realizada..."
            />

            <label>Recomendación</label>
            <textarea
              name="recomendacion"
              value={form.recomendacion}
              onChange={handleForm}
              placeholder="Recomendación para continuar o cerrar la acción..."
            />

            <button type="submit" disabled={guardando}>
              <Save size={17} />
              {guardando ? "Guardando..." : "Guardar seguimiento"}
            </button>
          </form>

          <section className="pm-seg-history">
            <div className="pm-seg-title">
              <History size={18} />
              <h4>Historial de seguimientos</h4>
              <span>{seguimientos.length}</span>
            </div>

            {loading && (
              <div className="pm-seg-empty">Cargando seguimientos...</div>
            )}

            {!loading && seguimientos.length === 0 && (
              <div className="pm-seg-empty">
                <AlertTriangle size={20} />
                No hay seguimientos registrados para esta acción.
              </div>
            )}

            {!loading && seguimientos.length > 0 && (
              <div className="pm-seg-timeline">
                {seguimientos.map((item) => {
                  const cambio = calcularCambioAvance(item);

                  return (
                    <article className="pm-seg-card" key={item.id}>
                      <div className="pm-seg-dot">
                        {item.estado_nuevo === "FINALIZADO" ? (
                          <CheckCircle2 size={18} />
                        ) : (
                          <Clock3 size={18} />
                        )}
                      </div>

                      <div className="pm-seg-content">
                        <div className="pm-seg-card-head">
                          <div>
                            <strong>{item.tipo_seguimiento}</strong>
                            <span>
                              {item.fecha_seguimiento || "Sin fecha"} · Usuario{" "}
                              {item.usuario_id || "-"}
                            </span>
                          </div>

                          <button
                            type="button"
                            onClick={() => eliminarSeguimiento(item.id)}
                          >
                            <Trash2 size={15} />
                          </button>
                        </div>

                        <div className="pm-seg-changes">
                          <span>
                            Estado:{" "}
                            <b>{estadoLabel[item.estado_anterior] || item.estado_anterior}</b>{" "}
                            →{" "}
                            <b>{estadoLabel[item.estado_nuevo] || item.estado_nuevo}</b>
                          </span>

                          <span>
                            Avance:{" "}
                            <b>{item.porcentaje_avance_anterior}%</b> →{" "}
                            <b>{item.porcentaje_avance_nuevo}%</b>
                            {cambio > 0 && (
                              <em>
                                <TrendingUp size={13} /> +{cambio}%
                              </em>
                            )}
                          </span>
                        </div>

                        <p>{item.observacion}</p>

                        {item.recomendacion && (
                          <div className="pm-seg-reco">
                            <strong>Recomendación</strong>
                            <span>{item.recomendacion}</span>
                          </div>
                        )}

                        {item.proxima_fecha && (
                          <div className="pm-seg-next">
                            <CalendarClock size={15} />
                            Próximo seguimiento: {item.proxima_fecha}
                          </div>
                        )}
                      </div>
                    </article>
                  );
                })}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}