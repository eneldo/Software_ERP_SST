from typing import Optional, List, Any
from datetime import date
from pydantic import ConfigDict,  BaseModel


class HijoInfo(BaseModel):
    nombre: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    edad: Optional[int] = None
    escolaridad: Optional[str] = None


class EmpleadoPerfilCreate(BaseModel):
    empresa_id: int
    empleado_id: int
    # 1. Identificación
    nombres_completos: Optional[str] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    libreta_militar: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    lugar_nacimiento: Optional[str] = None
    edad: Optional[int] = None
    raza_pertenencia_etnica: Optional[str] = None
    telefono_celular: Optional[str] = None
    # 2. Sociodemográficas
    estado_civil: Optional[str] = None
    conyuge_nombre: Optional[str] = None
    conyuge_ocupacion: Optional[str] = None
    conyuge_edad: Optional[int] = None
    conyuge_celular: Optional[str] = None
    numero_dependientes: Optional[int] = None
    tiene_hijos: Optional[bool] = False
    num_hijos: Optional[int] = 0
    hijos: Optional[List[HijoInfo]] = None
    # 3. Vivienda
    direccion_residencia: Optional[str] = None
    barrio: Optional[str] = None
    ciudad_municipio: Optional[str] = None
    estrato_socioeconomico: Optional[int] = None
    tipo_vivienda: Optional[str] = None
    servicios_vivienda: Optional[List[str]] = None
    medio_transporte: Optional[str] = None
    medio_transporte_otro: Optional[str] = None
    tiempo_desplazamiento: Optional[str] = None
    # 4. Laboral y formación
    cargo_actual: Optional[str] = None
    area_departamento: Optional[str] = None
    sede_centro_trabajo: Optional[str] = None
    tipo_contrato: Optional[str] = None
    tiempo_laborado: Optional[str] = None
    antiguedad_cargo: Optional[str] = None
    ultima_empresa: Optional[str] = None
    nivel_escolaridad: Optional[str] = None
    detalle_titulos: Optional[str] = None
    areas_formacion: Optional[List[str]] = None
    # 5. Salud y hábitos
    eps_actual: Optional[str] = None
    fondo_pensiones: Optional[str] = None
    grupo_sanguineo: Optional[str] = None
    tipo_rh: Optional[str] = None
    discapacidad: Optional[bool] = False
    tipo_discapacidad: Optional[str] = None
    porcentaje_discapacidad: Optional[int] = None
    diagnostico_previo: Optional[bool] = False
    diagnostico_detalle: Optional[str] = None
    actividad_fisica: Optional[str] = None
    consumo_cigarrillo: Optional[str] = None
    consumo_alcohol: Optional[str] = None
    talla_camisa: Optional[str] = None
    talla_pantalon: Optional[str] = None
    talla_chaqueta: Optional[str] = None
    talla_overol: Optional[str] = None
    talla_calzado: Optional[str] = None
    # 6. Referencias
    referencia_1_nombre: Optional[str] = None
    referencia_1_ocupacion: Optional[str] = None
    referencia_1_telefono: Optional[str] = None
    referencia_2_nombre: Optional[str] = None
    referencia_2_ocupacion: Optional[str] = None
    referencia_2_telefono: Optional[str] = None
    # 7. Consentimiento
    consentimiento_informado: Optional[bool] = False
    fecha_firma: Optional[date] = None
    completado: Optional[bool] = False


class EmpleadoPerfilUpdate(BaseModel):
    nombres_completos: Optional[str] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    libreta_militar: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    lugar_nacimiento: Optional[str] = None
    edad: Optional[int] = None
    raza_pertenencia_etnica: Optional[str] = None
    telefono_celular: Optional[str] = None
    estado_civil: Optional[str] = None
    conyuge_nombre: Optional[str] = None
    conyuge_ocupacion: Optional[str] = None
    conyuge_edad: Optional[int] = None
    conyuge_celular: Optional[str] = None
    numero_dependientes: Optional[int] = None
    tiene_hijos: Optional[bool] = None
    num_hijos: Optional[int] = None
    hijos: Optional[List[HijoInfo]] = None
    direccion_residencia: Optional[str] = None
    barrio: Optional[str] = None
    ciudad_municipio: Optional[str] = None
    estrato_socioeconomico: Optional[int] = None
    tipo_vivienda: Optional[str] = None
    servicios_vivienda: Optional[List[str]] = None
    medio_transporte: Optional[str] = None
    medio_transporte_otro: Optional[str] = None
    tiempo_desplazamiento: Optional[str] = None
    cargo_actual: Optional[str] = None
    area_departamento: Optional[str] = None
    sede_centro_trabajo: Optional[str] = None
    tipo_contrato: Optional[str] = None
    tiempo_laborado: Optional[str] = None
    antiguedad_cargo: Optional[str] = None
    ultima_empresa: Optional[str] = None
    nivel_escolaridad: Optional[str] = None
    detalle_titulos: Optional[str] = None
    areas_formacion: Optional[List[str]] = None
    eps_actual: Optional[str] = None
    fondo_pensiones: Optional[str] = None
    grupo_sanguineo: Optional[str] = None
    tipo_rh: Optional[str] = None
    discapacidad: Optional[bool] = None
    tipo_discapacidad: Optional[str] = None
    porcentaje_discapacidad: Optional[int] = None
    diagnostico_previo: Optional[bool] = None
    diagnostico_detalle: Optional[str] = None
    actividad_fisica: Optional[str] = None
    consumo_cigarrillo: Optional[str] = None
    consumo_alcohol: Optional[str] = None
    talla_camisa: Optional[str] = None
    talla_pantalon: Optional[str] = None
    talla_chaqueta: Optional[str] = None
    talla_overol: Optional[str] = None
    talla_calzado: Optional[str] = None
    referencia_1_nombre: Optional[str] = None
    referencia_1_ocupacion: Optional[str] = None
    referencia_1_telefono: Optional[str] = None
    referencia_2_nombre: Optional[str] = None
    referencia_2_ocupacion: Optional[str] = None
    referencia_2_telefono: Optional[str] = None
    consentimiento_informado: Optional[bool] = None
    fecha_firma: Optional[date] = None
    completado: Optional[bool] = None


class EmpleadoPerfilResponse(BaseModel):
    id: int
    empresa_id: int
    empleado_id: int
    nombres_completos: Optional[str] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    libreta_militar: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    lugar_nacimiento: Optional[str] = None
    edad: Optional[int] = None
    raza_pertenencia_etnica: Optional[str] = None
    telefono_celular: Optional[str] = None
    estado_civil: Optional[str] = None
    conyuge_nombre: Optional[str] = None
    conyuge_ocupacion: Optional[str] = None
    conyuge_edad: Optional[int] = None
    conyuge_celular: Optional[str] = None
    numero_dependientes: Optional[int] = None
    tiene_hijos: Optional[bool] = None
    num_hijos: Optional[int] = None
    hijos: Optional[Any] = None
    direccion_residencia: Optional[str] = None
    barrio: Optional[str] = None
    ciudad_municipio: Optional[str] = None
    estrato_socioeconomico: Optional[int] = None
    tipo_vivienda: Optional[str] = None
    servicios_vivienda: Optional[Any] = None
    medio_transporte: Optional[str] = None
    medio_transporte_otro: Optional[str] = None
    tiempo_desplazamiento: Optional[str] = None
    cargo_actual: Optional[str] = None
    area_departamento: Optional[str] = None
    sede_centro_trabajo: Optional[str] = None
    tipo_contrato: Optional[str] = None
    tiempo_laborado: Optional[str] = None
    antiguedad_cargo: Optional[str] = None
    ultima_empresa: Optional[str] = None
    nivel_escolaridad: Optional[str] = None
    detalle_titulos: Optional[str] = None
    areas_formacion: Optional[Any] = None
    eps_actual: Optional[str] = None
    fondo_pensiones: Optional[str] = None
    grupo_sanguineo: Optional[str] = None
    tipo_rh: Optional[str] = None
    discapacidad: Optional[bool] = None
    tipo_discapacidad: Optional[str] = None
    porcentaje_discapacidad: Optional[int] = None
    diagnostico_previo: Optional[bool] = None
    diagnostico_detalle: Optional[str] = None
    actividad_fisica: Optional[str] = None
    consumo_cigarrillo: Optional[str] = None
    consumo_alcohol: Optional[str] = None
    talla_camisa: Optional[str] = None
    talla_pantalon: Optional[str] = None
    talla_chaqueta: Optional[str] = None
    talla_overol: Optional[str] = None
    talla_calzado: Optional[str] = None
    referencia_1_nombre: Optional[str] = None
    referencia_1_ocupacion: Optional[str] = None
    referencia_1_telefono: Optional[str] = None
    referencia_2_nombre: Optional[str] = None
    referencia_2_ocupacion: Optional[str] = None
    referencia_2_telefono: Optional[str] = None
    consentimiento_informado: Optional[bool] = None
    fecha_firma: Optional[date] = None
    completado: Optional[bool] = None
    fuente: Optional[str] = None
    fecha_creacion: Optional[Any] = None
    fecha_actualizacion: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)
