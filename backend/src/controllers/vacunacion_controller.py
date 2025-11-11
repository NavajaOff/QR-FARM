# Controlador Vacunacion
from typing import Tuple, Any
from flask import request, jsonify
from src.services.vacunacion_service import VacunacionService
from src.models.vacunacion import Vacunacion

class VacunacionController:
    # Error message constants
    ERROR_INTERNO_SERVIDOR = 'Error interno del servidor'
    VACUNACION_NO_ENCONTRADA = 'Vacunación no encontrada'
    @staticmethod
    def obtener_todas_vacunaciones() -> Tuple[Any, int]:
        """Obtener todas las vacunaciones"""
        try:
            print("Obteniendo lista de vacunaciones desde la base de datos...")

            vacunaciones = VacunacionService.obtener_todas_vacunaciones()

            # Convertir a formato compatible con el frontend
            vacunaciones_data = []
            for vacunacion in vacunaciones:
                data = vacunacion.to_dict()
                # Formatear para el frontend
                vacunaciones_data.append({
                    "id": data["id"],
                    "idAnimal": data["id_animal"],
                    "nombre": data["nombre_animal"] or f"Animal {data['id_animal']}",
                    "tipoVacuna": data["nombre_tipo_vacuna"] or f"Tipo {data['id_tipo_vacuna']}",
                    "fechaAplicacion": data["fecha_aplicacion"],
                    "proximaDosis": data["proxima_dosis"],
                    "responsable": data["nombre_responsable"] or f"Responsable {data['responsable']}",
                    "estado": data["estado"]
                })

            print(f"Enviando {len(vacunaciones_data)} vacunaciones desde la base de datos")

            return jsonify({
                "status": "success",
                "message": "Vacunaciones obtenidas exitosamente",
                "data": vacunaciones_data
            }), 200

        except Exception as e:
            print(f"Error obteniendo vacunaciones: {str(e)}")
            return jsonify({
                "status": "error",
                "message": VacunacionController.ERROR_INTERNO_SERVIDOR
            }), 500

    @staticmethod
    def obtener_vacunacion_por_id(vacunacion_id: int) -> Tuple[Any, int]:
        """Obtener una vacunación por ID"""
        try:
            vacunacion = VacunacionService.obtener_vacunacion_por_id(vacunacion_id)

            if not vacunacion:
                return jsonify({
                    "status": "error",
                    "message": VacunacionController.VACUNACION_NO_ENCONTRADA
                }), 404

            return jsonify({
                "status": "success",
                "message": "Vacunación obtenida exitosamente",
                "data": vacunacion.to_dict()
            }), 200

        except Exception as e:
            print(f"Error obteniendo vacunación: {str(e)}")
            return jsonify({
                "status": "error",
                "message": VacunacionController.ERROR_INTERNO_SERVIDOR
            }), 500

    @staticmethod
    def crear_vacunacion() -> Tuple[Any, int]:
        """Crear una nueva vacunación"""
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    "status": "error",
                    "message": "Se requieren datos JSON"
                }), 400

            # Validar campos requeridos
            required_fields = ['id_animal', 'id_tipo_vacuna', 'responsable']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "status": "error",
                        "message": f"El campo {field} es requerido"
                    }), 400

            # Crear objeto Vacunacion
            vacunacion = Vacunacion.from_dict(data)

            # Crear en la base de datos
            success = VacunacionService.crear_vacunacion(vacunacion)

            if success:
                return jsonify({
                    "status": "success",
                    "message": "Vacunación creada exitosamente"
                }), 201
            else:
                return jsonify({
                    "status": "error",
                    "message": "Error al crear la vacunación"
                }), 500

        except Exception as e:
            print(f"Error creando vacunación: {str(e)}")
            return jsonify({
                "status": "error",
                "message": VacunacionController.ERROR_INTERNO_SERVIDOR
            }), 500

    @staticmethod
    def actualizar_vacunacion(vacunacion_id: int) -> Tuple[Any, int]:
        """Actualizar una vacunación existente"""
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    "status": "error",
                    "message": "Se requieren datos JSON"
                }), 400

            # Verificar que la vacunación existe
            existing_vacunacion = VacunacionService.obtener_vacunacion_por_id(vacunacion_id)
            if not existing_vacunacion:
                return jsonify({
                    "status": "error",
                    "message": VacunacionController.VACUNACION_NO_ENCONTRADA
                }), 404

            # Crear objeto con datos actualizados
            updated_data = existing_vacunacion.to_dict()
            updated_data.update(data)
            vacunacion = Vacunacion.from_dict(updated_data)

            # Actualizar en la base de datos
            success = VacunacionService.actualizar_vacunacion(vacunacion_id, vacunacion)

            if success:
                return jsonify({
                    "status": "success",
                    "message": "Vacunación actualizada exitosamente"
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "Error al actualizar la vacunación"
                }), 500

        except Exception as e:
            print(f"Error actualizando vacunación: {str(e)}")
            return jsonify({
                "status": "error",
                "message": VacunacionController.ERROR_INTERNO_SERVIDOR
            }), 500

    @staticmethod
    def eliminar_vacunacion(vacunacion_id: int) -> Tuple[Any, int]:
        """Eliminar una vacunación"""
        try:
            print(f"Controller: Intentando eliminar vacunación con ID: {vacunacion_id}")
            # Verificar que la vacunación existe
            existing_vacunacion = VacunacionService.obtener_vacunacion_por_id(vacunacion_id)
            print(f"Controller: Vacunación encontrada: {existing_vacunacion is not None}")
            if not existing_vacunacion:
                print(f"Controller: Vacunación con ID {vacunacion_id} no encontrada")
                return jsonify({
                    "status": "error",
                    "message": VacunacionController.VACUNACION_NO_ENCONTRADA
                }), 404

            # Eliminar de la base de datos
            print(f"Controller: Llamando a VacunacionService.eliminar_vacunacion con ID: {vacunacion_id}")
            success = VacunacionService.eliminar_vacunacion(vacunacion_id)
            print(f"Controller: Resultado de eliminar_vacunacion: {success}")

            if success:
                print(f"Controller: Vacunación {vacunacion_id} eliminada exitosamente")
                return jsonify({
                    "status": "success",
                    "message": "Vacunación eliminada exitosamente"
                }), 200
            else:
                print(f"Controller: Error al eliminar vacunación {vacunacion_id}")
                return jsonify({
                    "status": "error",
                    "message": "Error al eliminar la vacunación"
                }), 500

        except Exception as e:
            print(f"Controller: Error eliminando vacunación: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "status": "error",
                "message": VacunacionController.ERROR_INTERNO_SERVIDOR
            }), 500

    @staticmethod
    def obtener_tipos_vacuna() -> Tuple[Any, int]:
        """Obtener lista de tipos de vacuna"""
        try:
            tipos_vacuna = VacunacionService.obtener_tipos_vacuna()

            return jsonify({
                "status": "success",
                "message": "Tipos de vacuna obtenidos exitosamente",
                "data": tipos_vacuna
            }), 200

        except Exception as e:
            print(f"Error obteniendo tipos de vacuna: {str(e)}")
            return jsonify({
                "status": "error",
                "message": VacunacionController.ERROR_INTERNO_SERVIDOR
            }), 500