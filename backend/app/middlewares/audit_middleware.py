from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.auditoria import Auditoria
from app.auth.auth_handler import decode_access_token


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware de auditoría.
    Registra método, ruta, IP, usuario, empresa y estado HTTP.
    """

    async def dispatch(self, request, call_next):
        db: Session = SessionLocal()

        usuario_id = None
        empresa_id = None

        try:
            auth_header = request.headers.get("authorization")

            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ")[1]
                payload = decode_access_token(token)

                if payload:
                    usuario_id = payload.get("user_id")
                    empresa_id = payload.get("empresa_id")

            response = await call_next(request)

            if not request.url.path.startswith("/docs") and not request.url.path.startswith("/openapi"):
                registro = Auditoria(
                    usuario_id=usuario_id,
                    empresa_id=empresa_id,
                    metodo=request.method,
                    ruta=request.url.path,
                    accion=f"{request.method} {request.url.path}",
                    ip=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    status_code=response.status_code,
                )

                db.add(registro)
                db.commit()

            return response

        except Exception:
            return await call_next(request)

        finally:
            db.close()