# Preferencias del Proyecto

Registrar preferencias técnicas y operativas estables.

## Idioma
- Comunicación y documentación en español (contexto colombiano)
- Nombres de dominio, variables y comentarios en español

## Documentación
- Guías operativas en PDF con scripts de acompañamiento (ZIP distribuible)
- Usar fpdf2 para generación de PDFs técnicos (sin dependencias pesadas)
- Incluir siempre instrucciones paso a paso con comandos exactos

## Despliegue
- Docker Compose para producción (docker-compose.prod.yml + docker-compose.proxy.yml)
- Coolify/Traefik para proxy reverso y HTTPS automático
- Oracle Cloud Always Free para hosting
- Backups offsite con Restic a OCI Object Storage

## Seguridad
- Contraseñas sin caracteres especiales en Redis (evitar errores de URL parsing)
- Credenciales en .env con chmod 600
- Nunca compartir contraseñas en chat (compromete seguridad)
- Rotar credenciales periódicamente

## Git
- Branch main para código estable
- Commits descriptivos en español
- No commitear secretos o credenciales
