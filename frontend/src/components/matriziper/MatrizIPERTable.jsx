import React from "react";
import { X, Eye, Shield, Download } from "lucide-react";

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

export default function MatrizIPERTable({ items, onClose, onVerDetalle }) {
  if (!items || items.length === 0) return null;

  const totalExpuestos = items.reduce(
    (sum, i) => sum + (i.expuestos_hombres || 0) + (i.expuestos_mujeres || 0) + (i.expuestos_gestantes || 0),
    0
  );

  const noAceptables = items.filter((i) => i.aceptabilidad === "NO ACEPTABLE").length;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content iper-table-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header" style={{ borderBottom: "2px solid #e2e8f0" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <Shield size={22} style={{ color: "#4f46e5" }} />
            <div>
              <h3 style={{ margin: 0, fontSize: "1.1rem" }}>Matriz IPER Completa</h3>
              <p style={{ margin: 0, fontSize: "0.78rem", color: "#64748b" }}>
                {items.length} registro{items.length !== 1 ? "s" : ""} · {totalExpuestos} expuestos total
                {noAceptables > 0 && (
                  <span style={{ color: "#dc2626", fontWeight: 700, marginLeft: 8 }}>
                    · {noAceptables} no aceptable{noAceptables !== 1 ? "s" : ""}
                  </span>
                )}
              </p>
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body iper-table-body">
          <div className="table-wrap">
            <table className="ml-table iper-matrix-table">
              <thead>
                <tr>
                  <th style={{ width: 40 }}>#</th>
                  <th>Proceso</th>
                  <th>Clasificación</th>
                  <th style={{ minWidth: 180 }}>Descripción Peligro</th>
                  <th style={{ textAlign: "center" }}>ND</th>
                  <th style={{ textAlign: "center" }}>NE</th>
                  <th style={{ textAlign: "center" }}>NP</th>
                  <th style={{ textAlign: "center" }}>NC</th>
                  <th style={{ textAlign: "center" }}>NR</th>
                  <th>Aceptabilidad</th>
                  <th>Responsable</th>
                  <th style={{ textAlign: "center" }}>Realizado</th>
                  <th style={{ width: 50 }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, idx) => {
                  const nrClass = colorNR(item.nr);
                  const clasifColor = CLASIFICACION_COLORS[item.clasificacion_peligro] || { bg: "#f1f5f9", color: "#475569" };
                  return (
                    <tr key={item.id}>
                      <td style={{ fontWeight: 600, color: "#64748b" }}>{idx + 1}</td>
                      <td style={{ fontWeight: 600, color: "#1e293b" }}>{item.proceso}</td>
                      <td>
                        <span
                          style={{
                            display: "inline-block",
                            borderRadius: 999,
                            padding: "4px 10px",
                            fontSize: "0.72rem",
                            fontWeight: 700,
                            background: clasifColor.bg,
                            color: clasifColor.color,
                          }}
                        >
                          {CLASIFICACION_LABELS[item.clasificacion_peligro] || item.clasificacion_peligro}
                        </span>
                      </td>
                      <td style={{ maxWidth: 200, fontSize: "0.8rem", color: "#475569" }}>
                        {item.descripcion_peligro}
                      </td>
                      <td style={{ textAlign: "center" }}><strong>{item.nd}</strong></td>
                      <td style={{ textAlign: "center" }}><strong>{item.ne}</strong></td>
                      <td style={{ textAlign: "center" }}><strong>{item.np}</strong></td>
                      <td style={{ textAlign: "center" }}><strong>{item.nc}</strong></td>
                      <td style={{ textAlign: "center" }}>
                        <strong className={nrClass} style={{ fontSize: "0.95rem" }}>{item.nr}</strong>
                      </td>
                      <td>
                        <span
                          className={`ml-pill ${item.aceptabilidad === "ACEPTABLE" ? "cumple" : item.aceptabilidad === "NO ACEPTABLE" ? "no_cumple" : "pendiente"}`}
                          style={{ fontSize: "0.7rem", whiteSpace: "nowrap" }}
                        >
                          {item.aceptabilidad}
                        </span>
                      </td>
                      <td style={{ fontSize: "0.8rem", color: "#475569", maxWidth: 120 }}>
                        {item.responsable || "—"}
                      </td>
                      <td style={{ textAlign: "center" }}>
                        <span
                          className={`ml-pill ${item.realizado === "SI" ? "cumple" : "pendiente"}`}
                          style={{ fontSize: "0.7rem", fontWeight: 800 }}
                        >
                          {item.realizado}
                        </span>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="iper-btn-ver"
                          onClick={() => onVerDetalle(item)}
                          title="Ver detalle completo"
                        >
                          <Eye size={16} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
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
