from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

from app.database import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String(255), nullable=False)
    nit = Column(String(50), unique=True, nullable=False)

    direccion = Column(String(255), nullable=True)
    telefono = Column(String(50), nullable=True)
    correo = Column(String(255), nullable=True)

    representante_legal = Column(String(255), nullable=True)

    actividad_economica = Column(String(255), nullable=True)

    arl = Column(String(150), nullable=True)
    
# =====================================================
# LOGO CORPORATIVO
# =====================================================

    logo = Column(
    String(500),
    nullable=True
    )

    # =====================================================
    # NUEVOS CAMPOS SST
    # =====================================================

    numero_trabajadores = Column(Integer, default=1)

    clase_riesgo = Column(String(5), default="I")

    tipo_empresa = Column(String(50), default="EMPRESA")

    tipo_estandares_sst = Column(String(10), default="7")

    total_estandares_sst = Column(Integer, default=7)

    descripcion_estandares_sst = Column(String(500), nullable=True)

    # =====================================================

    estado = Column(Boolean, default=True)

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    fecha_actualizacion = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )