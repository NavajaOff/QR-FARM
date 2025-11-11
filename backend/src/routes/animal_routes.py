from flask import Blueprint, jsonify, request, send_from_directory
from src.services.potrero_service import PotreroService
from src.services.animal_service import GanadoService
from src.models.animal import Ganado
import os
ERROR_INTERNO_SERVIDOR = 'Error interno del servidor'
DATOS_INVALIDOS = 'Datos inválidos'

try:
    from ...app import emit_update
except ImportError:
    def emit_update(event, data=None):
        print(f"WebSocket no disponible, evento omitido: {event}")

animal_bp = Blueprint('animal', __name__, url_prefix='/api/animales')

@animal_bp.route('/estados-ganado', methods=['GET'])
def get_estados_ganado():
    """Obtener los estados posibles del ganado usando GanadoService."""
    try:
        estados = GanadoService.obtener_estados_ganado()
        # Si no hay conexión a BD, retornar estados por defecto
        if not estados:
            estados = [
                {'id': 1, 'estado': 'activo', 'nombre_estado': 'activo'},
                {'id': 2, 'estado': 'saludable', 'nombre_estado': 'saludable'},
                {'id': 3, 'estado': 'revision', 'nombre_estado': 'revision'},
                {'id': 4, 'estado': 'enfermo', 'nombre_estado': 'enfermo'},
                {'id': 5, 'estado': 'vendido', 'nombre_estado': 'vendido'}
            ]
        return jsonify({'data': estados, 'success': True}), 200
    except Exception as e:
        print(f"Error obteniendo estados de ganado: {e}")
        # Retornar estados por defecto en caso de error
        estados_default = [
            {'id': 1, 'estado': 'activo', 'nombre_estado': 'activo'},
            {'id': 2, 'estado': 'saludable', 'nombre_estado': 'saludable'},
            {'id': 3, 'estado': 'revision', 'nombre_estado': 'revision'},
            {'id': 4, 'estado': 'enfermo', 'nombre_estado': 'enfermo'},
            {'id': 5, 'estado': 'vendido', 'nombre_estado': 'vendido'}
        ]
        return jsonify({'data': estados_default, 'success': True}), 200

@animal_bp.route('/', methods=['GET'])
def get_animales():
    """Obtener todos los animales."""
    try:
        animales = GanadoService.obtener_todos_ganados()
        return jsonify({'data': [animal.to_dict() for animal in animales], 'success': True}), 200
    except Exception as e:
        print(f"Error obteniendo animales: {e}")
        return jsonify({'data': [], 'success': True}), 200

@animal_bp.route('/<int:animal_id>', methods=['GET'])
def get_animal(animal_id):
    """Obtener un animal por ID."""
    try:
        animal = GanadoService.obtener_ganado(animal_id)
        if animal:
            return jsonify({'data': animal.to_dict(), 'success': True}), 200
        else:
            return jsonify({
                'error': 'Animal no encontrado',
                'message': f'No se encontró el animal con ID {animal_id}',
                'success': False
            }), 404
    except Exception as e:
        print(f"Error obteniendo animal {animal_id}: {e}")
        return jsonify({
            'error': ERROR_INTERNO_SERVIDOR,
            'message': str(e),
            'success': False
        }), 500

@animal_bp.route('/qr/<codigo_qr>.png', methods=['GET'])
def get_qr_image(codigo_qr):
    """Servir imágenes QR."""
    try:
        qr_dir = os.path.join(os.getcwd(), 'qr')
        return send_from_directory(qr_dir, f"{codigo_qr}.png")
    except Exception as e:
        print(f"Error sirviendo QR {codigo_qr}: {e}")
        return jsonify({
            'error': 'Imagen no encontrada',
            'message': f'No se encontró la imagen QR {codigo_qr}',
            'success': False
        }), 404

@animal_bp.route('/<int:animal_id>', methods=['PUT'])
def update_animal(animal_id):
    """Actualizar un animal."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': DATOS_INVALIDOS,
                'message': 'No se proporcionaron datos para actualizar',
                'success': False
            }), 400

        # Obtener el animal actual primero
        animal_actual = GanadoService.obtener_ganado(animal_id)
        if not animal_actual:
            return jsonify({
                'error': 'Animal no encontrado',
                'message': f'No se encontró el animal con ID {animal_id}',
                'success': False
            }), 404

        # Crear instancia del modelo con los datos actualizados
        animal_data = animal_actual.to_dict()  # Empezar con los datos actuales
        animal_data.update(data)  # Actualizar solo los campos enviados
        animal_data['id'] = animal_id  # Asegurar que tenga el ID correcto

        animal = Ganado.from_dict(animal_data)

        # Actualizar en la base de datos
        actualizado = GanadoService.actualizar_ganado(animal_id, animal)

        if actualizado:
            # Obtener el animal actualizado
            animal_actualizado = GanadoService.obtener_ganado(animal_id)
            # Emitir actualización en tiempo real
            emit_update('animal_updated', {
                'id': animal_id,
                'data': animal_actualizado.to_dict()
            })
            return jsonify({
                'data': animal_actualizado.to_dict(),
                'message': 'Animal actualizado correctamente',
                'success': True
            }), 200
        else:
            return jsonify({
                'error': 'Error al actualizar animal',
                'message': 'No se pudo actualizar el animal',
                'success': False
            }), 500

    except Exception as e:
        print(f"Error actualizando animal {animal_id}: {e}")
        return jsonify({
            'error': ERROR_INTERNO_SERVIDOR,
            'message': str(e),
            'success': False
        }), 500

@animal_bp.route('/', methods=['POST'])
def create_animal():
    """Create a new animal."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': DATOS_INVALIDOS,
                'message': 'No se proporcionaron datos',
                'success': False
            }), 400

        # Validaciones básicas
        if not data.get('nombre'):
            return jsonify({
                'error': DATOS_INVALIDOS,
                'message': 'El nombre es requerido',
                'success': False
            }), 400

        if not data.get('raza'):
            return jsonify({
                'error': DATOS_INVALIDOS,
                'message': 'La raza es requerida',
                'success': False
            }), 400

        if not data.get('fecha_nacimiento'):
            return jsonify({
                'error': DATOS_INVALIDOS,
                'message': 'La fecha de nacimiento es requerida',
                'success': False
            }), 400

        if not data.get('estado'):
            return jsonify({
                'error': DATOS_INVALIDOS,
                'message': 'El estado es requerido',
                'success': False
            }), 400

        # Crear instancia del modelo
        animal = Ganado.from_dict(data)

        # Guardar en la base de datos
        animal_creado = GanadoService.crear_ganado(animal)

        if animal_creado:
            # Crear QR para el ganado
            from src.services.qr_service import QRService
            qr_creado = QRService.crear_qr_ganado(
                id_ganado=animal_creado.id,
                id_persona_encargado=data.get('id_persona_encargado'),
                id_persona_dueno=data.get('id_persona_dueno')
            )

            if not qr_creado:
                print(f"Warning: No se pudo crear QR para el ganado {animal_creado.id}")

            # Emitir actualización en tiempo real para nuevo animal
            emit_update('animal_created', {
                'data': animal_creado.to_dict()
            })
            return jsonify({
                'data': animal_creado.to_dict(),
                'message': 'Animal creado correctamente',
                'success': True
            }), 201
        else:
            return jsonify({
                'error': 'Error al crear animal',
                'message': 'No se pudo crear el animal',
                'success': False
            }), 500

    except Exception as e:
        print(f"Error creando animal: {e}")
        return jsonify({
            'error': ERROR_INTERNO_SERVIDOR,
            'message': str(e),
            'success': False
        }), 500
