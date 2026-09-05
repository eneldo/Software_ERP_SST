# Evidencia TDD — Historia clínica con permiso (H-011 parcial, bloque 2)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-011; auditoría Resolución 1843 (Sección 5).

## Recorridos
- Como RESPONSABLE_SST sin permiso de historia clínica, no puedo ver el reporte de restricciones, la ficha individual ni los adjuntos clínicos.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Clínico sin permiso → 403 | `python -m unittest discover -s tests -p "test_historia_clinica.py" -v` | Seguridad | RED 3 FAIL + 1 ERROR; GREEN 4/4 |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 51 tests: 42 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/routers/examenes_medicos.py`: `_exigir_historia_clinica` en reporte de restricciones, ficha individual y evidencias (listar/subir/eliminar); `_puede_ver_concepto_medico` (médico, historia o `CONCEPTO_MEDICO_VER`) aplicado en `_sanitizar_respuesta_medica` (concepto se redacta sin permiso; historia subsume concepto); fix bug tenant en crear (usaba `empleado_id` como `empresa_id`).
- `backend/tests/test_historia_clinica.py`: nuevo, 4/4 GREEN.
- `backend/tests/test_concepto_medico.py`: nuevo, 3/3 GREEN (sin permisos oculta concepto+clínica; historia subsume concepto; con ambos muestra todo).

## Brechas
- Falta módulo psicosocial y separación física historia clínica vs concepto médico en el modelo.

## Ampliación — analítica por empleado
- `dashboard_examenes_medicos` con `empleado_id` exige `_puede_ver_concepto_medico` (403 sin permiso).
- `backend/tests/test_dashboard_concepto.py`: RED 1 FAIL → GREEN 2/2 OK.
- Suite: 59 tests, 50 OK; mismos 6 FAIL + 3 ERROR preexistentes por mocks.

## Ampliación — redacción en exportaciones
- `_crear_excel_examenes(..., mostrar_concepto, mostrar_historia)` y `_crear_pdf_tabla(..., mostrar_concepto)` redactan concepto e historia según permisos; endpoints general/vencimientos pasan los flags.
- `backend/tests/test_export_redaction.py`: RED 3 ERROR → GREEN 3/3 OK.
- Suite: 57 tests, 48 OK; mismos 6 FAIL + 3 ERROR preexistentes por mocks.
