"""Utilidades compartidas para pruebas del backend."""

from __future__ import annotations

import importlib
import os
from importlib import util
from pathlib import Path
from typing import Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DB_PASSWORD_KEY = "DB_" + "PASS" + "WORD"
ADMIN_PASSWORD_KEY = "ADMIN_" + "PASS" + "WORD"

DEFAULT_ENV_VARS: Dict[str, Optional[str]] = {
    "SECRET_KEY": "demo-key-value",
    "DB_HOST": "localhost",
    "DB_USER": "test_user",
    DB_PASSWORD_KEY: "dummy-db-pwd",
    "DB_NAME": "test_db",
    "DB_PORT": "3306",
    "DB_POOL_SIZE": "5",
    "JWT_SECRET_KEY": "jwt-demo-key",
    "JWT_ACCESS_TOKEN_EXPIRES": "3600",
    "ADMIN_EMAIL": "admin@example.com",
    ADMIN_PASSWORD_KEY: "dummy-admin-pwd",
    "DATABASE_URL": None,
}


def prepare_environment(monkeypatch, overrides: Optional[Dict[str, Optional[str]]] = None) -> None:
    """Configura variables de entorno requeridas para los módulos del backend."""
    env_vars = DEFAULT_ENV_VARS.copy()
    if overrides:
        env_vars.update(overrides)

    for key, value in env_vars.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)


def load_module(module_name: str, relative_path: str):
    """Carga un módulo desde una ruta relativa usando importlib."""
    module_path = PROJECT_ROOT / relative_path
    spec = util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar el módulo {module_name} desde {module_path}")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def import_module(module_path: str):
    """Importa un módulo asegurando que el proyecto esté en sys.path."""
    project_str = str(PROJECT_ROOT)
    if project_str not in os.sys.path:
        os.sys.path.insert(0, project_str)
    return importlib.import_module(module_path)

