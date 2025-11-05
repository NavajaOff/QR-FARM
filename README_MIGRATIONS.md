# 🗄️ Guía de Migraciones de Base de Datos - QR Farm

## 📋 Descripción

Este proyecto utiliza **Alembic** con **Flask-Migrate** para gestionar las migraciones de base de datos. Las migraciones permiten versionar los cambios en el esquema de la base de datos y compartirlos con el equipo de desarrollo.

## 🚀 Configuración Inicial

### Para el líder del proyecto (primera vez)

```bash
# 1. Instalar dependencias
cd backend
pip install -r requirements.txt

# 2. Configurar la base de datos desde cero
python setup_database.py
```

### Para miembros del equipo

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd QR-FARM

# 2. Instalar dependencias
cd backend
pip install -r requirements.txt

# 3. Aplicar todas las migraciones
python setup_database.py
```

## ✅ **Estado Actual del Sistema**

### Migraciones Aplicadas
- ✅ **001_migracion_inicial.py**: Estructura base de tablas
- ✅ **002_datos_iniciales.py**: Datos iniciales completos (roles, tipos de pasto, estados de ganado, tipos de vacuna, usuario admin)

### Datos Iniciales Incluidos
- **Roles**: admin, usuario
- **Tipos de pasto**: Brachiaria humidicola, Brachiaria decumbens, Pasto mombazaa
- **Estados de ganado**: activo, saludable, revision, enfermo, vendido
- **Tipos de vacuna**: Brucella, Aftosa, Clostridiales, Rabia, Leptospirosis
- **Usuario administrador**: admin@qrfarm.com / admin123

## 🛠️ Comandos de Gestión de Migraciones

### Comando Principal para Equipo

```bash
cd backend

# ✅ PARA NUEVOS MIEMBROS DEL EQUIPO: Aplicar todas las migraciones
python setup_database.py

# Esto ejecutará automáticamente:
# - python manage_db.py upgrade (aplica todas las migraciones)
# - Inserta datos iniciales si no existen
```

### Comandos Avanzados (para desarrollo)

```bash
cd backend

# Ver migración actual
python manage_db.py current

# Ver historial de migraciones
python manage_db.py history

# Crear nueva migración (después de cambiar modelos)
python manage_db.py migrate "descripción del cambio"

# Aplicar migraciones pendientes
python manage_db.py upgrade

# Revertir última migración
python manage_db.py downgrade

# Marcar una migración específica como aplicada
python manage_db.py stamp <revision_id>
```

### Usando Alembic directamente

```bash
cd backend/src/database/migrations

# Ver estado actual
alembic current

# Ver historial
alembic history

# Crear nueva migración
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

## 📁 Estructura de Migraciones

```
backend/
├── src/database/migrations/
│   ├── alembic.ini              # Configuración de Alembic
│   ├── env.py                   # Entorno de migraciones
│   ├── script.py.mako           # Plantilla para migraciones
│   └── versions/                # Archivos de migraciones
│       ├── 001_migracion_inicial.py
│       └── 002_datos_iniciales.py
├── manage_db.py                 # Script de gestión simplificado
└── setup_database.py            # Configuración inicial
```

## 🔄 Flujo de Trabajo

### 1. Desarrollador hace cambios en el esquema

```python
# Ejemplo: Agregar nueva tabla o columna
# En tus modelos o directamente en SQL
```

### 2. Crear migración

```bash
cd backend
python manage_db.py migrate "agregar tabla vacunaciones"
```

### 3. Revisar y ajustar la migración generada

Edita el archivo generado en `backend/src/database/migrations/versions/` si es necesario.

### 4. Probar la migración

```bash
# Aplicar
python manage_db.py upgrade

# Si hay errores, revertir y corregir
python manage_db.py downgrade
```

### 5. Commit y push

```bash
git add .
git commit -m "feat: agregar migración para nueva tabla"
git push
```

### 6. Equipo actualiza

```bash
git pull
cd backend
python manage_db.py upgrade
```

## ⚠️ Consideraciones Importantes

### ✅ Para nuevos miembros del equipo
```bash
# Después de clonar el repositorio:
cd backend
python setup_database.py  # ✅ Esto es TODO lo que necesitan
```

### Para bases de datos existentes
- Las migraciones están marcadas como aplicadas para evitar recrear tablas existentes
- Los datos iniciales ya están insertados

### Versionado de migraciones
- Cada migración tiene un ID único y secuencial
- No modificar migraciones ya aplicadas en producción
- Crear nuevas migraciones para cambios adicionales

### 🔐 Credenciales de Acceso Inicial
- **Usuario**: admin@qrfarm.com
- **Contraseña**: admin123
- **Rol**: Administrador

## 🐛 Solución de Problemas

### Error: "Table already exists"
```bash
# Marcar como aplicada sin ejecutar
python manage_db.py stamp <revision_id>
```

### Error: "No such revision"
```bash
# Ver historial y verificar IDs
python manage_db.py history
```

### Resetear migraciones (solo desarrollo)
```bash
# ⚠️ PELIGROSO: Borra todos los datos
python manage_db.py downgrade base
python manage_db.py upgrade
```

## 📞 Contacto

Si tienes problemas con las migraciones, contacta al líder del proyecto o revisa la documentación de [Alembic](https://alembic.sqlalchemy.org/) y [Flask-Migrate](https://flask-migrate.readthedocs.io/).