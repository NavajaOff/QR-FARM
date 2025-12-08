"""Servicio para generar y gestionar códigos QR."""
import json
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import qrcode

from ..database.db import get_connection
from .animal_service import GanadoService
from ..utils.tenant import get_current_tenant_id


class QRService:
    """Servicio para manejar códigos QR de ganado."""

    @staticmethod
    def _build_base_url() -> str:
        """Obtener URL base para redirigir a la ficha en línea."""
        base_url = os.getenv('QR_FARM_WEB_URL') or os.getenv('QR_FARM_FRONTEND_URL')
        if not base_url:
            return "https://github.com/NavajaOff/QR-FARM/tree/develop"
        return base_url.rstrip('/')

    @staticmethod
    def _build_offline_payload(
        codigo_qr: str,
        id_ganado: int,
        nombre_ganado: str,
        nombre_propietario: str,
        contacto: str,
        datos_extra: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[int] = None
    ) -> Dict[str, Any]:
        datos_extra = datos_extra or {}
        base_url = QRService._build_base_url()
        online_url = datos_extra.get('url') or f"{base_url}/ganado/{id_ganado}"

        # Payload optimizado: solo datos esenciales para reducir tamaño del QR
        # El resto de información se obtiene desde la API cuando hay conexión
        payload: Dict[str, Any] = {
            "s": "qr-farm.v1",  # schema (abreviado)
            "t": "ganado",  # type (abreviado)
            "id": id_ganado,
            "c": codigo_qr,  # codigo (abreviado)
            "n": nombre_ganado,  # nombre (abreviado)
            "u": online_url  # url (abreviado)
        }
        
        # Solo incluir datos críticos para modo offline
        if nombre_propietario:
            payload["p"] = nombre_propietario  # propietario (abreviado)
        if contacto:
            payload["ct"] = contacto  # contacto (abreviado)
        if datos_extra.get('estado'):
            payload["e"] = datos_extra.get('estado')  # estado (abreviado)
        # Incluir datos adicionales para mostrar más información cuando la sincronización falla
        if datos_extra.get('peso'):
            payload["peso"] = datos_extra.get('peso')
        if datos_extra.get('sexo'):
            payload["sexo"] = datos_extra.get('sexo')
        if datos_extra.get('fecha_nacimiento'):
            payload["fecha_nacimiento"] = datos_extra.get('fecha_nacimiento')
        if datos_extra.get('raza'):
            payload["raza"] = datos_extra.get('raza')
        
        # Incluir tenant_id solo si es necesario para multi-tenant
        if tenant_id:
            payload["tid"] = tenant_id  # tenant_id (abreviado)

        return payload

    @staticmethod
    def generar_codigo_qr(
        id_ganado: int,
        nombre_ganado: str,
        nombre_propietario: str = "",
        contacto: str = "",
        datos_extra: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[int] = None
    ) -> str:
        """Generar un código QR único para un ganado con datos embebidos."""
        codigo_qr = f"QR_{id_ganado}_{nombre_ganado.replace(' ', '_')}"

        offline_payload = QRService._build_offline_payload(
            codigo_qr=codigo_qr,
            id_ganado=id_ganado,
            nombre_ganado=nombre_ganado,
            nombre_propietario=nombre_propietario,
            contacto=contacto,
            datos_extra=datos_extra,
            tenant_id=tenant_id
        )

        texto = json.dumps(offline_payload, separators=(',', ':'))

        qr_dir = os.path.join(os.getcwd(), 'qr')
        os.makedirs(qr_dir, exist_ok=True)

        qr = qrcode.QRCode(
            version=None,  # Auto-ajustar versión según cantidad de datos
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% corrección de errores (máxima tolerancia)
            box_size=20,  # Tamaño más grande para mejor legibilidad y detección
            border=8,  # Borde más grande para mejor detección
        )

        qr.add_data(texto)
        qr.make(fit=True)

        # Generar imagen con mejor calidad y contraste
        img = qr.make_image(fill='black', back_color='white')

        filename = f"{codigo_qr}.png"
        filepath = os.path.join(qr_dir, filename)
        # Guardar sin compresión para máxima calidad y legibilidad
        # optimize=False evita compresión adicional, mejorando la detección
        img.save(filepath, 'PNG', optimize=False, compress_level=0)

        return codigo_qr

    @staticmethod
    def _obtener_datos_ganado(cursor, id_ganado, tenant_id):
        """Obtiene los datos del ganado desde la BD."""
        cursor.execute("""
            SELECT g.nombre, g.tenant_id, p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido, p.telefono
            FROM ganado g
            LEFT JOIN personas p ON g.id_persona = p.id
            WHERE g.id = %s AND g.tenant_id = %s
        """, (id_ganado, tenant_id))
        return cursor.fetchone()

    @staticmethod
    def _construir_nombre_propietario(ganado_data):
        """Construye el nombre completo del propietario."""
        if not (ganado_data['primer_nombre'] or ganado_data['primer_apellido']):
            return ""
        partes = [
            ganado_data['primer_nombre'] or '',
            ganado_data['segundo_nombre'] or '',
            ganado_data['primer_apellido'] or '',
            ganado_data['segundo_apellido'] or ''
        ]
        return ' '.join(partes).strip()

    @staticmethod
    def _serializar_potrero(potrero_detalle):
        """Serializa los datos del potrero."""
        if not isinstance(potrero_detalle, dict):
            return None
        return {
            'nombre': potrero_detalle.get('nombre'),
            'tipo_pasto': potrero_detalle.get('tipo_pasto'),
            'ultima_limpieza': potrero_detalle.get('ultima_limpieza'),
            'fecha_ultimo_uso': potrero_detalle.get('fecha_ultimo_uso'),
            'proxima_limpieza': potrero_detalle.get('proxima_limpieza'),
            'capacidad': potrero_detalle.get('capacidad'),
            'estado': potrero_detalle.get('estado')
        }

    @staticmethod
    def _obtener_datos_extra(id_ganado):
        """Obtiene los datos extra del ganado."""
        detalles_ganado = GanadoService.obtener_ganado_detallado(id_ganado)
        if not detalles_ganado:
            return {}
        potrero_detalle = detalles_ganado.get('potrero') or {}
        potrero_serializado = QRService._serializar_potrero(potrero_detalle)
        return {
            'estado': detalles_ganado.get('estado'),
            'estado_salud': detalles_ganado.get('estado_salud'),
            'potrero': potrero_serializado,
            'peso': detalles_ganado.get('peso'),
            'sexo': detalles_ganado.get('sexo'),
            'fecha_nacimiento': detalles_ganado.get('fecha_nacimiento'),
            'raza': detalles_ganado.get('raza'),
            'edad': detalles_ganado.get('edad'),
        }

    @staticmethod
    def crear_qr_ganado(id_ganado: int, id_persona_encargado: Optional[int] = None, id_persona_dueno: Optional[int] = None) -> bool:
        """Crear registro QR para un ganado."""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            tenant_id = get_current_tenant_id()
            if tenant_id is None:
                raise ValueError("Tenant requerido para crear QR")

            ganado_data = QRService._obtener_datos_ganado(cursor, id_ganado, tenant_id)
            if not ganado_data:
                return False

            nombre_propietario = QRService._construir_nombre_propietario(ganado_data)
            datos_extra = QRService._obtener_datos_extra(id_ganado)

            codigo_qr = QRService.generar_codigo_qr(
                id_ganado=id_ganado,
                nombre_ganado=ganado_data['nombre'],
                nombre_propietario=nombre_propietario,
                contacto=ganado_data['telefono'] or "",
                datos_extra=datos_extra,
                tenant_id=tenant_id
            )

            cursor.execute("""
                INSERT INTO qr (id_ganado, id_persona_encargado, id_persona_dueno, codigo_qr, tenant_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_ganado, id_persona_encargado, id_persona_dueno, codigo_qr, tenant_id))

            conn.commit()
            return True

        except ValueError as ve:
            print(f"Error de validación creando QR para ganado {id_ganado}: {ve}")
            return False
        except Exception as e:
            print(f"Error creando QR para ganado {id_ganado}: {type(e).__name__}: {e}")
            if 'conn' in locals() and conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    @staticmethod
    def obtener_qr_por_ganado(id_ganado: int) -> Optional[Dict[str, Any]]:
        """Obtener información QR de un ganado."""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            tenant_id = get_current_tenant_id()
            
            sql = """
                SELECT qr.*, g.nombre as nombre_ganado,
                       p_enc.primer_nombre as enc_primer_nom, p_enc.primer_apellido as enc_primer_ape,
                       p_dueno.primer_nombre as dueno_primer_nom, p_dueno.primer_apellido as dueno_primer_ape
                FROM qr
                JOIN ganado g ON qr.id_ganado = g.id
                LEFT JOIN personas p_enc ON qr.id_persona_encargado = p_enc.id
                LEFT JOIN personas p_dueno ON qr.id_persona_dueno = p_dueno.id
                WHERE qr.id_ganado = %s
            """
            params = (id_ganado,)
            if tenant_id is not None:
                sql += " AND qr.tenant_id = %s"
                params = (id_ganado, tenant_id)
            
            cursor.execute(sql, params)

            return cursor.fetchone()

        except Exception as e:
            print(f"Error obteniendo QR para ganado {id_ganado}: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()