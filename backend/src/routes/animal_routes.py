from flask import Blueprint, jsonify
from src.services.potrero_service import PotreroService

animal_bp = Blueprint('animal', __name__, url_prefix='/api/animales')

@animal_bp.route('/estados', methods=['GET'])
def get_estados_animales():
    """Obtener los estados posibles del ganado."""
    estados = PotreroService.get_estados_ganado()
    return jsonify({'data': estados, 'success': True}), 200

@animal_bp.route('/', methods=['GET'])
def get_animales():
    """Ruta temporal para evitar error 404."""
    return jsonify({'data': [], 'success': True}), 200
