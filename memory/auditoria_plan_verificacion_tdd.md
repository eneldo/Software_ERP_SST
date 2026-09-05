# Evidencia TDD — Verificación explícita de planes (H-022, bloque 3)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-022; auditoría Planes de Mejoramiento (Sección 19).

## Recorrido
- Como RESPONSABLE_SST, verifico un plan con resultado APROBADO/RECHAZADO solo si tiene evidencia; el cierre exige verificación aprobada.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Verificar sin evidencia → 400 | `python -m unittest discover -s tests -p "test_plan_verificacion.py" -v` | Unitario | RED ImportError; GREEN 3/3 |
| Resultado inválido → 422 | mismo comando | Validación | GREEN |
| Cierre sin verificación → 400 | `python -m unittest discover -s tests -p "test_plan_cierre.py" -v` | Unitario | GREEN 3/3 |
| Migración local | `alembic upgrade head` → `a3b4c5d6e7f8 (head)` | Migración | PASS |
| Cadena limpia | `alembic upgrade head` en BD temporal | Integración | PASS 23 migraciones, BD eliminada |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 68 tests: 59 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/models/plan_mejoramiento.py`: `verificado_por` (FK usuarios), `fecha_verificacion`, `resultado_verificacion`; `foreign_keys` explícitos en `usuario`/`verificador` (sin esto, `AmbiguousForeignKeysError` rompe el mapper global y toda la suite).
- `backend/app/schemas/plan_mejoramiento_schema.py`: `RESULTADOS_VERIFICACION_PLAN`, `VerificarPlanRequest`, campos en Base/Update/Response.
- `backend/app/services/plan_mejoramiento_service.py`: `verificar_plan` + `cerrar_plan` exige verificación APROBADO.
- `backend/app/routers/plan_mejoramiento.py`: `POST /{plan_id}/verificar` con tenant; cerrar verifica tenant.
- `backend/alembic/versions/20260904_0013_add_plan_verificacion.py`: nueva (`a3b4c5d6e7f8`).
- `backend/tests/test_plan_verificacion.py`: nuevo, 3/3 GREEN.

## Aprendizaje
- Toda FK adicional a `usuarios` exige `foreign_keys` explícito en los `relationship`; de lo contrario SQLAlchemy falla al configurar mappers y rompe TODOS los tests del proceso.
