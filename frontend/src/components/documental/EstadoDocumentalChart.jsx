// ============================================================
// COMPONENTE: EstadoDocumentalChart
// Gráfica tipo dona con distribución por estado documental.
// ============================================================

import React from "react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { BarChart3 } from "lucide-react";

const COLORS = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2"];

export default function EstadoDocumentalChart({ data = [] }) {
  return (
    <article className="ccd-panel">
      <div className="ccd-panel-title">
        <div>
          <h3>Estado documental</h3>
          <p>Distribución actual por estado.</p>
        </div>
        <BarChart3 size={22} />
      </div>

      <div className="ccd-chart-box">
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height={265}>
            <PieChart>
              <Pie data={data} dataKey="value" nameKey="name" innerRadius={58} outerRadius={92} paddingAngle={3}>
                {data.map((entry, index) => (
                  <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="ccd-empty">Sin datos de estados.</div>
        )}
      </div>

      <div className="ccd-legend-list">
        {data.map((item, index) => (
          <span key={item.name}>
            <i style={{ background: COLORS[index % COLORS.length] }} />
            {item.name}: <strong>{item.value}</strong>
          </span>
        ))}
      </div>
    </article>
  );
}
