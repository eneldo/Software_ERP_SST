# Evidencia TDD — Exportación auditoría con tenant (H-008 parcial)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-008; auditoría Estándares (EM-004).

## Recorrido
- Como AUDITOR de la empresa 1, no puedo exportar el PDF de una auditoría de otra empresa (404 sin revelar existencia, sin generar el PDF).

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Export ajena → 404 y no genera PDF | `python -m unittest discover -s tests -p "test_auditoria_export_tenant.py" -v` | Seguridad | RED sin excepción; GREEN 1/1 + `generar_pdf_auditoria` no llamado + 2 condiciones en filtro |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 38 tests: 29 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/routers/auditoria_pdf.py`: `_empresa_id_autorizada` + verificación previa `(id, empresa_id)` antes de `generar_pdf_auditoria`.
- `backend/tests/test_auditoria_export_tenant.py`: nuevo, 1/1 GREEN.

## Brechas
- Resto de exportaciones (`exportaciones_sst.py`, inspecciones, medidas) pendientes del mismo patrón.
