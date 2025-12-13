"""Service handling password recovery flows."""
from __future__ import annotations

import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.database.db import get_connection
from src.models.usuario import Usuario
from src.services.usuario_service import UsuarioService
from src.utils.email import send_email

logger = logging.getLogger(__name__)


class RecoveryService:
    """Orquesta tokens, correos y confirmaciones de recuperación de contraseñas."""

    TOKEN_TTL_MINUTES = 30
    ADMIN_ROLES = {'admin', 'administrador'}
    SUPER_ROLE = 'super_admin'
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_APROBADA = 'aprobada'
    ESTADO_RECHAZADA = 'rechazada'

    @staticmethod
    def _generate_token() -> tuple[str, str]:
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
        return token, token_hash

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    @staticmethod
    def _find_admin_email(tenant_id: int) -> Optional[str]:
        conn = get_connection()
        if conn is None:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT p.email
                FROM personas p
                JOIN usuarios u ON u.id_persona = p.id
                JOIN roles r ON r.id = u.id_rol
                WHERE p.tenant_id = %s
                  AND u.estado = 'activo'
                  AND LOWER(TRIM(r.rol)) IN ('admin', 'administrador')
                ORDER BY p.id ASC
                LIMIT 1
            """, (tenant_id,))
            row = cursor.fetchone()
            return row['email'] if row else None
        finally:
            cursor.close()
            if hasattr(conn, 'is_connected') and conn.is_connected():
                conn.close()

    @staticmethod
    def _insert_recovery_request(usuario_id: int, tipo: str, tenant_id: Optional[int], solicitante_email: str, contexto: str) -> int:
        """Create a recovery request in pending state (no token yet)."""
        conn = get_connection()
        if conn is None:
            raise RuntimeError("No hay conexión a la base de datos")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO password_recovery_tokens (
                    usuario_id, token_hash, tipo, tenant_id, solicitante_email,
                    contexto, estado, expires_at
                ) VALUES (%s, NULL, %s, %s, %s, %s, %s, NULL)
            """, (usuario_id, tipo, tenant_id, solicitante_email, contexto, RecoveryService.ESTADO_PENDIENTE))
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            if hasattr(conn, 'is_connected') and conn.is_connected():
                conn.close()

    @staticmethod
    def _update_recovery_with_token(recovery_id: int, token_hash: str, approved_by: int) -> None:
        """Update recovery request with token when approved."""
        expires_at = datetime.utcnow() + timedelta(minutes=RecoveryService.TOKEN_TTL_MINUTES)
        conn = get_connection()
        if conn is None:
            raise RuntimeError("No hay conexión a la base de datos")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE password_recovery_tokens
                SET token_hash = %s,
                    estado = %s,
                    expires_at = %s,
                    approved_at = UTC_TIMESTAMP(),
                    approved_by = %s
                WHERE id = %s
            """, (token_hash, RecoveryService.ESTADO_APROBADA, expires_at, approved_by, recovery_id))
            conn.commit()
        finally:
            cursor.close()
            if hasattr(conn, 'is_connected') and conn.is_connected():
                conn.close()

    @staticmethod
    def request_password_recovery(email: str) -> Dict[str, str]:
        """Create a password recovery request in pending state."""
        if not email:
            raise ValueError("El email es obligatorio")
        usuario = UsuarioService.buscar_por_email(email)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        rol_nombre = (usuario.rol.nombre_rol if usuario.rol else '').lower() if usuario.rol else ''
        tipo = 'admin' if rol_nombre in RecoveryService.ADMIN_ROLES else 'usuario'
        tenant_id = usuario.tenant_id

        if tipo == 'usuario' and tenant_id is None:
            raise ValueError("El usuario no está vinculado a ningún tenant válido")

        if rol_nombre == RecoveryService.SUPER_ROLE:
            raise ValueError("Contacta al equipo para recuperar la clave de superadmin")

        # Determine who should approve (admin of tenant or superadmin)
        if tipo == 'usuario':
            destinatario = RecoveryService._find_admin_email(tenant_id)
            if not destinatario:
                raise ValueError("No se encontró un admin activo para este tenant")
        else:
            destinatario = os.getenv('ROOT_SUPER_ADMIN_EMAIL')
            if not destinatario:
                raise ValueError("No se ha configurado el correo del superadmin (ROOT_SUPER_ADMIN_EMAIL)")

        persona_nombre = usuario.persona.nombre_completo if usuario.persona else email
        persona_email = usuario.persona.email if usuario.persona else email
        contexto = f"destinatario={destinatario};solicitante={persona_email}"
        
        # Create recovery request in pending state (no token yet)
        recovery_id = RecoveryService._insert_recovery_request(
            usuario.id, tipo, tenant_id, persona_email, contexto
        )

        # Send notification email to approver
        subject = "Solicitud de recuperación de contraseña QR FARM"
        body = (
            f"El usuario {persona_nombre} ({persona_email}) ha solicitado recuperar su contraseña.\n"
            f"Por favor, revisa la solicitud en el sistema y aprueba o rechaza la solicitud."
        )
        
        try:
            send_email(destinatario, subject, body)
            logger.info(
                f"Password recovery request notification sent to {destinatario} for user {persona_email} "
                f"(type: {tipo}, tenant_id: {tenant_id}, recovery_id: {recovery_id})"
            )
        except Exception as e:
            logger.error(
                f"Failed to send password recovery notification to {destinatario} for user {persona_email}: {e}"
            )
            # Don't fail the request if email fails, just log it

        return {
            'message': 'Solicitud de recuperación creada. El administrador revisará tu solicitud.',
            'recovery_id': recovery_id
        }

    @staticmethod
    def confirm_password_recovery(token: str, new_password: str, email: str) -> None:
        """Confirm password recovery using approved token. Validates that email matches the token owner."""
        if not token or not new_password:
            raise ValueError("Token y nueva contraseña son obligatorios")
        if not email:
            raise ValueError("El email es obligatorio para validar el token")
        if len(new_password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")

        token_hash = RecoveryService._hash_token(token)
        conn = get_connection()
        if conn is None:
            raise RuntimeError("Base de datos no disponible")
        cursor = conn.cursor(dictionary=True)
        try:
            # Get token with user email for validation
            cursor.execute("""
                SELECT prt.id, prt.usuario_id, prt.estado, prt.solicitante_email,
                       p.email AS usuario_email
                FROM password_recovery_tokens prt
                JOIN usuarios u ON u.id = prt.usuario_id
                LEFT JOIN personas p ON p.id = u.id_persona
                WHERE prt.token_hash = %s
                  AND prt.used_at IS NULL
                  AND prt.expires_at >= UTC_TIMESTAMP()
                LIMIT 1
            """, (token_hash,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Token inválido o expirado")
            
            # Check if request was approved
            if row['estado'] != RecoveryService.ESTADO_APROBADA:
                raise ValueError("La solicitud no ha sido aprobada por el administrador")
            
            # CRITICAL SECURITY: Validate that email matches the token owner
            email_normalized = email.strip().lower()
            solicitante_email = (row['solicitante_email'] or '').strip().lower()
            usuario_email = (row['usuario_email'] or '').strip().lower()
            
            if email_normalized != solicitante_email and email_normalized != usuario_email:
                raise ValueError("El email no coincide con el usuario que solicitó la recuperación. El token solo puede ser usado por el usuario que lo solicitó.")
            
            # Verify the user exists and email matches
            usuario = UsuarioService.buscar_por_email(email)
            if not usuario:
                raise ValueError("Usuario no encontrado con ese email")
            
            if usuario.id != row['usuario_id']:
                raise ValueError("El email no corresponde al usuario autorizado para este token")

            usuario.set_password(new_password)

            cursor.execute(
                "UPDATE usuarios SET contrasena = %s WHERE id = %s",
                (usuario.contrasena, usuario.id)
            )
            cursor.execute(
                "UPDATE password_recovery_tokens SET used_at = UTC_TIMESTAMP() WHERE id = %s",
                (row['id'],)
            )
            conn.commit()
        finally:
            cursor.close()
            if hasattr(conn, 'is_connected') and conn.is_connected():
                conn.close()

    @staticmethod
    def list_pending_requests(tenant_id: Optional[int] = None, current_user_id: Optional[int] = None, is_superadmin: bool = False) -> List[Dict]:
        """
        List pending password recovery requests for admin/superadmin.
        
        Args:
            tenant_id: Tenant ID to filter by (None for superadmin to see all)
            current_user_id: ID of current user (to exclude their own requests for regular admins)
            is_superadmin: Whether current user is superadmin
        """
        conn = get_connection()
        if conn is None:
            raise RuntimeError("Base de datos no disponible")
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT 
                    prt.id,
                    prt.usuario_id,
                    prt.tipo,
                    prt.tenant_id,
                    prt.solicitante_email,
                    prt.contexto,
                    prt.created_at,
                    prt.approved_at,
                    prt.rejected_at,
                    u.id AS usuario_id_db,
                    CONCAT(
                        COALESCE(p.primer_nombre, ''), ' ',
                        COALESCE(p.segundo_nombre, ''), ' ',
                        COALESCE(p.primer_apellido, ''), ' ',
                        COALESCE(p.segundo_apellido, '')
                    ) AS usuario_nombre,
                    p.email AS usuario_email,
                    r.rol AS usuario_rol
                FROM password_recovery_tokens prt
                JOIN usuarios u ON u.id = prt.usuario_id
                LEFT JOIN personas p ON p.id = u.id_persona
                LEFT JOIN roles r ON r.id = u.id_rol
                WHERE prt.estado = %s
                  AND prt.used_at IS NULL
            """
            params = [RecoveryService.ESTADO_PENDIENTE]
            
            if is_superadmin:
                # Superadmin only sees admin recovery requests (admins of tenants)
                query += " AND prt.tipo = 'admin'"
            else:
                # Regular admin only sees user recovery requests from their tenant
                # and excludes their own requests
                query += " AND prt.tipo = 'usuario'"
                if tenant_id is not None:
                    query += " AND prt.tenant_id = %s"
                    params.append(tenant_id)
                if current_user_id is not None:
                    query += " AND prt.usuario_id != %s"
                    params.append(current_user_id)
            
            query += " ORDER BY prt.created_at DESC"
            
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return rows
        finally:
            cursor.close()
            if hasattr(conn, 'is_connected') and conn.is_connected():
                conn.close()

    @staticmethod
    def approve_recovery_request(recovery_id: int, approved_by_user_id: int) -> Dict[str, str]:
        """Approve a recovery request and generate token."""
        conn = get_connection()
        if conn is None:
            raise RuntimeError("Base de datos no disponible")
        cursor = conn.cursor(dictionary=True)
        try:
            # Check if request exists and is pending
            cursor.execute("""
                SELECT id, usuario_id, estado, solicitante_email
                FROM password_recovery_tokens
                WHERE id = %s
            """, (recovery_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Solicitud no encontrada")
            if row['estado'] != RecoveryService.ESTADO_PENDIENTE:
                raise ValueError(f"La solicitud ya está {row['estado']}")
            
            # Generate token
            token, token_hash = RecoveryService._generate_token()
            
            # Update request with token
            RecoveryService._update_recovery_with_token(recovery_id, token_hash, approved_by_user_id)
            
            # Get user info for email
            usuario = UsuarioService.obtener_usuario(row['usuario_id'])
            persona_nombre = usuario.persona.nombre_completo if usuario.persona else row['solicitante_email']
            persona_email = usuario.persona.email if usuario.persona else row['solicitante_email']
            
            # Send email with token to user
            subject = "Solicitud de recuperación de contraseña aprobada - QR FARM"
            body = (
                f"Tu solicitud de recuperación de contraseña ha sido aprobada.\n"
                f"Usa este código temporal para cambiar tu contraseña: {token}\n"
                f"El token expira en {RecoveryService.TOKEN_TTL_MINUTES} minutos."
            )
            
            try:
                send_email(persona_email, subject, body)
                logger.info(f"Recovery approval email sent to {persona_email} with token")
            except Exception as e:
                logger.error(f"Failed to send approval email to {persona_email}: {e}")
                # Don't fail if email fails, token is already generated
            
            return {
                'message': 'Solicitud aprobada. El token ha sido generado.',
                'token': token  # Return token for admin to see/manually share if needed
            }
        finally:
            cursor.close()
            if hasattr(conn, 'is_connected') and conn.is_connected():
                conn.close()

    @staticmethod
    def reject_recovery_request(recovery_id: int, rejected_by_user_id: int) -> None:
        """Reject a recovery request."""
        conn = get_connection()
        if conn is None:
            raise RuntimeError("Base de datos no disponible")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE password_recovery_tokens
                SET estado = %s,
                    rejected_at = UTC_TIMESTAMP()
                WHERE id = %s
                  AND estado = %s
            """, (RecoveryService.ESTADO_RECHAZADA, recovery_id, RecoveryService.ESTADO_PENDIENTE))
            
            if cursor.rowcount == 0:
                raise ValueError("Solicitud no encontrada o ya procesada")
            
            conn.commit()
        finally:
            cursor.close()
            if hasattr(conn, 'is_connected') and conn.is_connected():
                conn.close()

