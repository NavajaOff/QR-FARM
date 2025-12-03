"""Routes for Potrero endpoints."""
from flask import Blueprint, jsonify
from src.controllers.potrero_controller import PotreroController

try:
    from ...app import emit_update
except ImportError:
    def emit_update(event):
        print(f"WebSocket no disponible, evento omitido: {event}")

POTRERO_ID_ROUTE = '/<int:potrero_id>'
# Create blueprint (sin url_prefix, se agrega al registrar en app.py)
potrero_bp = Blueprint('potrero', __name__)

# Register routes
potrero_bp.route('/', methods=['GET'])(PotreroController.get_all)
potrero_bp.route(POTRERO_ID_ROUTE, methods=['GET'])(PotreroController.get_by_id)
potrero_bp.route('/', methods=['POST'])(PotreroController.create)
potrero_bp.route(POTRERO_ID_ROUTE, methods=['PUT'])(PotreroController.update)
potrero_bp.route(POTRERO_ID_ROUTE, methods=['DELETE'])(PotreroController.delete)
potrero_bp.route('/estado/<estado>', methods=['GET'])(PotreroController.get_by_estado)
potrero_bp.route('/<int:potrero_id>/ocupacion', methods=['PATCH'])(PotreroController.actualizar_ocupacion)
potrero_bp.route('/tipos-pasto', methods=['GET'])(PotreroController.get_tipos_pasto)
potrero_bp.route('/personas-usuario', methods=['GET'])(PotreroController.get_personas_usuario)
potrero_bp.route('/estados', methods=['GET'])(PotreroController.get_estados_potrero)
