# QR-FARM

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

## Puesta en Marcha

1. **Backend**
   - Crear y activar un entorno virtual en `backend/`.
   - Instalar dependencias con `pip install -r requirements.txt`.
   - Copiar el archivo de ejemplo `cp .env.example .env` (o `copy .env.example .env` en Windows) desde la raíz del proyecto.
   - Generar una `SECRET_KEY` personal ejecutando `flask --app app generate-secret-key` dentro de `backend/`.
   - Aplicar las migraciones con `flask --app app db upgrade -d backend/src/database/migrations`.
   - Ejecutar `python app.py` para iniciar el servidor Flask con SocketIO en `http://localhost:5000`.

2. **Frontend**
   - Acceder a `frontend/` y ejecutar `npm install`.
   - Levantar el entorno con `npm run dev`, disponible en `http://localhost:5173`.

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

## Migraciones y Seeders Cifrados

- **Inicializar el entorno**  
  - Clona el repositorio y crea tu entorno virtual.  
  - Copia `.env.example` a `.env` y rellena credenciales de base de datos.  
  - Genera tu `SECRET_KEY` personal con `flask --app app generate-secret-key` desde `backend/`.  
  - Ejecuta `flask --app app db upgrade -d backend/src/database/migrations` para aplicar las migraciones.

- **Clave del equipo (`TEAM_KEY`)**  
  - Solo el líder del equipo ejecuta `flask --app app team:generate_key` para generar una clave hex segura (`token_hex(32)`).  
  - Comparte la `TEAM_KEY` con el equipo usando un canal seguro (gestor de contraseñas, Slack privado, Signal, etc.).  
  - Cada integrante agrega esa `TEAM_KEY` a su archivo `.env`.

- **Exportar e importar datos base**  
  - Con datos de referencia en la base, ejecuta `flask --app app seed:secure_export` para crear `backend/src/database/seeders/secure_seed.bin`.  
  - Sube el archivo `secure_seed.bin` al repositorio: está cifrado y no expone datos legibles sin la `TEAM_KEY`.  
  - En otra máquina, coloca la misma `TEAM_KEY` en `.env` y ejecuta `flask --app app seed:secure_import` para poblar la base de datos sin duplicados.

- **Verificación y mantenimiento**  
  - Revisa que la tabla `alembic_version` contenga la última migración y que las tablas claves (`roles`, `personas`, `potrero`, `ganado`, `vacunacion`, etc.) tengan datos.  
  - Confirma que `secure_seed.bin` existe y no es legible en texto plano.  
  - Si la `TEAM_KEY` se expone, genera una nueva, comparte la actualización y vuelve a cifrar los datos con `seed:secure_export`.

Estas herramientas sustituyen los seeders en texto plano y permiten mantener datos iniciales consistentes sin comprometer información sensible.

