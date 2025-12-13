# Plan: Recuperación de contraseñas

## Estado actual
- No existe flujo para que usuarios/administradores recuperen contraseñas.
- Superadmin tampoco tiene botón de recuperación.

## Estado final
- Endpoint y lógica que permite solicitar recuperación para usuario/admin generando token temporal y enviándolo al email del admin de su tenant.
- Endpoint separado (o mismo) que permita a admin recuperar con superadmin mediante token envíado a email superadmin.
- Frontend muestra formularios: "Recuperar contraseña" (correo/admin) y "Superadmin restablece una cuenta".

## Archivos a modificar
- `backend/src/services/authentication_service.py` (nuevo/mismos)
- `backend/src/controllers/auth_controller.py`
- `backend/src/utils/email.py` (si no existe crear)
- `backend/src/routes/auth_routes.py`
- `backend/src/models/usuario.py` (si requiere campos)
- `frontend/src/views/public/RecuperarPassword.vue`
- `frontend/src/components/RecuperarPasswordForm.vue`
- `frontend/src/services/api.js`

## Lista de tareas
1. Implementar endpoint `/api/usuarios/recovery/request` que valide email, genere token (hash) y lo guarda en DB con expiración, asociado a tenant/admin.
2. Endpoint `/api/usuarios/recovery/confirm` para cambiar contraseña usando token.
3. Endpoint especial `/api/usuarios/recovery/admin` solo super admin (token superadmin) o similar.
4. Añadir servicios de email/mailing placeholder que imprimen token.
5. Frontend: nuevo componente para solicitar recuperación y otro para ingresar token + nueva contraseña.
6. Actualizar `authService` y vistas login para mostrar enlace.

