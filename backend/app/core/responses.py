# ============================================================
# RESPUESTAS NORMALIZADAS - ERP SST PRO
# FASE 36.4 — Normalización Enterprise
# ============================================================

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    ok: bool = True
    mensaje: str = "Operación realizada correctamente"
    data: T | None = None


class ApiListResponse(BaseModel, Generic[T]):
    ok: bool = True
    mensaje: str = "Consulta realizada correctamente"
    total: int = 0
    data: list[T] = Field(default_factory=list)


class ApiErrorResponse(BaseModel):
    ok: bool = False
    mensaje: str = "No fue posible procesar la solicitud"
    detalle: Any | None = None


def success_response(data: Any = None, mensaje: str = "Operación realizada correctamente") -> dict[str, Any]:
    return {"ok": True, "mensaje": mensaje, "data": data}


def list_response(data: list[Any], total: int | None = None, mensaje: str = "Consulta realizada correctamente") -> dict[str, Any]:
    return {"ok": True, "mensaje": mensaje, "total": len(data) if total is None else total, "data": data}
