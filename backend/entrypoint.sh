#!/bin/bash
set -e

echo "🚀 Iniciando entrypoint.sh para QR-FARM Backend"

# Variables de conexión a MySQL desde variables de entorno
DB_HOST=${DB_HOST:-mysql}
DB_PORT=${DB_PORT:-3306}
DB_USER=${DB_USER:-root}
DB_PASSWORD=${DB_PASSWORD:-}
DB_NAME=${DB_NAME:-gestion_ganadera}

echo "📋 Configuración de base de datos:"
echo "   DB_HOST=$DB_HOST"
echo "   DB_PORT=$DB_PORT"
echo "   DB_USER=$DB_USER"
echo "   DB_NAME=$DB_NAME"
echo "   DB_PASSWORD=[oculto]"

# Función para verificar si MySQL está listo para aceptar conexiones
wait_for_mysql() {
    echo "⏳ Esperando a que MySQL esté completamente listo..."
    
    # Verificar que el comando mysql está disponible
    if ! command -v mysql >/dev/null 2>&1; then
        echo "❌ Error: El comando 'mysql' no está disponible."
        echo "   Verifica que default-mysql-client esté instalado."
        exit 1
    fi
    
    # Docker Compose ya garantiza que MySQL está healthy, así que normalmente debería estar listo
    # Pero hacemos una espera defensiva por si hay un pequeño delay
    local max_attempts=10
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        # Intenta hacer una conexión real a MySQL ejecutando un SELECT simple
        local connection_result=1
        local error_output=""
        
        if [ -z "$DB_PASSWORD" ]; then
            # MySQL sin contraseña - usar protocolo TCP explícitamente
            error_output=$(mysql --protocol=TCP -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -e "SELECT 1;" 2>&1)
            mysql_exit_code=$?
        else
            # MySQL con contraseña - usar protocolo TCP explícitamente
            error_output=$(mysql --protocol=TCP -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" --password="$DB_PASSWORD" -e "SELECT 1;" 2>&1)
            mysql_exit_code=$?
        fi
        
        if [ $mysql_exit_code -eq 0 ]; then
            echo "✅ MySQL está listo y aceptando conexiones."
            return 0
        fi
        
        attempt=$((attempt + 1))
        if [ $attempt -le 3 ]; then
            echo "   Intento $attempt/$max_attempts: MySQL aún no está listo, esperando..."
            if [ -n "$error_output" ]; then
                echo "   Error: $(echo "$error_output" | head -1)"
            fi
        elif [ $((attempt % 3)) -eq 0 ]; then
            echo "   Intento $attempt/$max_attempts: MySQL aún no está listo, esperando..."
        fi
        
        # En los primeros intentos esperar menos tiempo ya que Docker Compose ya verificó el healthcheck
        sleep 1
    done
    
    echo "❌ Error: MySQL no está disponible después de $max_attempts intentos."
    echo "   Verifica que el servicio MySQL esté corriendo y accesible en $DB_HOST:$DB_PORT"
    echo "   Intentando conexión directa para diagnóstico..."
    if [ -z "$DB_PASSWORD" ]; then
        mysql --protocol=TCP -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -e "SELECT 1;" 2>&1 || true
    else
        mysql --protocol=TCP -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" --password="$DB_PASSWORD" -e "SELECT 1;" 2>&1 || true
    fi
    exit 1
}

# Esperar a que MySQL esté listo
wait_for_mysql

# Verificar que la base de datos existe, crearla si no existe
echo "🔍 Verificando existencia de la base de datos '$DB_NAME'..."
if [ -z "$DB_PASSWORD" ]; then
    mysql --protocol=TCP -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;" 2>/dev/null || true
else
    mysql --protocol=TCP -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" --password="$DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;" 2>/dev/null || true
fi
echo "✅ Base de datos '$DB_NAME' verificada/creada."

# Ejecutar migraciones de Alembic ANTES de cargar Flask
# Esto asegura que las tablas existan antes de que inicializar_super_admin() se ejecute
echo "🚀 Ejecutando migraciones de base de datos (alembic upgrade head)..."
if alembic -c alembic.ini upgrade head 2>&1; then
    echo "✅ Migraciones completadas exitosamente."
else
    migration_exit_code=$?
    echo "❌ Error al ejecutar migraciones (código de salida: $migration_exit_code)."
    echo "   Verifica los logs anteriores para más detalles."
    exit 1
fi

# Iniciar la aplicación Flask
echo "🚀 Iniciando aplicación Flask..."
exec python app.py
