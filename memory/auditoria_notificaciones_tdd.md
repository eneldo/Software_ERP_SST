# Evidencia TDD — Notificaciones con tenant (H-024, bloque 4)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-024; auditoría Alertas (Sección 30).

## Recorrido
- Como RESPONSABLE_SST de la empresa 1, no puedo listar ni ver el dashboard de notificaciones de la empresa 2.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Lectura ajena → 403 | `python -m unittest discover -s tests -p "test_notificaciones_tenant.py" -v` | Seguridad | RED 1 FAIL + 1 ERROR; GREEN 2/2 |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 78 tests: 69 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/routers/notificaciones_sst.py`: `_empresa_id_autorizada` en listar + dashboard (filtro obligatorio para no-SUPER_ADMIN).
- `backend/tests/test_notificaciones_tenant.py`: nuevo, 2/2 GREEN.

## Brechas
- Faltan canales email/push, plantillas, escalamiento, 6 dominios de alerta y generación programada.
