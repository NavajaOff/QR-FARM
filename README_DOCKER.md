# 🐳 QR-Farm - Guía Completa de Docker

Esta guía explica paso a paso cómo ejecutar QR-Farm **completamente dockerizado** usando el builder clásico de Docker para máxima estabilidad y compatibilidad.

**Para desarrollo local sin Docker, consulta el [`README.md`](README.md) principal del proyecto.**

---

## 📋 Tabla de Contenidos

1. [¿Por qué Docker?](#por-qué-docker)
2. [Requisitos Previos](#requisitos-previos)
3. [Configuración Inicial](#configuración-inicial)
4. [Instalación Paso a Paso](#instalación-paso-a-paso)
5. [Verificación y Uso](#verificación-y-uso)
6. [Comandos Útiles](#comandos-útiles)
7. [Solución de Problemas](#solución-de-problemas)
8. [Reconstrucción Después de Cambios](#reconstrucción-después-de-cambios)

---

## 🎯 ¿Por qué Docker?

Docker permite ejecutar QR-Farm de forma **aislada y reproducible** en cualquier máquina con Docker instalado. Es ideal para:

- ✅ **Demostraciones** rápidas del proyecto
- ✅ **Desarrollo** consistente entre el equipo
- ✅ **Entornos institucionales** (SENA) con configuraciones controladas
- ✅ **Distribución** fácil del proyecto completo
- ✅ **Sin conflictos** de versiones de Python, Node.js o MySQL

### ⚡ Ventajas de Docker vs Desarrollo Local

| Aspecto | Desarrollo Local | Docker |
|---------|------------------|--------|
| **Configuración inicial** | 15-20 minutos | 5 minutos |
| **Dependencias** | Instalar Python, MySQL, Node.js | Solo Docker |
| **Base de datos** | Configurar MySQL local | MySQL automático en contenedor |
| **Compatibilidad** | Solo tu máquina | Cualquier máquina con Docker |
| **Persistencia** | Manual | Volúmenes automáticos |
| **Limpieza** | Manual | `docker compose down -v` |

---

## 📦 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

### 1. Docker y Docker Compose

**Windows:**
- Docker Desktop (incluye Docker y Docker Compose)
- Descarga desde: https://www.docker.com/products/docker-desktop

**Linux:**
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**Verificar instalación:**
```bash
docker --version
docker compose version
```

### 2. WSL2 (Solo Windows)

Si usas Windows, necesitas WSL2 habilitado:
- Docker Desktop lo configura automáticamente
- O instala manualmente: `wsl --install`

### 3. Recursos del Sistema

- **RAM mínima:** 4 GB disponibles
- **Espacio en disco:** 5 GB libres
- **Conexión a Internet:** Para descargar imágenes base (solo primera vez)

---

## 🔧 Configuración Inicial

### Paso 1: Clonar o Descargar el Proyecto

### Paso 2: Configurar Variables de Entorno

Crea el archivo `.env` en la raíz del proyecto:

```bash
# En Linux/Mac/WSL
cp .env.example .env

# En Windows (PowerShell)
Copy-Item .env.example .env
```

**Edita el archivo `.env`** y configura las siguientes variables:

```env
# ============================================================================
# Configuración de Flask
# ============================================================================
FLASK_ENV=production
DEBUG=False
SECRET_KEY=tu_clave_secreta_aqui_genera_una_aleatoria
FLASK_APP=app.py

# ============================================================================
# Configuración de Base de Datos
# NOTA: En Docker, estas variables se sobrescriben por docker-compose.yml
# DB_HOST se establece automáticamente como 'mysql' dentro de Docker
# ============================================================================
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=gestion_ganadera

# ============================================================================
# Configuración CORS (OBLIGATORIO)
# Debe incluir el puerto del frontend: http://localhost:5174
# ============================================================================
CORS_ORIGINS=http://localhost:5174,http://localhost:5173,http://localhost:80

# ============================================================================
# URL del Backend para el Frontend (OBLIGATORIO)
# Debe usar el puerto externo mapeado: http://localhost:5010
# ============================================================================
VITE_BACKEND_URL=http://localhost:5010

# ============================================================================
# Super Administrador (creado automáticamente)
# ============================================================================
ROOT_SUPER_ADMIN_EMAIL=superadmin@qrfarm.com
ROOT_SUPER_ADMIN_PASSWORD=tu_contraseña_segura_aqui
ROOT_SUPER_ADMIN_NOMBRE=Super Administrador QR-Farm

# ============================================================================
# JWT Secret Key (para tokens de autenticación)
# ============================================================================
JWT_SECRET_KEY=tu_jwt_secret_aqui_genera_una_aleatoria
```

**Generar claves seguras:**

Para generar claves aleatorias seguras, ejecuta:

```bash
# Generar SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Generar JWT_SECRET_KEY
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
```

Copia los valores generados y pégalos en tu archivo `.env`.

### Paso 3: Verificar Estructura del Proyecto

Asegúrate de que tienes estos archivos en la raíz:

```
QR-FARM/
├── .env                    ← Archivo que acabas de crear
├── docker-compose.yml      ← Configuración de servicios
├── Dockerfile.backend      ← Imagen del backend
├── Dockerfile.frontend     ← Imagen del frontend
├── .dockerignore           ← Archivos excluidos del build
├── backend/
│   ├── entrypoint.sh       ← Script de inicialización
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── package.json
│   └── ...
└── ...
```

---

## 🚀 Instalación Paso a Paso

### Paso 1: Preparar el Entorno (Solo Primera Vez)

#### En Linux/Mac/WSL:

```bash
# Navegar al directorio del proyecto
cd QR-FARM

# Corregir finales de línea en entrypoint.sh (solo si usas WSL/Windows)
# Esto asegura que el script funcione correctamente
sed -i 's/\r$//' backend/entrypoint.sh
```

#### En Windows (PowerShell):

```bash
# Navegar al directorio del proyecto
cd QR-FARM

# Si usas Git Bash o WSL, puedes ejecutar el comando sed desde ahí
# O simplemente asegúrate de que entrypoint.sh tenga finales de línea Unix (LF)
```

### Paso 2: Deshabilitar BuildKit (Recomendado)

**¿Por qué deshabilitar BuildKit?**

BuildKit es el builder moderno de Docker que permite builds paralelos, pero puede causar:
- Timeouts con `auth.docker.io` en redes lentas o institucionales
- Errores `ETXTBSY` con esbuild durante `npm install` en WSL2
- Problemas de sincronización de archivos en entornos compartidos

El builder clásico es más estable y tolerante a problemas de red:

```bash
# En Linux/Mac/WSL
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

# En Windows (PowerShell) recomendable hacer el de arriba en la consola wsl
$env:DOCKER_BUILDKIT=0
$env:COMPOSE_DOCKER_CLI_BUILD=0
```

**Nota:** Estas variables solo afectan a la sesión actual del terminal. Si cierras y abres un nuevo terminal, debes volver a ejecutarlas antes de hacer builds.

### Paso 3: Construir las Imágenes Docker

```bash
# Construir todas las imágenes (backend, frontend, MySQL se descarga automáticamente)
docker compose build
```

**¿Qué hace este comando?**

1. Descarga imágenes base (si no están en cache):
   - `python:3.11-slim` (backend)
   - `node:20-alpine` (frontend build)
   - `nginx:stable-alpine` (frontend runtime)
   - `mysql:8.0` (base de datos)

2. Construye el backend:
   - Instala dependencias Python
   - Copia código del backend
   - Crea imagen `qr-farm-backend`

3. Construye el frontend:
   - Instala dependencias Node.js
   - Compila la aplicación Vue.js
   - Crea imagen `qr-farm-frontend`

**Tiempo estimado:** 5-15 minutos (depende de tu conexión a Internet y velocidad del CPU)

### Paso 4: Iniciar los Servicios

```bash
# Iniciar todos los servicios en segundo plano
docker compose up -d
```

**¿Qué hace este comando?**

1. ✅ Crea la red `qr-farm-network`
2. ✅ Crea el volumen `mysql_data` (persistencia de BD)
3. ✅ Inicia MySQL y espera a que esté healthy
4. ✅ Inicia el backend:
   - Espera a que MySQL esté listo
   - Ejecuta migraciones automáticamente (`alembic upgrade head`)
   - Inicializa el super admin
   - Inicia Flask en puerto 5000
5. ✅ Inicia el frontend (Nginx sirviendo la app Vue)

**Verificar que todo esté corriendo:**

```bash
# Ver estado de todos los contenedores
docker compose ps

# Deberías ver algo como:
# NAME                 STATUS          PORTS
# qr-farm-backend      Up (healthy)    0.0.0.0:5010->5000/tcp
# qr-farm-frontend     Up              0.0.0.0:5174->80/tcp
# qr-farm-mysql        Up (healthy)    0.0.0.0:3313->3306/tcp
```

---

## ✅ Verificación y Uso

### 1. Verificar Logs

```bash
# Ver logs de todos los servicios
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mysql
```

**Logs esperados del backend:**
```
🚀 Iniciando entrypoint.sh para QR-FARM Backend
📋 Configuración de base de datos:
   DB_HOST=mysql
   DB_PORT=3306
   DB_USER=root
   DB_NAME=gestion_ganadera
⏳ Esperando a que MySQL esté completamente listo...
✅ MySQL está listo y aceptando conexiones.
🔍 Verificando existencia de la base de datos 'gestion_ganadera'...
✅ Base de datos 'gestion_ganadera' verificada/creada.
🚀 Ejecutando migraciones de base de datos (alembic upgrade head)...
✅ Migraciones completadas exitosamente.
🚀 Iniciando aplicación Flask...
```

### 2. Acceder a la Aplicación

Una vez que todos los servicios estén corriendo:

- **Frontend (Interfaz Web):** http://localhost:5174
- **Backend API:** http://localhost:5010
- **Health Check API:** http://localhost:5010/api/health
- **Base de datos MySQL:** `localhost:3313` (desde herramientas externas)

### 3. Credenciales de Acceso

**Super Administrador (creado automáticamente):**
- **Email:** El valor de `ROOT_SUPER_ADMIN_EMAIL` en tu `.env` 
- **Contraseña:** El valor de `ROOT_SUPER_ADMIN_PASSWORD` en tu `.env`

### 4. Prueba Rápida

1. Abre tu navegador en http://localhost:5174
2. Inicia sesión con las credenciales del super admin que definiste en el .env
3. Deberías ver el dashboard de QR-Farm

---

## 🛠️ Comandos Útiles

### Gestión de Contenedores

```bash
# Ver estado de servicios
docker compose ps

# Iniciar servicios
docker compose up -d

# Detener servicios (mantiene datos)
docker compose stop

# Detener y eliminar contenedores (mantiene datos)
docker compose down

# Detener y eliminar TODO (incluyendo volúmenes - BORRA DATOS)
docker compose down -v

# Reiniciar un servicio específico
docker compose restart backend
docker compose restart frontend

# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f backend
```

### Ejecutar Comandos Dentro de Contenedores

```bash
# Acceder al shell del backend
docker compose exec backend bash

# Ejecutar comando en el backend
docker compose exec backend python -c "print('Hola')"

# Ver migraciones aplicadas (desde el backend)
docker compose exec backend alembic -c alembic.ini current

# Ver historial de migraciones
docker compose exec backend alembic -c alembic.ini history
```

### Gestión de Imágenes

```bash
# Ver imágenes construidas
docker images | grep qr-farm

# Limpiar imágenes no utilizadas
docker image prune -f

# Limpiar todo (imágenes, contenedores, volúmenes no usados)
docker system prune -a
```

---

## 🔧 Solución de Problemas

### Error: "Cannot connect to Docker daemon"

**Causa:** Docker no está corriendo.

**Solución:**
```bash
# Linux
sudo systemctl start docker

# Windows/Mac: Abre Docker Desktop
```

### Error: Timeout al construir imágenes

**Causa:** Problemas de red o BuildKit intentando verificar metadata.

**Solución:**
```bash
# Deshabilitar BuildKit (como se explicó arriba)
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

# Limpiar cache y reconstruir
docker builder prune -a
docker compose build --no-cache
```

### Error: "ETXTBSY" o "Text file busy" durante npm install

**Causa:** BuildKit intentando acceder a archivos mientras se instalan.

**Solución:**
```bash
# Deshabilitar BuildKit (obligatorio)
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

# Limpiar imágenes anteriores
docker compose down
docker image prune -f

# Reconstruir
docker compose build
```

### Error: "Can't connect to MySQL server"

**Causa:** MySQL no está listo o backend inició antes.

**Solución:**
```bash
# Verificar estado de MySQL
docker compose ps mysql
docker compose logs mysql

# Verificar healthcheck
docker compose exec mysql mysqladmin ping -h localhost --silent

# Si MySQL no está healthy, reiniciar
docker compose restart mysql

# Esperar a que esté healthy, luego reiniciar backend
docker compose up -d mysql
docker compose restart backend
```

### Error: "CORS_ORIGINS debe estar configurado"

**Causa:** Falta la variable `CORS_ORIGINS` en `.env`.

**Solución:**
Edita `.env` y agrega:
```env
CORS_ORIGINS=http://localhost:5174,http://localhost:5173,http://localhost:80
```

Luego reinicia el backend:
```bash
docker compose restart backend
```

### Error: "Table doesn't exist" o "No such table"

**Causa:** Las migraciones no se ejecutaron.

**Solución:**
```bash
# Ejecutar migraciones manualmente
docker compose exec backend alembic -c alembic.ini upgrade head

# Verificar migraciones aplicadas
docker compose exec backend alembic -c alembic.ini current
```

### Error: Backend se reinicia constantemente

**Causa:** Error en el código o configuración que causa crash.

**Solución:**
```bash
# Ver logs detallados
docker compose logs -f backend

# Buscar el error específico en los logs
# Comúnmente son:
# - Error de importación de módulos
# - Error de conexión a MySQL
# - Error de variables de entorno faltantes
```

### Contenedor MySQL no inicia

**Causa:** Puerto 3313 ya en uso o volumen corrupto.

**Solución:**
```bash
# Verificar qué usa el puerto 3313
# Linux/Mac
lsof -i :3313

# Windows
netstat -ano | findstr :3313

# Si necesitas cambiar el puerto, edita docker-compose.yml:
# ports:
#   - "3314:3306"  # Cambiar 3313 por otro puerto

# Si el volumen está corrupto, eliminar y recrear (BORRA DATOS)
docker compose down -v
docker compose up -d mysql
```

### Limpiar Todo y Empezar de Nuevo

Si necesitas empezar completamente desde cero:

```bash
# Detener y eliminar TODO
docker compose down -v

# Eliminar imágenes
docker rmi qr-farm-backend qr-farm-frontend 2>/dev/null || true

# Limpiar cache de Docker
docker builder prune -a
docker system prune -f

# Reconstruir desde cero
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
docker compose build
docker compose up -d
```

---

## 🔄 Reconstrucción Después de Cambios

Cuando haces cambios en el código, debes reconstruir las imágenes para ver los cambios.

### Cambios en el Backend

```bash
# Reconstruir imagen del backend
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
docker compose build backend

# Reiniciar contenedor con nueva imagen
docker compose up -d backend
```

### Cambios en el Frontend

```bash
# Reconstruir imagen del frontend
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
docker compose build frontend

# Reiniciar contenedor con nueva imagen
docker compose up -d frontend
```

### Cambios en Ambos

```bash
# Reconstruir todo
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
docker compose build

# Reiniciar servicios
docker compose up -d
```

### Reconstrucción Completa (Sin Cache)

Si quieres asegurarte de que todo se reconstruya desde cero:

```bash
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
docker compose build --no-cache
docker compose up -d
```

---

## 📊 Arquitectura Docker

### Servicios

```
┌─────────────────────────────────────────────────────────┐
│                    qr-farm-network                      │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐   ┌───────────┐ │
│  │   Frontend   │    │   Backend    │   │   MySQL   │ │
│  │  (Nginx)     │    │   (Flask)    │   │  (8.0)    │ │
│  │  :80 → 5174  │◄───│  :5000→5010  │──►│  :3306    │ │
│  └──────────────┘    └──────────────┘   └───────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Puertos

| Servicio | Puerto Interno | Puerto Externo | URL de Acceso |
|----------|----------------|----------------|---------------|
| Frontend | 80 | 5174 | http://localhost:5174 |
| Backend | 5000 | 5010 | http://localhost:5010 |
| MySQL | 3306 | 3313 | localhost:3313 |

### Volúmenes

- **`mysql_data`**: Persistencia de la base de datos MySQL
- **`./qr:/app/qr`**: Códigos QR generados (mapeado al host)

### Variables de Entorno

Las variables se cargan desde:
1. Archivo `.env` (en la raíz del proyecto)
2. `docker-compose.yml` (sobrescribe algunas variables)
3. Variables de entorno del sistema (máxima prioridad)

---

## 🎓 Notas para Entornos Institucionales (SENA)

### BuildKit Deshabilitado

Este proyecto usa el **builder clásico de Docker** (BuildKit deshabilitado) porque:
- ✅ Más estable en redes institucionales
- ✅ Evita timeouts con `auth.docker.io`
- ✅ Previene errores `ETXTBSY` con esbuild
- ✅ Compatible con proxies corporativos



### Firewall

Asegúrate de que estos puertos estén abiertos:
- **5174**: Frontend
- **5010**: Backend API
- **3313**: MySQL (solo si necesitas acceso externo)

---

## 📝 Resumen de Comandos Esenciales

```bash
# ============================================================================
# SETUP INICIAL (Solo primera vez)
# ============================================================================
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
docker compose build
docker compose up -d

# ============================================================================
# USO DIARIO
# ============================================================================
# Iniciar servicios
docker compose up -d

# Ver logs
docker compose logs -f

# Detener servicios
docker compose stop

# Reiniciar un servicio
docker compose restart backend

# ============================================================================
# DESPUÉS DE CAMBIOS EN CÓDIGO
# ============================================================================
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
docker compose build
docker compose up -d

# ============================================================================
# LIMPIEZA
# ============================================================================
# Detener y eliminar (mantiene datos)
docker compose down

# Detener y eliminar TODO (BORRA DATOS)
docker compose down -v
```

---

## 🆘 Soporte Adicional

Si encuentras problemas que no están documentados aquí:

1. **Revisa los logs:**
   ```bash
   docker compose logs -f
   ```

2. **Verifica el estado:**
   ```bash
   docker compose ps
   ```

3. **Consulta la documentación oficial:**
   - Docker: https://docs.docker.com/
   - Docker Compose: https://docs.docker.com/compose/

4. **Revisa el README principal:**
   - [`README.md`](README.md) para desarrollo local

---

## ✅ Checklist de Instalación

Marca cada paso conforme lo completes:

- [ ] Docker y Docker Compose instalados y funcionando
- [ ] Archivo `.env` creado y configurado con todas las variables
- [ ] BuildKit deshabilitado (`export DOCKER_BUILDKIT=0`)
- [ ] Imágenes construidas exitosamente (`docker compose build`)
- [ ] Servicios iniciados (`docker compose up -d`)
- [ ] Todos los contenedores en estado "Up" (`docker compose ps`)
- [ ] Frontend accesible en http://localhost:5174
- [ ] Backend accesible en http://localhost:5010/api/health
- [ ] Login funciona con credenciales del super admin

**¡Tu aplicación QR-Farm está lista para usar!** 🎉

---

**Última actualización:** Diciembre 2024  
**Builder utilizado:** Docker Classic Builder (BuildKit deshabilitado)  
**Versión de Docker Compose:** v2.x
