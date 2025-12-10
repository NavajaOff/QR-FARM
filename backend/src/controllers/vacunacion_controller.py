# Controlador Vacunacion
from typing import Tuple, Any, Dict
from flask import request, jsonify
from src.services.vacunacion_service import VacunacionService
from src.models.vacunacion import Vacunacion
from src.utils.auth import token_required
from src.utils.tenant import tenant_required
from src.utils.permissions import permission_required

class VacunacionController:
    # Error message constants
    ERROR_INTERNO_SERVIDOR = 'Error interno del servidor'
    VACUNACION_NO_ENCONTRADA = 'Vacunación no encontrada'
    @staticmethod
    @token_required
    @tenant_required
    @permission_required('ver_vacunaciones')
    def obtener_todas_vacunaciones() -> Tuple[Any, int]:
        """Obtener todas las vacunaciones. Acepta tenant_id como query param para super admin."""
        try:
            print("Obteniendo lista de vacunaciones desde la base de datos...")

            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass

            vacunaciones = VacunacionService.obtener_todas_vacunaciones(tenant_id_override=tenant_id)

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
    @token_required
    @tenant_required
    @permission_required('ver_vacunaciones')
    def obtener_vacunacion_por_id(vacunacion_id: int) -> Tuple[Any, int]:
        """Obtener una vacunación por ID. Acepta tenant_id como query param para super admin."""
        try:
            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass
            
            vacunacion = VacunacionService.obtener_vacunacion_por_id(vacunacion_id, tenant_id_override=tenant_id)

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
    @token_required
    @tenant_required
    @permission_required('crear_vacunaciones')
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
    @token_required
    @tenant_required
    @permission_required('editar_vacunaciones')
    def actualizar_vacunacion(vacunacion_id: int) -> Tuple[Any, int]:
        """Actualizar una vacunación existente. Acepta tenant_id como query param para super admin."""
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    "status": "error",
                    "message": "Se requieren datos JSON"
                }), 400

            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass

            # Verificar que la vacunación existe
            existing_vacunacion = VacunacionService.obtener_vacunacion_por_id(vacunacion_id, tenant_id_override=tenant_id)
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
            success = VacunacionService.actualizar_vacunacion(vacunacion_id, vacunacion, tenant_id_override=tenant_id)

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
    @token_required
    @tenant_required
    @permission_required('eliminar_vacunaciones')
    def eliminar_vacunacion(vacunacion_id: int) -> Tuple[Any, int]:
        """Eliminar una vacunación. Acepta tenant_id como query param para super admin."""
        try:
            print(f"Controller: Intentando eliminar vacunación con ID: {vacunacion_id}")
            
            # Obtener tenant_id desde query params si existe (para super admin)
            tenant_id = None
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    tenant_id = int(tenant_id_param)
                except (ValueError, TypeError):
                    pass
            
            # Verificar que la vacunación existe
            existing_vacunacion = VacunacionService.obtener_vacunacion_por_id(vacunacion_id, tenant_id_override=tenant_id)
            print(f"Controller: Vacunación encontrada: {existing_vacunacion is not None}")
            if not existing_vacunacion:
                print(f"Controller: Vacunación con ID {vacunacion_id} no encontrada")
                return jsonify({
                    "status": "error",
                    "message": VacunacionController.VACUNACION_NO_ENCONTRADA
                }), 404

            # Eliminar de la base de datos
            print(f"Controller: Llamando a VacunacionService.eliminar_vacunacion con ID: {vacunacion_id}")
            success = VacunacionService.eliminar_vacunacion(vacunacion_id, tenant_id_override=tenant_id)
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

    @staticmethod
    @token_required
    @tenant_required
    @permission_required('crear_vacunaciones')
    def crear_tipo_vacuna() -> Tuple[Any, int]:
        """Crear un nuevo tipo de vacuna."""
        try:
            data = request.get_json()
            nombre = (data or {}).get('nombre')
            if not nombre or not isinstance(nombre, str):
                return jsonify({
                    'status': 'error',
                    'message': 'El nombre del tipo de vacuna es obligatorio.'
                }), 400

            tipo = VacunacionService.crear_tipo_vacuna(nombre)
            return jsonify({
                'status': 'success',
                'message': 'Tipo de vacuna creado.',
                'data': tipo
            }), 201
        except ValueError as ve:
            return jsonify({
                'status': 'error',
                'message': str(ve)
            }), 400
        except Exception as e:
            print(f"Error creando tipo de vacuna: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': VacunacionController.ERROR_INTERNO_SERVIDOR
            }), 500

    @staticmethod
    @token_required
    @tenant_required
    @permission_required('editar_vacunaciones')
    def actualizar_tipo_vacuna(tipo_id: int) -> Tuple[Any, int]:
        """Actualizar un tipo de vacuna."""
        try:
            data = request.get_json()
            nombre = (data or {}).get('nombre')
            if not nombre or not isinstance(nombre, str):
                return jsonify({
                    'status': 'error',
                    'message': 'El nombre del tipo de vacuna es obligatorio.'
                }), 400

            tipo = VacunacionService.actualizar_tipo_vacuna(tipo_id, nombre)
            return jsonify({
                'status': 'success',
                'message': 'Tipo de vacuna actualizado.',
                'data': tipo
            }), 200
        except ValueError as ve:
            return jsonify({
                'status': 'error',
                'message': str(ve)
            }), 400
        except Exception as e:
            print(f"Error actualizando tipo de vacuna: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': VacunacionController.ERROR_INTERNO_SERVIDOR
            }), 500
