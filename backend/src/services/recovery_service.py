"""Service handling password recovery flows."""
from __future__ import annotations

import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

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
    def _insert_token_record(token_hash: str, usuario_id: int, tipo: str, tenant_id: Optional[int], destinatario: str, contexto: str) -> None:
        conn = get_connection()
        if conn is None:
            raise RuntimeError("No hay conexión a la base de datos")
        cursor = conn.cursor()
        expires_at = datetime.utcnow() + timedelta(minutes=RecoveryService.TOKEN_TTL_MINUTES)
        try:
            cursor.execute("""
                INSERT INTO password_recovery_tokens (
                    usuario_id, token_hash, tipo, tenant_id, solicitante_email,
                    contexto, expires_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (usuario_id, token_hash, tipo, tenant_id, destinatario, contexto, expires_at))
            conn.commit()
        finally:
            cursor.close()
            if hasattr(conn, 'is_connected') and conn.is_connected():
                conn.close()

    @staticmethod
    def request_password_recovery(email: str) -> Dict[str, str]:
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

        if tipo == 'usuario':
            destinatario = RecoveryService._find_admin_email(tenant_id)
            if not destinatario:
                raise ValueError("No se encontró un admin activo para este tenant")
        else:
            destinatario = os.getenv('ROOT_SUPER_ADMIN_EMAIL')
            if not destinatario:
                raise ValueError("No se ha configurado el correo del superadmin (ROOT_SUPER_ADMIN_EMAIL)")

        token, token_hash = RecoveryService._generate_token()
        persona_nombre = usuario.persona.nombre_completo if usuario.persona else email
        persona_email = usuario.persona.email if usuario.persona else email
        contexto = f"destinatario={destinatario};solicitante={persona_email}"
        RecoveryService._insert_token_record(
            token_hash, usuario.id, tipo, tenant_id, persona_email, contexto
        )

        subject = "Solicitud de recuperación de contraseña QR FARM"
        body = (
            f"Se ha generado un token de recuperación para {persona_nombre} ({persona_email}).\n"
            f"Usa este código temporal: {token}\n"
            f"El token expira en {RecoveryService.TOKEN_TTL_MINUTES} minutos."
        )
        send_email(destinatario, subject, body)

        return {'destinatario': destinatario}

    @staticmethod
    def confirm_password_recovery(token: str, new_password: str) -> None:
        if not token or not new_password:
            raise ValueError("Token y nueva contraseña son obligatorios")
        if len(new_password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")

        token_hash = RecoveryService._hash_token(token)
        conn = get_connection()
        if conn is None:
            raise RuntimeError("Base de datos no disponible")
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, usuario_id
                FROM password_recovery_tokens
                WHERE token_hash = %s
                  AND used_at IS NULL
                  AND expires_at >= UTC_TIMESTAMP()
                LIMIT 1
            """, (token_hash,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Token inválido o expirado")

            usuario = Usuario(id=row['usuario_id'])
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

