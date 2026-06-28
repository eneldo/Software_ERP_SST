# ============================================================
# MIDDLEWARE ENTERPRISE DE AUDITORÍA Y TRAZABILIDAD
# ERP SST PRO - FASE 36.8.1
# Archivo: backend/app/middlewares/audit_middleware.py
# ============================================================

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Awaitable, Callable, Optional

from sqlalchemy.orm import Session
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.auth.auth_handler import decode_access_token
from app.database import SessionLocal
from app.models.auditoria import Auditoria

logger = logging.getLogger("app.audit")


class AuditMiddleware:
    """
    Middleware ASGI nativo para auditoría Enterprise.

    Motivo del cambio:
    - Evita el AssertionError generado por BaseHTTPMiddleware + call_next
      en FastAPI/Starlette recientes, especialmente en Docker/Python 3.12.
    - No interrumpe la respuesta del usuario si falla la auditoría.
    - Agrega X-Request-ID para trazabilidad.
    - Registra método, ruta, IP, user-agent, usuario, empresa y status HTTP.

    Importante:
    - Este middleware no debe lanzar errores hacia la aplicación por fallos
      de auditoría o base de datos.
    - Solo re-lanza errores reales de la aplicación después de registrar
      intento de auditoría con status 500.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.skip_prefixes = (
            "/docs",
            "/redoc",
            "/openapi",
            "/favicon.ico",
            "/uploads",
            "/static",
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        path = str(scope.get("path") or "")
        method = str(scope.get("method") or "")
        start_time = time.perf_counter()
        request_id = self._get_header(scope, b"x-request-id") or str(uuid.uuid4())
        status_code_holder: dict[str, Optional[int]] = {"status_code": None}

        async def send_wrapper(message: Message) -> None:
            if message.get("type") == "http.response.start":
                status_code_holder["status_code"] = int(message.get("status", 0) or 0)

                headers = list(message.get("headers") or [])
                if not any(k.lower() == b"x-request-id" for k, _ in headers):
                    headers.append((b"x-request-id", request_id.encode("utf-8")))
                message["headers"] = headers

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            self._safe_register_audit(
                scope=scope,
                request_id=request_id,
                status_code=500,
                elapsed_ms=elapsed_ms,
                error=True,
            )
            logger.exception(
                "Unhandled backend exception request_id=%s method=%s path=%s elapsed_ms=%s",
                request_id,
                method,
                path,
                elapsed_ms,
            )
            raise
        else:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            status_code = status_code_holder.get("status_code") or 200
            self._safe_register_audit(
                scope=scope,
                request_id=request_id,
                status_code=status_code,
                elapsed_ms=elapsed_ms,
                error=False,
            )
            logger.info(
                "HTTP %s method=%s path=%s request_id=%s elapsed_ms=%s",
                status_code,
                method,
                path,
                request_id,
                elapsed_ms,
            )

    def _safe_register_audit(
        self,
        *,
        scope: Scope,
        request_id: str,
        status_code: int,
        elapsed_ms: float,
        error: bool,
    ) -> None:
        path = str(scope.get("path") or "")
        method = str(scope.get("method") or "")

        if self._should_skip(path):
            return

        db: Optional[Session] = None
        try:
            usuario_id, empresa_id = self._extract_identity(scope)
            db = SessionLocal()

            accion_base = f"{method} {path}"
            if error:
                accion_base = f"ERROR {accion_base}"

            registro = Auditoria(
                usuario_id=usuario_id,
                empresa_id=empresa_id,
                metodo=self._truncate(method, 20),
                ruta=self._truncate(path, 255),
                accion=self._truncate(accion_base, 100),
                ip=self._truncate(self._get_client_ip(scope), 80),
                user_agent=self._truncate(self._get_header(scope, b"user-agent"), 1000),
                status_code=status_code,
            )

            db.add(registro)
            db.commit()

            logger.debug(
                "Audit stored request_id=%s status=%s path=%s elapsed_ms=%s",
                request_id,
                status_code,
                path,
                elapsed_ms,
            )
        except Exception:
            if db is not None:
                try:
                    db.rollback()
                except Exception:
                    pass
            logger.exception(
                "Audit middleware could not store event request_id=%s method=%s path=%s",
                request_id,
                method,
                path,
            )
        finally:
            if db is not None:
                try:
                    db.close()
                except Exception:
                    pass

    def _extract_identity(self, scope: Scope) -> tuple[Optional[int], Optional[int]]:
        authorization = self._get_header(scope, b"authorization")
        if not authorization or not authorization.lower().startswith("bearer "):
            return None, None

        token = authorization.split(" ", 1)[1].strip()
        if not token:
            return None, None

        try:
            payload: Optional[dict[str, Any]] = decode_access_token(token)
        except Exception:
            return None, None

        if not payload:
            return None, None

        usuario_id = payload.get("user_id") or payload.get("usuario_id") or payload.get("sub")
        empresa_id = payload.get("empresa_id")

        return self._safe_int(usuario_id), self._safe_int(empresa_id)

    def _get_client_ip(self, scope: Scope) -> Optional[str]:
        forwarded_for = self._get_header(scope, b"x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",", 1)[0].strip()

        real_ip = self._get_header(scope, b"x-real-ip")
        if real_ip:
            return real_ip.strip()

        client = scope.get("client")
        if isinstance(client, (list, tuple)) and client:
            return str(client[0])

        return None

    def _get_header(self, scope: Scope, name: bytes) -> Optional[str]:
        headers = scope.get("headers") or []
        name_lower = name.lower()
        for key, value in headers:
            if key.lower() == name_lower:
                try:
                    return value.decode("utf-8", errors="ignore")
                except Exception:
                    return None
        return None

    def _should_skip(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self.skip_prefixes)

    def _truncate(self, value: Optional[Any], max_length: int) -> Optional[str]:
        if value is None:
            return None
        text = str(value)
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    def _safe_int(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except Exception:
            return None
