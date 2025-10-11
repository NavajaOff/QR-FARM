# Controlador Animal
from datetime import datetime
from flask import jsonify, request
from ..models.animal import Animal
from ..services.animal_service import AnimalService

class AnimalController:
    @staticmethod
    def crear_animal():
        try:
            data = request.get_json()
            
            # Convertir fechas de string a objeto date si están presentes
            if 'fecha_nacimiento' in data:
                data['fecha_nacimiento'] = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
            
            animal = Animal.from_dict(data)
            nuevo_animal = AnimalService.crear_animal(animal)
            
            if nuevo_animal:
                return jsonify({
                    'status': 'success',
                    'message': 'Animal creado exitosamente',
                    'data': nuevo_animal.to_dict()
                }), 201
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Error al crear el animal'
                }), 400
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def obtener_animal(id):
        try:
            animal = AnimalService.obtener_animal(id)
            
            if animal:
                return jsonify({
                    'status': 'success',
                    'data': animal.to_dict()
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Animal no encontrado'
                }), 404
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def obtener_todos_animales():
        try:
            animales = AnimalService.obtener_todos_animales()
            return jsonify({
                'status': 'success',
                'data': [animal.to_dict() for animal in animales]
            }), 200
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def actualizar_animal(id):
        try:
            data = request.get_json()
            
            # Obtener el animal existente
            animal_existente = AnimalService.obtener_animal(id)
            if not animal_existente:
                return jsonify({
                    'status': 'error',
                    'message': 'Animal no encontrado'
                }), 404
            
            # Actualizar los campos del animal con los nuevos datos
            for key, value in data.items():
                if key == 'fecha_nacimiento' and value:
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                setattr(animal_existente, key, value)
            
            # Intentar actualizar en la base de datos
            if AnimalService.actualizar_animal(id, animal_existente):
                return jsonify({
                    'status': 'success',
                    'message': 'Animal actualizado exitosamente',
                    'data': animal_existente.to_dict()
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Error al actualizar el animal'
                }), 400
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def eliminar_animal(id):
        try:
            if AnimalService.eliminar_animal(id):
                return jsonify({
                    'status': 'success',
                    'message': 'Animal eliminado exitosamente'
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Animal no encontrado o error al eliminar'
                }), 404
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def obtener_animales_por_potrero(potrero_id):
        try:
            animales = AnimalService.buscar_por_potrero(potrero_id)
            return jsonify({
                'status': 'success',
                'data': [animal.to_dict() for animal in animales]
            }), 200
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def buscar_por_codigo_qr(codigo_qr):
        try:
            animal = AnimalService.buscar_por_codigo_qr(codigo_qr)
            
            if animal:
                return jsonify({
                    'status': 'success',
                    'data': animal.to_dict()
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Animal no encontrado'
                }), 404
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
