#!/bin/bash
set -e

# Variables de conexión a MySQL desde el .env
DB_HOST=${DB_HOST:-mysql}
DB_USER=${DB_USER:-root}
DB_PASS=${DB_PASSWORD:-}
DB_NAME=${DB_NAME:-gestion_ganadera}

# Función para verificar si MySQL está listo
wait_for_mysql() {
    echo "⏳ Esperando a que MySQL esté listo..."
    until mysqladmin ping -h "$DB_HOST" -u "$DB_USER" --password="$DB_PASS" --ssl=0 --silent &>/dev/null; do
        echo "MySQL no está listo, esperando..."
        sleep 2
    done
    echo "✅ MySQL está listo."
}

wait_for_mysql

echo "🚀 Ejecutando migraciones de Alembic..."
alembic -c alembic.ini upgrade head

echo "✅ Migraciones completadas. Iniciando aplicación Flask..."
exec python app.py
