# 🚀 QR Farm - Sistema de Gestión Ganadera

Sistema completo de gestión ganadera con frontend en Vue.js y backend en Flask.

## 📋 Requisitos

- **Python 3.8+**
- **Node.js 16+**
- **MySQL/MariaDB**
- **Git**

## 🚀 Inicio Rápido

### Opción 1: Inicio automático (Recomendado)

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd qr-farm

# Ejecutar el script de inicio automático
python iniciar_qrfarm.py
```

### Opción 2: Inicio manual

```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py

# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

## 🌐 Acceder a la aplicación

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000

## ⚙️ Configuración

### Variables de entorno

#### Backend (.env)
```env
# Base de datos
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=gestion_ganadera

# JWT
SECRET_KEY=tu_clave_secreta

# Servidor
HOST=0.0.0.0
PORT=5000
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:5173
```

#### Frontend (.env)
```env
VUE_APP_API_BASE_URL=http://localhost:5000/api
VUE_APP_APP_NAME=QR Farm
VUE_APP_DEBUG=true
```

### Archivo de configuración global (frontend/public/config.js)

```javascript
window.config = {
  API_BASE_URL: 'http://localhost:5000/api',
  APP_NAME: 'QR Farm',
  VERSION: '1.0.0',
  DEBUG: true,
  TIMEOUT: 10000
};
```

## 🏗️ Arquitectura

### Backend (Flask)
- **Puerto**: 5000
- **Base de datos**: MySQL
- **Autenticación**: JWT
- **CORS**: Configurado para desarrollo

### Frontend (Vue.js + Vite)
- **Puerto**: 5173
- **Framework**: Vue 3
- **Build tool**: Vite
- **UI**: Bootstrap 5

## 🔐 Roles de usuario

- **Administrador**: Acceso completo a todas las funcionalidades
- **Usuario**: Acceso limitado a funciones básicas

## 📚 API Endpoints

### Autenticación
- `POST /api/usuarios/register` - Registro de usuarios
- `POST /api/usuarios/login` - Inicio de sesión

### Usuarios (Admin)
- `GET /api/usuarios/` - Listar usuarios
- `PUT /api/usuarios/{id}/estado` - Cambiar estado de usuario

### Ganado
- `GET /api/ganados/` - Listar ganado
- `POST /api/ganados/` - Crear ganado

### Potreros
- `GET /api/potreros/` - Listar potreros
- `POST /api/potreros/` - Crear potrero

## 🛠️ Desarrollo

### Instalación de dependencias

```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install
```

### Ejecución en modo desarrollo

```bash
# Opción automática (recomendado)
python iniciar_qrfarm.py

# O manualmente:
# Terminal 1 - Backend
cd backend && python app.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

## 🚀 Despliegue

### Producción

1. **Configurar variables de entorno**:
   ```env
   # Backend
   DEBUG=False
   SECRET_KEY=tu_clave_produccion_segura

   # Frontend
   VUE_APP_API_BASE_URL=https://tu-api.com/api
   VUE_APP_DEBUG=false
   ```

2. **Construir frontend**:
   ```bash
   cd frontend
   npm run build
   ```

3. **Desplegar backend** con WSGI (Gunicorn, uWSGI)

4. **Servir frontend** con Nginx o Apache

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 📞 Soporte

Para soporte técnico, contacta al equipo de desarrollo.

---

**Desarrollado con ❤️ por el equipo QR Farm**