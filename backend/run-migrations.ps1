# Script para ejecutar migraciones de Alembic desde Windows
# Este script detecta automáticamente el entorno y configura las variables necesarias

Write-Host "🚀 Iniciando migraciones de Alembic..." -ForegroundColor Cyan

# Verificar si las variables ya están configuradas (desde .env o manualmente)
$dbHost = $env:DB_HOST
$dbUser = $env:DB_USER
$dbPassword = $env:DB_PASSWORD
$dbName = $env:DB_NAME
$dbPort = $env:DB_PORT

# Si no están configuradas, usar valores por defecto para desarrollo local
if (-not $dbHost) {
    Write-Host "⚠️  DB_HOST no configurado, usando 'localhost' (desarrollo local)" -ForegroundColor Yellow
    $env:DB_HOST = "localhost"
    $dbHost = "localhost"
}

if (-not $dbUser) {
    $env:DB_USER = "root"
    $dbUser = "root"
}

if (-not $dbPassword) {
    $env:DB_PASSWORD = ""
    $dbPassword = ""
}

if (-not $dbName) {
    $env:DB_NAME = "gestion_ganadera"
    $dbName = "gestion_ganadera"
}

if (-not $dbPort) {
    $env:DB_PORT = "3306"
    $dbPort = "3306"
}

Write-Host "✅ Configuración de base de datos:" -ForegroundColor Green
Write-Host "   Host: $dbHost" -ForegroundColor Gray
Write-Host "   Usuario: $dbUser" -ForegroundColor Gray
Write-Host "   Base de datos: $dbName" -ForegroundColor Gray
Write-Host "   Puerto: $dbPort" -ForegroundColor Gray

# Verificar si MySQL está disponible (solo si es localhost)
if ($dbHost -eq "localhost" -or $dbHost -eq "127.0.0.1") {
    Write-Host "`n🔍 Verificando conexión a MySQL..." -ForegroundColor Cyan
    $mysqlRunning = docker ps --filter "name=qr-farm-mysql" --format "{{.Names}}" 2>$null
    if (-not $mysqlRunning) {
        Write-Host "⚠️  MySQL no está corriendo en Docker. Iniciando..." -ForegroundColor Yellow
        docker-compose up -d mysql
        Start-Sleep -Seconds 3
    } else {
        Write-Host "✅ MySQL está corriendo" -ForegroundColor Green
    }
}

Write-Host "`n🔄 Ejecutando migraciones de Alembic..." -ForegroundColor Cyan
alembic -c alembic.ini upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Migraciones ejecutadas correctamente!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Error al ejecutar migraciones. Verifica que:" -ForegroundColor Red
    Write-Host "   1. MySQL esté corriendo: docker-compose up -d mysql" -ForegroundColor Yellow
    Write-Host "   2. El puerto 3306 esté disponible" -ForegroundColor Yellow
    Write-Host "   3. Las credenciales en .env sean correctas" -ForegroundColor Yellow
    Write-Host "   4. La base de datos '$dbName' exista" -ForegroundColor Yellow
    exit $LASTEXITCODE
}

