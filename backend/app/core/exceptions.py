# ============================================================
# MANEJO CENTRALIZADO DE ERRORES - ERP SST PRO
# FASE 36.4 — Normalización Enterprise
# ============================================================

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "ok": False,
                "mensaje": "La información enviada no es válida.",
                "detalle": exc.errors(),
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "ok": False,
                "mensaje": exc.detail if isinstance(exc.detail, str) else "Error HTTP",
                "detalle": exc.detail if not isinstance(exc.detail, str) else None,
                "path": str(request.url.path),
            },
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "ok": False,
                "mensaje": "Error interno de base de datos.",
                "detalle": "Revise los logs del backend para mayor información.",
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "ok": False,
                "mensaje": "Error interno del servidor.",
                "detalle": "Revise los logs del backend para mayor información.",
                "path": str(request.url.path),
            },
        )
