# ============================================================
# SERVICIO INDICADORES OFICIALES SST
# H-016: TF, TG, TI, Mortalidad, Ausentismo
# formulas: GTC 45 / Res.1401 / Decreto 1072
# ============================================================

from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.models.empleado import Empleado
from app.models.incidente import IncidenteAccidenteSST, IncidenteLesionadoSST
from app.models.ausentismo_sst import AusentismoSST


DIAS_LABORALES_MES = 22
DIAS_LABORALES_ANIO = 240
HORAS_JORNADA_DEFAULT = 8


def _obtener_empleados_activos(db: Session, empresa_id: int) -> int:
    return (
        db.query(func.count(Empleado.id))
        .filter(Empleado.empresa_id == empresa_id, Empleado.activo == True)
        .scalar()
    )


def _obtener_horas_trabajadas(
    db: Session, empresa_id: int, fecha_inicio: date, fecha_fin: date
) -> float:
    num_empleados = _obtener_empleados_activos(db, empresa_id)
    jornada = (
        db.query(func.avg(Empleado.jornada_laboral_diaria))
        .filter(Empleado.empresa_id == empresa_id, Empleado.activo == True)
        .scalar()
    ) or HORAS_JORNADA_DEFAULT

    dias = (fecha_fin - fecha_inicio).days + 1
    return num_empleados * jornada * dias


def calcular_tasa_frecuencia(
    db: Session,
    empresa_id: int,
    fecha_inicio: date,
    fecha_fin: date,
) -> dict:
    """TF = (Nro accidentes x 1.000.000) / Horas hombre trabajadas"""
    accidentes = (
        db.query(func.count(IncidenteAccidenteSST.id))
        .filter(
            IncidenteAccidenteSST.empresa_id == empresa_id,
            IncidenteAccidenteSST.fecha_evento >= fecha_inicio,
            IncidenteAccidenteSST.fecha_evento <= fecha_fin,
            IncidenteAccidenteSST.activo == True,
        )
        .scalar()
    )

    horas_trabajadas = _obtener_horas_trabajadas(db, empresa_id, fecha_inicio, fecha_fin)

    tf = (accidentes * 1_000_000) / horas_trabajadas if horas_trabajadas > 0 else 0

    return {
        "indicador": "TF",
        "nombre": "Tasa de Frecuencia",
        "formula": f"({accidentes} x 1.000.000) / {horas_trabajadas:,.0f}",
        "resultado": round(tf, 4),
        "unidad": "por millon de horas-hombre",
        "accidentes": accidentes,
        "horas_trabajadas": round(horas_trabajadas, 2),
        "periodo": {"inicio": fecha_inicio.isoformat(), "fin": fecha_fin.isoformat()},
    }


def calcular_tasa_gravedad(
    db: Session,
    empresa_id: int,
    fecha_inicio: date,
    fecha_fin: date,
) -> dict:
    """TG = (Dias incapacidad x 1.000.000) / Horas hombre trabajadas"""
    dias_incapacidad = (
        db.query(func.coalesce(func.sum(IncidenteLesionadoSST.dias_incapacidad), 0))
        .join(IncidenteAccidenteSST, IncidenteLesionadoSST.incidente_id == IncidenteAccidenteSST.id)
        .filter(
            IncidenteAccidenteSST.empresa_id == empresa_id,
            IncidenteAccidenteSST.fecha_evento >= fecha_inicio,
            IncidenteAccidenteSST.fecha_evento <= fecha_fin,
            IncidenteAccidenteSST.activo == True,
        )
        .scalar()
    )

    horas_trabajadas = _obtener_horas_trabajadas(db, empresa_id, fecha_inicio, fecha_fin)

    tg = (dias_incapacidad * 1_000_000) / horas_trabajadas if horas_trabajadas > 0 else 0

    return {
        "indicador": "TG",
        "nombre": "Tasa de Gravedad",
        "formula": f"({dias_incapacidad} x 1.000.000) / {horas_trabajadas:,.0f}",
        "resultado": round(tg, 4),
        "unidad": "por millon de horas-hombre",
        "dias_incapacidad": dias_incapacidad,
        "horas_trabajadas": round(horas_trabajadas, 2),
        "periodo": {"inicio": fecha_inicio.isoformat(), "fin": fecha_fin.isoformat()},
    }


def calcular_tasa_incapacidad(
    db: Session,
    empresa_id: int,
    fecha_inicio: date,
    fecha_fin: date,
) -> dict:
    """TI = (Dias incapacidad / Dias laborables) x 100"""
    dias_incapacidad = (
        db.query(func.coalesce(func.sum(IncidenteLesionadoSST.dias_incapacidad), 0))
        .join(IncidenteAccidenteSST, IncidenteLesionadoSST.incidente_id == IncidenteAccidenteSST.id)
        .filter(
            IncidenteAccidenteSST.empresa_id == empresa_id,
            IncidenteAccidenteSST.fecha_evento >= fecha_inicio,
            IncidenteAccidenteSST.fecha_evento <= fecha_fin,
            IncidenteAccidenteSST.activo == True,
        )
        .scalar()
    )

    num_empleados = _obtener_empleados_activos(db, empresa_id)
    dias = (fecha_fin - fecha_inicio).days + 1
    dias_laborables = num_empleados * dias

    ti = (dias_incapacidad / dias_laborables * 100) if dias_laborables > 0 else 0

    return {
        "indicador": "TI",
        "nombre": "Tasa de Incapacidad",
        "formula": f"({dias_incapacidad} / {dias_laborables}) x 100",
        "resultado": round(ti, 4),
        "unidad": "%",
        "dias_incapacidad": dias_incapacidad,
        "dias_laborables": dias_laborables,
        "periodo": {"inicio": fecha_inicio.isoformat(), "fin": fecha_fin.isoformat()},
    }


def calcular_tasa_mortalidad(
    db: Session,
    empresa_id: int,
    fecha_inicio: date,
    fecha_fin: date,
) -> dict:
    """Mortalidad = (Defunciones / Empleados) x 1000"""
    defunciones = (
        db.query(func.count(IncidenteLesionadoSST.id))
        .join(IncidenteAccidenteSST, IncidenteLesionadoSST.incidente_id == IncidenteAccidenteSST.id)
        .filter(
            IncidenteAccidenteSST.empresa_id == empresa_id,
            IncidenteAccidenteSST.fecha_evento >= fecha_inicio,
            IncidenteAccidenteSST.fecha_evento <= fecha_fin,
            IncidenteAccidenteSST.activo == True,
            IncidenteLesionadoSST.gravedad == "MORTAL",
        )
        .scalar()
    )

    num_empleados = _obtener_empleados_activos(db, empresa_id)

    mortalidad = (defunciones / num_empleados * 1000) if num_empleados > 0 else 0

    return {
        "indicador": "MORTALIDAD",
        "nombre": "Tasa de Mortalidad Laboral",
        "formula": f"({defunciones} / {num_empleados}) x 1000",
        "resultado": round(mortalidad, 4),
        "unidad": "por 1000 empleados",
        "defunciones": defunciones,
        "num_empleados": num_empleados,
        "periodo": {"inicio": fecha_inicio.isoformat(), "fin": fecha_fin.isoformat()},
    }


def calcular_tasa_ausentismo(
    db: Session,
    empresa_id: int,
    fecha_inicio: date,
    fecha_fin: date,
) -> dict:
    """Ausentismo = (Dias ausentismo / Dias laborables) x 100"""
    dias_ausentismo = (
        db.query(func.coalesce(func.sum(AusentismoSST.dias_ausentismo), 0))
        .filter(
            AusentismoSST.empresa_id == empresa_id,
            AusentismoSST.fecha_inicio >= fecha_inicio,
            AusentismoSST.activo == True,
        )
        .scalar()
    )

    num_empleados = _obtener_empleados_activos(db, empresa_id)
    dias = (fecha_fin - fecha_inicio).days + 1
    dias_laborables = num_empleados * dias

    ausentismo = (dias_ausentismo / dias_laborables * 100) if dias_laborables > 0 else 0

    return {
        "indicador": "AUSENTISMO",
        "nombre": "Tasa de Ausentismo",
        "formula": f"({dias_ausentismo} / {dias_laborables}) x 100",
        "resultado": round(ausentismo, 4),
        "unidad": "%",
        "dias_ausentismo": dias_ausentismo,
        "dias_laborables": dias_laborables,
        "periodo": {"inicio": fecha_inicio.isoformat(), "fin": fecha_fin.isoformat()},
    }


def calcular_indicadores_oficiales(
    db: Session,
    empresa_id: int,
    fecha_inicio: date,
    fecha_fin: date,
) -> dict:
    return {
        "tasa_frecuencia": calcular_tasa_frecuencia(db, empresa_id, fecha_inicio, fecha_fin),
        "tasa_gravedad": calcular_tasa_gravedad(db, empresa_id, fecha_inicio, fecha_fin),
        "tasa_incapacidad": calcular_tasa_incapacidad(db, empresa_id, fecha_inicio, fecha_fin),
        "mortalidad": calcular_tasa_mortalidad(db, empresa_id, fecha_inicio, fecha_fin),
        "ausentismo": calcular_tasa_ausentismo(db, empresa_id, fecha_inicio, fecha_fin),
    }
