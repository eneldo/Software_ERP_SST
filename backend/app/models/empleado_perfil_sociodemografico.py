from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class EmpleadoPerfilSociodemografico(Base):
    __tablename__ = "empleado_perfil_sociodemografico"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False, index=True)

    # ── 1. DATOS DE IDENTIFICACIÓN GENERAL Y CONTACTO ──
    nombres_completos = Column(String(255), nullable=True)
    tipo_documento = Column(String(20), nullable=True)
    numero_documento = Column(String(50), nullable=True)
    libreta_militar = Column(String(50), nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    lugar_nacimiento = Column(String(255), nullable=True)
    edad = Column(Integer, nullable=True)
    raza_pertenencia_etnica = Column(String(100), nullable=True)
    telefono_celular = Column(String(50), nullable=True)

    # ── 2. VARIABLES SOCIODEMOGRÁFICAS Y NÚCLEO FAMILIAR ──
    estado_civil = Column(String(50), nullable=True)
    conyuge_nombre = Column(String(255), nullable=True)
    conyuge_ocupacion = Column(String(255), nullable=True)
    conyuge_edad = Column(Integer, nullable=True)
    conyuge_celular = Column(String(50), nullable=True)
    numero_dependientes = Column(Integer, nullable=True)
    tiene_hijos = Column(Boolean, default=False)
    num_hijos = Column(Integer, default=0)
    hijos = Column(JSON, nullable=True)  # [{nombre, fecha_nacimiento, edad, escolaridad}]

    # ── 3. ENTORNO SOCIOECONÓMICO Y VIVIENDA ──
    direccion_residencia = Column(String(500), nullable=True)
    barrio = Column(String(255), nullable=True)
    ciudad_municipio = Column(String(255), nullable=True)
    estrato_socioeconomico = Column(Integer, nullable=True)
    tipo_vivienda = Column(String(50), nullable=True)
    servicios_vivienda = Column(JSON, nullable=True)  # [acueducto, alcantarillado, energia, gas]
    medio_transporte = Column(String(100), nullable=True)
    medio_transporte_otro = Column(String(255), nullable=True)
    tiempo_desplazamiento = Column(String(50), nullable=True)

    # ── 4. INFORMACIÓN LABORAL Y FORMACIÓN ──
    cargo_actual = Column(String(255), nullable=True)
    area_departamento = Column(String(255), nullable=True)
    sede_centro_trabajo = Column(String(255), nullable=True)
    tipo_contrato = Column(String(100), nullable=True)
    tiempo_laborado = Column(String(100), nullable=True)
    antiguedad_cargo = Column(String(50), nullable=True)
    ultima_empresa = Column(String(255), nullable=True)
    nivel_escolaridad = Column(String(100), nullable=True)
    detalle_titulos = Column(String(500), nullable=True)
    areas_formacion = Column(JSON, nullable=True)  # ["Ingenieria", "Seguridad Industrial", ...]

    # ── 5. SALUD, DOTACIÓN Y HÁBITOS DE VIDA ──
    eps_actual = Column(String(255), nullable=True)
    fondo_pensiones = Column(String(255), nullable=True)
    grupo_sanguineo = Column(String(10), nullable=True)  # A, B, AB, O
    tipo_rh = Column(String(10), nullable=True)
    discapacidad = Column(Boolean, default=False)
    tipo_discapacidad = Column(String(100), nullable=True)  # FISICA, VISUAL, AUDITIVA, COGNITIVA, MULTIPLE
    porcentaje_discapacidad = Column(Integer, nullable=True)  # 0-100
    diagnostico_previo = Column(Boolean, default=False)
    diagnostico_detalle = Column(String(500), nullable=True)
    actividad_fisica = Column(String(10), nullable=True)
    consumo_cigarrillo = Column(String(50), nullable=True)
    consumo_alcohol = Column(String(50), nullable=True)
    talla_camisa = Column(String(10), nullable=True)
    talla_pantalon = Column(String(10), nullable=True)
    talla_chaqueta = Column(String(10), nullable=True)
    talla_overol = Column(String(10), nullable=True)
    talla_calzado = Column(String(10), nullable=True)

    # ── 6. REFERENCIAS PERSONALES ──
    referencia_1_nombre = Column(String(255), nullable=True)
    referencia_1_ocupacion = Column(String(255), nullable=True)
    referencia_1_telefono = Column(String(50), nullable=True)
    referencia_2_nombre = Column(String(255), nullable=True)
    referencia_2_ocupacion = Column(String(255), nullable=True)
    referencia_2_telefono = Column(String(50), nullable=True)

    # ── 7. FIRMA Y CONSENTIMIENTO ──
    consentimiento_informado = Column(Boolean, default=False)
    fecha_firma = Column(Date, nullable=True)

    # ── METADATOS ──
    completado = Column(Boolean, default=False)
    fuente = Column(String(50), default="MANUAL")  # MANUAL | IMPORTADO
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    empleado = relationship("Empleado")
