"""Pruebas para funciones de configuración."""

from __future__ import annotations

import pytest

from .helpers import prepare_environment


def test_require_env_return(monkeypatch):
    """El helper debe obtener variables existentes."""
    prepare_environment(monkeypatch)

    from src.config import _require_env
    assert _require_env("SECRET_KEY") == "demo-key-value"


def test_require_env_missing(monkeypatch):
    """Debe lanzar ValueError cuando falta la variable."""
    prepare_environment(monkeypatch)

    from src.config import _require_env
    monkeypatch.delenv("VARIABLE_INEXISTENTE", raising=False)
    with pytest.raises(ValueError):
        _require_env("VARIABLE_INEXISTENTE")


def test_require_int_env_success(monkeypatch):
    """Convierte correctamente variables numéricas."""
    prepare_environment(monkeypatch)

    from src.config import _require_int_env
    assert _require_int_env("DB_PORT") == 3306
    assert _require_int_env("DB_POOL_SIZE") == 5


def test_require_int_env_invalid(monkeypatch):
    """Lanza ValueError si el contenido no es entero."""
    prepare_environment(monkeypatch)

    from src.config import _require_int_env
    monkeypatch.setenv("INVALID_INT_VALUE", "no-entero")
    with pytest.raises(ValueError):
        _require_int_env("INVALID_INT_VALUE")


def test_config_class_attributes(monkeypatch):
    """Verifica que la clase Config tenga los atributos correctos."""
    prepare_environment(monkeypatch)

    # Forzar recarga del módulo para que tome las nuevas variables de entorno
    import importlib
    import src.config
    importlib.reload(src.config)

    assert src.config.Config.SECRET_KEY == "demo-key-value"
    assert src.config.Config.DB_HOST == "localhost"
    assert src.config.Config.DB_USER == "test_user"
    assert src.config.Config.DB_PASSWORD == "dummy-db-pwd"
    assert src.config.Config.DB_NAME == "test_db"
    assert src.config.Config.JWT_ACCESS_TOKEN_EXPIRES == 24 * 60 * 60


def test_config_initialization(monkeypatch):
    """Verifica que la configuración se inicialice correctamente."""
    prepare_environment(monkeypatch)

    # Forzar recarga del módulo
    import importlib
    import src.config
    importlib.reload(src.config)

    # Verificar que no haya errores al acceder a la configuración
    config = src.config.Config()
    assert hasattr(config, 'SECRET_KEY')
    assert hasattr(config, 'DB_HOST')
    assert hasattr(config, 'DB_USER')
    assert hasattr(config, 'DB_PASSWORD')
    assert hasattr(config, 'DB_NAME')
    assert hasattr(config, 'JWT_ACCESS_TOKEN_EXPIRES')

