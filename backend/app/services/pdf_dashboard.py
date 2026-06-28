"""Compat wrapper for the canonical dashboard PDF helpers."""

from app.services.pdf.pdf_dashboard import (
    PLATINUM_ACCENT,
    PLATINUM_BORDER,
    PLATINUM_DANGER,
    PLATINUM_LIGHT,
    PLATINUM_MUTED,
    PLATINUM_PRIMARY,
    PLATINUM_SECONDARY,
    PLATINUM_SUCCESS,
    PLATINUM_WARNING,
    bar_chart,
    build_dashboard,
    kpi_card,
    pie_chart,
)

__all__ = [
    "PLATINUM_ACCENT",
    "PLATINUM_BORDER",
    "PLATINUM_DANGER",
    "PLATINUM_LIGHT",
    "PLATINUM_MUTED",
    "PLATINUM_PRIMARY",
    "PLATINUM_SECONDARY",
    "PLATINUM_SUCCESS",
    "PLATINUM_WARNING",
    "bar_chart",
    "build_dashboard",
    "kpi_card",
    "pie_chart",
]
