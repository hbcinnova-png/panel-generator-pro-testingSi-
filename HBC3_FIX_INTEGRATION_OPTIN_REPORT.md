# HBC3 Fix Integration Opt-in

Estado: APTO PARA AUDITORIA / NO VALIDADO EN PRODUCCION.

## Motivo

Codex detectó que `buildIntegrationsPayload()` añadía `integrations.email` siempre que existía `formData.email`.

Como `submitForm()` exige `formData.email`, eso hacía que la integración Email se enviara incluso cuando el usuario no marcaba el checkbox Email.

## Corrección

`buildIntegrationsPayload()` ahora crea un `Set` con las integraciones seleccionadas y solo añade detalles cuando la integración está marcada:

- `email` solo se envía si `selected.has('email')`.
- `whatsapp` solo se envía si `selected.has('whatsapp')`.
- Los valores siguen siendo strings compatibles con `Dict[str, Dict[str, str]]`.

## Seguridad

- No PAT.
- No tokens.
- No contraseñas.
- No `.env` real.
- No producción.
- No merge automático.

## Pendiente

Validar en Codespaces/runner real:

1. Email checkbox sin marcar -> no debe aparecer `integrations.email`.
2. Email checkbox marcado -> debe aparecer `integrations.email` con `enabled: "true"` y `address`.
3. Backend activo -> POST `/api/v1/panels` sin 422.
