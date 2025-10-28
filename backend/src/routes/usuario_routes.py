# Rutas Usuario
from flask import Blueprint
from ..controllers.usuario_controller import UsuarioController
from ..utils.auth import token_required

usuario_bp = Blueprint('usuario', __name__)

# Rutas públicas
usuario_bp.route('/register', methods=['POST'])(UsuarioController.registrar_usuario)
usuario_bp.route('/login', methods=['POST'])(UsuarioController.login)

# Rutas protegidas
usuario_bp.route('/', methods=['GET'])(token_required(UsuarioController.obtener_todos_usuarios))
usuario_bp.route('/<int:id>', methods=['GET'])(token_required(UsuarioController.obtener_usuario))
usuario_bp.route('/<int:id>', methods=['PUT'])(token_required(UsuarioController.actualizar_usuario))
usuario_bp.route('/<int:id>/estado', methods=['PUT'])(token_required(UsuarioController.cambiar_estado_usuario))
usuario_bp.route('/<int:id>', methods=['DELETE'])(token_required(UsuarioController.eliminar_usuario))
