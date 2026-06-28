# ============================================================
# ERP SST PRO ENTERPRISE
# MÓDULO: VERSIONADO DOCUMENTAL
# ARCHIVO: revision_version.py
#
# PROPÓSITO:
# Almacena snapshots históricos de cada revisión
# por la dirección SST.
#
# Permite:
# - Historial de versiones
# - Recuperación documental
# - Comparación entre versiones
# - Auditoría documental ISO 45001
# - Trazabilidad completa
#
# FASE 1.8.4.3
# ============================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class RevisionDireccionVersionSST(Base):
    """
    Historial documental de revisiones SST.
    Cada registro representa un snapshot completo
    de una revisión en un momento determinado.
    """

    __tablename__ = "revisiones_direccion_versiones_sst"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    revision_id = Column(
        Integer,
        ForeignKey(
            "revisiones_direccion_sst.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    version_numero = Column(
        Integer,
        nullable=False,
    )

    codigo_version = Column(
        String(100),
        nullable=False,
    )

    usuario_id = Column(
        Integer,
        ForeignKey(
            "usuarios.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    accion = Column(
        String(50),
        nullable=False,
    )

    datos_json = Column(
        JSONB,
        nullable=False,
    )

    hash_sha256 = Column(
        String(128),
        nullable=True,
    )

    observacion = Column(
        Text,
        nullable=True,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # =====================================
    # RELACIONES
    # =====================================

    revision = relationship(
        "RevisionDireccionSST",
        backref="versiones_documentales",
    )

    usuario = relationship(
        "Usuario",
        foreign_keys=[usuario_id],
    )