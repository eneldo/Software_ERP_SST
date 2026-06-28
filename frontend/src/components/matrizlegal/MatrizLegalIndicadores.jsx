// ============================================================
// COMPONENTE: MatrizLegalIndicadores
// FASE 1.8.5.1 / 1.8.5.2
// Indicadores rápidos de cumplimiento legal
// ============================================================

import React from "react";
import { BarChart3, FileCheck2, Scale, TriangleAlert } from "lucide-react";

export default function MatrizLegalIndicadores({ dashboard = {} }) {
  const cumplimiento = dashboard?.porcentaje_cumplimiento || 0;
  const evidencias = dashboard?.porcentaje_evidencias || 0;

  return (
    <section className="ml-indicadores-grid">
      <article className="ml-indicador-card">
        <div className="ml-panel-head mini">
          <div>
            <h3>Indicadores de cumplimiento</h3>
            <p>Lectura ejecutiva para auditorías SST.</p>
          </div>
          <BarChart3 size={18} />
        </div>

        <div className="ml-indicator-row">
          <span>Cumplimiento legal</span>
          <strong>{cumplimiento}%</strong>
        </div>
        <div className="ml-progress big">
          <span style={{ width: `${cumplimiento}%` }} />
        </div>

        <div className="ml-indicator-row">
          <span>Evidencias cargadas</span>
          <strong>{evidencias}%</strong>
        </div>
        <div className="ml-progress evidence">
          <span style={{ width: `${evidencias}%` }} />
        </div>
      </article>

      <article className="ml-indicador-card">
        <div className="ml-panel-head mini">
          <div>
            <h3>Estado normativo</h3>
            <p>Control por vigencia de normas.</p>
          </div>
          <Scale size={18} />
        </div>

        <div className="ml-mini-metrics">
          <div>
            <FileCheck2 size={18} />
            <span>Vigentes</span>
            <strong>{dashboard?.vigentes || 0}</strong>
          </div>
          <div>
            <TriangleAlert size={18} />
            <span>Derogadas</span>
            <strong>{dashboard?.derogadas || 0}</strong>
          </div>
          <div>
            <Scale size={18} />
            <span>Modificadas</span>
            <strong>{dashboard?.modificadas || 0}</strong>
          </div>
        </div>
      </article>
    </section>
  );
}
