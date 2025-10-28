# Rutas Ganado
from flask import Blueprint
from ..controllers.animal_controller import GanadoController

ganado_bp = Blueprint('ganado', __name__)

# Rutas CRUD básicas
ganado_bp.route('/', methods=['POST'])(GanadoController.crear_ganado)
ganado_bp.route('/', methods=['GET'])(GanadoController.obtener_todos_ganados)
ganado_bp.route('/<int:id>', methods=['GET'])(GanadoController.obtener_ganado)
ganado_bp.route('/<int:id>', methods=['PUT'])(GanadoController.actualizar_ganado)
ganado_bp.route('/<int:id>', methods=['DELETE'])(GanadoController.eliminar_ganado)

# Rutas adicionales
ganado_bp.route('/potrero/<int:potrero_id>', methods=['GET'])(GanadoController.obtener_ganados_por_potrero)
ganado_bp.route('/qr/<string:codigo_qr>', methods=['GET'])(GanadoController.buscar_por_codigo_qr)
