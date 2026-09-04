import React, { Suspense, lazy } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import RequireAuth from "./components/auth/RequireAuth";
import RequireRole from "./components/auth/RequireRole";
import AdminLayout from "./layouts/AdminLayout";
import PageLoader from "./components/common/PageLoader";
import {
  ROLES_DASHBOARD,
  ROLES_PORTAL_EMPLEADO,
  ROLES_ADMIN_SISTEMA,
  ROLES_ORGANIZACION,
  ROLES_PLANEAR,
  ROLES_HACER,
  ROLES_VERIFICAR,
  ROLES_DOCUMENTAL,
  ROLES_EXAMENES,
  ROLES_CAPACITACIONES,
  ROLES_INCIDENTES,
  ROLES_AUDITORIAS,
  ROLES_INDICADORES,
  ROLES_REPORTES_ANONIMOS,
  ROLES_ACCIONES_CORRECTIVAS,
} from "./constants/roles";
import { BrandingProvider } from "./components/branding/BrandingProvider";

const LoginPage = lazy(() => import("./pages/auth/LoginPage"));
const VerificarDocumento = lazy(() => import("./pages/public/VerificarDocumento"));
const ReporteAnonimoSSTPage = lazy(() => import("./pages/public/ReporteAnonimoSSTPage"));

const DashboardEjecutivoSST = lazy(() => import("./pages/admin/DashboardEjecutivoSST"));
const UsuariosSistemaPage = lazy(() => import("./pages/admin/UsuariosSistemaPage"));
const RolesSistemaPage = lazy(() => import("./pages/admin/RolesSistemaPage"));
const PermisosSistemaPage = lazy(() => import("./pages/admin/PermisosSistemaPage"));
const AuditoriaSistemaPage = lazy(() => import("./pages/admin/AuditoriaSistemaPage"));
const ConfiguracionSistemaPage = lazy(() => import("./pages/admin/ConfiguracionSistemaPage"));
const AuditoriaEvidenciasPage = lazy(() => import("./pages/admin/AuditoriaEvidenciasPage"));

const EmpresasSSTPage = lazy(() => import("./pages/organizacion/EmpresasSSTPage"));
const SedesSSTPage = lazy(() => import("./pages/organizacion/SedesSSTPage"));
const AreasSSTPage = lazy(() => import("./pages/organizacion/AreasSSTPage"));
const CargosSSTPage = lazy(() => import("./pages/organizacion/CargosSSTPage"));
const EmpleadosSSTPage = lazy(() => import("./pages/organizacion/EmpleadosSSTPage"));

const PoliticaSSTPage = lazy(() => import("./pages/planear/PoliticaSSTPage"));
const ObjetivosSSTPage = lazy(() => import("./pages/planear/ObjetivosSSTPage"));
const EvaluacionInicialPage = lazy(() => import("./pages/planear/EvaluacionInicialPage"));
const MatrizLegalPage = lazy(() => import("./pages/planear/MatrizLegalPage"));
const MatrizPeligrosPage = lazy(() => import("./pages/planear/MatrizPeligrosPage"));
const PlanAnualPage = lazy(() => import("./pages/planear/PlanAnualPage"));
const PlanMejoramientoPage = lazy(() => import("./pages/planear/PlanMejoramientoPage"));
const MatrizIPERPage = lazy(() => import("./pages/planear/MatrizIPERPage"));

const ExamenesMedicosPage = lazy(() => import("./pages/hacer/ExamenesMedicosSSTPage"));
const ProfesiogramaPage = lazy(() => import("./pages/hacer/ProfesiogramaPage"));
const EPPPage = lazy(() => import("./pages/hacer/EPPPage"));
const InspeccionesPage = lazy(() => import("./pages/hacer/InspeccionesPage"));
const CAPAPage = lazy(() => import("./pages/hacer/CAPAPage"));
const IncidentesPage = lazy(() => import("./pages/hacer/IncidentesPage"));
const CapacitacionesPage = lazy(() => import("./pages/hacer/CapacitacionesPage"));

const AuditoriasPage = lazy(() => import("./pages/verificar/AuditoriasPage"));
const RevisionDireccionPage = lazy(() => import("./pages/verificar/RevisionDireccionPage"));
const IndicadoresPage = lazy(() => import("./pages/verificar/IndicadoresPage"));
const NotificacionesSSTPage = lazy(() => import("./pages/verificar/NotificacionesSSTPage"));
const RevisionVersionesPage = lazy(() => import("./pages/verificar/RevisionVersionesPage"));
const ReportesAnonimosSSTPage = lazy(() => import("./pages/verificar/ReportesAnonimosSSTPage"));
const MisCasosSSTPage = lazy(() => import("./pages/verificar/MisCasosSSTPage"));

const BibliotecaDocumentalPage = lazy(() => import("./pages/documental/BibliotecaDocumentalPage"));
const CentroControlDocumentalPage = lazy(() => import("./pages/documental/CentroControlDocumentalPage"));
const FirmaDocumentalPage = lazy(() => import("./pages/documental/FirmaDocumentalPage"));

const PortalEmpleadoPage = lazy(() => import("./pages/portal/PortalEmpleadoPage"));
const MedidasCorrectivasPage = lazy(() => import("./pages/sst/MedidasCorrectivasPage"));

function ProtectedPage({ children, roles = null, layout = true }) {
  let content = children;

  if (layout) {
    content = <AdminLayout>{content}</AdminLayout>;
  }

  if (roles?.length) {
    content = <RequireRole allowedRoles={roles}>{content}</RequireRole>;
  }

  return <RequireAuth>{content}</RequireAuth>;
}

export default function App() {
  return (
    <BrandingProvider><BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/verificar-documento" element={<VerificarDocumento />} />
          <Route path="/verificar-documento/:codigo" element={<VerificarDocumento />} />
          <Route path="/reporte-sst" element={<ReporteAnonimoSSTPage />} />

          <Route path="/admin/dashboard" element={<ProtectedPage roles={ROLES_DASHBOARD} layout={false}><DashboardEjecutivoSST /></ProtectedPage>} />
          <Route path="/portal-empleado" element={<ProtectedPage roles={ROLES_PORTAL_EMPLEADO}><PortalEmpleadoPage /></ProtectedPage>} />

          <Route path="/organizacion/empresas" element={<ProtectedPage roles={ROLES_ORGANIZACION}><EmpresasSSTPage /></ProtectedPage>} />
          <Route path="/organizacion/sedes" element={<ProtectedPage roles={ROLES_ORGANIZACION}><SedesSSTPage /></ProtectedPage>} />
          <Route path="/organizacion/areas" element={<ProtectedPage roles={ROLES_ORGANIZACION}><AreasSSTPage /></ProtectedPage>} />
          <Route path="/organizacion/cargos" element={<ProtectedPage roles={ROLES_ORGANIZACION}><CargosSSTPage /></ProtectedPage>} />
          <Route path="/organizacion/empleados" element={<ProtectedPage roles={ROLES_ORGANIZACION}><EmpleadosSSTPage /></ProtectedPage>} />

          <Route path="/planear/politica-sst" element={<ProtectedPage roles={ROLES_PLANEAR} layout={false}><PoliticaSSTPage /></ProtectedPage>} />
          <Route path="/planear/objetivos-sst" element={<ProtectedPage roles={ROLES_PLANEAR} layout={false}><ObjetivosSSTPage /></ProtectedPage>} />
          <Route path="/planear/evaluacion-inicial" element={<ProtectedPage roles={ROLES_PLANEAR} layout={false}><EvaluacionInicialPage /></ProtectedPage>} />
          <Route path="/planear/matriz-legal" element={<ProtectedPage roles={ROLES_PLANEAR} layout={false}><MatrizLegalPage /></ProtectedPage>} />
          <Route path="/planear/matriz-peligros" element={<ProtectedPage roles={ROLES_PLANEAR} layout={false}><MatrizPeligrosPage /></ProtectedPage>} />
          <Route path="/planear/plan-anual" element={<ProtectedPage roles={ROLES_PLANEAR} layout={false}><PlanAnualPage /></ProtectedPage>} />
          <Route path="/planear/plan-mejoramiento" element={<ProtectedPage roles={ROLES_PLANEAR} layout={false}><PlanMejoramientoPage /></ProtectedPage>} />
          <Route path="/planear/matriz-iper" element={<ProtectedPage roles={ROLES_PLANEAR} layout={false}><MatrizIPERPage /></ProtectedPage>} />

          <Route path="/hacer/examenes-medicos" element={<ProtectedPage roles={ROLES_EXAMENES}><ExamenesMedicosPage /></ProtectedPage>} />
          <Route path="/hacer/profesiograma" element={<ProtectedPage roles={ROLES_EXAMENES}><ProfesiogramaPage /></ProtectedPage>} />
          <Route path="/hacer/epp" element={<ProtectedPage roles={ROLES_HACER}><EPPPage /></ProtectedPage>} />
          <Route path="/hacer/capacitaciones" element={<ProtectedPage roles={ROLES_CAPACITACIONES} layout={false}><CapacitacionesPage /></ProtectedPage>} />
          <Route path="/hacer/inspecciones" element={<ProtectedPage roles={ROLES_HACER}><InspeccionesPage /></ProtectedPage>} />
          <Route path="/hacer/capa" element={<ProtectedPage roles={ROLES_HACER}><CAPAPage /></ProtectedPage>} />
          <Route path="/hacer/incidentes" element={<ProtectedPage roles={ROLES_INCIDENTES}><IncidentesPage /></ProtectedPage>} />
          <Route path="/hacer/accidentes" element={<ProtectedPage roles={ROLES_INCIDENTES}><IncidentesPage tipoInicial="ACCIDENTE" /></ProtectedPage>} />

          <Route path="/verificar/indicadores" element={<ProtectedPage roles={ROLES_INDICADORES}><IndicadoresPage /></ProtectedPage>} />
          <Route path="/verificar/auditorias" element={<ProtectedPage roles={ROLES_AUDITORIAS} layout={false}><AuditoriasPage /></ProtectedPage>} />
          <Route path="/verificar/notificaciones" element={<ProtectedPage roles={ROLES_VERIFICAR}><NotificacionesSSTPage /></ProtectedPage>} />
          <Route path="/verificar/revision-direccion" element={<ProtectedPage roles={ROLES_VERIFICAR} layout={false}><RevisionDireccionPage /></ProtectedPage>} />
          <Route path="/verificar/revision-direccion/versiones" element={<ProtectedPage roles={ROLES_VERIFICAR} layout={false}><RevisionVersionesPage /></ProtectedPage>} />
          <Route path="/verificar/reportes-anonimos" element={<ProtectedPage roles={ROLES_REPORTES_ANONIMOS}><ReportesAnonimosSSTPage /></ProtectedPage>} />
          <Route path="/verificar/mis-casos-sst" element={<ProtectedPage roles={ROLES_VERIFICAR}><MisCasosSSTPage /></ProtectedPage>} />
          <Route path="/verificar/acciones-correctivas" element={<ProtectedPage roles={ROLES_ACCIONES_CORRECTIVAS}><MedidasCorrectivasPage /></ProtectedPage>} />

          <Route path="/documental/control" element={<ProtectedPage roles={ROLES_DOCUMENTAL} layout={false}><CentroControlDocumentalPage /></ProtectedPage>} />
          <Route path="/documental/biblioteca" element={<ProtectedPage roles={ROLES_DOCUMENTAL} layout={false}><BibliotecaDocumentalPage /></ProtectedPage>} />
          <Route path="/documental/firma-digital" element={<ProtectedPage roles={ROLES_DOCUMENTAL}><FirmaDocumentalPage /></ProtectedPage>} />

          <Route path="/admin/usuarios-sistema" element={<ProtectedPage roles={ROLES_ADMIN_SISTEMA}><UsuariosSistemaPage /></ProtectedPage>} />
          <Route path="/admin/roles" element={<ProtectedPage roles={ROLES_ADMIN_SISTEMA}><RolesSistemaPage /></ProtectedPage>} />
          <Route path="/admin/permisos" element={<ProtectedPage roles={ROLES_ADMIN_SISTEMA}><PermisosSistemaPage /></ProtectedPage>} />
          <Route path="/admin/auditoria" element={<ProtectedPage roles={ROLES_ADMIN_SISTEMA}><AuditoriaSistemaPage /></ProtectedPage>} />
          <Route path="/admin/auditoria-evidencias" element={<ProtectedPage roles={["SUPER_ADMIN", "AUDITOR"]}><AuditoriaEvidenciasPage /></ProtectedPage>} />
          <Route path="/admin/configuracion" element={<ProtectedPage roles={ROLES_ADMIN_SISTEMA}><ConfiguracionSistemaPage /></ProtectedPage>} />

          <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter></BrandingProvider>
  );
}
