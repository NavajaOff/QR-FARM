# Instrucciones de Despliegue - QR-FARM

## Requisitos Previos

### Sistema Operativo
- Windows 10/11 con WSL2 (recomendado) o Windows nativo
- Linux/macOS (compatible)

### Software Requerido
- Python 3.12+
- Node.js 18+
- MySQL 8.0+
- Git

## Configuración del Entorno

### 1. Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd qr-farm
Crear archivo `.env` en la raíz del proyecto:
```env
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_password_mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=gestion_ganadera
```

### 3. Instalar Dependencias del Backend

#### Python y Librerías
```bash
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Instalar dependencias
pip install -r requirements.txt
```

#### Verificar Instalación
```bash
python -c "import flask, flask_socketio; print('Backend dependencies OK')"
```

### 4. Instalar Dependencias del Frontend
```bash
cd ../frontend

# Instalar dependencias de Node.js
npm install

# Verificar socket.io-client
npm list socket.io-client
```

### 5. Configurar Base de Datos MySQL

#### Crear Base de Datos
```sql
CREATE DATABASE gestion_ganadera CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Ejecutar Migraciones
```bash
cd backend
python manage_db.py upgrade
```

#### Verificar Datos Iniciales
```sql
USE gestion_ganadera;
SELECT * FROM roles;
SELECT * FROM estado_ganado;
SELECT * FROM tipo_vacuna;
SELECT * FROM usuarios;
```

## Despliegue

### Opción 1: Despliegue de Desarrollo

#### Backend
```bash
cd backend
python app.py
# O usando el script de inicio
python ../iniciar_qrfarm.py
```

#### Frontend
```bash
cd frontend
npm run dev
```

### Opción 2: Despliegue con Docker (Recomendado para Producción)

#### Crear Dockerfile para Backend
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

#### Crear Dockerfile para Frontend
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json .
RUN npm install

COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: gestion_ganadera
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  backend:
    build: ./backend
    environment:
      DB_HOST: mysql
      DB_USER: root
      DB_PASSWORD: rootpassword
      DB_NAME: gestion_ganadera
    ports:
      - "5000:5000"
    depends_on:
      - mysql

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend

volumes:
  mysql_data:
```

## Verificación del Despliegue

### Endpoints Principales
```bash
# Health check
curl http://localhost:5000/api/health

# Lista de animales
curl http://localhost:5000/api/animales/

# Lista de potreros
curl http://localhost:5000/api/potreros/

# Estados de ganado
curl http://localhost:5000/api/animales/estados-ganado

# Login (requiere token JWT para otros endpoints)
curl -X POST http://localhost:5000/api/usuarios/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@qrfarm.com","password":"admin123"}'
```

### WebSockets
- URL: `ws://localhost:5000/socket.io`
- Eventos disponibles:
  - `animal_created`
  - `animal_updated`
  - `potrero_created`
  - `potrero_updated`
  - `potrero_deleted`
  - `usuario_updated`
  - `usuario_deleted`

### Acceso a la Aplicación
- Backend API: http://localhost:5000
- Frontend: http://localhost:5173
- Usuario admin por defecto:
  - Email: admin@qrfarm.com
  - Password: admin123

## Solución de Problemas

### Error de Conexión MySQL
```bash
# Verificar que MySQL esté ejecutándose
net start mysql  # Windows
sudo systemctl start mysql  # Linux

# Verificar credenciales
mysql -u root -p
```

### Error de Puertos Ocupados
```bash
# Cambiar puertos en configuración
# Backend: modificar port en app.py
# Frontend: modificar port en vite.config.js
```

### Error de Dependencias
```bash
# Reinstalar dependencias
cd backend && pip install --force-reinstall -r requirements.txt
cd ../frontend && rm -rf node_modules && npm install
```

### Logs de Depuración
```bash
# Backend con debug
cd backend && python app.py  # Incluye debug=True

# Frontend con logs detallados
cd frontend && npm run dev -- --logLevel info
```

## Estructura del Proyecto

```
qr-farm/
├── backend/
│   ├── app.py                 # Aplicación Flask principal
│   ├── requirements.txt       # Dependencias Python
│   ├── src/
│   │   ├── controllers/       # Controladores HTTP
│   │   ├── services/          # Lógica de negocio
│   │   ├── routes/            # Definición de rutas
│   │   ├── models/            # Modelos de datos
│   │   └── database/          # Configuración BD y migraciones
│   └── manage_db.py           # Gestión de migraciones
├── frontend/
│   ├── package.json           # Dependencias Node.js
│   ├── src/
│   │   ├── assets/js/         # Lógica JavaScript
│   │   └── components/        # Componentes Vue.js
│   └── vite.config.js         # Configuración Vite
└── README_CORRECCIONES_QR_FARM.md  # Documentación de cambios
```

## Monitoreo y Mantenimiento

### Logs
- Backend: Consola donde se ejecuta Flask
- Frontend: Navegador (DevTools Console)
- Base de datos: Logs de MySQL

### Backup de Base de Datos
```bash
mysqldump -u root -p gestion_ganadera > backup.sql
```

### Actualización del Proyecto
```bash
git pull origin main
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
python manage_db.py upgrade
```

---

**Versión**: 1.0.0
**Fecha**: Noviembre 2025
**Estado**: Listo para producción