# ============================================================
# REQUEST CONTEXT MIDDLEWARE - ERP SST PRO ENTERPRISE
# FASE 36.8 — Logging Enterprise y Manejo de Errores
# Archivo: backend/app/middlewares/request_context.py
# ============================================================

from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Agrega X-Request-ID, mide tiempo y registra accesos relevantes."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        started = time.perf_counter()

        try:
            response: Response = await call_next(request)
        except Exception:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.exception(
                "Unhandled request error method=%s path=%s elapsed_ms=%s",
                request.method,
                request.url.path,
                elapsed_ms,
                extra={"request_id": request_id},
            )
            raise

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-ms"] = str(elapsed_ms)

        status = getattr(response, "status_code", 0)
        if status >= 400:
            logger.warning(
                "HTTP %s method=%s path=%s elapsed_ms=%s",
                status,
                request.method,
                request.url.path,
                elapsed_ms,
                extra={"request_id": request_id},
            )
        else:
            logger.info(
                "HTTP %s method=%s path=%s elapsed_ms=%s",
                status,
                request.method,
                request.url.path,
                elapsed_ms,
                extra={"request_id": request_id},
            )

        return response
