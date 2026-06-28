# ============================================================
# SCHEMAS DASHBOARD BI MEDIDAS CORRECTIVAS
# ERP SST PRO
# FASE 1.1.8.7.5.4 — Dashboard Ejecutivo BI
# Archivo: backend/app/schemas/medidas_correctivas_bi_schema.py
# ============================================================

from __future__ import annotations

from pydantic import BaseModel


class BIChartItem(BaseModel):
    name: str
    value: float | int
    extra: dict | None = None


class MedidasCorrectivasBIResponse(BaseModel):
    kpis: dict
    eficacia: dict
    alertas: dict
    costos: dict
    semaforo: dict
    charts: dict[str, list[BIChartItem]]
    ranking: dict[str, list[dict]]
    recomendaciones: list[str]
