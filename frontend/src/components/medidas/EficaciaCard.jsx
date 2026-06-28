// ============================================================
// EFICACIA CARD — MEDIDAS CORRECTIVAS ENTERPRISE
// ERP SST PRO
// FASE 1.1.8.7.4
// Archivo: frontend/src/components/medidas/EficaciaCard.jsx
// ============================================================

import { useState } from "react";
import { ShieldCheck } from "lucide-react";

export default function EficaciaCard({ medida, loading, onSubmit }) {
  const [form, setForm] = useState({
    resultado: "SI",
    porcentaje_eficacia: "",
    verificacion_eficacia: "",
    observacion: "",
  });

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit?.({
      ...form,
      porcentaje_eficacia: form.porcentaje_eficacia === "" ? null : Number(form.porcentaje_eficacia),
    });
  }

  return (
    <section className="mc-enterprise-card">
      <div className="mc-enterprise-card-header">
        <div>
          <span>Verificación de eficacia</span>
          <h3>{medida?.porcentaje_eficacia ?? "Pendiente"}%</h3>
        </div>
        <ShieldCheck size={22} />
      </div>

      <div className="mc-eficacia-current">
        <span>Resultado actual</span>
        <strong>{medida?.efectiva === true ? "Eficaz" : medida?.efectiva === false ? "No / Parcial" : "Sin evaluar"}</strong>
        <small>{medida?.fecha_verificacion_eficacia || "Sin fecha de verificación"}</small>
      </div>

      <form className="mc-enterprise-form" onSubmit={handleSubmit}>
        <label>
          Resultado
          <select value={form.resultado} onChange={(e) => setForm({ ...form, resultado: e.target.value })}>
            <option value="SI">Sí, fue eficaz</option>
            <option value="PARCIAL">Parcial</option>
            <option value="NO">No fue eficaz</option>
          </select>
        </label>

        <label>
          % eficacia opcional
          <input
            type="number"
            min="0"
            max="100"
            value={form.porcentaje_eficacia}
            onChange={(e) => setForm({ ...form, porcentaje_eficacia: e.target.value })}
            placeholder="Automático"
          />
        </label>

        <label className="full">
          Verificación de eficacia
          <textarea
            required
            minLength={5}
            value={form.verificacion_eficacia}
            onChange={(e) => setForm({ ...form, verificacion_eficacia: e.target.value })}
            placeholder="Explique si la causa raíz fue eliminada, si el riesgo se redujo o si requiere nueva acción."
          />
        </label>

        <label className="full">
          Observación
          <textarea
            value={form.observacion}
            onChange={(e) => setForm({ ...form, observacion: e.target.value })}
            placeholder="Observación adicional"
          />
        </label>

        <button className="mc-btn primary full" type="submit" disabled={loading}>
          Guardar eficacia
        </button>
      </form>
    </section>
  );
}
