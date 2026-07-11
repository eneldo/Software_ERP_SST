from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.metrics import increment_metric


@dataclass(frozen=True)
class RateLimitPolicy:
    name: str
    requests: int
    window_seconds: int


class RateLimitStore(Protocol):
    def hit(self, key: str, window_seconds: int) -> tuple[int, int]:
        """Return current hit count and retry-after seconds."""


class MemoryRateLimitStore:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def hit(self, key: str, window_seconds: int) -> tuple[int, int]:
        now = time.monotonic()
        bucket = self._hits[key]
        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()
        bucket.append(now)
        retry_after = max(1, int(window_seconds - (now - bucket[0])))
        return len(bucket), retry_after


class RedisRateLimitStore:
    def __init__(self, redis_url: str | None, prefix: str) -> None:
        if not redis_url:
            raise RuntimeError("RATE_LIMIT_REDIS_URL es obligatorio cuando RATE_LIMIT_BACKEND=redis.")
        try:
            from redis import Redis
        except ImportError as exc:
            raise RuntimeError("Instale redis para usar RATE_LIMIT_BACKEND=redis.") from exc

        self._client = Redis.from_url(redis_url, decode_responses=True)
        self._prefix = prefix.rstrip(":")

    def hit(self, key: str, window_seconds: int) -> tuple[int, int]:
        redis_key = f"{self._prefix}:{key}"
        pipe = self._client.pipeline()
        pipe.incr(redis_key)
        pipe.ttl(redis_key)
        count, ttl = pipe.execute()

        if int(ttl) < 0:
            self._client.expire(redis_key, window_seconds)
            ttl = window_seconds

        return int(count), max(1, int(ttl))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limit por IP con Redis para produccion y memoria para desarrollo."""

    def __init__(
        self,
        app,
        *,
        store: RateLimitStore,
        default_policy: RateLimitPolicy,
        login_policy: RateLimitPolicy,
        public_report_policy: RateLimitPolicy,
        upload_policy: RateLimitPolicy,
    ) -> None:
        super().__init__(app)
        self.store = store
        self.default_policy = default_policy
        self.login_policy = login_policy
        self.public_report_policy = public_report_policy
        self.upload_policy = upload_policy

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        if request.client:
            return request.client.host
        return "unknown"

    def _policy_for_path(self, method: str, path: str) -> RateLimitPolicy | None:
        if path in {"/health", "/"}:
            return None

        path_lower = path.lower()
        method_upper = method.upper()

        if path_lower.startswith("/auth/login"):
            return self.login_policy

        if path_lower.startswith("/reporte-anonimo-sst"):
            return self.public_report_policy

        if (
            method_upper in {"POST", "PUT", "PATCH"}
            and (
                "upload" in path_lower
                or "evidencia" in path_lower
                or "archivo" in path_lower
                or path_lower.startswith("/uploads")
            )
        ):
            return self.upload_policy

        return self.default_policy

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        policy = self._policy_for_path(request.method, request.url.path)
        if policy is None:
            return await call_next(request)

        key = f"{policy.name}:{self._client_key(request)}"
        count, retry_after = self.store.hit(key, policy.window_seconds)

        if count > policy.requests:
            increment_metric("rate_limit_exceeded_total")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Demasiadas solicitudes. Intente nuevamente en unos segundos.",
                    "code": "RATE_LIMIT_EXCEEDED",
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)


__all__ = [
    "MemoryRateLimitStore",
    "RateLimitMiddleware",
    "RateLimitPolicy",
    "RedisRateLimitStore",
]
