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
            tenant_id = None
            tenant_param = request.args.get('tenant_id')
            if tenant_param:
                try:
                    tenant_id = int(tenant_param)
                except (ValueError, TypeError):
                    tenant_id = None

            eventos = NotificationController._obtener_eventos(tenant_id)
            return jsonify({'data': eventos, 'success': True}), 200
        except Exception as error:
            print(f"Error entregando notificaciones: {error}")
            return jsonify({
                'error': NotificationController.ERROR_INTERNO_SERVIDOR,
                'message': str(error),
                'success': False
            }), 500

    @staticmethod
    def _obtener_eventos(tenant_id_override: Optional[int]) -> List[dict]:
        """Helper to request notifications from service."""
        return NotificationService.obtener_notificaciones_proximas(tenant_id_override)

