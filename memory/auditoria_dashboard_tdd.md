# Evidencia TDD — H-012 Dashboard tenant + KPIs reales

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-012; `PROMPT_MAESTRO_AUDITORIA_SG_SST.md` §21/§23.

## Recorridos
- Como ADMIN_EMPRESA sin empresa asignada, no puedo ver el dashboard.
- Como RESPONSABLE_SST de la empresa 1, no puedo ver el dashboard de la empresa 2.
- Como RESPONSABLE_SST, veo KPIs CAP/INS/ACC/ACP con conteos reales de mi empresa y enlace al registro fuente.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Sin empresa → 403 | `python -m unittest discover -s tests -p "test_dashboard_tenant.py" -v` | Seguridad | RED sin excepción; GREEN 403 |
| Otra empresa → 403 | mismo comando | Seguridad | RED sin excepción; GREEN 403 |
| KPIs = conteos reales | mismo comando (`CAP=3, INS=5, ACC=2, ACP=7`) | Unitario | RED `0 != 3`; GREEN 3/3 |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |

## Cambios
- `backend/app/routers/dashboard_ejecutivo.py`: `_empresa_id_autorizada`, tenant obligatorio no-SUPER_ADMIN, conteos reales `CapacitacionSST`/`InspeccionSST`/`IncidenteAccidenteSST(tipo ACCIDENTE)`/`PlanMejoramientoSST`, `url_detalle` en 4 KPIs, `actividades_recientes` filtradas por tenant.
- `backend/app/schemas/dashboard_ejecutivo_schema.py`: `KpiCard.url_detalle: Optional[str]`.
- `backend/tests/test_dashboard_tenant.py`: nuevo, 3/3 GREEN.

## Brechas
- Cumplimiento SG-SST/Res.0312 sigue con fórmula provisional (`*0.65`); requiere evaluación inicial real.
- Faltan 8/12 indicadores §21 y exportaciones; `actividades_recientes` sigue sobre auditoría HTTP genérica.
