"""
Comandos CLI seguros para exportar e importar datos base cifrados.
"""
import base64
import json
import logging
import os
import secrets
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Tuple

import click
from cryptography.fernet import Fernet, InvalidToken
from flask.cli import with_appcontext

from src.database.db import DatabaseError, get_connection

LOGGER = logging.getLogger("secure_seed")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)

MODULE_PATH = Path(__file__).resolve()
SRC_PATH = MODULE_PATH.parents[1]
BACKEND_PATH = MODULE_PATH.parents[2]
PROJECT_ROOT = MODULE_PATH.parents[3]
SEED_DIR = SRC_PATH / "database" / "seeders"
SEED_FILE = SEED_DIR / "secure_seed.bin"
ENV_EXAMPLE_PATH = PROJECT_ROOT / ".env.example"


def _ensure_seed_directory() -> None:
    SEED_DIR.mkdir(parents=True, exist_ok=True)


def _load_team_key() -> str:
    team_key = os.getenv("TEAM_KEY")
    if not team_key:
        raise click.ClickException(
            "TEAM_KEY no está definida en las variables de entorno. "
            "Agrega TEAM_KEY=. en tu .env antes de continuar."
        )
    cleaned_key = team_key.strip().lower()
    if not cleaned_key:
        raise click.ClickException("TEAM_KEY está vacía. Configúrala antes de continuar.")
    return cleaned_key


def _build_fernet(team_key_hex: str) -> Fernet:
    try:
        raw_key = bytes.fromhex(team_key_hex)
    except ValueError as exc:
        raise click.ClickException(
            "TEAM_KEY tiene un formato inválido. Debe ser una cadena hex generada con token_hex(32)."
        ) from exc

    if len(raw_key) != 32:
        raise click.ClickException(
            f"TEAM_KEY debe representar 32 bytes (64 caracteres hex). Longitud actual: {len(raw_key)} bytes."
        )

    fernet_key = base64.urlsafe_b64encode(raw_key)
    return Fernet(fernet_key)


def _json_default(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _parse_datetime(value: Any) -> Any:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    if isinstance(value, str):
        candidate = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(candidate)
        except ValueError:
            return value
        if parsed.tzinfo:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    return value


def _get_connection_checked():
    try:
        conn = get_connection()
    except DatabaseError as exc:
        raise click.ClickException(f"Error al obtener conexión con la base de datos: {exc}") from exc

    if conn is None:
        raise click.ClickException(
            "No se pudo obtener una conexión a la base de datos. Verifica tu configuración en .env."
        )
    return conn


def _fetch_table(cursor, query: str) -> List[Dict[str, Any]]:
    cursor.execute(query)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def _collect_dataset() -> Dict[str, Any]:
    conn = _get_connection_checked()
    cursor = conn.cursor(dictionary=True)
    try:
        dataset = {
            "metadata": {
                "version": 1,
                "exported_at": datetime.utcnow().isoformat() + "Z",
                "tables": [
                    "roles",
                    "tipo_pasto",
                    "tipo_vacuna",
                    "estado_ganado",
                    "personas",
                    "potrero",
                    "ganado",
                    "vacunacion",
                    "usuarios",
                ],
            }
        }

        dataset["roles"] = _fetch_table(
            cursor, "SELECT id, rol, descripcion FROM roles ORDER BY id"
        )
        dataset["tipo_pasto"] = _fetch_table(
            cursor, "SELECT id, tipo_pasto FROM tipo_pasto ORDER BY id"
        )
        dataset["tipo_vacuna"] = _fetch_table(
            cursor, "SELECT id, nombre_vacuna FROM tipo_vacuna ORDER BY id"
        )
        dataset["estado_ganado"] = _fetch_table(
            cursor, "SELECT id, tipo_estado FROM estado_ganado ORDER BY id"
        )
        dataset["personas"] = _fetch_table(
            cursor,
            (
                "SELECT id, id_rol, primer_nombre, segundo_nombre, primer_apellido, "
                "segundo_apellido, email, telefono, fecha_creacion "
                "FROM personas ORDER BY id"
            ),
        )
        dataset["potrero"] = _fetch_table(
            cursor,
            (
                "SELECT id, id_tipo_pasto, nombre, capacidad, hectareas, ocupacion, "
                "fecha_ultimo_uso, responsable_persona_id, proxima_limpieza, area, "
                "ultima_limpieza, descripcion, estado "
                "FROM potrero ORDER BY id"
            ),
        )
        dataset["ganado"] = _fetch_table(
            cursor,
            (
                "SELECT id, id_potrero, id_persona, id_revision, nombre, peso, raza, "
                "fecha_nacimiento, id_estado, sexo "
                "FROM ganado ORDER BY id"
            ),
        )
        dataset["vacunacion"] = _fetch_table(
            cursor,
            (
                "SELECT id, id_animal, fecha_aplicacion, proxima_dosis, responsable, "
                "estado, id_tipo_vacuna "
                "FROM vacunacion ORDER BY id"
            ),
        )

        usuarios = _fetch_table(
            cursor,
            (
                "SELECT id, id_persona, id_rol, contrasena, estado "
                "FROM usuarios ORDER BY id"
            ),
        )

        for usuario in usuarios:
            password = usuario.get("contrasena")
            if password and not password.startswith("$2"):
                raise click.ClickException(
                    "Se detectó una contraseña de usuario sin hash seguro. "
                    "Actualiza las contraseñas antes de exportar."
                )

        dataset["usuarios"] = usuarios

        return {
            key: json.loads(json.dumps(value, default=_json_default))
            for key, value in dataset.items()
        }
    finally:
        cursor.close()
        conn.close()


def _encrypt_payload(fernet: Fernet, data: Dict[str, Any]) -> bytes:
    payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    return fernet.encrypt(payload)


def _decrypt_payload(fernet: Fernet, content: bytes) -> Dict[str, Any]:
    try:
        decrypted = fernet.decrypt(content)
    except InvalidToken as exc:
        raise click.ClickException(
            "No se pudo descifrar secure_seed.bin. Verifica que TEAM_KEY sea la correcta."
        ) from exc

    try:
        return json.loads(decrypted.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise click.ClickException("El archivo secure_seed.bin está corrupto o no es JSON válido.") from exc


def _execute_many(cursor, query: str, params: Tuple[Any, ...]) -> None:
    cursor.execute(query, params)


def _import_roles(cursor, rows: List[Dict[str, Any]]) -> None:
    for row in rows:
        _execute_many(
            cursor,
            """
            INSERT INTO roles (id, rol, descripcion)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                rol = VALUES(rol),
                descripcion = VALUES(descripcion)
            """,
            (
                row.get("id"),
                row.get("rol"),
                row.get("descripcion"),
            ),
        )


def _import_tipo_pasto(cursor, rows: List[Dict[str, Any]]) -> None:
    for row in rows:
        _execute_many(
            cursor,
            """
            INSERT INTO tipo_pasto (id, tipo_pasto)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                tipo_pasto = VALUES(tipo_pasto)
            """,
            (row.get("id"), row.get("tipo_pasto")),
        )


def _import_tipo_vacuna(cursor, rows: List[Dict[str, Any]]) -> None:
    for row in rows:
        _execute_many(
            cursor,
            """
            INSERT INTO tipo_vacuna (id, nombre_vacuna)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                nombre_vacuna = VALUES(nombre_vacuna)
            """,
            (row.get("id"), row.get("nombre_vacuna")),
        )


def _import_estado_ganado(cursor, rows: List[Dict[str, Any]]) -> None:
    for row in rows:
        _execute_many(
            cursor,
            """
            INSERT INTO estado_ganado (id, tipo_estado)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                tipo_estado = VALUES(tipo_estado)
            """,
            (row.get("id"), row.get("tipo_estado")),
        )


def _import_personas(cursor, rows: List[Dict[str, Any]]) -> None:
    for row in rows:
        _execute_many(
            cursor,
            """
            INSERT INTO personas (
                id, id_rol, primer_nombre, segundo_nombre, primer_apellido,
                segundo_apellido, email, telefono, fecha_creacion
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                id_rol = VALUES(id_rol),
                primer_nombre = VALUES(primer_nombre),
                segundo_nombre = VALUES(segundo_nombre),
                primer_apellido = VALUES(primer_apellido),
                segundo_apellido = VALUES(segundo_apellido),
                telefono = VALUES(telefono),
                fecha_creacion = VALUES(fecha_creacion)
            """,
            (
                row.get("id"),
                row.get("id_rol"),
                row.get("primer_nombre"),
                row.get("segundo_nombre"),
                row.get("primer_apellido"),
                row.get("segundo_apellido"),
                row.get("email"),
                row.get("telefono"),
                _parse_datetime(row.get("fecha_creacion")),
            ),
        )


def _import_potreros(cursor, rows: List[Dict[str, Any]]) -> None:
    for row in rows:
        _execute_many(
            cursor,
            """
            INSERT INTO potrero (
                id, id_tipo_pasto, nombre, capacidad, hectareas, ocupacion,
                fecha_ultimo_uso, responsable_persona_id, proxima_limpieza,
                area, ultima_limpieza, descripcion, estado
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                id_tipo_pasto = VALUES(id_tipo_pasto),
                nombre = VALUES(nombre),
                capacidad = VALUES(capacidad),
                hectareas = VALUES(hectareas),
                ocupacion = VALUES(ocupacion),
                fecha_ultimo_uso = VALUES(fecha_ultimo_uso),
                responsable_persona_id = VALUES(responsable_persona_id),
                proxima_limpieza = VALUES(proxima_limpieza),
                area = VALUES(area),
                ultima_limpieza = VALUES(ultima_limpieza),
                descripcion = VALUES(descripcion),
                estado = VALUES(estado)
            """,
            (
                row.get("id"),
                row.get("id_tipo_pasto"),
                row.get("nombre"),
                row.get("capacidad"),
                row.get("hectareas"),
                row.get("ocupacion"),
                _parse_datetime(row.get("fecha_ultimo_uso")),
                row.get("responsable_persona_id"),
                _parse_datetime(row.get("proxima_limpieza")),
                row.get("area"),
                _parse_datetime(row.get("ultima_limpieza")),
                row.get("descripcion"),
                row.get("estado"),
            ),
        )


def _import_ganado(cursor, rows: List[Dict[str, Any]]) -> None:
    for row in rows:
        _execute_many(
            cursor,
            """
            INSERT INTO ganado (
                id, id_potrero, id_persona, id_revision, nombre, peso, raza,
                fecha_nacimiento, id_estado, sexo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                id_potrero = VALUES(id_potrero),
                id_persona = VALUES(id_persona),
                id_revision = VALUES(id_revision),
                nombre = VALUES(nombre),
                peso = VALUES(peso),
                raza = VALUES(raza),
                fecha_nacimiento = VALUES(fecha_nacimiento),
                id_estado = VALUES(id_estado),
                sexo = VALUES(sexo)
            """,
            (
                row.get("id"),
                row.get("id_potrero"),
                row.get("id_persona"),
                row.get("id_revision"),
                row.get("nombre"),
                row.get("peso"),
                row.get("raza"),
                _parse_datetime(row.get("fecha_nacimiento")),
                row.get("id_estado"),
                row.get("sexo"),
            ),
        )


def _import_vacunacion(cursor, rows: List[Dict[str, Any]]) -> None:
    for row in rows:
        _execute_many(
            cursor,
            """
            INSERT INTO vacunacion (
                id, id_animal, fecha_aplicacion, proxima_dosis, responsable,
                estado, id_tipo_vacuna
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                id_animal = VALUES(id_animal),
                fecha_aplicacion = VALUES(fecha_aplicacion),
                proxima_dosis = VALUES(proxima_dosis),
                responsable = VALUES(responsable),
                estado = VALUES(estado),
                id_tipo_vacuna = VALUES(id_tipo_vacuna)
            """,
            (
                row.get("id"),
                row.get("id_animal"),
                _parse_datetime(row.get("fecha_aplicacion")),
                _parse_datetime(row.get("proxima_dosis")),
                row.get("responsable"),
                row.get("estado"),
                row.get("id_tipo_vacuna"),
            ),
        )


def _import_usuarios(cursor, rows: List[Dict[str, Any]]) -> None:
    for row in rows:
        _execute_many(
            cursor,
            """
            INSERT INTO usuarios (
                id, id_persona, id_rol, contrasena, estado
            )
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                id_persona = VALUES(id_persona),
                id_rol = VALUES(id_rol),
                contrasena = VALUES(contrasena),
                estado = VALUES(estado)
            """,
            (
                row.get("id"),
                row.get("id_persona"),
                row.get("id_rol"),
                row.get("contrasena"),
                row.get("estado"),
            ),
        )


def _import_dataset(data: Dict[str, Any]) -> None:
    expected_tables = data.get("metadata", {}).get("tables", [])
    missing_tables = [
        table
        for table in ["roles", "tipo_pasto", "tipo_vacuna", "estado_ganado", "personas", "potrero", "ganado", "vacunacion", "usuarios"]
        if table not in data
    ]
    if missing_tables:
        raise click.ClickException(
            f"El archivo de semillas cifrado no contiene todas las tablas requeridas: {', '.join(missing_tables)}"
        )

    conn = _get_connection_checked()
    cursor = conn.cursor(dictionary=True)

    try:
        conn.start_transaction()
        _import_roles(cursor, data["roles"])
        _import_tipo_pasto(cursor, data["tipo_pasto"])
        _import_tipo_vacuna(cursor, data["tipo_vacuna"])
        _import_estado_ganado(cursor, data["estado_ganado"])
        _import_personas(cursor, data["personas"])
        _import_potreros(cursor, data["potrero"])
        _import_ganado(cursor, data["ganado"])
        _import_vacunacion(cursor, data["vacunacion"])
        _import_usuarios(cursor, data["usuarios"])
        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise click.ClickException(f"No se pudo importar el dataset cifrado: {exc}") from exc
    finally:
        cursor.close()
        conn.close()


@click.command("seed:secure_export")
@with_appcontext
def secure_export() -> None:
    """Exporta datos base a un archivo cifrado secure_seed.bin."""
    LOGGER.info("Iniciando exportación cifrada de seeders...")
    _ensure_seed_directory()
    team_key_hex = _load_team_key()
    fernet = _build_fernet(team_key_hex)

    dataset = _collect_dataset()
    encrypted = _encrypt_payload(fernet, dataset)

    with open(SEED_FILE, "wb") as output:
        output.write(encrypted)

    LOGGER.info("Exportación completada. Archivo generado en %s", SEED_FILE)
    click.echo(f"[OK] Datos cifrados exportados en: {SEED_FILE}")


@click.command("seed:secure_import")
@with_appcontext
def secure_import() -> None:
    """Importa datos base desde secure_seed.bin aplicando inserciones idempotentes."""
    LOGGER.info("Iniciando importación cifrada de seeders...")
    if not SEED_FILE.exists():
        raise click.ClickException(
            f"No se encontró el archivo {SEED_FILE}. Ejecuta seed:secure_export en una máquina con datos válidos."
        )

    team_key_hex = _load_team_key()
    fernet = _build_fernet(team_key_hex)

    with open(SEED_FILE, "rb") as encrypted_file:
        encrypted_content = encrypted_file.read()

    dataset = _decrypt_payload(fernet, encrypted_content)
    _import_dataset(dataset)

    LOGGER.info("Importación completada correctamente.")
    click.echo("[OK] Importación completada sin duplicar registros.")


def _update_env_example(team_key: str) -> None:
    if not ENV_EXAMPLE_PATH.exists():
        LOGGER.warning("No se encontró .env.example; omitiendo actualización.")
        return

    with open(ENV_EXAMPLE_PATH, "r", encoding="utf-8") as env_file:
        lines = env_file.readlines()

    updated = []
    team_key_line_found = False
    secret_key_line_found = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("TEAM_KEY="):
            updated.append(f"TEAM_KEY={team_key}\n")
            team_key_line_found = True
        elif stripped.startswith("SECRET_KEY="):
            updated.append("SECRET_KEY=\n")
            secret_key_line_found = True
        else:
            updated.append(line)

    if not team_key_line_found:
        updated.append("\n# Clave compartida del equipo para seeders cifrados (hex). El líder del equipo la genera y la comparte:\n")
        updated.append(f"TEAM_KEY={team_key}\n")

    if not secret_key_line_found:
        updated.insert(1, "SECRET_KEY=\n")

    with open(ENV_EXAMPLE_PATH, "w", encoding="utf-8") as env_file:
        env_file.writelines(updated)

    click.echo("[INFO] Se actualizó TEAM_KEY en .env.example (solo como referencia).")


@click.command("team:generate_key")
@with_appcontext
def team_generate_key() -> None:
    """Genera una TEAM_KEY segura y ofrece actualizar .env.example."""
    team_key = secrets.token_hex(32)
    click.echo(f"TEAM_KEY generada: {team_key}")
    if click.confirm(
        "¿Deseas escribir esta TEAM_KEY como ejemplo en .env.example? (No modifica tu .env actual)",
        default=False,
    ):
        _update_env_example(team_key)
    else:
        click.echo("Recuerda compartir la TEAM_KEY por un canal seguro.")


COMMANDS = [secure_export, secure_import, team_generate_key]


