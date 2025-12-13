from unittest.mock import Mock, patch

from src.models.usuario import Persona, Rol, Usuario
from src.services.recovery_service import RecoveryService


@patch("src.services.recovery_service.UsuarioService.buscar_por_email")
@patch("src.services.recovery_service.RecoveryService._find_admin_email")
@patch("src.services.recovery_service.RecoveryService._insert_token_record")
@patch("src.services.recovery_service.send_email")
def test_request_password_recovery_usuario(
    mock_send_email,
    mock_insert_token,
    mock_find_admin,
    mock_buscar_por_email
):
    persona = Persona(
        id=1,
        email="usuario@example.com",
        primer_nombre="Lumi",
        primer_apellido="Luna",
        tenant_id=5
    )
    usuario = Usuario(
        id=10,
        persona=persona,
        rol=Rol(id=2, nombre_rol="usuario"),
        tenant_id=5
    )
    mock_buscar_por_email.return_value = usuario
    mock_find_admin.return_value = "admin@tenant.com"

    with patch.object(RecoveryService, "_generate_token", return_value=("code-123", "hash-123")):
        resultado = RecoveryService.request_password_recovery("usuario@example.com")

    assert resultado["destinatario"] == "admin@tenant.com"
    mock_insert_token.assert_called_once()
    mock_send_email.assert_called_once()


@patch("src.services.recovery_service.get_connection")
def test_confirm_password_recovery(get_connection):
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    get_connection.return_value = mock_conn
    mock_cursor.fetchone.return_value = {"id": 1, "usuario_id": 99}

    class FakeHash:
        def __init__(self):
            self._value = "hash-456"

        def hexdigest(self):
            return self._value

    with patch("src.services.recovery_service.hashlib.sha256", return_value=FakeHash()):
        RecoveryService.confirm_password_recovery("token-abc", "newstrongpassword")

    assert mock_cursor.execute.call_count == 3
    mock_conn.commit.assert_called_once()

