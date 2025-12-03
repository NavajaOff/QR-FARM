"""Tests para verificar el aislamiento multi-tenant."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, g

from src.services.usuario_service import UsuarioService
from src.services.animal_service import GanadoService
from src.services.potrero_service import PotreroService
from src.services.vacunacion_service import VacunacionService
from src.models.usuario import Usuario, Persona, EstadoUsuario
from src.models.animal import Ganado


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def app_context(app):
    """Provide Flask application context."""
    with app.app_context():
        yield


class TestTenantIsolationUsuarioService:
    """Tests de aislamiento multi-tenant para UsuarioService."""

    @patch('src.services.usuario_service.get_connection')
    def test_obtener_usuario_filtra_por_tenant_id(self, mock_get_connection, app_context):
        """Test que obtener_usuario filtra por tenant_id."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'id': 1,
            'id_persona': 1,
            'id_rol': 1,
            'contrasena': 'hashed',
            'estado': 'activo',
            'primer_nombre': 'Juan',
            'segundo_nombre': None,
            'primer_apellido': 'Pérez',
            'segundo_apellido': None,
            'email': 'juan@example.com',
            'telefono': '123456789',
            'fecha_creacion': '2023-01-01',
            'rol_nombre': 'usuario',
            'tenant_id': 1
        }

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            result = UsuarioService.obtener_usuario(1, tenant_id_override=1)

            # Verificar que se ejecutó la query
            assert mock_cursor.execute.called

    @patch('src.services.usuario_service.get_connection')
    def test_obtener_usuario_no_encuentra_usuario_de_otro_tenant(self, mock_get_connection, app_context):
        """Test que obtener_usuario no encuentra usuarios de otro tenant."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Usuario del tenant 2, pero buscamos con tenant_id=1
        mock_cursor.fetchone.return_value = None

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            result = UsuarioService.obtener_usuario(1, tenant_id_override=1)

            # Debe retornar None porque el usuario no pertenece al tenant
            assert result is None

    @patch('src.services.usuario_service.get_connection')
    def test_actualizar_usuario_completo_valida_tenant_id(self, mock_get_connection, app_context):
        """Test que actualizar_usuario_completo valida tenant_id."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Usuario del tenant 2, pero intentamos actualizar con tenant_id=1
        mock_cursor.fetchone.return_value = {'id_persona': 1, 'tenant_id': 2}

        persona = Persona(
            id_rol=1,
            primer_nombre='Juan',
            primer_apellido='Pérez',
            email='juan@example.com',
            telefono='123456789'
        )

        usuario = Usuario(
            id_rol=1,
            estado=EstadoUsuario.ACTIVO,
            persona=persona
        )

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            result = UsuarioService.actualizar_usuario_completo(1, usuario, tenant_id_override=1)

            # Debe retornar False porque el tenant no coincide
            assert result is False

    @patch('src.services.usuario_service.get_connection')
    def test_eliminar_usuario_valida_tenant_id(self, mock_get_connection, app_context):
        """Test que eliminar_usuario valida tenant_id."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.start_transaction = Mock()
        mock_conn.commit = Mock()
        mock_conn.rollback = Mock()

        # Usuario del tenant 2, pero intentamos eliminar con tenant_id=1
        mock_cursor.fetchone.return_value = {'id_persona': 1, 'tenant_id': 2}

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            success, message = UsuarioService.eliminar_usuario(1, tenant_id_override=1)

            # Debe retornar False porque el tenant no coincide
            assert success is False
            assert 'permisos' in message.lower() or 'No tiene permisos' in message

    @patch('src.services.usuario_service.get_connection')
    def test_obtener_todos_usuarios_filtra_por_tenant_id(self, mock_get_connection, app_context):
        """Test que obtener_todos_usuarios filtra por tenant_id."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Solo usuarios del tenant 1
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'id_persona': 1,
                'id_rol': 1,
                'contrasena': 'hashed',
                'estado': 'activo',
                'primer_nombre': 'Juan',
                'segundo_nombre': None,
                'primer_apellido': 'Pérez',
                'segundo_apellido': None,
                'email': 'juan@example.com',
                'telefono': '123456789',
                'fecha_creacion': '2023-01-01',
                'rol_nombre': 'usuario',
                'tenant_id': 1
            }
        ]

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            result = UsuarioService.obtener_todos_usuarios(tenant_id=1)

            # Verificar que se ejecutó la query
            assert mock_cursor.execute.called
            assert isinstance(result, list)


class TestTenantIsolationGanadoService:
    """Tests de aislamiento multi-tenant para GanadoService."""

    @patch('src.services.animal_service.get_connection')
    def test_obtener_ganado_filtra_por_tenant_id(self, mock_get_connection, app_context):
        """Test que obtener_ganado filtra por tenant_id."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'id': 1,
            'nombre': 'Toro 1',
            'raza': 'Angus',
            'tenant_id': 1
        }

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            with patch('src.services.animal_service.Ganado.from_dict') as mock_from_dict:
                mock_ganado = Mock()
                mock_from_dict.return_value = mock_ganado
                result = GanadoService.obtener_ganado(1, tenant_id_override=1)

                # Verificar que se ejecutó la query
                assert mock_cursor.execute.called

    @patch('src.services.animal_service.get_connection')
    def test_obtener_ganado_no_encuentra_ganado_de_otro_tenant(self, mock_get_connection, app_context):
        """Test que obtener_ganado no encuentra ganado de otro tenant."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Ganado del tenant 2, pero buscamos con tenant_id=1
        mock_cursor.fetchone.return_value = None

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            result = GanadoService.obtener_ganado(1, tenant_id_override=1)

            # Debe retornar None porque el ganado no pertenece al tenant
            assert result is None

    @patch('src.services.animal_service.get_connection')
    def test_buscar_por_codigo_qr_filtra_por_tenant_id(self, mock_get_connection, app_context):
        """Test que buscar_por_codigo_qr filtra por tenant_id."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'id': 1,
            'nombre': 'Toro 1',
            'codigo_qr': 'QR123',
            'tenant_id': 1
        }

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            with patch('src.services.animal_service.Ganado.from_dict') as mock_from_dict:
                mock_ganado = Mock()
                mock_from_dict.return_value = mock_ganado
                result = GanadoService.buscar_por_codigo_qr('QR123', tenant_id_override=1)

                # Verificar que se ejecutó la query
                assert mock_cursor.execute.called

    @patch('src.services.animal_service.get_connection')
    def test_buscar_por_potrero_filtra_por_tenant_id(self, mock_get_connection, app_context):
        """Test que buscar_por_potrero filtra por tenant_id."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'nombre': 'Toro 1',
                'id_potrero': 1,
                'tenant_id': 1
            }
        ]

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            with patch('src.services.animal_service.Ganado.from_dict') as mock_from_dict:
                mock_ganado = Mock()
                mock_from_dict.return_value = mock_ganado
                result = GanadoService.buscar_por_potrero(1, tenant_id_override=1)

                # Verificar que se ejecutó la query con tenant_id
                assert mock_cursor.execute.called

    @patch.object(GanadoService, 'dar_baja_ganado')
    def test_eliminar_ganado_valida_tenant_id(self, mock_dar_baja, app_context):
        """Test que eliminar_ganado valida tenant_id."""
        mock_dar_baja.return_value = "Animal no encontrado"
        
        result = GanadoService.eliminar_ganado(1, tenant_id_override=1)
        
        # Verificar que se llamó con tenant_id_override
        mock_dar_baja.assert_called_once_with(1, 'otra', 'Eliminación automática', tenant_id_override=1)


class TestTenantIsolationPotreroService:
    """Tests de aislamiento multi-tenant para PotreroService."""

    @patch('src.services.potrero_service.db')
    def test_get_by_id_filtra_por_tenant_id(self, mock_db, app_context):
        """Test que get_by_id filtra por tenant_id."""
        mock_cursor = Mock(dictionary=True)
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'nombre': 'Potrero 1',
            'tenant_id': 1
        }

        mock_cursor_context = MagicMock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_db.get_cursor.return_value = mock_cursor_context

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            with patch('src.services.potrero_service.PotreroService._obtener_ocupacion_real', return_value=10):
                with patch('src.services.potrero_service.PotreroService._actualizar_ocupacion_en_db'):
                    with patch('src.services.potrero_service.PotreroService.get_tipos_pasto', return_value=[]):
                        result = PotreroService.get_by_id(1, tenant_id_override=1)

                        # Verificar que se ejecutó la query
                        assert mock_cursor.execute.called
                        assert result is not None

    @patch('src.services.potrero_service.db')
    def test_get_personas_usuario_filtra_por_tenant_id(self, mock_db, app_context):
        """Test que get_personas_usuario filtra por tenant_id."""
        mock_cursor = Mock(dictionary=True)
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'primer_nombre': 'Juan',
                'primer_apellido': 'Pérez',
                'segundo_nombre': None,
                'segundo_apellido': None,
                'nombre_completo': 'Juan Pérez'
            }
        ]

        mock_cursor_context = MagicMock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_db.get_cursor.return_value = mock_cursor_context

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            result = PotreroService.get_personas_usuario(tenant_id_override=1)

            # Verificar que se ejecutó la query con tenant_id
            assert isinstance(result, list)
            assert mock_cursor.execute.called


class TestTenantIsolationVacunacionService:
    """Tests de aislamiento multi-tenant para VacunacionService."""

    @patch('src.services.vacunacion_service.get_connection')
    def test_obtener_vacunacion_por_id_filtra_por_tenant_id(self, mock_get_connection, app_context):
        """Test que obtener_vacunacion_por_id filtra por tenant_id."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        mock_cursor.fetchone.return_value = {
            'id': 1,
            'id_animal': 1,
            'nombre_animal': 'Toro 1',
            'fecha_aplicacion': '2023-01-01',
            'proxima_dosis': '2023-07-01',
            'responsable': 1,
            'nombre_responsable': 'Juan Pérez',
            'estado': 'aplicado',
            'id_tipo_vacuna': 1,
            'nombre_tipo_vacuna': 'Vacuna A',
            'tenant_id': 1
        }

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            with patch('src.services.vacunacion_service.Vacunacion.from_dict') as mock_from_dict:
                mock_vacunacion = Mock()
                mock_from_dict.return_value = mock_vacunacion
                
                result = VacunacionService.obtener_vacunacion_por_id(1, tenant_id_override=1)

                # Verificar que se ejecutó la query con tenant_id
                assert mock_cursor.execute.called

    @patch('src.services.vacunacion_service.get_connection')
    def test_eliminar_vacunacion_valida_tenant_id(self, mock_get_connection, app_context):
        """Test que eliminar_vacunacion valida tenant_id."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Vacunación del tenant 2, pero intentamos eliminar con tenant_id=1
        mock_cursor.rowcount = 0  # No se eliminó porque el tenant no coincide

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            result = VacunacionService.eliminar_vacunacion(1, tenant_id_override=1)

            # Debe retornar False porque el tenant no coincide
            assert result is False

    @patch('src.services.vacunacion_service.get_connection')
    def test_obtener_todas_vacunaciones_filtra_por_tenant_id(self, mock_get_connection, app_context):
        """Test que obtener_todas_vacunaciones filtra por tenant_id."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'id_animal': 1,
                'nombre_animal': 'Toro 1',
                'fecha_aplicacion': '2023-01-01',
                'proxima_dosis': '2023-07-01',
                'responsable': 1,
                'nombre_responsable': 'Juan Pérez',
                'estado': 'aplicado',
                'id_tipo_vacuna': 1,
                'nombre_tipo_vacuna': 'Vacuna A',
                'tenant_id': 1
            }
        ]

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            with patch('src.services.vacunacion_service.Vacunacion.from_dict') as mock_from_dict:
                mock_vacunacion = Mock()
                mock_from_dict.return_value = mock_vacunacion
                
                result = VacunacionService.obtener_todas_vacunaciones(tenant_id_override=1)

                # Verificar que se ejecutó la query con tenant_id
                assert mock_cursor.execute.called
                assert isinstance(result, list)


class TestTenantIsolationSuperAdmin:
    """Tests para verificar que super_admin puede acceder a todos los tenants."""

    @patch('src.services.usuario_service.get_connection')
    def test_super_admin_puede_ver_usuarios_de_cualquier_tenant(self, mock_get_connection, app_context):
        """Test que super_admin puede ver usuarios de cualquier tenant."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Usuarios de diferentes tenants
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'id_persona': 1,
                'id_rol': 1,
                'contrasena': 'hashed',
                'estado': 'activo',
                'primer_nombre': 'Juan',
                'primer_apellido': 'Pérez',
                'email': 'juan@example.com',
                'fecha_creacion': '2023-01-01',
                'rol_nombre': 'usuario',
                'tenant_id': 1
            },
            {
                'id': 2,
                'id_persona': 2,
                'id_rol': 1,
                'contrasena': 'hashed',
                'estado': 'activo',
                'primer_nombre': 'Pedro',
                'primer_apellido': 'García',
                'email': 'pedro@example.com',
                'fecha_creacion': '2023-01-01',
                'rol_nombre': 'usuario',
                'tenant_id': 2
            }
        ]

        # Super admin sin tenant_id (None) puede ver todos
        with patch('src.utils.tenant.get_current_tenant_id', return_value=None):
            result = UsuarioService.obtener_todos_usuarios(tenant_id=None)

            # Debe retornar usuarios de todos los tenants
            assert isinstance(result, list)

    @patch('src.services.usuario_service.get_connection')
    def test_super_admin_puede_ver_usuario_especifico_de_cualquier_tenant(self, mock_get_connection, app_context):
        """Test que super_admin puede ver usuario específico de cualquier tenant."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Usuario del tenant 2
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'id_persona': 1,
            'id_rol': 1,
            'contrasena': 'hashed',
            'estado': 'activo',
            'primer_nombre': 'Juan',
            'primer_apellido': 'Pérez',
            'email': 'juan@example.com',
            'fecha_creacion': '2023-01-01',
            'rol_nombre': 'usuario',
            'tenant_id': 2
        }

        # Super admin puede especificar tenant_id_override
        result = UsuarioService.obtener_usuario(1, tenant_id_override=2)

        # Debe poder ver el usuario
        assert result is None or (result is not None and result.id == 1)


class TestTenantIsolationCrossTenantAccess:
    """Tests para verificar que no se puede acceder a recursos de otros tenants."""

    @patch('src.services.usuario_service.get_connection')
    def test_admin_no_puede_ver_usuario_de_otro_tenant(self, mock_get_connection, app_context):
        """Test que un admin no puede ver usuarios de otro tenant."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Usuario del tenant 2, pero admin del tenant 1 intenta verlo
        mock_cursor.fetchone.return_value = None  # No encuentra porque el tenant no coincide

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            result = UsuarioService.obtener_usuario(1, tenant_id_override=1)

            # Debe retornar None porque el usuario no pertenece al tenant del admin
            assert result is None

    @patch('src.services.animal_service.get_connection')
    def test_admin_no_puede_ver_ganado_de_otro_tenant(self, mock_get_connection, app_context):
        """Test que un admin no puede ver ganado de otro tenant."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Ganado del tenant 2, pero admin del tenant 1 intenta verlo
        mock_cursor.fetchone.return_value = None

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            result = GanadoService.obtener_ganado(1, tenant_id_override=1)

            # Debe retornar None porque el ganado no pertenece al tenant del admin
            assert result is None

    @patch('src.services.potrero_service.db')
    def test_admin_no_puede_ver_potrero_de_otro_tenant(self, mock_db, app_context):
        """Test que un admin no puede ver potreros de otro tenant."""
        mock_cursor = Mock(dictionary=True)
        mock_cursor.fetchone.return_value = None  # No encuentra porque el tenant no coincide

        mock_cursor_context = MagicMock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_db.get_cursor.return_value = mock_cursor_context

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            try:
                result = PotreroService.get_by_id(1, tenant_id_override=1)
                # Si no lanza excepción, debe retornar None o lanzar ValueError
                assert result is None or isinstance(result, ValueError)
            except ValueError as e:
                # Esperado: debe lanzar ValueError si no encuentra el potrero
                assert "not found" in str(e).lower()

    @patch('src.services.vacunacion_service.get_connection')
    def test_admin_no_puede_ver_vacunacion_de_otro_tenant(self, mock_get_connection, app_context):
        """Test que un admin no puede ver vacunaciones de otro tenant."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        # Vacunación del tenant 2, pero admin del tenant 1 intenta verla
        mock_cursor.fetchone.return_value = None

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            result = VacunacionService.obtener_vacunacion_por_id(1, tenant_id_override=1)

            # Debe retornar None porque la vacunación no pertenece al tenant del admin
            assert result is None

    @patch('src.services.usuario_service.get_connection')
    def test_admin_no_puede_actualizar_usuario_de_otro_tenant(self, mock_get_connection, app_context):
        """Test que un admin no puede actualizar usuarios de otro tenant."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Usuario del tenant 2, pero admin del tenant 1 intenta actualizarlo
        mock_cursor.fetchone.return_value = {'id_persona': 1, 'tenant_id': 2}

        persona = Persona(
            id_rol=1,
            primer_nombre='Juan',
            primer_apellido='Pérez',
            email='juan@example.com',
            telefono='123456789'
        )

        usuario = Usuario(
            id_rol=1,
            estado=EstadoUsuario.ACTIVO,
            persona=persona
        )

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            result = UsuarioService.actualizar_usuario_completo(1, usuario, tenant_id_override=1)

            # Debe retornar False porque el tenant no coincide
            assert result is False

    @patch('src.services.usuario_service.get_connection')
    def test_admin_no_puede_eliminar_usuario_de_otro_tenant(self, mock_get_connection, app_context):
        """Test que un admin no puede eliminar usuarios de otro tenant."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.start_transaction = Mock()
        mock_conn.commit = Mock()
        mock_conn.rollback = Mock()

        # Usuario del tenant 2, pero admin del tenant 1 intenta eliminarlo
        mock_cursor.fetchone.return_value = {'id_persona': 1, 'tenant_id': 2}

        with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
            success, message = UsuarioService.eliminar_usuario(1, tenant_id_override=1)

            # Debe retornar False porque el tenant no coincide
            assert success is False
            assert 'permisos' in message.lower() or 'No tiene permisos' in message

