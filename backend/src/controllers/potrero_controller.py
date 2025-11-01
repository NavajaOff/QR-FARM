"""Controller for Potrero endpoints."""
from typing import Tuple, Any
from flask import jsonify, request
from src.database.db import DatabaseError
from src.services.potrero_service import PotreroService

class PotreroController:
    """Controller handling Potrero HTTP requests."""

    @staticmethod
    def get_all() -> Tuple[Any, int]:
        """Get all potreros endpoint."""
        try:
            potreros = PotreroService.get_all()
            return jsonify({'data': potreros, 'success': True}), 200
        except DatabaseError as e:
            return jsonify({
                'error': 'Error de base de datos',
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Error interno del servidor',
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def get_by_id(potrero_id: int) -> Tuple[Any, int]:
        """Get potrero by ID endpoint."""
        try:
            potrero = PotreroService.get_by_id(potrero_id)
            return jsonify({'data': potrero, 'success': True}), 200
        except ValueError as e:
            return jsonify({
                'error': 'Potrero no encontrado',
                'message': str(e),
                'success': False
            }), 404
        except DatabaseError as e:
            return jsonify({
                'error': 'Error de base de datos',
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Error interno del servidor',
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def create() -> Tuple[Any, int]:
        """Create potrero endpoint."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': 'Datos inválidos',
                    'message': 'No se proporcionaron datos',
                    'success': False
                }), 400

            print(f"Datos recibidos en controller: {data}")

            # El nombre puede ser null, el servicio lo generará automáticamente

            potrero = PotreroService.create(data)
            print(f"Potrero creado exitosamente: {potrero}")
            return jsonify({
                'data': potrero,
                'message': 'Potrero creado correctamente',
                'success': True
            }), 201
        except ValueError as e:
            print(f"Error de validación: {str(e)}")
            return jsonify({
                'error': 'Datos inválidos',
                'message': str(e),
                'success': False
            }), 400
        except DatabaseError as e:
            print(f"Error de base de datos: {str(e)}")
            return jsonify({
                'error': 'Error de base de datos',
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            print(f"Error interno del servidor: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': 'Error interno del servidor',
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def update(potrero_id: int) -> Tuple[Any, int]:
        """Update potrero endpoint."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': 'Datos inválidos',
                    'message': 'No se proporcionaron datos para actualizar',
                    'success': False
                }), 400
            
            potrero = PotreroService.update(potrero_id, data)
            return jsonify({
                'data': potrero,
                'message': 'Potrero actualizado correctamente',
                'success': True
            }), 200
        except ValueError as e:
            return jsonify({
                'error': 'Potrero no encontrado',
                'message': str(e),
                'success': False
            }), 404
        except DatabaseError as e:
            return jsonify({
                'error': 'Error de base de datos',
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Error interno del servidor',
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def delete(potrero_id: int) -> Tuple[Any, int]:
        """Delete potrero endpoint."""
        try:
            PotreroService.delete(potrero_id)
            return jsonify({
                'message': 'Potrero eliminado correctamente',
                'success': True
            }), 200
        except ValueError as e:
            return jsonify({
                'error': 'Potrero no encontrado',
                'message': str(e),
                'success': False
            }), 404
        except DatabaseError as e:
            return jsonify({
                'error': 'Error de base de datos',
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Error interno del servidor',
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def get_by_estado(estado: str) -> Tuple[Any, int]:
        """Get potreros by estado endpoint."""
        try:
            potreros = PotreroService.get_by_estado(estado)
            return jsonify({'data': potreros, 'success': True}), 200
        except ValueError as e:
            return jsonify({
                'error': 'Estado inválido',
                'message': str(e),
                'success': False
            }), 400
        except DatabaseError as e:
            return jsonify({
                'error': 'Error de base de datos',
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Error interno del servidor',
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def actualizar_ocupacion(potrero_id: int) -> Tuple[Any, int]:
        """Update potrero ocupacion endpoint."""
        try:
            data = request.get_json()
            if not isinstance(data.get('delta'), (int, float)):
                return jsonify({
                    'error': 'Datos inválidos',
                    'message': 'El campo delta es requerido y debe ser un número',
                    'success': False
                }), 400

            delta = int(data['delta'])
            potrero = PotreroService.actualizar_ocupacion(potrero_id, delta)

            return jsonify({
                'data': potrero,
                'message': 'Ocupación actualizada correctamente',
                'success': True
            }), 200
        except ValueError as e:
            return jsonify({
                'error': 'Operación inválida',
                'message': str(e),
                'success': False
            }), 400
        except DatabaseError as e:
            return jsonify({
                'error': 'Error de base de datos',
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Error interno del servidor',
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def get_tipos_pasto() -> Tuple[Any, int]:
        """Get tipos de pasto endpoint."""
        try:
            tipos_pasto = PotreroService.get_tipos_pasto()
            return jsonify({'data': tipos_pasto, 'success': True}), 200
        except DatabaseError as e:
            return jsonify({
                'error': 'Error de base de datos',
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Error interno del servidor',
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def get_personas_usuario() -> Tuple[Any, int]:
        """Get personas usuario endpoint."""
        try:
            personas = PotreroService.get_personas_usuario()
            return jsonify({'data': personas, 'success': True}), 200
        except DatabaseError as e:
            return jsonify({
                'error': 'Error de base de datos',
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Error interno del servidor',
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def get_estados_potrero() -> Tuple[Any, int]:
        """Get estados de potrero endpoint."""
        try:
            estados = PotreroService.get_estados_potrero()
            return jsonify({'data': estados, 'success': True}), 200
        except DatabaseError as e:
            return jsonify({
                'error': 'Error de base de datos',
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Error interno del servidor',
                'message': str(e),
                'success': False
            }), 500

    @staticmethod
    def get_estados_ganado() -> Tuple[Any, int]:
        """Get estados de ganado endpoint."""
        try:
            estados = PotreroService.get_estados_ganado()
            return jsonify({'data': estados, 'success': True}), 200
        except DatabaseError as e:
            return jsonify({
                'error': 'Error de base de datos',
                'message': str(e),
                'success': False
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Error interno del servidor',
                'message': str(e),
                'success': False
            }), 500
