# Configuración del Super Admin

## 📋 Resumen

El sistema **QR-FARM** ahora utiliza un sistema de super administrador único y seguro que:

- ✅ **Solo puede crearse desde variables de entorno** (no desde la API)
- ✅ **Se inicializa automáticamente** al iniciar el backend
- ✅ **Compartido para todo el equipo** (3 personas)
- ✅ **Bloquea cualquier intento** de crear super_admin desde la API

## 🔐 Configuración

### 1. Agregar variables al archivo `.env`

Agrega estas variables a tu archivo `.env` en la raíz del proyecto:

```env
# Super Admin Global (COMPARTIDO)
ROOT_SUPER_ADMIN_EMAIL=superadmin@qrfarm.com
ROOT_SUPER_ADMIN_PASSWORD=TuContrasenaMuySegura123!
ROOT_SUPER_ADMIN_NOMBRE=Super Administrador QR-Farm
```

### 2. El super_admin se crea automáticamente

Al iniciar el backend con `python app.py`, el sistema:

1. Verifica si ya existe un super_admin con ese email
2. Si no existe, lo crea automáticamente
3. Si ya existe, no hace nada (no lo sobrescribe)

## 🔒 Seguridad

### ¿Cómo funciona el bloqueo?

1. **En el Servicio de Usuarios** (`usuario_service.py`):
   - Bloquea la creación de usuarios con rol `super_admin`
   - Retorna error: "No se puede crear usuarios super_admin desde la API"

2. **En el Controlador** (`usuario_controller.py`):
   - Bloquea la asignación del rol `super_admin` al actualizar usuarios
   - Retorna error: "No se puede asignar el rol super_admin. Este rol solo se crea desde variables de entorno."

3. **Solo desde `.env`**:
   - El único lugar donde se puede definir el super_admin es en el archivo `.env`
   - Se crea automáticamente al iniciar la aplicación

## 📝 Notas Importantes

1. **Un solo super_admin**: Solo debe haber un super_admin en el sistema (el definido en `.env`)

2. **Compartido para el equipo**: Los 3 miembros del equipo usan las mismas credenciales definidas en `.env`

3. **No cambiar desde la UI**: No intentes cambiar el rol de un usuario a `super_admin` desde la interfaz, estará bloqueado

4. **Seguridad del `.env`**: 
   - Nunca subas el archivo `.env` al repositorio
   - Mantén las credenciales seguras
   - Cambia la contraseña después de la primera configuración

## 🔄 Flujo de Trabajo

1. Configurar variables en `.env`
2. Iniciar el backend: `python app.py`
3. El super_admin se crea automáticamente (si no existe)
4. Usar las credenciales para iniciar sesión

## ✅ Verificación

Para verificar que el super_admin se creó correctamente:

1. Inicia sesión con el email y password definidos en `.env`
2. Debes ver el badge "Super Admin" en la barra superior
3. Debes ver el menú "Tenants" en el sidebar
4. Puedes acceder a `/admin/gestionar-tenants`

---

**Última actualización**: Sistema de super_admin único desde variables de entorno

