# Controlador Ganado
from typing import Optional
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
        print("WebSocket no disponible, evento omitido: " + str(event))

# Constantes para mensajes de error
GANADO_NO_ENCONTRADO = 'Ganado no encontrado'

class GanadoController:
    @staticmethod
    def _parsear_fecha_nacimiento(data: dict) -> dict:
        """Parsea la fecha de nacimiento del diccionario de datos."""
        if 'fecha_nacimiento' in data and data['fecha_nacimiento']:
            try:
                data['fecha_nacimiento'] = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
            except (ValueError, TypeError) as date_error:
                raise ValueError('Formato de fecha inválido: ' + str(data.get("fecha_nacimiento"))) from date_error
        return data

    @staticmethod
    def _obtener_tenant_id_desde_contexto() -> Optional[int]:
        """Obtiene el tenant_id desde el contexto Flask."""
        from flask import g
        from src.utils.tenant import get_current_tenant_id
        
        if hasattr(g, 'tenant_id') and g.tenant_id is not None:
            return g.tenant_id
        if hasattr(g, 'current_user') and g.current_user and hasattr(g.current_user, 'tenant_id'):
            return g.current_user.tenant_id
        return get_current_tenant_id(require_tenant=True)

    @staticmethod
    def _crear_ganado_modelo(data: dict) -> Ganado:
        """Crea el modelo Ganado desde los datos recibidos."""
        try:
            return Ganado.from_dict(data)
        except (ValueError, KeyError) as model_error:
            raise ValueError('Error en los datos del animal: ' + str(model_error)) from model_error

    @staticmethod
    def _procesar_creacion_ganado(ganado: Ganado, tenant_id: Optional[int]) -> Optional[Ganado]:
        """Procesa la creación del ganado llamando al servicio."""
        try:
            return GanadoService.crear_ganado(ganado, tenant_id_override=tenant_id)
        except ValueError as service_error:
            raise ValueError(str(service_error)) from service_error
        except Exception as service_error:
            raise RuntimeError('Error al crear el animal: ' + str(service_error)) from service_error

    @staticmethod
    @token_required
    @tenant_required
    @permission_required('crear_ganado')
    def crear_ganado():
        """Crea un nuevo animal."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': 'No se proporcionaron datos',
                    'success': False
                }), 400

            data = GanadoController._parsear_fecha_nacimiento(data)
            ganado = GanadoController._crear_ganado_modelo(data)
            tenant_id = GanadoController._obtener_tenant_id_desde_contexto()
            
            if tenant_id is None:
                return jsonify({
                    'status': 'error',
                    'message': 'No se pudo determinar el tenant del usuario',
                    'success': False
                }), 403

            nuevo_ganado = GanadoController._procesar_creacion_ganado(ganado, tenant_id)

            if nuevo_ganado:
                # Crear QR para el ganado después de crearlo exitosamente
                try:
                    from ..services.qr_service import QRService
                    id_persona_encargado = data.get('id_persona_encargado')
                    id_persona_dueno = data.get('id_persona_dueno') or data.get('id_persona')
                    qr_creado = QRService.crear_qr_ganado(
                        id_ganado=nuevo_ganado.id,
                        id_persona_encargado=id_persona_encargado,
                        id_persona_dueno=id_persona_dueno
                    )
                    if not qr_creado:
                        print(f"Advertencia: No se pudo crear QR para el ganado {nuevo_ganado.id}")
                except Exception as qr_error:
                    print(f"Error creando QR para ganado {nuevo_ganado.id}: {qr_error}")
                    # No fallar la creación del animal si el QR falla, solo registrar el error
                
                payload = nuevo_ganado.to_dict()
                try:
                    emit_update('animal_created', {'data': payload})
                except Exception as ws_error:
                    print("No se pudo emitir animal_created: " + str(ws_error))

                return jsonify({
                    'status': 'success',
                    'message': 'Ganado creado exitosamente',
                    'data': payload,
                    'success': True
                }), 201
            
            return jsonify({
                'status': 'error',
                'message': 'No se pudo crear el animal',
                'success': False
            }), 500

        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': str(e),
                'success': False
            }), 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': 'Error interno del servidor: ' + str(e),
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
            
            print(f"[ANIMAL_CONTROLLER] obtener_ganado({id}): ganado={'encontrado' if ganado else 'NO encontrado'}")
            if ganado:
                print(f"[ANIMAL_CONTROLLER] Ganado tiene {len(ganado.get('vacunas', []))} vacunas")
                print(f"[ANIMAL_CONTROLLER] Vacunas: {ganado.get('vacunas', [])}")
            
            if ganado:
                return jsonify({
                    'status': 'success',
                    'success': True,  # Compatibilidad con frontend
                    'data': ganado
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'success': False,  # Compatibilidad con frontend
                    'message': GANADO_NO_ENCONTRADO
                }), 404

        except ValueError as e:
            return jsonify({
                'status': 'error',
                'success': False,
                'message': str(e)
            }), 400
        except Exception as e:
            print(f"[ERROR] Controller - Error obteniendo ganado {id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'success': False,
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
            print("[ERROR] Controller - Error obteniendo animales: " + str(e))
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
                    print("No se pudo emitir animal_updated: " + str(ws_error))

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
                    print("No se pudo emitir animal_deactivated: " + str(ws_error))
                
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
            print("Error en dar_baja_ganado: " + str(e))
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
                    print("No se pudo emitir animal_reactivated: " + str(ws_error))
                
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
            print("Error en reactivar_ganado: " + str(e))
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
            print("Error en eliminar_ganado: " + str(e))
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
            
            # Usar obtener_ganado_detallado directamente con el código QR para obtener todos los datos
            detalle = GanadoService.obtener_ganado_detallado(codigo_qr, tenant_id_override=tenant_id)

            if detalle:
                print(f"[ANIMAL_CONTROLLER] buscar_por_codigo_qr({codigo_qr}): Ganado encontrado con {len(detalle.get('vacunas', []))} vacunas")
                return jsonify({
                    'status': 'success',
                    'success': True,
                    'data': detalle
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'success': False,
                    'message': GANADO_NO_ENCONTRADO
                }), 404

        except Exception as e:
            print(f"[ERROR] Controller - Error buscando ganado por QR {codigo_qr}: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'success': False,
                'message': str(e)
            }), 500
