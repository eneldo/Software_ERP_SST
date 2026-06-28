from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(Integer, primary_key=True, index=True)

    nombres = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)

    tipo_documento = Column(String(20), default="CC")
    documento = Column(String(50), unique=True, nullable=False)

    correo = Column(String(255), nullable=True)
    telefono = Column(String(50), nullable=True)

    fecha_nacimiento = Column(Date, nullable=True)
    fecha_ingreso = Column(Date, nullable=True)

    tipo_contrato = Column(String(100), nullable=True)
    estado_laboral = Column(String(50), default="ACTIVO")

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="SET NULL"), nullable=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id", ondelete="SET NULL"), nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    empresa = relationship("Empresa")
    sede = relationship("Sede")
    area = relationship("Area")
    cargo = relationship("Cargo")