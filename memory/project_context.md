# Contexto del Proyecto

## Objetivo
ERP SST PRO: Sistema de Gestión de Seguridad y Salud en el Trabajo para empresas colombianas. Implementa el ciclo PDCA (Planear/Hacer/Verificar/Actuar) según normativa colombiana (GTC 45, Decreto 1072 de 2015).

## Estado actual
Producción activa - v2.7.9-hardening-36.14 (backend) / v1.6.1-hardening.36.7 (frontend)

## Arquitectura
- **Tipo:** Multi-tenant ERP con ciclos PDCA
- **Patrón:** Capas (models → schemas → services → routers)
- **Tenant:**empresa_id como FK en todos los modelos SST con CASCADE delete
- **Soft deletes:** activo = Column(Boolean, default=True)
- **Timestamps:** fecha_creacion y fecha_actualizacion en todos los modelos

## Backend
- **Framework:** FastAPI v0.136.3 (Python 3.12)
- **ORM:** SQLAlchemy 2.0.50
- **Migraciones:** Alembic v1.17.2
- **Validación:** Pydantic v2.13.4
- **Auth:** JWT (python-jose) + bcrypt (passlib)
- **PDF:** ReportLab
- **Excel:** openpyxl
- **QR:** qrcode
- **Rate limiting:** Redis-backed o in-memory

## Frontend
- **Framework:** React 18.3.1 + Vite 5.4.1
- **Routing:** react-router-dom v7.16.0
- **HTTP:** Axios v1.16.1
- **Charts:** Recharts v3.8.1
- **Icons:** Lucide React v1.17.0
- **Build:** Node 20 → Nginx 1.27-alpine

## Base de datos
- **PostgreSQL 17** (Alpine)
- **Redis 8** (Alpine) - rate limiting, persistencia
- **55+ modelos SQLAlchemy** (epp_catalogo: 17 cols, plan_anual_sst: 29 cols)
- **5 migraciones Alembic**

## Infraestructura
- **Docker Compose:** 3 variantes (dev, prod, Coolify)
- **Reverse proxy:** Caddy (VPS) o Nginx (container)
- **Red:** puente aislado erp_sst_net
- **Health checks:** todos los servicios

## Servicios externos
- JWT auth (tokens de acceso + refresco)
- Redis para rate limiting
- Almacenamiento local de archivos (12 subdirectorios)

## Seguridad
- **Hardening validator:** config.py verifica reglas estrictas en producción
- **Dual token:** Access (15 min) + Refresh (7 días, cookie-based)
- **Rate limiting:** General (120/min), login (5/min), reportes públicos (10/hora), uploads (20/5min)
- **Headers:** HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- **Audit middleware:** logging de requests
- **RBAC:** 17 roles con matrices de acceso granulares

## Funcionalidades terminadas
- Autenticación JWT completa
- Gestión de usuarios y roles (17 roles)
- Organización (empresas, sedes, áreas, cargos, empleados)
- Módulo Planear: Políticas, objetivos, evaluación inicial, matriz legal, matriz peligros, matriz IPER (GTC 45) — cálculo automático de NP/NR/nivel_riesgo, KPIs, filtros, tabla, dashboard, recálculo masivo, **plan anual (Decreto 1072/2015: vigencia, alcance, objetivo general, firmas)**, planes de mejoramiento
- Módulo Hacer: Capacitaciones, exámenes médicos, **EPP (catálogo + ficha técnica PDF + entregas + firmas digitales)**, inspecciones, CAPA, incidentes (5-Whys, árbol de causas)
- Módulo Verificar: Auditorías, revisión dirección, indicadores, notificaciones, reportes anónimos
- Módulo Actuar: Medidas correctivas, BI, exportaciones, alertas, evidencias inteligentes
- Módulo Documental: Biblioteca, centro control, firmas digitales, versionado
- Portal empleado y reporte anónimo público
- Generación de PDFs y exportación Excel
- Sistema de uploads con validación de tipos
- **Motor de compresión de evidencias:** Imágenes→WEBP (max 1600px, quality 80→50, fallback resize), PDFs→pikepdf (compress_streams, linearize)
- Rate limiting y headers de seguridad

## Funcionalidades pendientes
- Completar análisis de todas las funcionalidades
- Optimizaciones de rendimiento
- Tests unitarios y de integración

## Riesgos conocidos
- Mantener sincronización entre modelos backend y migraciones Alembic
- **`create_all()` no agrega columnas a tablas existentes** — requiere ALTER TABLE manual o Alembic
- Gestión de archivos grandes en uploads
- Rate limiting en producción requiere Redis
- Diferentes módulos usan estructuras de directorios distintas para variantes (sufijo vs subdirectorios)
- Frontend debe usar siempre `resolveFileUrl()` para acceder a archivos, nunca concatenación directa

## Módulos principales
1. **Seguridad y Administración** - Auth, usuarios, roles, permisos, auditoría
2. **Organización** - Empresas, sedes, áreas, cargos, empleados
3. **PLANEAR** - Políticas, objetivos, evaluación, matrices, planes
4. **HACER** - Capacitaciones, exámenes, EPP, inspecciones, CAPA, incidentes
5. **VERIFICAR** - Auditorías, revisión dirección, indicadores, reportes
6. **ACTUAR** - Medidas correctivas, BI, exportaciones
7. **Documental** - Biblioteca, control, firmas, versionado
8. **Portal** - Empleado, reporte anónimo, verificación documentos
9. **BI y Reportes** - Dashboards, indicadores, exportaciones

## Convenciones notables
- **Naming en español:** Todos los términos de dominio en español (contexto colombiano)
- **Versionado por fases:** Cambios rastreados por números de fase (FASE 1.1.8, FASE 2.5.3, FASE 36.x)
- **Importaciones explícitas en main.py:** Todos los modelos se importan al iniciar la app
- **Relation guard:** Router y modelo dedicados para prevenir eliminación de registros con dependencias
- **PDF como capa de servicio:** Múltiples módulos de servicios PDF para diferentes tipos de reportes

## Ubicación de archivos clave
| Componente | Ruta |
|---|---|
| Punto entrada backend | `backend/app/main.py` |
| Config backend | `backend/app/config.py` |
| Base de datos | `backend/app/database.py` |
| Auth | `backend/app/auth/` |
| Modelos (50) | `backend/app/models/` |
| Schemas (62) | `backend/app/schemas/` |
| Servicios (34) | `backend/app/services/` |
| Routers (71) | `backend/app/routers/` |
| Migraciones | `backend/alembic/versions/` |
| Punto entrada frontend | `frontend/src/main.jsx` |
| Routing frontend | `frontend/src/App.jsx` |
| Páginas (40+) | `frontend/src/pages/` |
| API modules (40) | `frontend/src/api/` |
| Docker producción | `docker-compose.prod.yml` |
| Scripts backup | `scripts/backup_postgres.sh`, `scripts/restore_postgres.sh` |
| Manual instalación | `MANUAL_INSTALACION_Y_DESPLIEGUE.md` |
