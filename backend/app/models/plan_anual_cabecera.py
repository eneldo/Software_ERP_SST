from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class PlanAnualCabecera(Base):
    __tablename__ = "plan_anual_cabecera"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    vigencia = Column(String(4), nullable=False, index=True)

    alcance = Column(Text, nullable=True)
    objetivo_general = Column(Text, nullable=True)
    meta_general = Column(Text, nullable=True)

    representante_legal_nombre = Column(String(255), nullable=True)
    representante_legal_cargo = Column(String(255), nullable=True)
    responsable_sst_nombre = Column(String(255), nullable=True)
    responsable_sst_cargo = Column(String(255), nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")
    actividades = relationship(
        "PlanAnualSST",
        back_populates="cabecera",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint("empresa_id", "vigencia", name="uq_plan_anual_cabecera_empresa_vigencia"),
    )