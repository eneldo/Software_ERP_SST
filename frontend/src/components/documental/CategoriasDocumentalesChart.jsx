// ============================================================
// COMPONENTE: CategoriasDocumentalesChart
// Barras por categoría documental SST.
// ============================================================

import React from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { FolderKanban } from "lucide-react";

export default function CategoriasDocumentalesChart({ data = [] }) {
  return (
    <article className="ccd-panel">
      <div className="ccd-panel-title">
        <div>
          <h3>Documentos por categoría</h3>
          <p>Inventario documental clasificado.</p>
        </div>
        <FolderKanban size={22} />
      </div>

      <div className="ccd-chart-box">
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height={265}>
            <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="categoria" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="total" radius={[10, 10, 0, 0]} fill="#2563eb" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="ccd-empty">Sin categorías documentales.</div>
        )}
      </div>
    </article>
  );
}
