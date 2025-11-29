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

        # Check that file was written with updated content
        mock_file().write.assert_called()
        written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        assert 'TEAM_KEY=new_team_key' in written_content