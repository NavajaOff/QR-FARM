"""Service layer for Potrero operations."""
from typing import List, Optional, Dict, Any
from mysql.connector import Error
from src.database.db import db, get_connection
from datetime import datetime, timedelta
from src.utils.tenant import get_current_tenant_id
from dateutil.parser import parse

class PotreroService:
    """Service class for handling Potrero business logic."""
    NO_DEFINIDO = 'NO_DEFINIDO'
    SQL_AND_TENANT_ID = " AND p.tenant_id = %s"
    SQL_AND_TENANT_ID_GENERIC = " AND tenant_id = %s"
    TIMEZONE_UTC_SUFFIX = '+00:00'
    
    @staticmethod
    def _obtener_actividades_potrero(potrero_id: int, tenant_id: Optional[int] = None) -> Dict[str, Any]:
        """Obtiene las fechas del historial de un potrero."""
        actividades = {
            'fecha_ultimo_uso': None,
            'ultima_limpieza': None,
            'proxima_limpieza': None
        }

        try:
            with db.get_cursor() as cursor:
                # La tabla historial_potreros tiene las fechas directamente en columnas
                cursor.execute("""
                    SELECT fecha_ultima_limpieza, fecha_proxima_limpieza, fecha_ultimo_uso
                    FROM historial_potreros
                    WHERE id_potrero = %s
                    ORDER BY id DESC LIMIT 1
                """, (potrero_id,))
                result = cursor.fetchone()
                if result:
                    actividades['fecha_ultimo_uso'] = result['fecha_ultimo_uso']
                    actividades['ultima_limpieza'] = result['fecha_ultima_limpieza']
                    actividades['proxima_limpieza'] = result['fecha_proxima_limpieza']
        except Exception as e:
            print(f"Error obteniendo actividades del potrero {potrero_id}: {e}")

        return actividades
    
    @staticmethod
    def _registrar_actividad_potrero(
        potrero_id: int,
        tipo_evento: str,
        fecha_evento: datetime,
        observaciones: Optional[str] = None,
        tenant_id: Optional[int] = None
    ) -> None:
        """Actualiza las fechas en la tabla historial_potreros."""
        try:
            with db.get_cursor() as cursor:
                # Primero verificar si existe registro en historial_potreros
                cursor.execute("SELECT id FROM historial_potreros WHERE id_potrero = %s", (potrero_id,))
                existing = cursor.fetchone()

                if not existing:
                    # Crear registro si no existe
                    cursor.execute("INSERT INTO historial_potreros (id_potrero) VALUES (%s)", (potrero_id,))

                # Actualizar campo correspondiente según tipo_evento
                if tipo_evento == 'uso':
                    cursor.execute("""
                        UPDATE historial_potreros
                        SET fecha_ultimo_uso = %s
                        WHERE id_potrero = %s
                    """, (fecha_evento, potrero_id))
                elif tipo_evento == 'limpieza':
                    if observaciones == 'Programada':
                        cursor.execute("""
                            UPDATE historial_potreros
                            SET fecha_proxima_limpieza = %s
                            WHERE id_potrero = %s
                        """, (fecha_evento, potrero_id))
                    else:
                        cursor.execute("""
                            UPDATE historial_potreros
                            SET fecha_ultima_limpieza = %s
                            WHERE id_potrero = %s
                        """, (fecha_evento, potrero_id))
        except Exception as e:
            print(f"Error registrando actividad del potrero {potrero_id}: {e}")
            raise

    @staticmethod
    def _obtener_tenant_id() -> Optional[int]:
        """Obtiene el tenant_id del contexto actual."""
        try:
            return get_current_tenant_id()
        except Exception:
            return None

    @staticmethod
    def _obtener_id_estado_desde_nombre(estado_nombre: str) -> int:
        """Obtiene el id_estado_potrero desde el nombre del estado."""
        estado_map = {
            'disponible': 1,
            'ocupado': 2,
            'limpieza': 3
        }
        return estado_map.get(estado_nombre, 1)  # Default a 'disponible'

    @staticmethod
    def _procesar_potrero(potrero: Dict[str, Any]) -> None:
        """Procesa un potrero individual agregando ocupación y tipo de pasto."""
        try:
            ocupacion_real = PotreroService._obtener_ocupacion_real(potrero['id'])
            if potrero.get('ocupacion') != ocupacion_real:
                PotreroService._actualizar_ocupacion_en_db(potrero['id'], ocupacion_real)
            potrero['ocupacion'] = ocupacion_real
        except Exception as sync_error:
            print(f"Advertencia sincronizando ocupación del potrero {potrero.get('id')}: {sync_error}")

        if potrero.get('id_tipo_pasto'):
            try:
                tipos_pasto = PotreroService.get_tipos_pasto()
                tipo_encontrado = next((tp for tp in tipos_pasto if tp['id'] == potrero['id_tipo_pasto']), None)
                potrero['tipo_pasto_nombre'] = tipo_encontrado['tipo_pasto'] if tipo_encontrado else 'NO_DEFINIDO'
            except Exception:
                potrero['tipo_pasto_nombre'] = 'NO_DEFINIDO'
        else:
            potrero['tipo_pasto_nombre'] = 'NO_DEFINIDO'

    @staticmethod
    def _determinar_estado_por_ocupacion(capacidad: Optional[int], ocupacion: int) -> str:
        if capacidad and capacidad > 0 and ocupacion >= capacidad:
            return 'ocupado'
        return 'disponible'

    @staticmethod
    def _actualizar_estado_por_ocupacion(potrero_id: int, capacidad: Optional[int], ocupacion: int, tenant_id: Optional[int] = None) -> None:
        nuevo_estado_nombre = PotreroService._determinar_estado_por_ocupacion(capacidad, ocupacion)
        nuevo_estado_id = PotreroService._obtener_id_estado_desde_nombre(nuevo_estado_nombre)

        with db.get_cursor() as cursor:
            sql = "SELECT id_estado_potrero FROM potrero WHERE id = %s"
            params = (potrero_id,)
            if tenant_id is not None:
                sql += PotreroService.SQL_AND_TENANT_ID_GENERIC
                params = (potrero_id, tenant_id)
            cursor.execute(sql, params)
            resultado = cursor.fetchone()
            if resultado and resultado.get('id_estado_potrero') == nuevo_estado_id:
                return nuevo_estado_nombre

            update_sql = "UPDATE potrero SET id_estado_potrero = %s WHERE id = %s"
            update_params = (nuevo_estado_id, potrero_id)
            if tenant_id is not None:
                update_sql += PotreroService.SQL_AND_TENANT_ID_GENERIC
                update_params = (nuevo_estado_id, potrero_id, tenant_id)
            cursor.execute(update_sql, update_params)
        return nuevo_estado_nombre

    @staticmethod
    def get_all(tenant_id_override: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all potreros.
        
        Args:
            tenant_id_override: Si se proporciona, usa este tenant_id en lugar del del contexto
                               (útil para super admin filtrando por tenant específico)
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            if conn is None:
                print("Advertencia: Base de datos no disponible, retornando lista vacía")
                return []
            cursor = conn.cursor(dictionary=True)
            
            # Usar override si se proporciona, sino obtener del contexto
            tenant_id = tenant_id_override if tenant_id_override is not None else PotreroService._obtener_tenant_id()
            
            sql = """
                SELECT p.*, ep.nombre_estado as estado_nombre
                FROM potrero p
                LEFT JOIN estado_potrero ep ON p.id_estado_potrero = ep.id
            """
            params = ()
            if tenant_id is not None:
                sql += " WHERE p.tenant_id = %s"
                params = (tenant_id,)
            
            sql += " ORDER BY p.id DESC"
            
            cursor.execute(sql, params)
            potreros = cursor.fetchall()

            # Procesar cada potrero
            for potrero in potreros:
                PotreroService._procesar_potrero(potrero)
                # Agregar actividades desde historial_potreros
                actividades = PotreroService._obtener_actividades_potrero(potrero['id'], tenant_id)
                potrero.update(actividades)
                # Agregar información del responsable
                PotreroService._agregar_responsable(potrero, tenant_id)

            return potreros
        except Exception as e:
            print(f"Error en get_all potreros service: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def get_by_id(potrero_id: int, tenant_id_override: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get potrero by ID.
        
        Args:
            potrero_id: ID del potrero
            tenant_id_override: Si se proporciona, valida que el potrero pertenezca a este tenant
        """
        tenant_id = tenant_id_override if tenant_id_override is not None else PotreroService._obtener_tenant_id()
        
        with db.get_cursor() as cursor:
            sql = """
                SELECT p.*, ep.nombre_estado as estado_nombre
                FROM potrero p
                LEFT JOIN estado_potrero ep ON p.id_estado_potrero = ep.id
                WHERE p.id = %s
            """
            params = (potrero_id,)

            if tenant_id is not None:
                sql += PotreroService.SQL_AND_TENANT_ID
                params = (potrero_id, tenant_id)
            
            cursor.execute(sql, params)
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Potrero with id {potrero_id} not found")

            try:
                ocupacion_real = PotreroService._obtener_ocupacion_real(potrero_id)
                if result.get('ocupacion') != ocupacion_real:
                    PotreroService._actualizar_ocupacion_en_db(potrero_id, ocupacion_real)
                result['ocupacion'] = ocupacion_real
            except Exception as sync_error:
                print(f"Advertencia al sincronizar ocupación para potrero {potrero_id}: {sync_error}")

            # Agregar el nombre del tipo de pasto
            if result.get('id_tipo_pasto'):
                try:
                    tipos_pasto = PotreroService.get_tipos_pasto()
                    tipo_encontrado = next((tp for tp in tipos_pasto if tp['id'] == result['id_tipo_pasto']), None)
                    result['tipo_pasto_nombre'] = tipo_encontrado['tipo_pasto'] if tipo_encontrado else 'NO_DEFINIDO'
                except Exception:
                    result['tipo_pasto_nombre'] = 'NO_DEFINIDO'
            else:
                result['tipo_pasto_nombre'] = 'NO_DEFINIDO'
            
            # Agregar actividades desde historial_potrero
            actividades = PotreroService._obtener_actividades_potrero(potrero_id, tenant_id)
            result.update(actividades)
            # Agregar información del responsable
            PotreroService._agregar_responsable(result, tenant_id)

            return result

    @staticmethod
    def _generar_nombre_potrero() -> str:
        """Genera un nombre automático para el potrero."""
        with db.get_cursor() as cursor:
            tenant_id = PotreroService._obtener_tenant_id()
            sql = "SELECT COUNT(*) FROM potrero"
            params = ()
            if tenant_id is not None:
                sql += " WHERE tenant_id = %s"
                params = (tenant_id,)
            
            cursor.execute(sql, params)
            result = cursor.fetchone()
            numero = result['COUNT(*)'] + 1
            return f"Potrero {numero}"

    @staticmethod
    def _preparar_datos_insercion(data: Dict[str, Any]) -> tuple:
        """Prepara los datos para la inserción del potrero (sin campos de actividad)."""
        nombre = data.get('nombre') or PotreroService._generar_nombre_potrero()

        # Auto-calcular hectáreas si se proporciona área
        hectareas = data.get('hectareas')

        if hectareas is None:
            area_value = data.get('area')
            if area_value is not None:
                # Calcular hectáreas automáticamente si se proporciona área
                hectareas = float(area_value) / 10000
        # Nota: 'area' no se persiste en BD (eliminada según dump SQL), solo se usa para calcular hectáreas

        # Nota: fecha_ultimo_uso, ultima_limpieza y proxima_limpieza ahora se gestionan
        # en la tabla historial_potrero, no en potrero
        # Nota: 'area' no se persiste en BD (eliminada según dump SQL), solo se calcula para el modelo
        # Convertir estado a id_estado_potrero si viene como string
        estado = data.get('estado', 'disponible')
        id_estado_potrero = PotreroService._obtener_id_estado_desde_nombre(estado) if isinstance(estado, str) else estado

        values = (
            data.get('tenant_id'),
            data.get('id_tipo_pasto'),
            data.get('responsable_persona_id'),
            id_estado_potrero,
            nombre,
            data.get('capacidad'),
            data.get('ocupacion', 0),
            hectareas,
            data.get('area'),
            data.get('descripcion')
        )
        return values

    @staticmethod
    def _insertar_potrero_en_db(values: tuple) -> int:
        """Inserta el potrero en la base de datos y retorna el ID."""
        conn = get_connection()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)

            sql = """
                INSERT INTO potrero (
                    tenant_id, id_tipo_pasto, responsable_persona_id, id_estado_potrero,
                    nombre, capacidad, ocupacion, hectareas, area, descripcion
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            cursor.execute(sql, values)
            potrero_id = cursor.lastrowid

            # Crear registro en historial_potreros
            cursor.execute("INSERT INTO historial_potreros (id_potrero) VALUES (%s)", (potrero_id,))

            conn.commit()
            print(f"Potrero INSERT ejecutado con ID: {potrero_id}")
            return potrero_id

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error en create potrero: {e}")
            raise e
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn and conn is not None:
                try:
                    if conn.is_connected():
                        conn.close()
                except Exception:
                    pass

    @staticmethod
    def _obtener_potrero_completo(potrero_id: int) -> Dict[str, Any]:
        """Obtiene el potrero completo con información adicional."""
        with db.get_cursor() as select_cursor:
            tenant_id = PotreroService._obtener_tenant_id()
            sql = "SELECT p.* FROM potrero p WHERE p.id = %s"
            params = (potrero_id,)
            if tenant_id is not None:
                sql += PotreroService.SQL_AND_TENANT_ID
                params = (potrero_id, tenant_id)
            
            select_cursor.execute(sql, params)
            result = select_cursor.fetchone()

            if not result:
                raise ValueError(f"Potrero with id {potrero_id} not found after commit")

            print(f"Potrero encontrado después del commit: {result}")

            # Agregar información adicional
            PotreroService._agregar_tipo_pasto(result)
            PotreroService._agregar_responsable(result, tenant_id)
            
            # Agregar actividades desde historial_potrero
            actividades = PotreroService._obtener_actividades_potrero(potrero_id, tenant_id)
            result.update(actividades)

            return result

    @staticmethod
    def _agregar_tipo_pasto(potrero: Dict[str, Any]) -> None:
        """Agrega el nombre del tipo de pasto al potrero."""
        if potrero.get('id_tipo_pasto'):
            try:
                tipos_pasto = PotreroService.get_tipos_pasto()
                tipo_encontrado = next((tp for tp in tipos_pasto if tp['id'] == potrero['id_tipo_pasto']), None)
                potrero['tipo_pasto_nombre'] = tipo_encontrado['tipo_pasto'] if tipo_encontrado else 'NO_DEFINIDO'
            except Exception as e:
                print(f"Error obteniendo tipo de pasto: {e}")
                potrero['tipo_pasto_nombre'] = 'NO_DEFINIDO'
        else:
            potrero['tipo_pasto_nombre'] = 'NO_DEFINIDO'

    @staticmethod
    def _agregar_responsable(potrero: Dict[str, Any], tenant_id: Optional[int] = None) -> None:
        """Agrega el nombre del responsable al potrero respetando tenant_id."""
        if potrero.get('responsable_persona_id'):
            try:
                with db.get_cursor() as resp_cursor:
                    sql = """
                        SELECT CONCAT(
                            COALESCE(primer_nombre, ''), ' ',
                            COALESCE(segundo_nombre, ''), ' ',
                            COALESCE(primer_apellido, ''), ' ',
                            COALESCE(segundo_apellido, '')
                        ) as nombre_completo
                        FROM personas
                        WHERE id = %s
                    """
                    params = (potrero['responsable_persona_id'],)
                    
                    # Filtrar por tenant_id si está disponible
                    if tenant_id is not None:
                        sql += PotreroService.SQL_AND_TENANT_ID_GENERIC
                        params = (potrero['responsable_persona_id'], tenant_id)
                    
                    resp_cursor.execute(sql, params)
                    resp_result = resp_cursor.fetchone()
                    if resp_result and resp_result.get('nombre_completo'):
                        nombre_completo = resp_result['nombre_completo'].strip()
                        if nombre_completo:
                            potrero['responsable_nombre'] = nombre_completo
                        else:
                            potrero['responsable_nombre'] = f"Persona {potrero['responsable_persona_id']}"
                    else:
                        potrero['responsable_nombre'] = f"Persona {potrero['responsable_persona_id']}"
            except Exception as e:
                print(f"Error obteniendo nombre del responsable: {e}")
                potrero['responsable_nombre'] = f"Persona {potrero['responsable_persona_id']}"
        else:
            potrero['responsable_nombre'] = 'No asignado'

    @staticmethod
    def _registrar_actividad_si_existe(potrero_id: int, data: Dict[str, Any], campo: str, 
                                       tipo_evento: str, observaciones: Optional[str], 
                                       tenant_id: Optional[int]) -> None:
        """Registra una actividad del potrero si existe en los datos."""
        if not data.get(campo):
            return
        try:
            from datetime import datetime
            fecha = data.get(campo)
            if isinstance(fecha, str):
                fecha = datetime.fromisoformat(fecha.replace('Z', PotreroService.TIMEZONE_UTC_SUFFIX))
            PotreroService._registrar_actividad_potrero(
                potrero_id, tipo_evento, fecha, observaciones, tenant_id
            )
        except Exception as e:
            print(f"Error registrando {campo}: {e}")

    @staticmethod
    def _registrar_actividades_potrero_create(potrero_id: int, data: Dict[str, Any], 
                                               tenant_id: Optional[int]) -> None:
        """Registra todas las actividades del potrero al crearlo."""
        from datetime import datetime
        
        observaciones_none: Optional[str] = None
        observaciones_programada: Optional[str] = 'Programada'
        
        PotreroService._registrar_actividad_si_existe(
            potrero_id, data, 'fecha_ultimo_uso', 'uso', observaciones_none, tenant_id
        )
        PotreroService._registrar_actividad_si_existe(
            potrero_id, data, 'ultima_limpieza', 'limpieza', observaciones_none, tenant_id
        )
        PotreroService._registrar_actividad_si_existe(
            potrero_id, data, 'proxima_limpieza', 'limpieza', observaciones_programada, tenant_id
        )
        
        # Registrar fecha_ultimo_uso automáticamente (siempre, fecha de creación del potrero)
        try:
            PotreroService._registrar_actividad_potrero(
                potrero_id, 'uso', datetime.now(), observaciones_none, tenant_id
            )
        except Exception as e:
            print(f"Error registrando fecha_ultimo_uso automática: {e}")

        # Registrar proxima_limpieza automáticamente (3 meses desde ultima_limpieza si existe, sino desde fecha de creación)
        try:
            # Si se proporcionó ultima_limpieza, calcular proxima_limpieza basada en esa fecha
            if data.get('ultima_limpieza'):
                fecha_ultima_limpieza = data['ultima_limpieza']
                if isinstance(fecha_ultima_limpieza, str):
                    fecha_ultima_limpieza = parse(fecha_ultima_limpieza)
                fecha_proxima_limpieza = fecha_ultima_limpieza + timedelta(days=90)
            else:
                # Fallback: 3 meses desde ahora
                fecha_proxima_limpieza = datetime.now() + timedelta(days=90)

            PotreroService._registrar_actividad_potrero(
                potrero_id, 'limpieza', fecha_proxima_limpieza, observaciones_programada, tenant_id
            )
        except Exception as e:
            print(f"Error registrando proxima_limpieza automática: {e}")

    @staticmethod
    def create(data):
        """Create new potrero."""
        # Obtener tenant_id del contexto del usuario
        tenant_id = PotreroService._obtener_tenant_id()

        # Si no hay tenant_id del contexto (super_admin), intentar obtenerlo de los datos
        if tenant_id is None and 'tenant_id' in data:
            try:
                tenant_id = int(data['tenant_id'])
                print(f"[POTRERO_CREATE] Tenant ID obtenido de datos: {tenant_id}")
            except (ValueError, TypeError):
                print(f"[POTRERO_CREATE] Error convirtiendo tenant_id de datos: {data.get('tenant_id')}")

        # Si aún no hay tenant_id, intentar de query params
        if tenant_id is None:
            from flask import request
            tenant_param = request.args.get('tenant_id')
            if tenant_param:
                try:
                    tenant_id = int(tenant_param)
                    print(f"[POTRERO_CREATE] Tenant ID obtenido de query param: {tenant_id}")
                except (ValueError, TypeError):
                    print(f"[POTRERO_CREATE] Error convirtiendo tenant param: {tenant_param}")

        if tenant_id is None:
            from src.utils.tenant import _es_super_admin_usuario
            is_super_admin = _es_super_admin_usuario()
            print(f"[POTRERO_CREATE] Usuario es super_admin: {is_super_admin}")
            if is_super_admin:
                raise ValueError("Super admin debe proporcionar tenant_id para crear un potrero. Seleccione un tenant en el selector.")
            else:
                raise ValueError("Usuario debe tener un tenant asignado para crear potreros.")

        print(f"[POTRERO_CREATE] Usando tenant_id: {tenant_id}")

        # Agregar tenant_id a los datos para _preparar_datos_insercion
        data_with_tenant = {**data, 'tenant_id': tenant_id}

        values = PotreroService._preparar_datos_insercion(data_with_tenant)
        potrero_id = PotreroService._insertar_potrero_en_db(values)

        PotreroService._registrar_actividades_potrero_create(potrero_id, data, tenant_id)

        return PotreroService._obtener_potrero_completo(potrero_id)

    @staticmethod
    def _procesar_campo_fecha(key: str, value: Any) -> Any:
        """Procesa campos de fecha convirtiendo strings vacías a None y extrayendo YYYY-MM-DD."""
        if key in ['proxima_limpieza', 'ultima_limpieza', 'fecha_ultimo_uso']:
            if value == '':
                return None
            elif isinstance(value, str) and value and 'T' in value:
                return value.split('T')[0]
        return value
    
    @staticmethod
    def _procesar_actividad_actualizacion(potrero_id: int, actividades_data: Dict[str, Any], 
                                          campo: str, tipo_evento: str, observaciones: Optional[str], 
                                          tenant_id: Optional[int]) -> None:
        """Procesa una actividad específica durante la actualización."""
        if campo not in actividades_data or not actividades_data[campo]:
            return
        try:
            from datetime import datetime
            fecha = actividades_data[campo]
            if isinstance(fecha, str):
                fecha = datetime.fromisoformat(fecha.replace('Z', PotreroService.TIMEZONE_UTC_SUFFIX))
            PotreroService._registrar_actividad_potrero(
                potrero_id, tipo_evento, fecha, observaciones, tenant_id
            )
        except Exception as e:
            print(f"Error actualizando {campo}: {e}")

    @staticmethod
    def _actualizar_actividades_potrero(potrero_id: int, actividades_data: Dict[str, Any]) -> None:
        """Actualiza las actividades de un potrero."""
        tenant_id_raw = PotreroService._obtener_tenant_id()
        if tenant_id_raw is None:
            raise ValueError("Tenant requerido para actualizar actividades")
        
        tenant_id: Optional[int] = tenant_id_raw
        observaciones_none: Optional[str] = None
        observaciones_programada: Optional[str] = 'Programada'
        
        PotreroService._procesar_actividad_actualizacion(
            potrero_id, actividades_data, 'fecha_ultimo_uso', 'uso', observaciones_none, tenant_id
        )
        PotreroService._procesar_actividad_actualizacion(
            potrero_id, actividades_data, 'ultima_limpieza', 'limpieza', observaciones_none, tenant_id
        )
        PotreroService._procesar_actividad_actualizacion(
            potrero_id, actividades_data, 'proxima_limpieza', 'limpieza', observaciones_programada, tenant_id
        )

    @staticmethod
    def _procesar_campo_estado(value: Any) -> int:
        """Procesa el campo estado convirtiéndolo a id_estado_potrero."""
        if isinstance(value, int):
            # Si ya es un ID, verificar que sea válido
            if value in [1, 2, 3]:
                return value
            return 1  # Default a 'disponible'
        elif isinstance(value, str):
            return PotreroService._obtener_id_estado_desde_nombre(value)
        else:
            return 1  # Default a 'disponible'

    @staticmethod
    def _preparar_campos_actualizacion(data: Dict[str, Any]) -> tuple:
        """Prepara los campos y valores para la actualización."""
        update_fields = []
        values = []
        data_copy = data.copy()

        # Auto-calcular hectáreas si se proporciona área (solo para el modelo, no se persiste)
        if 'area' in data_copy and 'hectareas' not in data_copy:
            area_value = data_copy.get('area')
            if area_value is not None:
                # Calcular hectáreas automáticamente si se proporciona área (solo para cálculo)
                data_copy['hectareas'] = float(area_value) / 10000
        
        # Remover 'area' de data_copy ya que no se persiste en BD (según dump SQL)
        data_copy.pop('area', None)

        # Separar campos de actividad de campos de potrero
        actividades_data = {}
        for key in ['proxima_limpieza', 'ultima_limpieza', 'fecha_ultimo_uso']:
            if key in data_copy:
                actividades_data[key] = data_copy.pop(key)
        
        for key, value in data_copy.items():
            if key in ['id', 'area']:  # Excluir 'area' de actualización
                continue

            # Procesar campos especiales
            if key == 'estado':
                value = PotreroService._procesar_campo_estado(value)
                key = 'id_estado_potrero'  # Cambiar el nombre del campo

            update_fields.append(f"{key} = %s")
            values.append(value)
        
        return update_fields, values, actividades_data

    @staticmethod
    def _ejecutar_actualizacion(potrero_id: int, update_fields: list, values: list) -> Dict[str, Any]:
        """Ejecuta la actualización en la base de datos."""
        values.append(potrero_id)

        print(f"Actualizando potrero {potrero_id} con campos: {update_fields}")
        print(f"Valores: {values[:-1]}")  # No mostrar el ID al final

        tenant_id = PotreroService._obtener_tenant_id()
        with db.get_cursor() as cursor:
            sql = f"""
                UPDATE potrero
                SET {', '.join(update_fields)}
                WHERE id = %s
            """
            params = tuple(values)
            if tenant_id is not None:
                sql += PotreroService.SQL_AND_TENANT_ID_GENERIC
                params = tuple(list(values) + [tenant_id])
            
            cursor.execute(sql, params)
            print(f"SQL ejecutado: {sql}")
            print(f"Filas afectadas: {cursor.rowcount}")

            # Obtener el registro actualizado
            sql = """
                SELECT p.*,
                       ep.nombre_estado as estado_nombre,
                       CONCAT(per.primer_nombre, ' ', COALESCE(per.segundo_nombre, ''), ' ', per.primer_apellido, ' ', COALESCE(per.segundo_apellido, '')) as responsable
                FROM potrero p
                LEFT JOIN estado_potrero ep ON p.id_estado_potrero = ep.id
                LEFT JOIN personas per ON p.responsable_persona_id = per.id
                WHERE p.id = %s
            """
            params = (potrero_id,)
            if tenant_id is not None:
                sql += PotreroService.SQL_AND_TENANT_ID
                params = (potrero_id, tenant_id)
            
            cursor.execute(sql, params)
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Potrero with id {potrero_id} not found after update")

        PotreroService._agregar_tipo_pasto_actualizado(result)
        actividades = PotreroService._obtener_actividades_potrero(potrero_id, tenant_id)
        result.update(actividades)
        ocupacion_real = PotreroService._obtener_ocupacion_real(potrero_id)
        nuevo_estado_nombre = PotreroService._actualizar_estado_por_ocupacion(
            potrero_id, result.get('capacidad'), ocupacion_real, tenant_id
        )
        result['ocupacion'] = ocupacion_real
        result['estado_nombre'] = nuevo_estado_nombre
        print(f"Potrero actualizado exitosamente: {result}")
        return result

    @staticmethod
    def _agregar_tipo_pasto_actualizado(potrero: Dict[str, Any]) -> None:
        """Agrega el nombre del tipo de pasto al potrero actualizado."""
        if potrero.get('id_tipo_pasto'):
            try:
                tipos_pasto = PotreroService.get_tipos_pasto()
                tipo_encontrado = next((tp for tp in tipos_pasto if tp['id'] == potrero['id_tipo_pasto']), None)
                potrero['tipo_pasto'] = tipo_encontrado['tipo_pasto'] if tipo_encontrado else 'NO_DEFINIDO'
            except Exception as e:
                print(f"Error obteniendo tipo de pasto: {e}")
                potrero['tipo_pasto'] = 'NO_DEFINIDO'
        else:
            potrero['tipo_pasto'] = 'NO_DEFINIDO'

    @staticmethod
    def update(potrero_id: int, data: Dict[str, Any], tenant_id_override: Optional[int] = None) -> Dict[str, Any]:
        """
        Update existing potrero.
        
        Args:
            potrero_id: ID del potrero
            data: Datos a actualizar
            tenant_id_override: Si se proporciona, valida que el potrero pertenezca a este tenant
        """
        # Verificar que el potrero existe
        PotreroService.get_by_id(potrero_id, tenant_id_override)

        update_fields, values, actividades_data = PotreroService._preparar_campos_actualizacion(data)

        # Actualizar actividades si existen
        if actividades_data:
            PotreroService._actualizar_actividades_potrero(potrero_id, actividades_data)

        if not update_fields:
            return PotreroService.get_by_id(potrero_id)

        return PotreroService._ejecutar_actualizacion(potrero_id, update_fields, values)

    @staticmethod
    def delete(potrero_id: int, tenant_id_override: Optional[int] = None) -> bool:
        """
        Delete potrero by ID.
        
        Args:
            potrero_id: ID del potrero
            tenant_id_override: Si se proporciona, valida que el potrero pertenezca a este tenant
        """
        # First check if potrero exists
        PotreroService.get_by_id(potrero_id, tenant_id_override)

        tenant_id = tenant_id_override if tenant_id_override is not None else PotreroService._obtener_tenant_id()
        
        with db.get_cursor() as cursor:
            sql = """
                DELETE FROM potrero
                WHERE id = %s
            """
            params = (potrero_id,)
            
            if tenant_id is not None:
                sql += PotreroService.SQL_AND_TENANT_ID_GENERIC
                params = (potrero_id, tenant_id)
            
            cursor.execute(sql, params)
            return True

    @staticmethod
    def _obtener_potreros_por_estado(estado: str, tenant_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtiene los potreros básicos por estado."""
        with db.get_cursor() as cursor:
            sql = """
                SELECT p.*
                FROM potrero p
                WHERE p.estado = %s
            """
            params = (estado,)
            
            if tenant_id is not None:
                sql += PotreroService.SQL_AND_TENANT_ID
                params = (estado, tenant_id)
            
            sql += " ORDER BY p.id DESC"
            cursor.execute(sql, params)
            return cursor.fetchall()

    @staticmethod
    def _enriquecer_potreros_con_informacion(potreros: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enriquece la lista de potreros con información adicional."""
        tipos_pasto = PotreroService.get_tipos_pasto()  # Obtener una vez para todos

        for potrero in potreros:
            PotreroService._agregar_tipo_pasto_a_potrero(potrero, tipos_pasto)
            PotreroService._agregar_responsable_a_potrero(potrero)
            PotreroService._log_responsable_potrero(potrero)

        return potreros

    @staticmethod
    def _agregar_tipo_pasto_a_potrero(potrero: Dict[str, Any], tipos_pasto: List[Dict[str, Any]]) -> None:
        """Agrega el nombre del tipo de pasto a un potrero."""
        if potrero.get('id_tipo_pasto'):
            try:
                tipo_encontrado = next((tp for tp in tipos_pasto if tp['id'] == potrero['id_tipo_pasto']), None)
                potrero['tipo_pasto_nombre'] = tipo_encontrado['tipo_pasto'] if tipo_encontrado else 'NO_DEFINIDO'
            except Exception:
                potrero['tipo_pasto_nombre'] = 'NO_DEFINIDO'
        else:
            potrero['tipo_pasto_nombre'] = 'NO_DEFINIDO'

    @staticmethod
    def _agregar_responsable_a_potrero(potrero: Dict[str, Any]) -> None:
        """Agrega el nombre del responsable a un potrero."""
        if potrero.get('responsable_persona_id'):
            try:
                resp_conn = get_connection()
                resp_cursor = resp_conn.cursor(dictionary=True)
                resp_cursor.execute("""
                    SELECT CONCAT(primer_nombre, ' ', primer_apellido) as nombre_completo
                    FROM personas WHERE id = %s
                """, (potrero['responsable_persona_id'],))
                resp_result = resp_cursor.fetchone()
                if resp_result and resp_result['nombre_completo']:
                    potrero['responsable_nombre'] = resp_result['nombre_completo']
                else:
                    potrero['responsable_nombre'] = f"Persona {potrero['responsable_persona_id']}"
                resp_cursor.close()
                resp_conn.close()
            except Exception as e:
                print(f"Error obteniendo nombre del responsable para potrero {potrero['id']}: {e}")
                potrero['responsable_nombre'] = f"Persona {potrero['responsable_persona_id']}"
        else:
            potrero['responsable_nombre'] = 'No asignado'

    @staticmethod
    def _log_responsable_potrero(potrero: Dict[str, Any]) -> None:
        """Registra información del responsable del potrero."""
        print(f"Potrero {potrero['id']}: responsable_id={potrero.get('responsable_persona_id')}, nombre={potrero.get('responsable_nombre')}")

    @staticmethod
    def get_by_estado(estado: str, tenant_id_override: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get potreros by estado.
        
        Args:
            estado: Estado del potrero
            tenant_id_override: Si se proporciona, filtra por este tenant
        """
        tenant_id = tenant_id_override if tenant_id_override is not None else PotreroService._obtener_tenant_id()
        potreros = PotreroService._obtener_potreros_por_estado(estado, tenant_id)
        return PotreroService._enriquecer_potreros_con_informacion(potreros)

    @staticmethod
    def actualizar_ocupacion(potrero_id: int, delta: int) -> Dict[str, Any]:
        """Actualiza la ocupación registrada del potrero aplicando un delta sobre la ocupación real."""
        capacidad = None
        try:
            potrero = PotreroService.get_by_id(potrero_id)
            capacidad = potrero.get('capacidad')
        except Exception:
            potrero = None

        ocupacion_real = PotreroService._obtener_ocupacion_real(potrero_id)
        nueva_ocupacion = ocupacion_real + (delta or 0)
        if nueva_ocupacion < 0:
            nueva_ocupacion = 0

        if capacidad and capacidad > 0 and nueva_ocupacion > capacidad:
            nombre = potrero.get('nombre') if potrero else f"Potrero {potrero_id}"
            raise ValueError(f"La ocupación no puede superar la capacidad del potrero {nombre} ({capacidad}).")

        return PotreroService._actualizar_ocupacion_en_db(potrero_id, nueva_ocupacion)

    @staticmethod
    def sincronizar_ocupacion(potrero_id: int) -> Dict[str, Any]:
        """Fuerza que la columna ocupacion refleje el número real de animales asignados."""
        ocupacion_real = PotreroService._obtener_ocupacion_real(potrero_id)
        return PotreroService._actualizar_ocupacion_en_db(potrero_id, ocupacion_real)

    @staticmethod
    def verificar_capacidad_disponible(potrero_id: int, cantidad: int = 1) -> Dict[str, Any]:
        """Verifica que el potrero tenga capacidad disponible antes de alojar animales."""
        potrero = PotreroService.get_by_id(potrero_id)
        capacidad = potrero.get('capacidad')
        ocupacion_real = PotreroService._obtener_ocupacion_real(potrero_id)
        nombre = potrero.get('nombre') or f"Potrero {potrero_id}"

        ocupacion_registrada = potrero.get('ocupacion')
        if ocupacion_registrada is None or ocupacion_registrada != ocupacion_real:
            PotreroService._actualizar_ocupacion_en_db(potrero_id, ocupacion_real)

        if potrero.get('estado_nombre', '').lower() == 'ocupado':
            raise ValueError(f"El potrero {nombre} está marcado como ocupado y no admite más animales.")
        if capacidad and capacidad > 0 and (ocupacion_real + cantidad) > capacidad:
            nombre = potrero.get('nombre') or f"Potrero {potrero_id}"
            raise ValueError(
                f"El potrero {nombre} ha alcanzado su capacidad máxima ({capacidad})."
            )

        nueva_ocupacion = ocupacion_real + cantidad
        tenant_id = potrero.get('tenant_id') or PotreroService._obtener_tenant_id()
        PotreroService._actualizar_estado_por_ocupacion(potrero_id, capacidad, nueva_ocupacion, tenant_id)

        return potrero

    @staticmethod
    def get_tipos_pasto() -> List[Dict[str, Any]]:
        """Get all tipos de pasto."""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id, tipo_pasto FROM tipo_pasto
                    ORDER BY tipo_pasto
                """)
                results = cursor.fetchall()
                return results if results else []
        except Exception as e:
            print(f"Error obteniendo tipos de pasto: {e}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def crear_tipo_pasto(nombre: str) -> Dict[str, Any]:
        """Crea un nuevo tipo de pasto si no existe y retorna su registro."""
        nombre_limpio = nombre.strip()
        if not nombre_limpio:
            raise ValueError("El tipo de pasto no puede estar vacío.")

        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO tipo_pasto (tipo_pasto)
                VALUES (%s)
                ON DUPLICATE KEY UPDATE tipo_pasto = VALUES(tipo_pasto)
            """, (nombre_limpio,))
            tipo_id = cursor.lastrowid
            if not tipo_id:
                cursor.execute("SELECT id FROM tipo_pasto WHERE tipo_pasto = %s", (nombre_limpio,))
                encontrado = cursor.fetchone()
                tipo_id = encontrado['id'] if encontrado else None

            if tipo_id is None:
                raise ValueError("No fue posible crear el tipo de pasto.")

            cursor.execute("SELECT id, tipo_pasto FROM tipo_pasto WHERE id = %s", (tipo_id,))
            return cursor.fetchone()

    @staticmethod
    def actualizar_tipo_pasto(tipo_id: int, nombre: str) -> Dict[str, Any]:
        """Actualiza el nombre de un tipo de pasto existente."""
        nombre_limpio = nombre.strip()
        if not nombre_limpio:
            raise ValueError("El tipo de pasto no puede estar vacío.")

        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE tipo_pasto
                SET tipo_pasto = %s
                WHERE id = %s
            """, (nombre_limpio, tipo_id))
            cursor.execute("SELECT id, tipo_pasto FROM tipo_pasto WHERE id = %s", (tipo_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError("No se encontró el tipo de pasto especificado.")
            return result

    @staticmethod
    def get_personas_usuario(tenant_id_override: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all personas with rol usuario, filtrado por tenant.
        
        IMPORTANTE: 
        - tenant_id está en personas (p.tenant_id), NO en usuarios (u.tenant_id).
        - Excluye usuarios con rol 'super_admin' para evitar mostrar super admins de otros tenants.
        - Si tenant_id es None, retorna lista vacía (no mostrar todos los usuarios sin filtro).
        
        Args:
            tenant_id_override: Si se proporciona, filtra por este tenant
        """
        try:
            tenant_id = tenant_id_override if tenant_id_override is not None else PotreroService._obtener_tenant_id()
            
            # CRÍTICO: Si no hay tenant_id, no mostrar ningún usuario (seguridad multi-tenant)
            if tenant_id is None:
                print("[POTRERO_SERVICE] ADVERTENCIA: tenant_id es None, retornando lista vacía por seguridad")
                return []
            
            with db.get_cursor() as cursor:
                sql = """
                    SELECT p.id, p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido,
                           CONCAT(p.primer_nombre, ' ', p.primer_apellido) as nombre_completo
                    FROM personas p
                    JOIN usuarios u ON p.id = u.id_persona
                    JOIN roles r ON u.id_rol = r.id
                    WHERE u.estado = 'activo'
                      AND LOWER(TRIM(r.rol)) != 'super_admin'
                      AND p.tenant_id = %s
                """
                params = (tenant_id,)
                print(f"[POTRERO_SERVICE] Filtrando personas con p.tenant_id: {tenant_id} (excluyendo super_admin)")
                
                sql += " ORDER BY p.primer_apellido, p.primer_nombre"
                
                cursor.execute(sql, params)
                results = cursor.fetchall()

                # Transformar la estructura para que coincida con lo que espera el frontend
                personas_transformadas = []
                for result in results:
                    personas_transformadas.append({
                        'id': result['id'],
                        'primer_nombre': result['primer_nombre'],
                        'segundo_nombre': result['segundo_nombre'],
                        'primer_apellido': result['primer_apellido'],
                        'segundo_apellido': result['segundo_apellido'],
                        'nombre_completo': result['nombre_completo'],
                        'nombre_persona': result['nombre_completo']  # Campo adicional para compatibilidad
                    })

                return personas_transformadas
        except Exception as e:
            print(f"Error obteniendo personas usuario: {e}")
            return []

    @staticmethod
    def _convertir_enum_str_a_string(enum_value: Any) -> str:
        """Convierte valor enum a string manejando bytearray."""
        if isinstance(enum_value, (bytes, bytearray)):
            return enum_value.decode('utf-8')
        if isinstance(enum_value, str):
            return enum_value
        return str(enum_value)

    @staticmethod
    def _parsear_valores_enum(enum_str: str) -> List[Dict[str, Any]]:
        """Parsea string enum y retorna lista de diccionarios."""
        if '(' not in enum_str or ')' not in enum_str:
            return []
        values_str = enum_str.split('(')[1].split(')')[0]
        valores = [v.strip("'\"") for v in values_str.split(',')]
        return [{'id': i+1, 'estado': valor, 'nombre_estado': valor} for i, valor in enumerate(valores)]

    @staticmethod
    def get_estados_potrero() -> List[Dict[str, Any]]:
        """Get all estados de potrero desde la tabla estado_potrero."""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id, nombre_estado as estado, nombre_estado as nombre_estado
                    FROM estado_potrero
                    ORDER BY id
                """)
                results = cursor.fetchall()
                return results if results else []
        except Exception as e:
            print(f"Error obteniendo estados de potrero: {e}")
            import traceback
            traceback.print_exc()
            return []

    # Método get_estados_ganado eliminado porque pertenece a GanadoService

    @staticmethod
    def _obtener_ocupacion_real(potrero_id: int) -> int:
        """Cuenta cuántos animales están actualmente asociados al potrero."""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) AS total
                    FROM ganado
                    WHERE id_potrero = %s
                """, (potrero_id,))
                row = cursor.fetchone()
                if row and row.get('total') is not None:
                    return int(row['total'])
        except Exception as error:
            print(f"Error obteniendo ocupación real del potrero {potrero_id}: {error}")
        return 0

    @staticmethod
    def _actualizar_ocupacion_en_db(potrero_id: int, ocupacion: int) -> Dict[str, Any]:
        """Actualiza la columna ocupacion en la tabla potrero y devuelve el registro actualizado."""
        ocupacion = max(0, int(ocupacion))
        tenant_id = None
        capacidad = None
        with db.get_cursor() as cursor:
            cursor.execute("SELECT capacidad, tenant_id FROM potrero WHERE id = %s", (potrero_id,))
            row = cursor.fetchone()
            if row:
                capacidad = row.get('capacidad')
                tenant_id = row.get('tenant_id')
            cursor.execute("""
                UPDATE potrero
                SET ocupacion = %s
                WHERE id = %s
            """, (ocupacion, potrero_id))
        if capacidad is not None:
            PotreroService._actualizar_estado_por_ocupacion(potrero_id, capacidad, ocupacion, tenant_id)
        return PotreroService.get_by_id(potrero_id)
