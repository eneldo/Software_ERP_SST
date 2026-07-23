// ============================================================
// ADMIN LAYOUT ENTERPRISE - ERP SST PRO
// FASE 1.6 + FASE 2.1: Sidebar colapsable, modo oscuro,
// responsive y navegación PLANEAR - Política SST
// ============================================================

import React, { useEffect, useMemo, useRef, useState } from "react";
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
  Grid3X3,
  Search,
  X,

} from "lucide-react";
import "../styles/admin-layout-enterprise.css";
import { logout as cerrarSesion } from "../services/authService";
import { useBranding } from "../components/branding/BrandingProvider";

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

const SIDEBAR_GROUP_STORAGE_KEY = "sst-sidebar-open-group";

function obtenerGrupoDeRuta(pathname) {
  return gruposMenu.find((grupo) =>
    grupo.items.some(
      (item) =>
        pathname === item.path || pathname.startsWith(`${item.path}/`)
    )
  )?.titulo;
}

export default function AdminLayout({ children }) {
  const { branding } = useBranding();
  const currentPath = window.location.pathname;
  const currentRouteGroup = obtenerGrupoDeRuta(currentPath);
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [moduleSelectorOpen, setModuleSelectorOpen] = useState(false);
  const [moduleSearch, setModuleSearch] = useState("");
  const moduleSelectorRef = useRef(null);
  const moduleSearchRef = useRef(null);
  const [darkMode, setDarkMode] = useState(
    () => localStorage.getItem("theme") === "dark"
  );

  const [openGroup, setOpenGroup] = useState(
    () =>
      currentRouteGroup ||
      localStorage.getItem(SIDEBAR_GROUP_STORAGE_KEY) ||
      "Principal"
  );

  let user = {};
  try {
    user = JSON.parse(localStorage.getItem("user") || "{}");
  } catch {
    user = {};
  }
  const userRole = String(user?.rol || "").toUpperCase();
  const isSuperAdmin = userRole === "SUPER_ADMIN";
  const isManagement = ["ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST"].includes(userRole);
  const isExecutive = ["ALTA_DIRECCION", "REPRESENTANTE_LEGAL"].includes(userRole);
  const isOperational = userRole === "TECNICO_SST";
  const isParticipation = ["COPASST", "VIGIA_SST", "JEFE_AREA"].includes(userRole);
  const isHealthSupport = ["TALENTO_HUMANO", "MEDICO_OCUPACIONAL"].includes(userRole);
  const isAuditor = userRole === "AUDITOR";
  const isWorker = ["EMPLEADO", "TRABAJADOR", "CONTRATISTA"].includes(userRole);
  const isReadOnly = userRole === "SOLO_LECTURA";

  const gruposMenuPermitidos = gruposMenu
    .map((grupo) => {
      if (isSuperAdmin) return grupo;
      if (isManagement) return grupo.titulo === "Seguridad" ? null : grupo;
      if (isWorker) return grupo.titulo === "PORTAL EMPLEADO" ? grupo : null;
      if (isExecutive) {
        if (grupo.titulo === "Principal") return grupo;
        if (grupo.titulo === "VERIFICAR / ACTUAR") {
          const rutas = new Set(["/verificar/indicadores", "/verificar/revision-direccion"]);
          return { ...grupo, items: grupo.items.filter((item) => rutas.has(item.path)) };
        }
        return null;
      }
      if (isOperational || isParticipation) {
        if (["Principal", "PORTAL EMPLEADO"].includes(grupo.titulo)) return grupo;
        return null;
      }
      if (isHealthSupport || isReadOnly) {
        return grupo.titulo === "Principal" ? grupo : null;
      }
      if (isAuditor) {
        if (grupo.titulo === "Principal") return grupo;
        if (grupo.titulo === "VERIFICAR / ACTUAR") {
          return { ...grupo, items: grupo.items.filter((item) => item.path === "/verificar/auditorias") };
        }
        if (grupo.titulo === "Seguridad") {
          return { ...grupo, items: grupo.items.filter((item) => item.path === "/admin/auditoria-evidencias") };
        }
      }
      return null;
    })
    .filter((grupo) => grupo?.items?.length);

  const gruposSelector = useMemo(() => {
    const termino = moduleSearch.trim().toLocaleLowerCase("es");
    if (!termino) return gruposMenuPermitidos;

    return gruposMenuPermitidos
      .map((grupo) => ({
        ...grupo,
        items: grupo.items.filter((item) =>
          `${grupo.titulo} ${item.label}`.toLocaleLowerCase("es").includes(termino)
        ),
      }))
      .filter((grupo) => grupo.items.length);
  }, [gruposMenuPermitidos, moduleSearch]);

  useEffect(() => {
    document.body.classList.toggle("sst-dark", darkMode);
    localStorage.setItem("theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  useEffect(() => {
    if (currentRouteGroup) {
      setOpenGroup(currentRouteGroup);
      localStorage.setItem(SIDEBAR_GROUP_STORAGE_KEY, currentRouteGroup);
    }
  }, [currentRouteGroup]);

  useEffect(() => {
    if (!moduleSelectorOpen) return undefined;

    moduleSearchRef.current?.focus();
    const cerrarSelector = (event) => {
      if (event.key === "Escape") setModuleSelectorOpen(false);
      if (event.type === "mousedown" && !moduleSelectorRef.current?.contains(event.target)) {
        setModuleSelectorOpen(false);
      }
    };

    document.addEventListener("keydown", cerrarSelector);
    document.addEventListener("mousedown", cerrarSelector);
    return () => {
      document.removeEventListener("keydown", cerrarSelector);
      document.removeEventListener("mousedown", cerrarSelector);
    };
  }, [moduleSelectorOpen]);

  const logout = async () => {
    await cerrarSesion();
    window.location.href = "/";
  };

  const selectGroup = (titulo) => {
    setOpenGroup(titulo);
    localStorage.setItem(SIDEBAR_GROUP_STORAGE_KEY, titulo);
  };

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
          <div className={`enterprise-logo ${branding.logo_data_url ? "has-image" : ""}`}>
            {branding.logo_data_url ? <img src={branding.logo_data_url} alt="Logo corporativo" /> : "SST"}
          </div>

          {!collapsed && (
            <div>
              <h2>{branding.nombre_plataforma}</h2>
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
            <div
              className={`menu-group ${openGroup === grupo.titulo ? "open" : ""}`}
              key={grupo.titulo}
            >
              {!collapsed && (
                <button
                  className="menu-group-title"
                  aria-expanded={openGroup === grupo.titulo}
                  onClick={() => selectGroup(grupo.titulo)}
                >
                  <span>{grupo.titulo}</span>
                  <ChevronDown
                    className={openGroup === grupo.titulo ? "rotate" : ""}
                    size={15}
                  />
                </button>
              )}

              {(collapsed || openGroup === grupo.titulo) && (
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
                        onClick={() => {
                          selectGroup(grupo.titulo);
                          setMobileOpen(false);
                        }}
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
            <h1>{branding.nombre_plataforma}</h1>
            <p>
              Arquitectura visual definitiva para módulos PHVA, Decreto 1072,
              Resolución 0312 e ISO 45001.
            </p>
          </div>

          <div className="enterprise-topbar-actions">
            <div className="module-selector" ref={moduleSelectorRef}>
              <button
                type="button"
                className={`module-selector-trigger ${moduleSelectorOpen ? "active" : ""}`}
                aria-haspopup="dialog"
                aria-expanded={moduleSelectorOpen}
                onClick={() => {
                  setModuleSelectorOpen((open) => !open);
                  setModuleSearch("");
                }}
              >
                <Grid3X3 size={18} />
                <span>Módulos</span>
                <ChevronDown size={15} />
              </button>

              {moduleSelectorOpen && (
                <div className="module-selector-panel" role="dialog" aria-label="Selector de módulos">
                  <div className="module-selector-header">
                    <div>
                      <strong>Ir a un módulo</strong>
                      <span>{gruposMenuPermitidos.reduce((total, grupo) => total + grupo.items.length, 0)} disponibles</span>
                    </div>
                    <button type="button" aria-label="Cerrar selector" onClick={() => setModuleSelectorOpen(false)}>
                      <X size={17} />
                    </button>
                  </div>

                  <label className="module-selector-search">
                    <Search size={17} />
                    <input
                      ref={moduleSearchRef}
                      value={moduleSearch}
                      onChange={(event) => setModuleSearch(event.target.value)}
                      placeholder="Buscar módulo..."
                      aria-label="Buscar módulo"
                    />
                  </label>

                  <div className="module-selector-groups">
                    {gruposSelector.map((grupo) => (
                      <section key={grupo.titulo} className="module-selector-group">
                        <h3>{grupo.titulo}</h3>
                        <div>
                          {grupo.items.map((item) => {
                            const Icon = item.icon;
                            return (
                              <a
                                key={item.path}
                                href={item.path}
                                className={currentPath === item.path ? "active" : ""}
                                onClick={() => {
                                  selectGroup(grupo.titulo);
                                  setModuleSelectorOpen(false);
                                  setMobileOpen(false);
                                }}
                              >
                                <span className="module-selector-icon"><Icon size={17} /></span>
                                <span>{item.label}</span>
                              </a>
                            );
                          })}
                        </div>
                      </section>
                    ))}
                    {!gruposSelector.length && (
                      <div className="module-selector-empty">No se encontraron módulos.</div>
                    )}
                  </div>
                </div>
              )}
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
          </div>
        </header>

        <section className="enterprise-content">{children}</section>
      </main>
    </div>
  );
}
