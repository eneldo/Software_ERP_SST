# ============================================================
# SCHEMAS AUTH - ERP SST PRO
# ============================================================

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """
    Login por JSON.
    Usar en frontend React.
    """
    correo: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None
    usuario: dict
