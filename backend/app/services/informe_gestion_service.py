# ============================================================
# SERVICIO DE CONSOLIDACIÓN DEL INFORME DE GESTIÓN SG-SST
#
# Motor que consulta todos los módulos del SG-SST y genera
# el snapshot histórico de datos para el informe.
#
# Ubicación: backend/app/services/informe_gestion_service.py
# ============================================================

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.empleado import Empleado
from app.models.plan_anual import PlanAnualSST
from app.models.objetivo_sst import ObjetivoSST
from app.models.indicador_sst import IndicadorSST
from app.models.incidente import IncidenteAccidenteSST
from app.models.ausentismo_sst import AusentismoSST
from app.models.capacitacion import CapacitacionSST
from app.models.inspeccion import InspeccionSST, InspeccionHallazgoSST
from app.models.auditoria_sst import AuditoriaSST, AuditoriaHallazgoSST
from app.models.capa import CapaSST
from app.models.matriz_legal import MatrizLegalSST
from app.models.matriz_peligros import MatrizPeligrosSST
from app.models.epp import EPPCatalogo, EPPEntrega
from app.models.comite_sst import ComiteSST, ComiteReunionSST
from app.models.emergencia_sst import BrigadaEmergencia, SimulacroEmergencia
from app.models.examen_medico import ExamenMedico
from app.models.estandar_minimo_criterio import EstandarMinimoCriterio
from app.models.evaluacion_inicial import EvaluacionInicialSST, EvaluacionInicialItemSST
from app.models.politica_sst import PoliticaSST
from app.models.informe_gestion import (
    InformeGestionSGSST,
    InformeGestionSeccion,
    InformeGestionVersion,
)


class InformeGestionService:
    """Servicio para consolidar datos del SG-SST en el Informe de Gestión."""

    def __init__(self, db: Session):
        self.db = db

    def generar_codigo_informe(self, empresa_id: int, anio: int) -> str:
        """Genera código único para el informe."""
        empresa = self.db.query(Empresa).filter(Empresa.id == empresa_id).first()
        prefijo = empresa.nit[:3].upper() if empresa and empresa.nit else "SGS"
        consecutivo = (
            self.db.query(func.count(InformeGestionSGSST.id))
            .filter(
                InformeGestionSGSST.empresa_id == empresa_id,
                InformeGestionSGSST.anio == anio,
            )
            .scalar()
            or 0
        )
        return f"IG-{prefijo}-{anio}-{consecutivo + 1:04d}"

    def crear_informe(
        self,
        empresa_id: int,
        usuario_id: int,
        anio: int,
        sede_id: Optional[int] = None,
    ) -> InformeGestionSGSST:
        """Crea un nuevo informe con datos básicos de la empresa."""
        empresa = self.db.query(Empresa).filter(Empresa.id == empresa_id).first()
        if not empresa:
            raise ValueError("Empresa no encontrada")

        codigo = self.generar_codigo_informe(empresa_id, anio)

        informe = InformeGestionSGSST(
            empresa_id=empresa_id,
            usuario_id=usuario_id,
            codigo=codigo,
            anio=anio,
            sede_id=sede_id,
            responsable_sst_nombre=empresa.responsable_sst,
            representante_legal_nombre=empresa.representante_legal,
        )
        self.db.add(informe)
        self.db.flush()

        self._crear_secciones_iniciales(informe.id, empresa_id)
        self.db.commit()
        self.db.refresh(informe)
        return informe

    def _crear_secciones_iniciales(self, informe_id: int, empresa_id: int):
        """Crea las secciones predefinidas del informe."""
        secciones = [
            ("5.1_PORTADA", "Portada", 1),
            ("5.2_INFO_GENERAL", "Información General", 2),
            ("5.3_RESUMEN_EJECUTIVO", "Resumen Ejecutivo", 3),
            ("5.4_PLAN_ANUAL", "Plan Anual de Trabajo SG-SST", 4),
            ("5.5_OBJETIVOS", "Objetivos SG-SST", 5),
            ("5.6_INDICADORES", "Indicadores", 6),
            ("5.7_ACCIDENTALIDAD", "Accidentalidad", 7),
            ("5.8_INCIDENTES", "Incidentes", 8),
            ("5.9_ENFERMEDAD_LABORAL", "Enfermedad Laboral", 9),
            ("5.10_AUSENTISMO", "Ausentismo", 10),
            ("5.11_EVALUACIONES_MEDICAS", "Evaluaciones Médicas Ocupacionales", 11),
            ("5.12_PVE", "Programas de Vigilancia Epidemiológica", 12),
            ("5.13_MATRIZ_PELIGROS", "Matriz de Peligros", 13),
            ("5.14_INSPECCIONES", "Inspecciones de Seguridad", 14),
            ("5.15_CAPACITACION", "Capacitación SG-SST", 15),
            ("5.16_INDUCCION", "Inducción y Reinducción", 16),
            ("5.17_EPP", "Elementos de Protección Personal", 17),
            ("5.18_COPASST", "COPASST / Vigía SST", 18),
            ("5.19_CONVIVENCIA", "Comité de Convivencia Laboral", 19),
            ("5.20_EMERGENCIAS", "Emergencias", 20),
            ("5.21_AUDITORIAS", "Auditorías", 21),
            ("5.22_ESTANDARES", "Estándares Mínimos", 22),
            ("5.23_MATRIZ_LEGAL", "Matriz Legal", 23),
            ("5.24_CAPA", "Acciones Correctivas, Preventivas y de Mejora", 24),
            ("5.25_RECURSOS", "Gestión de Recursos", 25),
            ("5.26_RENDICION_CUENTAS", "Rendición de Cuentas", 26),
            ("5.27_RECOMENDACIONES", "Recomendaciones del Responsable SG-SST", 27),
            ("5.28_REVISION_DIRECCION", "Revisión por la Alta Dirección", 28),
        ]

        for codigo, nombre, orden in secciones:
            seccion = InformeGestionSeccion(
                informe_id=informe_id,
                empresa_id=empresa_id,
                codigo_seccion=codigo,
                nombre_seccion=nombre,
                orden=orden,
            )
            self.db.add(seccion)

    def consolidar_datos(
        self, informe_id: int, forzar: bool = False
    ) -> Dict[str, Any]:
        """
        Consolida TODOS los datos del SG-SST en el informe.
        Genera snapshot histórico que no cambia al modificar datos operativos.
        """
        informe = (
            self.db.query(InformeGestionSGSST)
            .filter(InformeGestionSGSST.id == informe_id)
            .first()
        )
        if not informe:
            raise ValueError("Informe no encontrado")

        if informe.estado not in ("BORRADOR", "DEVUELTO") and not forzar:
            raise ValueError(
                "No se puede consolidar un informe en estado: "
                + informe.estado
            )

        empresa_id = informe.empresa_id
        anio = informe.anio
        sede_id = informe.sede_id

        datos = {
            "empresa": self._consolidar_empresa(empresa_id),
            "plan_anual": self._consolidar_plan_anual(empresa_id, anio, sede_id),
            "objetivos": self._consolidar_objetivos(empresa_id, anio),
            "indicadores": self._consolidar_indicadores(empresa_id, anio, sede_id),
            "accidentalidad": self._consolidar_accidentalidad(
                empresa_id, anio, sede_id
            ),
            "incidentes": self._consolidar_incidentes(empresa_id, anio, sede_id),
            "ausentismo": self._consolidar_ausentismo(empresa_id, anio, sede_id),
            "capacitaciones": self._consolidar_capacitaciones(
                empresa_id, anio, sede_id
            ),
            "inspecciones": self._consolidar_inspecciones(
                empresa_id, anio, sede_id
            ),
            "auditorias": self._consolidar_auditorias(empresa_id, anio, sede_id),
            "matriz_legal": self._consolidar_matriz_legal(empresa_id),
            "matriz_peligros": self._consolidar_matriz_peligros(empresa_id),
            "epp": self._consolidar_epp(empresa_id, anio),
            "comites": self._consolidar_comites(empresa_id, anio),
            "emergencias": self._consolidar_emergencias(empresa_id, anio),
            "examenes_medicos": self._consolidar_examenes_medicos(
                empresa_id, anio, sede_id
            ),
            "estandares": self._consolidar_estandares(empresa_id),
            "politicas": self._consolidar_politicas(empresa_id),
            "capa": self._consolidar_capa(empresa_id, anio, sede_id),
        }

        datos["resumen_ejecutivo"] = self._generar_resumen_ejecutivo(datos)
        datos["indicadores_calculados"] = self._calcular_indicadores_generales(
            datos
        )

        informe.datos_consolidados = datos
        informe.fecha_generacion = datetime.utcnow()
        informe.total_secciones = len(
            self.db.query(InformeGestionSeccion)
            .filter(InformeGestionSeccion.informe_id == informe_id)
            .all()
        )

        self._actualizar_cumplimientos(informe, datos)
        self._guardar_version(informe, "CONSOLIDACION")
        self.db.commit()
        self.db.refresh(informe)

        return {
            "informe_id": informe_id,
            "secciones_consolidadas": informe.total_secciones,
            "total_registros": sum(
                len(v) if isinstance(v, list) else 1
                for v in datos.values()
                if v is not None
            ),
            "mensaje": "Datos consolidados exitosamente",
        }

    def _consolidar_empresa(self, empresa_id: int) -> Dict:
        empresa = self.db.query(Empresa).filter(Empresa.id == empresa_id).first()
        if not empresa:
            return {}
        total_empleados = (
            self.db.query(func.count(Empleado.id))
            .filter(
                Empleado.empresa_id == empresa_id,
                Empleado.estado_laboral == "ACTIVO",
            )
            .scalar()
            or 0
        )
        total_sedes = (
            self.db.query(func.count(Sede.id))
            .filter(Sede.empresa_id == empresa_id)
            .scalar()
            or 0
        )
        return {
            "nombre": empresa.nombre,
            "nit": empresa.nit,
            "actividad_economica": empresa.actividad_economica,
            "clase_riesgo": empresa.clase_riesgo,
            "arl": empresa.arl,
            "numero_trabajadores": total_empleados,
            "total_sedes": total_sedes,
            "responsable_sst": empresa.responsable_sst,
            "representante_legal": empresa.representante_legal,
        }

    def _consolidar_plan_anual(
        self, empresa_id: int, anio: int, sede_id: Optional[int]
    ) -> Dict:
        query = self.db.query(PlanAnualSST).filter(
            PlanAnualSST.empresa_id == empresa_id,
            func.extract("year", PlanAnualSST.fecha_inicio) == anio,
        )
        if sede_id:
            query = query.filter(PlanAnualSST.sede_id == sede_id)
        actividades = query.all()
        total = len(actividades)
        ejecutadas = sum(1 for a in actividades if a.estado == "EJECUTADO")
        pendientes = sum(1 for a in actividades if a.estado in ("PLANIFICADO", "EN_PROCESO"))
        vencidas = sum(1 for a in actividades if a.estado == "VENCIDO")
        canceladas = sum(1 for a in actividades if a.estado == "CANCELADO")
        return {
            "total_programadas": total,
            "ejecutadas": ejecutadas,
            "pendientes": pendientes,
            "vencidas": vencidas,
            "canceladas": canceladas,
            "porcentaje_cumplimiento": round((ejecutadas / total * 100) if total > 0 else 0, 2),
            "actividades": [
                {
                    "id": a.id,
                    "actividad": a.actividad,
                    "responsable": a.responsable,
                    "fecha_inicio": str(a.fecha_inicio) if a.fecha_inicio else None,
                    "fecha_fin": str(a.fecha_fin) if a.fecha_fin else None,
                    "estado": a.estado,
                    "porcentaje_avance": float(a.porcentaje_avance or 0),
                }
                for a in actividades[:50]
            ],
        }

    def _consolidar_objetivos(self, empresa_id: int, anio: int) -> Dict:
        objetivos = (
            self.db.query(ObjetivoSST)
            .filter(
                ObjetivoSST.empresa_id == empresa_id,
                func.extract("year", ObjetivoSST.fecha_inicio) == anio,
            )
            .all()
        )
        total = len(objetivos)
        cumplidos = sum(1 for o in objetivos if o.estado == "CUMPLIDO")
        return {
            "total": total,
            "cumplidos": cumplidos,
            "parciales": sum(1 for o in objetivos if o.estado == "EN_PROCESO"),
            "no_cumplidos": sum(1 for o in objetivos if o.estado == "NO_CUMPLIDO"),
            "porcentaje_cumplimiento": round((cumplidos / total * 100) if total > 0 else 0, 2),
            "objetivos": [
                {
                    "id": o.id,
                    "objetivo": o.objetivo,
                    "meta": o.meta,
                    "indicador": o.indicador,
                    "cumplimiento": float(o.cumplimiento or 0),
                    "estado": o.estado,
                }
                for o in objetivos[:30]
            ],
        }

    def _consolidar_indicadores(
        self, empresa_id: int, anio: int, sede_id: Optional[int]
    ) -> Dict:
        query = self.db.query(IndicadorSST).filter(
            IndicadorSST.empresa_id == empresa_id,
            func.extract("year", IndicadorSST.periodo_inicio) == anio,
        )
        if sede_id:
            query = query.filter(IndicadorSST.sede_id == sede_id)
        indicadores = query.all()
        return {
            "total": len(indicadores),
            "estructura": sum(1 for i in indicadores if i.categoria == "ESTRUCTURA"),
            "proceso": sum(1 for i in indicadores if i.categoria == "PROCESO"),
            "resultado": sum(1 for i in indicadores if i.categoria == "RESULTADO"),
            "verde": sum(1 for i in indicadores if i.semaforo == "VERDE"),
            "amarillo": sum(1 for i in indicadores if i.semaforo == "AMARILLO"),
            "rojo": sum(1 for i in indicadores if i.semaforo == "ROJO"),
            "indicadores": [
                {
                    "id": i.id,
                    "nombre": i.nombre,
                    "tipo": i.tipo_indicador,
                    "formula": i.formula,
                    "meta": float(i.meta or 0),
                    "resultado": float(i.resultado or 0),
                    "semaforo": i.semaforo,
                    "tendencia": i.tendencia,
                }
                for i in indicadores[:30]
            ],
        }

    def _consolidar_accidentalidad(
        self, empresa_id: int, anio: int, sede_id: Optional[int]
    ) -> Dict:
        query = self.db.query(IncidenteAccidenteSST).filter(
            IncidenteAccidenteSST.empresa_id == empresa_id,
            IncidenteAccidenteSST.tipo_evento == "ACCIDENTE",
            func.extract("year", IncidenteAccidenteSST.fecha_evento) == anio,
        )
        if sede_id:
            query = query.filter(IncidenteAccidenteSST.sede_id == sede_id)
        accidentes = query.all()
        total = len(accidentes)
        leves = sum(1 for a in accidentes if a.severidad == "LEVE")
        graves = sum(1 for a in accidentes if a.severidad == "GRAVE")
        mortales = sum(1 for a in accidentes if a.severidad == "MORTAL")
        dias_incapacidad = sum(a.dias_incapacidad or 0 for a in accidentes)
        investigados = sum(1 for a in accidentes if a.investigado)
        return {
            "total": total,
            "leves": leves,
            "graves": graves,
            "mortales": mortales,
            "dias_incapacidad": dias_incapacidad,
            "investigados": investigados,
            "pendientes_investigacion": total - investigados,
        }

    def _consolidar_incidentes(
        self, empresa_id: int, anio: int, sede_id: Optional[int]
    ) -> Dict:
        query = self.db.query(IncidenteAccidenteSST).filter(
            IncidenteAccidenteSST.empresa_id == empresa_id,
            IncidenteAccidenteSST.tipo_evento == "INCIDENTE",
            func.extract("year", IncidenteAccidenteSST.fecha_evento) == anio,
        )
        if sede_id:
            query = query.filter(IncidenteAccidenteSST.sede_id == sede_id)
        incidentes = query.all()
        total = len(incidentes)
        investigados = sum(1 for i in incidentes if i.investigado)
        return {
            "total": total,
            "investigados": investigados,
            "pendientes": total - investigados,
        }

    def _consolidar_ausentismo(
        self, empresa_id: int, anio: int, sede_id: Optional[int]
    ) -> Dict:
        query = self.db.query(AusentismoSST).filter(
            AusentismoSST.empresa_id == empresa_id,
            func.extract("year", AusentismoSST.fecha_inicio) == anio,
        )
        registros = query.all()
        total_eventos = len(registros)
        dias_totales = sum(r.dias_ausentismo or 0 for r in registros)
        return {
            "total_eventos": total_eventos,
            "dias_totales": dias_totales,
            "tipos": {},
        }

    def _consolidar_capacitaciones(
        self, empresa_id: int, anio: int, sede_id: Optional[int]
    ) -> Dict:
        query = self.db.query(CapacitacionSST).filter(
            CapacitacionSST.empresa_id == empresa_id,
            func.extract("year", CapacitacionSST.fecha_programada) == anio,
        )
        if sede_id:
            query = query.filter(CapacitacionSST.sede_id == sede_id)
        capacitaciones = query.all()
        total = len(capacitaciones)
        ejecutadas = sum(1 for c in capacitaciones if c.estado == "EJECUTADA")
        return {
            "total_programadas": total,
            "ejecutadas": ejecutadas,
            "canceladas": sum(1 for c in capacitaciones if c.estado == "CANCELADA"),
            "porcentaje_cumplimiento": round((ejecutadas / total * 100) if total > 0 else 0, 2),
        }

    def _consolidar_inspecciones(
        self, empresa_id: int, anio: int, sede_id: Optional[int]
    ) -> Dict:
        query = self.db.query(InspeccionSST).filter(
            InspeccionSST.empresa_id == empresa_id,
            func.extract("year", InspeccionSST.fecha_programada) == anio,
        )
        if sede_id:
            query = query.filter(InspeccionSST.sede_id == sede_id)
        inspecciones = query.all()
        total = len(inspecciones)
        hallazgos = (
            self.db.query(func.count(InspeccionHallazgoSST.id))
            .join(InspeccionSST)
            .filter(
                InspeccionSST.empresa_id == empresa_id,
                func.extract("year", InspeccionSST.fecha_programada) == anio,
            )
            .scalar()
            or 0
        )
        return {
            "total_programadas": total,
            "ejecutadas": sum(1 for i in inspecciones if i.fecha_inspeccion),
            "total_hallazgos": hallazgos,
            "hallazgos_abiertos": 0,
            "hallazgos_cerrados": 0,
        }

    def _consolidar_auditorias(
        self, empresa_id: int, anio: int, sede_id: Optional[int]
    ) -> Dict:
        query = self.db.query(AuditoriaSST).filter(
            AuditoriaSST.empresa_id == empresa_id,
            func.extract("year", AuditoriaSST.fecha_programada) == anio,
        )
        auditorias = query.all()
        total = len(auditorias)
        hallazgos = (
            self.db.query(func.count(AuditoriaHallazgoSST.id))
            .join(AuditoriaSST)
            .filter(AuditoriaSST.empresa_id == empresa_id)
            .scalar()
            or 0
        )
        return {
            "total": total,
            "internas": sum(1 for a in auditorias if a.tipo_auditoria == "INTERNA"),
            "externas": sum(1 for a in auditorias if a.tipo_auditoria == "EXTERNA"),
            "total_hallazgos": hallazgos,
            "no_conformidades": sum(
                1
                for a in auditorias
                if hasattr(a, "no_conformidades") and a.no_conformidades
            ),
        }

    def _consolidar_matriz_legal(self, empresa_id: int) -> Dict:
        total = (
            self.db.query(func.count(MatrizLegalSST.id))
            .filter(MatrizLegalSST.empresa_id == empresa_id)
            .scalar()
            or 0
        )
        cumplidos = (
            self.db.query(func.count(MatrizLegalSST.id))
            .filter(
                MatrizLegalSST.empresa_id == empresa_id,
                MatrizLegalSST.estado_cumplimiento == "CUMPLE",
            )
            .scalar()
            or 0
        )
        pendientes = (
            self.db.query(func.count(MatrizLegalSST.id))
            .filter(
                MatrizLegalSST.empresa_id == empresa_id,
                MatrizLegalSST.estado_cumplimiento == "PENDIENTE",
            )
            .scalar()
            or 0
        )
        return {
            "total_requisitos": total,
            "cumplidos": cumplidos,
            "pendientes": pendientes,
            "no_cumple": total - cumplidos - pendientes,
            "porcentaje_cumplimiento": round((cumplidos / total * 100) if total > 0 else 0, 2),
        }

    def _consolidar_matriz_peligros(self, empresa_id: int) -> Dict:
        total = (
            self.db.query(func.count(MatrizPeligrosSST.id))
            .filter(MatrizPeligrosSST.empresa_id == empresa_id)
            .scalar()
            or 0
        )
        return {
            "total_peligros": total,
            "riesgos_aceptables": 0,
            "riesgos_moderados": 0,
            "riesgos_altos": 0,
            "riesgos_criticos": 0,
        }

    def _consolidar_epp(self, empresa_id: int, anio: int) -> Dict:
        total_catalogo = (
            self.db.query(func.count(EPPCatalogo.id))
            .filter(EPPCatalogo.empresa_id == empresa_id)
            .scalar()
            or 0
        )
        entregas = (
            self.db.query(func.count(EPPEntrega.id))
            .filter(
                EPPEntrega.empresa_id == empresa_id,
                func.extract("year", EPPEntrega.fecha_entrega) == anio,
            )
            .scalar()
            or 0
        )
        return {
            "total_catalogo": total_catalogo,
            "entregas_realizadas": entregas,
        }

    def _consolidar_comites(self, empresa_id: int, anio: int) -> Dict:
        comites = (
            self.db.query(ComiteSST)
            .filter(ComiteSST.empresa_id == empresa_id)
            .all()
        )
        total_reuniones = (
            self.db.query(func.count(ComiteReunionSST.id))
            .join(ComiteSST)
            .filter(
                ComiteSST.empresa_id == empresa_id,
                func.extract("year", ComiteReunionSST.fecha_reunion) == anio,
            )
            .scalar()
            or 0
        )
        return {
            "total_comites": len(comites),
            "total_reuniones": total_reuniones,
            "tipos": [c.tipo_comite for c in comites],
        }

    def _consolidar_emergencias(self, empresa_id: int, anio: int) -> Dict:
        brigadas = (
            self.db.query(func.count(BrigadaEmergencia.id))
            .filter(BrigadaEmergencia.empresa_id == empresa_id)
            .scalar()
            or 0
        )
        simulacros = (
            self.db.query(func.count(SimulacroEmergencia.id))
            .filter(
                SimulacroEmergencia.empresa_id == empresa_id,
                func.extract("year", SimulacroEmergencia.fecha_programada) == anio,
            )
            .scalar()
            or 0
        )
        return {
            "total_brigadas": brigadas,
            "total_simulacros": simulacros,
        }

    def _consolidar_examenes_medicos(
        self, empresa_id: int, anio: int, sede_id: Optional[int]
    ) -> Dict:
        query = (
            self.db.query(func.count(ExamenMedico.id))
            .join(Empleado, ExamenMedico.empleado_id == Empleado.id)
            .filter(
                Empleado.empresa_id == empresa_id,
                func.extract("year", ExamenMedico.fecha_examen) == anio,
            )
        )
        total = query.scalar() or 0
        return {
            "total_realizados": total,
            "programados": 0,
            "pendientes": 0,
            "aptos": 0,
            "no_aptos": 0,
            "con_restricciones": 0,
        }

    def _consolidar_estandares(self, empresa_id: int) -> Dict:
        empresa = self.db.query(Empresa).filter(Empresa.id == empresa_id).first()
        total_estandares = empresa.total_estandares_sst if empresa else 0
        return {
            "total_aplicables": total_estandares,
            "cumplidos": 0,
            "parciales": 0,
            "no_cumplidos": 0,
            "no_aplicables": 0,
            "puntaje": 0,
            "porcentaje": 0,
            "clasificacion": "Sin evaluar",
        }

    def _consolidar_politicas(self, empresa_id: int) -> Dict:
        total = (
            self.db.query(func.count(PoliticaSST.id))
            .filter(PoliticaSST.empresa_id == empresa_id)
            .scalar()
            or 0
        )
        aprobadas = (
            self.db.query(func.count(PoliticaSST.id))
            .filter(
                PoliticaSST.empresa_id == empresa_id,
                PoliticaSST.estado == "APROBADA",
            )
            .scalar()
            or 0
        )
        return {
            "total_politicas": total,
            "aprobadas": aprobadas,
            "divulgadas_copasst": 0,
        }

    def _consolidar_capa(
        self, empresa_id: int, anio: int, sede_id: Optional[int]
    ) -> Dict:
        query = self.db.query(CapaSST).filter(
            CapaSST.empresa_id == empresa_id,
            func.extract("year", CapaSST.fecha_creacion) == anio,
        )
        capas = query.all()
        total = len(capas)
        return {
            "total": total,
            "abiertas": sum(1 for c in capas if c.estado == "ABIERTA"),
            "en_ejecucion": sum(1 for c in capas if c.estado == "EN_EJECUCION"),
            "cerradas": sum(1 for c in capas if c.estado == "CERRADA"),
            "vencidas": 0,
        }

    def _generar_resumen_ejecutivo(self, datos: Dict) -> str:
        partes = []
        empresa = datos.get("empresa", {})
        if empresa.get("nombre"):
            partes.append(
                f"El presente informe corresponde a la gestión del SG-SST de "
                f"{empresa['nombre']} (NIT {empresa.get('nit', 'N/A')})."
            )
        plan = datos.get("plan_anual", {})
        if plan.get("total_programadas", 0) > 0:
            partes.append(
                f"Del Plan Anual se ejecutaron {plan.get('ejecutadas', 0)} de "
                f"{plan['total_programadas']} actividades "
                f"({plan.get('porcentaje_cumplimiento', 0)}% de cumplimiento)."
            )
        accidentalidad = datos.get("accidentalidad", {})
        if accidentalidad.get("total", 0) > 0:
            partes.append(
                f"Se registraron {accidentalidad['total']} accidentes de trabajo "
                f"con {accidentalidad.get('dias_incapacidad', 0)} días de incapacidad."
            )
        if not partes:
            return "Sin información consolidada para el periodo evaluado."
        return " ".join(partes)

    def _calcular_indicadores_generales(self, datos: Dict) -> Dict:
        plan = datos.get("plan_anual", {})
        indicadores = datos.get("indicadores", {})
        return {
            "cumplimiento_plan_anual": plan.get("porcentaje_cumplimiento", 0),
            "cumplimiento_objetivos": datos.get("objetivos", {}).get(
                "porcentaje_cumplimiento", 0
            ),
            "cumplimiento_legal": datos.get("matriz_legal", {}).get(
                "porcentaje_cumplimiento", 0
            ),
            "indicadores_verde": indicadores.get("verde", 0),
            "indicadores_amarillo": indicadores.get("amarillo", 0),
            "indicadores_rojo": indicadores.get("rojo", 0),
        }

    def _actualizar_cumplimientos(self, informe: InformeGestionSGSST, datos: Dict):
        calculados = datos.get("indicadores_calculados", {})
        informe.cumplimiento_plan_anual = calculados.get("cumplimiento_plan_anual")
        informe.cumplimiento_estandares = calculados.get("cumplimiento_legal")
        total = 0
        count = 0
        for key in ("cumplimiento_plan_anual", "cumplimiento_objetivos", "cumplimiento_legal"):
            val = calculados.get(key, 0)
            if val and val > 0:
                total += val
                count += 1
        informe.cumplimiento_global = round(total / count if count > 0 else 0, 2)

    def _guardar_version(self, informe: InformeGestionSGSST, motivo: str):
        version = InformeGestionVersion(
            informe_id=informe.id,
            empresa_id=informe.empresa_id,
            version_numero=informe.version,
            estado_anterior=informe.estado,
            estado_nuevo=informe.estado,
            datos_snapshot=informe.datos_consolidados,
            motivo_cambio=motivo,
            usuario_id=informe.usuario_id,
        )
        self.db.add(version)
        informe.version += 1

    def presentar_informe(self, informe_id: int, usuario_id: int) -> InformeGestionSGSST:
        informe = (
            self.db.query(InformeGestionSGSST)
            .filter(InformeGestionSGSST.id == informe_id)
            .first()
        )
        if not informe:
            raise ValueError("Informe no encontrado")
        if informe.estado not in ("BORRADOR", "DEVUELTO"):
            raise ValueError(f"No se puede presentar un informe en estado: {informe.estado}")
        if not informe.datos_consolidados:
            raise ValueError("Debe consolidar los datos antes de presentar")
        informe.estado = "PRESENTADO"
        informe.fecha_presentacion = datetime.utcnow()
        self.db.commit()
        self.db.refresh(informe)
        return informe

    def aprobar_informe(
        self,
        informe_id: int,
        usuario_id: int,
        resultado: str,
        observaciones: Optional[str] = None,
    ) -> InformeGestionSGSST:
        informe = (
            self.db.query(InformeGestionSGSST)
            .filter(InformeGestionSGSST.id == informe_id)
            .first()
        )
        if not informe:
            raise ValueError("Informe no encontrado")
        if informe.estado != "PRESENTADO":
            raise ValueError(f"No se puede aprobar un informe en estado: {informe.estado}")
        mapa = {
            "APROBADO": "APROBADO",
            "APROBADO_CON_OBSERVACIONES": "APROBADO_CON_OBSERVACIONES",
            "DEVUELTO": "DEVUELTO",
        }
        informe.estado = mapa.get(resultado, resultado)
        if resultado == "APROBADO":
            informe.fecha_aprobacion = datetime.utcnow()
            informe.aprobado_por_usuario_id = usuario_id
        elif resultado == "DEVUELTO":
            informe.fecha_cierre = None
        informe.resumen_ejecutivo = observaciones or informe.resumen_ejecutivo
        self.db.commit()
        self.db.refresh(informe)
        return informe

    def cerrar_informe(self, informe_id: int) -> InformeGestionSGSST:
        informe = (
            self.db.query(InformeGestionSGSST)
            .filter(InformeGestionSGSST.id == informe_id)
            .first()
        )
        if not informe:
            raise ValueError("Informe no encontrado")
        if informe.estado not in ("APROBADO", "APROBADO_CON_OBSERVACIONES"):
            raise ValueError(
                f"No se puede cerrar un informe en estado: {informe.estado}"
            )
        informe.estado = "CERRADO"
        informe.fecha_cierre = datetime.utcnow()
        self.db.commit()
        self.db.refresh(informe)
        return informe
