"""Servicio para generar y gestionar códigos QR."""
import os
import qrcode
from typing import Optional, Dict, Any
from ..database.db import get_connection

class QRService:
    """Servicio para manejar códigos QR de ganado."""

    @staticmethod
    def generar_codigo_qr(id_ganado: int, nombre_ganado: str, nombre_propietario: str = "", contacto: str = "") -> str:
        """Generar un código QR único para un ganado."""
        # Crear código único basado en el ID del ganado
        codigo_qr = f"QR_{id_ganado}_{nombre_ganado.replace(' ', '_')}"

        # URL del proyecto
        url = "https://github.com/NavajaOff/QR-FARM/tree/develop"

        # Crear el texto del QR
        texto = f"""
Para más información, visita la URL:
{url}

Información del Ganado:
-----------------------
Nombre del ganado: {nombre_ganado}
ID del ganado: {id_ganado}
Propietario: {nombre_propietario}
Contacto: {contacto}
Código QR: {codigo_qr}
"""

        # Crear directorio qr si no existe
        qr_dir = os.path.join(os.getcwd(), 'qr')
        os.makedirs(qr_dir, exist_ok=True)

        # Generar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(texto)
        qr.make(fit=True)

        # Crear imagen
        img = qr.make_image(fill='black', back_color='white')

        # Guardar imagen
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

            # Generar código QR
            codigo_qr = QRService.generar_codigo_qr(
                id_ganado=id_ganado,
                nombre_ganado=ganado_data['nombre'],
                nombre_propietario=nombre_propietario,
                contacto=ganado_data['telefono'] or ""
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