from __future__ import annotations

from collections import Counter
from threading import Lock
from typing import Any


_LOCK = Lock()
_COUNTERS: Counter[str] = Counter()


def increment_metric(name: str, amount: int = 1) -> None:
    if amount <= 0:
        return
    with _LOCK:
        _COUNTERS[name] += amount


def metrics_snapshot() -> dict[str, int]:
    with _LOCK:
        return dict(sorted(_COUNTERS.items()))


def observe_http_request(*, method: str, path: str, status_code: int) -> None:
    method_upper = (method or "").upper()
    path_lower = (path or "").lower()

    if status_code >= 500:
        increment_metric("http_5xx_total")

    if path_lower.startswith("/auth/login") and status_code in {400, 401, 403, 422, 429}:
        increment_metric("login_failed_total")

    if status_code == 429:
        increment_metric("rate_limit_exceeded_total")

    if status_code in {400, 413, 415, 422} and _looks_like_upload(method_upper, path_lower):
        increment_metric("uploads_rejected_total")

    if status_code < 400 and _looks_like_export(path_lower):
        increment_metric("exports_total")

    if status_code < 400 and method_upper == "DELETE":
        increment_metric("destructive_actions_total")


def metrics_payload() -> dict[str, Any]:
    counters = metrics_snapshot()
    return {
        "metrics": counters,
        "known_counters": [
            "http_5xx_total",
            "login_failed_total",
            "uploads_rejected_total",
            "exports_total",
            "destructive_actions_total",
            "rate_limit_exceeded_total",
        ],
    }


def _looks_like_upload(method: str, path: str) -> bool:
    return method in {"POST", "PUT", "PATCH"} and (
        "upload" in path
        or "evidencia" in path
        or "archivo" in path
        or "logo" in path
        or "firma" in path
        or "documento" in path
        or path.startswith("/uploads")
    )


def _looks_like_export(path: str) -> bool:
    return any(marker in path for marker in ("export", "exportaciones", "excel", "xlsx", "pdf"))
