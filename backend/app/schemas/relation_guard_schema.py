# ============================================================
# SCHEMAS RELATION GUARD - ERP SST PRO ENTERPRISE
# FASE 37.3 — Smart Delete Enterprise v2
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

    # FASE 37.3 — campos opcionales v2, compatibles con módulos anteriores.
    icon: str | None = Field(default=None, description="Icono lógico para frontend")
    severity: str | None = Field(default=None, description="LOW, MEDIUM, HIGH, CRITICAL")
    category: str | None = Field(default=None, description="Categoría funcional de la relación")


class RelationImpactItemResponse(BaseModel):
    """Fila del análisis de impacto, incluyendo dependencias con conteo cero."""

    table: str
    column: str
    label: str
    count: int = Field(default=0, ge=0)
    blocking: bool = True
    category: str = "general"
    severity: str = "LOW"
    icon: str = "database"
    message: str | None = None
    has_records: bool = False


class RelationImpactSummaryResponse(BaseModel):
    """Resumen ejecutivo del impacto de eliminación."""

    total_rules: int = 0
    total_related_records: int = 0
    total_blocking_records: int = 0
    blocking_rules: int = 0
    non_blocking_rules: int = 0
    impact_level: str = "LOW"
    impact_label: str = "Bajo"
    recommended_action: str = "DELETE"
    can_delete: bool = True


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

    # FASE 37.3 — Smart Impact v2.
    impact_summary: RelationImpactSummaryResponse | None = None
    impact_matrix: list[RelationImpactItemResponse] = Field(default_factory=list)


class RelationGuardEntityResponse(BaseModel):
    """Entidad registrada en el motor."""

    entity: str
    table: str
    label: str
    primary_key: str = "id"
    rules_count: int = 0
    # FASE 37.4 — metadata Enterprise opcional.
    # No rompe clientes anteriores porque es un campo nuevo opcional.
    meta: dict[str, Any] = Field(default_factory=dict)


class IntegrityFrameworkMetadataResponse(BaseModel):
    """Metadata global del Framework de Integridad Enterprise."""

    name: str
    version: str
    description: str | None = None
    features: dict[str, Any] = Field(default_factory=dict)
    severity_scale: dict[str, Any] = Field(default_factory=dict)
    default_delete_policy: dict[str, Any] = Field(default_factory=dict)
    entities_count: int = 0
    entities: list[dict[str, Any]] = Field(default_factory=list)


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

    # FASE 37.3 — información de impacto retornada también al ejecutar.
    impact_summary: RelationImpactSummaryResponse | None = None
    impact_matrix: list[RelationImpactItemResponse] = Field(default_factory=list)
