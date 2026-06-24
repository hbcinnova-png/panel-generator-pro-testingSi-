# Panel Generator Pro - API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require JWT token in header:
```
Authorization: Bearer <token>
```

---

## Authentication Endpoints

### POST /auth/register
Register new user

**Request:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### POST /auth/login
Login user

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### POST /auth/2fa/setup
Setup 2FA

**Response:**
```json
{
  "secret": "JBSWY3DPEBLW64TMMQ======",
  "qr_code": "data:image/png;base64,..."
}
```

### POST /auth/2fa/verify
Verify 2FA code

**Request:**
```json
{
  "code": "123456"
}
```

**Response:**
```json
{
  "verified": true
}
```

---

## Panel Endpoints

### GET /panels
Get user panels

**Query Parameters:**
- `skip`: 0
- `limit`: 10
- `status`: draft, published, archived

**Response:**
```json
{
  "panels": [
    {
      "id": "uuid",
      "name": "My Panel",
      "description": "Panel description",
      "theme": "doctor_piscinas",
      "status": "published",
      "created_at": "2024-01-01T00:00:00Z",
      "published_at": "2024-01-02T00:00:00Z"
    }
  ],
  "total": 1
}
```

### POST /panels
Create new panel

**Request:**
```json
{
  "name": "My Panel",
  "description": "Panel description",
  "theme": "doctor_piscinas",
  "config": {
    "colors": {
      "primary": "#FF69B4",
      "secondary": "#00CED1"
    }
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "My Panel",
  "status": "draft",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET /panels/{panel_id}
Get panel details

**Response:**
```json
{
  "id": "uuid",
  "name": "My Panel",
  "description": "Panel description",
  "theme": "doctor_piscinas",
  "config": {...},
  "status": "published",
  "created_at": "2024-01-01T00:00:00Z",
  "published_at": "2024-01-02T00:00:00Z"
}
```

### PUT /panels/{panel_id}
Update panel

**Request:**
```json
{
  "name": "Updated Panel",
  "description": "Updated description"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Updated Panel",
  "updated_at": "2024-01-03T00:00:00Z"
}
```

### DELETE /panels/{panel_id}
Delete panel

**Response:**
```json
{
  "deleted": true
}
```

### POST /panels/{panel_id}/publish
Publish panel

**Response:**
```json
{
  "id": "uuid",
  "status": "published",
  "published_at": "2024-01-02T00:00:00Z"
}
```

### POST /panels/{panel_id}/archive
Archive panel

**Response:**
```json
{
  "id": "uuid",
  "status": "archived"
}
```

### GET /panels/{panel_id}/stats
Get panel statistics

**Response:**
```json
{
  "panel_id": "uuid",
  "name": "My Panel",
  "installations": 5,
  "active_installations": 3,
  "total_views": 1234,
  "views_7d": 456
}
```

---

## Installation Endpoints

### POST /installations
Create installation

**Request:**
```json
{
  "panel_id": "uuid",
  "method": "zip",
  "wordpress_url": "https://example.com"
}
```

**Response:**
```json
{
  "id": "uuid",
  "panel_id": "uuid",
  "method": "zip",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET /installations/{installation_id}
Get installation status

**Response:**
```json
{
  "id": "uuid",
  "panel_id": "uuid",
  "method": "zip",
  "status": "active",
  "wordpress_url": "https://example.com",
  "created_at": "2024-01-01T00:00:00Z",
  "activated_at": "2024-01-01T12:00:00Z"
}
```

### GET /installations/{installation_id}/download
Download plugin ZIP

**Response:** Binary ZIP file

### POST /installations/{installation_id}/ftp
Install via FTP

**Request:**
```json
{
  "ftp_host": "ftp.example.com",
  "ftp_user": "user",
  "ftp_password": "password",
  "ftp_path": "/wp-content/plugins/"
}
```

**Response:**
```json
{
  "status": "installing",
  "message": "Installation started"
}
```

---

## Payment Endpoints

### GET /subscriptions
Get user subscriptions

**Response:**
```json
{
  "subscriptions": [
    {
      "id": "uuid",
      "plan": "pro",
      "price": 29.99,
      "status": "active",
      "started_at": "2024-01-01T00:00:00Z",
      "ends_at": "2024-02-01T00:00:00Z"
    }
  ]
}
```

### POST /subscriptions
Create subscription

**Request:**
```json
{
  "plan": "pro",
  "payment_method": "stripe"
}
```

**Response:**
```json
{
  "id": "uuid",
  "plan": "pro",
  "status": "active",
  "started_at": "2024-01-01T00:00:00Z"
}
```

### POST /payments/stripe/webhook
Stripe webhook

**Request:**
```json
{
  "type": "payment_intent.succeeded",
  "data": {...}
}
```

### GET /invoices
Get user invoices

**Response:**
```json
{
  "invoices": [
    {
      "id": "uuid",
      "number": "INV-001",
      "amount": 29.99,
      "status": "paid",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## Notification Endpoints

### GET /notifications
Get user notifications

**Query Parameters:**
- `skip`: 0
- `limit`: 10

**Response:**
```json
{
  "notifications": [
    {
      "id": "uuid",
      "type": "email",
      "subject": "Panel Created",
      "status": "sent",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /notifications/email
Send email

**Request:**
```json
{
  "to": "user@example.com",
  "subject": "Test Email",
  "html": "<p>Test content</p>"
}
```

### POST /notifications/sms
Send SMS

**Request:**
```json
{
  "phone": "+1234567890",
  "message": "Test message"
}
```

### POST /notifications/whatsapp
Send WhatsApp

**Request:**
```json
{
  "phone": "+1234567890",
  "message": "Test message"
}
```

---

## Admin Endpoints

### GET /admin/users
Get all users (admin only)

**Response:**
```json
{
  "users": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "username": "username",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100
}
```

### GET /admin/analytics
Get analytics (admin only)

**Response:**
```json
{
  "total_users": 1000,
  "total_panels": 5000,
  "total_revenue": 50000,
  "active_subscriptions": 500
}
```

### GET /admin/audit-logs
Get audit logs (admin only)

**Response:**
```json
{
  "logs": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "action": "panel_created",
      "resource_id": "uuid",
      "details": {...},
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request",
  "details": "Field 'name' is required"
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "details": "Invalid token"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "details": "You don't have permission"
}
```

### 404 Not Found
```json
{
  "error": "Not found",
  "details": "Panel not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "details": "Something went wrong"
}
```

---

## Rate Limiting

- 100 requests per minute per user
- 1000 requests per hour per user

Headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1234567890
```

---

## Webhooks

### Panel Events
- `panel.created`
- `panel.updated`
- `panel.published`
- `panel.archived`
- `panel.deleted`

### Installation Events
- `installation.created`
- `installation.pending`
- `installation.active`
- `installation.failed`

### Payment Events
- `payment.created`
- `payment.succeeded`
- `payment.failed`
- `subscription.created`
- `subscription.cancelled`

---

## Code Examples

### Python
```python
import requests

API_URL = "http://localhost:8000/api/v1"
TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# Get panels
response = requests.get(f"{API_URL}/panels", headers=headers)
panels = response.json()

# Create panel
data = {
    "name": "My Panel",
    "description": "Panel description",
    "theme": "doctor_piscinas",
    "config": {"colors": {"primary": "#FF69B4"}}
}
response = requests.post(f"{API_URL}/panels", json=data, headers=headers)
panel = response.json()
```

### JavaScript
```javascript
const API_URL = "http://localhost:8000/api/v1";
const TOKEN = "your_jwt_token";

const headers = {
    "Authorization": `Bearer ${TOKEN}`,
    "Content-Type": "application/json"
};

// Get panels
fetch(`${API_URL}/panels`, { headers })
    .then(r => r.json())
    .then(data => console.log(data));

// Create panel
const panelData = {
    name: "My Panel",
    description: "Panel description",
    theme: "doctor_piscinas",
    config: { colors: { primary: "#FF69B4" } }
};

fetch(`${API_URL}/panels`, {
    method: "POST",
    headers,
    body: JSON.stringify(panelData)
})
    .then(r => r.json())
    .then(data => console.log(data));
```

### cURL
```bash
# Get panels
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/panels

# Create panel
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Panel",
    "description": "Panel description",
    "theme": "doctor_piscinas",
    "config": {"colors": {"primary": "#FF69B4"}}
  }' \
  http://localhost:8000/api/v1/panels
```

---

## Support

For API support, visit: https://panelgenerator.pro/docs
