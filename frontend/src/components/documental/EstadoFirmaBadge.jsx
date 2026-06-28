// ============================================================
// COMPONENTE: EstadoFirmaBadge
// Muestra el estado visual de firma/aprobación documental.
// ============================================================

import React from "react";
import { CheckCircle2, Clock3, XCircle, ShieldCheck } from "lucide-react";

const ESTADOS = {
  FIRMADO: {
    label: "Firmado",
    className: "firmado",
    icon: <CheckCircle2 size={14} />,
  },
  APROBADO: {
    label: "Aprobado",
    className: "aprobado",
    icon: <ShieldCheck size={14} />,
  },
  RECHAZADO: {
    label: "Rechazado",
    className: "rechazado",
    icon: <XCircle size={14} />,
  },
  PENDIENTE: {
    label: "Pendiente",
    className: "pendiente",
    icon: <Clock3 size={14} />,
  },
};

export default function EstadoFirmaBadge({ estado = "PENDIENTE" }) {
  const config = ESTADOS[estado] || ESTADOS.PENDIENTE;

  return (
    <span className={`firma-badge ${config.className}`}>
      {config.icon}
      {config.label}
    </span>
  );
}
