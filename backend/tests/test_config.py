"""Pruebas para funciones de configuración."""

from __future__ import annotations

import pytest

from .helpers import load_module, prepare_environment


def test_require_env_return(monkeypatch):
    """El helper debe obtener variables existentes."""
    prepare_environment(monkeypatch)
    config_module = load_module("backend_config_module", "config.py")

    assert config_module._require_env("SECRET_KEY") == "demo-key-value"


def test_require_env_missing(monkeypatch):
    """Debe lanzar ValueError cuando falta la variable."""
    prepare_environment(monkeypatch)
    config_module = load_module("backend_config_module_missing", "config.py")

    monkeypatch.delenv("VARIABLE_INEXISTENTE", raising=False)
    with pytest.raises(ValueError):
        config_module._require_env("VARIABLE_INEXISTENTE")


def test_require_int_env_success(monkeypatch):
    """Convierte correctamente variables numéricas."""
    prepare_environment(monkeypatch)
    config_module = load_module("backend_config_module_int", "config.py")

    assert config_module._require_int_env("DB_PORT") == 3306
    assert config_module._require_int_env("DB_POOL_SIZE") == 5


def test_require_int_env_invalid(monkeypatch):
    """Lanza ValueError si el contenido no es entero."""
    prepare_environment(monkeypatch)
    config_module = load_module("backend_config_module_invalid", "config.py")

    monkeypatch.setenv("INVALID_INT_VALUE", "no-entero")
    with pytest.raises(ValueError):
        config_module._require_int_env("INVALID_INT_VALUE")


def test_src_config_require_env(monkeypatch):
    """Verifica el helper en la configuración de src."""
    prepare_environment(monkeypatch)
    src_config_module = load_module("src_config_module", "src/config.py")

    assert src_config_module._require_env("DB_USER") == "test_user"

    monkeypatch.delenv("OTRA_VARIABLE_INEXISTENTE", raising=False)
    with pytest.raises(ValueError):
        src_config_module._require_env("OTRA_VARIABLE_INEXISTENTE")

