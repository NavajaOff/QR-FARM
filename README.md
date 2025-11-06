# 🐄 QR-FARM - Sistema de Gestión Ganadera

Sistema integral de gestión ganadera basado en códigos QR para el seguimiento y control del ganado.

## 📋 Descripción

QR-FARM es una aplicación web moderna que permite gestionar de manera eficiente una granja ganadera mediante el uso de códigos QR. Cada animal tiene un código QR único que permite acceder rápidamente a toda su información.

## 🏗️ Arquitectura

- **Backend**: Flask (Python) - API REST con autenticación JWT
- **Frontend**: Vue.js 3 con Vite - SPA reactiva
- **Base de Datos**: MySQL
- **Comunicación en tiempo real**: Socket.IO
- **Arquitectura**: MVC (Model-View-Controller)

## ✨ Características Principales

- 🔐 **Autenticación segura** con JWT y contraseñas hasheadas (bcrypt)
- 👥 **Gestión de usuarios** con roles (admin, user, veterinario, supervisor)
- 🐮 **Gestión de ganado** con códigos QR únicos
- 🌾 **Gestión de potreros** y tipos de pasto
- 💉 **Control de vacunación** y salud del ganado
- 📊 **Dashboard** con estadísticas en tiempo real
- 🔄 **Actualizaciones en tiempo real** con WebSockets
- 📱 **Diseño responsive** para móviles y tablets

## 🚀 Instalación Rápida

### Prerrequisitos

- Python 3.8+
- Node.js 16+
- MySQL 5.7+
- Git

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/QR-FARM.git
cd QR-FARM
```

### Paso 2: Configurar el archivo .env

Copia el archivo de ejemplo y configura tus variables:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus configuraciones:

```env
# Configuración del entorno Flask
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta_aqui
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost/qr_farm

# Configuración de la base de datos MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=gestion_ganadera
DB_USER=root
DB_PASSWORD=tu_contraseña_mysql

# Credenciales para el usuario admin (se crean automáticamente)
ADMIN_EMAIL=admin@qrfarm.com
ADMIN_PASSWORD=admin123
```

### Paso 3: Instalar dependencias

#### Backend (Python)
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend (Node.js)
```bash
cd frontend
npm install
```

### Paso 4: Configurar la base de datos

#### Crear la base de datos
```sql
CREATE DATABASE gestion_ganadera CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Ejecutar migraciones
```bash
# Desde la raíz del proyecto
flask --app backend/app.py db upgrade -d backend/src/database/migrations
```

#### Cargar datos iniciales (seeders)
```bash
python backend/src/database/seeders/seeder_manager.py
```

### Paso 5: Ejecutar el proyecto

#### Opción 1: Ejecutar todo junto (Recomendado)
```bash
python backend/run_all.py
```

#### Opción 2: Ejecutar por separado

Terminal 1 - Backend:
```bash
cd backend
python app.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

## 🌐 Acceso al Sistema

- **Frontend**: http://localhost:5173 (o el puerto que se asigne)
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

### Credenciales por defecto

```
Email: admin@qrfarm.com
Contraseña: admin123
```

## 📁 Estructura del Proyecto

```
QR-FARM/
│
├── backend/                    # Servidor Flask
│   ├── app.py                 # Aplicación principal
│   ├── run_all.py            # Script para ejecutar todo
│   ├── requirements.txt      # Dependencias Python
│   └── src/
│       ├── controllers/      # Controladores MVC
│       ├── models/           # Modelos de datos
│       ├── services/         # Lógica de negocio
│       ├── routes/           # Rutas de la API
│       ├── database/         # Configuración BD
│       │   ├── migrations/   # Migraciones de BD
│       │   └── seeders/      # Datos iniciales
│       └── utils/            # Utilidades
│
├── frontend/                  # Cliente Vue.js
│   ├── src/
│   │   ├── views/           # Vistas/Páginas
│   │   ├── components/      # Componentes
│   │   ├── composables/     # Composables Vue
│   │   ├── services/        # Servicios API
│   │   ├── router/          # Rutas Vue
│   │   └── assets/          # Recursos estáticos
│   ├── package.json         # Dependencias Node
│   └── vite.config.js       # Configuración Vite
│
├── .env                     # Variables de entorno (no subir)
├── .env.example            # Ejemplo de variables
├── README.md               # Este archivo
└── README_MIGRATIONS.md    # Guía de migraciones
```

## 🛠️ Comandos Útiles

### Backend

```bash
# Crear nueva migración
flask --app backend/app.py db migrate -m "Descripción del cambio"

# Aplicar migraciones
flask --app backend/app.py db upgrade -d backend/src/database/migrations

# Revertir última migración
flask --app backend/app.py db downgrade -d backend/src/database/migrations

# Ejecutar seeders
python backend/src/database/seeders/seeder_manager.py

# Resetear y recargar seeders
python backend/src/database/seeders/seeder_manager.py --reset
```

### Frontend

```bash
# Desarrollo
npm run dev

# Compilar para producción
npm run build

# Vista previa de producción
npm run preview

# Linter
npm run lint
```

## 🔧 Configuración Avanzada

### Migraciones de Base de Datos

Las migraciones se gestionan con Flask-Migrate (Alembic). Ver [README_MIGRATIONS.md](README_MIGRATIONS.md) para más detalles.

### Seeders

Los seeders cargan datos iniciales necesarios para el funcionamiento del sistema:
- Roles de usuario
- Tipos de pasto
- Tipos de vacunas
- Estados del ganado

### Sistema de Autenticación

- Contraseñas hasheadas con bcrypt
- Tokens JWT con expiración de 24 horas
- Middleware de autenticación en rutas protegidas
- Roles y permisos por usuario

## 📊 API Endpoints Principales

### Autenticación
- `POST /api/usuarios/login` - Iniciar sesión
- `POST /api/usuarios/register` - Registrar usuario

### Usuarios
- `GET /api/usuarios/` - Listar usuarios
- `GET /api/usuarios/:id` - Obtener usuario
- `PUT /api/usuarios/:id` - Actualizar usuario
- `DELETE /api/usuarios/:id` - Eliminar usuario

### Ganado
- `GET /api/animales/` - Listar animales
- `POST /api/animales/` - Crear animal
- `GET /api/animales/:id` - Obtener animal
- `PUT /api/animales/:id` - Actualizar animal
- `DELETE /api/animales/:id` - Eliminar animal

### Potreros
- `GET /api/potreros/` - Listar potreros
- `POST /api/potreros/` - Crear potrero
- `GET /api/potreros/:id` - Obtener potrero
- `PUT /api/potreros/:id` - Actualizar potrero
- `DELETE /api/potreros/:id` - Eliminar potrero

### Vacunación
- `GET /api/vacunaciones/` - Listar vacunaciones
- `POST /api/vacunaciones/` - Registrar vacunación
- `GET /api/vacunaciones/animal/:id` - Historial por animal

## 🐛 Solución de Problemas

### Error de conexión a MySQL
```bash
# Verificar que MySQL esté ejecutándose
mysql -u root -p

# Verificar credenciales en .env
```

### Error de módulos Python
```bash
# Reinstalar dependencias
pip install -r backend/requirements.txt
```

### Error de módulos Node
```bash
# Limpiar caché y reinstalar
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Puerto en uso
```bash
# El sistema busca automáticamente puertos libres
# O puedes especificar manualmente en .env
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Equipo

- **Desarrollo Backend**: Equipo Flask
- **Desarrollo Frontend**: Equipo Vue.js
- **Base de Datos**: Equipo MySQL
- **DevOps**: Equipo de Infraestructura

## 📞 Soporte

Para soporte, envía un email a soporte@qrfarm.com o abre un issue en GitHub.

---

**QR-FARM** - *Transformando la gestión ganadera con tecnología* 🐄🚀