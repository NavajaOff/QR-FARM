from flask import Blueprint
from src.controllers.vacunacion_controller import VacunacionController

vacunacion_bp = Blueprint('vacunacion', __name__)

@vacunacion_bp.route('/', methods=['GET'])
def get_vacunaciones():
    """Obtener todas las vacunaciones"""
    return VacunacionController.obtener_todas_vacunaciones()

@vacunacion_bp.route('/<int:vacunacion_id>', methods=['GET'])
def get_vacunacion(vacunacion_id):
    """Obtener una vacunación por ID"""
    return VacunacionController.obtener_vacunacion_por_id(vacunacion_id)

@vacunacion_bp.route('/', methods=['POST'])
def create_vacunacion():
    """Crear una nueva vacunación"""
    return VacunacionController.crear_vacunacion()

@vacunacion_bp.route('/<int:vacunacion_id>', methods=['PUT'])
def update_vacunacion(vacunacion_id):
    """Actualizar una vacunación existente"""
    return VacunacionController.actualizar_vacunacion(vacunacion_id)

@vacunacion_bp.route('/<int:vacunacion_id>', methods=['DELETE'])
def delete_vacunacion(vacunacion_id):
    """Eliminar una vacunación"""
    return VacunacionController.eliminar_vacunacion(vacunacion_id)

@vacunacion_bp.route('/tipos-vacuna', methods=['GET'])
def get_tipos_vacuna():
    """Obtener lista de tipos de vacuna"""
    return VacunacionController.obtener_tipos_vacuna()