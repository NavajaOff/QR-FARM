# QR-Farm - Docker Setup

Esta guía explica cómo ejecutar QR-Farm completamente dockerizado.

## Requisitos Previos

- Docker y Docker Compose instalados
- WSL (si usas Windows)
- Al menos 4GB de RAM disponible

## Archivos de Configuración

1. **Dockerfile.backend**: Contenedor para el backend Python/Flask
2. **Dockerfile.frontend**: Contenedor para el frontend Vue.js con Nginx
3. **docker-compose.yml**: Orquestación de servicios
4. **nginx.conf**: Configuración de Nginx para SPA
5. **.env.docker.example**: Plantilla de variables de entorno para Docker

## Servicios

- **MySQL 8.0**: Base de datos persistente
- **Backend (Flask)**: API REST en puerto 5000
- **Frontend (Vue.js)**: Interfaz en puerto 80

## Instrucciones de Instalación

### 1. Preparar Variables de Entorno

```bash
cp .env.docker.example .env
# Edita .env con tus valores personalizados
```

### 2. Construir e Iniciar Servicios

```bash
# Construir imágenes y iniciar servicios
docker-compose up --build

# O en background
docker-compose up -d --build
```

### 3. Inicializar Base de Datos (Primera vez)

```bash
# Ejecutar migraciones de base de datos
docker-compose exec backend flask db upgrade

# Crear super administrador
docker-compose exec backend python -c "from backend.app import inicializar_super_admin; inicializar_super_admin()"
```

### 4. Acceder a la Aplicación

- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000
- **Base de datos**: localhost:3306 (desde host)

## Comandos Útiles

```bash
# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Limpiar volúmenes (cuidado: borra datos)
docker-compose down -v

# Reiniciar un servicio
docker-compose restart backend
```

## Configuración de Red

Los servicios se comunican a través de la red `qr-farm-network`:
- Backend conecta a MySQL usando `mysql:3306`
- Frontend accede al backend desde el navegador usando `localhost:5000`

## Persistencia de Datos

- **Base de datos**: Volumen `mysql_data`
- **Códigos QR**: Volumen `./qr` mapeado al contenedor backend

## Solución de Problemas

### Error de conexión a MySQL
Asegúrate que el contenedor MySQL esté healthy:
```bash
docker-compose ps
docker-compose logs mysql
```

### Error de CORS
Verifica que las URLs permitidas en `backend/app.py` incluyan `http://localhost:80`

### Migraciones no aplicadas
Ejecuta manualmente:
```bash
docker-compose exec backend flask db upgrade
```

## Optimizaciones para Producción

- Cambia `SECRET_KEY` y contraseñas en `.env`
- Configura HTTPS con Nginx
- Usa Docker Swarm o Kubernetes para escalado
- Configura backups automáticos de la base de datos