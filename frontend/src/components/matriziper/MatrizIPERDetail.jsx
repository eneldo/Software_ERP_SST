import React from "react";
import { X, Calendar, CheckCircle, AlertTriangle, Shield } from "lucide-react";

const CLASIFICACION_LABELS = {
  FISICO: "Físico",
  QUIMICO: "Químico",
  BIOLOGICO: "Biológico",
  BIOMECANICO: "Biomecánico",
  PSICOSOCIAL: "Psicosocial",
  CONDICIONES_SEGURIDAD: "Condiciones de Seguridad",
  FENOMENOS_NATURALES: "Fenómenos Naturales",
};

const CLASIFICACION_COLORS = {
  FISICO: { bg: "#fef2f2", color: "#991b1b" },
  QUIMICO: { bg: "#fefce8", color: "#854d0e" },
  BIOLOGICO: { bg: "#f0fdf4", color: "#166534" },
  BIOMECANICO: { bg: "#eff6ff", color: "#1e40af" },
  PSICOSOCIAL: { bg: "#faf5ff", color: "#6b21a8" },
  CONDICIONES_SEGURIDAD: { bg: "#fff7ed", color: "#9a3412" },
  FENOMENOS_NATURALES: { bg: "#f0f9ff", color: "#0c4a6e" },
};

function colorNR(nr) {
  if (nr >= 600) return "nr-critico";
  if (nr >= 150) return "nr-alto";
  if (nr >= 40) return "nr-medio";
  return "nr-bajo";
}

function ValorCampo({ label, valor, icon }) {
  return (
    <div className="detail-item">
      <label>{icon} {label}</label>
      <span>{valor || "—"}</span>
    </div>
  );
}

function ValorCampoSpan2({ label, valor, icon }) {
  return (
    <div className="detail-item span-2">
      <label>{icon} {label}</label>
      <span>{valor || "—"}</span>
    </div>
  );
}

export default function MatrizIPERDetail({ item, onClose }) {
  if (!item) return null;

  const nrClass = colorNR(item.nr);
  const clasifColor = CLASIFICACION_COLORS[item.clasificacion_peligro] || { bg: "#f1f5f9", color: "#475569" };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content iper-detail-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header" style={{ borderBottom: "2px solid #e2e8f0" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <Shield size={22} style={{ color: "#4f46e5" }} />
            <div>
              <h3 style={{ margin: 0, fontSize: "1.05rem" }}>Detalle Fila IPER</h3>
              <p style={{ margin: 0, fontSize: "0.78rem", color: "#64748b" }}>
                Registro #{item.id} · {item.proceso}
              </p>
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {/* SECCIÓN 1: CONTEXTO */}
          <fieldset className="iper-seccion">
            <legend>1. Contexto del Proceso</legend>
            <div className="detail-grid">
              <ValorCampo label="Proceso" valor={item.proceso} />
              <ValorCampo label="Zona / Lugar" valor={item.zona_lugar} />
              <ValorCampo label="Actividades" valor={item.actividades} />
              <ValorCampoSpan2 label="Tareas" valor={item.tareas} />
              <ValorCampo label="Rutinaria" valor={item.rutinaria === "SI" ? "Sí" : "No"} />
            </div>
          </fieldset>

          {/* SECCIÓN 2: PELIGRO */}
          <fieldset className="iper-seccion">
            <legend>2. Identificación del Peligro</legend>
            <div className="detail-grid">
              <div className="detail-item">
                <label>Clasificación</label>
                <span
                  style={{
                    display: "inline-block",
                    borderRadius: 999,
                    padding: "4px 12px",
                    fontSize: "0.78rem",
                    fontWeight: 700,
                    background: clasifColor.bg,
                    color: clasifColor.color,
                    width: "fit-content",
                  }}
                >
                  {CLASIFICACION_LABELS[item.clasificacion_peligro] || item.clasificacion_peligro}
                </span>
              </div>
              <ValorCampoSpan2 label="Descripción del Peligro" valor={item.descripcion_peligro} />
              <ValorCampo label="Riesgo (Efecto)" valor={item.riesgo} />
              <ValorCampoSpan2 label="Efectos Posibles" valor={item.efectos_posibles} />
            </div>
          </fieldset>

          {/* SECCIÓN 3: CONTROLES EXISTENTES */}
          <fieldset className="iper-seccion">
            <legend>3. Controles Existentes</legend>
            <div className="detail-grid tres">
              <ValorCampo label="Fuente" valor={item.fuente} />
              <ValorCampo label="Medio" valor={item.medio} />
              <ValorCampo label="Individuo" valor={item.individuo} />
            </div>
          </fieldset>

          {/* SECCIÓN 4: EVALUACIÓN */}
          <fieldset className="iper-seccion seccion-valoracion">
            <legend>4. Evaluación del Riesgo (GTC 45)</legend>
            <div className="detail-grid">
              <ValorCampo label="ND (Nivel de Deficiencia)" valor={<strong style={{ fontSize: "1.1rem" }}>{item.nd}</strong>} />
              <ValorCampo label="NE (Nivel de Exposición)" valor={<strong style={{ fontSize: "1.1rem" }}>{item.ne}</strong>} />
              <ValorCampo label="NP = ND × NE" valor={<><strong style={{ fontSize: "1.1rem" }}>{item.np}</strong> <span style={{ color: "#64748b", fontSize: "0.8rem" }}>({item.interpretacion_np})</span></>} />
              <ValorCampo label="NC (Nivel de Consecuencia)" valor={<strong style={{ fontSize: "1.1rem" }}>{item.nc}</strong>} />
              <ValorCampo label="NR = NP × NC" valor={<strong style={{ fontSize: "1.1rem" }}>{item.nr}</strong>} />
              <div className="detail-item">
                <label>Nivel de Riesgo</label>
                <span
                  style={{
                    display: "inline-block",
                    borderRadius: 999,
                    padding: "4px 12px",
                    fontSize: "0.78rem",
                    fontWeight: 700,
                    width: "fit-content",
                    background: nrClass === "nr-critico" ? "#fef2f2" : nrClass === "nr-alto" ? "#fff7ed" : nrClass === "nr-medio" ? "#fefce8" : "#f0fdf4",
                    color: nrClass === "nr-critico" ? "#dc2626" : nrClass === "nr-alto" ? "#ea580c" : nrClass === "nr-medio" ? "#ca8a04" : "#16a34a",
                  }}
                >
                  {item.interpretacion_nr}
                </span>
              </div>
              <div className="detail-item">
                <label>Aceptabilidad</label>
                <span
                  className={`ml-pill ${item.aceptabilidad === "ACEPTABLE" ? "cumple" : item.aceptabilidad === "NO ACEPTABLE" ? "no_cumple" : "pendiente"}`}
                  style={{ width: "fit-content" }}
                >
                  {item.aceptabilidad}
                </span>
              </div>
            </div>
          </fieldset>

          {/* SECCIÓN 5: CRITERIOS */}
          <fieldset className="iper-seccion">
            <legend>5. Criterios para Establecer Controles</legend>
            <div className="detail-grid">
              <ValorCampo label="Expuestos Hombres" valor={item.expuestos_hombres} />
              <ValorCampo label="Expuestos Mujeres" valor={item.expuestos_mujeres} />
              <ValorCampo label="Gestantes / Lactantes" valor={item.expuestos_gestantes} />
              <ValorCampoSpan2 label="Peor Consecuencia" valor={item.peor_consecuencia} />
            </div>
          </fieldset>

          {/* SECCIÓN 6: MEDIDAS DE INTERVENCIÓN */}
          <fieldset className="iper-seccion">
            <legend>6. Medidas de Intervención (Jerarquía de Controles)</legend>
            <div className="detail-grid">
              <ValorCampo label="Eliminación" valor={item.eliminacion} />
              <ValorCampo label="Control de Ingeniería" valor={item.control_ingenieria} />
              <ValorCampo label="Sustitución" valor={item.sustitucion} />
              <ValorCampo label="Señalización / Controles Administrativos" valor={item.senalizacion_admin} />
              <ValorCampo label="EPP" valor={item.epp} />
              <ValorCampo label="Responsable" valor={item.responsable} />
            </div>
          </fieldset>

          {/* SECCIÓN 7: SEGUIMIENTO */}
          <fieldset className="iper-seccion">
            <legend>7. Seguimiento</legend>
            <div className="detail-grid">
              <ValorCampo label="Fecha Proyectada" valor={item.fecha_proyectada} icon={<Calendar size={12} />} />
              <ValorCampo label="Fecha de Ejecución" valor={item.fecha_ejecucion} icon={<Calendar size={12} />} />
              <ValorCampoSpan2 label="Evidencias" valor={item.evidencias} />
              <div className="detail-item">
                <label>Realizado</label>
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 6,
                    borderRadius: 999,
                    padding: "4px 12px",
                    fontSize: "0.78rem",
                    fontWeight: 700,
                    width: "fit-content",
                    background: item.realizado === "SI" ? "#dcfce7" : "#fef3c7",
                    color: item.realizado === "SI" ? "#166534" : "#92400e",
                  }}
                >
                  {item.realizado === "SI" ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
                  {item.realizado === "SI" ? "Sí" : "No"}
                </span>
              </div>
            </div>
          </fieldset>
        </div>

        <div className="modal-footer">
          <button type="button" className="iper-btn-cancelar" onClick={onClose}>
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
