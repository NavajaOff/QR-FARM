from flask import Blueprint, jsonify, request, send_from_directory
from src.services.potrero_service import PotreroService
from src.services.animal_service import GanadoService
from src.models.animal import Ganado
from src.utils.auth import token_required
import os

# Constantes para mensajes de error
ERROR_INTERNO_SERVIDOR = 'Error interno del servidor'
DATOS_INVALIDOS = 'Datos inválidos'
ANIMAL_NO_ENCONTRADO = 'Animal no encontrado'

# Estados por defecto para fallback
ESTADOS_DEFAULT = [
    {'id': 1, 'estado': 'activo', 'nombre_estado': 'activo'},
    {'id': 2, 'estado': 'saludable', 'nombre_estado': 'saludable'},
    {'id': 3, 'estado': 'revision', 'nombre_estado': 'revision'},
    {'id': 4, 'estado': 'enfermo', 'nombre_estado': 'enfermo'},
    {'id': 5, 'estado': 'vendido', 'nombre_estado': 'vendido'}
]

# Parámetros de query string
PARAM_SOLO_ACTIVOS = 'solo_activos'
PARAM_SOLO_BAJAS = 'solo_bajas'
VALOR_TRUE = 'true'

try:
    from ...app import emit_update
except ImportError:
    def emit_update(event, _data=None):
        print(f"WebSocket no disponible, evento omitido: {event}")

animal_bp = Blueprint('animal', __name__, url_prefix='/api/animales')

@animal_bp.route('/estados-ganado', methods=['GET'])
def get_estados_ganado():
    """
    Obtener los estados posibles del ganado.

    Query parameters:
    - solo_activos: boolean - Si es true, retorna solo estados activos (1-3)
    - solo_bajas: boolean - Si es true, retorna solo estados de baja (4-8)
    """
    try:
        solo_activos = request.args.get(PARAM_SOLO_ACTIVOS, 'false').lower() == VALOR_TRUE
        solo_bajas = request.args.get(PARAM_SOLO_BAJAS, 'false').lower() == VALOR_TRUE
        estados = GanadoService.obtener_estados_ganado(solo_activos=solo_activos, solo_bajas=solo_bajas)
        # Si no hay conexión a BD, retornar estados por defecto
        if not estados:
            estados = ESTADOS_DEFAULT
        return jsonify({'data': estados, 'success': True}), 200
    except Exception as e:
        print(f"Error obteniendo estados de ganado: {e}")
        # Retornar estados por defecto en caso de error
        return jsonify({'data': ESTADOS_DEFAULT, 'success': True}), 200

@animal_bp.route('/', methods=['GET'])
def get_animales():
    """Obtener todos los animales."""
    try:
        from src.controllers.animal_controller import GanadoController
        return GanadoController.obtener_todos_ganados()
    except Exception as e:
        print(f"Error obteniendo animales: {e}")
        return jsonify({'data': [], 'success': True}), 200

@animal_bp.route('/qr/<codigo_qr>', methods=['GET'])
def get_animal_by_qr(codigo_qr):
    """Obtener un animal por código QR."""
    try:
        from src.controllers.animal_controller import GanadoController
        return GanadoController.buscar_por_codigo_qr(codigo_qr)
    except Exception as e:
        print(f"Error obteniendo animal por QR {codigo_qr}: {e}")
        return jsonify({
            'error': ERROR_INTERNO_SERVIDOR,
            'message': str(e),
            'success': False
        }), 500

@animal_bp.route('/<int:animal_id>', methods=['GET'])
def get_animal(animal_id):
    """Obtener un animal por ID."""
    try:
        from src.controllers.animal_controller import GanadoController
        return GanadoController.obtener_ganado(animal_id)
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
@token_required
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
                'error': ANIMAL_NO_ENCONTRADO,
                'message': f'No se encontró el animal con ID {animal_id}',
                'success': False
            }), 404

        # Crear instancia del modelo con los datos actualizados
        animal_data = animal_actual.to_dict()  # Empezar con los datos actuales
        print(f"[ANIMAL_ROUTES] Datos actuales del animal: estado={animal_data.get('estado')}, id_estado={animal_data.get('id_estado')}, estado_tipo={animal_data.get('estado_tipo')}")
        print(f"[ANIMAL_ROUTES] Datos recibidos para actualizar: {data}")
        print(f"[ANIMAL_ROUTES] Estado recibido en data: {data.get('estado')}")
        
        # Actualizar solo los campos enviados
        animal_data.update(data)
        # Si se envió un nuevo estado, limpiar estado_tipo para que from_dict use el nuevo estado
        if 'estado' in data and data.get('estado'):
            animal_data['estado_tipo'] = None  # Forzar que use el nuevo estado
            print(f"[ANIMAL_ROUTES] Limpiando estado_tipo para usar nuevo estado: {data.get('estado')}")
        
        animal_data['id'] = animal_id  # Asegurar que tenga el ID correcto

        print(f"[ANIMAL_ROUTES] Datos combinados después de update: estado={animal_data.get('estado')}, id_estado={animal_data.get('id_estado')}, estado_tipo={animal_data.get('estado_tipo')}")

        try:
            animal = Ganado.from_dict(animal_data)
            print(f"[ANIMAL_ROUTES] Objeto Ganado creado: estado={animal.estado}, id_estado={animal.id_estado}")
        except Exception as e:
            print(f"[ANIMAL_ROUTES] Error creando objeto Ganado: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

        # Actualizar en la base de datos
        actualizado = GanadoService.actualizar_ganado(animal_id, animal)
        print(f"[ANIMAL_ROUTES] Resultado de actualizar_ganado: {actualizado}")

        if actualizado:
            # Obtener el animal actualizado
            animal_actualizado = GanadoService.obtener_ganado(animal_id)
            if animal_actualizado:
                animal_dict = animal_actualizado.to_dict()
                print(f"[ANIMAL_ROUTES] Animal actualizado devuelto: estado={animal_dict.get('estado')}, id_estado={animal_dict.get('id_estado')}, estado_tipo={animal_dict.get('estado_tipo')}")
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

@animal_bp.route('/<int:animal_id>/baja', methods=['PUT'])
def dar_baja_animal(animal_id):
    """Dar de baja lógica a un animal."""
    try:
        from src.controllers.animal_controller import GanadoController
        return GanadoController.dar_baja_ganado(animal_id)
    except Exception as e:
        print(f"Error dando de baja animal {animal_id}: {e}")
        return jsonify({
            'error': ERROR_INTERNO_SERVIDOR,
            'message': str(e),
            'success': False
        }), 500

@animal_bp.route('/<int:animal_id>/reactivar', methods=['PUT'])
def reactivar_animal(animal_id):
    """Reactivar un animal que estaba dado de baja."""
    try:
        from src.controllers.animal_controller import GanadoController
        return GanadoController.reactivar_ganado(animal_id)
    except Exception as e:
        print(f"Error reactivando animal {animal_id}: {e}")
        return jsonify({
            'error': ERROR_INTERNO_SERVIDOR,
            'message': str(e),
            'success': False
        }), 500

@animal_bp.route('/<int:animal_id>', methods=['DELETE'])
def delete_animal(animal_id):
    """Eliminar un animal (legacy - ahora usa baja lógica)."""
    try:
        from src.controllers.animal_controller import GanadoController
        return GanadoController.eliminar_ganado(animal_id)
    except Exception as e:
        print(f"Error eliminando animal {animal_id}: {e}")
        return jsonify({
            'error': ERROR_INTERNO_SERVIDOR,
            'message': str(e),
            'success': False
        }), 500

@animal_bp.route('/', methods=['POST'])
def create_animal():
    """Create a new animal."""
    try:
        from src.controllers.animal_controller import GanadoController
        return GanadoController.crear_ganado()

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
