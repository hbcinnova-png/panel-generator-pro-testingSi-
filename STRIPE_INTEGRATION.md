# Integración Stripe - Documentación Completa

## 🔧 Configuración

### 1. Variables de Entorno

Agregar a `.env`:

```bash
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxx
STRIPE_PUBLIC_KEY=pk_test_xxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxx
```

### 2. Instalar Dependencia

```bash
pip install stripe
```

### 3. Crear Productos en Stripe

```python
from services.stripe_service import StripeService

# Crear productos para cada plan
StripeService.create_stripe_product("basic")
StripeService.create_stripe_product("pro")
StripeService.create_stripe_product("enterprise")
```

---

## 📚 API Endpoints

### Planes

#### GET /api/v1/stripe/plans
Obtener planes disponibles

**Response:**
```json
{
  "plans": [
    {
      "key": "basic",
      "name": "Basic",
      "price": 29.99,
      "currency": "usd",
      "interval": "month",
      "features": ["5 paneles", "Instalación manual", "Email support"]
    },
    {
      "key": "pro",
      "name": "Pro",
      "price": 79.99,
      "currency": "usd",
      "interval": "month",
      "features": ["50 paneles", "Instalación automática", "Priority support", "Analytics"]
    },
    {
      "key": "enterprise",
      "name": "Enterprise",
      "price": 199.99,
      "currency": "usd",
      "interval": "month",
      "features": ["Paneles ilimitados", "Instalación automática", "24/7 support", "Custom integrations"]
    }
  ]
}
```

---

### Suscripciones

#### POST /api/v1/stripe/subscriptions
Crear suscripción

**Request:**
```json
{
  "plan": "pro"
}
```

**Response:**
```json
{
  "status": "success",
  "subscription": {
    "subscription_id": "sub_1234567890",
    "client_secret": "pi_secret_123",
    "status": "incomplete"
  }
}
```

#### GET /api/v1/stripe/subscriptions
Obtener suscripciones del usuario

**Response:**
```json
{
  "subscriptions": [
    {
      "id": "uuid",
      "plan": "pro",
      "status": "active",
      "price": 79.99,
      "currency": "usd",
      "started_at": "2024-01-01T00:00:00Z",
      "ends_at": "2024-02-01T00:00:00Z",
      "stripe_subscription_id": "sub_123"
    }
  ]
}
```

#### GET /api/v1/stripe/subscriptions/{subscription_id}/status
Obtener estado de suscripción

**Response:**
```json
{
  "subscription_id": "sub_123",
  "status": "active",
  "plan": "pro",
  "current_period_start": 1234567890,
  "current_period_end": 1234654290,
  "cancel_at_period_end": false
}
```

#### POST /api/v1/stripe/subscriptions/{subscription_id}/update
Actualizar plan

**Request:**
```json
{
  "new_plan": "enterprise"
}
```

**Response:**
```json
{
  "status": "success",
  "subscription": {
    "subscription_id": "sub_123",
    "plan": "enterprise",
    "status": "active"
  }
}
```

#### POST /api/v1/stripe/subscriptions/{subscription_id}/cancel
Cancelar suscripción

**Response:**
```json
{
  "status": "success",
  "subscription": {
    "subscription_id": "sub_123",
    "status": "canceled"
  }
}
```

---

### Pagos

#### POST /api/v1/stripe/payments/intent
Crear payment intent

**Request:**
```json
{
  "amount": 29.99,
  "description": "Panel Generator Pro - Basic Plan"
}
```

**Response:**
```json
{
  "status": "success",
  "payment": {
    "client_secret": "pi_secret_123",
    "payment_id": "pi_123"
  }
}
```

#### POST /api/v1/stripe/payments/{payment_id}/confirm
Confirmar pago

**Response:**
```json
{
  "status": "success",
  "payment": {
    "status": "succeeded",
    "payment_id": "pi_123",
    "amount": 29.99
  }
}
```

#### GET /api/v1/stripe/payments
Obtener pagos del usuario

**Response:**
```json
{
  "payments": [
    {
      "id": "uuid",
      "amount": 29.99,
      "currency": "usd",
      "status": "succeeded",
      "description": "Panel Generator Pro - Basic Plan",
      "created_at": "2024-01-01T00:00:00Z",
      "paid_at": "2024-01-01T00:05:00Z"
    }
  ]
}
```

---

### Facturas

#### POST /api/v1/stripe/invoices
Crear factura

**Request:**
```json
{
  "amount": 79.99,
  "description": "Panel Generator Pro - Pro Plan"
}
```

**Response:**
```json
{
  "status": "success",
  "invoice": {
    "invoice_id": "in_123",
    "invoice_number": "INV-001",
    "status": "open",
    "pdf_url": "https://invoice.stripe.com/..."
  }
}
```

#### GET /api/v1/stripe/invoices
Obtener facturas del usuario

**Response:**
```json
{
  "invoices": [
    {
      "id": "uuid",
      "invoice_number": "INV-001",
      "amount": 79.99,
      "status": "paid",
      "description": "Panel Generator Pro - Pro Plan",
      "created_at": "2024-01-01T00:00:00Z",
      "pdf_url": "https://invoice.stripe.com/..."
    }
  ]
}
```

---

### Webhooks

#### POST /api/v1/stripe/webhooks
Manejar webhooks de Stripe

Stripe enviará eventos automáticamente a este endpoint.

**Eventos soportados:**
- `payment_intent.succeeded` - Pago exitoso
- `payment_intent.payment_failed` - Pago fallido
- `customer.subscription.created` - Suscripción creada
- `customer.subscription.updated` - Suscripción actualizada
- `customer.subscription.deleted` - Suscripción cancelada
- `invoice.paid` - Factura pagada

---

## 💻 Ejemplos de Uso

### Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"
TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# Obtener planes
response = requests.get(f"{API_URL}/stripe/plans")
plans = response.json()

# Crear suscripción
data = {"plan": "pro"}
response = requests.post(
    f"{API_URL}/stripe/subscriptions",
    json=data,
    headers=headers
)
subscription = response.json()

# Crear payment intent
data = {
    "amount": 29.99,
    "description": "Panel Generator Pro"
}
response = requests.post(
    f"{API_URL}/stripe/payments/intent",
    json=data,
    headers=headers
)
payment = response.json()

# Confirmar pago
response = requests.post(
    f"{API_URL}/stripe/payments/{payment['payment']['payment_id']}/confirm",
    headers=headers
)
confirmed = response.json()

# Obtener suscripciones
response = requests.get(
    f"{API_URL}/stripe/subscriptions",
    headers=headers
)
subscriptions = response.json()

# Actualizar plan
data = {"new_plan": "enterprise"}
response = requests.post(
    f"{API_URL}/stripe/subscriptions/{subscription['subscription']['subscription_id']}/update",
    json=data,
    headers=headers
)
updated = response.json()

# Cancelar suscripción
response = requests.post(
    f"{API_URL}/stripe/subscriptions/{subscription['subscription']['subscription_id']}/cancel",
    headers=headers
)
canceled = response.json()
```

### JavaScript

```javascript
const API_URL = "http://localhost:8000/api/v1";
const TOKEN = "your_jwt_token";

const headers = {
    "Authorization": `Bearer ${TOKEN}`,
    "Content-Type": "application/json"
};

// Obtener planes
fetch(`${API_URL}/stripe/plans`)
    .then(r => r.json())
    .then(data => console.log(data));

// Crear suscripción
const subscriptionData = { plan: "pro" };
fetch(`${API_URL}/stripe/subscriptions`, {
    method: "POST",
    headers,
    body: JSON.stringify(subscriptionData)
})
    .then(r => r.json())
    .then(data => console.log(data));

// Crear payment intent
const paymentData = {
    amount: 29.99,
    description: "Panel Generator Pro"
};
fetch(`${API_URL}/stripe/payments/intent`, {
    method: "POST",
    headers,
    body: JSON.stringify(paymentData)
})
    .then(r => r.json())
    .then(data => {
        // Usar client_secret con Stripe.js para confirmar pago
        console.log(data);
    });

// Obtener suscripciones
fetch(`${API_URL}/stripe/subscriptions`, { headers })
    .then(r => r.json())
    .then(data => console.log(data));

// Obtener pagos
fetch(`${API_URL}/stripe/payments`, { headers })
    .then(r => r.json())
    .then(data => console.log(data));

// Obtener facturas
fetch(`${API_URL}/stripe/invoices`, { headers })
    .then(r => r.json())
    .then(data => console.log(data));
```

### cURL

```bash
# Obtener planes
curl http://localhost:8000/api/v1/stripe/plans

# Crear suscripción
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan": "pro"}' \
  http://localhost:8000/api/v1/stripe/subscriptions

# Crear payment intent
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 29.99,
    "description": "Panel Generator Pro"
  }' \
  http://localhost:8000/api/v1/stripe/payments/intent

# Obtener suscripciones
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/stripe/subscriptions

# Obtener pagos
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/stripe/payments

# Obtener facturas
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/stripe/invoices
```

---

## 🧪 Testing

Ejecutar tests:

```bash
pytest backend/tests/test_stripe_service.py -v
```

Tests incluidos:
- ✅ Crear producto
- ✅ Crear cliente
- ✅ Crear suscripción
- ✅ Crear payment intent
- ✅ Confirmar pago
- ✅ Cancelar suscripción
- ✅ Actualizar suscripción
- ✅ Obtener estado
- ✅ Crear factura
- ✅ Manejar webhooks
- ✅ Verificar firma

---

## 🔐 Seguridad

✅ Validación de firma de webhook
✅ Encriptación de datos sensibles
✅ Autenticación JWT requerida
✅ Rate limiting
✅ Logging de eventos
✅ Error handling completo

---

## 📊 Flujo de Pago

```
1. Usuario obtiene planes disponibles
   GET /stripe/plans

2. Usuario crea suscripción
   POST /stripe/subscriptions

3. Frontend obtiene client_secret
   Usa Stripe.js para confirmar pago

4. Stripe envía webhook
   POST /stripe/webhooks

5. Sistema actualiza estado
   Suscripción activada

6. Usuario puede ver suscripción
   GET /stripe/subscriptions
```

---

## 🐛 Troubleshooting

### Error: "Invalid API Key"
- Verificar STRIPE_SECRET_KEY en .env
- Asegurar que es una clave de prueba (sk_test_)

### Error: "Invalid Webhook Signature"
- Verificar STRIPE_WEBHOOK_SECRET en .env
- Asegurar que coincide con Stripe dashboard

### Error: "Customer not found"
- Verificar que el usuario existe en BD
- Crear cliente con StripeService.create_customer()

### Error: "Invalid Plan"
- Verificar que el plan existe en StripeService.PLANS
- Planes válidos: "basic", "pro", "enterprise"

---

## 📞 Soporte

Para más información:
- Documentación Stripe: https://stripe.com/docs
- API Reference: https://stripe.com/docs/api
- Testing: https://stripe.com/docs/testing

---

**Integración Stripe 100% Funcional** ✅
