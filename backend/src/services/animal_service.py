# Servicio Ganado
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pathlib import Path
from ..database.db import get_connection
from ..models.animal import Ganado, EstadoGanado
from .potrero_service import PotreroService
from ..utils.tenant import get_current_tenant_id

BASE_DIR = Path(__file__).resolve().parents[2]
QR_STORAGE_DIR = BASE_DIR / "qr"

# SQL constants
SQL_AND_TENANT_ID = " AND tenant_id = %s"
SQL_WHERE_TENANT_ID = " WHERE tenant_id = %s"
SQL_AND_G_TENANT_ID = " AND g.tenant_id = %s"
SQL_WHERE_G_TENANT_ID = " WHERE g.tenant_id = %s"

class GanadoService:
    @staticmethod
    def _obtener_tenant_id_desde_g() -> Optional[int]:
        """Intenta obtener tenant_id desde el contexto Flask g."""
        try:
            from flask import g
            if hasattr(g, 'tenant_id') and g.tenant_id is not None:
                return g.tenant_id
            if hasattr(g, 'current_user') and g.current_user:
                if hasattr(g.current_user, 'tenant_id') and g.current_user.tenant_id is not None:
                    return g.current_user.tenant_id
        except Exception:
            pass
        return None

    @staticmethod
    def _obtener_tenant_id() -> Optional[int]:
        """Obtiene el tenant_id del contexto actual."""
        tenant_id = GanadoService._obtener_tenant_id_desde_g()
        if tenant_id is not None:
            return tenant_id
        
        try:
            tenant_id = get_current_tenant_id(require_tenant=True)
            if tenant_id is not None:
                return tenant_id
        except Exception:
            pass
        
        return GanadoService._obtener_tenant_id_desde_g()

    @staticmethod
    def _agregar_filtro_tenant(sql: str, tenant_id: Optional[int], 
                               usar_where: bool = False) -> tuple:
        """Agrega filtro de tenant a una query SQL."""
        if tenant_id is None:
            return sql, ()
        
        if usar_where:
            sql += SQL_WHERE_G_TENANT_ID
        else:
            sql += SQL_AND_G_TENANT_ID
        
        return sql, (tenant_id,)

    @staticmethod
    def _to_iso_string(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            return value
        return None

    @staticmethod
    def _calcular_edad(valor: Any) -> Optional[int]:
        referencia = None
        if isinstance(valor, datetime):
            referencia = valor.date()
        elif isinstance(valor, date):
            referencia = valor
        elif isinstance(valor, str):
            try:
                referencia = datetime.fromisoformat(valor.replace('Z', '')).date()
            except ValueError:
                try:
                    referencia = datetime.strptime(valor.split('T')[0], '%Y-%m-%d').date()
                except ValueError:
                    return None
        else:
            return None

        hoy = date.today()
        edad = hoy.year - referencia.year - ((hoy.month, hoy.day) < (referencia.month, referencia.day))
        return edad if edad >= 0 else None

    @staticmethod
    def _empty_propietario() -> Dict[str, Optional[str]]:
        return {
            "nombre": None,
            "telefono": None,
            "rol": None
        }

    @staticmethod
    def _empty_potrero() -> Dict[str, Optional[Any]]:
        return {
            "nombre": None,
            "tipo_pasto": None,
            "ultima_limpieza": None,
            "fecha_ultimo_uso": None,
            "proxima_limpieza": None,
            "capacidad": None,
            "estado": None
        }

    @staticmethod
    def _to_nullable_int(value: Any) -> Optional[int]:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_nullable_float(value: Any) -> Optional[float]:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _fetch_vacunas(connection, animal_id: int, tenant_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtiene las vacunas asociadas a un animal."""
        query = """
            SELECT
                v.id,
                v.fecha_aplicacion,
                v.proxima_dosis,
                v.estado,
                v.responsable,
                tv.nombre_vacuna,
                CONCAT_WS(' ', resp.primer_nombre, resp.segundo_nombre, resp.primer_apellido, resp.segundo_apellido) AS responsable_nombre
            FROM vacunacion v
            LEFT JOIN tipo_vacuna tv ON tv.id = v.id_tipo_vacuna
            LEFT JOIN personas resp ON resp.id = v.responsable
            WHERE v.id_animal = %s
        """
        params = (animal_id,)
        
        # Filtrar por tenant_id si se proporciona (seguridad multi-tenant)
        # Incluir vacunas que tengan el tenant_id correcto O que sean NULL pero el animal pertenezca al tenant
        if tenant_id is not None:
            query += """
                AND (
                    v.tenant_id = %s OR 
                    (v.tenant_id IS NULL AND EXISTS (
                        SELECT 1 FROM ganado g WHERE g.id = v.id_animal AND g.tenant_id = %s
                    ))
                )
            """
            params = (animal_id, tenant_id, tenant_id)
        
        query += " ORDER BY v.fecha_aplicacion DESC, v.id DESC"

        cursor = connection.cursor(dictionary=True)
        rows: List[Dict[str, Any]] = []
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            print(f"[GANADO_SERVICE] _fetch_vacunas: Encontradas {len(rows)} vacunas para animal {animal_id} (tenant_id: {tenant_id})")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[GANADO_SERVICE] Error obteniendo vacunas para animal {animal_id}: {exc}")
            # Si falla por falta de columna tenant_id, intentar sin filtro de tenant
            try:
                query_simple = """
                    SELECT
                        v.id,
                        v.fecha_aplicacion,
                        v.proxima_dosis,
                        v.estado,
                        v.responsable,
                        tv.nombre_vacuna,
                        CONCAT_WS(' ', resp.primer_nombre, resp.segundo_nombre, resp.primer_apellido, resp.segundo_apellido) AS responsable_nombre
                    FROM vacunacion v
                    LEFT JOIN tipo_vacuna tv ON tv.id = v.id_tipo_vacuna
                    LEFT JOIN personas resp ON resp.id = v.responsable
                    WHERE v.id_animal = %s
                    ORDER BY v.fecha_aplicacion DESC, v.id DESC
                """
                cursor.execute(query_simple, (animal_id,))
                rows = cursor.fetchall()
                print(f"[GANADO_SERVICE] _fetch_vacunas (fallback): Encontradas {len(rows)} vacunas para animal {animal_id}")
            except Exception as exc2:
                print(f"[GANADO_SERVICE] Error en fallback de vacunas: {exc2}")
        finally:
            cursor.close()

        vacunas: List[Dict[str, Any]] = []
        for row in rows:
            vacunas.append({
                "id": row.get("id"),
                "nombre": row.get("nombre_vacuna"),
                "nombre_vacuna": row.get("nombre_vacuna"),  # Incluir ambos campos para compatibilidad
                "fecha_aplicacion": GanadoService._to_iso_string(row.get("fecha_aplicacion")),
                "proxima_dosis": GanadoService._to_iso_string(row.get("proxima_dosis")),
                "estado": row.get("estado"),
                "responsable": row.get("responsable_nombre") or row.get("responsable"),
            })
        print(f"[GANADO_SERVICE] _fetch_vacunas: Retornando {len(vacunas)} vacunas procesadas")
        return vacunas

    @staticmethod
    def _validar_y_obtener_tenant_id(tenant_id_override: Optional[int]) -> int:
        """Valida y obtiene el tenant_id para crear ganado."""
        tenant_id = tenant_id_override
        if tenant_id is None:
            tenant_id = GanadoService._obtener_tenant_id()
        if tenant_id is None:
            raise ValueError("Tenant requerido para crear ganado")
        return tenant_id

    @staticmethod
    def _preparar_valores_insercion(ganado: Ganado, tenant_id: int) -> tuple:
        """Prepara los valores para la inserción en la base de datos."""
        fecha_nac = ganado.fecha_nacimiento
        if fecha_nac and hasattr(fecha_nac, 'isoformat'):
            fecha_nac = fecha_nac.isoformat()
        elif not isinstance(fecha_nac, str):
            fecha_nac = None

        estado_id = GanadoService._obtener_estado_id_desde_db(ganado.estado)
        if estado_id is None:
            estado_id = GanadoService._mapear_estado_string_a_id(ganado.estado)
        
        sexo_value = ganado.sexo.value if hasattr(ganado.sexo, 'value') else str(ganado.sexo)
        
        return (
            ganado.nombre, ganado.raza,
            fecha_nac, sexo_value,
            ganado.peso, estado_id,
            ganado.id_potrero, ganado.id_persona, tenant_id
        )

    @staticmethod
    def _insertar_ganado_en_db(cursor, ganado: Ganado, values: tuple) -> int:
        """Inserta el ganado en la base de datos y retorna el ID generado."""
        sql = """
            INSERT INTO ganado (
                nombre, raza, fecha_nacimiento,
                sexo, peso, id_estado, id_potrero, id_persona, tenant_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(sql, values)
        return cursor.lastrowid

    @staticmethod
    def _sincronizar_potrero_despues_crear(ganado: Ganado) -> None:
        """Sincroniza la ocupación del potrero después de crear ganado."""
        if ganado.id_potrero:
            try:
                PotreroService.sincronizar_ocupacion(ganado.id_potrero)
            except Exception:
                pass

    @staticmethod
    def _cerrar_conexion_ganado(cursor, conn) -> None:
        """Cierra cursor y conexión de forma segura."""
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                if conn.is_connected():
                    conn.close()
            except Exception:
                pass

    @staticmethod
    def crear_ganado(ganado: Ganado, tenant_id_override: Optional[int] = None) -> Optional[Ganado]:
        """Crea un nuevo ganado en la base de datos."""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            if ganado.id_potrero:
                PotreroService.verificar_capacidad_disponible(ganado.id_potrero)

            tenant_id = GanadoService._validar_y_obtener_tenant_id(tenant_id_override)
            values = GanadoService._preparar_valores_insercion(ganado, tenant_id)
            ganado.id = GanadoService._insertar_ganado_en_db(cursor, ganado, values)
            conn.commit()

            GanadoService._sincronizar_potrero_despues_crear(ganado)
            return ganado

        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise e
        finally:
            GanadoService._cerrar_conexion_ganado(cursor, conn)


    @staticmethod
    def obtener_ganado(id: int, tenant_id_override: Optional[int] = None) -> Optional[Ganado]:
        """
        Obtener ganado por ID.
        
        Args:
            id: ID del ganado
            tenant_id_override: Si se proporciona, valida que el ganado pertenezca a este tenant
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            tenant_id = tenant_id_override if tenant_id_override is not None else GanadoService._obtener_tenant_id()
            
            sql = """
                SELECT g.*,
                       eg.tipo_estado as estado_tipo,
                       p.nombre as potrero_nombre,
                       CONCAT(per.primer_nombre, ' ', COALESCE(per.segundo_nombre, ''), ' ', per.primer_apellido, ' ', COALESCE(per.segundo_apellido, '')) as persona_nombre,
                       per.primer_nombre as persona_primer_nombre,
                       per.primer_apellido as persona_primer_apellido,
                       qr.codigo_qr
                FROM ganado g
                LEFT JOIN estado_ganado eg ON g.id_estado = eg.id
                LEFT JOIN potrero p ON g.id_potrero = p.id
                LEFT JOIN personas per ON g.id_persona = per.id
                LEFT JOIN qr ON g.id = qr.id_ganado
                WHERE g.id = %s
            """
            params = (id,)
            
            if tenant_id is not None:
                sql += SQL_AND_G_TENANT_ID
                params = (id, tenant_id)
            
            cursor.execute(sql, params)

            result = cursor.fetchone()
            if result:
                ganado = Ganado.from_dict(result)
                return ganado
            return None

        except Exception as e:
            print("Error al obtener ganado " + str(id) + ": " + str(e))
            return None
        finally:
            if 'conn' in locals() and conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    @staticmethod
    def obtener_todos_ganados(incluir_bajas: bool = False, tenant_id_override: Optional[int] = None) -> List[Ganado]:
        """
        Obtiene todos los animales, incluyendo dados de baja si se solicita.
        
        Args:
            incluir_bajas: Si incluir animales dados de baja
            tenant_id_override: Si se proporciona, filtra por este tenant
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            tenant_id = tenant_id_override if tenant_id_override is not None else GanadoService._obtener_tenant_id()

            # Consulta: todos los animales
            sql = """
                SELECT g.*,
                       eg.tipo_estado as estado_tipo,
                       p.nombre as potrero_nombre,
                       CONCAT(per.primer_nombre, ' ', COALESCE(per.segundo_nombre, ''), ' ', per.primer_apellido, ' ', COALESCE(per.segundo_apellido, '')) as persona_nombre,
                       per.primer_nombre as persona_primer_nombre,
                       per.primer_apellido as persona_primer_apellido,
                       qr.codigo_qr
                FROM ganado g
                LEFT JOIN estado_ganado eg ON g.id_estado = eg.id
                LEFT JOIN potrero p ON g.id_potrero = p.id
                LEFT JOIN personas per ON g.id_persona = per.id
                LEFT JOIN qr ON g.id = qr.id_ganado
            """
            
            params = ()
            if tenant_id is not None:
                sql += " WHERE g.tenant_id = %s"
                params = (tenant_id,)
            
            sql += " ORDER BY g.id DESC LIMIT 50"

            cursor.execute(sql, params)
            results = cursor.fetchall()

            # Crear objetos Ganado desde resultados de BD
            ganados = []
            for result in results:
                result_copy = result.copy()
                result_copy['estado_tipo'] = result.get('estado_tipo')
                ganado = Ganado.from_dict(result_copy)
                ganados.append(ganado)

            return ganados

        except Exception as e:
            print("Error al obtener animales: " + str(e))
            return []
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()

    @staticmethod
    def _mapear_estado_a_id(estado: EstadoGanado) -> int:
        """Mapea un estado del enum EstadoGanado a su ID en la base de datos."""
        estado_mapping = {
            EstadoGanado.SALUDABLE: 1,
            EstadoGanado.REVISION: 2,
            EstadoGanado.ENFERMO: 3
        }
        return estado_mapping.get(estado, 1)  # Default: saludable

    @staticmethod
    def _mapear_estado_string_a_id(estado: str) -> int:
        """Mapea un estado string a su ID en la base de datos."""
        estado_mapping = {
            'saludable': 1,
            'revision': 2,
            'enfermo': 3
        }
        return estado_mapping.get(estado.lower(), 1)  # Default: saludable

    @staticmethod
    def _obtener_estado_id_desde_db(estado_value: str) -> Optional[int]:
        """Obtiene el ID del estado desde la base de datos."""
        try:
            conn_temp = get_connection()
            cursor_temp = conn_temp.cursor()
            cursor_temp.execute("SELECT id FROM estado_ganado WHERE tipo_estado = %s", (estado_value,))
            result = cursor_temp.fetchone()
            cursor_temp.close()
            conn_temp.close()
            return result[0] if result else None
        except Exception:
            return None

    @staticmethod
    def _convertir_fecha_nacimiento(fecha_nac):
        """Convierte la fecha de nacimiento al formato adecuado para la BD."""
        if fecha_nac is None:
            return None
        if hasattr(fecha_nac, 'isoformat'):
            # Si es un objeto date o datetime, extraer solo la fecha
            if hasattr(fecha_nac, 'date'):
                return fecha_nac.date().isoformat()
            return fecha_nac.isoformat().split('T')[0] if 'T' in fecha_nac.isoformat() else fecha_nac.isoformat()
        elif isinstance(fecha_nac, str):
            # Si tiene formato ISO con tiempo, extraer solo la fecha
            if 'T' in fecha_nac:
                return fecha_nac.split('T')[0]
            # Si tiene espacio (formato datetime de MySQL), extraer solo la fecha
            if ' ' in fecha_nac:
                return fecha_nac.split(' ')[0]
            return fecha_nac
        else:
            return None

    @staticmethod
    def _eliminar_archivo_qr(codigo_qr: str) -> None:
        if not codigo_qr:
            return
        try:
            qr_path = QR_STORAGE_DIR / (codigo_qr + ".png")
            if qr_path.exists():
                qr_path.unlink()
        except OSError:
            pass

    @staticmethod
    def _obtener_potrero_anterior(id: int) -> Optional[int]:
        try:
            registro_actual = GanadoService.obtener_ganado(id)
            return registro_actual.id_potrero if registro_actual else None
        except Exception:
            return None

    @staticmethod
    def _verificar_cambio_potrero(nuevo_potrero_id: Optional[int], potrero_anterior_id: Optional[int]) -> None:
        if nuevo_potrero_id and nuevo_potrero_id != potrero_anterior_id:
            PotreroService.verificar_capacidad_disponible(nuevo_potrero_id)

    @staticmethod
    def _sincronizar_potreros_despues_actualizacion(actualizado: bool, nuevo_potrero_id: Optional[int], potrero_anterior_id: Optional[int]) -> None:
        if not actualizado or nuevo_potrero_id == potrero_anterior_id:
            return
        if potrero_anterior_id:
            try:
                PotreroService.sincronizar_ocupacion(potrero_anterior_id)
            except Exception:
                pass
        if nuevo_potrero_id:
            try:
                PotreroService.sincronizar_ocupacion(nuevo_potrero_id)
            except Exception:
                pass

    @staticmethod
    def _validar_animal_existe(cursor, animal_id: int, tenant_id: Optional[int]) -> Optional[Dict[str, Any]]:
        """Valida que el animal existe y pertenece al tenant."""
        check_sql = "SELECT id, tenant_id, nombre, raza, fecha_nacimiento, sexo, peso, id_estado, id_potrero, id_persona FROM ganado WHERE id = %s"
        cursor.execute(check_sql, (animal_id,))
        check_result = cursor.fetchone()
        if not check_result:
            return None
        if tenant_id is not None and check_result.get('tenant_id') != tenant_id:
            return None
        return check_result

    @staticmethod
    def _normalizar_fecha_para_comparacion(bd_fecha: Any) -> Optional[str]:
        """Normaliza la fecha de la BD para comparación."""
        if isinstance(bd_fecha, datetime):
            return bd_fecha.strftime('%Y-%m-%d')
        if isinstance(bd_fecha, date):
            return bd_fecha.isoformat()
        if bd_fecha:
            return str(bd_fecha).split()[0]
        return None

    @staticmethod
    def _normalizar_valor_entero(valor: Any) -> Optional[int]:
        """Normaliza un valor a entero para comparación."""
        if valor is not None:
            return int(valor)
        return None

    @staticmethod
    def _verificar_cambios(check_result: Dict[str, Any], ganado: Ganado, fecha_nac: Optional[str], estado_id: int) -> bool:
        """Verifica si hay cambios entre los valores actuales y los nuevos."""
        bd_fecha_str = GanadoService._normalizar_fecha_para_comparacion(check_result.get('fecha_nacimiento'))
        bd_id_estado = GanadoService._normalizar_valor_entero(check_result.get('id_estado'))
        bd_id_potrero = GanadoService._normalizar_valor_entero(check_result.get('id_potrero'))
        bd_id_persona = GanadoService._normalizar_valor_entero(check_result.get('id_persona'))
        nuevo_id_potrero = GanadoService._normalizar_valor_entero(ganado.id_potrero)
        nuevo_id_persona = GanadoService._normalizar_valor_entero(ganado.id_persona)
        
        return not (
            check_result.get('nombre') == ganado.nombre and
            check_result.get('raza') == ganado.raza and
            bd_fecha_str == fecha_nac and
            check_result.get('sexo') == ganado.sexo.value and
            float(check_result.get('peso') or 0) == float(ganado.peso or 0) and
            bd_id_estado == estado_id and
            bd_id_potrero == nuevo_id_potrero and
            bd_id_persona == nuevo_id_persona
        )

    @staticmethod
    def _ejecutar_update_ganado(cursor, conn, animal_id: int, ganado: Ganado, fecha_nac: Optional[str], estado_id: int, tenant_id: Optional[int]) -> bool:
        """Ejecuta el UPDATE del ganado en la base de datos."""
        sql = """
            UPDATE ganado SET
                nombre = %s,
                raza = %s,
                fecha_nacimiento = %s,
                sexo = %s,
                peso = %s,
                id_estado = %s,
                id_potrero = %s,
                id_persona = %s
            WHERE id = %s
        """
        values = [
            ganado.nombre, ganado.raza,
            fecha_nac, ganado.sexo.value,
            ganado.peso, estado_id,
            ganado.id_potrero, ganado.id_persona, animal_id
        ]
        
        if tenant_id is not None:
            sql += SQL_AND_TENANT_ID
            values.append(tenant_id)
        
        cursor.execute(sql, tuple(values))
        rowcount = cursor.rowcount
        
        if rowcount == 0:
            return False
        
        conn.commit()
        return True

    @staticmethod
    def _actualizar_ganado_en_db(id: int, ganado: Ganado, tenant_id_override: Optional[int] = None) -> bool:
        """Actualiza el ganado en la base de datos."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            estado_id = GanadoService._obtener_estado_id_desde_db(ganado.estado)
            if estado_id is None:
                estado_id = GanadoService._mapear_estado_string_a_id(ganado.estado)
            fecha_nac = GanadoService._convertir_fecha_nacimiento(ganado.fecha_nacimiento)
            tenant_id = tenant_id_override if tenant_id_override is not None else GanadoService._obtener_tenant_id()
            
            check_result = GanadoService._validar_animal_existe(cursor, id, tenant_id)
            if not check_result:
                return False
            
            if not GanadoService._verificar_cambios(check_result, ganado, fecha_nac, estado_id):
                conn.commit()
                return True
            
            return GanadoService._ejecutar_update_ganado(cursor, conn, id, ganado, fecha_nac, estado_id, tenant_id)
        except Exception:
            return False
        finally:
            conn.close()

    @staticmethod
    def actualizar_ganado(id: int, ganado: Ganado, tenant_id_override: Optional[int] = None) -> bool:
        """
        Actualizar ganado.
        
        Args:
            id: ID del ganado
            ganado: Objeto Ganado con datos actualizados
            tenant_id_override: Si se proporciona, valida que el ganado pertenezca a este tenant
        """
        try:
            # Verificar que el ganado existe y pertenece al tenant
            ganado_existente = GanadoService.obtener_ganado(id, tenant_id_override)
            if not ganado_existente:
                return False
            
            potrero_anterior_id = GanadoService._obtener_potrero_anterior(id)
            nuevo_potrero_id = ganado.id_potrero
            
            GanadoService._verificar_cambio_potrero(nuevo_potrero_id, potrero_anterior_id)
            actualizado = GanadoService._actualizar_ganado_en_db(id, ganado, tenant_id_override)
            GanadoService._sincronizar_potreros_despues_actualizacion(actualizado, nuevo_potrero_id, potrero_anterior_id)
            
            return actualizado
        except Exception:
            return False

    @staticmethod
    def _obtener_id_estado_por_causa(causa_baja: str) -> int:
        """Obtiene el id_estado correspondiente a una causa de baja."""
        mapeo_causas = {
            'muerte': 5,
            'venta': 6,
            'robo': 7,
            'otra': 8
        }
        return mapeo_causas.get(causa_baja.lower(), 8)  # Por defecto 'otra'
    
    @staticmethod
    def dar_baja_ganado(id: int, causa_baja: str, observaciones: Optional[str] = None, tenant_id_override: Optional[int] = None) -> bool | str:
        """
        Da de baja lógica a un animal cambiando su id_estado.
        
        Args:
            id: ID del ganado
            causa_baja: Causa de la baja
            observaciones: Observaciones opcionales
            tenant_id_override: Si se proporciona, valida que el ganado pertenezca a este tenant
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # Verificar que el animal existe y pertenece al tenant
            tenant_id = tenant_id_override if tenant_id_override is not None else GanadoService._obtener_tenant_id()
            sql = "SELECT id_estado, id_potrero, tenant_id FROM ganado WHERE id = %s"
            params = (id,)
            if tenant_id is not None:
                sql += SQL_AND_TENANT_ID
                params = (id, tenant_id)
            
            cursor.execute(sql, params)
            animal = cursor.fetchone()

            if not animal:
                cursor.close()
                conn.close()
                return "Animal no encontrado"
            
            # Validar tenant
            if tenant_id is not None and animal.get('tenant_id') != tenant_id:
                cursor.close()
                conn.close()
                return "No tiene acceso a este animal"

            id_estado_actual = animal.get('id_estado')

            # Verificar si ya está dado de baja (id_estado >= 4)
            if id_estado_actual and id_estado_actual >= 4:
                cursor.close()
                conn.close()
                return "El animal ya está dado de baja"

            # Obtener potrero_id antes de actualizar
            potrero_id = animal.get('id_potrero')

            # Obtener el id_estado correspondiente a la causa de baja
            nuevo_id_estado = GanadoService._obtener_id_estado_por_causa(causa_baja)

            # Actualizar id_estado a uno de baja y liberar potrero
            sql = """
                UPDATE ganado
                SET id_estado = %s,
                    id_potrero = NULL
                WHERE id = %s
            """
            params = (nuevo_id_estado, id)
            if tenant_id is not None:
                sql += SQL_AND_TENANT_ID
                params = (nuevo_id_estado, id, tenant_id)
            
            cursor.execute(sql, params)
            conn.commit()

            # Sincronizar ocupación del potrero si tenía uno
            if potrero_id:
                try:
                    PotreroService.sincronizar_ocupacion(potrero_id)
                except Exception:
                    pass

            cursor.close()
            conn.close()
            return True

        except Exception as e:
            return False
        finally:
            if 'conn' in locals():
                try:
                    conn.close()
                except Exception:
                    pass

    @staticmethod
    def reactivar_ganado(id: int, nuevo_estado: str = 'saludable', tenant_id_override: Optional[int] = None) -> bool | str:
        """
        Reactivar un animal cambiando su id_estado a uno activo.
        
        Args:
            id: ID del ganado
            nuevo_estado: Nuevo estado del animal
            tenant_id_override: Si se proporciona, valida que el ganado pertenezca a este tenant
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Verificar que el animal existe y pertenece al tenant
            tenant_id = tenant_id_override if tenant_id_override is not None else GanadoService._obtener_tenant_id()
            sql = "SELECT id_estado, tenant_id FROM ganado WHERE id = %s"
            params = (id,)
            if tenant_id is not None:
                sql += SQL_AND_TENANT_ID
                params = (id, tenant_id)
            
            cursor.execute(sql, params)
            animal = cursor.fetchone()
            
            if not animal:
                cursor.close()
                conn.close()
                return "Animal no encontrado"
            
            # Validar tenant
            if tenant_id is not None and animal.get('tenant_id') != tenant_id:
                cursor.close()
                conn.close()
                return "No tiene acceso a este animal"
            
            id_estado_actual = animal.get('id_estado')
            
            # Verificar si ya está activo (id_estado < 4)
            if id_estado_actual and id_estado_actual < 4:
                cursor.close()
                conn.close()
                return "El animal ya está activo"
            
            # Obtener el id_estado correspondiente al nuevo estado activo
            mapeo_estados = {
                'saludable': 1,
                'revision': 2,
                'enfermo': 3
            }
            nuevo_id_estado = mapeo_estados.get(nuevo_estado.lower(), 1)  # Por defecto 'saludable'
            
            # Actualizar id_estado a uno activo
            sql = """
                UPDATE ganado 
                SET id_estado = %s
                WHERE id = %s
            """
            params = (nuevo_id_estado, id)
            if tenant_id is not None:
                sql += SQL_AND_TENANT_ID
                params = (nuevo_id_estado, id, tenant_id)
            
            cursor.execute(sql, params)
            conn.commit()
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            return False
        finally:
            if 'conn' in locals():
                try:
                    conn.close()
                except Exception:
                    pass

    @staticmethod
    def eliminar_ganado(id: int, tenant_id_override: Optional[int] = None) -> bool | str:
        """
        Elimina un ganado dando de baja con causa 'otra'.
        
        Args:
            id: ID del ganado
            tenant_id_override: Si se proporciona, valida que el ganado pertenezca a este tenant
        """
        result = GanadoService.dar_baja_ganado(id, 'otra', 'Eliminación automática', tenant_id_override=tenant_id_override)
        
        # Convertir mensajes de error específicos a False para casos de "no encontrado"
        if isinstance(result, str) and "no encontrado" in result.lower():
            return False
        
        # Retornar el resultado tal cual (True, False, o string con mensaje de error)
        return result

    @staticmethod
    def buscar_por_potrero(potrero_id: int, tenant_id_override: Optional[int] = None) -> List[Ganado]:
        """
        Buscar ganado por potrero con validación de tenant.
        
        Args:
            potrero_id: ID del potrero
            tenant_id_override: Si se proporciona, filtra por este tenant
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            tenant_id = tenant_id_override if tenant_id_override is not None else GanadoService._obtener_tenant_id()

            sql = "SELECT * FROM ganado WHERE id_potrero = %s"
            params = (potrero_id,)
            if tenant_id is not None:
                sql += SQL_AND_TENANT_ID
                params = (potrero_id, tenant_id)
            
            cursor.execute(sql, params)
            results = cursor.fetchall()

            return [Ganado.from_dict(result) for result in results]

        except Exception as e:
            return []
        finally:
            if 'conn' in locals() and conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    @staticmethod
    def buscar_por_codigo_qr(codigo_qr: str, tenant_id_override: Optional[int] = None) -> Optional[Ganado]:
        """
        Buscar ganado por código QR con validación de tenant.
        
        Args:
            codigo_qr: Código QR del ganado
            tenant_id_override: Si se proporciona, filtra por este tenant
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            tenant_id = tenant_id_override if tenant_id_override is not None else GanadoService._obtener_tenant_id()

            sql = "SELECT * FROM ganado WHERE codigo_qr = %s"
            params = (codigo_qr,)
            if tenant_id is not None:
                sql += SQL_AND_TENANT_ID
                params = (codigo_qr, tenant_id)
            
            cursor.execute(sql, params)

            result = cursor.fetchone()
            if result:
                return Ganado.from_dict(result)
            return None

        except Exception:
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def _validar_tenant_ganado(row: Dict[str, Any], tenant_id: Optional[int]) -> bool:
        """Valida que el ganado pertenece al tenant especificado."""
        if tenant_id is None:
            return True
        return row.get('tenant_id') == tenant_id

    @staticmethod
    def _procesar_propietario(row: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa y retorna los datos del propietario desde el row."""
        propietario = GanadoService._empty_propietario()
        propietario.update({
            "nombre": row.get("propietario_nombre"),
            "telefono": row.get("propietario_telefono"),
            "rol": row.get("propietario_rol"),
        })
        return propietario

    @staticmethod
    def _procesar_potrero(row: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa y retorna los datos del potrero desde el row."""
        potrero = GanadoService._empty_potrero()
        if row.get("id_potrero") is not None:
            potrero.update({
                "nombre": row.get("potrero_nombre"),
                "tipo_pasto": row.get("potrero_tipo_pasto"),
                "ultima_limpieza": GanadoService._to_iso_string(row.get("potrero_ultima_limpieza")),
                "fecha_ultimo_uso": GanadoService._to_iso_string(row.get("potrero_fecha_ultimo_uso")),
                "proxima_limpieza": GanadoService._to_iso_string(row.get("potrero_proxima_limpieza")),
                "capacidad": GanadoService._to_nullable_int(row.get("potrero_capacidad")),
                "estado": row.get("potrero_estado"),
            })
        return potrero

    @staticmethod
    def _construir_detalle_ganado(row: Dict[str, Any], animal_id: Optional[int], 
                                   propietario: Dict[str, Any], potrero: Dict[str, Any],
                                   vacunas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Construye el diccionario de detalle del ganado."""
        animal_id_value = row.get("id")
        return {
            "id": animal_id if animal_id is not None else animal_id_value,
            "nombre": row.get("nombre"),
            "raza": row.get("raza"),
            "fecha_nacimiento": GanadoService._to_iso_string(row.get("fecha_nacimiento")),
            "edad": GanadoService._calcular_edad(row.get("fecha_nacimiento")),
            "sexo": row.get("sexo"),
            "peso": GanadoService._to_nullable_float(row.get("peso")),
            "estado": row.get("estado_principal"),
            "estado_salud": row.get("estado_salud"),
            "codigo_qr": row.get("codigo_qr"),
            "propietario": propietario,
            "propietario_nombre": propietario["nombre"],
            "propietario_telefono": propietario["telefono"],
            "propietario_rol": propietario["rol"],
            "potrero": potrero,
            "potrero_nombre": potrero["nombre"],
            "vacunas": vacunas,
            "historial": [],
            "id_potrero": GanadoService._to_nullable_int(row.get("id_potrero")),
            "id_persona": GanadoService._to_nullable_int(row.get("id_persona")),
        }

    @staticmethod
    def _extraer_id_numerico(identifier: int | str) -> Optional[int]:
        """Extrae ID numérico del identifier si es posible."""
        if isinstance(identifier, int):
            return identifier
        if isinstance(identifier, str):
            import re
            match = re.search(r'(\d+)', identifier)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, TypeError):
                    pass
        return None

    @staticmethod
    def _construir_query_principal(search_id: Any, identifier: Any, tenant_id: Optional[int]) -> tuple:
        """Construye la query principal y parámetros."""
        query = """
            SELECT
                g.id,
                g.nombre,
                g.raza,
                g.fecha_nacimiento,
                g.sexo,
                g.peso,
                g.id_potrero,
                g.id_persona,
                g.id_estado,
                g.tenant_id,
                q.codigo_qr,
                eg.tipo_estado AS estado_principal,
                NULL AS estado_salud,
                p.nombre AS potrero_nombre,
                p.capacidad AS potrero_capacidad,
                hp.fecha_ultima_limpieza AS potrero_ultima_limpieza,
                hp.fecha_ultimo_uso AS potrero_fecha_ultimo_uso,
                hp.fecha_proxima_limpieza AS potrero_proxima_limpieza,
                ep.nombre_estado AS potrero_estado,
                tp.tipo_pasto AS potrero_tipo_pasto,
                per.telefono AS propietario_telefono,
                CONCAT_WS(' ', per.primer_nombre, per.segundo_nombre, per.primer_apellido, per.segundo_apellido) AS propietario_nombre,
                roles.rol AS propietario_rol
            FROM ganado g
            LEFT JOIN qr q ON q.id_ganado = g.id
            LEFT JOIN estado_ganado eg ON eg.id = g.id_estado
            LEFT JOIN potrero p ON p.id = g.id_potrero
            LEFT JOIN estado_potrero ep ON ep.id = p.id_estado_potrero
            LEFT JOIN tipo_pasto tp ON tp.id = p.id_tipo_pasto
            LEFT JOIN personas per ON per.id = g.id_persona
            LEFT JOIN roles ON roles.id = per.id_rol
            LEFT JOIN historial_potreros hp ON hp.id_potrero = p.id
            WHERE (g.id = %s OR q.codigo_qr = %s)
        """

        params = (search_id, identifier)
        if tenant_id is not None:
            query += SQL_AND_G_TENANT_ID
            params = (search_id, identifier, tenant_id)

        return query + " LIMIT 1", params

    @staticmethod
    def _construir_query_fallback(identifier: Any, tenant_id: Optional[int]) -> tuple:
        """Construye la query de fallback sin historial_potreros."""
        query = """
            SELECT
                g.id,
                g.nombre,
                g.raza,
                g.fecha_nacimiento,
                g.sexo,
                g.peso,
                g.id_potrero,
                g.id_persona,
                g.id_estado,
                g.tenant_id,
                q.codigo_qr,
                eg.tipo_estado AS estado_principal,
                NULL AS estado_salud,
                p.nombre AS potrero_nombre,
                p.capacidad AS potrero_capacidad,
                NULL AS potrero_ultima_limpieza,
                NULL AS potrero_fecha_ultimo_uso,
                NULL AS potrero_proxima_limpieza,
                ep.nombre_estado AS potrero_estado,
                tp.tipo_pasto AS potrero_tipo_pasto,
                per.telefono AS propietario_telefono,
                CONCAT_WS(' ', per.primer_nombre, per.segundo_nombre, per.primer_apellido, per.segundo_apellido) AS propietario_nombre,
                roles.rol AS propietario_rol
            FROM ganado g
            LEFT JOIN qr q ON q.id_ganado = g.id
            LEFT JOIN estado_ganado eg ON eg.id = g.id_estado
            LEFT JOIN potrero p ON p.id = g.id_potrero
            LEFT JOIN estado_potrero ep ON ep.id = p.id_estado_potrero
            LEFT JOIN tipo_pasto tp ON tp.id = p.id_tipo_pasto
            LEFT JOIN personas per ON per.id = g.id_persona
            LEFT JOIN roles ON roles.id = per.id_rol
            WHERE (g.id = %s OR q.codigo_qr = %s)
        """

        if tenant_id is not None:
            query += SQL_AND_G_TENANT_ID
            params = (identifier, identifier, tenant_id)
        else:
            params = (identifier, identifier)

        return query + " LIMIT 1", params

    @staticmethod
    def _ejecutar_consulta_principal(cursor, query: str, params: tuple, identifier: Any, tenant_id: Optional[int]) -> Optional[Dict[str, Any]]:
        """Ejecuta la consulta principal y maneja errores."""
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()

            if not row:
                print("[GANADO_SERVICE] No se encontró ganado con identifier={} (sin tenant_id)".format(identifier))
                return None

            if not GanadoService._validar_tenant_ganado(row, tenant_id):
                print("[GANADO_SERVICE] Ganado encontrado pero no pertenece al tenant {} (tenant_id del ganado: {})".format(
                    tenant_id, row.get('tenant_id')))
                return None

            return row
        except Exception as query_error:
            error_msg = str(query_error)
            print("[GANADO_SERVICE] Error ejecutando consulta principal: {}".format(error_msg))

            # Si falla por tabla historial_potreros, intentar fallback
            if any(keyword in error_msg.lower() for keyword in ['historial_potreros', "doesn't exist", 'unknown column']):
                return GanadoService._ejecutar_consulta_fallback(cursor, identifier, tenant_id)
            raise

    @staticmethod
    def _ejecutar_consulta_fallback(cursor, identifier: Any, tenant_id: Optional[int]) -> Optional[Dict[str, Any]]:
        """Ejecuta la consulta de fallback."""
        try:
            print("[GANADO_SERVICE] Intentando consulta sin historial_potreros...")
            query, params = GanadoService._construir_query_fallback(identifier, tenant_id)
            cursor.execute(query, params)
            row = cursor.fetchone()

            if not row or not GanadoService._validar_tenant_ganado(row, tenant_id):
                print("[GANADO_SERVICE] No se encontró ganado con identifier={} en consulta simplificada".format(identifier))
                return None

            print("[GANADO_SERVICE] Consulta simplificada exitosa")
            return row
        except Exception as fallback_error:
            print("[GANADO_SERVICE] Error en consulta simplificada: {}".format(fallback_error))
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def obtener_ganado_detallado(identifier: int | str, tenant_id_override: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Obtener ganado detallado por ID o código QR.

        Args:
            identifier: ID del ganado o código QR
            tenant_id_override: Si se proporciona, valida que el ganado pertenezca a este tenant
        """
        connection = get_connection()
        if connection is None:
            print("No se pudo obtener conexión a la base de datos.")
            return None

        tenant_id = tenant_id_override if tenant_id_override is not None else GanadoService._obtener_tenant_id()
        numeric_id = GanadoService._extraer_id_numerico(identifier)
        search_id = numeric_id if numeric_id is not None else identifier

        print("[GANADO_SERVICE] Búsqueda: identifier={}, numeric_id={}, search_id={}".format(identifier, numeric_id, search_id))

        query, params = GanadoService._construir_query_principal(search_id, identifier, tenant_id)
        print("[GANADO_SERVICE] obtener_ganado_detallado: Buscando con identifier={}, tenant_id={}".format(identifier, tenant_id))
        print("[GANADO_SERVICE] Parámetros de consulta: {}".format(params))

        try:
            cursor = connection.cursor(dictionary=True)
            try:
                row = GanadoService._ejecutar_consulta_principal(cursor, query, params, identifier, tenant_id)
                if not row:
                    return None

                print("[GANADO_SERVICE] Resultado de consulta: encontrado")
                print("[GANADO_SERVICE] Datos encontrados: id={}, nombre={}, tenant_id={}".format(
                    row.get('id'), row.get('nombre'), row.get('tenant_id')))

            finally:
                cursor.close()

            animal_id = GanadoService._to_nullable_int(row.get("id"))
            propietario = GanadoService._procesar_propietario(row)
            potrero = GanadoService._procesar_potrero(row)

            vacunas = []
            if animal_id is not None:
                vacunas = GanadoService._fetch_vacunas(connection, animal_id, tenant_id)
                print("[GANADO_SERVICE] obtener_ganado_detallado: Animal {} tiene {} vacunas".format(animal_id, len(vacunas)))

            resultado = GanadoService._construir_detalle_ganado(row, animal_id, propietario, potrero, vacunas)
            print("[GANADO_SERVICE] obtener_ganado_detallado: Resultado incluye {} vacunas en el dict".format(len(resultado.get('vacunas', []))))
            print("[GANADO_SERVICE] obtener_ganado_detallado: Datos del potrero: {}".format(resultado.get('potrero', {})))
            print("[GANADO_SERVICE] obtener_ganado_detallado: Datos del propietario: {}".format(resultado.get('propietario', {})))
            return resultado
        except Exception as e:
            print("[GANADO_SERVICE] Error en obtener_ganado_detallado: {}: {}".format(type(e).__name__, e))
            import traceback
            traceback.print_exc()
            return None
        finally:
            try:
                connection.close()
            except Exception:
                pass

    @staticmethod
    def obtener_estados_ganado(solo_activos: bool = False, solo_bajas: bool = False) -> List[dict]:
        """
        Obtiene los estados de ganado.
        - solo_activos=True: solo estados activos (id 1-3)
        - solo_bajas=True: solo estados de baja (id 4-8)
        - ambos False: todos los estados
        """
        try:
            conn = get_connection()
            if conn is None:
                return []
            cursor = conn.cursor(dictionary=True)

            if solo_activos:
                cursor.execute("SELECT id, tipo_estado FROM estado_ganado WHERE id BETWEEN 1 AND 3 ORDER BY tipo_estado")
            elif solo_bajas:
                cursor.execute("SELECT id, tipo_estado FROM estado_ganado WHERE id BETWEEN 4 AND 8 ORDER BY tipo_estado")
            else:
                cursor.execute("SELECT id, tipo_estado FROM estado_ganado ORDER BY tipo_estado")

            results = cursor.fetchall()

            # Transformar la estructura para que coincida con lo que espera el frontend
            estados_transformados = []
            for result in results:
                estados_transformados.append({
                    'id': result['id'],
                    'estado': result['tipo_estado'],
                    'nombre_estado': result['tipo_estado']
                })

            return estados_transformados

        except Exception as e:
            return []
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()
