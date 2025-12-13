# Rutas Usuario
from flask import Blueprint
from ..controllers.usuario_controller import UsuarioController
from ..utils.auth import token_required

try:
    from ...app import emit_update
except ImportError:
    def emit_update(event, _data=None):
        print(f"WebSocket no disponible, evento omitido: {event}")

# Constantes para rutas
USER_ID_ROUTE = '/<int:id>'

usuario_bp = Blueprint('usuario', __name__)

# Rutas públicas
# Nota: /register puede recibir token opcional - el controlador verifica si hay usuario autenticado
# para permitir asignar tenant_id (solo super admin)
usuario_bp.route('/register', methods=['POST'])(UsuarioController.registrar_usuario)
usuario_bp.route('/login', methods=['POST'])(UsuarioController.login)
usuario_bp.route('/recovery/request', methods=['POST'])(UsuarioController.request_password_recovery)
usuario_bp.route('/recovery/confirm', methods=['POST'])(UsuarioController.confirm_password_recovery)
usuario_bp.route('/recovery/requests', methods=['GET'])(token_required(UsuarioController.list_recovery_requests))
usuario_bp.route('/recovery/<int:recovery_id>/approve', methods=['POST'])(token_required(UsuarioController.approve_recovery_request))
usuario_bp.route('/recovery/<int:recovery_id>/reject', methods=['POST'])(token_required(UsuarioController.reject_recovery_request))

# Ruta adicional para compatibilidad
usuario_bp.route('/', methods=['POST'])(UsuarioController.login)

# Rutas protegidas
usuario_bp.route('/', methods=['GET'])(token_required(UsuarioController.obtener_todos_usuarios))
usuario_bp.route(USER_ID_ROUTE, methods=['GET'])(token_required(UsuarioController.obtener_usuario))
usuario_bp.route(USER_ID_ROUTE, methods=['PUT'])(token_required(UsuarioController.actualizar_usuario))
usuario_bp.route('/<int:id>/estado', methods=['PUT'])(token_required(UsuarioController.cambiar_estado_usuario))
usuario_bp.route(USER_ID_ROUTE, methods=['DELETE'])(token_required(UsuarioController.eliminar_usuario))
usuario_bp.route('/profile', methods=['GET'])(token_required(UsuarioController.obtener_perfil_actual))
usuario_bp.route('/profile', methods=['PUT'])(token_required(UsuarioController.actualizar_perfil_actual))
