# QR-FARM

## Equipo de Desarrollo

Este proyecto fue desarrollado por el equipo conformado por:
- **Juan David Castro Villarreal**
- **Jose David Hernandez Navaja**
- **Ronald Bejarano Barbosa**

## Descripción General

QR-FARM es una plataforma integral para la gestión ganadera que combina un backend desarrollado con Flask y un frontend en Vue 3. El sistema permite administrar usuarios, potreros, animales, vacunaciones y lectura de códigos QR, ofreciendo herramientas específicas para administradores y usuarios finales.

## Arquitectura del Proyecto

- **Backend:** Flask + Flask-SocketIO, organizado bajo el directorio `backend/`.
  - Controladores en `src/controllers` definen la lógica de cada recurso.
  - Servicios en `src/services` encapsulan el acceso a datos y la lógica de negocio.
  - Las rutas están centralizadas en `src/routes`, donde se aplica el middleware de autenticación.
  - `src/utils/auth.py` implementa la verificación JWT mediante el decorador `token_required`.
  - `app.py` inicializa Flask, configura CORS, SocketIO y las variables de entorno.

- **Frontend:** Vue 3 + Vite, ubicado en `frontend/`.
  - Componentes y vistas en `src/views` y `src/components` componen la interfaz.
  - `src/composables/useUsuarios.js` y otros composables gestionan la comunicación con la API.
  - `src/services/api.js` define un cliente Axios con interceptores para adjuntar el token JWT.

- **Base de datos:** MySQL, administrada mediante scripts de conexión en `backend/src/database` y migraciones en `backend/src/database/migrations`.

## Autenticación y Seguridad

- Inicio de sesión disponible en `POST /api/usuarios/login`.
- Los tokens JWT incluyen `user_id`, `email`, `role` y fecha de expiración (`exp`).
- El decorador `token_required` valida el encabezado Authorization, verifica el token y asegura que el usuario esté activo antes de permitir el acceso a rutas protegidas.
- CORS está configurado para aceptar peticiones desde `http://localhost:5173` y `http://127.0.0.1:5173` tanto en Flask como en SocketIO.

## Funcionalidades Principales

- **Gestión de usuarios:**
  - Listado, creación, edición, activación/desactivación y eliminación lógica.
  - Sincronización en tiempo real mediante eventos SocketIO (`usuario_updated`, `usuario_deleted`).
- **Gestión de potreros, animales y vacunaciones:**
  - CRUD completo desde el panel administrativo.
  - Visualización estructurada por roles.
- **Código QR:**
  - Generación y actualización de códigos QR para identificar animales.
  - Archivos disponibles en `backend/qr`.

## Configuración del Super Admin

### 📋 Resumen

El sistema **QR-FARM** utiliza un sistema de super administrador único y seguro que:

- ✅ **Solo puede crearse desde variables de entorno** (no desde la API)
- ✅ **Se inicializa automáticamente** al iniciar el backend
- ✅ **Compartido para todo el equipo** (3 personas)
- ✅ **Bloquea cualquier intento** de crear super_admin desde la API

### 🔐 Configuración

#### 1. Agregar variables al archivo `.env`

Agrega estas variables a tu archivo `.env` en la raíz del proyecto:

```env
# Super Admin Global (COMPARTIDO)
ROOT_SUPER_ADMIN_EMAIL=superadmin@qrfarm.com
ROOT_SUPER_ADMIN_PASSWORD=TuContrasenaMuySegura123!
ROOT_SUPER_ADMIN_NOMBRE=Super Administrador QR-Farm
```

#### 2. El super_admin se crea automáticamente

Al iniciar el backend con `python app.py`, el sistema:

1. Verifica si ya existe un super_admin con ese email
2. Si no existe, lo crea automáticamente
3. Si ya existe, no hace nada (no lo sobrescribe)

### 🔒 Seguridad

#### ¿Cómo funciona el bloqueo?

1. **En el Servicio de Usuarios** (`usuario_service.py`):
   - Bloquea la creación de usuarios con rol `super_admin`
   - Retorna error: "No se puede crear usuarios super_admin desde la API"

2. **En el Controlador** (`usuario_controller.py`):
   - Bloquea la asignación del rol `super_admin` al actualizar usuarios
   - Retorna error: "No se puede asignar el rol super_admin. Este rol solo se crea desde variables de entorno."

3. **Solo desde `.env`**:
   - El único lugar donde se puede definir el super_admin es en el archivo `.env`
   - Se crea automáticamente al iniciar la aplicación

### 📝 Notas Importantes

1. **Un solo super_admin**: Solo debe haber un super_admin en el sistema (el definido en `.env`)

2. **Compartido para el equipo**: Los 3 miembros del equipo usan las mismas credenciales definidas en `.env`

3. **No cambiar desde la UI**: No intentes cambiar el rol de un usuario a `super_admin` desde la interfaz, estará bloqueado

4. **Seguridad del `.env**:
   - Nunca subas el archivo `.env` al repositorio
   - Mantén las credenciales seguras
   - Cambia la contraseña después de la primera configuración

### 🔄 Flujo de Trabajo

1. Configurar variables en `.env`
2. Iniciar el backend: `python app.py`
3. El super_admin se crea automáticamente (si no existe)
4. Usar las credenciales para iniciar sesión

### ✅ Verificación

Para verificar que el super_admin se creó correctamente:

1. Inicia sesión con el email y password definidos en `.env`
2. Debes ver el badge "Super Admin" en la barra superior
3. Debes ver el menú "Tenants" en el sidebar
4. Puedes acceder a `/admin/gestionar-tenants`

---

**Última actualización**: Sistema de super_admin único desde variables de entorno

## Migraciones y Seeders Cifrados

### 📚 Guía de Migraciones y Seeders Cifrados - QR-FARM
### 🔄 Basado en Flask-Migrate + Seeders Seguros Fernet

#### 1. Preparar el entorno local

1. Clona el repositorio y sitúate en la raíz del proyecto.
2. Crea el entorno virtual:
   - Windows: `python -m venv venv`
   - macOS/Linux: `python3 -m venv venv`
3. Activa el entorno virtual.
4. Instala dependencias del backend:
   ```
   cd backend
   pip install -r requirements.txt
   ```
5. Copia la configuración de ejemplo desde la raíz del proyecto:
   - Windows: `copy .env.example .env`
   - macOS/Linux: `cp .env.example .env`
6. Genera tu `SECRET_KEY` personal (se actualiza el `.env` local, nunca el ejemplo):
   ```
   flask --app app generate-secret-key
   ```

#### 2. Base de datos y migraciones

1. Crea la base de datos vacía con el nombre indicado en `.env` (por defecto `gestion_ganadera`).
2. Aplica todas las migraciones versionadas desde el directorio backend:
   ```
   cd backend
   
   alembic -c alembic.ini upgrade head
   ```
   O usando el script de gestión:
   ```
   python manage_db.py upgrade
   ```
3. Verifica en MySQL Workbench (u otra herramienta) que:
   - La tabla `alembic_version` contiene la última revisión.
   - Las tablas `roles`, `personas`, `potrero`, `ganado`, `vacunacion`, etc. fueron creadas.

#### 3. Generar y compartir la TEAM_KEY

1. Solo el líder del equipo ejecuta:
   ```
   flask --app app team:generate_key
   ```
2. La clave generada (`token_hex(32)`) se comparte manualmente por un canal seguro (gestor de contraseñas, Slack privado, Signal, etc.).
3. Cada integrante copia esa `TEAM_KEY` en su archivo `.env` local. **Nunca** hagas commit de `.env`.

#### 4. Exportar datos base cifrados

1. Asegúrate de que la base de datos contenga los datos iniciales que deseas compartir (roles, personas, usuarios, potreros, ganado, vacunaciones, catálogos).
2. Ejecuta:
   ```
   flask --app app seed:secure_export
   ```
3. Se generará `backend/src/database/seeders/secure_seed.bin`. Sube este archivo al repositorio: está cifrado con Fernet y no expone datos en texto plano.
4. Comprueba que el archivo no sea legible abriéndolo con un editor hexadecimal o cualquier visor: debe verse como datos binarios.

#### 5. Importar datos en otras máquinas

1. Cada integrante coloca la misma `TEAM_KEY` en su `.env`.
2. Ejecuta:
   ```
   flask --app app seed:secure_import
   ```
3. El script realiza inserciones idempotentes (`ON DUPLICATE KEY UPDATE`) para evitar duplicados. Revisa que los datos se hayan creado consultando las tablas en MySQL Workbench.

#### 6. Rotación y mantenimiento

- Si sospechas que la `TEAM_KEY` se filtró:
  1. Exporta con la clave actual para no perder los datos.
  2. Genera una nueva clave con `flask --app app team:generate_key`.
  3. Distribuye la nueva clave de forma segura.
  4. Vuelve a exportar con la clave renovada y sube el `secure_seed.bin` actualizado.
- Cada vez que actualices el script o la estructura de datos, repite el proceso de exportar y avisar al equipo.

#### 7. Validaciones rápidas

- `flask --help` debe listar los comandos:
  - `seed:secure_export`
  - `seed:secure_import`
  - `team:generate_key`
- `secure_seed.bin` debe existir y estar cifrado (contenido ilegible).
- La tabla `alembic_version` debe tener la última revisión después de ejecutar `alembic upgrade head` o `python manage_db.py upgrade`.

Con este flujo cada integrante puede reconstruir la base de datos de forma segura y consistente 🚀

## Escáner de códigos QR

Este frontend Vue 3 incluye ahora el componente reutilizable `QrScanner.vue`, compatible con rutas `/admin/scan-qr` y `/user/scan-qr`. El escáner activa la cámara del dispositivo, detecta códigos QR mediante `html5-qrcode` y consulta el backend para mostrar la información del recurso sin abandonar la página.

### Integración en rutas

- Administrador: `frontend/src/views/admin/EscanearQRAdmin.vue` usa `<QrScanner role="admin" resource-endpoint="/ganado/{id}" />`.
- Usuario: `frontend/src/views/user/EscanearQRUsuario.vue` usa `<QrScanner role="user" resource-endpoint="/ganado/{id}" />`.
- Las rutas están declaradas en `frontend/src/router/index.js`.


### QR con datos embebidos

- Cada QR generado incluye un payload JSON con la estructura `schema: "qr-farm.v1"` que contiene datos básicos del ganado (ID, nombre, propietario, potrero, estado y URL).
- Define la variable de entorno `QR_FARM_WEB_URL` (o `QR_FARM_FRONTEND_URL`) en el backend para que el QR apunte a la ficha en línea correcta.
- El QR mantiene compatibilidad con códigos antiguos: si solo incluye texto, el escáner extrae el ID y consulta la API como antes.

### Flujo offline / online

- Si el QR aporta el JSON embebido y el navegador está sin conexión, `QrScanner.vue` renderiza la tarjeta con esa información inmediata.
- Cuando hay conexión, el escáner muestra los datos embebidos y sincroniza con la API; si la actualización falla, se mantiene la información offline y se muestra una alerta suave.
- Si el QR no incluye datos embebidos y no hay conexión, se informa claramente al usuario que no es posible obtener la información.

### Pruebas manuales

1. **Permisos**: al entrar por primera vez al escáner, aceptar el acceso a la cámara.
2. **Dispositivos**: probar en iPhone (Safari), Android (Chrome) y escritorio (Chrome/Firefox con webcam).
3. **Escenarios**:
   - QR con JSON `{ "id": 123 }`.
   - QR con texto `ID:123`.
   - QR con URL (el componente avisa si no contiene ID).
   - Fallback cargando una imagen (`Subir imagen (fallback)`).
4. **Errores esperados**:
   - 404 → "QR no reconocido. Verifica que el código exista."
   - 403 → "No autorizado para consultar este recurso."
   - 500 → "Error del servidor al consultar el recurso."

### Requisitos de permisos

- Cámara: `navigator.mediaDevices.getUserMedia({ video: true })`.
- HTTPS recomendado para habilitar cámaras en móviles.
- Token JWT enviado automáticamente por `src/services/api.js` en el encabezado `Authorization`.

### Telemetría

El componente registra en consola todos los intentos de lectura (exitosos y fallidos) y conserva un historial visible en la interfaz para auditoría básica. Para extenderlo, envía los eventos capturados en `QrScanner.vue` al backend.

### Tarjeta detallada del ganado

- La información se presenta en `GanadoDetailCard.vue` con pestañas: **Información general**, **Potrero**, **Vacunas** y **Historial**.
- Cada sección incluye íconos de FontAwesome, disposición responsive (grid en escritorio, bloques en móvil) y mensajes amigables cuando faltan datos.
- Las dosis próximas a vencer (<= 10 días) y vencidas se resaltan con chips de color.
- El botón `Volver a escanear` reactiva la cámara sin recargar la vista; acciones extra (`Ver historial completo`, `Descargar ficha`) se emiten hacia la vista que consume el componente.
- Cuando los datos provienen del QR (modo offline) se muestra un banner amarillo. Si hay conexión, el botón **Actualizar datos** sincroniza la ficha con `/api/ganado/{id}`.

### Modo offline

- El backend genera QR con un payload JSON `qr-farm.v1` que incluye datos esenciales (ID, nombre, estado, propietario, potrero, peso, URL).
- `QrScanner.vue` detecta este payload embebido y muestra la ficha sin necesidad de una llamada HTTP cuando `navigator.onLine === false`.
- Al recuperar la conexión, el sistema intenta sincronizar automáticamente; el usuario también puede forzar la actualización desde la tarjeta.
- Los QR antiguos que contienen solo la URL siguen funcionando: el escáner extrae el ID numérico de la ruta y consulta la API como antes.

## 🚀 Instalación y Configuración

### 📋 Opciones de Instalación

Este proyecto se puede ejecutar de **dos formas**:

#### 🔧 **Opción A: Desarrollo Local** (Recomendado para desarrollo)
Sigue las instrucciones a continuación para configurar el entorno de desarrollo.

#### 🐳 **Opción B: Docker** (Recomendado para producción/demo)
Si prefieres usar Docker, consulta el archivo [`README_DOCKER.md`](README_DOCKER.md) para instrucciones completas.

---

### 🔧 Desarrollo Local

#### Requisitos Previos
- **Python 3.12+**
- **MySQL 8.0+** (o MariaDB)
- **Node.js 18+**
- **Git**

#### 1. Clonar el Repositorio
```bash
git clone <url-del-repo>
cd QR-FARM
```

#### 2. Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones locales
nano .env  # o notepad .env en Windows


#### 3. Configurar Base de Datos MySQL

Crea la base de datos vacía:
```sql
-- Ejecutar en MySQL Workbench o terminal MySQL
CREATE DATABASE gestion_ganadera;

-- Crear usuario (opcional, puedes usar 'root')
CREATE USER 'tu_usuario'@'localhost' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON gestion_ganadera.* TO 'tu_usuario'@'localhost';
FLUSH PRIVILEGES;
```

#### 4. Instalar Dependencias del Backend
```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### 5. Ejecutar Migraciones
```bash
# Desde el directorio backend/
alembic -c alembic.ini upgrade head
```

#### 6. Instalar Dependencias del Frontend
```bash
cd ../frontend
npm install
```

#### 7. Iniciar Servicios

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```
**Servidor disponible en:** http://localhost:5000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
**Aplicación disponible en:** http://localhost:5173

#### 8. Verificar Instalación

1. **Accede al frontend:** http://localhost:5173
2. **Inicia sesión** con las credenciales del super admin definidas en `.env`
3. **Verifica la API:** http://localhost:5000/api/health

### 🔧 Comandos Útiles para Desarrollo

```bash
# Backend
cd backend
python app.py                    # Iniciar servidor
alembic -c alembic.ini upgrade head  # Aplicar migraciones
flask --app app generate-secret-key  # Generar nueva SECRET_KEY

# Frontend
cd frontend
npm run dev                     # Desarrollo con hot reload
npm run build                   # Build para producción
npm run preview                 # Vista previa del build
```

### 🐛 Solución de Problemas (Desarrollo Local)

#### Error: "Can't connect to MySQL server"
- Verifica que MySQL esté ejecutándose
- Confirma las credenciales en `.env`
- Asegúrate de que la base de datos `gestion_ganadera` existe

#### Error: "Module not found" en frontend
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Error: "SECRET_KEY not found"
```bash
cd backend
flask --app app generate-secret-key
```

---

### 🐳 Docker (Producción/Demo)

Para usar Docker en lugar del desarrollo local, consulta el archivo [`README_DOCKER.md`](README_DOCKER.md) que contiene:

- ✅ Instrucciones completas de instalación con Docker
- ✅ Configuración automática de servicios
- ✅ Comparación entre desarrollo local y Docker
- ✅ Solución de problemas específicos de Docker
- ✅ Optimizaciones para producción

**Comando rápido para Docker:**
```bash
cp .env.docker .env
docker-compose up --build -d
```

## Flujo de Trabajo

1. El usuario inicia sesión y recibe un JWT.
2. Axios agrega automáticamente el token al encabezado `Authorization`.
3. Los controladores del backend validan y procesan las solicitudes mediante sus servicios asociados.
4. Los datos se persisten en MySQL y se retornan en formato JSON al frontend.
5. Los cambios relevantes se emiten a través de SocketIO para reflejarse en tiempo real.

## Mantenimiento y Buenas Prácticas

- Mantener sincronizada la estructura de la base de datos con las migraciones.
- Verificar los logs del backend (`print` en controladores/servicios) para depurar errores.
- Utilizar el decorador `token_required` en cualquier nueva ruta protegida.
- Evitar duplicar lógica: centralizar validaciones y transformaciones en los servicios.

## Próximos Pasos Recomendados

- Implementar pruebas unitarias para servicios críticos.
- Añadir manejo de roles granular en el frontend (guardas de ruta) y el backend (autorización detallada).
- Mejorar la gestión de errores globales mostrando mensajes consistentes en la interfaz.
- Documentar los esquemas de base de datos y los contratos de la API para facilitar integraciones futuras.

---

## 🐳 Opción Docker (Rápida)

Si prefieres una **configuración instantánea** sin instalar dependencias locales, usa Docker:

```bash
# Copiar configuración
cp .env.docker .env

# Iniciar todo automáticamente
docker-compose up --build -d

# Acceder: http://localhost
```

**Documentación completa en [`README_DOCKER.md`](README_DOCKER.md)**
