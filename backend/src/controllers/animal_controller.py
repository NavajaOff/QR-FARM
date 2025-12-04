# Controlador Ganado
from datetime import datetime
from flask import jsonify, request
from ..models.animal import Ganado
from ..services.animal_service import GanadoService
from ..utils.auth import token_required
from ..utils.tenant import tenant_required
from ..utils.permissions import permission_required

try:
    from ...app import emit_update
except ImportError:
    def emit_update(event, _data=None):  # type: ignore
        print(f"WebSocket no disponible, evento omitido: {event}")

# Constantes para mensajes de error
GANADO_NO_ENCONTRADO = 'Ganado no encontrado'

class GanadoController:
    @staticmethod
    @token_required
    @tenant_required
    @permission_required('crear_ganado')
    def crear_ganado():
        print(f"[GANADO_CONTROLLER] 🚀 crear_ganado() INICIADO")
        try:
            from flask import g
            print(f"[GANADO_CONTROLLER] Verificando contexto Flask g...")
            print(f"[GANADO_CONTROLLER] g.tenant_id: {getattr(g, 'tenant_id', 'NO EXISTE')}")
            print(f"[GANADO_CONTROLLER] g.current_user existe: {hasattr(g, 'current_user')}")
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': 'No se proporcionaron datos',
                    'success': False
                }), 400

            print(f"[GANADO_CONTROLLER] Datos recibidos: {data}")

            # Convertir fechas de string a objeto date si están presentes
            if 'fecha_nacimiento' in data and data['fecha_nacimiento']:
                try:
                    data['fecha_nacimiento'] = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
                except (ValueError, TypeError) as date_error:
                    print(f"[GANADO_CONTROLLER] Error parseando fecha: {date_error}")
                    return jsonify({
                        'status': 'error',
                        'message': f'Formato de fecha inválido: {data.get("fecha_nacimiento")}',
                        'success': False
                    }), 400

            try:
                ganado = Ganado.from_dict(data)
            except (ValueError, KeyError) as model_error:
                print(f"[GANADO_CONTROLLER] Error creando modelo Ganado: {model_error}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'status': 'error',
                    'message': f'Error en los datos del animal: {str(model_error)}',
                    'success': False
                }), 400

            # Obtener tenant_id desde el contexto Flask antes de llamar al servicio
            from flask import g
            tenant_id = None
            if hasattr(g, 'tenant_id') and g.tenant_id is not None:
                tenant_id = g.tenant_id
                print(f"[GANADO_CONTROLLER] Tenant ID obtenido desde g.tenant_id: {tenant_id}")
            elif hasattr(g, 'current_user') and g.current_user and hasattr(g.current_user, 'tenant_id'):
                tenant_id = g.current_user.tenant_id
                print(f"[GANADO_CONTROLLER] Tenant ID obtenido desde g.current_user.tenant_id: {tenant_id}")
            else:
                from src.utils.tenant import get_current_tenant_id
                tenant_id = get_current_tenant_id(require_tenant=True)
                print(f"[GANADO_CONTROLLER] Tenant ID obtenido desde get_current_tenant_id(): {tenant_id}")
            
            if tenant_id is None:
                return jsonify({
                    'status': 'error',
                    'message': 'No se pudo determinar el tenant del usuario',
                    'success': False
                }), 403

            try:
                nuevo_ganado = GanadoService.crear_ganado(ganado, tenant_id_override=tenant_id)
            except ValueError as service_error:
                print(f"[GANADO_CONTROLLER] Error en servicio (ValueError): {service_error}")
                return jsonify({
                    'status': 'error',
                    'message': str(service_error),
                    'success': False
                }), 400
            except Exception as service_error:
                print(f"[GANADO_CONTROLLER] Error en servicio: {service_error}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'status': 'error',
                    'message': f'Error al crear el animal: {str(service_error)}',
                    'success': False
                }), 500

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
                    'data': payload,
                    'success': True
                }), 201
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'No se pudo crear el animal',
                    'success': False
                }), 500

        except ValueError as e:
            print(f"[GANADO_CONTROLLER] ValueError: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'message': str(e),
                'success': False
            }), 400
        except Exception as e:
            print(f"[GANADO_CONTROLLER] Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'message': f'Error interno del servidor: {str(e)}',
                'success': False
            }), 500

    @staticmethod
    @token_required
    @tenant_required
    @permission_required('ver_ganado')
    def obtener_ganado(id):
        """Obtener ganado por ID. Acepta tenant_id como query param para super admin."""
        try:
            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass
            
            ganado = GanadoService.obtener_ganado_detallado(id, tenant_id_override=tenant_id)

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
    @token_required
    @tenant_required
    @permission_required('ver_ganado')
    def obtener_todos_ganados():
        """Obtener todos los ganados. Acepta tenant_id como query param para super admin."""
        try:
            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass

            ganados = GanadoService.obtener_todos_ganados(tenant_id_override=tenant_id)
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
    @token_required
    @tenant_required
    @permission_required('editar_ganado')
    def actualizar_ganado(id):
        """Actualizar ganado. Acepta tenant_id como query param para super admin."""
        try:
            data = request.get_json()

            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass

            # Obtener el ganado existente
            ganado_existente = GanadoService.obtener_ganado(id, tenant_id_override=tenant_id)
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
            if GanadoService.actualizar_ganado(id, ganado_existente, tenant_id_override=tenant_id):
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
    @token_required
    @tenant_required
    @permission_required('eliminar_ganado')
    def dar_baja_ganado(id):
        """Da de baja lógica a un animal. Acepta tenant_id como query param para super admin."""
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
            
            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass
            
            result = GanadoService.dar_baja_ganado(id, causa_baja, observaciones, tenant_id_override=tenant_id)
            
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
    @token_required
    @tenant_required
    @permission_required('editar_ganado')
    def reactivar_ganado(id):
        """Reactivar un animal que estaba dado de baja. Acepta tenant_id como query param para super admin."""
        try:
            data = request.get_json() or {}
            nuevo_estado = data.get('nuevo_estado', 'saludable')
            
            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass
            
            result = GanadoService.reactivar_ganado(id, nuevo_estado, tenant_id_override=tenant_id)
            
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
    @token_required
    @tenant_required
    @permission_required('eliminar_ganado')
    def eliminar_ganado(id):
        """Elimina un ganado usando GanadoService.eliminar_ganado(). Acepta tenant_id como query param para super admin."""
        try:
            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass
            
            result = GanadoService.eliminar_ganado(id, tenant_id_override=tenant_id)
            
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
    @token_required
    @tenant_required
    @permission_required('ver_ganado')
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
    @token_required
    @tenant_required
    @permission_required('escanear_qr')
    def buscar_por_codigo_qr(codigo_qr):
        """Buscar ganado por código QR. Acepta tenant_id como query param para super admin."""
        try:
            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass
            
            ganado = GanadoService.buscar_por_codigo_qr(codigo_qr, tenant_id_override=tenant_id)

            if ganado:
                detalle = GanadoService.obtener_ganado_detallado(ganado.id, tenant_id_override=tenant_id) if ganado.id else None
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
