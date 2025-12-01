"""Pruebas para utilidades de autenticación."""
import pytest
from unittest.mock import Mock, patch


def test_unauthorized_function(app_context, mock_jsonify):
    """Test _unauthorized function returns correct response."""
    from src.utils.auth import _unauthorized

    response, status_code = _unauthorized('test_code', 'Test message')

    assert status_code == 401
    assert response.get_json() == {
        'status': 'error',
        'code': 'test_code',
        'message': 'Test message'
    }


def test_token_required_missing_header(app, app_context, mock_jsonify, mock_current_app):
    """Test token_required with missing authorization header."""
    from src.utils.auth import token_required

    # Create a mock function to decorate
    @token_required
    def mock_function():
        return "success"

    # Use Flask test client context
    with app.test_request_context():
        response, status_code = mock_function()

        assert status_code == 401
        assert response.get_json()['code'] == 'missing_authorization_header'


def test_token_required_invalid_format(app, app_context, mock_jsonify, mock_current_app):
    """Test token_required with invalid authorization format."""
    from src.utils.auth import token_required

    @token_required
    def mock_function():
        return "success"

    # Use Flask test client context with invalid header
    with app.test_request_context(headers={'Authorization': 'InvalidFormat'}):
        response, status_code = mock_function()

        assert status_code == 401
        assert response.get_json()['code'] == 'invalid_authorization_format'


def test_token_required_expired_token(app, app_context, mock_jsonify, mock_current_app):
    """Test token_required with expired token."""
    from src.utils.auth import token_required
    import jwt

    @token_required
    def mock_function():
        return "success"

    # Mock JWT decode to raise ExpiredSignatureError
    with patch('src.utils.auth.jwt.decode') as mock_decode:
        mock_decode.side_effect = jwt.ExpiredSignatureError()
        with app.test_request_context(headers={'Authorization': 'Bearer valid.token.here'}):
            response, status_code = mock_function()

            assert status_code == 401
            assert response.get_json()['code'] == 'token_expired'


def test_token_required_invalid_token(app, app_context, mock_jsonify, mock_current_app):
    """Test token_required with invalid token."""
    from src.utils.auth import token_required
    import jwt

    @token_required
    def mock_function():
        return "success"

    # Mock JWT decode to raise InvalidTokenError
    with patch('src.utils.auth.jwt.decode') as mock_decode:
        mock_decode.side_effect = jwt.InvalidTokenError()
        with app.test_request_context(headers={'Authorization': 'Bearer invalid.token.here'}):
            response, status_code = mock_function()

            assert status_code == 401
            assert response.get_json()['code'] == 'invalid_token'


def test_token_required_missing_user_id(app, app_context, mock_jsonify, mock_current_app):
    """Test token_required with payload missing user_id."""
    from src.utils.auth import token_required

    @token_required
    def mock_function():
        return "success"

    # Mock successful JWT decode but missing user_id
    with patch('src.utils.auth.jwt') as mock_jwt:
        mock_jwt.decode.return_value = {'some_key': 'some_value'}
        with app.test_request_context(headers={'Authorization': 'Bearer valid.token.here'}):
            response, status_code = mock_function()

            assert status_code == 401
            assert response.get_json()['code'] == 'token_missing_user_id'


def test_token_required_user_not_found(app, app_context, mock_jsonify, mock_current_app):
    """Test token_required when user is not found."""
    from src.utils.auth import token_required

    @token_required
    def mock_function():
        return "success"

    # Mock JWT decode with user_id and UsuarioService to return None
    with patch('src.utils.auth.jwt') as mock_jwt, \
         patch('src.utils.auth.UsuarioService') as mock_usuario_service:
        mock_jwt.decode.return_value = {'user_id': 123}
        mock_usuario_service.obtener_usuario.return_value = None
        with app.test_request_context(headers={'Authorization': 'Bearer valid.token.here'}):
            response, status_code = mock_function()

            assert status_code == 401
            assert response.get_json()['code'] == 'user_not_found'


def test_token_required_user_inactive(app, app_context, mock_jsonify, mock_current_app):
    """Test token_required when user is inactive."""
    from src.utils.auth import token_required

    @token_required
    def mock_function():
        return "success"

    # Mock JWT decode with user_id and inactive user
    with patch('src.utils.auth.jwt') as mock_jwt, \
         patch('src.utils.auth.UsuarioService') as mock_usuario_service:
        mock_jwt.decode.return_value = {'user_id': 123}
        mock_user = Mock()
        mock_user.estado.value = 'inactivo'
        mock_usuario_service.obtener_usuario.return_value = mock_user
        with app.test_request_context(headers={'Authorization': 'Bearer valid.token.here'}):
            response, status_code = mock_function()

            assert status_code == 401
            assert response.get_json()['code'] == 'user_inactive'


def test_token_required_success(app, app_context, mock_jsonify, mock_current_app):
    """Test token_required with successful authentication."""
    from src.utils.auth import token_required

    @token_required
    def mock_function():
        return "success"

    # Mock JWT decode with user_id and active user
    with patch('src.utils.auth.jwt') as mock_jwt, \
         patch('src.utils.auth.UsuarioService') as mock_usuario_service, \
         patch('src.utils.auth.g') as mock_g:
        mock_jwt.decode.return_value = {'user_id': 123}
        mock_user = Mock()
        mock_user.estado.value = 'activo'
        mock_user.tenant_id = 456
        mock_usuario_service.obtener_usuario.return_value = mock_user
        with app.test_request_context(headers={'Authorization': 'Bearer valid.token.here'}):
            result = mock_function()

            assert result == "success"

            # Verify that g variables were set
            assert mock_g.current_user == mock_user
            assert mock_g.jwt_payload == {'user_id': 123, 'tenant_id': 456}
            assert mock_g.tenant_id == 456


def test_token_required_success_no_tenant(app, app_context, mock_jsonify, mock_current_app):
    """Test token_required with successful authentication but no tenant."""
    from src.utils.auth import token_required

    @token_required
    def mock_function():
        return "success"

    # Mock JWT decode with user_id and active user without tenant
    with patch('src.utils.auth.jwt') as mock_jwt, \
         patch('src.utils.auth.UsuarioService') as mock_usuario_service, \
         patch('src.utils.auth.g') as mock_g:
        mock_jwt.decode.return_value = {'user_id': 123}
        mock_user = Mock()
        mock_user.estado.value = 'activo'
        mock_user.tenant_id = None
        mock_usuario_service.obtener_usuario.return_value = mock_user
        with app.test_request_context(headers={'Authorization': 'Bearer valid.token.here'}):
            result = mock_function()

            assert result == "success"

            # Verify that g variables were set without tenant_id
            assert mock_g.current_user == mock_user
            assert mock_g.jwt_payload == {'user_id': 123}
            assert mock_g.tenant_id is None


def test_token_required_success_estado_as_string(app, app_context, mock_jsonify, mock_current_app):
    """Test token_required with user estado as string (not object with value)."""
    from src.utils.auth import token_required

    @token_required
    def mock_function():
        return "success"

    # Mock JWT decode with user_id and active user where estado is a string
    with patch('src.utils.auth.jwt') as mock_jwt, \
         patch('src.utils.auth.UsuarioService') as mock_usuario_service, \
         patch('src.utils.auth.g') as mock_g:
        mock_jwt.decode.return_value = {'user_id': 123}
        mock_user = Mock()
        # Remove the value attribute so getattr returns None, then it falls back to str(estado)
        del mock_user.estado.value  # This makes estado_obj None
        mock_user.estado = 'activo'  # Direct string value
        mock_user.tenant_id = 456
        mock_usuario_service.obtener_usuario.return_value = mock_user
        with app.test_request_context(headers={'Authorization': 'Bearer valid.token.here'}):
            result = mock_function()

            assert result == "success"

            # Verify that g variables were set
            assert mock_g.current_user == mock_user
            assert mock_g.jwt_payload == {'user_id': 123, 'tenant_id': 456}
            assert mock_g.tenant_id == 456