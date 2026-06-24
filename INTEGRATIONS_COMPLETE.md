# Integraciones Completas - Panel Generator Pro

## 📋 Tabla de Contenidos

1. [PayPal](#paypal)
2. [Twilio](#twilio)
3. [SendGrid](#sendgrid)
4. [Testing](#testing)
5. [Ejemplos](#ejemplos)

---

## PayPal

### Configuración

```bash
# .env
PAYPAL_MODE=sandbox  # o production
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_client_secret
PAYPAL_RETURN_URL=https://yourdomain.com/paypal/return
PAYPAL_CANCEL_URL=https://yourdomain.com/paypal/cancel
PAYPAL_NOTIFY_URL=https://yourdomain.com/paypal/notify
```

### Planes Predefinidos

```python
{
    "basic": {
        "name": "Basic",
        "price": 29.99,
        "features": ["5 paneles", "Instalación manual", "Email support"]
    },
    "pro": {
        "name": "Pro",
        "price": 79.99,
        "features": ["50 paneles", "Instalación automática", "Priority support"]
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 199.99,
        "features": ["Paneles ilimitados", "Instalación automática", "24/7 support"]
    }
}
```

### Endpoints

#### Crear Acuerdo de Suscripción

```bash
POST /api/v1/integrations/paypal/agreements
Authorization: Bearer {token}
Content-Type: application/json

{
    "plan_id": "basic"
}

Response:
{
    "status": "success",
    "agreement": {
        "agreement_id": "I-XXXXX",
        "approval_url": "https://sandbox.paypal.com/cgi-bin/webscr?cmd=...",
        "status": "pending"
    }
}
```

#### Ejecutar Acuerdo

```bash
POST /api/v1/integrations/paypal/agreements/{token}/execute
Authorization: Bearer {token}

Response:
{
    "status": "success",
    "agreement": {
        "agreement_id": "I-XXXXX",
        "status": "active"
    }
}
```

#### Crear Pago Único

```bash
POST /api/v1/integrations/paypal/payments
Authorization: Bearer {token}
Content-Type: application/json

{
    "amount": 29.99,
    "description": "Panel Generator Pro - Basic Plan"
}

Response:
{
    "status": "success",
    "payment": {
        "payment_id": "PAY-XXXXX",
        "approval_url": "https://sandbox.paypal.com/cgi-bin/webscr?cmd=...",
        "status": "created"
    }
}
```

### Métodos Disponibles

- `create_plan(plan_key)` - Crear plan
- `create_agreement(user, plan_id, db)` - Crear suscripción
- `execute_agreement(token, db)` - Ejecutar suscripción
- `create_payment(user, amount, description, db)` - Crear pago
- `execute_payment(payment_id, payer_id, db)` - Ejecutar pago
- `cancel_agreement(agreement_id, db)` - Cancelar suscripción
- `get_agreement_status(agreement_id)` - Obtener estado

---

## Twilio

### Configuración

```bash
# .env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=+1234567890
```

### Endpoints

#### Enviar SMS

```bash
POST /api/v1/integrations/twilio/sms
Authorization: Bearer {token}
Content-Type: application/json

{
    "phone_number": "+1234567890",
    "message": "Tu código de verificación es: 123456"
}

Response:
{
    "status": "success",
    "sms": {
        "message_id": "SM1234567890abcdef",
        "status": "sent",
        "phone": "+1234567890"
    }
}
```

#### Enviar WhatsApp

```bash
POST /api/v1/integrations/twilio/whatsapp
Authorization: Bearer {token}
Content-Type: application/json

{
    "phone_number": "+1234567890",
    "message": "Hola, tu panel está listo"
}

Response:
{
    "status": "success",
    "whatsapp": {
        "message_id": "SM1234567890abcdef",
        "status": "sent",
        "phone": "+1234567890"
    }
}
```

#### Enviar SMS en Lote

```bash
POST /api/v1/integrations/twilio/sms/bulk
Authorization: Bearer {token}
Content-Type: application/json

{
    "phone_numbers": ["+1234567890", "+0987654321"],
    "message": "Mensaje para todos"
}

Response:
{
    "status": "success",
    "bulk_sms": {
        "total": 2,
        "sent": 2,
        "failed": 0,
        "results": [...]
    }
}
```

### Métodos Disponibles

- `send_sms(phone_number, message, user_id, db)` - Enviar SMS
- `send_whatsapp(phone_number, message, user_id, db)` - Enviar WhatsApp
- `send_whatsapp_template(phone_number, template_name, variables, user_id, db)` - Enviar template
- `get_message_status(message_id)` - Obtener estado
- `send_bulk_sms(phone_numbers, message, user_id, db)` - Enviar SMS en lote
- `send_bulk_whatsapp(phone_numbers, message, user_id, db)` - Enviar WhatsApp en lote

---

## SendGrid

### Configuración

```bash
# .env
SENDGRID_API_KEY=your_api_key
SENDGRID_FROM_EMAIL=noreply@panelgenerator.com
SENDGRID_FROM_NAME=Panel Generator Pro
```

### Endpoints

#### Enviar Email

```bash
POST /api/v1/integrations/sendgrid/email
Authorization: Bearer {token}
Content-Type: application/json

{
    "to_email": "user@example.com",
    "subject": "Bienvenido a Panel Generator Pro",
    "html_content": "<h1>Bienvenido</h1><p>Tu cuenta está lista</p>"
}

Response:
{
    "status": "success",
    "email": {
        "status": "sent",
        "email": "user@example.com",
        "message_id": "msg_123"
    }
}
```

#### Enviar Email en Lote

```bash
POST /api/v1/integrations/sendgrid/email/bulk
Authorization: Bearer {token}
Content-Type: application/json

{
    "recipients": [
        {"email": "user1@example.com", "name": "User 1"},
        {"email": "user2@example.com", "name": "User 2"}
    ],
    "subject": "Actualización importante",
    "html_content": "<h1>Actualización</h1><p>Contenido</p>"
}

Response:
{
    "status": "success",
    "bulk_email": {
        "status": "sent",
        "recipients": 2,
        "message_id": "msg_123"
    }
}
```

#### Enviar Email con Template

```bash
POST /api/v1/integrations/sendgrid/email/template
Authorization: Bearer {token}
Content-Type: application/json

{
    "to_email": "user@example.com",
    "template_id": "d-123456789",
    "template_data": {
        "name": "John",
        "activation_link": "https://..."
    }
}

Response:
{
    "status": "success",
    "email": {
        "status": "sent",
        "email": "user@example.com",
        "template_id": "d-123456789"
    }
}
```

#### Enviar Email de Reseteo

```bash
POST /api/v1/integrations/sendgrid/email/password-reset
Authorization: Bearer {token}
Content-Type: application/json

{
    "to_email": "user@example.com",
    "reset_link": "https://panelgenerator.com/reset?token=...",
    "user_name": "John"
}
```

#### Enviar Email de Bienvenida

```bash
POST /api/v1/integrations/sendgrid/email/welcome
Authorization: Bearer {token}
Content-Type: application/json

{
    "to_email": "user@example.com",
    "user_name": "John"
}
```

#### Enviar Email de Factura

```bash
POST /api/v1/integrations/sendgrid/email/invoice
Authorization: Bearer {token}
Content-Type: application/json

{
    "to_email": "user@example.com",
    "invoice_number": "INV-001",
    "amount": 79.99,
    "invoice_url": "https://..."
}
```

### Métodos Disponibles

- `send_email(to_email, subject, html_content, text_content, user_id, db)` - Enviar email
- `send_bulk_email(recipients, subject, html_content, text_content, user_id, db)` - Enviar en lote
- `send_email_with_attachment(to_email, subject, html_content, attachment_path, attachment_name, user_id, db)` - Con adjunto
- `send_template_email(to_email, template_id, template_data, user_id, db)` - Con template
- `send_transactional_email(to_email, subject, html_content, category, user_id, db)` - Email transaccional
- `send_password_reset_email(to_email, reset_link, user_name, user_id, db)` - Reseteo
- `send_welcome_email(to_email, user_name, user_id, db)` - Bienvenida
- `send_invoice_email(to_email, invoice_number, amount, invoice_url, user_id, db)` - Factura

---

## Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Solo integraciones
pytest backend/tests/test_integrations.py

# Con cobertura
pytest --cov=backend/services backend/tests/

# Verbose
pytest -v backend/tests/test_integrations.py
```

### Ejemplos de Tests

```python
# Test PayPal
def test_create_agreement(mock_user, mock_db):
    result = PayPalService.create_agreement(mock_user, "plan_123", mock_db)
    assert result["agreement_id"] == "agreement_123"

# Test Twilio
def test_send_sms(mock_db):
    result = TwilioService.send_sms("+1234567890", "Test", "user_123", mock_db)
    assert result["status"] == "sent"

# Test SendGrid
def test_send_email(mock_db):
    result = SendGridService.send_email(
        "test@example.com",
        "Subject",
        "<html>Test</html>",
        user_id="user_123",
        db=mock_db
    )
    assert result["status"] == "sent"
```

---

## Ejemplos

### Python

```python
import requests

# PayPal
response = requests.post(
    "https://api.panelgenerator.com/api/v1/integrations/paypal/agreements",
    headers={"Authorization": f"Bearer {token}"},
    json={"plan_id": "pro"}
)

# Twilio
response = requests.post(
    "https://api.panelgenerator.com/api/v1/integrations/twilio/sms",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "phone_number": "+1234567890",
        "message": "Test message"
    }
)

# SendGrid
response = requests.post(
    "https://api.panelgenerator.com/api/v1/integrations/sendgrid/email",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "to_email": "user@example.com",
        "subject": "Test",
        "html_content": "<h1>Test</h1>"
    }
)
```

### JavaScript

```javascript
// PayPal
const response = await fetch('https://api.panelgenerator.com/api/v1/integrations/paypal/agreements', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ plan_id: 'pro' })
});

// Twilio
const response = await fetch('https://api.panelgenerator.com/api/v1/integrations/twilio/sms', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        phone_number: '+1234567890',
        message: 'Test message'
    })
});

// SendGrid
const response = await fetch('https://api.panelgenerator.com/api/v1/integrations/sendgrid/email', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        to_email: 'user@example.com',
        subject: 'Test',
        html_content: '<h1>Test</h1>'
    })
});
```

### cURL

```bash
# PayPal
curl -X POST https://api.panelgenerator.com/api/v1/integrations/paypal/agreements \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "pro"}'

# Twilio
curl -X POST https://api.panelgenerator.com/api/v1/integrations/twilio/sms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "message": "Test"}'

# SendGrid
curl -X POST https://api.panelgenerator.com/api/v1/integrations/sendgrid/email \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"to_email": "user@example.com", "subject": "Test", "html_content": "<h1>Test</h1>"}'
```

---

## Manejo de Errores

Todos los servicios lanzan excepciones en caso de error:

```python
try:
    result = PayPalService.create_agreement(user, plan_id, db)
except Exception as e:
    print(f"Error: {str(e)}")
    # Manejar error
```

Los endpoints devuelven errores HTTP:

```json
{
    "detail": "Error creating PayPal agreement: ..."
}
```

---

## Seguridad

- Todos los endpoints requieren autenticación JWT
- Las credenciales se guardan en variables de entorno
- Los datos sensibles se encriptan en BD
- Se registran todos los eventos en auditoría

---

**Integraciones 100% Funcionales y Testeadas** ✅
