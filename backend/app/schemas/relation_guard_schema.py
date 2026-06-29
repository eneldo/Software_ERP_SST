# ============================================================
# SCHEMAS RELATION GUARD - ERP SST PRO ENTERPRISE
# FASE 37.1.1 — Motor Global de Validación de Relaciones
# Archivo: backend/app/schemas/relation_guard_schema.py
# ============================================================

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RelationDependencyResponse(BaseModel):
    """Detalle de una dependencia encontrada para una entidad."""

    table: str = Field(..., description="Tabla relacionada encontrada")
    column: str = Field(..., description="Columna FK o de referencia")
    label: str = Field(..., description="Nombre legible de la relación")
    count: int = Field(..., ge=0, description="Cantidad de registros relacionados")
    blocking: bool = Field(default=True)
    message: str | None = None


class RelationGuardResponse(BaseModel):
    """Respuesta estándar del motor de eliminación inteligente."""

    entity: str
    entity_id: int
    can_delete: bool
    recommended_action: str = "DELETE"
    total_dependencies: int = 0
    blocking_dependencies: int = 0
    dependencies: list[RelationDependencyResponse] = Field(default_factory=list)
    message: str
    meta: dict[str, Any] = Field(default_factory=dict)


class RelationGuardEntityResponse(BaseModel):
    """Entidad registrada en el motor."""

    entity: str
    table: str
    label: str
    primary_key: str = "id"
    rules_count: int = 0


class SmartDeleteResponse(BaseModel):
    """Respuesta de ejecución del motor de eliminación inteligente."""

    success: bool
    entity: str
    entity_id: int
    action: str = Field(..., description="DELETE, INACTIVATE, BLOCKED, NOT_FOUND o ERROR")
    can_delete: bool = False
    was_deleted: bool = False
    was_inactivated: bool = False
    message: str
    recommended_action: str = "REVIEW"
    dependencies: list[RelationDependencyResponse] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)
