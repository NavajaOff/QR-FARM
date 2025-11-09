# 📚 Guía de Migraciones y Seeders Cifrados - QR-FARM
# 🔄 Basado en Flask-Migrate + Seeders Seguros Fernet

## 1. Preparar el entorno local

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

## 2. Base de datos y migraciones

1. Crea la base de datos vacía con el nombre indicado en `.env` (por defecto `gestion_ganadera`).
2. Aplica todas las migraciones versionadas:
   ```
   flask --app app db upgrade -d backend/src/database/migrations
   ```
3. Verifica en MySQL Workbench (u otra herramienta) que:
   - La tabla `alembic_version` contiene la última revisión.
   - Las tablas `roles`, `personas`, `potrero`, `ganado`, `vacunacion`, etc. fueron creadas.

## 3. Generar y compartir la TEAM_KEY

1. Solo el líder del equipo ejecuta:
   ```
   flask --app app team:generate_key
   ```
2. La clave generada (`token_hex(32)`) se comparte manualmente por un canal seguro (gestor de contraseñas, Slack privado, Signal, etc.).
3. Cada integrante copia esa `TEAM_KEY` en su archivo `.env` local. **Nunca** hagas commit de `.env`.

## 4. Exportar datos base cifrados

1. Asegúrate de que la base de datos contenga los datos iniciales que deseas compartir (roles, personas, usuarios, potreros, ganado, vacunaciones, catálogos).
2. Ejecuta:
   ```
   flask --app app seed:secure_export
   ```
3. Se generará `backend/src/database/seeders/secure_seed.bin`. Sube este archivo al repositorio: está cifrado con Fernet y no expone datos en texto plano.
4. Comprueba que el archivo no sea legible abriéndolo con un editor hexadecimal o cualquier visor: debe verse como datos binarios.

## 5. Importar datos en otras máquinas

1. Cada integrante coloca la misma `TEAM_KEY` en su `.env`.
2. Ejecuta:
   ```
   flask --app app seed:secure_import
   ```
3. El script realiza inserciones idempotentes (`ON DUPLICATE KEY UPDATE`) para evitar duplicados. Revisa que los datos se hayan creado consultando las tablas en MySQL Workbench.

## 6. Rotación y mantenimiento

- Si sospechas que la `TEAM_KEY` se filtró:
  1. Exporta con la clave actual para no perder los datos.
  2. Genera una nueva clave con `flask --app app team:generate_key`.
  3. Distribuye la nueva clave de forma segura.
  4. Vuelve a exportar con la clave renovada y sube el `secure_seed.bin` actualizado.
- Cada vez que actualices el script o la estructura de datos, repite el proceso de exportar y avisar al equipo.

## 7. Validaciones rápidas

- `flask --help` debe listar los comandos:
  - `seed:secure_export`
  - `seed:secure_import`
  - `team:generate_key`
- `secure_seed.bin` debe existir y estar cifrado (contenido ilegible).
- La tabla `alembic_version` debe tener la última revisión después de ejecutar `db upgrade`.

Con este flujo cada integrante puede reconstruir la base de datos de forma segura y consistente 🚀

