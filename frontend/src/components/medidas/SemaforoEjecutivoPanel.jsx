// ============================================================
// SEMÁFORO EJECUTIVO MEDIDAS CORRECTIVAS
// ERP SST PRO
// FASE 1.1.8.7.5
// Archivo: frontend/src/components/medidas/SemaforoEjecutivoPanel.jsx
// ============================================================

import { AlertTriangle, CheckCircle2, ShieldAlert } from "lucide-react";
import "../../styles/medidas-inteligentes.css";

function colorClass(color) {
  const c = String(color || "").toUpperCase();
  if (c === "ROJO") return "red";
  if (c === "NARANJA") return "orange";
  if (c === "AMARILLO") return "yellow";
  return "green";
}

export default function SemaforoEjecutivoPanel({ data }) {
  const semaforo = data?.semaforo || {};
  const cls = colorClass(semaforo.color);

  return (
    <section className={`mci-semaforo ${cls}`}>
      <div className="mci-semaforo-main">
        <div className="mci-semaforo-icon">
          {cls === "green" ? <CheckCircle2 size={28} /> : cls === "red" ? <ShieldAlert size={28} /> : <AlertTriangle size={28} />}
        </div>
        <div>
          <span>Semáforo ejecutivo</span>
          <h3>{semaforo.nivel || "SIN NIVEL"}</h3>
          <p>{semaforo.mensaje || "Sin evaluación ejecutiva."}</p>
        </div>
        <strong>{semaforo.score ?? 0}</strong>
      </div>

      <div className="mci-factor-list">
        {(semaforo.factores || []).map((factor) => (
          <span key={factor}>{factor}</span>
        ))}
      </div>
    </section>
  );
}
