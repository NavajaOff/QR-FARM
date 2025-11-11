"""Pruebas para utilidades del módulo principal de Flask."""

from __future__ import annotations

from .helpers import load_module, prepare_environment


def test_build_sqlalchemy_uri_from_env(monkeypatch):
    """Construye la URI usando las variables definidas."""
    prepare_environment(monkeypatch)
    app_module = load_module("app_module_env", "app.py")

    uri = app_module._build_sqlalchemy_uri()
    assert uri == "mysql+mysqlconnector://test_user:test_password@localhost:3306/test_db"


def test_build_sqlalchemy_uri_uses_database_url(monkeypatch):
    """Respeta DATABASE_URL cuando está definida."""
    prepare_environment(monkeypatch, {"DATABASE_URL": "mysql://example.com/db"})
    app_module = load_module("app_module_database_url", "app.py")

    assert app_module._build_sqlalchemy_uri() == "mysql://example.com/db"

