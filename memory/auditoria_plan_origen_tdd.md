# Evidencia TDD — Origen de hallazgo en planes (H-023, bloque 3)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-023; auditoría Planes de Mejoramiento (Sección 19).

## Recorrido
- Como RESPONSABLE_SST, registro el origen del hallazgo (auditoría, inspección, incidente, etc.) al crear un plan; el sistema rechaza orígenes inventados.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Modelo/crear aceptan origen | `python -m unittest discover -s tests -p "test_plan_origen.py" -v` | Unitario | RED TypeError + sin ValidationError; GREEN 3/3 |
| Origen inválido → 422 | mismo comando | Validación | RED; GREEN |
| Migración local | `alembic upgrade head` → `f2a3b4c5d6e7 (head)` | Migración | PASS (tras transferir propiedad de `planes_mejoramiento_sst` a `sst_user`) |
| Cadena limpia | `alembic upgrade head` en BD temporal | Integración | PASS 22 migraciones, BD eliminada |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 64 tests: 55 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/models/plan_mejoramiento.py`: `origen_hallazgo` (String 40, default OTRO) + `origen_id` nullable.
- `backend/app/schemas/plan_mejoramiento_schema.py`: `ORIGENES_HALLAZGO_PLAN` (9 valores) + campos en Base/Update + validadores.
- `backend/app/services/plan_mejoramiento_service.py`: `crear_plan_manual` persiste origen.
- `backend/alembic/versions/20260904_0012_add_plan_origen.py`: nueva (`f2a3b4c5d6e7`).
- `backend/tests/test_plan_origen.py`: nuevo, 3/3 GREEN.

## Brechas
- Falta verificación explícita (verificado_por/fecha/resultado) y `responsable_id` como FK.
