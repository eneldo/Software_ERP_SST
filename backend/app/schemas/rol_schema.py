from pydantic import ConfigDict,  BaseModel
from typing import Optional


class RolCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class RolUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class RolResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool

    model_config = ConfigDict(from_attributes=True)
