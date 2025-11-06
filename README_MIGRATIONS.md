📚 Guía de Migraciones - QR-FARM
🔄 Sistema de Migraciones con Flask-Migrate

El proyecto QR-FARM utiliza Flask-Migrate (basado en Alembic y SQLAlchemy) para crear automáticamente la estructura de la base de datos a partir de las migraciones incluidas en el repositorio.

👉 Ya no se usan seeders, ya que las migraciones iniciales crean toda la estructura y los datos esenciales del sistema.

⚙️ Configuración del Entorno (.env)

Antes de iniciar el proyecto, cada desarrollador debe tener su propio archivo .env en la carpeta principal del proyecto (no en backend/).
Para ello:

1️⃣ Duplica el archivo de ejemplo:

cp .env.example .env


2️⃣ Genera una clave secreta automáticamente:

flask --app backend/app.py secret


3️⃣ Verifica que el archivo .env tenga el siguiente formato:

# Configuración del entorno Flask
FLASK_ENV=development
SECRET_KEY=  # Se generará automáticamente con el comando anterior
DATABASE_URL=mysql+pymysql://root:@localhost/gestion_ganadera

# Configuración de la base de datos MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=gestion_ganadera
DB_USER=root
DB_PASSWORD=

# Credenciales del usuario administrador
ADMIN_EMAIL=admin@qrfarm.com
ADMIN_PASSWORD=admin123

# Configuración adicional
DEBUG=True
TESTING=False


⚠️ Importante:
El archivo .env no debe subirse a GitHub. Cada integrante del equipo lo configura localmente con su conexión MySQL.

🛠️ Aplicar Migraciones

Las migraciones ya están creadas y versionadas dentro del proyecto.
Cada integrante solo debe aplicarlas localmente para generar la base de datos y las tablas.

Ejecuta este comando:

flask --app backend/app.py db upgrade -d backend/src/database/migrations


✅ Qué hace este comando:

Si no tienes la base de datos creada, la genera automáticamente.

Si ya tienes la base de datos, crea todas las tablas necesarias según la última versión de migración.

Inserta los datos iniciales mínimos (como roles, tipos base o usuario administrador).

🧩 Flujo de Trabajo del Equipo

Cuando un integrante clona el repositorio o actualiza su entorno:

git pull origin main
flask --app backend/app.py db upgrade -d backend/src/database/migrations


Esto asegura que tu base de datos esté sincronizada con la estructura más reciente.

⚠️ Solución de Problemas Comunes

🔹 Error: “Target database is not up to date”

flask --app backend/app.py db upgrade


🔹 Error: “Can't locate revision identified by...”

flask --app backend/app.py db stamp head

💾 Buenas Prácticas

✅ Haz esto:

Ejecuta siempre db upgrade después de hacer git pull.

Mantén tu .env fuera del repositorio.

Verifica la base de datos tras aplicar las migraciones.

❌ No hagas esto:

No crees nuevas migraciones manualmente si no cambiaste los modelos.

No edites las migraciones ya aplicadas.

🧠 Resumen Final

El archivo .env se crea a partir de .env.example y se genera la clave con flask --app backend/app.py secret.

Las migraciones ya están incluidas en el proyecto.

Cada integrante solo debe ejecutar un comando para generar la base de datos y sus tablas:

flask --app backend/app.py db upgrade -d backend/src/database/migrations


Con eso, el entorno queda listo para trabajar 🚀