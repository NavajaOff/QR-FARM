"""Routes for Potrero endpoints."""
from flask import Blueprint
from src.controllers.potrero_controller import PotreroController

# Create blueprint
potrero_bp = Blueprint('potrero', __name__, url_prefix='/api/potreros')

# Register routes
potrero_bp.route('/', methods=['GET'])(PotreroController.get_all)
potrero_bp.route('/<int:potrero_id>', methods=['GET'])(PotreroController.get_by_id)
potrero_bp.route('/', methods=['POST'])(PotreroController.create)
potrero_bp.route('/<int:potrero_id>', methods=['PUT'])(PotreroController.update)
potrero_bp.route('/<int:potrero_id>', methods=['DELETE'])(PotreroController.delete)
potrero_bp.route('/estado/<estado>', methods=['GET'])(PotreroController.get_by_estado)
potrero_bp.route('/<int:potrero_id>/ocupacion', methods=['PATCH'])(PotreroController.actualizar_ocupacion)
