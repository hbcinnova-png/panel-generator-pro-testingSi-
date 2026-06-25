# HBC3 Fix Auth Screen

Estado: APTO PARA AUDITORIA / NO VALIDADO EN PRODUCCION.

## Cambios

- Reparado `frontend/app.js`.
- Evita enviar `Authorization: Bearer null`.
- Añade flujo de login real contra `/api/v1/auth/login`.
- Si no hay token o backend falla, genera la pantalla en modo local sin romper la app.
- Convierte el payload del frontend a formato backend `snake_case`.
- Mantiene vista previa en tiempo real.
- Añade apertura de pantalla generada en nueva ventana como HTML local.

## Seguridad HBC3

- No toca `main` directamente.
- No añade claves.
- No añade PAT.
- No añade `.pem`.
- No merge automático.
- No producción.

## Pendiente antes de producción

- Validar en navegador real.
- Validar login con backend activo.
- Validar creación de panel con base de datos operativa.
- Revisar backend `api.py` en una PR separada para limpiar router duplicado y dependencias.
