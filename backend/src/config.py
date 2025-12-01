"""Configuration module."""
import os


def _require_env(nombre_variable: str) -> str:
    """Obtiene una variable de entorno obligatoria."""
    valor = os.getenv(nombre_variable)
    if valor is None:
        raise ValueError(f"Variable de entorno obligatoria no configurada: {nombre_variable}")
    return valor


def _require_int_env(nombre_variable: str) -> int:
    """Obtiene una variable de entorno obligatoria y la convierte a entero."""
    valor_str = _require_env(nombre_variable)
    try:
        return int(valor_str)
    except ValueError:
        raise ValueError(f"La variable de entorno {nombre_variable} debe ser un número entero, pero se obtuvo: {valor_str}")


class Config:
    """Base configuration."""

    # Secret key para JWT y sesiones
    SECRET_KEY: str = _require_env('SECRET_KEY')

    # Configuración de la base de datos
    DB_HOST: str = _require_env('DB_HOST')
    DB_USER: str = _require_env('DB_USER')
    DB_PASSWORD: str = _require_env('DB_PASSWORD')
    DB_NAME: str = _require_env('DB_NAME')

    # Configuración de JWT
    JWT_ACCESS_TOKEN_EXPIRES: int = 24 * 60 * 60  # 24 horas en segundos

# Log de configuración cargada para debug
print("Configuración cargada exitosamente: SECRET_KEY presente, DB_HOST =", Config.DB_HOST, ", DB_NAME =", Config.DB_NAME)