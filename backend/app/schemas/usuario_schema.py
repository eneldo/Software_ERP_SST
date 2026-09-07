# ============================================================
# SCHEMAS USUARIO - ERP SST PRO
# ============================================================

from typing import Optional
from pydantic import ConfigDict,  BaseModel, EmailStr


class UsuarioCreate(BaseModel):
    nombres: str
    apellidos: str
    correo: EmailStr
    password: str
    rol: str = "ADMIN_EMPRESA"
    empresa_id: Optional[int] = None


class UsuarioResponse(BaseModel):
    id: int
    nombres: str
    apellidos: str
    correo: EmailStr
    rol: str
    activo: bool
    empresa_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
