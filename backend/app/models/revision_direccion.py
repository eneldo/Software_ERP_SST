# ============================================================
# USO DEL ARCHIVO:
# Modelos SQLAlchemy para el módulo Revisión por la Dirección SST.
#
# Incluye:
# - Tabla principal revisiones_direccion_sst
# - Tabla de compromisos gerenciales
# - Soporte doble firma electrónica:
#   gerente_usuario_id
#   responsable_sst_usuario_id
#
# Ubicación:
# backend/app/models/revision_direccion.py
#
# FASE 1.8.4.1 — Firma Gerente + Doble Firma Electrónica
# ============================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class RevisionDireccionSST(Base):
    __tablename__ = "revisiones_direccion_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    gerente_usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    responsable_sst_usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    codigo = Column(String(50), unique=True, nullable=False, index=True)
    titulo = Column(String(255), nullable=False)

    fecha_revision = Column(Date, nullable=False)
    periodo_evaluado = Column(String(100), nullable=True)

    gerente = Column(String(255), nullable=True)
    responsable_sst = Column(String(255), nullable=True)
    participantes = Column(Text, nullable=True)

    objetivo = Column(Text, nullable=True)
    alcance = Column(Text, nullable=True)
    agenda = Column(Text, nullable=True)

    resumen_auditorias = Column(Text, nullable=True)
    resumen_indicadores = Column(Text, nullable=True)
    resumen_planes_mejora = Column(Text, nullable=True)
    resumen_accidentes = Column(Text, nullable=True)
    resumen_capacitaciones = Column(Text, nullable=True)
    resumen_cumplimiento_legal = Column(Text, nullable=True)

    conclusiones = Column(Text, nullable=True)
    decisiones = Column(Text, nullable=True)
    recomendaciones = Column(Text, nullable=True)

    total_compromisos = Column(Integer, default=0)
    compromisos_pendientes = Column(Integer, default=0)
    compromisos_cerrados = Column(Integer, default=0)
    porcentaje_cumplimiento = Column(Numeric(5, 2), default=0)

    estado = Column(String(50), default="BORRADOR")
    activo = Column(Boolean, default=True)
    
# ==================================================
# FASE 1.8.4.2
# Bloqueo legal documental
# ==================================================

    bloqueado = Column(Boolean, default=False)

    fecha_bloqueo = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    bloqueado_por_usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )

    fecha_aprobacion = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    aprobado_por_usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )

    motivo_bloqueo = Column(
        Text,
        nullable=True,
    )

    version_documental = Column(
        String(50),
        default="BORRADOR",
    )

    hash_final_sha256 = Column(
        String(128),
        nullable=True,
    )

    codigo_validacion_final = Column(
        String(120),
        nullable=True,
    )
    
    

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    empresa = relationship("Empresa")

    usuario = relationship(
        "Usuario",
        foreign_keys=[usuario_id],
    )

    gerente_usuario = relationship(
        "Usuario",
        foreign_keys=[gerente_usuario_id],
    )

    responsable_sst_usuario = relationship(
        "Usuario",
        foreign_keys=[responsable_sst_usuario_id],
    )

    compromisos = relationship(
        "RevisionDireccionCompromisoSST",
        back_populates="revision",
        cascade="all, delete-orphan",
    )


class RevisionDireccionCompromisoSST(Base):
    __tablename__ = "revision_direccion_compromisos_sst"

    id = Column(Integer, primary_key=True, index=True)

    revision_id = Column(
        Integer,
        ForeignKey("revisiones_direccion_sst.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    compromiso = Column(Text, nullable=False)
    responsable = Column(String(255), nullable=True)

    fecha_compromiso = Column(Date, nullable=True)
    fecha_cierre = Column(Date, nullable=True)

    prioridad = Column(String(50), default="MEDIA")
    estado = Column(String(50), default="PENDIENTE")

    observaciones = Column(Text, nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    revision = relationship(
        "RevisionDireccionSST",
        back_populates="compromisos",
    )

    empresa = relationship("Empresa")