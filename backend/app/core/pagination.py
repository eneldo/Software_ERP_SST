# ============================================================
# PAGINACIÓN NORMALIZADA - ERP SST PRO
# FASE 36.4 — Normalización Enterprise
# ============================================================

from fastapi import Query
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def get_pagination_params(
    page: int = Query(1, ge=1, description="Página actual"),
    page_size: int = Query(20, ge=1, le=200, description="Registros por página"),
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)
