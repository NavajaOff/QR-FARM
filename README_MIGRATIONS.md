📚 Guía de Migraciones - QR-FARM
🔄 Sistema de Migraciones con Flask-Migrate

El proyecto QR-FARM utiliza Flask-Migrate (basado en Alembic y SQLAlchemy) para crear automáticamente la estructura de la base de datos a partir de las migraciones incluidas en el repositorio.

👉 Ya no se usan seeders, ya que las migraciones iniciales crean toda la estructura y los datos esenciales del sistema.

---

## ⚙️ Configuración del Entorno (.env)

Antes de iniciar el proyecto, cada desarrollador debe tener su propio archivo .env en la carpeta principal del proyecto (no en backend/).

### 1️⃣ Duplica el archivo de ejemplo:

```bash
cp .env.example .env
```

### 2️⃣ Genera una clave secreta automáticamente:

```bash
flask --app backend/app.py secret
```

### 3️⃣ Verifica que el archivo .env tenga el siguiente formato:

```env
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
```

⚠️ **Importante:** El archivo .env no debe subirse a GitHub. Cada integrante del equipo lo configura localmente con su conexión MySQL.

---

## 🛠️ Aplicar Migraciones

Las migraciones ya están creadas y versionadas dentro del proyecto. Cada integrante solo debe aplicarlas localmente para generar la base de datos y las tablas.

### Comando Principal:

```bash
cd backend
flask --app app.py db upgrade -d src/database/migrations
```

✅ **Qué hace este comando:**
- Si no tienes la base de datos creada, la genera automáticamente.
- Si ya tienes la base de datos, crea todas las tablas necesarias según la última versión de migración.
- Inserta los datos iniciales mínimos (como roles, tipos base o usuario administrador).

---

## 🚀 Comandos Paso a Paso para Actualizar la Base de Datos

### PASO 1: Verificar que tienes el archivo .env

```bash
# Desde la raíz del proyecto
Test-Path .env
```

Si no existe, créalo basándote en `.env.example` o con el contenido mínimo mostrado arriba.

### PASO 2: Instalar/Actualizar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

**Verificar dependencias críticas:**
```bash
pip list | Select-String -Pattern "Flask-Migrate|Flask-SQLAlchemy|pymysql|mysql-connector"
```

Si falta `pymysql`, instálalo:
```bash
pip install pymysql
```

### PASO 3: Verificar Estado Actual de Migraciones

```bash
# Desde el directorio backend
cd backend

# Ver qué migraciones hay disponibles
flask --app app.py db history -d src/database/migrations

# Ver estado actual de la BD
flask --app app.py db current -d src/database/migrations
```

### PASO 4: Aplicar Migraciones

```bash
# Desde el directorio backend
cd backend

# Aplicar todas las migraciones pendientes
flask --app app.py db upgrade -d src/database/migrations
```

**Qué hace este comando:**
- ✅ Crea todas las tablas si no existen
- ✅ Inserta datos iniciales (roles, tipos de pasto, tipos de vacuna, estados)
- ✅ Actualiza la tabla `alembic_version` con la versión aplicada

### PASO 5: Verificar que se Aplicaron Correctamente

```bash
# Conectar a MySQL
mysql -u root -p gestion_ganadera
```

Dentro de MySQL:
```sql
-- Ver todas las tablas
SHOW TABLES;

-- Deberías ver:
-- alembic_version
-- estado_ganado
-- ganado
-- personas
-- potrero
-- qr
-- revision
-- roles
-- tipo_pasto
-- tipo_vacuna
-- usuarios
-- vacunacion

-- Ver datos iniciales insertados
SELECT * FROM roles;
SELECT * FROM tipo_pasto;
SELECT * FROM tipo_vacuna;
SELECT * FROM estado_ganado;

-- Ver versión de migración aplicada
SELECT * FROM alembic_version;

-- Salir
exit;
```

---

## 📊 Estado Esperado Después de Aplicar Migraciones

### Tablas Creadas:
- ✅ `roles` (con datos: admin, usuario)
- ✅ `tipo_pasto` (con datos: Brachiaria humidicola, Brachiaria decumbens, Pasto mombazaa)
- ✅ `tipo_vacuna` (con datos: Brucella, Aftosa, Clostridiales)
- ✅ `estado_ganado` (con datos: saludable, revision, enfermo)
- ✅ `personas`
- ✅ `usuarios`
- ✅ `potrero`
- ✅ `ganado`
- ✅ `qr`
- ✅ `vacunacion`
- ✅ `revision`
- ✅ `alembic_version` (versión: 001)

---

## 🧩 Flujo de Trabajo del Equipo

Cuando un integrante clona el repositorio o actualiza su entorno:

```bash
git pull origin main
cd backend
flask --app app.py db upgrade -d src/database/migrations
```

Esto asegura que tu base de datos esté sincronizada con la estructura más reciente.

---

## ⚠️ Solución de Problemas Comunes

### Error: "No such command 'db'"

**Causa**: Flask-Migrate no está correctamente inicializado

**Solución**: Verifica que `requirements.txt` tenga:
```
Flask-Migrate==4.0.5
Flask-SQLAlchemy==3.1.1
```

Y reinstala:
```bash
pip install Flask-Migrate Flask-SQLAlchemy
```

### Error: "Can't connect to MySQL"

**Solución**:
1. Verifica que MySQL esté ejecutándose
2. Verifica las credenciales en `.env` (en la raíz del proyecto)
3. Prueba la conexión manualmente:
```bash
mysql -u root -p
```

### Error: "Target database is not up to date"

**Solución**:
```bash
cd backend
flask --app app.py db upgrade -d src/database/migrations
```

### Error: "Can't locate revision identified by..."

**Solución**:
```bash
cd backend
flask --app app.py db stamp head -d src/database/migrations
flask --app app.py db upgrade -d src/database/migrations
```

---

## 🎯 Comandos Rápidos (Copy-Paste)

```bash
# 1. Ir al directorio backend
cd backend

# 2. Instalar dependencias (si es necesario)
pip install -r requirements.txt

# 3. Ver migraciones disponibles
flask --app app.py db history -d src/database/migrations

# 4. Aplicar migraciones
flask --app app.py db upgrade -d src/database/migrations

# 5. Verificar estado
flask --app app.py db current -d src/database/migrations
```

---

## ✅ Checklist Final

- [ ] Archivo `.env` configurado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Migraciones aplicadas (`flask db upgrade`)
- [ ] Tablas creadas (verificar con `SHOW TABLES`)
- [ ] Datos iniciales insertados (verificar con `SELECT * FROM roles`)

---

## 💾 Buenas Prácticas

✅ **Haz esto:**
- Ejecuta siempre `db upgrade` después de hacer `git pull`.
- Mantén tu `.env` fuera del repositorio.
- Verifica la base de datos tras aplicar las migraciones.

❌ **No hagas esto:**
- No crees nuevas migraciones manualmente si no cambiaste los modelos.
- No edites las migraciones ya aplicadas.

---

## 🧠 Resumen Final

1. El archivo `.env` se crea a partir de `.env.example` y se genera la clave con `flask --app backend/app.py secret`.
2. Las migraciones ya están incluidas en el proyecto.
3. Cada integrante solo debe ejecutar un comando para generar la base de datos y sus tablas:

```bash
cd backend
flask --app app.py db upgrade -d src/database/migrations
```

Con eso, el entorno queda listo para trabajar 🚀
