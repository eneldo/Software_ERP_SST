from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.auth.auth_handler import decode_access_token
from app.core.metrics import observe_http_request

logger = logging.getLogger("app.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Add request id, measure latency, emit structured access logs and metrics."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        started = time.perf_counter()
        log_extra = self._log_extra(request, request_id)

        try:
            response: Response = await call_next(request)
        except Exception:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            observe_http_request(method=request.method, path=request.url.path, status_code=500)
            logger.exception(
                "Unhandled request error method=%s path=%s elapsed_ms=%s",
                request.method,
                request.url.path,
                elapsed_ms,
                extra=log_extra,
            )
            raise

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-ms"] = str(elapsed_ms)

        status = getattr(response, "status_code", 0)
        observe_http_request(method=request.method, path=request.url.path, status_code=status)

        log_method = logger.warning if status >= 400 else logger.info
        log_method(
            "HTTP %s method=%s path=%s elapsed_ms=%s",
            status,
            request.method,
            request.url.path,
            elapsed_ms,
            extra=log_extra,
        )

        return response

    def _log_extra(self, request: Request, request_id: str) -> dict[str, str]:
        usuario_id, empresa_id = self._extract_identity(request)
        return {
            "request_id": request_id,
            "user_id": str(usuario_id) if usuario_id is not None else "-",
            "empresa_id": str(empresa_id) if empresa_id is not None else "-",
            "route": request.url.path,
        }

    def _extract_identity(self, request: Request) -> tuple[int | None, int | None]:
        authorization = request.headers.get("authorization")
        if not authorization or not authorization.lower().startswith("bearer "):
            return None, None

        token = authorization.split(" ", 1)[1].strip()
        if not token:
            return None, None

        try:
            payload = decode_access_token(token)
        except Exception:
            return None, None

        if not payload:
            return None, None

        return self._safe_int(payload.get("user_id") or payload.get("sub")), self._safe_int(payload.get("empresa_id"))

    def _safe_int(self, value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except Exception:
            return None
