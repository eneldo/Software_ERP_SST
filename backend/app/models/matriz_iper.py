# ============================================================
# MODELO MATRIZ IPER - GTC 45
# Identificación de Peligros, Evaluación y Valoración de Riesgos
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class MatrizIPER(Base):
    __tablename__ = "matriz_iper"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    # 1. Contexto del proceso
    proceso = Column(String(200), nullable=False)
    zona_lugar = Column(String(255), nullable=True)
    actividades = Column(String(255), nullable=True)
    tareas = Column(Text, nullable=True)
    rutinaria = Column(String(5), default="SI")  # SI / NO

    # 2. Identificación del peligro
    clasificacion_peligro = Column(String(50), nullable=False)  # FISICO, QUIMICO, BIOLOGICO, BIOMECANICO, PSICOSOCIAL, CONDICIONES_SEGURIDAD, FENOMENOS_NATURALES
    descripcion_peligro = Column(Text, nullable=False)
    riesgo = Column(String(300), nullable=True)
    efectos_posibles = Column(Text, nullable=False)

    # 3. Controles existentes
    fuente = Column(String(300), nullable=True)
    medio = Column(String(300), nullable=True)
    individuo = Column(String(300), nullable=True)

    # 4. Evaluación del riesgo (GTC 45)
    nd = Column(Integer, default=0)          # Nivel de Deficiencia: 0, 2, 6, 10
    ne = Column(Integer, default=1)          # Nivel de Exposición: 1, 2, 3, 4
    np = Column(Integer, default=0)          # Nivel de Probabilidad = ND × NE
    interpretacion_np = Column(String(50), nullable=True)  # Bajo, Medio, Alto, Muy Alto
    nc = Column(Integer, default=10)         # Nivel de Consecuencia: 10, 25, 60, 100
    nr = Column(Integer, default=0)          # Nivel de Riesgo = NP × NC
    interpretacion_nr = Column(String(80), nullable=True)  # Aceptable, Mejorable, No Aceptable / Control Específico
    nivel_riesgo = Column(String(10), nullable=True)  # I, II, III, IV (número romano)
    aceptabilidad = Column(String(50), nullable=True)      # ACEPTABLE, MEJORABLE, CON CONTROL ESPECÍFICO, NO ACEPTABLE

    # 5. Criterios para establecer controles
    expuestos_hombres = Column(Integer, default=0)
    expuestos_mujeres = Column(Integer, default=0)
    expuestos_gestantes = Column(Integer, default=0)
    peor_consecuencia = Column(String(300), nullable=True)

    # 6. Medidas de intervención (jerarquía de controles)
    eliminacion = Column(Text, nullable=True)
    control_ingenieria = Column(Text, nullable=True)
    sustitucion = Column(Text, nullable=True)
    senalizacion_admin = Column(Text, nullable=True)
    epp = Column(Text, nullable=True)
    responsable = Column(Text, nullable=True)

    # 7. Seguimiento
    fecha_proyectada = Column(DateTime(timezone=True), nullable=True)
    fecha_ejecucion = Column(DateTime(timezone=True), nullable=True)
    evidencias = Column(Text, nullable=True)
    realizado = Column(String(5), default="NO")  # SI / NO

    # Control
    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")
