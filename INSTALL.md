# Panel Generator Pro - Installation Guide

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)

## Quick Start with Docker

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/panel-generator-pro.git
cd panel-generator-pro
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start services

```bash
docker-compose up -d
```

### 4. Initialize database

```bash
docker-compose exec backend python -m alembic upgrade head
```

### 5. Access the application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Dashboard: http://localhost:3001
- API Docs: http://localhost:8000/api/docs
- Database UI: http://localhost:8080

## Local Development Setup

### Backend Setup

#### 1. Create virtual environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

#### 3. Configure database

```bash
# Create PostgreSQL database
createdb panel_generator
```

#### 4. Run migrations

```bash
alembic upgrade head
```

#### 5. Start backend server

```bash
uvicorn main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

#### 1. Install dependencies

```bash
cd frontend
npm install
```

#### 2. Create .env file

```bash
REACT_APP_API_URL=http://localhost:8000
```

#### 3. Start development server

```bash
npm start
```

Frontend will be available at http://localhost:3000

### Admin Dashboard Setup

#### 1. Install dependencies

```bash
cd admin
npm install
```

#### 2. Create .env file

```bash
REACT_APP_API_URL=http://localhost:8000
```

#### 3. Start development server

```bash
npm start
```

Admin will be available at http://localhost:3001

## Configuration

### Environment Variables

Key variables to configure in `.env`:

```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/panel_generator

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# PayPal
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_client_secret

# Email
SENDGRID_API_KEY=SG.your_api_key

# SMS
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token

# WhatsApp
WHATSAPP_BUSINESS_ACCESS_TOKEN=your_token
```

## Database Migrations

### Create new migration

```bash
alembic revision --autogenerate -m "Description"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback migrations

```bash
alembic downgrade -1
```

## Testing

### Backend tests

```bash
cd backend
pytest
```

### Frontend tests

```bash
cd frontend
npm test
```

## Deployment

### Production with Docker

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Deploy to AWS

```bash
# Using AWS CLI
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

docker build -t panel-generator-pro .
docker tag panel-generator-pro:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/panel-generator-pro:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/panel-generator-pro:latest
```

### Deploy to Heroku

```bash
heroku create panel-generator-pro
heroku addons:create heroku-postgresql:standard-0
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
```

## Troubleshooting

### Database connection error

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check database URL in .env
# Format: postgresql://user:password@host:port/database
```

### Port already in use

```bash
# Change port in docker-compose.yml
# Or kill process using the port
lsof -i :8000
kill -9 <PID>
```

### Redis connection error

```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
redis-cli ping
```

### Frontend can't connect to API

```bash
# Check REACT_APP_API_URL in frontend/.env
# Should be http://localhost:8000 for local development
# Should be https://api.yourdomain.com for production
```

## Monitoring

### View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Health check

```bash
curl http://localhost:8000/api/v1/health
```

### Metrics

Prometheus metrics available at:
```
http://localhost:8000/metrics
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/panel-generator-pro/issues
- Email: support@panelgenerator.pro
- Documentation: https://docs.panelgenerator.pro

## License

MIT License - See LICENSE file for details
