# ============================================================
# RATE LIMIT MIDDLEWARE - ERP SST PRO ENTERPRISE
# FASE 36.6 — Seguridad Enterprise Backend/Frontend
# Archivo: backend/app/middlewares/rate_limit.py
# ============================================================

from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limit simple por IP para protección base."""

    def __init__(self, app, requests: int = 120, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.requests = max(1, int(requests))
        self.window_seconds = max(1, int(window_seconds))
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        path = request.url.path
        if path.startswith("/uploads") or path in {"/health", "/"}:
            return await call_next(request)

        key = self._client_key(request)
        now = time.monotonic()
        bucket = self._hits[key]

        while bucket and now - bucket[0] > self.window_seconds:
            bucket.popleft()

        if len(bucket) >= self.requests:
            retry_after = max(1, int(self.window_seconds - (now - bucket[0])))
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Demasiadas solicitudes. Intente nuevamente en unos segundos.",
                    "code": "RATE_LIMIT_EXCEEDED",
                },
                headers={"Retry-After": str(retry_after)},
            )

        bucket.append(now)
        return await call_next(request)
