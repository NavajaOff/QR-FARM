#!/bin/bash
# Script para ejecutar migraciones de Alembic desde Linux/Mac
# Este script detecta automáticamente el entorno y configura las variables necesarias

set -e

echo "🚀 Iniciando migraciones de Alembic..."

# Verificar si las variables ya están configuradas (desde .env o manualmente)
DB_HOST=${DB_HOST:-localhost}
DB_USER=${DB_USER:-root}
DB_PASSWORD=${DB_PASSWORD:-}
DB_NAME=${DB_NAME:-gestion_ganadera}
DB_PORT=${DB_PORT:-3306}

# Exportar variables de entorno
export DB_HOST
export DB_USER
export DB_PASSWORD
export DB_NAME
export DB_PORT

echo "✅ Configuración de base de datos:"
echo "   Host: $DB_HOST"
echo "   Usuario: $DB_USER"
echo "   Base de datos: $DB_NAME"
echo "   Puerto: $DB_PORT"

# Verificar si MySQL está disponible (solo si es localhost)
if [ "$DB_HOST" = "localhost" ] || [ "$DB_HOST" = "127.0.0.1" ]; then
    echo ""
    echo "🔍 Verificando conexión a MySQL..."
    if ! docker ps --filter "name=qr-farm-mysql" --format "{{.Names}}" | grep -q "qr-farm-mysql"; then
        echo "⚠️  MySQL no está corriendo en Docker. Iniciando..."
        docker-compose up -d mysql
        sleep 3
    else
        echo "✅ MySQL está corriendo"
    fi
fi

echo ""
echo "🔄 Ejecutando migraciones de Alembic..."
alembic -c alembic.ini upgrade head

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migraciones ejecutadas correctamente!"
else
    echo ""
    echo "❌ Error al ejecutar migraciones. Verifica que:"
    echo "   1. MySQL esté corriendo: docker-compose up -d mysql"
    echo "   2. El puerto 3306 esté disponible"
    echo "   3. Las credenciales en .env sean correctas"
    echo "   4. La base de datos '$DB_NAME' exista"
    exit 1
fi

