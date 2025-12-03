"""Controlador para gestión de tenants."""
from flask import request, jsonify
from src.services.tenant_service import TenantService
from src.utils.auth import token_required
from src.utils.tenant import super_admin_required, get_current_tenant_id, _es_super_admin_usuario


class TenantController:
    """Controlador para operaciones de tenant."""

    @staticmethod
    @token_required
    @super_admin_required
    def listar_tenants():
        """Listar todos los tenants."""
        try:
            activos_only = request.args.get('activos_only', 'true').lower() == 'true'
            tenants = TenantService.listar_tenants(activos_only=activos_only)
            
            return jsonify({
                'status': 'success',
                'data': [t.to_dict() for t in tenants]
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    @token_required
    @super_admin_required
    def crear_tenant():
        """Crear nuevo tenant."""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': 'Datos requeridos'
                }), 400
            
            nombre = data.get('nombre')
            
            if not nombre or not nombre.strip():
                return jsonify({
                    'status': 'error',
                    'message': 'El nombre del tenant es requerido'
                }), 400
            
            tenant = TenantService.crear_tenant(nombre.strip())
            
            if tenant:
                return jsonify({
                    'status': 'success',
                    'message': 'Tenant creado exitosamente',
                    'data': tenant.to_dict()
                }), 201
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Error al crear tenant'
                }), 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    @token_required
    @super_admin_required
    def obtener_tenant(tenant_id: int):
        """Obtener tenant por ID."""
        try:
            tenant = TenantService.obtener_tenant(tenant_id)
            
            if tenant:
                return jsonify({
                    'status': 'success',
                    'data': tenant.to_dict()
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Tenant no encontrado'
                }), 404
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    @token_required
    @super_admin_required
    def actualizar_tenant(tenant_id: int):
        """Actualizar tenant."""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': 'Datos requeridos'
                }), 400
            
            nombre = data.get('nombre')
            estado = data.get('estado')
            
            tenant = TenantService.actualizar_tenant(
                tenant_id,
                nombre=nombre,
                estado=estado
            )
            
            if tenant:
                return jsonify({
                    'status': 'success',
                    'message': 'Tenant actualizado exitosamente',
                    'data': tenant.to_dict()
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Error al actualizar tenant'
                }), 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    @token_required
    def obtener_tenant_actual():
        """
        Obtener el tenant actual del usuario.
        
        Para super admin: retorna null (no tiene tenant asignado).
        Para usuarios normales: retorna su tenant asignado.
        """
        try:
            is_super_admin = _es_super_admin_usuario()
            tenant_id = get_current_tenant_id(require_tenant=False)
            
            # Si es super admin y no tiene tenant seleccionado, retornar null
            if is_super_admin and tenant_id is None:
                return jsonify({
                    'success': True,
                    'tenant': None
                }), 200
            
            # Si tiene tenant_id, obtener los datos del tenant
            if tenant_id:
                tenant = TenantService.obtener_tenant(tenant_id)
                if tenant:
                    return jsonify({
                        'success': True,
                        'tenant': tenant.to_dict()
                    }), 200
            
            # Si no es super admin y no tiene tenant, retornar null también
            return jsonify({
                'success': True,
                'tenant': None
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

