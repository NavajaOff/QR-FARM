"""Controller for Potrero endpoints."""
from typing import Tuple, Any
from datetime import datetime, date
from flask import jsonify, request
from ..database.db import DatabaseError
from ..services.potrero_service import PotreroService
from ..utils.auth import token_required
from ..utils.tenant import tenant_required
from ..utils.permissions import permission_required

class PotreroController:
    """Controller handling Potrero HTTP requests."""

    # Error message constants
    ERROR_INTERNO_SERVIDOR = 'Error interno del servidor'
    ERROR_BASE_DATOS = 'Error de base de datos'
    POTRERO_NO_ENCONTRADO = 'Potrero no encontrado'
    DATOS_INVALIDOS = 'Datos inválidos'
    FECHA_LIMPIEZA_FUTURA = 'La fecha de última limpieza no puede ser posterior al día actual'
    CAMPOS_OBLIGATORIOS = [
        'capacidad',
        'hectareas',
        'id_tipo_pasto',
        'responsable_persona_id',
        'ultima_limpieza',
        'area'
    ]
    CAMPOS_LABELS = {
        'capacidad': 'Capacidad',
        'hectareas': 'Hectáreas',
        'id_tipo_pasto': 'Tipo de pasto',
        'responsable_persona_id': 'Responsable',
        'ultima_limpieza': 'Última limpieza',
        'area': 'Área'
    }
    WEBSOCKET_NO_DISPONIBLE = 'WebSocket no disponible, omitiendo emisión'

    @staticmethod
    def _validar_fecha_ultima_limpieza(data: dict) -> None:
        fecha_raw = data.get('ultima_limpieza')
        if not fecha_raw:
            return

        try:
            if isinstance(fecha_raw, (datetime, date)) and not isinstance(fecha_raw, datetime):
                fecha_obj = fecha_raw
            else:
                fecha_obj = datetime.fromisoformat(str(fecha_raw).replace('Z', ''))
                fecha_obj = fecha_obj.date()
        except (ValueError, TypeError) as exc:
            raise ValueError('La fecha de última limpieza tiene un formato inválido') from exc

        if fecha_obj > date.today():
            raise ValueError(PotreroController.FECHA_LIMPIEZA_FUTURA)

    @staticmethod
    def _validar_campos_obligatorios(data: dict, require_all: bool = False) -> None:
        campos_a_validar = []
        if require_all:
            campos_a_validar = PotreroController.CAMPOS_OBLIGATORIOS
        else:
            campos_a_validar = [campo for campo in PotreroController.CAMPOS_OBLIGATORIOS if campo in data]

        campos_invalidos = []
        for campo in campos_a_validar:
            valor = data.get(campo)

            if valor is None:
                campos_invalidos.append(campo)
                continue

            if isinstance(valor, str) and valor.strip() == '':
                campos_invalidos.append(campo)
                continue

        if campos_invalidos:
            etiquetas = [PotreroController.CAMPOS_LABELS.get(c, c) for c in campos_invalidos]
            campos_texto = ', '.join(etiquetas)
            raise ValueError(f'Los siguientes campos obligatorios no pueden estar vacíos: {campos_texto}')

    @staticmethod
    @token_required
    @tenant_required
    @permission_required('ver_potreros')
    def get_all() -> Tuple[Any, int]:
        """Get all potreros endpoint. Acepta tenant_id como query param para super admin."""
        try:
            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass
            
            potreros = PotreroService.get_all(tenant_id_override=tenant_id)
            return jsonify({'data': potreros, 'success': True}), 200
        except Exception as e:
            print(f"Error en get_all potreros controller: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': PotreroController.ERROR_INTERNO_SERVIDOR,
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    @token_required
    @tenant_required
    @permission_required('ver_potreros')
    def get_by_id(potrero_id: int) -> Tuple[Any, int]:
        """Get potrero by ID endpoint. Acepta tenant_id como query param para super admin."""
        try:
            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass
            
            potrero = PotreroService.get_by_id(potrero_id, tenant_id_override=tenant_id)
            return jsonify({'data': potrero, 'success': True}), 200
        except ValueError as e:
            return jsonify({
                'error': PotreroController.POTRERO_NO_ENCONTRADO,
                'message': str(e),
                'success': False
            }), 404
        except DatabaseError as e:
            return jsonify({
                'error': PotreroController.ERROR_BASE_DATOS,
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': PotreroController.ERROR_INTERNO_SERVIDOR,
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    @token_required
    @tenant_required
    @permission_required('crear_potreros')
    def create() -> Tuple[Any, int]:
        """Create potrero endpoint."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': PotreroController.DATOS_INVALIDOS,
                    'message': 'No se proporcionaron datos',
                    'success': False
                }), 400

            print(f"Datos recibidos en controller: {data}")

            # El nombre puede ser null, el servicio lo generará automáticamente
            PotreroController._validar_fecha_ultima_limpieza(data)
            PotreroController._validar_campos_obligatorios(data, require_all=True)

            potrero = PotreroService.create(data)
            print(f"Potrero creado exitosamente: {potrero}")
            # Emitir actualización en tiempo real para nuevo potrero
            try:
                from ...app import emit_update
                emit_update('potrero_created', {
                    'data': potrero
                })
            except ImportError:
                print(PotreroController.WEBSOCKET_NO_DISPONIBLE)
            return jsonify({
                'data': potrero,
                'message': 'Potrero creado correctamente',
                'success': True
            }), 201
        except ValueError as e:
            print(f"Error de validación: {str(e)}")
            return jsonify({
                'error': PotreroController.DATOS_INVALIDOS,
                'message': str(e),
                'success': False
            }), 400
        except DatabaseError as e:
            print(f"Error de base de datos: {str(e)}")
            return jsonify({
                'error': PotreroController.ERROR_BASE_DATOS,
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            print(f"Error interno del servidor: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': PotreroController.ERROR_INTERNO_SERVIDOR,
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    @token_required
    @tenant_required
    @permission_required('editar_potreros')
    def update(potrero_id: int) -> Tuple[Any, int]:
        """Update potrero endpoint. Acepta tenant_id como query param para super admin."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': PotreroController.DATOS_INVALIDOS,
                    'message': 'No se proporcionaron datos para actualizar',
                    'success': False
                }), 400
            
            try:
                PotreroController._validar_fecha_ultima_limpieza(data)
            except ValueError as e:
                return jsonify({
                    'error': PotreroController.DATOS_INVALIDOS,
                    'message': str(e),
                    'success': False
                }), 400

            try:
                PotreroController._validar_campos_obligatorios(data, require_all=False)
            except ValueError as e:
                return jsonify({
                    'error': PotreroController.DATOS_INVALIDOS,
                    'message': str(e),
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
            
            potrero = PotreroService.update(potrero_id, data, tenant_id_override=tenant_id)
            # Emitir actualización en tiempo real para potrero actualizado
            try:
                from ...app import emit_update
                emit_update('potrero_updated', {
                    'id': potrero_id,
                    'data': potrero
                })
            except ImportError:
                print(PotreroController.WEBSOCKET_NO_DISPONIBLE)
            return jsonify({
                'data': potrero,
                'message': 'Potrero actualizado correctamente',
                'success': True
            }), 200
        except ValueError as e:
            return jsonify({
                'error': PotreroController.POTRERO_NO_ENCONTRADO,
                'message': str(e),
                'success': False
            }), 404
        except DatabaseError as e:
            return jsonify({
                'error': PotreroController.ERROR_BASE_DATOS,
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': PotreroController.ERROR_INTERNO_SERVIDOR,
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    @token_required
    @tenant_required
    @permission_required('eliminar_potreros')
    def delete(potrero_id: int) -> Tuple[Any, int]:
        """Delete potrero endpoint. Acepta tenant_id como query param para super admin."""
        try:
            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass
            
            PotreroService.delete(potrero_id, tenant_id_override=tenant_id)
            # Emitir actualización en tiempo real para potrero eliminado
            try:
                from ...app import emit_update
                emit_update('potrero_deleted', {
                    'id': potrero_id
                })
            except ImportError:
                print(PotreroController.WEBSOCKET_NO_DISPONIBLE)
            return jsonify({
                'message': 'Potrero eliminado correctamente',
                'success': True
            }), 200
        except ValueError as e:
            return jsonify({
                'error': PotreroController.POTRERO_NO_ENCONTRADO,
                'message': str(e),
                'success': False
            }), 404
        except DatabaseError as e:
            return jsonify({
                'error': PotreroController.ERROR_BASE_DATOS,
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': PotreroController.ERROR_INTERNO_SERVIDOR,
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    @token_required
    @tenant_required
    @permission_required('ver_potreros')
    def get_by_estado(estado: str) -> Tuple[Any, int]:
        """Get potreros by estado endpoint. Acepta tenant_id como query param para super admin."""
        try:
            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass
            
            potreros = PotreroService.get_by_estado(estado, tenant_id_override=tenant_id)
            return jsonify({'data': potreros, 'success': True}), 200
        except ValueError as e:
            return jsonify({
                'error': 'Estado inválido',
                'message': str(e),
                'success': False
            }), 400
        except DatabaseError as e:
            return jsonify({
                'error': PotreroController.ERROR_BASE_DATOS,
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': PotreroController.ERROR_INTERNO_SERVIDOR,
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    @token_required
    @tenant_required
    @permission_required('editar_potreros')
    def actualizar_ocupacion(potrero_id: int) -> Tuple[Any, int]:
        """Update potrero ocupacion endpoint."""
        try:
            data = request.get_json()
            if not isinstance(data.get('delta'), (int, float)):
                return jsonify({
                    'error': PotreroController.DATOS_INVALIDOS,
                    'message': 'El campo delta es requerido y debe ser un número',
                    'success': False
                }), 400

            delta = int(data['delta'])
            potrero = PotreroService.actualizar_ocupacion(potrero_id, delta)

            return jsonify({
                'data': potrero,
                'message': 'Ocupación actualizada correctamente',
                'success': True
            }), 200
        except ValueError as e:
            return jsonify({
                'error': 'Operación inválida',
                'message': str(e),
                'success': False
            }), 400
        except DatabaseError as e:
            return jsonify({
                'error': PotreroController.ERROR_BASE_DATOS,
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': PotreroController.ERROR_INTERNO_SERVIDOR,
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def get_tipos_pasto() -> Tuple[Any, int]:
        """Get tipos de pasto endpoint."""
        try:
            tipos_pasto = PotreroService.get_tipos_pasto()
            return jsonify({'data': tipos_pasto, 'success': True}), 200
        except DatabaseError as e:
            return jsonify({
                'error': PotreroController.ERROR_BASE_DATOS,
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': PotreroController.ERROR_INTERNO_SERVIDOR,
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    @token_required
    @tenant_required
    @permission_required('ver_potreros')
    def get_personas_usuario() -> Tuple[Any, int]:
        """
        Get personas usuario endpoint. 
        
        IMPORTANTE: Solo muestra usuarios del tenant actual. Super admins pueden usar 
        tenant_id como query param para filtrar por un tenant específico.
        Excluye usuarios con rol 'super_admin' para evitar mostrar super admins de otros tenants.
        """
        try:
            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass
            
            # Si no hay tenant_id en query params, obtenerlo del usuario actual
            if tenant_id is None:
                from src.utils.tenant import get_current_tenant_id
                tenant_id = get_current_tenant_id(allow_query_param=False, require_tenant=True)
            
            # CRÍTICO: Si aún no hay tenant_id, retornar error (seguridad multi-tenant)
            if tenant_id is None:
                return jsonify({
                    'error': 'Tenant requerido',
                    'message': 'No se pudo determinar el tenant. Este endpoint requiere un tenant válido.',
                    'success': False
                }), 400
            
            personas = PotreroService.get_personas_usuario(tenant_id_override=tenant_id)
            return jsonify({'data': personas, 'success': True}), 200
        except DatabaseError as e:
            return jsonify({
                'error': PotreroController.ERROR_BASE_DATOS,
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': PotreroController.ERROR_INTERNO_SERVIDOR,
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def get_estados_potrero() -> Tuple[Any, int]:
        """Get estados de potrero endpoint."""
        try:
            estados = PotreroService.get_estados_potrero()
            return jsonify({'data': estados, 'success': True}), 200
        except DatabaseError as e:
            return jsonify({
                'error': PotreroController.ERROR_BASE_DATOS,
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': PotreroController.ERROR_INTERNO_SERVIDOR,
                'message': str(e),
                'success': False
            }), 500

    # Método get_estados_ganado eliminado porque pertenece a animal_routes
