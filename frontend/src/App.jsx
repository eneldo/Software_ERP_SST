import React, { Suspense, lazy } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import RequireAuth from "./components/auth/RequireAuth";
import RequireRole from "./components/auth/RequireRole";
import AdminLayout from "./layouts/AdminLayout";
import PageLoader from "./components/common/PageLoader";
import { ROLES_DASHBOARD, ROLES_PORTAL_EMPLEADO } from "./constants/roles";

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

const ExamenesMedicosPage = lazy(() => import("./pages/hacer/ExamenesMedicosSSTPage"));
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
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/verificar-documento" element={<VerificarDocumento />} />
          <Route path="/verificar-documento/:codigo" element={<VerificarDocumento />} />
          <Route path="/reporte-sst" element={<ReporteAnonimoSSTPage />} />

          <Route path="/admin/dashboard" element={<ProtectedPage roles={ROLES_DASHBOARD} layout={false}><DashboardEjecutivoSST /></ProtectedPage>} />
          <Route path="/portal-empleado" element={<ProtectedPage roles={ROLES_PORTAL_EMPLEADO}><PortalEmpleadoPage /></ProtectedPage>} />

          <Route path="/organizacion/empresas" element={<ProtectedPage><EmpresasSSTPage /></ProtectedPage>} />
          <Route path="/organizacion/sedes" element={<ProtectedPage><SedesSSTPage /></ProtectedPage>} />
          <Route path="/organizacion/areas" element={<ProtectedPage><AreasSSTPage /></ProtectedPage>} />
          <Route path="/organizacion/cargos" element={<ProtectedPage><CargosSSTPage /></ProtectedPage>} />
          <Route path="/organizacion/empleados" element={<ProtectedPage><EmpleadosSSTPage /></ProtectedPage>} />

          <Route path="/planear/politica-sst" element={<ProtectedPage layout={false}><PoliticaSSTPage /></ProtectedPage>} />
          <Route path="/planear/objetivos-sst" element={<ProtectedPage layout={false}><ObjetivosSSTPage /></ProtectedPage>} />
          <Route path="/planear/evaluacion-inicial" element={<ProtectedPage layout={false}><EvaluacionInicialPage /></ProtectedPage>} />
          <Route path="/planear/matriz-legal" element={<ProtectedPage layout={false}><MatrizLegalPage /></ProtectedPage>} />
          <Route path="/planear/matriz-peligros" element={<ProtectedPage layout={false}><MatrizPeligrosPage /></ProtectedPage>} />
          <Route path="/planear/plan-anual" element={<ProtectedPage layout={false}><PlanAnualPage /></ProtectedPage>} />
          <Route path="/planear/plan-mejoramiento" element={<ProtectedPage layout={false}><PlanMejoramientoPage /></ProtectedPage>} />

          <Route path="/hacer/examenes-medicos" element={<ProtectedPage><ExamenesMedicosPage /></ProtectedPage>} />
          <Route path="/hacer/epp" element={<ProtectedPage><EPPPage /></ProtectedPage>} />
          <Route path="/hacer/capacitaciones" element={<ProtectedPage layout={false}><CapacitacionesPage /></ProtectedPage>} />
          <Route path="/hacer/inspecciones" element={<ProtectedPage><InspeccionesPage /></ProtectedPage>} />
          <Route path="/hacer/capa" element={<ProtectedPage><CAPAPage /></ProtectedPage>} />
          <Route path="/hacer/incidentes" element={<ProtectedPage><IncidentesPage /></ProtectedPage>} />
          <Route path="/hacer/accidentes" element={<ProtectedPage><IncidentesPage tipoInicial="ACCIDENTE" /></ProtectedPage>} />

          <Route path="/verificar/indicadores" element={<ProtectedPage><IndicadoresPage /></ProtectedPage>} />
          <Route path="/verificar/auditorias" element={<ProtectedPage layout={false}><AuditoriasPage /></ProtectedPage>} />
          <Route path="/verificar/notificaciones" element={<ProtectedPage><NotificacionesSSTPage /></ProtectedPage>} />
          <Route path="/verificar/revision-direccion" element={<ProtectedPage layout={false}><RevisionDireccionPage /></ProtectedPage>} />
          <Route path="/verificar/revision-direccion/versiones" element={<ProtectedPage layout={false}><RevisionVersionesPage /></ProtectedPage>} />
          <Route path="/verificar/reportes-anonimos" element={<ProtectedPage><ReportesAnonimosSSTPage /></ProtectedPage>} />
          <Route path="/verificar/mis-casos-sst" element={<ProtectedPage><MisCasosSSTPage /></ProtectedPage>} />
          <Route path="/verificar/acciones-correctivas" element={<ProtectedPage><MedidasCorrectivasPage /></ProtectedPage>} />

          <Route path="/documental/control" element={<ProtectedPage layout={false}><CentroControlDocumentalPage /></ProtectedPage>} />
          <Route path="/documental/biblioteca" element={<ProtectedPage layout={false}><BibliotecaDocumentalPage /></ProtectedPage>} />
          <Route path="/documental/firma-digital" element={<ProtectedPage><FirmaDocumentalPage /></ProtectedPage>} />

          <Route path="/admin/usuarios-sistema" element={<ProtectedPage roles={["SUPER_ADMIN"]}><UsuariosSistemaPage /></ProtectedPage>} />
          <Route path="/admin/roles" element={<ProtectedPage roles={["SUPER_ADMIN"]}><RolesSistemaPage /></ProtectedPage>} />
          <Route path="/admin/permisos" element={<ProtectedPage roles={["SUPER_ADMIN"]}><PermisosSistemaPage /></ProtectedPage>} />
          <Route path="/admin/auditoria" element={<ProtectedPage roles={["SUPER_ADMIN"]}><AuditoriaSistemaPage /></ProtectedPage>} />
          <Route path="/admin/auditoria-evidencias" element={<ProtectedPage roles={["SUPER_ADMIN", "AUDITOR"]}><AuditoriaEvidenciasPage /></ProtectedPage>} />
          <Route path="/admin/configuracion" element={<ProtectedPage roles={["SUPER_ADMIN"]}><ConfiguracionSistemaPage /></ProtectedPage>} />

          <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
