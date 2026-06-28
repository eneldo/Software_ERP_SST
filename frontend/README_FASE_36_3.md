# FASE 36.3 — Limpieza Frontend

## Objetivo

Endurecer y limpiar el frontend React/Vite del ERP SST sin cambiar la lógica de negocio.

## Cambios aplicados

- Se eliminan del entregable limpio carpetas generadas o pesadas: `node_modules/`, `dist/`.
- Se agrega `.gitignore` para evitar subir dependencias, builds y variables sensibles.
- Se agrega `.dockerignore` para builds reproducibles y livianos.
- Se agrega `.env.example` con `VITE_API_URL`.
- Se normaliza `src/api/axios.js` para usar `VITE_API_URL` o `VITE_API_BASE_URL`.
- Se corrigen rutas/constantes con URL local hardcodeada para permitir despliegue en producción.
- Se protege la ruta `/documental/firma-digital` con `RequireAuth` y `AdminLayout`.
- Se elimina import no utilizado en `App.jsx`.
- Se limpia `package.json`: `@vitejs/plugin-react` queda solo como dependencia de desarrollo.
- Se agregan scripts `clean`, `build:clean` y `check`.

## Instalación recomendada

```bash
cd frontend
copy .env.example .env
npm install
npm run build
```

En Linux:

```bash
cd frontend
cp .env.example .env
npm install
npm run build
```

## Producción

Editar `.env`:

```env
VITE_API_URL=https://api.tu-dominio.com
```

Luego:

```bash
npm run build:clean
```

## Validaciones posteriores

- Login.
- Dashboard.
- Rutas privadas.
- Exportaciones PDF/Excel.
- Visualización de evidencias.
- Portal público `/reporte-sst`.
- Validación documental pública `/verificar-documento`.
