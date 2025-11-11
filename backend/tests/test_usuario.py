import pytest
from datetime import datetime
from src.models.usuario import Usuario, Persona, Rol, EstadoUsuario, EstadoGanado, SexoGanado

# Constants for test data
TEST_APELLIDO = 'Pérez'
TEST_EMAIL = 'juan@example.com'
TEST_NOMBRE_COMPLETO = 'Juan Pérez'


class TestRol:
    def test_init(self):
        """Test Rol initialization"""
        rol = Rol(id=1, nombre_rol='admin', descripcion='Administrator')
        assert rol.id == 1
        assert rol.nombre_rol == 'admin'
        assert rol.descripcion == 'Administrator'

    def test_from_dict(self):
        """Test Rol from_dict"""
        data = {'id': 1, 'rol': 'admin', 'descripcion': 'Administrator'}
        rol = Rol.from_dict(data)
        assert rol.id == 1
        assert rol.nombre_rol == 'admin'
        assert rol.descripcion == 'Administrator'

    def test_to_dict(self):
        """Test Rol to_dict"""
        rol = Rol(id=1, nombre_rol='admin', descripcion='Administrator')
        result = rol.to_dict()
        assert result == {'id': 1, 'rol': 'admin', 'descripcion': 'Administrator'}


class TestPersona:
    def test_init(self):
        """Test Persona initialization"""
        persona = Persona(
            id=1,
            primer_nombre='Juan',
            primer_apellido=TEST_APELLIDO,
            email=TEST_EMAIL
        )
        assert persona.id == 1
        assert persona.primer_nombre == 'Juan'
        assert persona.primer_apellido == TEST_APELLIDO
        assert persona.email == TEST_EMAIL

    def test_nombre_completo(self):
        """Test nombre_completo property"""
        persona = Persona(
            primer_nombre='Juan',
            segundo_nombre='Carlos',
            primer_apellido=TEST_APELLIDO,
            segundo_apellido='Gómez'
        )
        assert persona.nombre_completo == 'Juan Carlos Pérez Gómez'

    def test_nombre_completo_sin_segundos(self):
        """Test nombre_completo without second names"""
        persona = Persona(primer_nombre='Juan', primer_apellido=TEST_APELLIDO)
        assert persona.nombre_completo == TEST_NOMBRE_COMPLETO

    def test_from_dict(self):
        """Test Persona from_dict"""
        data = {
            'id': 1,
            'primer_nombre': 'Juan',
            'segundo_nombre': 'Carlos',
            'primer_apellido': TEST_APELLIDO,
            'email': TEST_EMAIL,
            'telefono': '123456789',
            'rol': {'id': 1, 'rol': 'admin'}
        }
        persona = Persona.from_dict(data)
        assert persona.id == 1
        assert persona.primer_nombre == 'Juan'
        assert persona.rol.nombre_rol == 'admin'

    def test_to_dict(self):
        """Test Persona to_dict"""
        persona = Persona(
            id=1,
            primer_nombre='Juan',
            primer_apellido=TEST_APELLIDO,
            email=TEST_EMAIL
        )
        result = persona.to_dict()
        assert result['id'] == 1
        assert result['primer_nombre'] == 'Juan'
        assert result['nombre_completo'] == TEST_NOMBRE_COMPLETO


class TestUsuario:
    def test_init(self):
        """Test Usuario initialization"""
        usuario = Usuario(id=1, id_persona=1, estado=EstadoUsuario.ACTIVO)
        assert usuario.id == 1
        assert usuario.id_persona == 1
        assert usuario.estado == EstadoUsuario.ACTIVO

    def test_nombre_completo_con_persona(self):
        """Test nombre_completo with associated persona"""
        persona = Persona(primer_nombre='Juan', primer_apellido=TEST_APELLIDO)
        usuario = Usuario(persona=persona)
        assert usuario.nombre_completo == TEST_NOMBRE_COMPLETO

    def test_nombre_completo_sin_persona(self):
        """Test nombre_completo without persona"""
        usuario = Usuario()
        assert usuario.nombre_completo == ''

    def test_set_password(self):
        """Test password setting with hashing"""
        usuario = Usuario()
        usuario.set_password('password123')
        assert usuario.contrasena is not None
        assert usuario.contrasena != 'password123'  # Should be hashed
        assert usuario.password_hash == usuario.contrasena

    def test_check_password_correct(self):
        """Test password verification with correct password"""
        usuario = Usuario()
        usuario.set_password('password123')
        assert usuario.check_password('password123') is True

    def test_check_password_incorrect(self):
        """Test password verification with incorrect password"""
        usuario = Usuario()
        usuario.set_password('password123')
        assert usuario.check_password('wrongpassword') is False

    def test_check_password_no_hash(self):
        """Test password verification without hash (legacy)"""
        usuario = Usuario(contrasena='password123')
        assert usuario.check_password('password123') is True
        assert usuario.check_password('wrong') is False

    def test_check_password_none(self):
        """Test password verification when password is None"""
        usuario = Usuario()
        assert usuario.check_password('password') is False

    def test_from_dict(self):
        """Test Usuario from_dict"""
        data = {
            'id': 1,
            'id_persona': 1,
            'estado': 'activo',
            'persona': {
                'id': 1,
                'primer_nombre': 'Juan',
                'primer_apellido': TEST_APELLIDO
            }
        }
        usuario = Usuario.from_dict(data)
        assert usuario.id == 1
        assert usuario.persona.primer_nombre == 'Juan'

    def test_from_dict_sin_persona(self):
        """Test Usuario from_dict without persona"""
        data = {'id': 1, 'estado': 'activo'}
        usuario = Usuario.from_dict(data, include_persona=False)
        assert usuario.id == 1
        assert usuario.persona is None

    def test_from_registration_data(self):
        """Test from_registration_data"""
        data = {
            'primer_nombre': 'Juan',
            'segundo_nombre': 'Carlos',
            'primer_apellido': TEST_APELLIDO,
            'email': TEST_EMAIL,
            'telefono': '123456789',
            'password': 'password123'
        }
        persona, usuario = Usuario.from_registration_data(data)
        assert persona.primer_nombre == 'Juan'
        assert persona.email == TEST_EMAIL
        assert usuario.estado == EstadoUsuario.ACTIVO
        assert usuario.check_password('password123') is True

    def test_to_dict(self):
        """Test Usuario to_dict"""
        persona = Persona(id=1, primer_nombre='Juan', primer_apellido=TEST_APELLIDO)
        usuario = Usuario(id=1, persona=persona, estado=EstadoUsuario.ACTIVO)
        result = usuario.to_dict()
        assert result['id'] == 1
        assert result['estado'] == 'activo'
        assert result['persona']['primer_nombre'] == 'Juan'

    def test_to_dict_sin_persona(self):
        """Test Usuario to_dict without persona"""
        usuario = Usuario(id=1, estado=EstadoUsuario.ACTIVO)
        result = usuario.to_dict(include_persona=False)
        assert result['id'] == 1
        assert 'persona' not in result

    def test_from_dict_con_rol(self):
        """Test Usuario from_dict with rol"""
        data = {
            'id': 1,
            'estado': 'activo',
            'rol': {'id': 1, 'rol': 'admin', 'descripcion': 'Administrator'}
        }
        usuario = Usuario.from_dict(data)
        assert usuario.id == 1
        assert usuario.rol.nombre_rol == 'admin'

    def test_to_dict_con_rol(self):
        """Test Usuario to_dict with rol"""
        rol = Rol(id=1, nombre_rol='admin', descripcion='Administrator')
        usuario = Usuario(id=1, rol=rol, estado=EstadoUsuario.ACTIVO)
        result = usuario.to_dict()
        assert result['id'] == 1
        assert result['rol']['rol'] == 'admin'

    def test_persona_from_dict_con_rol(self):
        """Test Persona from_dict with rol"""
        data = {
            'id': 1,
            'primer_nombre': 'Juan',
            'primer_apellido': TEST_APELLIDO,
            'rol': {'id': 1, 'rol': 'admin', 'descripcion': 'Administrator'}
        }
        persona = Persona.from_dict(data)
        assert persona.id == 1
        assert persona.rol.nombre_rol == 'admin'

    def test_persona_to_dict_con_rol(self):
        """Test Persona to_dict with rol"""
        rol = Rol(id=1, nombre_rol='admin', descripcion='Administrator')
        persona = Persona(id=1, primer_nombre='Juan', primer_apellido=TEST_APELLIDO, rol=rol)
        result = persona.to_dict()
        assert result['id'] == 1
        assert result['rol']['rol'] == 'admin'


class TestEnums:
    def test_estado_usuario(self):
        """Test EstadoUsuario enum"""
        assert EstadoUsuario.ACTIVO.value == 'activo'
        assert EstadoUsuario.INACTIVO.value == 'inactivo'

    def test_estado_ganado(self):
        """Test EstadoGanado enum"""
        assert EstadoGanado.ACTIVO.value == 'activo'
        assert EstadoGanado.VENDIDO.value == 'vendido'
        assert EstadoGanado.MUERTO.value == 'muerto'

    def test_sexo_ganado(self):
        """Test SexoGanado enum"""
        assert SexoGanado.MACHO.value == 'macho'
        assert SexoGanado.HEMBRA.value == 'hembra'
        assert SexoGanado.OTRO.value == 'otro'