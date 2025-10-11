# Rutas Animal
from flask import Blueprint
from ..controllers.animal_controller import AnimalController

animal_bp = Blueprint('animal', __name__)

# Rutas CRUD básicas
animal_bp.route('/', methods=['POST'])(AnimalController.crear_animal)
animal_bp.route('/', methods=['GET'])(AnimalController.obtener_todos_animales)
animal_bp.route('/<int:id>', methods=['GET'])(AnimalController.obtener_animal)
animal_bp.route('/<int:id>', methods=['PUT'])(AnimalController.actualizar_animal)
animal_bp.route('/<int:id>', methods=['DELETE'])(AnimalController.eliminar_animal)

# Rutas adicionales
animal_bp.route('/potrero/<int:potrero_id>', methods=['GET'])(AnimalController.obtener_animales_por_potrero)
animal_bp.route('/qr/<string:codigo_qr>', methods=['GET'])(AnimalController.buscar_por_codigo_qr)
