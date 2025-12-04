import pytest
import os
from unittest.mock import Mock, patch
from flask import Flask
from src.routes.animal_routes import animal_bp


class TestAnimalRoutes:
    @pytest.fixture(autouse=True)
    def setup_app(self, app):
        """Setup test client and app context"""
        app.register_blueprint(animal_bp)
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def teardown_method(self):
        """Clean up after each test"""
        self.app_context.pop()

    @patch('src.routes.animal_routes.GanadoService')
    def test_get_estados_ganado_sin_parametros(self, mock_service):
        """Test get_estados_ganado without query parameters"""
        mock_service.obtener_estados_ganado.return_value = [
            {'id': 1, 'estado': 'saludable', 'nombre_estado': 'saludable'},
            {'id': 2, 'estado': 'revision', 'nombre_estado': 'revision'}
        ]

        response = self.client.get('/api/animales/estados-ganado')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2
        mock_service.obtener_estados_ganado.assert_called_once_with(solo_activos=False, solo_bajas=False)

    @patch('src.routes.animal_routes.GanadoService')
    def test_get_estados_ganado_solo_activos(self, mock_service):
        """Test get_estados_ganado with solo_activos=true"""
        mock_service.obtener_estados_ganado.return_value = [
            {'id': 1, 'estado': 'saludable', 'nombre_estado': 'saludable'},
            {'id': 2, 'estado': 'revision', 'nombre_estado': 'revision'},
            {'id': 3, 'estado': 'enfermo', 'nombre_estado': 'enfermo'}
        ]

        response = self.client.get('/api/animales/estados-ganado?solo_activos=true')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 3
        mock_service.obtener_estados_ganado.assert_called_once_with(solo_activos=True, solo_bajas=False)

    @patch('src.routes.animal_routes.GanadoService')
    def test_get_estados_ganado_solo_bajas(self, mock_service):
        """Test get_estados_ganado with solo_bajas=true"""
        mock_service.obtener_estados_ganado.return_value = [
            {'id': 4, 'estado': 'dado_de_baja', 'nombre_estado': 'dado_de_baja'},
            {'id': 5, 'estado': 'muerte', 'nombre_estado': 'muerte'}
        ]

        response = self.client.get('/api/animales/estados-ganado?solo_bajas=true')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2
        mock_service.obtener_estados_ganado.assert_called_once_with(solo_activos=False, solo_bajas=True)

    @patch('src.routes.animal_routes.GanadoService')
    def test_get_estados_ganado_service_returns_empty(self, mock_service):
        """Test get_estados_ganado when service returns empty list"""
        mock_service.obtener_estados_ganado.return_value = []

        response = self.client.get('/api/animales/estados-ganado')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        # Should return default states when service returns empty
        assert len(data['data']) == 5  # ESTADOS_DEFAULT length

    @patch('src.routes.animal_routes.GanadoService')
    def test_get_estados_ganado_service_exception(self, mock_service):
        """Test get_estados_ganado when service raises exception"""
        mock_service.obtener_estados_ganado.side_effect = Exception("Database error")

        response = self.client.get('/api/animales/estados-ganado')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        # Should return default states on exception
        assert len(data['data']) == 5  # ESTADOS_DEFAULT length

    @patch('src.controllers.animal_controller.GanadoController')
    def test_get_animales_success(self, mock_controller):
        """Test get_animales success"""
        mock_controller.obtener_todos_ganados.return_value = ([], 200)

        response = self.client.get('/api/animales/')

        assert response.status_code == 200
        mock_controller.obtener_todos_ganados.assert_called_once()

    @patch('src.controllers.animal_controller.GanadoController')
    def test_get_animales_exception(self, mock_controller):
        """Test get_animales exception"""
        mock_controller.obtener_todos_ganados.side_effect = Exception("Controller error")

        response = self.client.get('/api/animales/')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data'] == []

    @patch('src.controllers.animal_controller.GanadoController')
    def test_get_animal_success(self, mock_controller_class):
        """Test get_animal success"""
        from flask import jsonify
        mock_response = jsonify({'data': {'id': 1, 'nombre': 'Vaca1'}, 'success': True})
        mock_response.status_code = 200
        mock_controller_class.obtener_ganado.return_value = (mock_response, 200)

        response = self.client.get('/api/animales/1', headers={'Authorization': 'Bearer test_token'})

        assert response.status_code == 200
        mock_controller_class.obtener_ganado.assert_called_once()

    @patch('src.controllers.animal_controller.GanadoController')
    def test_get_animal_not_found(self, mock_controller_class):
        """Test get_animal not found"""
        from flask import jsonify
        mock_response = jsonify({'error': 'Animal no encontrado', 'success': False})
        mock_response.status_code = 404
        mock_controller_class.obtener_ganado.return_value = (mock_response, 404)

        response = self.client.get('/api/animales/1', headers={'Authorization': 'Bearer test_token'})

        assert response.status_code == 404
        mock_controller_class.obtener_ganado.assert_called_once()

    @patch('src.controllers.animal_controller.GanadoController.obtener_ganado')
    def test_get_animal_exception(self, mock_controller):
        """Test get_animal exception"""
        mock_controller.side_effect = Exception("Service error")

        response = self.client.get('/api/animales/1', headers={'Authorization': 'Bearer test_token'})

        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert data['error'] == 'Error interno del servidor'

    @patch('src.routes.animal_routes.send_from_directory')
    def test_get_qr_image_success(self, mock_send):
        """Test get_qr_image success"""
        mock_send.return_value = 'image data'

        response = self.client.get('/api/animales/qr/123.png')

        assert response.status_code == 200
        mock_send.assert_called_once_with(os.path.join(os.getcwd(), 'qr'), '123.png')

    @patch('src.routes.animal_routes.send_from_directory')
    def test_get_qr_image_exception(self, mock_send):
        """Test get_qr_image exception"""
        mock_send.side_effect = Exception("File not found")

        response = self.client.get('/api/animales/qr/123.png')

        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'Imagen no encontrada' in data['error']

    @patch('src.routes.animal_routes.emit_update')
    @patch('src.routes.animal_routes.GanadoService')
    @patch('src.routes.animal_routes.Ganado')
    @patch('src.routes.animal_routes.token_required')
    def test_update_animal_success(self, mock_token_required, mock_ganado_class, mock_service, mock_emit):
        """Test update_animal success"""
        mock_token_required.return_value = lambda f: f
        mock_animal_actual = Mock()
        mock_animal_actual.to_dict.return_value = {'id': 1, 'nombre': 'ViejoNombre'}
        mock_service.obtener_ganado.return_value = mock_animal_actual
        mock_animal_nuevo = Mock()
        mock_ganado_class.from_dict.return_value = mock_animal_nuevo
        mock_service.actualizar_ganado.return_value = True
        mock_animal_actualizado = Mock()
        mock_animal_actualizado.to_dict.return_value = {'id': 1, 'nombre': 'NuevoNombre'}
        # Second call for obtener_ganado
        mock_service.obtener_ganado.side_effect = [mock_animal_actual, mock_animal_actualizado]

        response = self.client.put('/api/animales/1', json={'nombre': 'NuevoNombre'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == 'Animal actualizado correctamente'
        mock_emit.assert_called_once()


    @patch('src.routes.animal_routes.GanadoService')
    @patch('src.routes.animal_routes.token_required')
    def test_update_animal_not_found(self, mock_token_required, mock_service):
        """Test update_animal not found"""
        mock_token_required.return_value = lambda f: f
        mock_service.obtener_ganado.return_value = None

        response = self.client.put('/api/animales/1', json={'nombre': 'Nuevo'})

        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'No se encontró el animal' in data['message']

    @patch('src.routes.animal_routes.emit_update')
    @patch('src.routes.animal_routes.GanadoService')
    @patch('src.routes.animal_routes.Ganado')
    @patch('src.routes.animal_routes.token_required')
    def test_update_animal_update_fails(self, mock_token_required, mock_ganado_class, mock_service, mock_emit):
        """Test update_animal update fails"""
        mock_token_required.return_value = lambda f: f
        mock_animal_actual = Mock()
        mock_animal_actual.to_dict.return_value = {'id': 1, 'nombre': 'Viejo'}
        mock_service.obtener_ganado.return_value = mock_animal_actual
        mock_animal_nuevo = Mock()
        mock_ganado_class.from_dict.return_value = mock_animal_nuevo
        mock_service.actualizar_ganado.return_value = False

        response = self.client.put('/api/animales/1', json={'nombre': 'Nuevo'})

        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert 'No se pudo actualizar el animal' in data['message']

    @patch('src.routes.animal_routes.emit_update')
    @patch('src.routes.animal_routes.GanadoService')
    @patch('src.routes.animal_routes.Ganado')
    @patch('src.routes.animal_routes.token_required')
    def test_update_animal_exception(self, mock_token_required, mock_ganado_class, mock_service, mock_emit):
        """Test update_animal exception"""
        mock_token_required.return_value = lambda f: f
        mock_service.obtener_ganado.side_effect = Exception("DB error")

        response = self.client.put('/api/animales/1', json={'nombre': 'Nuevo'})

        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert data['error'] == 'Error interno del servidor'

    @patch('src.controllers.animal_controller.GanadoController')
    def test_dar_baja_animal_success(self, mock_controller):
        """Test dar_baja_animal success"""
        mock_controller.dar_baja_ganado.return_value = ({'message': 'Baja exitosa'}, 200)

        response = self.client.put('/api/animales/1/baja')

        assert response.status_code == 200
        mock_controller.dar_baja_ganado.assert_called_once_with(1)

    @patch('src.controllers.animal_controller.GanadoController')
    def test_dar_baja_animal_exception(self, mock_controller):
        """Test dar_baja_animal exception"""
        mock_controller.dar_baja_ganado.side_effect = Exception("Controller error")

        response = self.client.put('/api/animales/1/baja')

        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert data['error'] == 'Error interno del servidor'

    @patch('src.controllers.animal_controller.GanadoController')
    def test_reactivar_animal_success(self, mock_controller):
        """Test reactivar_animal success"""
        mock_controller.reactivar_ganado.return_value = ({'message': 'Reactivado'}, 200)

        response = self.client.put('/api/animales/1/reactivar')

        assert response.status_code == 200
        mock_controller.reactivar_ganado.assert_called_once_with(1)

    @patch('src.controllers.animal_controller.GanadoController')
    def test_reactivar_animal_exception(self, mock_controller):
        """Test reactivar_animal exception"""
        mock_controller.reactivar_ganado.side_effect = Exception("Controller error")

        response = self.client.put('/api/animales/1/reactivar')

        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert data['error'] == 'Error interno del servidor'

    @patch('src.controllers.animal_controller.GanadoController')
    def test_delete_animal_success(self, mock_controller):
        """Test delete_animal success"""
        mock_controller.eliminar_ganado.return_value = ({'message': 'Eliminado'}, 200)

        response = self.client.delete('/api/animales/1')

        assert response.status_code == 200
        mock_controller.eliminar_ganado.assert_called_once_with(1)

    @patch('src.controllers.animal_controller.GanadoController')
    def test_delete_animal_exception(self, mock_controller):
        """Test delete_animal exception"""
        mock_controller.eliminar_ganado.side_effect = Exception("Controller error")

        response = self.client.delete('/api/animales/1')

        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert data['error'] == 'Error interno del servidor'

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.animal_controller.GanadoController')
    def test_create_animal_success(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test create_animal success"""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = Mock()
        mock_user.id = 1
        mock_user.tenant_id = 1
        mock_estado = Mock()
        mock_estado.value = 'activo'
        mock_user.estado = mock_estado
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        data = {
            'nombre': 'VacaNueva',
            'raza': 'Holstein',
            'fecha_nacimiento': '2020-01-01',
            'estado': 'activo'
        }
        
        from flask import jsonify
        mock_response = jsonify({
            'data': {**data, 'id': 10},
            'message': 'Ganado creado exitosamente',
            'success': True
        })
        mock_response.status_code = 201
        mock_controller_class.crear_ganado.return_value = (mock_response, 201)

        response = self.client.post('/api/animales/', json=data, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 201
        data_resp = response.get_json()
        assert data_resp['success'] is True


    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.animal_controller.GanadoController')
    def test_create_animal_missing_nombre(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test create_animal missing nombre"""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = Mock()
        mock_user.id = 1
        mock_user.tenant_id = 1
        mock_estado = Mock()
        mock_estado.value = 'activo'
        mock_user.estado = mock_estado
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        from flask import jsonify
        mock_response = jsonify({
            'status': 'error',
            'message': 'El nombre es requerido',
            'success': False
        })
        mock_response.status_code = 400
        mock_controller_class.crear_ganado.return_value = (mock_response, 400)
        
        data = {'raza': 'Holstein', 'fecha_nacimiento': '2020-01-01', 'estado': 'activo'}

        response = self.client.post('/api/animales/', json=data, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 400
        data_resp = response.get_json()
        assert data_resp['success'] is False

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.animal_controller.GanadoController')
    def test_create_animal_missing_raza(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test create_animal missing raza"""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = Mock()
        mock_user.id = 1
        mock_user.tenant_id = 1
        mock_estado = Mock()
        mock_estado.value = 'activo'
        mock_user.estado = mock_estado
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        from flask import jsonify
        mock_response = jsonify({
            'status': 'error',
            'message': 'La raza es requerida',
            'success': False
        })
        mock_response.status_code = 400
        mock_controller_class.crear_ganado.return_value = (mock_response, 400)
        
        data = {'nombre': 'Vaca', 'fecha_nacimiento': '2020-01-01', 'estado': 'activo'}

        response = self.client.post('/api/animales/', json=data, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 400
        data_resp = response.get_json()
        assert data_resp['success'] is False

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.animal_controller.GanadoController')
    def test_create_animal_missing_fecha(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test create_animal missing fecha_nacimiento"""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = Mock()
        mock_user.id = 1
        mock_user.tenant_id = 1
        mock_estado = Mock()
        mock_estado.value = 'activo'
        mock_user.estado = mock_estado
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        from flask import jsonify
        mock_response = jsonify({
            'status': 'error',
            'message': 'La fecha de nacimiento es requerida',
            'success': False
        })
        mock_response.status_code = 400
        mock_controller_class.crear_ganado.return_value = (mock_response, 400)
        
        data = {'nombre': 'Vaca', 'raza': 'Holstein', 'estado': 'activo'}

        response = self.client.post('/api/animales/', json=data, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 400
        data_resp = response.get_json()
        assert data_resp['success'] is False

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.animal_controller.GanadoController')
    def test_create_animal_missing_estado(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test create_animal missing estado"""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = Mock()
        mock_user.id = 1
        mock_user.tenant_id = 1
        mock_estado = Mock()
        mock_estado.value = 'activo'
        mock_user.estado = mock_estado
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        from flask import jsonify
        mock_response = jsonify({
            'status': 'error',
            'message': 'El estado es requerido',
            'success': False
        })
        mock_response.status_code = 400
        mock_controller_class.crear_ganado.return_value = (mock_response, 400)
        
        data = {'nombre': 'Vaca', 'raza': 'Holstein', 'fecha_nacimiento': '2020-01-01'}

        response = self.client.post('/api/animales/', json=data, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 400
        data_resp = response.get_json()
        assert data_resp['success'] is False

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.animal_controller.GanadoController')
    def test_create_animal_crear_fails(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test create_animal crear fails"""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = Mock()
        mock_user.id = 1
        mock_user.tenant_id = 1
        mock_estado = Mock()
        mock_estado.value = 'activo'
        mock_user.estado = mock_estado
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        from flask import jsonify
        mock_response = jsonify({
            'status': 'error',
            'message': 'No se pudo crear el animal',
            'success': False
        })
        mock_response.status_code = 500
        mock_controller_class.crear_ganado.return_value = (mock_response, 500)
        
        data = {
            'nombre': 'VacaNueva',
            'raza': 'Holstein',
            'fecha_nacimiento': '2020-01-01',
            'estado': 'activo'
        }

        response = self.client.post('/api/animales/', json=data, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500
        data_resp = response.get_json()
        assert data_resp['success'] is False

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.animal_controller.GanadoController')
    def test_create_animal_exception(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test create_animal exception"""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = Mock()
        mock_user.id = 1
        mock_user.tenant_id = 1
        mock_estado = Mock()
        mock_estado.value = 'activo'
        mock_user.estado = mock_estado
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        from flask import jsonify
        mock_response = jsonify({
            'status': 'error',
            'message': 'Error interno del servidor: DB error',
            'success': False
        })
        mock_response.status_code = 500
        mock_controller_class.crear_ganado.return_value = (mock_response, 500)
        
        data = {
            'nombre': 'VacaNueva',
            'raza': 'Holstein',
            'fecha_nacimiento': '2020-01-01',
            'estado': 'activo'
        }

        response = self.client.post('/api/animales/', json=data, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500
        data_resp = response.get_json()
        assert data_resp['success'] is False