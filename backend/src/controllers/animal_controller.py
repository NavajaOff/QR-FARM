# Controlador Ganado
from datetime import datetime
from flask import jsonify, request
from ..models.animal import Ganado
from ..services.animal_service import GanadoService

try:
    from ...app import emit_update
except ImportError:
    def emit_update(event, _data=None):  # type: ignore
        print(f"WebSocket no disponible, evento omitido: {event}")

# Constantes para mensajes de error
GANADO_NO_ENCONTRADO = 'Ganado no encontrado'

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

        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def obtener_ganado(id):
        try:
            ganado = GanadoService.obtener_ganado_detallado(id)

            if ganado:
                return jsonify({
                    'status': 'success',
                    'data': ganado
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': GANADO_NO_ENCONTRADO
                }), 404

        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def obtener_todos_ganados():
        try:
            # Siempre devolver todos los animales para simplificar
            ganados = GanadoService.obtener_todos_ganados()
            print(f"[DEBUG] Controller - Animales devueltos: {len(ganados)}")
            return jsonify({
                'status': 'success',
                'data': [ganado.to_dict() for ganado in ganados],
                'success': True
            }), 200

        except Exception as e:
            print(f"[ERROR] Controller - Error obteniendo animales: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def obtener_estados_ganado():
        """
        Obtiene los estados de ganado filtrados por tipo.

        Query parameters:
        - solo_activos: boolean - Si es true, retorna solo estados activos (1-3)
        - solo_bajas: boolean - Si es true, retorna solo estados de baja (4-8)
        """
        try:
            from ..services.animal_service import GanadoService
            solo_activos = request.args.get('solo_activos', 'false').lower() == 'true'
            solo_bajas = request.args.get('solo_bajas', 'false').lower() == 'true'
            estados = GanadoService.obtener_estados_ganado(solo_activos=solo_activos, solo_bajas=solo_bajas)
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
                    'message': GANADO_NO_ENCONTRADO
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
    def dar_baja_ganado(id):
        """Da de baja lógica a un animal."""
        try:
            data = request.get_json()
            causa_baja = data.get('causa_baja')
            observaciones = data.get('observaciones')
            
            if not causa_baja:
                return jsonify({
                    'status': 'error',
                    'message': 'La causa de baja es requerida',
                    'success': False
                }), 400
            
            result = GanadoService.dar_baja_ganado(id, causa_baja, observaciones)
            
            if result is True:
                try:
                    emit_update('animal_deactivated', {'id': id})
                except Exception as ws_error:
                    print(f"No se pudo emitir animal_deactivated: {ws_error}")
                
                return jsonify({
                    'status': 'success',
                    'message': 'Animal dado de baja correctamente',
                    'success': True
                }), 200
            elif isinstance(result, str):
                return jsonify({
                    'status': 'error',
                    'message': result,
                    'success': False
                }), 400
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Error al dar de baja el animal',
                    'success': False
                }), 500
        except Exception as e:
            print(f"Error en dar_baja_ganado: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def reactivar_ganado(id):
        """Reactivar un animal que estaba dado de baja."""
        try:
            data = request.get_json() or {}
            nuevo_estado = data.get('nuevo_estado', 'saludable')
            result = GanadoService.reactivar_ganado(id, nuevo_estado)
            
            if result is True:
                try:
                    emit_update('animal_reactivated', {'id': id})
                except Exception as ws_error:
                    print(f"No se pudo emitir animal_reactivated: {ws_error}")
                
                return jsonify({
                    'status': 'success',
                    'message': 'Animal reactivado correctamente',
                    'success': True
                }), 200
            elif isinstance(result, str):
                return jsonify({
                    'status': 'error',
                    'message': result,
                    'success': False
                }), 400
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Error al reactivar el animal',
                    'success': False
                }), 500
        except Exception as e:
            print(f"Error en reactivar_ganado: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def eliminar_ganado(id):
        """Elimina un ganado usando GanadoService.eliminar_ganado()."""
        try:
            result = GanadoService.eliminar_ganado(id)
            
            if result is True:
                return jsonify({
                    'status': 'success',
                    'message': 'Ganado eliminado exitosamente'
                }), 200
            elif result is False:
                return jsonify({
                    'status': 'error',
                    'message': 'Ganado no encontrado o error al eliminar'
                }), 404
            elif isinstance(result, str):
                return jsonify({
                    'status': 'error',
                    'message': result
                }), 400
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Error inesperado al eliminar el ganado'
                }), 500
        except Exception as e:
            print(f"Error en eliminar_ganado: {str(e)}")
            import traceback
            traceback.print_exc()
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
                detalle = GanadoService.obtener_ganado_detallado(ganado.id) if ganado.id else None
                return jsonify({
                    'status': 'success',
                    'data': detalle if detalle else ganado.to_dict()
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': GANADO_NO_ENCONTRADO
                }), 404

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
