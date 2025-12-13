"\"\"\"Controller for notification endpoints.\"\"\""
from typing import Any, List, Optional, Tuple

from flask import jsonify, request

from ..services.notification_service import NotificationService
from ..utils.auth import token_required
from ..utils.tenant import tenant_required


class NotificationController:
    """Controller exposing upcoming alerts."""

    ERROR_INTERNO_SERVIDOR = 'Error interno del servidor'

    @staticmethod
    @token_required
    @tenant_required
    def get_proximas() -> Tuple[Any, int]:
        """Return combined alerts for cleaning and vaccination."""
        try:
            from flask import g
            from ..utils.tenant import get_current_tenant_id, _obtener_rol_nombre
            
            tenant_id = None
            tenant_param = request.args.get('tenant_id')
            
            # If tenant_id is provided in query params, use it (for superadmin filtering)
            if tenant_param:
                try:
                    tenant_id = int(tenant_param)
                except (ValueError, TypeError):
                    tenant_id = None
            
            # If no tenant_id in query params, get it from user context
            if tenant_id is None:
                # Check if user is superadmin
                if hasattr(g, 'current_user') and g.current_user:
                    rol_nombre = _obtener_rol_nombre(g.current_user)
                    if rol_nombre == 'super_admin':
                        # Superadmin without tenant: return empty list instead of error
                        tenant_id = get_current_tenant_id(require_tenant=False)
                        if tenant_id is None:
                            # Superadmin without tenant selection: return empty notifications
                            return jsonify({
                                'data': [], 
                                'success': True, 
                                'message': 'Selecciona un tenant para ver las notificaciones'
                            }), 200
                    else:
                        # Non-superadmin users must have a tenant_id from their context
                        tenant_id = get_current_tenant_id(require_tenant=True)
                        if tenant_id is None:
                            return jsonify({
                                'error': 'Tenant requerido',
                                'message': 'No se pudo determinar el tenant del usuario',
                                'success': False
                            }), 400
                else:
                    # Fallback: try to get tenant_id from context
                    tenant_id = get_current_tenant_id(require_tenant=True)
                    if tenant_id is None:
                        return jsonify({
                            'error': 'Tenant requerido',
                            'message': 'No se pudo determinar el tenant del contexto',
                            'success': False
                        }), 400

            eventos = NotificationController._obtener_eventos(tenant_id)
            return jsonify({'data': eventos, 'success': True}), 200
        except ValueError as ve:
            # Handle ValueError from service layer
            return jsonify({
                'error': 'Error de validación',
                'message': str(ve),
                'success': False
            }), 400
        except Exception as error:
            print(f"Error entregando notificaciones: {error}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': NotificationController.ERROR_INTERNO_SERVIDOR,
                'message': str(error),
                'success': False
            }), 500

    @staticmethod
    def _obtener_eventos(tenant_id_override: Optional[int]) -> List[dict]:
        """Helper to request notifications from service."""
        return NotificationService.obtener_notificaciones_proximas(tenant_id_override)

