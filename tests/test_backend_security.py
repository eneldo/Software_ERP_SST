from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
import asyncio
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
TMP = Path(tempfile.mkdtemp(prefix="sst_backend_tests_"))

os.environ.setdefault("DATABASE_URL", f"sqlite:///{TMP / 'test.db'}")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-automated-suite-123456789")
os.environ.setdefault("AUTO_CREATE_TABLES", "false")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
os.environ.setdefault("SECURITY_HEADERS_ENABLED", "false")
os.environ.setdefault("UPLOAD_DIR", str(TMP / "uploads"))
os.environ.setdefault("LOG_DIR", str(TMP / "logs"))

sys.path.insert(0, str(BACKEND))

from app.auth.auth_handler import create_access_token, create_refresh_token  # noqa: E402
from app.core.metrics import metrics_snapshot  # noqa: E402
from app.core.roles import ROLES_SISTEMA  # noqa: E402
from app.middlewares.rate_limit import (  # noqa: E402
    MemoryRateLimitStore,
    RateLimitMiddleware,
    RateLimitPolicy,
)
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.auditoria import Auditoria  # noqa: E402
from app.models.empleado import Empleado  # noqa: E402
from app.models.empresa import Empresa  # noqa: E402
from app.models.evaluacion_inicial import EvaluacionInicialItemSST, EvaluacionInicialSST  # noqa: E402
from app.models.plan_mejoramiento import PlanMejoramientoSST  # noqa: E402
from app.models.permiso import Permiso  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402
from app.models.usuario_permiso import UsuarioPermiso  # noqa: E402
from app.routers.portal_empleado import _asegurar_contexto_reporte, _buscar_empleado_contexto  # noqa: E402
from app.routers.indicadores_bi import _empresa_autorizada as empresa_bi_autorizada  # noqa: E402
from app.routers.revision_direccion import empresa_autorizada as empresa_revision_autorizada  # noqa: E402
from app.routers.permisos import actualizar_permiso, crear_permiso, eliminar_permiso  # noqa: E402
from app.schemas.permiso_schema import PermisoCreate, PermisoUpdate  # noqa: E402


class AsgiResponse:
    def __init__(self, status_code: int, body: bytes, headers: list[tuple[bytes, bytes]]) -> None:
        self.status_code = status_code
        self.content = body
        self.headers = {key.decode().lower(): value.decode() for key, value in headers}

    def json(self):
        return json.loads(self.content.decode("utf-8"))


class MiniAsgiClient:
    def __init__(self, app) -> None:
        self.app = app

    def get(self, path: str, *, headers: dict[str, str] | None = None) -> AsgiResponse:
        return self.request("GET", path, headers=headers)

    def delete(
        self,
        path: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> AsgiResponse:
        return self.request("DELETE", path, params=params, headers=headers)

    def post_multipart(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        field_name: str,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> AsgiResponse:
        boundary = "----sst-test-boundary"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("utf-8")
        merged_headers = {
            **(headers or {}),
            "content-type": f"multipart/form-data; boundary={boundary}",
            "content-length": str(len(body)),
        }
        return self.request("POST", path, headers=merged_headers, body=body)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        body: bytes = b"",
    ) -> AsgiResponse:
        return asyncio.run(self._request(method, path, params=params, headers=headers, body=body))

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None,
        headers: dict[str, str] | None,
        body: bytes,
    ) -> AsgiResponse:
        import urllib.parse

        query = urllib.parse.urlencode(params or {}).encode("ascii")
        request_headers = {"host": "localhost", **(headers or {})}
        raw_headers = [(key.lower().encode("latin-1"), value.encode("latin-1")) for key, value in request_headers.items()]
        messages: list[dict] = []
        sent = False

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method.upper(),
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("ascii"),
            "query_string": query,
            "headers": raw_headers,
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
        }

        async def receive():
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            messages.append(message)

        await self.app(scope, receive, send)
        start = next(message for message in messages if message["type"] == "http.response.start")
        chunks = [message.get("body", b"") for message in messages if message["type"] == "http.response.body"]
        return AsgiResponse(start["status"], b"".join(chunks), start.get("headers", []))


class BackendSecurityTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(TMP, ignore_errors=True)

    def setUp(self) -> None:
        self._drop_test_tables()
        self._create_test_tables()
        self.client = MiniAsgiClient(app)
        self.db = SessionLocal()

    def tearDown(self) -> None:
        self.db.close()

    def _create_test_tables(self) -> None:
        for model in (
            Empresa,
            Usuario,
            Empleado,
            Auditoria,
            EvaluacionInicialSST,
            EvaluacionInicialItemSST,
            PlanMejoramientoSST,
            Permiso,
            UsuarioPermiso,
        ):
            model.__table__.create(bind=engine, checkfirst=True)

    def _drop_test_tables(self) -> None:
        for model in (
            UsuarioPermiso,
            Permiso,
            PlanMejoramientoSST,
            EvaluacionInicialItemSST,
            EvaluacionInicialSST,
            Auditoria,
            Empleado,
            Usuario,
            Empresa,
        ):
            model.__table__.drop(bind=engine, checkfirst=True)

    def _empresa(self, nombre: str, nit: str) -> Empresa:
        empresa = Empresa(nombre=nombre, nit=nit, estado=True)
        self.db.add(empresa)
        self.db.commit()
        self.db.refresh(empresa)
        return empresa

    def _usuario(self, *, rol: str, empresa_id: int | None = None) -> Usuario:
        usuario = Usuario(
            nombres="Test",
            apellidos=rol,
            correo=f"{rol.lower()}-{empresa_id or 'global'}@example.com",
            password="hash-no-login",
            rol=rol,
            empresa_id=empresa_id,
            activo=True,
        )
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def _empleado(self, *, empresa_id: int, documento: str, correo: str | None = None) -> Empleado:
        empleado = Empleado(
            nombres="Empleado",
            apellidos=documento,
            documento=documento,
            correo=correo,
            empresa_id=empresa_id,
            activo=True,
        )
        self.db.add(empleado)
        self.db.commit()
        self.db.refresh(empleado)
        return empleado

    def _headers(self, usuario: Usuario) -> dict[str, str]:
        token = create_access_token(
            {
                "user_id": usuario.id,
                "correo": usuario.correo,
                "rol": usuario.rol,
                "empresa_id": usuario.empresa_id,
            }
        )
        return {"Authorization": f"Bearer {token}"}

    def test_endpoint_privado_sin_token_responde_401(self) -> None:
        response = self.client.get("/empresas/")
        self.assertEqual(response.status_code, 401)

    def test_refresh_token_no_autoriza_endpoint_privado(self) -> None:
        empresa = self._empresa("Empresa A", "A-REFRESH")
        usuario = self._usuario(rol="ADMIN_EMPRESA", empresa_id=empresa.id)
        token = create_refresh_token(
            {
                "user_id": usuario.id,
                "correo": usuario.correo,
                "rol": usuario.rol,
                "empresa_id": usuario.empresa_id,
            }
        )

        response = self.client.get("/empresas/", headers={"Authorization": f"Bearer {token}"})

        self.assertEqual(response.status_code, 401)

    def test_usuario_empresa_a_no_puede_leer_empresa_b(self) -> None:
        empresa_a = self._empresa("Empresa A", "A-001")
        empresa_b = self._empresa("Empresa B", "B-001")
        usuario_a = self._usuario(rol="ADMIN_EMPRESA", empresa_id=empresa_a.id)

        response = self.client.get(f"/empresas/{empresa_b.id}", headers=self._headers(usuario_a))

        self.assertEqual(response.status_code, 403)

    def test_dashboard_separa_criticas_de_sin_evaluacion(self) -> None:
        empresa_evaluada = self._empresa("Empresa Evaluada", "EVAL-001")
        empresa_sin_evaluar = self._empresa("Empresa Sin Evaluar", "EVAL-002")
        empresa_evaluada.total_estandares_sst = 2
        empresa_sin_evaluar.total_estandares_sst = 2

        evaluacion = EvaluacionInicialSST(
            empresa_id=empresa_evaluada.id,
            codigo="EVAL-DASHBOARD",
            nombre="Evaluacion dashboard",
            activo=True,
        )
        evaluacion.items = [
            EvaluacionInicialItemSST(
                estandar="E1",
                criterio="Cumple",
                respuesta="CUMPLE",
                activo=True,
            ),
            EvaluacionInicialItemSST(
                estandar="E2",
                criterio="No cumple",
                respuesta="NO_CUMPLE",
                activo=True,
            ),
        ]
        self.db.add(evaluacion)
        self.db.add_all([
            PlanMejoramientoSST(
                empresa_id=empresa_evaluada.id,
                codigo="PM-DASH-1",
                titulo="Accion empresa evaluada",
                accion_correctiva="Corregir hallazgo",
                estado="VENCIDO",
                activo=True,
            ),
            PlanMejoramientoSST(
                empresa_id=empresa_sin_evaluar.id,
                codigo="PM-DASH-2",
                titulo="Accion empresa sin evaluar",
                accion_correctiva="Completar evaluacion",
                estado="PENDIENTE",
                activo=True,
            ),
        ])
        self.db.commit()
        super_admin = self._usuario(rol="SUPER_ADMIN")

        response = self.client.get(
            "/dashboard-sst/resumen",
            headers=self._headers(super_admin),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["empresas_criticas"], 1)
        self.assertEqual(payload["empresas_sin_evaluacion"], 1)
        self.assertEqual(payload["empresas_evaluadas"], 1)
        self.assertEqual(payload["promedio_general"], 50.0)
        self.assertEqual(payload["cobertura_evaluacion"], 50.0)
        self.assertEqual(payload["total_acciones"], 2)
        self.assertEqual(payload["acciones_vencidas"], 1)

    def test_super_admin_abre_portal_con_primer_empleado_activo(self) -> None:
        empresa = self._empresa("Empresa Portal", "PORTAL-001")
        empleado = self._empleado(empresa_id=empresa.id, documento="EMP-PORTAL-1")
        super_admin = self._usuario(rol="SUPER_ADMIN")

        encontrado = _buscar_empleado_contexto(self.db, super_admin)

        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.id, empleado.id)

    def test_admin_empresa_no_puede_seleccionar_empleado_ajeno(self) -> None:
        empresa_a = self._empresa("Empresa Portal A", "PORTAL-A")
        empresa_b = self._empresa("Empresa Portal B", "PORTAL-B")
        self._empleado(empresa_id=empresa_a.id, documento="EMP-PORTAL-A")
        empleado_b = self._empleado(empresa_id=empresa_b.id, documento="EMP-PORTAL-B")
        admin_a = self._usuario(rol="ADMIN_EMPRESA", empresa_id=empresa_a.id)

        encontrado = _buscar_empleado_contexto(self.db, admin_a, empleado_b.id)

        self.assertIsNone(encontrado)

    def test_trabajador_sin_correo_asociado_no_recibe_otro_empleado(self) -> None:
        empresa = self._empresa("Empresa Portal Privado", "PORTAL-PRIV")
        self._empleado(empresa_id=empresa.id, documento="EMP-AJENO")
        trabajador = self._usuario(rol="TRABAJADOR", empresa_id=empresa.id)

        encontrado = _buscar_empleado_contexto(self.db, trabajador)

        self.assertIsNone(encontrado)

    def test_catalogo_incluye_roles_participativos_y_trabajador(self) -> None:
        for rol in ("ALTA_DIRECCION", "REPRESENTANTE_LEGAL", "COPASST", "VIGIA_SST", "TRABAJADOR", "CONTRATISTA"):
            self.assertIn(rol, ROLES_SISTEMA)

    def test_coordinador_hereda_acceso_de_responsable_sst(self) -> None:
        empresa = self._empresa("Empresa Coordinador", "COORD-001")
        coordinador = self._usuario(rol="COORDINADOR_SST", empresa_id=empresa.id)

        response = self.client.get("/empresas/", headers=self._headers(coordinador))

        self.assertEqual(response.status_code, 200)

    def test_indicadores_y_revision_rechazan_empresa_ajena(self) -> None:
        empresa_a = self._empresa("Empresa Alcance A", "SCOPE-A")
        empresa_b = self._empresa("Empresa Alcance B", "SCOPE-B")
        responsable = self._usuario(rol="RESPONSABLE_SST", empresa_id=empresa_a.id)

        with self.assertRaises(Exception) as bi_error:
            empresa_bi_autorizada(responsable, empresa_b.id)
        self.assertEqual(getattr(bi_error.exception, "status_code", None), 403)

        with self.assertRaises(Exception) as revision_error:
            empresa_revision_autorizada(responsable, empresa_b.id)
        self.assertEqual(getattr(revision_error.exception, "status_code", None), 403)

    def test_contexto_reporte_usa_datos_del_empleado_resuelto(self) -> None:
        empresa_a = self._empresa("Empresa Portal Contexto A", "PORTAL-CTX-A")
        empresa_b = self._empresa("Empresa Portal Contexto B", "PORTAL-CTX-B")
        empleado_a = self._empleado(empresa_id=empresa_a.id, documento="EMP-CTX-A")
        admin_a = self._usuario(rol="ADMIN_EMPRESA", empresa_id=empresa_a.id)

        payload = _asegurar_contexto_reporte(
            self.db,
            admin_a,
            {
                "empleado_id": empleado_a.id,
                "empresa_id": empresa_b.id,
                "sede_id": None,
                "area_id": None,
                "cargo_id": None,
            },
        )

        self.assertEqual(payload["empleado_id"], empleado_a.id)
        self.assertEqual(payload["empresa_id"], empresa_a.id)

    def test_permisos_tienen_ciclo_crud_completo(self) -> None:
        super_admin = self._usuario(rol="SUPER_ADMIN")
        creado = crear_permiso(
            PermisoCreate(codigo="PRUEBA_CRUD", nombre="Permiso prueba", modulo="PRUEBAS"),
            self.db,
            super_admin,
        )

        actualizado = actualizar_permiso(
            creado.id,
            PermisoUpdate(nombre="Permiso actualizado", activo=True),
            self.db,
            super_admin,
        )
        self.assertEqual(actualizado.nombre, "Permiso actualizado")

        eliminado = eliminar_permiso(creado.id, self.db, super_admin)
        self.assertEqual(eliminado["permiso_id"], creado.id)
        self.db.refresh(creado)
        self.assertFalse(creado.activo)

    def test_upload_rechaza_extension_y_mime_invalidos(self) -> None:
        empresa = self._empresa("Empresa Upload", "UP-001")
        super_admin = self._usuario(rol="SUPER_ADMIN")
        before = metrics_snapshot().get("uploads_rejected_total", 0)

        response = self.client.post_multipart(
            f"/empresas/{empresa.id}/logo",
            headers=self._headers(super_admin),
            field_name="file",
            filename="malware.exe",
            content=b"MZ fake executable",
            content_type="application/x-msdownload",
        )

        self.assertEqual(response.status_code, 400)
        after = metrics_snapshot().get("uploads_rejected_total", 0)
        self.assertGreaterEqual(after, before + 1)

    def test_rate_limit_store_en_memoria_calcula_reintento(self) -> None:
        store = MemoryRateLimitStore()

        first_count, first_retry_after = store.hit("login:127.0.0.1", 60)
        second_count, second_retry_after = store.hit("login:127.0.0.1", 60)

        self.assertEqual(first_count, 1)
        self.assertEqual(second_count, 2)
        self.assertGreaterEqual(first_retry_after, 1)
        self.assertGreaterEqual(second_retry_after, 1)

    def test_rate_limit_publico_solo_cuenta_envios_reales(self) -> None:
        policy = RateLimitPolicy("test", 10, 60)
        middleware = RateLimitMiddleware(
            object(),
            store=MemoryRateLimitStore(),
            default_policy=RateLimitPolicy("default", 120, 60),
            login_policy=RateLimitPolicy("login", 5, 60),
            public_report_policy=policy,
            upload_policy=RateLimitPolicy("upload", 20, 60),
        )

        self.assertIsNone(
            middleware._policy_for_path("GET", "/reporte-anonimo-sst/opciones")
        )
        self.assertIsNone(
            middleware._policy_for_path("OPTIONS", "/reporte-anonimo-sst/reportes")
        )
        self.assertIs(
            middleware._policy_for_path("POST", "/reporte-anonimo-sst/reportes"),
            policy,
        )

    def test_eliminacion_inteligente_respeta_dependencias(self) -> None:
        empresa = self._empresa("Empresa Dependencias", "DEP-001")
        empleado = Empleado(
            nombres="Ana",
            apellidos="Dependencia",
            documento="10000001",
            empresa_id=empresa.id,
            activo=True,
        )
        self.db.add(empleado)
        self.db.commit()
        super_admin = self._usuario(rol="SUPER_ADMIN")

        response = self.client.delete(
            f"/integridad/eliminacion/empresa/{empresa.id}",
            params={"confirmar": "true"},
            headers=self._headers(super_admin),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["action"], "INACTIVATE")
        self.assertFalse(payload["can_delete"])
        self.assertTrue(payload["was_inactivated"])

        self.db.refresh(empresa)
        self.assertFalse(empresa.estado)


if __name__ == "__main__":
    unittest.main()
