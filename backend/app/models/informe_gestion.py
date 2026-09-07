# ============================================================
# MODELOS SQLAlchemy PARA EL MÓDULO INFORME DE GESTIÓN SG-SST
#
# Tablas:
# - informes_gestion_sgsst (Informe principal)
# - informes_gestion_versiones (Versionado histórico)
# - informes_gestion_secciones (Secciones con snapshot JSON)
# - informes_gestion_evidencias (Evidencias adjuntas)
# - informes_gestion_recomendaciones (Recomendaciones del responsable)
# - informes_gestion_aprobaciones (Flujo de aprobaciones)
# - rendiciones_cuentas (Rendición de cuentas)
# - rendiciones_cuentas_responsabilidades (Detalle responsabilidades)
#
# Ubicación: backend/app/models/informe_gestion.py
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
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class InformeGestionSGSST(Base):
    __tablename__ = "informes_gestion_sgsst"

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

    responsable_sst_usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    codigo = Column(String(50), unique=True, nullable=False, index=True)
    titulo = Column(String(255), nullable=False, default="INFORME ANUAL DE GESTIÓN SG-SST")

    anio = Column(Integer, nullable=False, index=True)
    periodo_evaluado = Column(String(100), nullable=True)
    fecha_inicio_periodo = Column(Date, nullable=True)
    fecha_fin_periodo = Column(Date, nullable=True)

    sede_id = Column(
        Integer,
        ForeignKey("sedes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    responsable_sst_nombre = Column(String(255), nullable=True)
    representante_legal_nombre = Column(String(255), nullable=True)

    version = Column(Integer, default=1)
    estado = Column(String(50), default="BORRADOR", index=True)
    # Estados: BORRADOR, EN_REVISION, PRESENTADO, APROBADO,
    # APROBADO_CON_OBSERVACIONES, DEVUELTO, CERRADO

    # Resumen ejecutivo
    resumen_ejecutivo = Column(Text, nullable=True)

    # Snapshot de datos consolidados (JSON)
    datos_consolidados = Column(JSON, nullable=True)

    # Indicadores generales
    cumplimiento_global = Column(Numeric(5, 2), nullable=True)
    cumplimiento_plan_anual = Column(Numeric(5, 2), nullable=True)
    cumplimiento_estandares = Column(Numeric(5, 2), nullable=True)

    # Totales del informe
    total_secciones = Column(Integer, default=0)
    total_evidencias = Column(Integer, default=0)
    total_recomendaciones = Column(Integer, default=0)

    # Fechas de flujo
    fecha_generacion = Column(DateTime(timezone=True), nullable=True)
    fecha_presentacion = Column(DateTime(timezone=True), nullable=True)
    fecha_aprobacion = Column(DateTime(timezone=True), nullable=True)
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)

    # Aprobación
    aprobado_por_usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Documental
    codigo_documental = Column(String(100), nullable=True)
    hash_final_sha256 = Column(String(128), nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    empresa = relationship("Empresa")
    sede = relationship("Sede")
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    responsable_sst_usuario = relationship(
        "Usuario", foreign_keys=[responsable_sst_usuario_id]
    )
    aprobado_por_usuario = relationship(
        "Usuario", foreign_keys=[aprobado_por_usuario_id]
    )

    versiones = relationship(
        "InformeGestionVersion",
        back_populates="informe",
        cascade="all, delete-orphan",
    )
    secciones = relationship(
        "InformeGestionSeccion",
        back_populates="informe",
        cascade="all, delete-orphan",
    )
    evidencias = relationship(
        "InformeGestionEvidencia",
        back_populates="informe",
        cascade="all, delete-orphan",
    )
    recomendaciones = relationship(
        "InformeGestionRecomendacion",
        back_populates="informe",
        cascade="all, delete-orphan",
    )
    aprobaciones = relationship(
        "InformeGestionAprobacion",
        back_populates="informe",
        cascade="all, delete-orphan",
    )


class InformeGestionVersion(Base):
    __tablename__ = "informes_gestion_versiones"

    id = Column(Integer, primary_key=True, index=True)

    informe_id = Column(
        Integer,
        ForeignKey("informes_gestion_sgsst.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    version_numero = Column(Integer, nullable=False)
    estado_anterior = Column(String(50), nullable=True)
    estado_nuevo = Column(String(50), nullable=False)

    datos_snapshot = Column(JSON, nullable=True)
    motivo_cambio = Column(Text, nullable=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    informe = relationship("InformeGestionSGSST", back_populates="versiones")
    empresa = relationship("Empresa")
    usuario = relationship("Usuario")


class InformeGestionSeccion(Base):
    __tablename__ = "informes_gestion_secciones"

    id = Column(Integer, primary_key=True, index=True)

    informe_id = Column(
        Integer,
        ForeignKey("informes_gestion_sgsst.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    codigo_seccion = Column(String(50), nullable=False, index=True)
    # Ej: "5.1_PORTADA", "5.4_PLAN_ANUAL", "5.6_INDICADORES"

    nombre_seccion = Column(String(255), nullable=False)

    orden = Column(Integer, default=0)

    # Snapshot de datos de esta sección
    datos_seccion = Column(JSON, nullable=True)

    # Estado de la sección
    estado_seccion = Column(String(50), default="PENDIENTE")
    # PENDIENTE, CONSOLIDADA, REVISADA, APROBADA

    observaciones = Column(Text, nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    informe = relationship("InformeGestionSGSST", back_populates="secciones")
    empresa = relationship("Empresa")


class InformeGestionEvidencia(Base):
    __tablename__ = "informes_gestion_evidencias"

    id = Column(Integer, primary_key=True, index=True)

    informe_id = Column(
        Integer,
        ForeignKey("informes_gestion_sgsst.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    codigo_seccion = Column(String(50), nullable=True)
    nombre = Column(String(255), nullable=False)
    tipo_archivo = Column(String(50), nullable=False)  # PDF, EXCEL, IMAGEN, etc.
    tamano_bytes = Column(Integer, nullable=True)
    hash_archivo = Column(String(128), nullable=True)

    archivo_url = Column(String(500), nullable=True)
    archivo_nombre_original = Column(String(255), nullable=True)

    modulo_origen = Column(String(100), nullable=True)
    registro_origen_id = Column(Integer, nullable=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    informe = relationship("InformeGestionSGSST", back_populates="evidencias")
    empresa = relationship("Empresa")
    usuario = relationship("Usuario")


class InformeGestionRecomendacion(Base):
    __tablename__ = "informes_gestion_recomendaciones"

    id = Column(Integer, primary_key=True, index=True)

    informe_id = Column(
        Integer,
        ForeignKey("informes_gestion_sgsst.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    hallazgo = Column(Text, nullable=False)
    riesgo = Column(Text, nullable=True)
    recomendacion = Column(Text, nullable=False)

    prioridad = Column(String(50), default="MEDIA")
    # CRITICA, ALTA, MEDIA, BAJA

    accion_propuesta = Column(Text, nullable=True)
    responsable_sugerido = Column(String(255), nullable=True)
    recursos_requeridos = Column(Text, nullable=True)
    fecha_recomendada = Column(Date, nullable=True)

    estado = Column(String(50), default="PENDIENTE")
    # PENDIENTE, ACEPTADA, EN_EJECUCION, CERRADA

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    informe = relationship("InformeGestionSGSST", back_populates="recomendaciones")
    empresa = relationship("Empresa")
    usuario = relationship("Usuario")


class InformeGestionAprobacion(Base):
    __tablename__ = "informes_gestion_aprobaciones"

    id = Column(Integer, primary_key=True, index=True)

    informe_id = Column(
        Integer,
        ForeignKey("informes_gestion_sgsst.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

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
    )

    tipo_accion = Column(String(50), nullable=False)
    # PRESENTACION, REVISION, APROBACION, DEVOLUCION, CIERRE

    resultado = Column(String(50), nullable=False)
    # APROBADO, APROBADO_CON_OBSERVACIONES, DEVUELTO, CERRADO

    observaciones = Column(Text, nullable=True)
    comentarios = Column(Text, nullable=True)

    hash_firma = Column(String(128), nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    informe = relationship("InformeGestionSGSST", back_populates="aprobaciones")
    empresa = relationship("Empresa")
    usuario = relationship("Usuario")


class RendicionCuentas(Base):
    __tablename__ = "rendiciones_cuentas"

    id = Column(Integer, primary_key=True, index=True)

    informe_id = Column(
        Integer,
        ForeignKey("informes_gestion_sgsst.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

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

    persona_nombre = Column(String(255), nullable=False)
    cargo = Column(String(255), nullable=True)
    rol_sgsst = Column(String(100), nullable=True)

    responsabilidad_asignada = Column(Text, nullable=False)
    actividades = Column(Text, nullable=True)
    meta = Column(Text, nullable=True)
    resultado = Column(Text, nullable=True)
    porcentaje_cumplimiento = Column(Numeric(5, 2), nullable=True)

    estado = Column(String(50), default="BORRADOR")
    # BORRADOR, PRESENTADO, REVISADO, APROBADO, DEVUELTO

    dificultades = Column(Text, nullable=True)
    actividades_pendientes = Column(Text, nullable=True)
    compromisos = Column(Text, nullable=True)
    acciones_mejora = Column(Text, nullable=True)

    fecha_evaluacion = Column(Date, nullable=True)
    observaciones = Column(Text, nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    informe = relationship("InformeGestionSGSST")
    empresa = relationship("Empresa")
    usuario = relationship("Usuario")

    responsabilidades = relationship(
        "RendicionCuentasResponsabilidad",
        back_populates="rendicion",
        cascade="all, delete-orphan",
    )


class RendicionCuentasResponsabilidad(Base):
    __tablename__ = "rendiciones_cuentas_responsabilidades"

    id = Column(Integer, primary_key=True, index=True)

    rendicion_id = Column(
        Integer,
        ForeignKey("rendiciones_cuentas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    responsabilidad = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)

    actividades_ejecutadas = Column(Text, nullable=True)
    meta = Column(Text, nullable=True)
    resultado_obtenido = Column(Text, nullable=True)

    porcentaje_cumplimiento = Column(Numeric(5, 2), nullable=True)
    estado = Column(String(50), default="PENDIENTE")

    evidencias = Column(Text, nullable=True)
    fecha_cumplimiento = Column(Date, nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    rendicion = relationship("RendicionCuentas", back_populates="responsabilidades")
    empresa = relationship("Empresa")
