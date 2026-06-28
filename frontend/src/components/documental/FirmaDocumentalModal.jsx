// ============================================================
// COMPONENTE: FirmaDocumentalModal
// Modal para registrar firma digital documental SST.
// ============================================================

import React, { useEffect, useState } from "react";
import { X, PenLine, Loader2 } from "lucide-react";

const ROLES_FIRMA = [
  "RESPONSABLE_SST",
  "GERENCIA",
  "COORDINADOR_SST",
  "AUDITOR_SST",
  "REPRESENTANTE_LEGAL",
];

export default function FirmaDocumentalModal({
  open,
  documento,
  onClose,
  onSubmit,
  loading = false,
}) {
  const [form, setForm] = useState({
    documento_id: null,
    rol_firmante: "RESPONSABLE_SST",
    nombre_firmante: "",
    cargo_firmante: "Responsable SST",
    observaciones: "Firma electrónica documental SST",
    firma_digital_id: null,
  });

  useEffect(() => {
    if (documento) {
      setForm((prev) => ({
        ...prev,
        documento_id: documento.id,
        nombre_firmante: documento.responsable || "",
      }));
    }
  }, [documento]);

  if (!open) return null;

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit?.({
      ...form,
      firma_digital_id: form.firma_digital_id || null,
    });
  };

  return (
    <div className="firma-modal-backdrop">
      <div className="firma-modal">
        <header className="firma-modal-header">
          <div>
            <span>Firma electrónica SST</span>
            <h2>{documento?.titulo || "Documento"}</h2>
            <p>{documento?.codigo_documental || documento?.codigo || "Documento controlado"}</p>
          </div>

          <button type="button" className="firma-icon-button" onClick={onClose}>
            <X size={20} />
          </button>
        </header>

        <form className="firma-form" onSubmit={handleSubmit}>
          <label>
            Rol firmante
            <select
              name="rol_firmante"
              value={form.rol_firmante}
              onChange={handleChange}
              required
            >
              {ROLES_FIRMA.map((rol) => (
                <option value={rol} key={rol}>{rol}</option>
              ))}
            </select>
          </label>

          <label>
            Nombre firmante
            <input
              name="nombre_firmante"
              value={form.nombre_firmante}
              onChange={handleChange}
              placeholder="Nombre completo"
              required
            />
          </label>

          <label>
            Cargo firmante
            <input
              name="cargo_firmante"
              value={form.cargo_firmante}
              onChange={handleChange}
              placeholder="Cargo"
              required
            />
          </label>

          <label className="firma-form-full">
            Observaciones
            <textarea
              name="observaciones"
              value={form.observaciones}
              onChange={handleChange}
              rows={4}
              placeholder="Observaciones de firma"
            />
          </label>

          <div className="firma-modal-actions">
            <button type="button" className="firma-btn secondary" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="firma-btn primary" disabled={loading}>
              {loading ? <Loader2 className="spin" size={18} /> : <PenLine size={18} />}
              Registrar firma
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
