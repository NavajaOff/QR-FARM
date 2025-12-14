# 🐄 QR-FARM

**Sistema Integral de Gestión Ganadera**

QR-FARM es una plataforma web completa para la administración de explotaciones ganaderas, con soporte multi-tenant, códigos QR para identificación de animales, gestión de vacunaciones, potreros y reportes en tiempo real.

---

## 👥 Equipo de Desarrollo

Este proyecto fue desarrollado por:
- **Juan David Castro Villarreal**
- **Jose David Hernandez Navaja**
- **Ronald Bejarano Barbosa**

---

## 📋 Descripción General

QR-FARM es una solución tecnológica que permite gestionar de manera eficiente:

- **Gestión de Animales**: Registro, seguimiento e identificación mediante códigos QR
- **Gestión de Potreros**: Administración de espacios y sus actividades
- **Control de Vacunaciones**: Registro y alertas de próximas dosis
- **Sistema Multi-Tenant**: Aislamiento de datos por organización (tenant)
- **Notificaciones**: Alertas de limpieza, vacunaciones y solicitudes pendientes
- **Reportes**: Generación de reportes PDF de ganado y vacunaciones
- **Escáner QR**: Lectura de códigos QR con soporte offline
- **Recuperación de Contraseñas**: Sistema seguro de recuperación por token con email 

---

## 🚀 Instalación y Configuración

Este proyecto puede ejecutarse de **dos formas**. Elige la que mejor se adapte a tus necesidades:

### 📋 Opción A: Docker (Recomendado para producción/demos)

**Recomendado para: producción, demos o entornos institucionales**

La forma más rápida y sencilla de ejecutar el proyecto es usando Docker. Consulta el archivo **[`README_DOCKER.md`](README_DOCKER.md)** para instrucciones completas.

**Inicio rápido con Docker:**

```bash
# 1. Copiar configuración
cp .env.example .env
# Editar .env con tus valores

# 2. Deshabilitar BuildKit (recomendado para estabilidad)
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

# 3. Construir e iniciar
docker compose build
docker compose up -d

# 4. Acceder
# Frontend: http://localhost:5174
# Backend: http://localhost:5010
```

**Ventajas de Docker:**
- ✅ Configuración automática de todos los servicios
- ✅ Sin necesidad de instalar Python, MySQL o Node.js localmente
- ✅ Entorno aislado y reproducible
- ✅ Base de datos MySQL incluida
- ✅ Migraciones automáticas al iniciar

**Documentación completa:** Consulta **[`README_DOCKER.md`](README_DOCKER.md)** para:
- Instrucciones paso a paso detalladas
- Solución de problemas específicos
- Optimizaciones para producción

---

### 📋 Opción B: Desarrollo Local (Recomendado para desarrollo activo)

**Recomendado para: desarrollo activo y debugging**

Si prefieres ejecutar el proyecto en tu máquina local, sigue estos pasos:

#### Requisitos Previos
- **Python 3.11+**
- **MySQL 8.0+** (o MariaDB)
- **Node.js 18+**
- **npm** o **yarn**
- **Git**

#### Paso 1: Clonar el Repositorio

#### Paso 2: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
# Usa tu editor preferido (nano, vim, notepad, etc.)
```

**Configuración mínima requerida en `.env`:**

```env
# Flask
FLASK_ENV=development
DEBUG=True
SECRET_KEY=genera_una_clave_segura_aqui
FLASK_APP=app.py

# Base de Datos
DB_HOST=localhost
DB_PORT=3306
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_password_mysql
DB_NAME=gestion_ganadera


# Frontend
VITE_BACKEND_URL=http://localhost:5000

# Super Admin
ROOT_SUPER_ADMIN_EMAIL=correo_admin_aqui
ROOT_SUPER_ADMIN_PASSWORD=tu_contraseña_segura
ROOT_SUPER_ADMIN_NOMBRE=Super Administrador QR-Farm

# JWT
JWT_SECRET_KEY=genera_otra_clave_segura_aqui
```

**Generar claves seguras:**

```bash
# Generar SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Generar JWT_SECRET_KEY
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
```

#### Paso 3: Crear Base de Datos MySQL

```sql
-- Ejecutar en MySQL Workbench o terminal MySQL
CREATE DATABASE gestion_ganadera CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


#### Paso 4: Configurar Backend

```bash
cd backend

# Instalar dependencias
pip install -r requirements.txt
```

#### Paso 5: Ejecutar Migraciones

```bash
# Desde el directorio backend/
alembic -c alembic.ini upgrade head
```

Esto creará todas las tablas necesarias en la base de datos.

#### Paso 6: Configurar Frontend

```bash
# Desde la raíz del proyecto
cd frontend
npm install
```

#### Paso 7: Iniciar Servicios

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```
✅ Backend disponible en la ruta que te dio al iniciar el comando

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
✅ Frontend disponible en la ruta que te dio al iniciar el comando

#### Paso 8: Verificar Instalación

1. Accede al frontend
2. Inicia sesión con las credenciales del super admin definidas en `.env`


---

## 🏗️ Arquitectura del Proyecto

### Stack Tecnológico

**Backend:**
- **Flask 3.1.2** - Framework web Python
- **SQLAlchemy 2.0.45** - ORM para base de datos
- **Alembic** - Sistema de migraciones
- **MySQL 8.0+** - Base de datos relacional
- **Flask-SocketIO 5.5.1** - WebSockets para actualizaciones en tiempo real
- **PyJWT 2.10.1** - Autenticación JWT
- **ReportLab 4.4.6** - Generación de reportes PDF
- **qrcode[pil]** - Generación de códigos QR
- **python-dotenv** - Gestión de variables de entorno

**Frontend:**
- **Vue 3.5.18** - Framework JavaScript progresivo
- **Vite 7.2.2** - Build tool y dev server
- **Vue Router 4.5.1** - Enrutamiento
- **Axios 1.13.0** - Cliente HTTP
- **Socket.io-client 4.7.5** - Cliente WebSocket
- **Bootstrap 5.3.8** - Framework CSS
- **html5-qrcode 2.3.8** - Escáner de códigos QR
- **SweetAlert2 11.23.0** - Alertas y modales
- **Chart.js 4.4.4** - Gráficos y visualizaciones

**Base de Datos:**
- **MySQL 8.0+** - Motor de base de datos
- **Alembic** - Sistema de migraciones versionadas

**Infraestructura:**
- **Docker & Docker Compose** - Containerización (opcional)
- **Nginx** - Servidor web para producción (frontend)

### Estructura del Proyecto

```
QR-FARM/
├── backend/                    # Backend Flask
│   ├── src/
│   │   ├── controllers/        # Controladores HTTP
│   │   ├── services/           # Lógica de negocio
│   │   ├── models/             # Modelos de datos
│   │   ├── routes/             # Definición de rutas (Blueprints)
│   │   ├── database/           # Conexión y migraciones
│   │   │   └── migrations/     # Migraciones Alembic
│   │   ├── utils/              # Utilidades (auth, tenant, etc.)
│   │   └── cli/                # Comandos CLI
│   ├── alembic.ini             # Configuración de Alembic
│   ├── requirements.txt        # Dependencias Python
│   ├── entrypoint.sh           # Script de inicio (Docker)
│   └── app.py                  # Aplicación Flask principal
├── frontend/                   # Frontend Vue 3
│   ├── src/
│   │   ├── views/              # Vistas/páginas
│   │   ├── components/         # Componentes reutilizables
│   │   ├── composables/        # Composables Vue
│   │   ├── services/           # Servicios API
│   │   ├── layouts/            # Layouts
│   │   └── router/             # Configuración de rutas
│   ├── package.json            # Dependencias Node.js
│   └── vite.config.js          # Configuración de Vite
├── docker-compose.yml          # Configuración Docker Compose
├── Dockerfile.backend          # Imagen Docker del backend
├── Dockerfile.frontend         # Imagen Docker del frontend
├── .env.example                # Plantilla de variables de entorno
├── README.md                   # Este archivo
└── README_DOCKER.md            # Documentación específica de Docker
```

### Patrón de Arquitectura

El proyecto sigue una **arquitectura en capas**:

1. **Capa de Presentación** (Frontend Vue 3)
   - Vistas y componentes
   - Composables para lógica reactiva
   - Servicios API

2. **Capa de API** (Backend Flask)
   - Rutas (Blueprints)
   - Middleware (autenticación, tenant, permisos)

3. **Capa de Controladores**
   - Orquestación de peticiones HTTP
   - Validación de entrada
   - Formateo de respuestas JSON
   - Emisión de eventos WebSocket

4. **Capa de Servicios**
   - Lógica de negocio
   - Validaciones del dominio
   - Aislamiento multi-tenant
   - Transformación de datos

5. **Capa de Modelos**
   - Entidades de dominio
   - Validaciones
   - Métodos de transformación

6. **Capa de Base de Datos**
   - Conexiones MySQL
   - Migraciones Alembic
   - Seeders cifrados

---

## 🔐 Autenticación y Seguridad

### Sistema de Autenticación JWT

- **Endpoint de Login**: `POST /api/usuarios/login`
- **Tokens JWT** incluyen: `user_id`, `email`, `role`, `tenant_id`, `exp`
- **Decorador `@token_required`**: Valida tokens y asegura usuarios activos
- **CORS configurable**: Mediante variable de entorno `CORS_ORIGINS`

### Roles y Permisos

- **Super Admin**: Acceso completo, gestión de tenants
- **Admin**: Gestión completa dentro de su tenant
- **Usuario**: Acceso limitado según permisos dentro de su tenant

### Super Administrador

El super administrador se crea automáticamente desde variables de entorno:

```env
ROOT_SUPER_ADMIN_EMAIL=correo_super_admin
ROOT_SUPER_ADMIN_PASSWORD=tu_contraseña_segura_aqui
ROOT_SUPER_ADMIN_NOMBRE=Super Administrador QR-Farm
```

**Características:**
- ✅ Solo puede crearse desde variables de entorno (no desde la API)
- ✅ Se inicializa automáticamente al iniciar el backend
- ✅ Bloqueo de creación desde la API
- ✅ Gestión multi-tenant global

### Recuperación de Contraseñas

Sistema seguro de recuperación mediante tokens temporales enviados por email:
- Tokens con expiración configurable
- Validación de estado antes de reset
- Cambio seguro de contraseña con hash bcrypt

---

## 🏢 Sistema Multi-Tenant

El sistema implementa **aislamiento completo de datos por tenant**:

- Cada organización tiene su propio tenant con datos aislados
- Los usuarios solo ven datos de su tenant asignado
- El super admin puede ver todos los tenants o filtrar por uno específico
- Aislamiento basado en `tenant_id` en la tabla `personas`

### Gestión de Tenants

- **Crear tenants**: Solo super admin
- **Asignar usuarios**: Los usuarios pertenecen a un tenant específico
- **Selector de tenant**: Super admin puede cambiar contexto de visualización

---

## ⚡ Funcionalidades Principales

### 1. Gestión de Usuarios
- ✅ CRUD completo de usuarios
- ✅ Activación/desactivación
- ✅ Asignación de roles y tenants
- ✅ Sincronización en tiempo real vía WebSocket
- ✅ Bloqueo de creación de super_admin desde API

### 2. Gestión de Animales (Ganado)
- ✅ Registro completo con información detallada
- ✅ Generación de códigos QR únicos
- ✅ Actualización de QR al modificar datos
- ✅ Historial de cambios
- ✅ Estados: activo, vendido, muerto, baja
- ✅ Relación con potreros y propietarios

### 3. Gestión de Potreros
- ✅ CRUD completo de potreros
- ✅ Control de capacidad y ocupación
- ✅ Historial de actividades (limpieza, mantenimiento)
- ✅ Alertas de limpieza próxima (7 días)
- ✅ Relación con animales asignados

### 4. Control de Vacunaciones
- ✅ Registro de vacunaciones por animal
- ✅ Control de dosis y fechas
- ✅ Alertas de próximas vacunaciones (7 días)
- ✅ Historial completo de vacunaciones
- ✅ Filtrado por animal, tipo y fecha

### 5. Códigos QR
- ✅ Generación automática de QR al crear animal
- ✅ QR con payload JSON embebido (`schema: qr-farm.v1`)
- ✅ Datos incluidos: ID, nombre, propietario, potrero, estado, URL
- ✅ Soporte offline (datos en el QR)
- ✅ Escáner con cámara o imagen
- ✅ Compatibilidad con QR antiguos

### 6. Escáner QR
- ✅ Componente reutilizable `QrScanner.vue`
- ✅ Activación de cámara del dispositivo
- ✅ Detección mediante `html5-qrcode`
- ✅ Modo offline con datos embebidos
- ✅ Tarjeta detallada del ganado con pestañas
- ✅ Sincronización automática cuando hay conexión

### 7. Notificaciones
- ✅ Alertas de limpieza de potreros próximas
- ✅ Alertas de vacunaciones próximas
- ✅ Solicitudes de recuperación de contraseña pendientes
- ✅ Integración en layout administrativo con campana
- ✅ Filtrado por tenant

### 8. Reportes
- ✅ Reporte de ganado (PDF)
- ✅ Reporte de vacunaciones (PDF)
- ✅ Generación con ReportLab
- ✅ Descarga directa desde la interfaz

### 9. Auditoría
- ✅ Historial de cambios en animales
- ✅ Registro de actividades en potreros
- ✅ Trazabilidad de modificaciones

---

## 🛠️ Comandos Útiles

### Backend

```bash
cd backend

# Iniciar servidor de desarrollo
python app.py

# Ejecutar migraciones
alembic -c alembic.ini upgrade head

# Crear nueva migración
alembic -c alembic.ini revision --autogenerate -m "descripción"

# Generar SECRET_KEY
flask --app app generate-secret-key

# Exportar seeders cifrados
flask --app app seed:secure_export

# Importar seeders cifrados
flask --app app seed:secure_import

# Generar TEAM_KEY para seeders
flask --app app team:generate_key



### Frontend

```bash
cd frontend

# Desarrollo con hot reload
npm run dev

# Build para producción
npm run build

# Vista previa del build
npm run preview

# Ejecutar tests
npm test





## 🔄 Migraciones y Base de Datos

### Sistema de Migraciones con Alembic

El proyecto usa **Alembic** directamente (no Flask-Migrate CLI) para gestionar el esquema de base de datos.

**Comandos principales:**

```bash
# Aplicar todas las migraciones pendientes
alembic -c alembic.ini upgrade head

# Ver estado de migraciones
alembic -c alembic.ini current

# Crear nueva migración (después de modificar modelos)
alembic -c alembic.ini revision --autogenerate -m "descripción del cambio"

# Revertir última migración
alembic -c alembic.ini downgrade -1
```

### Seeders Cifrados (Opcional)

Para compartir datos iniciales de forma segura entre el equipo:

```bash
# 1. Generar TEAM_KEY (solo el líder del equipo)
flask --app app team:generate_key

# 2. Compartir TEAM_KEY por canal seguro
# Cada integrante la agrega a su .env

# 3. Exportar datos (después de poblar la BD localmente)
flask --app app seed:secure_export
# Genera: backend/src/database/seeders/secure_seed.bin

# 4. Importar datos (en otras máquinas)
flask --app app seed:secure_import
```

---

## 📡 API REST

### Endpoints Principales

**Autenticación:**
- `POST /api/usuarios/login` - Iniciar sesión

**Usuarios:**
- `GET /api/usuarios` - Listar usuarios
- `POST /api/usuarios` - Crear usuario
- `GET /api/usuarios/{id}` - Obtener usuario
- `PUT /api/usuarios/{id}` - Actualizar usuario
- `DELETE /api/usuarios/{id}` - Eliminar usuario (lógico)

**Animales:**
- `GET /api/ganado` - Listar animales
- `POST /api/ganado` - Crear animal
- `GET /api/ganado/{id}` - Obtener animal
- `PUT /api/ganado/{id}` - Actualizar animal
- `DELETE /api/ganado/{id}` - Eliminar animal (lógico)

**Potreros:**
- `GET /api/potreros` - Listar potreros
- `POST /api/potreros` - Crear potrero
- `PUT /api/potreros/{id}` - Actualizar potrero
- `DELETE /api/potreros/{id}` - Eliminar potrero

**Vacunaciones:**
- `GET /api/vacunaciones` - Listar vacunaciones
- `POST /api/vacunaciones` - Crear vacunación
- `PUT /api/vacunaciones/{id}` - Actualizar vacunación
- `DELETE /api/vacunaciones/{id}` - Eliminar vacunación

**Tenants:**
- `GET /api/tenants` - Listar tenants (solo super admin)
- `POST /api/tenants` - Crear tenant (solo super admin)
- `GET /api/tenants/{id}` - Obtener tenant

**Notificaciones:**
- `GET /api/notificaciones/proximas` - Obtener alertas próximas

**Reportes:**
- `GET /api/reportes/ganado` - Generar reporte de ganado (PDF)
- `GET /api/reportes/vacunaciones` - Generar reporte de vacunaciones (PDF)

**Recuperación:**
- `POST /api/recovery/solicitar` - Solicitar recuperación de contraseña
- `POST /api/recovery/reset` - Resetear contraseña con token

### Autenticación

Todas las rutas protegidas requieren un token JWT en el header:

```
Authorization: Bearer <token>
```

---

## 🧪 Testing

### Backend (pytest)

```bash
cd backend

# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=src tests/

# Test específico
pytest tests/test_usuario_service.py

# Verbose
pytest -v
```

### Frontend (Vitest)

```bash
cd frontend

# Ejecutar tests
npm test

# Tests con cobertura
npm run test:coverage

# Watch mode
npm test -- --watch
```

---

## 🐛 Solución de Problemas

### Error: "Can't connect to MySQL server"

**Solución:**
- Verifica que MySQL esté ejecutándose
- Confirma las credenciales en `.env`
- Asegúrate de que la base de datos existe
- Verifica que el usuario tenga permisos

### Error: "SECRET_KEY not found"

**Solución:**
```bash
cd backend
flask --app app generate-secret-key
# O genera manualmente y agrega a .env
```

### Error: "Module not found" en frontend

**Solución:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Error: "Alembic no encuentra migraciones"

**Solución:**
```bash
cd backend
# Verificar que alembic.ini apunta al directorio correcto
alembic -c alembic.ini current
alembic -c alembic.ini upgrade head
```

### Error: "CORS_ORIGINS debe estar configurado"

**Solución:**
En desarrollo, puedes dejar `CORS_ORIGINS` vacío o configurar:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

### Problemas con Docker

Consulta la sección de solución de problemas en [`README_DOCKER.md`](README_DOCKER.md).

---

## 📚 Documentación Adicional

- **[README_DOCKER.md](README_DOCKER.md)** - Guía completa de Docker
- **[docs/diagrama-capas-detallado.md](docs/diagrama-capas-detallado.md)** - Arquitectura detallada
- **[backend/MIGRACION_ESQUEMA_ERD.md](backend/MIGRACION_ESQUEMA_ERD.md)** - Esquema de base de datos

---

## 🔒 Seguridad

### Buenas Prácticas Implementadas

- ✅ Contraseñas hasheadas con bcrypt
- ✅ Tokens JWT con expiración
- ✅ Validación de entrada en todos los endpoints
- ✅ Aislamiento multi-tenant estricto
- ✅ CORS configurable
- ✅ Variables de entorno para secretos
- ✅ Protección contra inyección SQL (usando parámetros)
- ✅ Tokens de recuperación con expiración

### Checklist de Seguridad para Producción

Antes de desplegar en producción, verifica:

- [ ] Cambiar todas las claves secretas (`SECRET_KEY`, `JWT_SECRET_KEY`)
- [ ] Configurar contraseña segura para MySQL (`DB_PASSWORD`)
- [ ] Configurar `CORS_ORIGINS` solo con dominios de producción (HTTPS)
- [ ] Cambiar contraseña del super admin
- [ ] Configurar `DEBUG=False`
- [ ] Configurar `FLASK_ENV=production`
- [ ] Usar HTTPS en producción
- [ ] Configurar firewall adecuado
- [ ] Revisar permisos de archivos y directorios
- [ ] Asegurar que `.env` NO esté en el repositorio (verificar `.gitignore`)

---

## 🚧 Próximos Pasos

Mejoras planificadas:

- [ ] Tests de integración más completos
- [ ] Documentación de API con Swagger/OpenAPI
- [ ] Dashboard con métricas y estadísticas
- [ ] Exportación de datos a Excel/CSV
- [ ] Notificaciones por email
- [ ] App móvil (React Native)
- [ ] Sincronización offline mejorada
- [ ] Más tipos de reportes

---

## 📄 Licencia

Este proyecto fue desarrollado como parte de un proyecto académico/institucional.

---

## 👨‍💻 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📞 Soporte

Para reportar problemas o solicitar ayuda:

1. Revisa la documentación
2. Consulta los issues existentes
3. Crea un nuevo issue con detalles del problema

---

**Última actualización:** Diciembre 2025
