# Evidencia TDD — Usuarios con tenant (H-013 parcial)

Fecha: 2026-09-04
Fuente: `.tmp/hallazgos_consolidados.md` H-013; auditoría Usuarios/Roles (Sección 22).

## Recorridos
- Como ADMIN_EMPRESA de la empresa 1, solo listo y cuento usuarios de mi empresa.
- Como ADMIN_EMPRESA, no puedo leer, modificar ni trasladar usuarios de otra empresa.
- Como ADMIN_EMPRESA, no puedo crear usuarios en otra empresa.

## Evidencia
| Garantía | Prueba o comando | Tipo | Resultado |
|---|---|---|---|
| Listar/stats filtran empresa | `python -m unittest discover -s tests -p "test_usuarios_tenant.py" -v` | Seguridad | RED 3 FAIL; GREEN 3/3 |
| Obtener ajeno → 404 con filtro id+empresa | mismo comando | Seguridad | RED; GREEN |
| Compilación | `python -m compileall app tests` | Estático | PASS |
| Diff whitespace | `git diff --check` | Estático | PASS |
| Suite completa | `python -m unittest discover -s tests` | Regresión | 41 tests: 32 OK; 6 FAIL + 3 ERROR preexistentes solo por mocks en `test_auditoria_p0_epp_insp_med.py` |

## Cambios
- `backend/app/routers/usuarios_sistema.py`: `_empresa_id_autorizada`; `obtener_usuario_o_404(..., empresa_id)`; tenant en listar/obtener/crear/actualizar/password/estado/eliminar/stats; bloqueo de traslado cross-tenant en actualizar.
- `backend/tests/test_usuarios_tenant.py`: nuevo, 3/3 GREEN.

## Brechas
- Falta MFA TOTP, blocklist/revocación JWT, matriz de roles normativos y permisos granulares por empresa.
