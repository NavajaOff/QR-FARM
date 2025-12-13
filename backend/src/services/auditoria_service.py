# Servicio Auditoría
from typing import Optional, Dict, Any
from datetime import datetime
import json
import logging
from ..database.db import get_connection
from ..models.historial_cambio import HistorialCambio, TipoEntidad, TipoAccion

logger = logging.getLogger(__name__)


class AuditoriaService:
    @staticmethod
    def registrar_cambio(
        usuario_id: int,
        tenant_id: Optional[int],
        entidad_tipo: TipoEntidad,
        entidad_id: Optional[int],
        accion: TipoAccion,
        descripcion: Optional[str] = None,
        datos_anteriores: Optional[Dict[str, Any]] = None,
        datos_nuevos: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Registra un cambio en el historial de auditoría.
        
        Args:
            usuario_id: ID del usuario que realizó el cambio
            tenant_id: ID del tenant (opcional)
            entidad_tipo: Tipo de entidad modificada
            entidad_id: ID de la entidad modificada
            accion: Tipo de acción realizada
            descripcion: Descripción del cambio
            datos_anteriores: Datos anteriores (JSON)
            datos_nuevos: Datos nuevos (JSON)
        
        Returns:
            True si se registró correctamente, False en caso contrario
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Convertir datos a JSON string si son diccionarios
            datos_anteriores_json = None
            datos_nuevos_json = None
            
            if datos_anteriores:
                try:
                    datos_anteriores_json = json.dumps(datos_anteriores, default=str)
                except (TypeError, ValueError) as e:
                    logger.warning(f"Error serializando datos_anteriores: {e}")
                    datos_anteriores_json = json.dumps({"error": "No se pudieron serializar los datos"})
            
            if datos_nuevos:
                try:
                    datos_nuevos_json = json.dumps(datos_nuevos, default=str)
                except (TypeError, ValueError) as e:
                    logger.warning(f"Error serializando datos_nuevos: {e}")
                    datos_nuevos_json = json.dumps({"error": "No se pudieron serializar los datos"})
            
            sql = """
                INSERT INTO historial_cambios (
                    tenant_id, usuario_id, entidad_tipo, entidad_id,
                    accion, datos_anteriores, datos_nuevos, descripcion, fecha_cambio
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                )
            """
            
            values = (
                tenant_id,
                usuario_id,
                entidad_tipo.value,
                entidad_id,
                accion.value,
                datos_anteriores_json,
                datos_nuevos_json,
                descripcion
            )
            
            cursor.execute(sql, values)
            conn.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error al registrar cambio en historial: {e}", exc_info=True)
            if 'conn' in locals():
                try:
                    conn.rollback()
                except Exception:
                    pass
            return False
        finally:
            if 'conn' in locals():
                try:
                    conn.close()
                except Exception:
                    pass

    @staticmethod
    def obtener_historial_por_tenant(
        tenant_id: int,
        entidad_tipo: Optional[TipoEntidad] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Dict[str, Any]]:
        """
        Obtiene el historial de cambios de un tenant.
        
        Args:
            tenant_id: ID del tenant
            entidad_tipo: Tipo de entidad a filtrar (opcional)
            limit: Límite de resultados
            offset: Offset para paginación
        
        Returns:
            Lista de cambios
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                SELECT 
                    hc.*,
                    CONCAT_WS(' ', p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido) as usuario_nombre,
                    p.email as usuario_email
                FROM historial_cambios hc
                LEFT JOIN usuarios u ON hc.usuario_id = u.id
                LEFT JOIN personas p ON u.id_persona = p.id
                WHERE hc.tenant_id = %s
            """
            
            params = [tenant_id]
            
            if entidad_tipo:
                sql += " AND hc.entidad_tipo = %s"
                params.append(entidad_tipo.value)
            
            sql += " ORDER BY hc.fecha_cambio DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            historial = []
            for result in results:
                historial_dict = {
                    'id': result['id'],
                    'tenant_id': result['tenant_id'],
                    'usuario_id': result['usuario_id'],
                    'usuario_nombre': result.get('usuario_nombre'),
                    'usuario_email': result.get('usuario_email'),
                    'entidad_tipo': result['entidad_tipo'],
                    'entidad_id': result['entidad_id'],
                    'accion': result['accion'],
                    'descripcion': result['descripcion'],
                    'fecha_cambio': result['fecha_cambio'].isoformat() if result['fecha_cambio'] else None
                }
                
                # Parsear JSON si existe
                if result.get('datos_anteriores'):
                    try:
                        historial_dict['datos_anteriores'] = json.loads(result['datos_anteriores'])
                    except (json.JSONDecodeError, TypeError):
                        historial_dict['datos_anteriores'] = None
                
                if result.get('datos_nuevos'):
                    try:
                        historial_dict['datos_nuevos'] = json.loads(result['datos_nuevos'])
                    except (json.JSONDecodeError, TypeError):
                        historial_dict['datos_nuevos'] = None
                
                historial.append(historial_dict)
            
            return historial
            
        except Exception as e:
            logger.error(f"Error al obtener historial: {e}", exc_info=True)
            return []
        finally:
            if 'conn' in locals():
                try:
                    conn.close()
                except Exception:
                    pass

    @staticmethod
    def obtener_historial_por_entidad(
        entidad_tipo: TipoEntidad,
        entidad_id: int,
        tenant_id: Optional[int] = None
    ) -> list[Dict[str, Any]]:
        """
        Obtiene el historial de cambios de una entidad específica.
        
        Args:
            entidad_tipo: Tipo de entidad
            entidad_id: ID de la entidad
            tenant_id: ID del tenant (opcional, para seguridad)
        
        Returns:
            Lista de cambios
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                SELECT 
                    hc.*,
                    CONCAT_WS(' ', p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido) as usuario_nombre
                FROM historial_cambios hc
                LEFT JOIN usuarios u ON hc.usuario_id = u.id
                LEFT JOIN personas p ON u.id_persona = p.id
                WHERE hc.entidad_tipo = %s AND hc.entidad_id = %s
            """
            
            params = [entidad_tipo.value, entidad_id]
            
            if tenant_id:
                sql += " AND hc.tenant_id = %s"
                params.append(tenant_id)
            
            sql += " ORDER BY hc.fecha_cambio DESC"
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            historial = []
            for result in results:
                historial_dict = {
                    'id': result['id'],
                    'usuario_id': result['usuario_id'],
                    'usuario_nombre': result.get('usuario_nombre'),
                    'accion': result['accion'],
                    'descripcion': result['descripcion'],
                    'fecha_cambio': result['fecha_cambio'].isoformat() if result['fecha_cambio'] else None
                }
                
                if result.get('datos_anteriores'):
                    try:
                        historial_dict['datos_anteriores'] = json.loads(result['datos_anteriores'])
                    except (json.JSONDecodeError, TypeError):
                        historial_dict['datos_anteriores'] = None
                
                if result.get('datos_nuevos'):
                    try:
                        historial_dict['datos_nuevos'] = json.loads(result['datos_nuevos'])
                    except (json.JSONDecodeError, TypeError):
                        historial_dict['datos_nuevos'] = None
                
                historial.append(historial_dict)
            
            return historial
            
        except Exception as e:
            logger.error(f"Error al obtener historial por entidad: {e}", exc_info=True)
            return []
        finally:
            if 'conn' in locals():
                try:
                    conn.close()
                except Exception:
                    pass
