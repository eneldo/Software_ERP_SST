// ============================================================
// ADMIN LAYOUT ENTERPRISE - ERP SST PRO
// FASE 1.6 + FASE 2.1: Sidebar colapsable, modo oscuro,
// responsive y navegación PLANEAR - Política SST
// ============================================================

import React, { useEffect, useState } from "react";
import {
  LayoutDashboard,
  Building2,
  MapPin,
  Network,
  BriefcaseBusiness,
  Users,
  ShieldCheck,
  ClipboardList,
  Target,
  FileCheck2,
  Scale,
  TriangleAlert,
  CalendarCheck,
  GraduationCap,
  HardHat,
  Stethoscope,
  ClipboardCheck,
  Activity,
  SearchCheck,
  RefreshCcw,
  Settings,
  LogOut,
  Menu,
  Moon,
  Sun,
  ChevronDown,
  Shield,
  KeyRound,
  History,
  Archive,
  UserCheck,
  

} from "lucide-react";
import "../styles/admin-layout-enterprise.css";

const gruposMenu = [
  {
    titulo: "Principal",
    items: [
      {
        label: "Dashboard Ejecutivo",
        icon: LayoutDashboard,
        path: "/admin/dashboard",
      },
    ],
  },
  {
    titulo: "PORTAL EMPLEADO",
    items: [
      {
        label: "Portal Empleado",
        icon: UserCheck,
        path: "/portal-empleado",
      },
    ],
  },

  {
    titulo: "Organización",
    items: [
      { label: "Empresas", icon: Building2, path: "/organizacion/empresas" },
      { label: "Sedes", icon: MapPin, path: "/organizacion/sedes" },
      { label: "Áreas", icon: Network, path: "/organizacion/areas" },
      {
        label: "Cargos",
        icon: BriefcaseBusiness,
        path: "/organizacion/cargos",
      },
      { label: "Empleados", icon: Users, path: "/organizacion/empleados" },
      {
        label: "Centro Documental",
        icon: FileCheck2,
        path: "/documental/control",
      },
      {
        label: "Biblioteca Documental",
        icon: Archive,
        path: "/documental/biblioteca",
      },
      {
        label: "Firma Digital SST",
        icon: SearchCheck,
        path: "/documental/firma-digital",
      },
    ],
  },
  {
    titulo: "PLANEAR",
    items: [
      {
        label: "Política SST",
        icon: FileCheck2,
        path: "/planear/politica-sst",
      },
      { label: "Objetivos SST", icon: Target, path: "/planear/objetivos-sst" },
      {
        label: "Evaluación Inicial",
        icon: ClipboardList,
        path: "/planear/evaluacion-inicial",
      },
      { label: "Matriz Legal", icon: Scale, path: "/planear/matriz-legal" },
      {
        label: "Matriz de Peligros",
        icon: TriangleAlert,
        path: "/planear/matriz-peligros",
      },
      { label: "Plan Anual", icon: CalendarCheck, path: "/planear/plan-anual" },
      {
        label: "Plan Mejoramiento",
        icon: ClipboardCheck,
        path: "/planear/plan-mejoramiento",
      },
    ],
  },
  {
    titulo: "HACER",
    items: [
      {
        label: "Capacitaciones",
        icon: GraduationCap,
        path: "/hacer/capacitaciones",
      },
      { label: "EPP", icon: HardHat, path: "/hacer/epp" },
      {
        label: "Exámenes Médicos",
        icon: Stethoscope,
        path: "/hacer/examenes-medicos",
      },
      {
        label: "Inspecciones",
        icon: ClipboardCheck,
        path: "/hacer/inspecciones",
      },
      { label: "CAPA", icon: ClipboardCheck, path: "/hacer/capa" },
      { label: "Incidentes", icon: Activity, path: "/hacer/incidentes" },
      { label: "Accidentes", icon: TriangleAlert, path: "/hacer/accidentes" },
    ],
  },
  {
    titulo: "VERIFICAR / ACTUAR",
    items: [
      { label: "Indicadores", icon: Activity, path: "/verificar/indicadores" },
      {
        label: "Auditorías SST",
        icon: ClipboardCheck,
        path: "/verificar/auditorias",
      },
      {
        label: "Revisión Dirección",
        icon: RefreshCcw,
        path: "/verificar/revision-direccion",
      },
      { label: "Acciones Correctivas", icon: ClipboardCheck, path: "/verificar/acciones-correctivas" },
      { label: "Reportes Anonimos SST", icon: ClipboardCheck, path: "/verificar/reportes-anonimos" },
      { label: "Mis Casos SST", icon: ClipboardCheck, path: "/verificar/mis-casos-sst" },


      {
        label: "Notificaciones SST",
        icon: ClipboardCheck,
        path: "/verificar/notificaciones",
      },
    ],
  },
  {
    titulo: "Seguridad",
    items: [
      { label: "Usuarios", icon: ShieldCheck, path: "/admin/usuarios-sistema" },
      { label: "Roles", icon: Shield, path: "/admin/roles" },
      { label: "Permisos", icon: KeyRound, path: "/admin/permisos" },
      { label: "Auditoría", icon: History, path: "/admin/auditoria" },
      { label: "Configuración", icon: Settings, path: "/admin/configuracion" },
      { label: "Auditoría de Evidencias", icon: History, path: "/admin/auditoria-evidencias" },
    ],
  },
];

export default function AdminLayout({ children }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(
    () => localStorage.getItem("theme") === "dark"
  );

  const [openGroups, setOpenGroups] = useState({
    Principal: true,
    Organización: true,
    PLANEAR: true,
    HACER: false,
    "VERIFICAR / ACTUAR": false,
    Seguridad: false,
  });

  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const userRole = String(user?.rol || "").toUpperCase();
  const isSuperAdmin = userRole === "SUPER_ADMIN";

  const gruposMenuPermitidos = gruposMenu.filter((grupo) => {
    if (grupo.titulo === "Seguridad") {
      return isSuperAdmin;
    }
    return true;
  });

  useEffect(() => {
    document.body.classList.toggle("sst-dark", darkMode);
    localStorage.setItem("theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    window.location.href = "/";
  };

  const toggleGroup = (titulo) => {
    setOpenGroups((prev) => ({ ...prev, [titulo]: !prev[titulo] }));
  };

  const currentPath = window.location.pathname;

  return (
    <div className={`enterprise-shell ${collapsed ? "sidebar-collapsed" : ""}`}>
      <button
        className="mobile-menu-btn"
        onClick={() => setMobileOpen(!mobileOpen)}
      >
        <Menu size={22} />
      </button>

      <aside className={`enterprise-sidebar ${mobileOpen ? "mobile-open" : ""}`}>
        <div className="enterprise-brand">
          <div className="enterprise-logo">SST</div>

          {!collapsed && (
            <div>
              <h2>ERP SST PRO</h2>
              <span>Enterprise SG-SST</span>
            </div>
          )}
        </div>

        <button className="collapse-btn" onClick={() => setCollapsed(!collapsed)}>
          <Menu size={18} />
          {!collapsed && <span>Contraer menú</span>}
        </button>

        <nav className="enterprise-menu">
          {gruposMenuPermitidos.map((grupo) => (
            <div className="menu-group" key={grupo.titulo}>
              {!collapsed && (
                <button
                  className="menu-group-title"
                  onClick={() => toggleGroup(grupo.titulo)}
                >
                  <span>{grupo.titulo}</span>
                  <ChevronDown
                    className={openGroups[grupo.titulo] ? "rotate" : ""}
                    size={15}
                  />
                </button>
              )}

              {(collapsed || openGroups[grupo.titulo]) && (
                <div className="menu-group-items">
                  {grupo.items.map((item) => {
                    const Icon = item.icon;
                    const active = currentPath === item.path;

                    return (
                      <a
                        href={item.path}
                        className={active ? "active" : ""}
                        key={item.label}
                        title={item.label}
                      >
                        <Icon size={18} />
                        {!collapsed && <span>{item.label}</span>}
                      </a>
                    );
                  })}
                </div>
              )}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="theme-btn" onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            {!collapsed && <span>{darkMode ? "Modo claro" : "Modo oscuro"}</span>}
          </button>

          <button className="logout-btn" onClick={logout}>
            <LogOut size={18} />
            {!collapsed && <span>Cerrar sesión</span>}
          </button>
        </div>
      </aside>

      <main className="enterprise-main">
        <header className="enterprise-topbar">
          <div>
            <span className="eyebrow">
              Sistema de Gestión de Seguridad y Salud en el Trabajo
            </span>
            <h1>Dashboard Ejecutivo SST PRO</h1>
            <p>
              Arquitectura visual definitiva para módulos PHVA, Decreto 1072,
              Resolución 0312 e ISO 45001.
            </p>
          </div>

          <div className="enterprise-user">
            <div className="user-avatar">
              {(user?.nombres || "A").slice(0, 1)}
            </div>
            <div>
              <strong>{user?.nombres || "Administrador"}</strong>
              <span>{user?.rol || "SUPER_ADMIN"}</span>
            </div>
          </div>
        </header>

        <section className="enterprise-content">{children}</section>
      </main>
    </div>
  );
}