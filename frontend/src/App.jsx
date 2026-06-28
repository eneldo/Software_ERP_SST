import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import RequireAuth from "./components/auth/RequireAuth";
import RequireRole from "./components/auth/RequireRole";
import LoginPage from "./pages/auth/LoginPage";
import EmpresasSSTPage from "./pages/organizacion/EmpresasSSTPage";
import SedesSSTPage from "./pages/organizacion/SedesSSTPage";
import AreasSSTPage from "./pages/organizacion/AreasSSTPage";
import CargosSSTPage from "./pages/organizacion/CargosSSTPage";
import EmpleadosSSTPage from "./pages/organizacion/EmpleadosSSTPage";
import AdminLayout from "./layouts/AdminLayout";

import DashboardEjecutivoSST from "./pages/admin/DashboardEjecutivoSST";
import UsuariosSistemaPage from "./pages/admin/UsuariosSistemaPage";
import RolesSistemaPage from "./pages/admin/RolesSistemaPage";
import PermisosSistemaPage from "./pages/admin/PermisosSistemaPage";
import AuditoriaSistemaPage from "./pages/admin/AuditoriaSistemaPage";
import ConfiguracionSistemaPage from "./pages/admin/ConfiguracionSistemaPage";

import PoliticaSSTPage from "./pages/planear/PoliticaSSTPage";
import ObjetivosSSTPage from "./pages/planear/ObjetivosSSTPage";
import EvaluacionInicialPage from "./pages/planear/EvaluacionInicialPage";
import MatrizLegalPage from "./pages/planear/MatrizLegalPage";
import MatrizPeligrosPage from "./pages/planear/MatrizPeligrosPage";
import PlanAnualPage from "./pages/planear/PlanAnualPage";
import PlanMejoramientoPage from "./pages/planear/PlanMejoramientoPage";
import ExamenesMedicosPage from "./pages/hacer/ExamenesMedicosSSTPage";
import EPPPage from "./pages/hacer/EPPPage";
import InspeccionesPage from "./pages/hacer/InspeccionesPage";
import CAPAPage from "./pages/hacer/CAPAPage";
import IncidentesPage from "./pages/hacer/IncidentesPage";

import CapacitacionesPage from "./pages/hacer/CapacitacionesPage";

import AuditoriasPage from "./pages/verificar/AuditoriasPage";
import RevisionDireccionPage from "./pages/verificar/RevisionDireccionPage";
import IndicadoresPage from "./pages/verificar/IndicadoresPage";

import BibliotecaDocumentalPage from "./pages/documental/BibliotecaDocumentalPage";
import CentroControlDocumentalPage from "./pages/documental/CentroControlDocumentalPage";
import FirmaDocumentalPage from "./pages/documental/FirmaDocumentalPage";
import NotificacionesSSTPage from "./pages/verificar/NotificacionesSSTPage";

import RevisionVersionesPage from "./pages/verificar/RevisionVersionesPage";
import PortalEmpleadoPage from "./pages/portal/PortalEmpleadoPage";
import ReporteAnonimoSSTPage from "./pages/public/ReporteAnonimoSSTPage";
import ReportesAnonimosSSTPage from "./pages/verificar/ReportesAnonimosSSTPage";
import MisCasosSSTPage from "./pages/verificar/MisCasosSSTPage";
import AuditoriaEvidenciasPage from "./pages/admin/AuditoriaEvidenciasPage";
import MedidasCorrectivasPage from './pages/sst/MedidasCorrectivasPage';
import InspeccionPdfPlatinumButton from "./components/inspecciones/InspeccionPdfPlatinumButtons";



/* NUEVO */
import VerificarDocumento from "./pages/public/VerificarDocumento";


export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* LOGIN */}
        <Route path="/" element={<LoginPage />} />

        {/* PORTAL PÚBLICO DE VALIDACIÓN */}
        <Route path="/verificar-documento" element={<VerificarDocumento />} />

        <Route
          path="/verificar-documento/:codigo"
          element={<VerificarDocumento />}
        />
        <Route path="/reporte-sst" element={<ReporteAnonimoSSTPage />} />

        <Route
          path="/verificar/reportes-anonimos"
          element={
            <RequireAuth>
              <AdminLayout>
                <ReportesAnonimosSSTPage />
              </AdminLayout>
            </RequireAuth>
          }
        />

        <Route
          path="/verificar/mis-casos-sst"
          element={
            <RequireAuth>
              <AdminLayout>
                <MisCasosSSTPage />
              </AdminLayout>
            </RequireAuth>
          }
        />

        {/* DASHBOARD */}
        <Route
          path="/admin/dashboard"
          element={
            <RequireAuth>
              <DashboardEjecutivoSST />
            </RequireAuth>
          }
        />

        <Route
          path="/portal-empleado"
          element={
            <RequireAuth>
              <AdminLayout>
                <PortalEmpleadoPage />
              </AdminLayout>
            </RequireAuth>
          }
        />

        <Route
          path="/organizacion/empresas"
          element={
            <RequireAuth>
              <AdminLayout>
                <EmpresasSSTPage />
              </AdminLayout>
            </RequireAuth>
          }
        />

        <Route
          path="/organizacion/sedes"
          element={
            <RequireAuth>
              <AdminLayout>
                <SedesSSTPage />
              </AdminLayout>
            </RequireAuth>
          }
        />

        <Route
          path="/organizacion/areas"
          element={
            <RequireAuth>
              <AdminLayout>
                <AreasSSTPage />
              </AdminLayout>
            </RequireAuth>
          }
        />

        <Route
          path="/organizacion/cargos"
          element={
            <RequireAuth>
              <AdminLayout>
                <CargosSSTPage />
              </AdminLayout>
            </RequireAuth>
          }
        />

        <Route
          path="/organizacion/empleados"
          element={
            <RequireAuth>
              <AdminLayout>
                <EmpleadosSSTPage />
              </AdminLayout>
            </RequireAuth>
          }
        />
        <Route
          path="/hacer/examenes-medicos"
          element={
            <RequireAuth>
              <AdminLayout>
                <ExamenesMedicosPage />
              </AdminLayout>
            </RequireAuth>
          }
        />

        {/* PLANEAR */}
        <Route
          path="/planear/politica-sst"
          element={
            <RequireAuth>
              <PoliticaSSTPage />
            </RequireAuth>
          }
        />

        <Route
          path="/planear/objetivos-sst"
          element={
            <RequireAuth>
              <ObjetivosSSTPage />
            </RequireAuth>
          }
        />

        <Route
          path="/planear/evaluacion-inicial"
          element={
            <RequireAuth>
              <EvaluacionInicialPage />
            </RequireAuth>
          }
        />

        <Route
          path="/planear/matriz-legal"
          element={
            <RequireAuth>
              <MatrizLegalPage />
            </RequireAuth>
          }
        />

        <Route
          path="/planear/matriz-peligros"
          element={
            <RequireAuth>
              <MatrizPeligrosPage />
            </RequireAuth>
          }
        />

        <Route
          path="/planear/plan-anual"
          element={
            <RequireAuth>
              <PlanAnualPage />
            </RequireAuth>
          }
        />

        <Route
          path="/planear/plan-mejoramiento"
          element={
            <RequireAuth>
              <PlanMejoramientoPage />
            </RequireAuth>
          }
        />

        {/* HACER */}
        <Route
          path="/hacer/epp"
          element={
            <RequireAuth>
              <AdminLayout>
                <EPPPage />
              </AdminLayout>
            </RequireAuth>
          }
        />

        <Route
          path="/hacer/capacitaciones"
          element={
            <RequireAuth>
              <CapacitacionesPage />
            </RequireAuth>
          }
        />

        <Route
          path="/hacer/inspecciones"
          element={
            <RequireAuth>
              <AdminLayout>
                <InspeccionesPage />
              </AdminLayout>
            </RequireAuth>
          }
        />

        <Route
          path="/hacer/capa"
          element={
            <RequireAuth>
              <AdminLayout>
                <CAPAPage />
              </AdminLayout>
            </RequireAuth>
          }
        />

        <Route
          path="/hacer/incidentes"
          element={
            <RequireAuth>
              <AdminLayout>
                <IncidentesPage />
              </AdminLayout>
            </RequireAuth>
          }
        />
        {/* VERIFICAR */}

        <Route
          path="/verificar/indicadores"
          element={
            <RequireAuth>
              <AdminLayout>
                <IndicadoresPage />
              </AdminLayout>
            </RequireAuth>
          }
        />
        <Route
          path="/verificar/auditorias"
          element={
            <RequireAuth>
              <AuditoriasPage />
            </RequireAuth>
          }
        />
        <Route
          path="/verificar/notificaciones"
          element={
            <RequireAuth>
              <AdminLayout>
                <NotificacionesSSTPage />
              </AdminLayout>
            </RequireAuth>
          }
        />

        {/* DOCUMENTAL */}
        <Route
          path="/documental/control"
          element={
            <RequireAuth>
              <CentroControlDocumentalPage />
            </RequireAuth>
          }
        />

        <Route
          path="/documental/biblioteca"
          element={
            <RequireAuth>
              <BibliotecaDocumentalPage />
            </RequireAuth>
          }
        />

        <Route
          path="/documental/firma-digital"
          element={<FirmaDocumentalPage />}
        />

        {/* Verificar Revision de Dirección */}
        <Route
          path="/verificar/revision-direccion"
          element={
            <RequireAuth>
              <RevisionDireccionPage />
            </RequireAuth>
          }
        />

        <Route
          path="/verificar/revision-direccion/versiones"
          element={
            <RequireAuth>
              <RevisionVersionesPage />
            </RequireAuth>
          }
        />

        <Route
          path="/admin/usuarios-sistema"
          element={
            <RequireAuth>
              <RequireRole allowedRoles={["SUPER_ADMIN"]}>
                <AdminLayout>
                  <UsuariosSistemaPage />
                </AdminLayout>
              </RequireRole>
            </RequireAuth>
          }
        />

        <Route
          path="/admin/roles"
          element={
            <RequireAuth>
              <RequireRole allowedRoles={["SUPER_ADMIN"]}>
                <AdminLayout>
                  <RolesSistemaPage />
                </AdminLayout>
              </RequireRole>
            </RequireAuth>
          }
        />

        <Route
          path="/admin/permisos"
          element={
            <RequireAuth>
              <RequireRole allowedRoles={["SUPER_ADMIN"]}>
                <AdminLayout>
                  <PermisosSistemaPage />
                </AdminLayout>
              </RequireRole>
            </RequireAuth>
          }
        />

        <Route
          path="/admin/auditoria"
          element={
            <RequireAuth>
              <RequireRole allowedRoles={["SUPER_ADMIN"]}>
                <AdminLayout>
                  <AuditoriaSistemaPage />
                </AdminLayout>
              </RequireRole>
            </RequireAuth>
          }
        />
        <Route
          path="/admin/auditoria-evidencias"
          element={
            <RequireAuth>
              <RequireRole allowedRoles={["SUPER_ADMIN", "AUDITOR"]}>
                <AdminLayout>
                  <AuditoriaEvidenciasPage />
                </AdminLayout>
              </RequireRole>
            </RequireAuth>
          }
        />

        <Route
          path="/admin/configuracion"
          element={
            <RequireAuth>
              <RequireRole allowedRoles={["SUPER_ADMIN"]}>
                <AdminLayout>
                  <ConfiguracionSistemaPage />
                </AdminLayout>
              </RequireRole>
            </RequireAuth>
          }
        />

        <Route path='/verificar/acciones-correctivas' element={<RequireAuth><AdminLayout><MedidasCorrectivasPage /></AdminLayout></RequireAuth>} />

        {/* DEFAULT */}
        <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}