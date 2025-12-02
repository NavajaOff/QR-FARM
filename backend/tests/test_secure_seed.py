import pytest
from unittest.mock import Mock, patch, mock_open
import os
from pathlib import Path

from src.cli.secure_seed import (
    _load_team_key,
    _build_fernet,
    _json_default,
    _parse_datetime,
    _ensure_seed_directory,
    _encrypt_payload,
    _decrypt_payload,
    _update_env_example
)


class TestSecureSeed:
    def test_load_team_key_success(self):
        """Test _load_team_key with valid TEAM_KEY"""
        with patch.dict(os.environ, {'TEAM_KEY': 'test_key'}):
            result = _load_team_key()
            assert result == 'test_key'

    def test_load_team_key_missing(self):
        """Test _load_team_key with missing TEAM_KEY"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception) as exc_info:
                _load_team_key()
            assert 'TEAM_KEY no está definida' in str(exc_info.value)

    def test_load_team_key_empty(self):
        """Test _load_team_key with empty TEAM_KEY"""
        with patch.dict(os.environ, {'TEAM_KEY': '   '}):
            with pytest.raises(Exception) as exc_info:
                _load_team_key()
            assert 'TEAM_KEY está vacía' in str(exc_info.value)

    def test_build_fernet_valid_key(self):
        """Test _build_fernet with valid hex key"""
        from cryptography.fernet import Fernet
        key_hex = 'a' * 64  # 32 bytes in hex
        result = _build_fernet(key_hex)
        assert isinstance(result, Fernet)

    def test_build_fernet_invalid_hex(self):
        """Test _build_fernet with invalid hex"""
        with pytest.raises(Exception) as exc_info:
            _build_fernet('invalid_hex')
        assert 'formato inválido' in str(exc_info.value)

    def test_build_fernet_wrong_length(self):
        """Test _build_fernet with wrong key length"""
        with pytest.raises(Exception) as exc_info:
            _build_fernet('a' * 60)  # 30 bytes instead of 32
        assert '32 bytes' in str(exc_info.value)

    def test_json_default_datetime(self):
        """Test _json_default with datetime"""
        from datetime import datetime
        dt = datetime(2023, 1, 1, 10, 0)
        result = _json_default(dt)
        assert result == '2023-01-01T10:00:00'

    def test_json_default_date(self):
        """Test _json_default with date"""
        from datetime import date
        d = date(2023, 1, 1)
        result = _json_default(d)
        assert result == '2023-01-01'

    def test_json_default_decimal(self):
        """Test _json_default with Decimal"""
        from decimal import Decimal
        dec = Decimal('10.5')
        result = _json_default(dec)
        assert result == 10.5

    def test_json_default_other(self):
        """Test _json_default with other types"""
        result = _json_default('test')
        assert result == 'test'

    def test_parse_datetime_none(self):
        """Test _parse_datetime with None"""
        result = _parse_datetime(None)
        assert result is None

    def test_parse_datetime_empty_string(self):
        """Test _parse_datetime with empty string"""
        result = _parse_datetime('')
        assert result is None

    def test_parse_datetime_datetime(self):
        """Test _parse_datetime with datetime object"""
        from datetime import datetime
        dt = datetime(2023, 1, 1)
        result = _parse_datetime(dt)
        assert result == dt

    def test_parse_datetime_date(self):
        """Test _parse_datetime with date object"""
        from datetime import date, datetime
        d = date(2023, 1, 1)
        result = _parse_datetime(d)
        assert isinstance(result, datetime)
        assert result.date() == d

    def test_parse_datetime_iso_string(self):
        """Test _parse_datetime with ISO string"""
        from datetime import datetime
        result = _parse_datetime('2023-01-01T10:00:00')
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 1

    def test_parse_datetime_invalid_string(self):
        """Test _parse_datetime with invalid string"""
        result = _parse_datetime('invalid')
        assert result == 'invalid'

    @patch('src.cli.secure_seed.SEED_DIR')
    def test_ensure_seed_directory(self, mock_seed_dir):
        """Test _ensure_seed_directory"""
        mock_seed_dir.mkdir = Mock()
        _ensure_seed_directory()
        mock_seed_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_encrypt_payload(self):
        """Test _encrypt_payload"""
        from cryptography.fernet import Fernet
        import base64

        # Create a test key
        key = base64.urlsafe_b64encode(b'a' * 32)
        fernet = Fernet(key)

        data = {'test': 'data'}
        result = _encrypt_payload(fernet, data)

        # Should be bytes and decryptable
        assert isinstance(result, bytes)
        decrypted = fernet.decrypt(result)
        assert decrypted == b'{\n  "test": "data"\n}'

    def test_decrypt_payload_valid(self):
        """Test _decrypt_payload with valid data"""
        from cryptography.fernet import Fernet
        import base64

        key = base64.urlsafe_b64encode(b'a' * 32)
        fernet = Fernet(key)

        data = {'test': 'data'}
        encrypted = fernet.encrypt(b'{"test": "data"}')

        result = _decrypt_payload(fernet, encrypted)
        assert result == {'test': 'data'}

    def test_decrypt_payload_invalid_token(self):
        """Test _decrypt_payload with invalid token"""
        from cryptography.fernet import Fernet
        import base64

        key = base64.urlsafe_b64encode(b'a' * 32)
        fernet = Fernet(key)

        with pytest.raises(Exception) as exc_info:
            _decrypt_payload(fernet, b'invalid_token')
        assert 'No se pudo descifrar' in str(exc_info.value)

    def test_decrypt_payload_invalid_json(self):
        """Test _decrypt_payload with invalid JSON"""
        from cryptography.fernet import Fernet
        import base64

        key = base64.urlsafe_b64encode(b'a' * 32)
        fernet = Fernet(key)

        encrypted = fernet.encrypt(b'invalid json')

        with pytest.raises(Exception) as exc_info:
            _decrypt_payload(fernet, encrypted)
        assert 'corrupto' in str(exc_info.value)

    @patch('builtins.open', new_callable=mock_open)
    @patch('src.cli.secure_seed.ENV_EXAMPLE_PATH')
    def test_update_env_example_file_not_exists(self, mock_env_path, mock_file):
        """Test _update_env_example when file doesn't exist"""
        mock_env_path.exists.return_value = False
        _update_env_example('test_key')
        # Should not attempt to read/write

    @patch('builtins.open', new_callable=mock_open, read_data='SECRET_KEY=\nTEAM_KEY=\n')
    @patch('src.cli.secure_seed.ENV_EXAMPLE_PATH')
    def test_update_env_example_success(self, mock_env_path, mock_file):
        """Test _update_env_example with existing file"""
        mock_env_path.exists.return_value = True

        _update_env_example('new_team_key')

        # Check that file was written
        mock_file().writelines.assert_called()

    def test_parse_datetime_with_timezone(self):
        """Test _parse_datetime with ISO string with timezone"""
        from datetime import datetime
        result = _parse_datetime('2023-01-01T10:00:00Z')
        assert isinstance(result, datetime)
        assert result.year == 2023

    def test_parse_datetime_with_other_type(self):
        """Test _parse_datetime with other types"""
        result = _parse_datetime(123)
        assert result == 123

    @patch('src.cli.secure_seed.get_connection')
    def test_get_connection_checked_success(self, mock_get_conn):
        """Test _get_connection_checked with successful connection"""
        from src.cli.secure_seed import _get_connection_checked
        mock_conn = Mock()
        mock_get_conn.return_value = mock_conn
        result = _get_connection_checked()
        assert result == mock_conn

    @patch('src.cli.secure_seed.get_connection')
    def test_get_connection_checked_database_error(self, mock_get_conn):
        """Test _get_connection_checked with DatabaseError"""
        from src.cli.secure_seed import _get_connection_checked
        from src.database.db import DatabaseError
        mock_get_conn.side_effect = DatabaseError('DB error')
        with pytest.raises(Exception) as exc_info:
            _get_connection_checked()
        assert 'Error al obtener conexión' in str(exc_info.value)

    @patch('src.cli.secure_seed.get_connection')
    def test_get_connection_checked_none(self, mock_get_conn):
        """Test _get_connection_checked when connection is None"""
        from src.cli.secure_seed import _get_connection_checked
        mock_get_conn.return_value = None
        with pytest.raises(Exception) as exc_info:
            _get_connection_checked()
        assert 'No se pudo obtener una conexión' in str(exc_info.value)

    def test_fetch_table(self):
        """Test _fetch_table"""
        from src.cli.secure_seed import _fetch_table
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'name': 'Test1'},
            {'id': 2, 'name': 'Test2'}
        ]
        result = _fetch_table(mock_cursor, 'SELECT * FROM test')
        assert len(result) == 2
        assert result[0]['id'] == 1
        mock_cursor.execute.assert_called_once_with('SELECT * FROM test')

    @patch('src.cli.secure_seed._get_connection_checked')
    def test_collect_dataset_success(self, mock_get_conn):
        """Test _collect_dataset with successful collection"""
        from src.cli.secure_seed import _collect_dataset
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_get_conn.return_value = mock_conn
        result = _collect_dataset()
        assert 'metadata' in result
        assert 'roles' in result
        assert 'tipo_pasto' in result

    @patch('src.cli.secure_seed._get_connection_checked')
    def test_collect_dataset_with_unhashed_password(self, mock_get_conn):
        """Test _collect_dataset detects unhashed password"""
        from src.cli.secure_seed import _collect_dataset
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock fetchall to return empty for most queries, but usuarios with unhashed password
        call_count = [0]
        def fetchall_side_effect():
            call_count[0] += 1
            # The usuarios query is called last (after all other tables)
            # We need to track which query is being executed
            if call_count[0] >= 9:  # usuarios is the 9th query
                return [{'id': 1, 'id_persona': 1, 'id_rol': 1, 'contrasena': 'plaintext', 'estado': 'activo'}]
            return []
        
        mock_cursor.fetchall = fetchall_side_effect
        mock_get_conn.return_value = mock_conn
        
        with pytest.raises(Exception) as exc_info:
            _collect_dataset()
        assert 'contraseña de usuario sin hash' in str(exc_info.value)

    def test_execute_many(self):
        """Test _execute_many"""
        from src.cli.secure_seed import _execute_many
        mock_cursor = Mock()
        _execute_many(mock_cursor, 'INSERT INTO test VALUES (%s)', (1,))
        mock_cursor.execute.assert_called_once_with('INSERT INTO test VALUES (%s)', (1,))

    @patch('src.cli.secure_seed._execute_many')
    def test_import_roles(self, mock_execute):
        """Test _import_roles"""
        from src.cli.secure_seed import _import_roles
        rows = [
            {'id': 1, 'rol': 'admin', 'descripcion': 'Administrator'}
        ]
        mock_cursor = Mock()
        _import_roles(mock_cursor, rows)
        assert mock_execute.called

    @patch('src.cli.secure_seed._execute_many')
    def test_import_tipo_pasto(self, mock_execute):
        """Test _import_tipo_pasto"""
        from src.cli.secure_seed import _import_tipo_pasto
        rows = [
            {'id': 1, 'tipo_pasto': 'Bermuda'}
        ]
        mock_cursor = Mock()
        _import_tipo_pasto(mock_cursor, rows)
        assert mock_execute.called

    @patch('src.cli.secure_seed._execute_many')
    def test_import_tipo_vacuna(self, mock_execute):
        """Test _import_tipo_vacuna"""
        from src.cli.secure_seed import _import_tipo_vacuna
        rows = [
            {'id': 1, 'nombre_vacuna': 'Vacuna A'}
        ]
        mock_cursor = Mock()
        _import_tipo_vacuna(mock_cursor, rows)
        assert mock_execute.called

    @patch('src.cli.secure_seed._execute_many')
    def test_import_estado_ganado(self, mock_execute):
        """Test _import_estado_ganado"""
        from src.cli.secure_seed import _import_estado_ganado
        rows = [
            {'id': 1, 'tipo_estado': 'saludable'}
        ]
        mock_cursor = Mock()
        _import_estado_ganado(mock_cursor, rows)
        assert mock_execute.called