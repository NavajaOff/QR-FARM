#!/usr/bin/env python3
"""Herramienta para regenerar códigos QR archivando versiones anteriores."""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


LOGGER = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent
SRC_DIR = BACKEND_DIR / "src"
QR_DIR = BACKEND_DIR / "qr"
ARCHIVE_DIR = QR_DIR / "desactualizados"
TIMESTAMP_FORMAT = "%Y-%m-%d_%H%M%S"


if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from src.database.db import get_connection  # noqa: E402  pylint: disable=wrong-import-position
from src.services.animal_service import GanadoService  # noqa: E402  pylint: disable=wrong-import-position
from src.services.qr_service import QRService  # noqa: E402  pylint: disable=wrong-import-position


def configure_logging(log_level: int = logging.INFO) -> None:
    """Configura el logger raíz para el script."""
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def slugify_animal_name(animal_name: str) -> str:
    """Normaliza el nombre del animal para usarlo en rutas de archivos."""
    normalized = "".join(
        character.lower() if character.isalnum() else "_"
        for character in animal_name.strip()
    )
    normalized = normalized.strip("_")
    return normalized or "animal"


def ensure_directory_exists(directory: Path) -> None:
    """Crea un directorio si aún no existe."""
    directory.mkdir(parents=True, exist_ok=True)


def move_old_qr(animal_name: str, old_qr_path: Path) -> Optional[Path]:
    """Mueve un código QR antiguo del animal a la carpeta desactualizados/<animal_name>/."""
    if not old_qr_path.exists():
        LOGGER.info("No se encontró QR anterior para mover en %s", old_qr_path)
        return None

    safe_name = slugify_animal_name(animal_name)
    archived_qr_dir = ARCHIVE_DIR / safe_name
    ensure_directory_exists(archived_qr_dir)

    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    destination = archived_qr_dir / f"{safe_name}_qr_{timestamp}{old_qr_path.suffix}"

    suffix_counter = 1
    while destination.exists():
        destination = archived_qr_dir / f"{safe_name}_qr_{timestamp}_{suffix_counter}{old_qr_path.suffix}"
        suffix_counter += 1

    try:
        shutil.move(str(old_qr_path), destination)
        LOGGER.info("QR anterior movido a %s", destination)
        return destination
    except OSError as exc:
        LOGGER.exception("No se pudo mover el QR anterior: %s", exc)
        raise


def _build_datos_extra(gathered_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepara los datos adicionales a incluir en el QR."""
    potrero_nombre = gathered_data.get("potrero_nombre")
    potrero_info: Optional[Dict[str, Any]] = None
    if potrero_nombre:
        potrero_info = {"nombre": potrero_nombre}

    return {
        "estado": gathered_data.get("estado"),
        "estado_salud": gathered_data.get("estado_salud"),
        "potrero": potrero_info,
        "peso": gathered_data.get("peso"),
        "sexo": gathered_data.get("sexo"),
        "fecha_nacimiento": gathered_data.get("fecha_nacimiento"),
    }


def _generate_qr_filename_from_code(codigo_qr: str) -> Path:
    """Obtiene la ruta completa del archivo QR a partir del código."""
    ensure_directory_exists(QR_DIR)
    return QR_DIR / f"{codigo_qr}.png"


def generate_new_qr(
    animal_id: int,
    animal_name: str,
    owner_name: str,
    owner_contact: str,
    datos_extra: Dict[str, Any],
) -> Path:
    """Genera el código QR actualizado y devuelve la ruta donde se guardó."""
    original_cwd = Path.cwd()
    try:
        os.chdir(BACKEND_DIR)
        codigo_qr = QRService.generar_codigo_qr(
            id_ganado=animal_id,
            nombre_ganado=animal_name,
            nombre_propietario=owner_name,
            contacto=owner_contact,
            datos_extra=datos_extra,
        )
    finally:
        os.chdir(original_cwd)

    new_qr_path = _generate_qr_filename_from_code(codigo_qr)
    LOGGER.info("QR actualizado generado en %s", new_qr_path)
    return new_qr_path


def persist_qr_code(animal_id: int, codigo_qr: str) -> None:
    """Actualiza la base de datos con el nuevo código QR."""
    conn = get_connection()
    if conn is None:
        raise ConnectionError("No se pudo establecer conexión con la base de datos.")

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE qr
                SET codigo_qr = %s, fecha_actualizacion = NOW()
                WHERE id_ganado = %s
                """,
                (codigo_qr, animal_id),
            )
            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO qr (id_ganado, codigo_qr, fecha_creacion, fecha_actualizacion)
                    VALUES (%s, %s, NOW(), NOW())
                    """,
                    (animal_id, codigo_qr),
                )

            cursor.execute(
                """
                UPDATE ganado
                SET codigo_qr = %s, updated_at = NOW()
                WHERE id = %s
                """,
                (codigo_qr, animal_id),
            )
        conn.commit()
    except Exception as exc:  # pylint: disable=broad-except
        conn.rollback()
        LOGGER.exception("Error actualizando registros del QR: %s", exc)
        raise
    finally:
        conn.close()


def get_animal_data(animal_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene los datos detallados del animal requeridos para regenerar el QR."""
    try:
        return GanadoService.obtener_ganado_detallado(animal_id)
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.exception("Error obteniendo datos del animal %s: %s", animal_id, exc)
        return None


def update_qr_for_animal(animal_id: int) -> bool:
    """Regenera el QR de un animal, archivando el anterior si existiera."""
    animal_data = get_animal_data(animal_id)
    if not animal_data:
        LOGGER.error("No se encontraron datos para el animal con id %s", animal_id)
        return False

    animal_name = animal_data.get("nombre") or "Animal"
    existing_qr = QRService.obtener_qr_por_ganado(animal_id)
    codigo_qr_existente = (
        (existing_qr or {}).get("codigo_qr")
        or animal_data.get("codigo_qr")
    )

    if codigo_qr_existente:
        old_qr_path = _generate_qr_filename_from_code(codigo_qr_existente)
        try:
            move_old_qr(animal_name, old_qr_path)
        except OSError:
            LOGGER.error(
                "No se pudo archivar el QR anterior del animal %s; se aborta la actualización.",
                animal_id,
            )
            return False

    datos_extra = _build_datos_extra(animal_data)
    try:
        new_qr_path = generate_new_qr(
            animal_id=animal_id,
            animal_name=animal_name,
            owner_name=animal_data.get("propietario_nombre") or "",
            owner_contact=animal_data.get("propietario_telefono") or "",
            datos_extra=datos_extra,
        )
    except Exception:
        LOGGER.error("No se pudo generar el nuevo QR para el animal %s", animal_id)
        return False

    persist_qr_code(animal_id, new_qr_path.stem)
    return True


def parse_arguments() -> argparse.Namespace:
    """Define y procesa los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Regenera el código QR de un animal, archivando versiones anteriores."
    )
    parser.add_argument("animal_id", type=int, help="Identificador del animal a actualizar.")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Nivel de logging deseado (por defecto: INFO).",
    )
    return parser.parse_args()


def main() -> None:
    """Punto de entrada del script."""
    args = parse_arguments()
    configure_logging(getattr(logging, args.log_level.upper(), logging.INFO))

    success = update_qr_for_animal(args.animal_id)
    if success:
        LOGGER.info("QR actualizado correctamente para el animal %s", args.animal_id)
    else:
        LOGGER.error("No se pudo actualizar el QR para el animal %s", args.animal_id)


if __name__ == "__main__":
    main()