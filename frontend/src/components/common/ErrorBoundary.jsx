// ============================================================
// ERROR BOUNDARY - ERP SST PRO ENTERPRISE
// FASE 36.8 — Logging Enterprise y Manejo de Errores
// Archivo: frontend/src/components/common/ErrorBoundary.jsx
// ============================================================

import React from "react";
import { logger } from "../../utils/logger";
import "../../styles/error-boundary.css";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    logger.error("Error no controlado en React", error, { componentStack: info?.componentStack });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleHome = () => {
    window.location.href = "/dashboard";
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <div className="erp-error-boundary">
        <div className="erp-error-card">
          <div className="erp-error-icon">⚠️</div>
          <h1>Algo salió mal</h1>
          <p>
            El módulo no pudo cargarse correctamente. Puede intentar recargar la página o volver al panel principal.
          </p>
          <div className="erp-error-actions">
            <button type="button" onClick={this.handleReload}>Recargar</button>
            <button type="button" className="secondary" onClick={this.handleHome}>Ir al dashboard</button>
          </div>
        </div>
      </div>
    );
  }
}

export default ErrorBoundary;
