// ============================================================
// DASHBOARD SAAS PRO - ERP SST PRO
// Consume /dashboard-saas/resumen y /dashboard-saas/salud
// ============================================================

import React, { useEffect, useState } from "react";
import {
  Building2,
  MapPin,
  Users,
  UserCheck,
  ShieldCheck,
  KeyRound,
  Activity,
  Database,
  RefreshCcw,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Tooltip,
  ResponsiveContainer,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

import api from "../../api/axios";
import AdminLayout from "../../layouts/AdminLayout";
import "../../styles/dashboard-saas.css";

export default function DashboardSaaS() {
  const [resumen, setResumen] = useState(null);
  const [salud, setSalud] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const cargarDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const [resumenRes, saludRes] = await Promise.all([
        api.get("/dashboard-saas/resumen"),
        api.get("/dashboard-saas/salud"),
      ]);

      setResumen(resumenRes.data);
      setSalud(saludRes.data);
    } catch (err) {
      console.error(err);
      setError("No se pudo cargar el Dashboard SaaS PRO. Verifica el token o el backend.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDashboard();
  }, []);

  const cards = resumen
    ? [
        {
          title: "Empresas",
          value: resumen.total_empresas,
          icon: Building2,
          subtitle: `${resumen.empresas_activas} activas`,
        },
        {
          title: "Sedes",
          value: resumen.total_sedes,
          icon: MapPin,
          subtitle: `${resumen.sedes_activas} activas`,
        },
        {
          title: "Áreas",
          value: resumen.total_areas,
          icon: Activity,
          subtitle: "Áreas organizacionales",
        },
        {
          title: "Cargos",
          value: resumen.total_cargos,
          icon: UserCheck,
          subtitle: "Cargos laborales",
        },
        {
          title: "Empleados",
          value: resumen.total_empleados,
          icon: Users,
          subtitle: `${resumen.empleados_activos} activos`,
        },
        {
          title: "Usuarios",
          value: resumen.total_usuarios,
          icon: ShieldCheck,
          subtitle: "Accesos al sistema",
        },
        {
          title: "Roles",
          value: resumen.total_roles,
          icon: KeyRound,
          subtitle: "Roles dinámicos",
        },
        {
          title: "Permisos",
          value: resumen.total_permisos,
          icon: Database,
          subtitle: "Permisos configurados",
        },
      ]
    : [];

  const empleadosData = resumen
    ? [
        { name: "Activos", value: resumen.empleados_activos },
        { name: "Inactivos", value: resumen.empleados_inactivos },
      ]
    : [];

  const seguridadData = resumen
    ? [
        { name: "Auditorías", total: resumen.total_auditorias },
        { name: "Logins", total: resumen.total_logins },
        { name: "Roles", total: resumen.total_roles },
        { name: "Permisos", total: resumen.total_permisos },
      ]
    : [];

  return (
    <AdminLayout>
      <div className="dashboard-saas">
        <div className="dashboard-header">
          <div>
            <span className="dashboard-badge">DASHBOARD SAAS PRO</span>
            <h2>Dashboard SaaS PRO</h2>
            <p>
              Vista ejecutiva de plataforma, seguridad, empresas, empleados y
              auditoría del ERP SST.
            </p>
          </div>

          <button className="refresh-btn" onClick={cargarDashboard}>
            <RefreshCcw size={18} />
            Actualizar
          </button>
        </div>

        {loading && <div className="dashboard-loading">Cargando dashboard...</div>}

        {error && (
          <div className="dashboard-error">
            <AlertTriangle size={18} />
            {error}
          </div>
        )}

        {!loading && resumen && (
          <>
            <section className="kpi-grid">
              {cards.map((card) => {
                const Icon = card.icon;

                return (
                  <article className="kpi-card" key={card.title}>
                    <div className="kpi-icon">
                      <Icon size={24} />
                    </div>
                    <div>
                      <span>{card.title}</span>
                      <h3>{card.value}</h3>
                      <p>{card.subtitle}</p>
                    </div>
                  </article>
                );
              })}
            </section>

            <section className="dashboard-grid">
              <article className="dashboard-panel">
                <div className="panel-title">
                  <h3>Estado empleados</h3>
                  <span>Activos vs inactivos</span>
                </div>

                <div className="chart-box">
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={empleadosData}
                        dataKey="value"
                        nameKey="name"
                        outerRadius={90}
                        label
                      >
                        {empleadosData.map((entry, index) => (
                          <Cell key={`cell-${index}`} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </article>

              <article className="dashboard-panel">
                <div className="panel-title">
                  <h3>Seguridad y auditoría</h3>
                  <span>Eventos principales del sistema</span>
                </div>

                <div className="chart-box">
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={seguridadData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Bar dataKey="total" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </article>
            </section>

            <section className="health-panel">
              <div className="health-title">
                <CheckCircle2 size={24} />
                <div>
                  <h3>Estado de plataforma</h3>
                  <p>Validación técnica del backend y servicios base</p>
                </div>
              </div>

              <div className="health-grid">
                <div>
                  <span>Estado</span>
                  <strong>{salud?.estado}</strong>
                </div>

                <div>
                  <span>Servicio</span>
                  <strong>{salud?.servicio}</strong>
                </div>

                <div>
                  <span>Versión</span>
                  <strong>{salud?.version}</strong>
                </div>

                <div>
                  <span>Base de datos</span>
                  <strong>{salud?.base_datos}</strong>
                </div>

                <div>
                  <span>Seguridad</span>
                  <strong>{salud?.seguridad}</strong>
                </div>

                <div>
                  <span>Auditoría</span>
                  <strong>{salud?.auditoria}</strong>
                </div>
              </div>
            </section>
          </>
        )}
      </div>
    </AdminLayout>
  );
}
