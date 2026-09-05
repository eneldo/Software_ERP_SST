# ============================================================
# MODELO AUSENTISMO SST
# H-016: Indicador de Ausentismo (GTC 45, Decreto 1072)
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class AusentismoSST(Base):
    __tablename__ = "ausentismo_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True, index=True)
    usuario_registro_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    tipo_ausentismo = Column(String(80), nullable=False, index=True)
    # ENFERMEDAD_GENERAL, ACCIDENTE_LABORAL, ENFERMEDAD_LABORAL,
    # LICENCIA_REMUNERADA, LICENCIA_NO_REMUNERADA, MATERNIDAD,
    # PATERNIDAD, VACACIONES, CALAMIDAD_DOMESTICA, OTRO

    fecha_inicio = Column(Date, nullable=False, index=True)
    fecha_fin = Column(Date, nullable=True)
    dias_ausentismo = Column(Integer, nullable=False, default=1)

    diagnostico = Column(String(255), nullable=True)
    clase_riesgo = Column(String(50), nullable=True)
    # I, II, III, IV, V

    observaciones = Column(Text, nullable=True)

    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")
    empleado = relationship("Empleado")
