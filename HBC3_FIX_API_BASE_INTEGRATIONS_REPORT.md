# HBC3 Fix API Base + Integrations

Estado: APTO PARA AUDITORIA / NO VALIDADO EN PRODUCCION.

## Objetivo

Corregir dos bloqueos detectados en HBC3:

1. El frontend debe resolver correctamente el backend en Codespaces/local sin hardcodear una URL temporal.
2. El payload de integraciones no debe enviar booleanos cuando el backend declara `integrations` como `Dict[str, Dict[str, str]]`.

## Cambios realizados

- Actualizado `frontend/app.js`.
- `resolveApiOrigin()` ahora soporta:
  - `localStorage.API_BASE`,
  - `localStorage.api_url`,
  - Codespaces `-3000` → `-8000`,
  - localhost `:8000`,
  - fallback mismo origen.
- `API_BASE` se normaliza siempre a `/api/v1`.
- No se envía `Authorization: Bearer null`.
- `buildIntegrationsPayload()` ahora genera valores string:
  - `enabled: "true"`,
  - `phone: "..."`,
  - `address: "..."`.
- Si no hay token o backend disponible, la app genera pantalla local funcional.

## Seguridad

- No se añadió PAT.
- No se añadieron tokens.
- No se añadieron contraseñas.
- No se tocó `.env` real.
- No se tocó producción.
- No se hizo merge.
- No se tocó `main` directo.

## Workflows

Se auditó que `.github/workflows/main.yml` está vacío en `main` y por eso GitHub informa `No jobs were run`.
Intenté preparar el cambio de workflow en rama, pero la acción de escritura sobre `.github/workflows/` fue bloqueada por controles de seguridad del conector.

Estado workflow: BLOQUEO_REAL - escritura en `.github/workflows/` bloqueada por seguridad del conector.

## Validación pendiente

No tengo terminal real de Codespaces ni acceso al panel Render desde este conector. Pendiente validar en entorno real:

```bash
curl http://localhost:8000/health
curl https://turbo-eureka-xr56645wq465hp4x7-8000.app.github.dev/health
```

Si el backend público devuelve 404, el problema restante no está en `frontend/app.js`: el backend no está levantado o el puerto 8000 no está público en Codespaces.

## Estado final

APTO_TESTING con PR para frontend.
BLOQUEO_REAL para workflows y validación Codespaces externa.
NO_VALIDADO_PRODUCCION.
