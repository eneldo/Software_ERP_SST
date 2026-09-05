# Evidencia TDD — Plan Anual tenant (H-015 parcial)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-015; auditoría Plan Anual (PA H-001..003, H-022).

## Recorridos
- Como RESPONSABLE_SST de la empresa 1, no puedo listar ni resumir el plan de la empresa 2.
- Como RESPONSABLE_SST, no puedo leer una actividad de otra empresa (404 con filtro id+empresa).
- Como RESPONSABLE_SST, no puedo crear actividades en otra empresa.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Listar/resumen/crear otra empresa → 403 | `python -m unittest discover -s tests -p "test_plan_anual_tenant.py" -v` | Seguridad | RED 4 FAIL; GREEN 4/4 |
| Obtener filtra id+empresa → 404 | mismo comando (assert 2 condiciones) | Seguridad | RED; GREEN |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 33 tests: 24 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/routers/plan_anual.py`: `_empresa_id_autorizada`; tenant en crear, cargar-base, listar, resumen, obtener, actualizar, finalizar, evidencia, eliminar; `subir_evidencia_plan_anual` exige `ROLES_ESCRITURA` (antes `get_current_user`).
- `backend/tests/test_plan_anual_tenant.py`: nuevo, 4/4 GREEN.

## Brechas
- Falta `/dashboard` con KPIs reales, validator `fecha_inicio<=fecha_fin`, obligatoriedad Decreto 1072, evidencias versionadas.
