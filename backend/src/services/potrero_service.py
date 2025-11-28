"""Service layer for Potrero operations."""
from typing import List, Optional, Dict, Any
from mysql.connector import Error
from src.database.db import db, get_connection
from datetime import datetime
from src.utils.tenant import get_current_tenant_id

class PotreroService:
    """Service class for handling Potrero business logic."""
    NO_DEFINIDO = 'NO_DEFINIDO'

    @staticmethod
    def _obtener_tenant_id() -> Optional[int]:
        """Obtiene el tenant_id del contexto actual."""
        try:
            return get_current_tenant_id()
        except Exception:
            return None

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
                SELECT p.*
                FROM potrero p
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
                SELECT p.*
                FROM potrero p
                WHERE p.id = %s
            """
            params = (potrero_id,)
            
            if tenant_id is not None:
                sql += " AND p.tenant_id = %s"
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
        """Prepara los datos para la inserción del potrero."""
        from datetime import datetime
        nombre = data.get('nombre') or PotreroService._generar_nombre_potrero()
        fecha_ultimo_uso = datetime.now().date().isoformat()

        values = (
            data.get('id_tipo_pasto'),
            nombre,
            data.get('capacidad'),
            data.get('hectareas'),
            data.get('ocupacion', 0),
            fecha_ultimo_uso,
            data.get('responsable_persona_id'),
            data.get('proxima_limpieza'),
            data.get('area'),
            data.get('ultima_limpieza'),
            data.get('descripcion'),
            data.get('estado', 'disponible')
        )
        return values

    @staticmethod
    def _insertar_potrero_en_db(values: tuple) -> int:
        """Inserta el potrero en la base de datos y retorna el ID."""
        conn = get_connection()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)

            tenant_id = PotreroService._obtener_tenant_id()
            if tenant_id is None:
                raise ValueError("Tenant requerido para crear potrero")

            sql = """
                INSERT INTO potrero (
                    id_tipo_pasto, nombre, capacidad, hectareas, ocupacion,
                    fecha_ultimo_uso, responsable_persona_id, proxima_limpieza,
                    area, ultima_limpieza, descripcion, estado, tenant_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            values_list = list(values)
            values_list.append(tenant_id)
            values = tuple(values_list)

            cursor.execute(sql, values)
            potrero_id = cursor.lastrowid
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
                sql += " AND p.tenant_id = %s"
                params = (potrero_id, tenant_id)
            
            select_cursor.execute(sql, params)
            result = select_cursor.fetchone()

            if not result:
                raise ValueError(f"Potrero with id {potrero_id} not found after commit")

            print(f"Potrero encontrado después del commit: {result}")

            # Agregar información adicional
            PotreroService._agregar_tipo_pasto(result)
            PotreroService._agregar_responsable(result)

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
    def _agregar_responsable(potrero: Dict[str, Any]) -> None:
        """Agrega el nombre del responsable al potrero."""
        if potrero.get('responsable_persona_id'):
            try:
                with db.get_cursor() as resp_cursor:
                    resp_cursor.execute("""
                        SELECT CONCAT(primer_nombre, ' ', primer_apellido) as nombre_completo
                        FROM personas WHERE id = %s
                    """, (potrero['responsable_persona_id'],))
                    resp_result = resp_cursor.fetchone()
                    if resp_result:
                        potrero['responsable_nombre'] = resp_result['nombre_completo']
                    else:
                        potrero['responsable_nombre'] = f"Persona {potrero['responsable_persona_id']}"
            except Exception as e:
                print(f"Error obteniendo nombre del responsable: {e}")
                potrero['responsable_nombre'] = f"Persona {potrero['responsable_persona_id']}"
        else:
            potrero['responsable_nombre'] = 'No asignado'

    @staticmethod
    def create(data):
        """Create new potrero."""
        values = PotreroService._preparar_datos_insercion(data)
        potrero_id = PotreroService._insertar_potrero_en_db(values)
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
    def _procesar_campo_estado(value: Any) -> str:
        """Procesa el campo estado asegurando que sea válido."""
        valid_states = ['disponible', 'ocupado', 'limpieza']
        if not value or value not in valid_states:
            return 'disponible'
        return value

    @staticmethod
    def _preparar_campos_actualizacion(data: Dict[str, Any]) -> tuple:
        """Prepara los campos y valores para la actualización."""
        update_fields = []
        values = []

        for key, value in data.items():
            if key in ['id']:
                continue

            # Procesar campos especiales
            if key in ['proxima_limpieza', 'ultima_limpieza', 'fecha_ultimo_uso']:
                value = PotreroService._procesar_campo_fecha(key, value)
            elif key == 'estado':
                value = PotreroService._procesar_campo_estado(value)

            update_fields.append(f"{key} = %s")
            values.append(value)

        return update_fields, values

    @staticmethod
    def _ejecutar_actualizacion(potrero_id: int, update_fields: list, values: list) -> Dict[str, Any]:
        """Ejecuta la actualización en la base de datos."""
        values.append(potrero_id)

        print(f"Actualizando potrero {potrero_id} con campos: {update_fields}")
        print(f"Valores: {values[:-1]}")  # No mostrar el ID al final

        with db.get_cursor() as cursor:
            tenant_id = PotreroService._obtener_tenant_id()
            sql = f"""
                UPDATE potrero
                SET {', '.join(update_fields)}
                WHERE id = %s
            """
            params = tuple(values)
            if tenant_id is not None:
                sql += " AND tenant_id = %s"
                params = tuple(list(values) + [tenant_id])
            
            cursor.execute(sql, params)
            print(f"SQL ejecutado: {sql}")
            print(f"Filas afectadas: {cursor.rowcount}")

            # Obtener el registro actualizado
            sql = """
                SELECT p.*,
                       CONCAT(per.primer_nombre, ' ', COALESCE(per.segundo_nombre, ''), ' ', per.primer_apellido, ' ', COALESCE(per.segundo_apellido, '')) as responsable
                FROM potrero p
                LEFT JOIN personas per ON p.responsable_persona_id = per.id
                WHERE p.id = %s
            """
            params = (potrero_id,)
            if tenant_id is not None:
                sql += " AND p.tenant_id = %s"
                params = (potrero_id, tenant_id)
            
            cursor.execute(sql, params)

            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Potrero with id {potrero_id} not found after update")

            # Agregar información adicional
            PotreroService._agregar_tipo_pasto_actualizado(result)
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

        update_fields, values = PotreroService._preparar_campos_actualizacion(data)

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
                sql += " AND tenant_id = %s"
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
                sql += " AND p.tenant_id = %s"
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

        ocupacion_registrada = potrero.get('ocupacion')
        if ocupacion_registrada is None or ocupacion_registrada != ocupacion_real:
            PotreroService._actualizar_ocupacion_en_db(potrero_id, ocupacion_real)

        if capacidad and capacidad > 0 and (ocupacion_real + cantidad) > capacidad:
            nombre = potrero.get('nombre') or f"Potrero {potrero_id}"
            raise ValueError(
                f"El potrero {nombre} ha alcanzado su capacidad máxima ({capacidad})."
            )

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
    def get_personas_usuario() -> List[Dict[str, Any]]:
        """Get all personas with rol usuario."""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT p.id, p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido,
                           CONCAT(p.primer_nombre, ' ', p.primer_apellido) as nombre_completo
                    FROM personas p
                    JOIN usuarios u ON p.id = u.id_persona
                    WHERE u.estado = 'activo'
                    ORDER BY p.primer_apellido, p.primer_nombre
                """)
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
        """Get all estados de potrero desde el enum de la columna estado."""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COLUMN_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'potrero'
                    AND COLUMN_NAME = 'estado'
                """)
                result = cursor.fetchone()
                if result and result.get('COLUMN_TYPE'):
                    enum_str = PotreroService._convertir_enum_str_a_string(result['COLUMN_TYPE'])
                    return PotreroService._parsear_valores_enum(enum_str)
                return []
        except Exception as e:
            print(f"Error obteniendo estados del enum: {e}")
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
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE potrero
                SET ocupacion = %s
                WHERE id = %s
            """, (ocupacion, potrero_id))
        return PotreroService.get_by_id(potrero_id)
