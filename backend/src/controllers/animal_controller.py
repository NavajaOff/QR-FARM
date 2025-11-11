# Controlador Ganado
from datetime import datetime
from flask import jsonify, request
from ..models.animal import Ganado
from ..services.animal_service import GanadoService

try:
    from ...app import emit_update
except ImportError:
    def emit_update(event, data=None):  # type: ignore
        print(f"WebSocket no disponible, evento omitido: {event}")

class GanadoController:
    @staticmethod
    def crear_ganado():
        try:
            data = request.get_json()

            # Convertir fechas de string a objeto date si están presentes
            if 'fecha_nacimiento' in data:
                data['fecha_nacimiento'] = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()

            ganado = Ganado.from_dict(data)
            nuevo_ganado = GanadoService.crear_ganado(ganado)

            if nuevo_ganado:
                payload = nuevo_ganado.to_dict()
                try:
                    emit_update('animal_created', {
                        'data': payload
                    })
                except Exception as ws_error:
                    print(f"No se pudo emitir animal_created: {ws_error}")

                return jsonify({
                    'status': 'success',
                    'message': 'Ganado creado exitosamente',
                    'data': payload
                }), 201
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Error al crear el ganado'
                }), 400

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def obtener_ganado(id):
        try:
            ganado = GanadoService.obtener_ganado(id)

            if ganado:
                return jsonify({
                    'status': 'success',
                    'data': ganado.to_dict()
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Ganado no encontrado'
                }), 404

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def obtener_todos_ganados():
        try:
            ganados = GanadoService.obtener_todos_ganados()
            return jsonify({
                'status': 'success',
                'data': [ganado.to_dict() for ganado in ganados]
            }), 200

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def obtener_estados_ganado():
        try:
            from ..services.animal_service import GanadoService
            estados = GanadoService.obtener_estados_ganado()
            return jsonify({
                'status': 'success',
                'data': estados
            }), 200

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def actualizar_ganado(id):
        try:
            data = request.get_json()

            # Obtener el ganado existente
            ganado_existente = GanadoService.obtener_ganado(id)
            if not ganado_existente:
                return jsonify({
                    'status': 'error',
                    'message': 'Ganado no encontrado'
                }), 404

            # Actualizar los campos del ganado con los nuevos datos
            for key, value in data.items():
                if key == 'fecha_nacimiento' and value:
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                setattr(ganado_existente, key, value)

            # Intentar actualizar en la base de datos
            if GanadoService.actualizar_ganado(id, ganado_existente):
                payload = ganado_existente.to_dict()
                try:
                    emit_update('animal_updated', {
                        'id': id,
                        'data': payload
                    })
                except Exception as ws_error:
                    print(f"No se pudo emitir animal_updated: {ws_error}")

                return jsonify({
                    'status': 'success',
                    'message': 'Ganado actualizado exitosamente',
                    'data': payload
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Error al actualizar el ganado'
                }), 400

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def eliminar_ganado(id):
        try:
            if GanadoService.eliminar_ganado(id):
                try:
                    emit_update('animal_deleted', {
                        'id': id
                    })
                except Exception as ws_error:
                    print(f"No se pudo emitir animal_deleted: {ws_error}")

                return jsonify({
                    'status': 'success',
                    'message': 'Ganado eliminado exitosamente'
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Ganado no encontrado o error al eliminar'
                }), 404

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def obtener_ganados_por_potrero(potrero_id):
        try:
            ganados = GanadoService.buscar_por_potrero(potrero_id)
            return jsonify({
                'status': 'success',
                'data': [ganado.to_dict() for ganado in ganados]
            }), 200

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def buscar_por_codigo_qr(codigo_qr):
        try:
            ganado = GanadoService.buscar_por_codigo_qr(codigo_qr)

            if ganado:
                return jsonify({
                    'status': 'success',
                    'data': ganado.to_dict()
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Ganado no encontrado'
                }), 404

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
