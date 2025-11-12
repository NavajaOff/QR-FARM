"""Servicio para generar y gestionar códigos QR."""
import json
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import qrcode

from ..database.db import get_connection
from .animal_service import GanadoService


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
        datos_extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        datos_extra = datos_extra or {}
        base_url = QRService._build_base_url()
        online_url = datos_extra.get('url') or f"{base_url}/ganado/{id_ganado}"

        payload: Dict[str, Any] = {
            "schema": "qr-farm.v1",
            "type": "ganado",
            "id": id_ganado,
            "codigo": codigo_qr,
            "nombre": nombre_ganado,
            "estado": datos_extra.get('estado'),
            "estado_salud": datos_extra.get('estado_salud'),
            "propietario": {
                "nombre": nombre_propietario or None,
                "contacto": contacto or None
            },
            "potrero": datos_extra.get('potrero'),
            "url": online_url,
            "generado_en": datetime.now(timezone.utc).isoformat()
        }

        if datos_extra.get('peso') is not None:
            payload["peso"] = datos_extra.get('peso')
        if datos_extra.get('sexo'):
            payload["sexo"] = datos_extra.get('sexo')
        if datos_extra.get('fecha_nacimiento'):
            payload["fecha_nacimiento"] = datos_extra.get('fecha_nacimiento')

        resumen_parts = [
            f"Ganado: {nombre_ganado}",
            f"Propietario: {nombre_propietario}" if nombre_propietario else None,
            f"Estado: {datos_extra.get('estado')}" if datos_extra.get('estado') else None,
            f"Contacto: {contacto}" if contacto else None,
            f"Potrero: {datos_extra.get('potrero', {}).get('nombre')}" if isinstance(datos_extra.get('potrero'), dict) and datos_extra.get('potrero', {}).get('nombre') else None,
            f"URL: {online_url}"
        ]
        payload["resumen"] = " | ".join(part for part in resumen_parts if part)

        return payload

    @staticmethod
    def generar_codigo_qr(
        id_ganado: int,
        nombre_ganado: str,
        nombre_propietario: str = "",
        contacto: str = "",
        datos_extra: Optional[Dict[str, Any]] = None
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
        )

        texto = json.dumps(offline_payload, separators=(',', ':'))

        qr_dir = os.path.join(os.getcwd(), 'qr')
        os.makedirs(qr_dir, exist_ok=True)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(texto)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        filename = f"{codigo_qr}.png"
        filepath = os.path.join(qr_dir, filename)
        img.save(filepath)

        return codigo_qr

    @staticmethod
    def crear_qr_ganado(id_ganado: int, id_persona_encargado: Optional[int] = None, id_persona_dueno: Optional[int] = None) -> bool:
        """Crear registro QR para un ganado."""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # Obtener datos del ganado
            cursor.execute("""
                SELECT g.nombre, p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido, p.telefono
                FROM ganado g
                LEFT JOIN personas p ON g.id_persona = p.id
                WHERE g.id = %s
            """, (id_ganado,))

            ganado_data = cursor.fetchone()
            if not ganado_data:
                return False

            # Construir nombre completo del propietario
            nombre_propietario = ""
            if ganado_data['primer_nombre'] or ganado_data['primer_apellido']:
                nombre_propietario = f"{ganado_data['primer_nombre'] or ''} {ganado_data['segundo_nombre'] or ''} {ganado_data['primer_apellido'] or ''} {ganado_data['segundo_apellido'] or ''}".strip()

            detalles_ganado = GanadoService.obtener_ganado_detallado(id_ganado)
            datos_extra: Dict[str, Any] = {}
            if detalles_ganado:
                potrero_detalle = detalles_ganado.get('potrero') or {}
                if isinstance(potrero_detalle, dict):
                    potrero_serializado = {
                        'nombre': potrero_detalle.get('nombre'),
                        'tipo_pasto': potrero_detalle.get('tipo_pasto'),
                        'ultima_limpieza': potrero_detalle.get('ultima_limpieza'),
                        'fecha_ultimo_uso': potrero_detalle.get('fecha_ultimo_uso'),
                        'proxima_limpieza': potrero_detalle.get('proxima_limpieza'),
                        'capacidad': potrero_detalle.get('capacidad'),
                        'estado': potrero_detalle.get('estado')
                    }
                else:
                    potrero_serializado = None
                datos_extra = {
                    'estado': detalles_ganado.get('estado'),
                    'estado_salud': detalles_ganado.get('estado_salud'),
                    'potrero': potrero_serializado,
                    'peso': detalles_ganado.get('peso'),
                    'sexo': detalles_ganado.get('sexo'),
                    'fecha_nacimiento': detalles_ganado.get('fecha_nacimiento'),
                }

            # Generar código QR
            codigo_qr = QRService.generar_codigo_qr(
                id_ganado=id_ganado,
                nombre_ganado=ganado_data['nombre'],
                nombre_propietario=nombre_propietario,
                contacto=ganado_data['telefono'] or "",
                datos_extra=datos_extra
            )

            # Insertar en tabla QR
            cursor.execute("""
                INSERT INTO qr (id_ganado, id_persona_encargado, id_persona_dueno, codigo_qr)
                VALUES (%s, %s, %s, %s)
            """, (id_ganado, id_persona_encargado, id_persona_dueno, codigo_qr))

            conn.commit()
            return True

        except Exception as e:
            print(f"Error creando QR para ganado {id_ganado}: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_qr_por_ganado(id_ganado: int) -> Optional[Dict[str, Any]]:
        """Obtener información QR de un ganado."""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT qr.*, g.nombre as nombre_ganado,
                       p_enc.primer_nombre as enc_primer_nom, p_enc.primer_apellido as enc_primer_ape,
                       p_dueno.primer_nombre as dueno_primer_nom, p_dueno.primer_apellido as dueno_primer_ape
                FROM qr
                JOIN ganado g ON qr.id_ganado = g.id
                LEFT JOIN personas p_enc ON qr.id_persona_encargado = p_enc.id
                LEFT JOIN personas p_dueno ON qr.id_persona_dueno = p_dueno.id
                WHERE qr.id_ganado = %s
            """, (id_ganado,))

            return cursor.fetchone()

        except Exception as e:
            print(f"Error obteniendo QR para ganado {id_ganado}: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()