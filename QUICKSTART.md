# Panel Generator Pro - Guía Rápida

## 🚀 Inicio Rápido en 5 Minutos

### Opción 1: Con Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone https://github.com/tuusuario/panel-generator-pro.git
cd panel-generator-pro

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Iniciar con Docker Compose
docker-compose up -d

# 4. Acceder a la aplicación
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Admin: http://localhost:3001
# Database UI: http://localhost:8080
```

### Opción 2: Instalación Manual

```bash
# 1. Instalar dependencias Python
cd backend
pip install -r requirements.txt

# 2. Configurar base de datos
psql -U postgres -c "CREATE DATABASE panel_generator;"
psql -U postgres -d panel_generator -f ../database/schema.sql

# 3. Ejecutar servidor
python api.py

# 4. En otra terminal, servir frontend
cd ../frontend
python -m http.server 3000
```

## 📋 Configuración Inicial

### 1. Crear Usuario Admin

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "SecurePassword123!",
    "full_name": "Administrator",
    "company": "Your Company",
    "phone": "+34123456789"
  }'
```

### 2. Configurar Stripe (Opcional)

```bash
# En .env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### 3. Configurar Email (Opcional)

```bash
# En .env
SENDGRID_API_KEY=SG.your_api_key
# O usar SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## 🎯 Flujo de Uso

### Para Clientes

1. **Acceder a http://localhost:3000**
2. **Rellenar formulario en 4 pasos:**
   - Paso 1: Información del negocio
   - Paso 2: Diseño y tema
   - Paso 3: Servicios e integraciones
   - Paso 4: Método de instalación
3. **Generar panel**
4. **Instalar en WordPress**

### Para Administradores

1. **Acceder a http://localhost:3001**
2. **Dashboard:**
   - Ver estadísticas
   - Gestionar usuarios
   - Configurar sistema
   - Ver auditoría

## 🔧 Comandos Útiles

```bash
# Ver logs
docker-compose logs -f backend

# Acceder a base de datos
docker-compose exec postgres psql -U panel_user -d panel_generator

# Reiniciar servicios
docker-compose restart

# Detener todo
docker-compose down

# Eliminar datos
docker-compose down -v
```

## 📊 Estructura de Datos

### Usuario
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "company": "Company",
  "role": "user",
  "subscription_plan": "starter",
  "credits": 100
}
```

### Panel
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "Mi Panel",
  "business_name": "Mi Negocio",
  "theme": "doctor_piscinas",
  "colors": {
    "primary": "#ff006e",
    "secondary": "#00d9ff"
  },
  "services": ["Servicio 1", "Servicio 2"],
  "status": "published",
  "installation_status": "installed"
}
```

## 🔐 Seguridad

### Cambiar Secret Key (IMPORTANTE)

```bash
# Generar nueva clave
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Actualizar en .env
SECRET_KEY=tu_nueva_clave_segura
```

### Habilitar HTTPS

```bash
# Generar certificados SSL
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Actualizar nginx.conf con rutas a certificados
```

## 🚀 Despliegue en Producción

### Heroku

```bash
# 1. Crear aplicación
heroku create panel-generator-pro

# 2. Agregar base de datos
heroku addons:create heroku-postgresql:standard-0

# 3. Configurar variables
heroku config:set SECRET_KEY=your_secret_key
heroku config:set STRIPE_SECRET_KEY=sk_...

# 4. Deploy
git push heroku main
```

### AWS

```bash
# Usar Elastic Beanstalk
eb create panel-generator-pro
eb deploy
```

### DigitalOcean

```bash
# Usar App Platform
doctl apps create --spec app.yaml
```

## 📚 Documentación Completa

- [API Documentation](./docs/API.md)
- [Installation Guide](./docs/INSTALLATION.md)
- [Usage Guide](./docs/USAGE.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)

## 🆘 Solución de Problemas

### Error de conexión a base de datos

```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps postgres

# Reiniciar PostgreSQL
docker-compose restart postgres
```

### Error de puerto en uso

```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "5433:5432"  # Cambiar 5432 a 5433
```

### Error de CORS

```bash
# Actualizar CORS_ORIGINS en .env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://tu-dominio.com
```

## 💡 Tips

1. **Usar Postman** para probar API endpoints
2. **Habilitar debug** en desarrollo: `APP_DEBUG=True`
3. **Monitorear logs** en tiempo real: `docker-compose logs -f`
4. **Hacer backup** de base de datos regularmente
5. **Usar variables de entorno** para secretos

## 📞 Soporte

- Documentación: https://docs.panelgenerator.pro
- Email: support@panelgenerator.pro
- Chat: https://panelgenerator.pro/chat

---

**¡Listo para comenzar!** 🎉
