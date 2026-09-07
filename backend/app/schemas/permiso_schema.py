from pydantic import ConfigDict,  BaseModel
from typing import Optional, List


class PermisoCreate(BaseModel):
    codigo: str
    nombre: str
    modulo: str
    descripcion: Optional[str] = None


class PermisoUpdate(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    modulo: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class PermisoResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    modulo: str
    descripcion: Optional[str] = None
    activo: bool

    model_config = ConfigDict(from_attributes=True)


class AsignarPermisosUsuario(BaseModel):
    usuario_id: int
    permisos_ids: List[int]
