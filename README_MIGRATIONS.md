📚 Guía de Migraciones - QR-FARM
🔄 Sistema de Migraciones con Flask-Migrate

El proyecto QR-FARM utiliza Flask-Migrate (basado en Alembic y SQLAlchemy) para crear automáticamente la estructura de la base de datos a partir de las migraciones incluidas en el repositorio.


⚙Configuración del Entorno (.env)

Antes de iniciar el proyecto, cada desarrollador debe tener su propio archivo .env en la carpeta principal del proyecto (no en backend/).
Para ello:

python -m venv venv


# primero que todo instala todo lo necesario para develop:

cd backend

pip install -r requirements.txt

# Duplica el archivo de ejemplo:

cp .env.example .env

# Genera una clave secreta automáticamente:

flask --app app generate-secret-key

# importante este comando para generar la key se tiene que ejecutar en backend:

 cd backend


🛠 Aplicar Migraciones

Las migraciones ya están creadas y versionadas dentro del proyecto.
Cada integrante solo debe aplicarlas localmente para generar las tablas.

Ejecuta este comando:

alembic -c alembic.ini upgrade head

⚠ Importante: antes de ejecutar ese comando crea la base de datos con el nombre que sale en el example

# este comando hara es agregar todas las tablas con los datos importantes para que funcione el proyecto y ya solo seria correr develop


# si vas a aplicar nuevas migraciones:

alembic -c alembic.ini revision --autogenerate -m "Descripción del cambio"

# si vas a actualizar tus migraciones:

alembic -c alembic.ini upgrade head

# ahora inicializamos el backend (esto dentro de develop):

python app.py


# si al ejecutar el backend dice que no se puede crear el usuario admin ejecuta este comando:

pip install bcrypt==4.0.1 passlib==1.7.4 --force-reinstall

# despues vuelve a correr el backend, esto hara que se pueda crear el usuario admin correctamente



🧩 Flujo de Trabajo del Equipo

Cuando un integrante clona el repositorio o actualiza su entorno:

# git pull origin develop

# 


Esto asegura que tu base de datos esté sincronizada con la estructura más reciente.


❌ No hagas esto:

No crees nuevas migraciones manualmente si no cambiaste los modelos.

No edites las migraciones ya aplicadas.

🧠 Resumen Final

El archivo .env se crea a partir de .env.example y se genera la clave con flask --app backend/app.py secret.

Las migraciones ya están incluidas en el proyecto.

Cada integrante solo debe ejecutar un comando para generar la base de datos y sus tablas:


Con eso, el entorno queda listo para trabajar 🚀