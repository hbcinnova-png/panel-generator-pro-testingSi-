#!/bin/bash

# Panel Generator Pro - Startup Script

set -e

echo "🚀 Panel Generator Pro v4.0.0"
echo "================================"

# Verificar si .env existe
if [ ! -f .env ]; then
    echo "⚠️  .env no encontrado. Creando desde .env.example..."
    cp .env.example .env
    echo "✅ .env creado. Por favor, edita los valores necesarios."
    echo "   Luego ejecuta este script nuevamente."
    exit 1
fi

echo "📦 Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

echo "📦 Verificando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

echo "🔨 Construyendo imágenes..."
docker-compose build

echo "🚀 Iniciando servicios..."
docker-compose up -d

echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

echo "✅ Servicios iniciados"
echo ""
echo "📍 Acceso:"
echo "   Frontend:  http://localhost:3000"
echo "   Admin:     http://localhost:3001"
echo "   API:       http://localhost:8000"
echo "   Adminer:   http://localhost:8080"
echo ""
echo "🔐 HTTPS (con Nginx):"
echo "   Frontend:  https://localhost"
echo "   API:       https://localhost/api"
echo ""
echo "📊 Ver logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "🛑 Detener:"
echo "   docker-compose down"
echo ""
echo "✨ ¡Panel Generator Pro está listo!"
