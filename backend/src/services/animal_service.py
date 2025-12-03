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
    def _obtener_tenant_id() -> Optional[int]:
        """Obtiene el tenant_id del contexto actual."""
        try:
            from flask import g
            tenant_id = get_current_tenant_id()
            return tenant_id
        except Exception:
            return None

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
    def _fetch_vacunas(connection, animal_id: int) -> List[Dict[str, Any]]:
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
            ORDER BY v.fecha_aplicacion DESC, v.id DESC
        """

        cursor = connection.cursor(dictionary=True)
        rows: List[Dict[str, Any]] = []
        try:
            cursor.execute(query, (animal_id,))
            rows = cursor.fetchall()
        except Exception:  # pylint: disable=broad-except
            pass
        finally:
            cursor.close()

        vacunas: List[Dict[str, Any]] = []
        for row in rows:
            vacunas.append({
                "id": row.get("id"),
                "nombre": row.get("nombre_vacuna"),
                "fecha_aplicacion": GanadoService._to_iso_string(row.get("fecha_aplicacion")),
                "proxima_dosis": GanadoService._to_iso_string(row.get("proxima_dosis")),
                "estado": row.get("estado"),
                "responsable": row.get("responsable_nombre") or row.get("responsable"),
            })
        return vacunas

    @staticmethod
    def crear_ganado(ganado: Ganado) -> Optional[Ganado]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            if ganado.id_potrero:
                PotreroService.verificar_capacidad_disponible(ganado.id_potrero)

            tenant_id = GanadoService._obtener_tenant_id()
            if tenant_id is None:
                raise ValueError("Tenant requerido para crear ganado")

            sql = """
                INSERT INTO ganado (
                    nombre, raza, fecha_nacimiento,
                    sexo, peso, id_estado, id_potrero, id_persona, tenant_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            # Convertir fecha_nacimiento a string si es date object
            fecha_nac = ganado.fecha_nacimiento
            if fecha_nac and hasattr(fecha_nac, 'isoformat'):
                fecha_nac = fecha_nac.isoformat()
            elif isinstance(fecha_nac, str):
                # Si ya es string, mantenerlo
                pass
            else:
                fecha_nac = None

            estado_id = GanadoService._obtener_estado_id_desde_db(ganado.estado)
            if estado_id is None:
                estado_id = GanadoService._mapear_estado_string_a_id(ganado.estado)
            values = (
                ganado.nombre, ganado.raza,
                fecha_nac, ganado.sexo.value,
                ganado.peso, estado_id,
                ganado.id_potrero, ganado.id_persona, tenant_id
            )

            cursor.execute(sql, values)
            conn.commit()

            ganado.id = cursor.lastrowid
            if ganado.id_potrero:
                try:
                    PotreroService.sincronizar_ocupacion(ganado.id_potrero)
                except Exception:
                    pass
            return ganado

        except Exception as e:
            return None
        finally:
            if 'conn' in locals():
                conn.close()


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
                return Ganado.from_dict(result)
            return None

        except Exception as e:
            print(f"Error al obtener ganado {id}: {e}")
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
            print(f"Error al obtener animales: {e}")
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
        if fecha_nac and hasattr(fecha_nac, 'isoformat'):
            return fecha_nac.isoformat()
        elif isinstance(fecha_nac, str):
            return fecha_nac  # Ya es string, mantener como está
        else:
            return None

    @staticmethod
    def _eliminar_archivo_qr(codigo_qr: str) -> None:
        if not codigo_qr:
            return
        try:
            qr_path = QR_STORAGE_DIR / f"{codigo_qr}.png"
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
    def _actualizar_ganado_en_db(id: int, ganado: Ganado, tenant_id_override: Optional[int] = None) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            estado_id = GanadoService._obtener_estado_id_desde_db(ganado.estado)
            if estado_id is None:
                estado_id = GanadoService._mapear_estado_string_a_id(ganado.estado)
            fecha_nac = GanadoService._convertir_fecha_nacimiento(ganado.fecha_nacimiento)
            tenant_id = tenant_id_override if tenant_id_override is not None else GanadoService._obtener_tenant_id()
            
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
                ganado.id_potrero, ganado.id_persona, id
            ]
            
            if tenant_id is not None:
                sql += SQL_AND_TENANT_ID
                values.append(tenant_id)
            
            cursor.execute(sql, tuple(values))
            conn.commit()
            return cursor.rowcount > 0
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
            'otra': 8,
            'dado_de_baja': 4
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
            "id_revision": GanadoService._to_nullable_int(row.get("id_revision")),
        }

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
        
        main_query = """
            SELECT
                g.id,
                g.nombre,
                g.raza,
                g.fecha_nacimiento,
                g.sexo,
                g.peso,
                g.id_potrero,
                g.id_persona,
                g.id_revision,
                g.id_estado,
                g.tenant_id,
                q.codigo_qr,
                eg.tipo_estado AS estado_principal,
                NULL AS estado_salud,
                p.nombre AS potrero_nombre,
                p.capacidad AS potrero_capacidad,
                p.ultima_limpieza AS potrero_ultima_limpieza,
                p.fecha_ultimo_uso AS potrero_fecha_ultimo_uso,
                p.proxima_limpieza AS potrero_proxima_limpieza,
                p.estado AS potrero_estado,
                tp.tipo_pasto AS potrero_tipo_pasto,
                per.telefono AS propietario_telefono,
                CONCAT_WS(' ', per.primer_nombre, per.segundo_nombre, per.primer_apellido, per.segundo_apellido) AS propietario_nombre,
                roles.rol AS propietario_rol
            FROM ganado g
            LEFT JOIN qr q ON q.id_ganado = g.id
            LEFT JOIN estado_ganado eg ON eg.id = g.id_estado
            LEFT JOIN potrero p ON p.id = g.id_potrero
            LEFT JOIN tipo_pasto tp ON tp.id = p.id_tipo_pasto
            LEFT JOIN personas per ON per.id = g.id_persona
            LEFT JOIN roles ON roles.id = per.id_rol
            WHERE (g.id = %s OR q.codigo_qr = %s)
        """
        
        params = (identifier, identifier)
        if tenant_id is not None:
            main_query += SQL_AND_G_TENANT_ID
            params = (identifier, identifier, tenant_id)
        
        main_query += " LIMIT 1"

        try:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(main_query, params)
                row = cursor.fetchone()
                
                if not row or not GanadoService._validar_tenant_ganado(row, tenant_id):
                    return None
            finally:
                cursor.close()

            animal_id_value = row.get("id")
            animal_id: Optional[int] = None
            if animal_id_value is not None:
                try:
                    animal_id = int(animal_id_value)
                except (TypeError, ValueError):
                    animal_id = None

            propietario = GanadoService._procesar_propietario(row)
            potrero = GanadoService._procesar_potrero(row)

            vacunas: List[Dict[str, Any]] = []
            if animal_id is not None:
                vacunas = GanadoService._fetch_vacunas(connection, animal_id)

            return GanadoService._construir_detalle_ganado(row, animal_id, propietario, potrero, vacunas)
        except Exception:  # pylint: disable=broad-except
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
