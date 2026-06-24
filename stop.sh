#!/bin/bash

# Panel Generator Pro - Stop Script

echo "🛑 Deteniendo Panel Generator Pro..."

docker-compose down

echo "✅ Servicios detenidos"
echo ""
echo "💡 Para eliminar volúmenes (CUIDADO - borra datos):"
echo "   docker-compose down -v"
