// ============================================================
// MAIN FRONTEND - ERP SST PRO
// FASE 2.2.1E - Responsive Enterprise Final
// ============================================================

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import ErrorBoundary from "./components/common/ErrorBoundary.jsx";

// CSS global responsive final.
// Debe ir después de App para sobrescribir estilos anteriores.
import "./styles/responsive-enterprise-final.css";
import "./styles/compact-module-typography.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
