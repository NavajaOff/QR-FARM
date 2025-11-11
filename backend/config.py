"""Configuration module for the application."""
import os
from typing import Any, Dict


def _require_env(nombre_variable: str) -> str:
    """Obtiene una variable de entorno obligatoria."""
    valor = os.getenv(nombre_variable)
    if valor is None:
        raise ValueError(f"Variable de entorno obligatoria no configurada: {nombre_variable}")
    return valor


def _require_int_env(nombre_variable: str) -> int:
    """Obtiene una variable de entorno entera obligatoria."""
    valor = _require_env(nombre_variable)
    try:
        return int(valor)
    except ValueError as error:
        raise ValueError(f"La variable de entorno {nombre_variable} debe ser un número entero") from error


class Config:
    """Configuration class."""

    SECRET_KEY: str = _require_env('SECRET_KEY')

    # Database configuration
    DB_CONFIG: Dict[str, Any] = {
        'host': _require_env('DB_HOST'),
        'user': _require_env('DB_USER'),
        'password': _require_env('DB_PASSWORD'),
        'database': _require_env('DB_NAME'),
        'port': _require_int_env('DB_PORT'),
        'raise_on_warnings': True,
        'autocommit': False,  # Control explícito de transacciones
        'pool_name': 'qr_farm_pool',
        'pool_size': _require_int_env('DB_POOL_SIZE'),
        'pool_reset_session': True
    }

    # JWT configuration
    JWT_SECRET_KEY: str = _require_env('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES: int = _require_int_env('JWT_ACCESS_TOKEN_EXPIRES')

    # Application configuration
    DEBUG: bool = os.getenv('FLASK_ENV') == 'development'
    TESTING: bool = False
    JSON_SORT_KEYS: bool = False
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max-limit for file uploads
