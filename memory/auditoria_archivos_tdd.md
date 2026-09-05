# Evidencia TDD — Archivos tenant (H-010 parcial)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-010; auditoría Documentos (DOC-001, DOC-045..047, DOC-062).

## Recorridos
- Como RESPONSABLE_SST de la empresa 1, no puedo subir ni listar archivos de la empresa 2.
- Como RESPONSABLE_SST, no puedo leer ni desactivar un archivo de otra empresa (404 con filtro id+empresa).

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Subir/listar otra empresa → 403 | `python -m unittest discover -s tests -p "test_archivos_tenant.py" -v` | Seguridad | RED 4 FAIL; GREEN 4/4 |
| Leer/baja filtran id+empresa → 404 | mismo comando (assert 2 condiciones) | Seguridad | RED; GREEN |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 37 tests: 28 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/routers/archivos_sst.py`: `_empresa_id_autorizada`; tenant en subir/listar/obtener/eliminar; `subir_archivo_sst` exige roles SST/AUDITOR (antes `get_current_user`).
- `backend/tests/test_archivos_tenant.py`: nuevo, 4/4 GREEN.

## Brechas
- Falta `hash_sha256` en `ArchivoSST`, endpoint `GET /archivos-sst/{id}/descargar` con auditoría, y tenant en `archivos_protegidos.py` por path.
