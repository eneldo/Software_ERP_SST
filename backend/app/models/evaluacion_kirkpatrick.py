# ============================================================
# MODELO EVALUACIÓN KIRKPATRICK SST
# 4 niveles: Reacción / Aprendizaje / Comportamiento / Resultados
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class EvaluacionKirkpatrickSST(Base):
    __tablename__ = "evaluaciones_kirkpatrick_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    capacitacion_id = Column(Integer, ForeignKey("capacitaciones_sst.id", ondelete="CASCADE"), nullable=False, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True, index=True)

    # Nivel 1 — Reacción (satisfacción del participante)
    nivel1_satisfaccion = Column(Integer, nullable=True)
    nivel1_comentario = Column(Text, nullable=True)

    # Nivel 2 — Aprendizaje (conocimiento adquirido)
    nivel2_puntuacion_pre = Column(Numeric(5, 2), nullable=True)
    nivel2_puntuacion_post = Column(Numeric(5, 2), nullable=True)
    nivel2_aprobado = Column(Boolean, default=False)

    # Nivel 3 — Comportamiento (aplicación en el puesto, 30/60/90 días)
    nivel3_observacion_30d = Column(Text, nullable=True)
    nivel3_observacion_60d = Column(Text, nullable=True)
    nivel3_observacion_90d = Column(Text, nullable=True)
    nivel3_aplicacion_pct = Column(Numeric(5, 2), nullable=True)

    # Nivel 4 — Resultados (impacto organizacional)
    nivel4_indicador = Column(String(255), nullable=True)
    nivel4_valor_antes = Column(Numeric(10, 2), nullable=True)
    nivel4_valor_despues = Column(Numeric(10, 2), nullable=True)
    nivel4_impacto = Column(Text, nullable=True)

    responsable_seguimiento = Column(String(255), nullable=True)
    estado = Column(String(50), default="PENDIENTE")

    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    capacitacion = relationship("CapacitacionSST")
    empleado = relationship("Empleado")
