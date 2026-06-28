// ============================================================
// COMPONENTE: MatrizLegalBI
// FASE 1.8.5.2 - MATRIZ LEGAL SST BI EXECUTIVE
// Gráficas ejecutivas con Recharts
// ============================================================

import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
} from "recharts";
import { BarChart3, PieChart as PieIcon, TrendingUp } from "lucide-react";

const COLORS = ["#16a34a", "#f59e0b", "#dc2626", "#2563eb", "#7c3aed", "#0891b2"];

export default function MatrizLegalBI({ dashboard = {} }) {
  const cumplimientoData = dashboard?.por_cumplimiento?.length
    ? dashboard.por_cumplimiento
    : [
        { nombre: "CUMPLE", total: dashboard?.cumplen || 0 },
        { nombre: "PENDIENTE", total: dashboard?.pendientes || 0 },
        { nombre: "NO_CUMPLE", total: dashboard?.no_cumplen || 0 },
      ];

  const tipoNormaData = dashboard?.por_tipo_norma || [];
  const tendencia = dashboard?.tendencia_cumplimiento || [];

  return (
    <section className="ml-bi-executive">
      <article className="ml-bi-card">
        <div className="ml-panel-head mini">
          <div>
            <h3>Cumplimiento legal SST</h3>
            <p>Distribución por estado de cumplimiento.</p>
          </div>
          <PieIcon size={18} />
        </div>

        <div className="ml-chart-box">
          <ResponsiveContainer width="100%" height={245}>
            <PieChart>
              <Pie
                data={cumplimientoData}
                dataKey="total"
                nameKey="nombre"
                cx="50%"
                cy="50%"
                innerRadius={58}
                outerRadius={92}
                paddingAngle={4}
              >
                {cumplimientoData.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </article>

      <article className="ml-bi-card">
        <div className="ml-panel-head mini">
          <div>
            <h3>Normas por tipo</h3>
            <p>Clasificación normativa registrada.</p>
          </div>
          <BarChart3 size={18} />
        </div>

        <div className="ml-chart-box">
          {tipoNormaData.length ? (
            <ResponsiveContainer width="100%" height={245}>
              <BarChart data={tipoNormaData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="nombre" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="total" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="ml-empty-bi">Sin datos por tipo de norma.</div>
          )}
        </div>
      </article>

      <article className="ml-bi-card wide">
        <div className="ml-panel-head mini">
          <div>
            <h3>Tendencia de cumplimiento</h3>
            <p>Lectura por mes según registros disponibles.</p>
          </div>
          <TrendingUp size={18} />
        </div>

        <div className="ml-chart-box">
          <ResponsiveContainer width="100%" height={245}>
            <LineChart data={tendencia}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="mes" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="cumplimiento"
                strokeWidth={3}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </article>
    </section>
  );
}
