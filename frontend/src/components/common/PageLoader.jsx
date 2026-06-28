import React from "react";
import "../../styles/page-loader.css";

export default function PageLoader({ label = "Cargando módulo..." }) {
  return (
    <div className="sst-page-loader" role="status" aria-live="polite">
      <div className="sst-page-loader__spinner" aria-hidden="true" />
      <p>{label}</p>
    </div>
  );
}
