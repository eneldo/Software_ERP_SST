from typing import Optional
from pydantic import ConfigDict,  BaseModel, EmailStr


# ============================================================
# CREATE
# ============================================================

class EmpresaCreate(BaseModel):
    nombre: str
    nit: str
    digito_verificacion: Optional[str] = None
    logo: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None

    representante_legal: Optional[str] = None
    responsable_sst: Optional[str] = None

    actividad_economica: Optional[str] = None

    arl: Optional[str] = None

    # =====================================================
    # NUEVOS CAMPOS SST
    # =====================================================

    numero_trabajadores: int = 1

    clase_riesgo: str = "I"

    tipo_empresa: str = "EMPRESA"


# ============================================================
# UPDATE
# ============================================================

class EmpresaUpdate(BaseModel):
    nombre: Optional[str] = None
    nit: Optional[str] = None
    digito_verificacion: Optional[str] = None
    logo: Optional[str] = None

    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None

    representante_legal: Optional[str] = None
    responsable_sst: Optional[str] = None

    actividad_economica: Optional[str] = None

    arl: Optional[str] = None

    numero_trabajadores: Optional[int] = None

    clase_riesgo: Optional[str] = None

    tipo_empresa: Optional[str] = None

    estado: Optional[bool] = None


# ============================================================
# RESPONSE
# ============================================================

class EmpresaResponse(BaseModel):
    id: int
    logo: Optional[str] = None
    nombre: str
    nit: str
    digito_verificacion: Optional[str] = None

    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None

    representante_legal: Optional[str] = None
    responsable_sst: Optional[str] = None

    actividad_economica: Optional[str] = None

    arl: Optional[str] = None

    # =====================================================
    # CAMPOS SST
    # =====================================================

    numero_trabajadores: int

    clase_riesgo: str

    tipo_empresa: str

    tipo_estandares_sst: str

    total_estandares_sst: int

    descripcion_estandares_sst: Optional[str] = None

    estado: bool

    model_config = ConfigDict(from_attributes=True)
