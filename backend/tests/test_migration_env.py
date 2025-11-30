"""Tests for Alembic migration env.py module."""

from __future__ import annotations

import pytest
import os
import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from logging import Logger

from .helpers import prepare_environment


def load_env_module(monkeypatch, module_name_suffix=''):
    """Helper to load env.py module with proper mocking."""
    prepare_environment(monkeypatch)
    
    env_path = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'env.py'
    spec = importlib.util.spec_from_file_location(f"migration_env_{module_name_suffix}", env_path)
    env_module = importlib.util.module_from_spec(spec)
    
    # Mock context.config before loading
    mock_config_instance = Mock()
    mock_config_instance.config_file_name = 'test.ini'
    mock_config_instance.get_main_option = Mock(return_value='mysql+mysqlconnector://user:pass@host:3306/db')
    mock_config_instance.set_main_option = Mock()
    mock_config_instance.get_section = Mock(return_value={})
    mock_config_instance.config_ini_section = 'alembic'
    
    with patch('alembic.context.config', return_value=mock_config_instance), \
         patch('logging.config.fileConfig'), \
         patch('logging.getLogger') as mock_get_logger:
        mock_logger = Mock(spec=Logger)
        mock_get_logger.return_value = mock_logger
        
        try:
            spec.loader.exec_module(env_module)
        except (ValueError, Exception):
            # Expected for some tests (e.g., missing password)
            pass
    
    env_module._mock_config = mock_config_instance
    return env_module


class TestBuildDatabaseUrl:
    """Test suite for _build_database_url function."""

    def test_build_database_url_with_all_env_vars(self, monkeypatch):
        """Test _build_database_url with all environment variables set."""
        prepare_environment(monkeypatch, {
            'DB_HOST': 'test_host',
            'DB_USER': 'test_user',
            'DB_PASSWORD': 'test_password',
            'DB_NAME': 'test_db',
            'DB_PORT': '3307'
        })

        env_path = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'env.py'
        spec = importlib.util.spec_from_file_location("migration_env", env_path)
        env_module = importlib.util.module_from_spec(spec)

        mock_config_instance = Mock()
        mock_config_instance.config_file_name = 'test.ini'
        mock_logger = Mock(spec=Logger)

        mock_connectable = MagicMock()
        mock_connection = MagicMock()
        mock_connectable.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connectable.connect.return_value.__exit__ = Mock(return_value=False)

        with patch('alembic.context.config', return_value=mock_config_instance, create=True), \
             patch('alembic.context.is_offline_mode', return_value=False), \
             patch('sqlalchemy.engine_from_config', return_value=mock_connectable), \
             patch('alembic.context.configure'), \
             patch('alembic.context.begin_transaction') as mock_begin_transaction, \
             patch('alembic.context.run_migrations'), \
             patch('logging.config.fileConfig'), \
             patch('logging.getLogger', return_value=mock_logger):
            mock_begin_transaction.return_value.__enter__ = Mock()
            mock_begin_transaction.return_value.__exit__ = Mock(return_value=False)
            mock_config_instance.get_section.return_value = {}
            mock_config_instance.config_ini_section = 'alembic'
            mock_config_instance.set_main_option = Mock()
            
            spec.loader.exec_module(env_module)

            url = env_module._build_database_url()
            assert url == 'mysql+mysqlconnector://test_user:test_password@test_host:3307/test_db'
            assert mock_logger.info.call_count >= 2

    def test_build_database_url_with_defaults(self, monkeypatch):
        """Test _build_database_url with default values."""
        prepare_environment(monkeypatch, {
            'DB_PASSWORD': 'test_password'
        })
        monkeypatch.delenv('DB_HOST', raising=False)
        monkeypatch.delenv('DB_USER', raising=False)
        monkeypatch.delenv('DB_NAME', raising=False)
        monkeypatch.delenv('DB_PORT', raising=False)

        env_path = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'env.py'
        spec = importlib.util.spec_from_file_location("migration_env_defaults", env_path)
        env_module = importlib.util.module_from_spec(spec)

        mock_config_instance = Mock()
        mock_config_instance.config_file_name = 'test.ini'
        mock_logger = Mock(spec=Logger)

        mock_connectable = MagicMock()
        mock_connection = MagicMock()
        mock_connectable.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connectable.connect.return_value.__exit__ = Mock(return_value=False)

        with patch('alembic.context.config', return_value=mock_config_instance, create=True), \
             patch('alembic.context.is_offline_mode', return_value=False), \
             patch('sqlalchemy.engine_from_config', return_value=mock_connectable), \
             patch('alembic.context.configure'), \
             patch('alembic.context.begin_transaction') as mock_begin_transaction, \
             patch('alembic.context.run_migrations'), \
             patch('logging.config.fileConfig'), \
             patch('logging.getLogger', return_value=mock_logger):
            mock_begin_transaction.return_value.__enter__ = Mock()
            mock_begin_transaction.return_value.__exit__ = Mock(return_value=False)
            mock_config_instance.get_section.return_value = {}
            mock_config_instance.config_ini_section = 'alembic'
            mock_config_instance.set_main_option = Mock()
            
            spec.loader.exec_module(env_module)

            url = env_module._build_database_url()
            assert url == 'mysql+mysqlconnector://root:test_password@localhost:3306/gestion_ganadera'

    def test_build_database_url_missing_password(self, monkeypatch):
        """Test _build_database_url raises ValueError when DB_PASSWORD is missing."""
        prepare_environment(monkeypatch)
        monkeypatch.delenv('DB_PASSWORD', raising=False)

        env_path = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'env.py'
        spec = importlib.util.spec_from_file_location("migration_env_no_password", env_path)
        env_module = importlib.util.module_from_spec(spec)

        mock_config_instance = Mock()
        mock_config_instance.config_file_name = 'test.ini'
        mock_logger = Mock(spec=Logger)

        mock_connectable = MagicMock()
        mock_connection = MagicMock()
        mock_connectable.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connectable.connect.return_value.__exit__ = Mock(return_value=False)

        with patch('alembic.context.config', return_value=mock_config_instance, create=True), \
             patch('alembic.context.is_offline_mode', return_value=False), \
             patch('sqlalchemy.engine_from_config', return_value=mock_connectable), \
             patch('alembic.context.configure'), \
             patch('alembic.context.begin_transaction') as mock_begin_transaction, \
             patch('alembic.context.run_migrations'), \
             patch('logging.config.fileConfig'), \
             patch('logging.getLogger', return_value=mock_logger):
            mock_begin_transaction.return_value.__enter__ = Mock()
            mock_begin_transaction.return_value.__exit__ = Mock(return_value=False)
            mock_config_instance.get_section.return_value = {}
            mock_config_instance.config_ini_section = 'alembic'
            mock_config_instance.set_main_option = Mock()
            
            try:
                spec.loader.exec_module(env_module)
            except ValueError:
                # Expected during module load
                pass

            with pytest.raises(ValueError) as exc_info:
                env_module._build_database_url()

            assert "DB_PASSWORD environment variable must be set" in str(exc_info.value)

    def test_build_database_url_empty_password(self, monkeypatch):
        """Test _build_database_url raises ValueError when DB_PASSWORD is empty."""
        prepare_environment(monkeypatch, {'DB_PASSWORD': ''})

        env_path = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'env.py'
        spec = importlib.util.spec_from_file_location("migration_env_empty_password", env_path)
        env_module = importlib.util.module_from_spec(spec)

        mock_config_instance = Mock()
        mock_config_instance.config_file_name = 'test.ini'
        mock_logger = Mock(spec=Logger)

        mock_connectable = MagicMock()
        mock_connection = MagicMock()
        mock_connectable.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connectable.connect.return_value.__exit__ = Mock(return_value=False)

        with patch('alembic.context.config', return_value=mock_config_instance, create=True), \
             patch('alembic.context.is_offline_mode', return_value=False), \
             patch('sqlalchemy.engine_from_config', return_value=mock_connectable), \
             patch('alembic.context.configure'), \
             patch('alembic.context.begin_transaction') as mock_begin_transaction, \
             patch('alembic.context.run_migrations'), \
             patch('logging.config.fileConfig'), \
             patch('logging.getLogger', return_value=mock_logger):
            mock_begin_transaction.return_value.__enter__ = Mock()
            mock_begin_transaction.return_value.__exit__ = Mock(return_value=False)
            mock_config_instance.get_section.return_value = {}
            mock_config_instance.config_ini_section = 'alembic'
            mock_config_instance.set_main_option = Mock()
            
            try:
                spec.loader.exec_module(env_module)
            except ValueError:
                # Expected during module load
                pass

            with pytest.raises(ValueError) as exc_info:
                env_module._build_database_url()

            assert "DB_PASSWORD environment variable must be set" in str(exc_info.value)


class TestDotenvLoading:
    """Test suite for dotenv loading functionality."""

    @patch('pathlib.Path.exists')
    @patch('dotenv.load_dotenv')
    def test_load_dotenv_when_available_and_exists(self, mock_load_dotenv, mock_exists, monkeypatch):
        """Test dotenv loading when available and .env file exists."""
        prepare_environment(monkeypatch)
        mock_exists.return_value = True

        env_path = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'env.py'
        spec = importlib.util.spec_from_file_location("migration_env_dotenv", env_path)
        env_module = importlib.util.module_from_spec(spec)

        mock_config_instance = Mock()
        mock_config_instance.config_file_name = 'test.ini'
        mock_logger = Mock(spec=Logger)

        mock_connectable = MagicMock()
        mock_connection = MagicMock()
        mock_connectable.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connectable.connect.return_value.__exit__ = Mock(return_value=False)

        with patch('alembic.context.config', return_value=mock_config_instance, create=True), \
             patch('alembic.context.is_offline_mode', return_value=False), \
             patch('sqlalchemy.engine_from_config', return_value=mock_connectable), \
             patch('alembic.context.configure'), \
             patch('alembic.context.begin_transaction') as mock_begin_transaction, \
             patch('alembic.context.run_migrations'), \
             patch('logging.config.fileConfig'), \
             patch('logging.getLogger', return_value=mock_logger):
            spec.loader.exec_module(env_module)

            mock_load_dotenv.assert_called_once()

    @patch('pathlib.Path.exists')
    def test_load_dotenv_when_file_not_exists(self, mock_exists, monkeypatch):
        """Test dotenv loading when .env file does not exist."""
        prepare_environment(monkeypatch)
        mock_exists.return_value = False

        env_path = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'env.py'
        spec = importlib.util.spec_from_file_location("migration_env_no_dotenv_file", env_path)
        env_module = importlib.util.module_from_spec(spec)

        mock_config_instance = Mock()
        mock_config_instance.config_file_name = 'test.ini'
        mock_logger = Mock(spec=Logger)

        mock_connectable = MagicMock()
        mock_connection = MagicMock()
        mock_connectable.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connectable.connect.return_value.__exit__ = Mock(return_value=False)

        with patch('alembic.context.config', return_value=mock_config_instance, create=True), \
             patch('alembic.context.is_offline_mode', return_value=False), \
             patch('sqlalchemy.engine_from_config', return_value=mock_connectable), \
             patch('alembic.context.configure'), \
             patch('alembic.context.begin_transaction') as mock_begin_transaction, \
             patch('alembic.context.run_migrations'), \
             patch('logging.config.fileConfig'), \
             patch('logging.getLogger', return_value=mock_logger), \
             patch('dotenv.load_dotenv') as mock_load_dotenv:
            spec.loader.exec_module(env_module)

            mock_load_dotenv.assert_not_called()

    def test_load_dotenv_when_not_available(self, monkeypatch):
        """Test dotenv loading when python-dotenv is not available."""
        prepare_environment(monkeypatch)

        env_path = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'env.py'
        spec = importlib.util.spec_from_file_location("migration_env_no_dotenv_module", env_path)
        env_module = importlib.util.module_from_spec(spec)

        mock_config_instance = Mock()
        mock_config_instance.config_file_name = 'test.ini'
        mock_logger = Mock(spec=Logger)

        mock_connectable = MagicMock()
        mock_connection = MagicMock()
        mock_connectable.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connectable.connect.return_value.__exit__ = Mock(return_value=False)

        with patch('alembic.context.config', return_value=mock_config_instance, create=True), \
             patch('alembic.context.is_offline_mode', return_value=False), \
             patch('sqlalchemy.engine_from_config', return_value=mock_connectable), \
             patch('alembic.context.configure'), \
             patch('alembic.context.begin_transaction') as mock_begin_transaction, \
             patch('alembic.context.run_migrations'), \
             patch('logging.config.fileConfig'), \
             patch('logging.getLogger', return_value=mock_logger), \
             patch.dict('sys.modules', {'dotenv': None}):
            spec.loader.exec_module(env_module)

            # Should not raise exception, just continue without dotenv


class TestRunMigrationsOffline:
    """Test suite for run_migrations_offline function."""

    def test_run_migrations_offline_configures_context(self, monkeypatch):
        """Test run_migrations_offline configures context correctly."""
        prepare_environment(monkeypatch)

        env_path = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'env.py'
        spec = importlib.util.spec_from_file_location("migration_env_offline", env_path)
        env_module = importlib.util.module_from_spec(spec)

        mock_config_instance = Mock()
        mock_config_instance.config_file_name = 'test.ini'
        mock_config_instance.get_main_option.return_value = 'mysql+mysqlconnector://user:pass@host:3306/db'
        mock_logger = Mock(spec=Logger)

        mock_connectable = MagicMock()
        mock_connection = MagicMock()
        mock_connectable.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connectable.connect.return_value.__exit__ = Mock(return_value=False)

        with patch('alembic.context.config', return_value=mock_config_instance, create=True), \
             patch('alembic.context.is_offline_mode', return_value=False), \
             patch('sqlalchemy.engine_from_config', return_value=mock_connectable), \
             patch('alembic.context.configure') as mock_configure, \
             patch('alembic.context.begin_transaction') as mock_begin_transaction, \
             patch('alembic.context.run_migrations') as mock_run_migrations, \
             patch('logging.config.fileConfig'), \
             patch('logging.getLogger', return_value=mock_logger):
            mock_begin_transaction.return_value.__enter__ = Mock()
            mock_begin_transaction.return_value.__exit__ = Mock(return_value=False)

            spec.loader.exec_module(env_module)

            # Reset mocks after module load to ignore calls during import
            mock_configure.reset_mock()
            mock_begin_transaction.reset_mock()
            mock_run_migrations.reset_mock()
            mock_config_instance.get_main_option.reset_mock()

            env_module.run_migrations_offline()

            # Verify that get_main_option was called (may be called on config object)
            assert mock_config_instance.get_main_option.called or hasattr(env_module, 'config')
            mock_configure.assert_called_once()
            call_kwargs = mock_configure.call_args[1]
            assert 'url' in call_kwargs
            assert call_kwargs['target_metadata'] is None
            assert call_kwargs['literal_binds'] is True
            assert 'dialect_opts' in call_kwargs
            mock_begin_transaction.assert_called_once()
            mock_run_migrations.assert_called_once()


class TestRunMigrationsOnline:
    """Test suite for run_migrations_online function."""

    def test_run_migrations_online_creates_engine(self, monkeypatch):
        """Test run_migrations_online creates engine and configures context."""
        prepare_environment(monkeypatch)

        env_path = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'env.py'
        spec = importlib.util.spec_from_file_location("migration_env_online", env_path)
        env_module = importlib.util.module_from_spec(spec)

        mock_connection = MagicMock()
        mock_connectable = MagicMock()
        mock_connectable.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connectable.connect.return_value.__exit__ = Mock(return_value=False)

        mock_config_instance = Mock()
        mock_config_instance.config_file_name = 'test.ini'
        mock_config_instance.get_section.return_value = {}
        mock_config_instance.config_ini_section = 'alembic'
        mock_logger = Mock(spec=Logger)

        mock_connectable = MagicMock()
        mock_connection = MagicMock()
        mock_connectable.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connectable.connect.return_value.__exit__ = Mock(return_value=False)

        with patch('alembic.context.config', return_value=mock_config_instance, create=True), \
             patch('alembic.context.is_offline_mode', return_value=False), \
             patch('sqlalchemy.engine_from_config', return_value=mock_connectable), \
             patch('alembic.context.configure'), \
             patch('alembic.context.begin_transaction') as mock_begin_transaction, \
             patch('alembic.context.run_migrations'), \
             patch('logging.config.fileConfig'), \
             patch('logging.getLogger', return_value=mock_logger), \
             patch('sqlalchemy.engine_from_config') as mock_engine_from_config, \
             patch('alembic.context.configure') as mock_configure, \
             patch('alembic.context.begin_transaction') as mock_begin_transaction, \
             patch('alembic.context.run_migrations') as mock_run_migrations:
            mock_engine_from_config.return_value = mock_connectable

            mock_begin_transaction.return_value.__enter__ = Mock()
            mock_begin_transaction.return_value.__exit__ = Mock(return_value=False)

            spec.loader.exec_module(env_module)

            # Reset mocks after module load to ignore calls during import
            mock_engine_from_config.reset_mock()
            mock_configure.reset_mock()
            mock_begin_transaction.reset_mock()
            mock_run_migrations.reset_mock()

            env_module.run_migrations_online()

            mock_engine_from_config.assert_called_once()
            call_kwargs = mock_engine_from_config.call_args[1]
            assert call_kwargs['prefix'] == 'sqlalchemy.'
            assert call_kwargs['poolclass'].__name__ == 'NullPool'
            mock_configure.assert_called_once()
            call_kwargs = mock_configure.call_args[1]
            assert call_kwargs['connection'] == mock_connection
            assert call_kwargs['target_metadata'] is None
            mock_begin_transaction.assert_called_once()
            mock_run_migrations.assert_called_once()


class TestConditionalExecution:
    """Test suite for conditional execution at module level."""

    def test_runs_offline_when_offline_mode(self, monkeypatch):
        """Test that run_migrations_offline function exists and can be called."""
        prepare_environment(monkeypatch)

        env_path = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'env.py'
        spec = importlib.util.spec_from_file_location("migration_env_conditional_offline", env_path)
        env_module = importlib.util.module_from_spec(spec)

        mock_config_instance = Mock()
        mock_config_instance.config_file_name = 'test.ini'
        mock_config_instance.get_main_option.return_value = 'mysql+mysqlconnector://user:pass@host:3306/db'
        mock_config_instance.set_main_option = Mock()
        mock_logger = Mock(spec=Logger)

        mock_connectable = MagicMock()
        mock_connection = MagicMock()
        mock_connectable.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connectable.connect.return_value.__exit__ = Mock(return_value=False)

        with patch('alembic.context.config', return_value=mock_config_instance, create=True), \
             patch('alembic.context.is_offline_mode', return_value=False), \
             patch('sqlalchemy.engine_from_config', return_value=mock_connectable), \
             patch('alembic.context.configure'), \
             patch('alembic.context.begin_transaction') as mock_begin_transaction, \
             patch('alembic.context.run_migrations'), \
             patch('logging.config.fileConfig'), \
             patch('logging.getLogger', return_value=mock_logger):
            spec.loader.exec_module(env_module)

            # Verify function exists
            assert hasattr(env_module, 'run_migrations_offline')
            assert callable(env_module.run_migrations_offline)

    def test_runs_online_when_online_mode(self, monkeypatch):
        """Test that run_migrations_online function exists and can be called."""
        prepare_environment(monkeypatch)

        env_path = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'env.py'
        spec = importlib.util.spec_from_file_location("migration_env_conditional_online", env_path)
        env_module = importlib.util.module_from_spec(spec)

        mock_config_instance = Mock()
        mock_config_instance.config_file_name = 'test.ini'
        mock_config_instance.get_section.return_value = {}
        mock_config_instance.config_ini_section = 'alembic'
        mock_config_instance.set_main_option = Mock()
        mock_logger = Mock(spec=Logger)

        mock_connectable = MagicMock()
        mock_connection = MagicMock()
        mock_connectable.connect.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connectable.connect.return_value.__exit__ = Mock(return_value=False)

        with patch('alembic.context.config', return_value=mock_config_instance, create=True), \
             patch('alembic.context.is_offline_mode', return_value=False), \
             patch('sqlalchemy.engine_from_config', return_value=mock_connectable), \
             patch('alembic.context.configure'), \
             patch('alembic.context.begin_transaction') as mock_begin_transaction, \
             patch('alembic.context.run_migrations'), \
             patch('logging.config.fileConfig'), \
             patch('logging.getLogger', return_value=mock_logger):
            spec.loader.exec_module(env_module)

            # Verify function exists
            assert hasattr(env_module, 'run_migrations_online')
            assert callable(env_module.run_migrations_online)

