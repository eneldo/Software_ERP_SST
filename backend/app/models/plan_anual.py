from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class PlanAnualSST(Base):
    __tablename__ = "plan_anual_sst"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    archivo_id = Column(Integer, ForeignKey("archivos_sst.id", ondelete="SET NULL"), nullable=True)

    codigo = Column(String(80), nullable=False, default="PA-SST-001")
    actividad = Column(Text, nullable=False)
    objetivo = Column(Text, nullable=True)
    responsable = Column(String(255), nullable=True)

    recurso_humano = Column(Text, nullable=True)
    recurso_fisico = Column(Text, nullable=True)
    recurso_financiero = Column(Text, nullable=True)
    presupuesto = Column(Numeric(14, 2), nullable=True, default=0)

    indicador = Column(Text, nullable=True)
    meta = Column(Text, nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)

    estado = Column(String(80), default="PLANIFICADO")
    porcentaje_avance = Column(Integer, default=0)

    evidencia = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    # =====================================================
    # CAMPOS SEGÚN DECRETO 1072 DE 2015
    # =====================================================
    alcance = Column(Text, nullable=True)
    objetivo_general = Column(Text, nullable=True)
    vigencia = Column(String(4), nullable=True)

    # Firmas
    representante_legal_nombre = Column(String(255), nullable=True)
    representante_legal_cargo = Column(String(255), nullable=True)
    responsable_sst_nombre = Column(String(255), nullable=True)
    responsable_sst_cargo = Column(String(255), nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")
    archivo = relationship("ArchivoSST")
    evidencias = relationship(
        "ArchivoSST",
        primaryjoin="and_(PlanAnualSST.id==ArchivoSST.referencia_id, ArchivoSST.modulo=='PLAN_ANUAL', ArchivoSST.activo==True)",
        foreign_keys="ArchivoSST.referencia_id",
        viewonly=True,
    )
