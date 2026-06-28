# ============================================================
# EXCEPTION HANDLERS - ERP SST PRO ENTERPRISE
# FASE 36.8 — Logging Enterprise y Manejo de Errores
# Archivo: backend/app/core/exception_handlers.py
# ============================================================

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings

logger = logging.getLogger("app.errors")


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


def _error_response(
    *,
    request: Request,
    status_code: int,
    message: str,
    code: str,
    details=None,
) -> JSONResponse:
    payload = {
        "success": False,
        "message": message,
        "code": code,
        "request_id": _request_id(request),
    }
    if details is not None and settings.ENVIRONMENT != "production":
        payload["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(
            "Validation error path=%s errors=%s",
            request.url.path,
            exc.errors(),
            extra={"request_id": _request_id(request)},
        )
        return _error_response(
            request=request,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="La información enviada no es válida.",
            code="VALIDATION_ERROR",
            details=exc.errors(),
        )

    @app.exception_handler(HTTPException)
    async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
        if exc.status_code >= 500:
            logger.error(
                "HTTPException path=%s status=%s detail=%s",
                request.url.path,
                exc.status_code,
                exc.detail,
                extra={"request_id": _request_id(request)},
            )
        return _error_response(
            request=request,
            status_code=exc.status_code,
            message=str(exc.detail or "No fue posible completar la solicitud."),
            code="HTTP_ERROR",
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        message = "Recurso no encontrado." if exc.status_code == 404 else str(exc.detail or "Error HTTP.")
        return _error_response(
            request=request,
            status_code=exc.status_code,
            message=message,
            code="HTTP_ERROR",
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.warning(
            "Database integrity error path=%s error=%s",
            request.url.path,
            str(exc.orig) if getattr(exc, "orig", None) else str(exc),
            extra={"request_id": _request_id(request)},
        )
        return _error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            message="No se pudo guardar porque existe una restricción de datos o un registro relacionado.",
            code="DATABASE_INTEGRITY_ERROR",
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        logger.exception(
            "Database error path=%s",
            request.url.path,
            extra={"request_id": _request_id(request)},
        )
        return _error_response(
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Error interno de base de datos.",
            code="DATABASE_ERROR",
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(
            "Unhandled exception path=%s",
            request.url.path,
            extra={"request_id": _request_id(request)},
        )
        return _error_response(
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Error interno del servidor.",
            code="INTERNAL_SERVER_ERROR",
        )
