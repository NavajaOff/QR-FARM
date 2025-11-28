# 🐳 QR-Farm - Guía Docker

Esta guía explica cómo ejecutar QR-Farm **completamente dockerizado** para producción o demostraciones.

**Para desarrollo local, consulta el [`README.md`](README.md) principal del proyecto.**

## 🐳 ¿Por qué Docker?

Docker permite ejecutar QR-Farm de forma **aislada y reproducible** en cualquier máquina con Docker instalado. Es ideal para:

- ✅ **Demostraciones** rápidas del proyecto
- ✅ **Desarrollo** consistente entre el equipo
- ✅ **Producción** con configuración optimizada
- ✅ **Distribución** fácil del proyecto completo

### ⚡ Ventajas de Docker vs Desarrollo Local

| Aspecto | Desarrollo Local | Docker |
|---------|------------------|--------|
| **Configuración inicial** | 15-20 minutos | 2-3 minutos |
| **Dependencias** | Instalar Python, MySQL, Node.js | Solo Docker |
| **Base de datos** | Configurar MySQL local | MySQL en contenedor |
| **Compatibilidad** | Solo tu máquina | Cualquier máquina |
| **Persistencia** | Manual | Volúmenes automáticos |
| **Limpieza** | Manual | `docker-compose down -v` |

### Requisitos Previos
- Docker y Docker Compose instalados
- WSL (si usas Windows)
- Al menos 4GB de RAM disponible

### Archivos de Configuración Docker

1. **Dockerfile.backend**: Contenedor para el backend Python/Flask
2. **Dockerfile.frontend**: Contenedor para el frontend Vue.js con Nginx
3. **docker-compose.yml**: Orquestación de servicios
4. **nginx.conf**: Configuración de Nginx para SPA
5. **backend/entrypoint.sh**: Script de inicialización automática
6. **.env.docker**: Variables de entorno configuradas para Docker
7. **.env.docker.example**: Plantilla de respaldo (segura para repositorio)

### Servicios Docker

- **MySQL 8.0**: Base de datos persistente (usuario root, sin contraseña, BD: gestion_ganadera)
- **Backend (Flask)**: API REST en puerto 5000
- **Frontend (Vue.js)**: Interfaz en puerto 80

### Configuración de Base de Datos Docker

**MySQL está configurado con:**
- Usuario:tu_usuario
- Contraseña:tu_contraseña
- Base de datos: `gestion_ganadera`
- Puerto interno: `3306`

**El backend se conecta usando credenciales hardcodeadas en docker-compose.yml**

### Archivo .env.docker para Docker
```bash
# Copia de .env.docker.example y configura:
FLASK_ENV=production
SECRET_KEY=tu_clave_secreta_aqui
JWT_SECRET_KEY=tu_jwt_secret_aqui
# ⚠️  NOTA: Las variables DB_* están HARDCODEADAS en docker-compose.yml
# MySQL: root/(vacía)/gestion_ganadera - NO se usan las variables DB_* de este archivo
ROOT_SUPER_ADMIN_EMAIL=superadmin@qrfarm.com
ROOT_SUPER_ADMIN_PASSWORD=tu_contraseña_segura_aqui
ROOT_SUPER_ADMIN_NOMBRE=Super Administrador QR-Farm
```

**Nota:** Para generar una clave segura para JWT, ejecuta el siguiente comando y reemplaza `tu_jwt_secret_aqui` con el resultado:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Instrucciones de Instalación con Docker

### 1. Preparar Variables de Entorno

```bash
cp .env.docker .env
# El archivo .env.docker ya tiene todas las configuraciones necesarias
# Las variables DB_* están hardcodeadas en docker-compose.yml para consistencia
```



**Nota:** Si has hecho cambios en los Dockerfiles (como la instalación de mysql-client), usa `--build` para reconstruir las imágenes.

### 2. Iniciar Todos los Servicios

**¡Ahora es completamente automático!** Solo ejecuta:

```bash
# Corregir finales de línea en entrypoint.sh
# Esto es necesario para que el script funcione correctamente en Windows ejecutalo antes de construir los contenedores (en consola de wsl)
sed -i 's/\r$//' backend/entrypoint.sh

# Construir los servicios
docker compose build

# iniciar todos los servicios
docker compose up -d

```

**Lo que sucede automáticamente:**
1. ✅ MySQL se inicia y espera conexiones
2. ✅ Backend espera a que MySQL esté listo (usando mysqladmin con verificación robusta)
3. ✅ Se ejecutan las migraciones de Alembic automáticamente
4. ✅ Se inicializa el super admin desde variables del .env
5. ✅ Se inicia la aplicación Flask sin errores de Werkzeug
6. ✅ Frontend se conecta al backend

### 3. Acceder a la Aplicación

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

### Error "Table doesn't exist"
Asegúrate de ejecutar las migraciones antes de iniciar el backend:
```bash
docker-compose up -d mysql
docker-compose exec backend flask db upgrade
docker-compose up -d backend frontend
```

### Error "No se encontró el archivo .env"
Reconstruye las imágenes del backend:
```bash
docker-compose build backend
docker-compose up -d backend
```

### Error Werkzeug en producción
Ya está corregido en el código, pero si persiste, verifica que uses `--build`.

## 🎯 Después de la Instalación

### Credenciales de Acceso

**Super Administrador (creado automáticamente):**
- **Email**: `superadmin@qrfarm.com`
- **Contraseña**: `tu_contraseña_segura`

### Verificación de Funcionamiento

1. **Accede al frontend**: http://localhost
2. **Haz login** con las credenciales arriba
3. **Verifica la API**: http://localhost:5000/api/health
4. **Revisa logs**: `docker-compose logs -f`

### Próximos Pasos

- **Para desarrollo**: Modifica código y reconstruye con `docker-compose up --build`
- **Para producción**: Configura dominios, HTTPS, y escalado
- **Para equipo**: Comparte el repositorio (sin archivos .env)

## Reconstrucción Después de Cambios en el Código

### Cómo Funciona Docker en el Proyecto

En QR-Farm, los contenedores están configurados para producción, lo que significa que el código fuente se copia en las imágenes durante la construcción. Los cambios en el código no se reflejan automáticamente en los contenedores en ejecución. Para ver los cambios, es necesario reconstruir las imágenes y reiniciar los contenedores.

- **Backend**: Ejecuta la API REST en el puerto 5000.
- **Frontend**: Sirve la interfaz de usuario en el puerto 80 usando Nginx.
- **Base de datos MySQL**: Corre en su propio contenedor con persistencia en un volumen dedicado.

### Pasos para Reconstruir y Levantar Contenedores

Después de hacer cambios en el código del backend o frontend, sigue estos pasos:

1. **Reconstruir la imagen del backend**:
   ```bash
   docker-compose build backend
   ```
   *Explicación*: Este comando reconstruye la imagen del backend con los últimos cambios en el código fuente.

2. **Reconstruir la imagen del frontend**:
   ```bash
   docker-compose build frontend
   ```
   *Explicación*: Este comando reconstruye la imagen del frontend con los últimos cambios en el código fuente.

3. **Levantar el contenedor del backend**:
   ```bash
   docker-compose up -d backend
   ```
   *Explicación*: Este comando inicia o reinicia el contenedor del backend en segundo plano con la nueva imagen.

4. **Levantar el contenedor del frontend**:
   ```bash
   docker-compose up -d frontend
   ```
   *Explicación*: Este comando inicia o reinicia el contenedor del frontend en segundo plano con la nueva imagen.

### Buenas Prácticas

- Cada desarrollador debe ejecutar estos comandos manualmente después de hacer `git pull` para ver los cambios en su entorno local.
- No automatizar la reconstrucción con hooks de pre-pull, ya que podría romper entornos de desarrollo o causar conflictos.
- Mantén el archivo `.env` seguro y nunca subas credenciales sensibles al repositorio.

Sigue estos pasos paso a paso para asegurar que tus cambios se vean reflejados en la aplicación Docker.

## Ejecutar Migraciones de Alembic

### 🔄 Migraciones desde Docker (Automático)

Las migraciones se ejecutan automáticamente cuando el contenedor del backend inicia, gracias al script `entrypoint.sh`. No necesitas hacer nada adicional.

### 💻 Migraciones desde Windows (Desarrollo Local)

Si necesitas ejecutar migraciones manualmente desde Windows (fuera de Docker), el sistema ahora detecta automáticamente el entorno y usa la configuración correcta.

#### Opción 1: Usar el Script PowerShell (Recomendado)

```powershell
cd backend
.\run-migrations.ps1
```

Este script:
- ✅ Detecta automáticamente si MySQL está corriendo en Docker
- ✅ Configura las variables de entorno necesarias
- ✅ Inicia MySQL si no está corriendo
- ✅ Ejecuta las migraciones

#### Opción 2: Configuración Manual

Si prefieres configurar las variables manualmente:

```powershell
cd backend
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD=""
$env:DB_NAME="gestion_ganadera"
$env:DB_PORT="3306"
alembic -c alembic.ini upgrade head
```

#### Opción 3: Usar Archivo .env

Si tienes un archivo `.env` en la raíz del proyecto con las variables configuradas, simplemente ejecuta:

```powershell
cd backend
alembic -c alembic.ini upgrade head
```

El sistema cargará automáticamente las variables desde el archivo `.env`.

### 🐧 Migraciones desde Linux/Mac

```bash
cd backend
chmod +x run-migrations.sh
./run-migrations.sh
```

O manualmente:

```bash
cd backend
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=""
export DB_NAME=gestion_ganadera
export DB_PORT=3306
alembic -c alembic.ini upgrade head
```

### ⚙️ Cómo Funciona

El archivo `backend/src/database/migrations/env.py` ha sido modificado para:

1. **Cargar variables desde `.env`**: Si existe un archivo `.env` en la raíz del proyecto, lo carga automáticamente
2. **Usar variables de entorno**: Prioriza las variables de entorno del sistema
3. **Valores por defecto**: Si no hay configuración, usa valores seguros para desarrollo local
4. **Detección automática**: Funciona tanto desde Docker (`DB_HOST=mysql`) como desde Windows/Linux (`DB_HOST=localhost`)

### 🔧 Solución de Problemas

**Error: "Unknown MySQL server host 'mysql'"**
- ✅ **Solucionado**: El sistema ahora detecta automáticamente el entorno
- Si persiste, verifica que MySQL esté corriendo: `docker-compose up -d mysql`

**Error: "Can't connect to MySQL server"**
- Verifica que MySQL esté corriendo: `docker ps | grep mysql`
- Verifica el puerto: `docker-compose ps`
- Revisa las credenciales en tu archivo `.env`

## Optimizaciones para Producción

- Cambia `SECRET_KEY` y contraseñas en `.env`
- Configura HTTPS con Nginx (certbot + Let's Encrypt)
- Usa Docker Swarm o Kubernetes para escalado
- Configura backups automáticos de la base de datos
- Implementa monitoring (Prometheus + Grafana)
- Configura logs centralizados (ELK stack)

---

## 📞 Soporte

Si encuentras problemas:

1. **Revisa logs**: `docker-compose logs -f`
2. **Verifica estado**: `docker-compose ps`
3. **Reinicia servicios**: `docker-compose restart`
4. **Reconstruye**: `docker-compose up --build -d`

**¡Tu aplicación QR-Farm está lista para usar!** 🎉