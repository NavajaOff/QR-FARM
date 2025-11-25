"""Utilidad para inicializar el super_admin desde variables de entorno."""
import os
from typing import Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv
from ..database.db import get_connection
from passlib.hash import bcrypt


def _cargar_env():
    """Carga el archivo .env desde la raíz del proyecto."""
    # Intentar múltiples rutas posibles
    posibles_rutas = [
        Path(__file__).parent.parent.parent.parent / '.env',  # Desde backend/src/utils/ a raíz
        Path(__file__).parent.parent.parent / '.env',  # Desde backend/src/ a raíz (si .env está en backend/)
    ]
    
    for env_path in posibles_rutas:
        if env_path.exists():
            # Leer el archivo para debug
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    # Buscar las variables en el contenido
                    tiene_email = 'ROOT_SUPER_ADMIN_EMAIL' in contenido
                    tiene_password = 'ROOT_SUPER_ADMIN_PASSWORD' in contenido
                    print(f"📁 Archivo .env encontrado: {env_path}")
                    print(f"   - ROOT_SUPER_ADMIN_EMAIL presente: {'✅' if tiene_email else '❌'}")
                    print(f"   - ROOT_SUPER_ADMIN_PASSWORD presente: {'✅' if tiene_password else '❌'}")
                    
                    # Mostrar líneas que contienen ROOT_SUPER (sin mostrar valores completos)
                    lineas_root = [line.strip() for line in contenido.split('\n') 
                                  if 'ROOT_SUPER' in line and not line.strip().startswith('#')]
                    if lineas_root:
                        print(f"   - Líneas encontradas con ROOT_SUPER: {len(lineas_root)}")
                        for linea in lineas_root[:3]:  # Mostrar máximo 3 líneas
                            # Ocultar el valor después del =
                            if '=' in linea:
                                var_name = linea.split('=')[0].strip()
                                print(f"     → {var_name}=[VALOR_OCULTO]")
            except Exception as e:
                print(f"   ⚠️  Error al leer .env: {e}")
            
            # Cargar las variables
            resultado = load_dotenv(dotenv_path=env_path, override=True)
            print(f"   - load_dotenv resultado: {'✅ Cargado' if resultado else '⚠️  No se cargaron variables'}")
            return True
    
    # Si no se encuentra, buscar desde el directorio actual hacia arriba
    current = Path(__file__).resolve()
    while current.parent != current:
        env_file = current.parent / '.env'
        if env_file.exists():
            load_dotenv(dotenv_path=env_file, override=True)
            print(f"📁 Archivo .env cargado desde: {env_file}")
            return True
        current = current.parent
    
    print("⚠️  No se encontró el archivo .env")
    return False


def obtener_rol_super_admin_id() -> Optional[int]:
    """Obtiene el ID del rol super_admin."""
    conn = get_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM roles WHERE rol = 'super_admin'")
        rol = cursor.fetchone()
        return rol['id'] if rol else None
    finally:
        cursor.close()
        conn.close()


def existe_super_admin(email: str) -> bool:
    """Verifica si ya existe un super_admin con el email dado."""
    conn = get_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
            JOIN roles r ON u.id_rol = r.id
            WHERE r.rol = 'super_admin' AND p.email = %s
        """, (email,))
        result = cursor.fetchone()
        return result['count'] > 0 if result else False
    finally:
        cursor.close()
        conn.close()


def crear_super_admin_desde_env() -> Tuple[bool, str]:
    """
    Crea el super_admin desde variables de entorno.
    Retorna (éxito, mensaje)
    """
    # Cargar .env antes de leer las variables
    _cargar_env()
    
    # Obtener variables de entorno
    email = os.getenv('ROOT_SUPER_ADMIN_EMAIL')
    password = os.getenv('ROOT_SUPER_ADMIN_PASSWORD')
    nombre = os.getenv('ROOT_SUPER_ADMIN_NOMBRE', 'Super Administrador')
    
    # Debug: mostrar qué variables se encontraron
    print(f"🔍 Debug - ROOT_SUPER_ADMIN_EMAIL: {'✅ Configurado' if email else '❌ No encontrado'}")
    print(f"🔍 Debug - ROOT_SUPER_ADMIN_PASSWORD: {'✅ Configurado' if password else '❌ No encontrado'}")
    
    # Debug adicional: mostrar todas las variables que empiezan con ROOT_SUPER
    todas_vars = {k: v for k, v in os.environ.items() if k.startswith('ROOT_SUPER')}
    if todas_vars:
        print(f"🔍 Variables ROOT_SUPER encontradas en os.environ: {list(todas_vars.keys())}")
    else:
        print(f"🔍 No hay variables ROOT_SUPER en os.environ")
    
    if not email or not password:
        return False, "Variables ROOT_SUPER_ADMIN_EMAIL y ROOT_SUPER_ADMIN_PASSWORD no configuradas en .env"
    
    # Verificar si ya existe
    if existe_super_admin(email):
        return True, f"Super admin con email {email} ya existe"
    
    # Obtener ID del rol super_admin
    rol_id = obtener_rol_super_admin_id()
    if not rol_id:
        return False, "El rol 'super_admin' no existe en la base de datos. Ejecuta las migraciones primero."
    
    conn = get_connection()
    if conn is None:
        return False, "No se pudo conectar a la base de datos"
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Parsear nombre
        partes = nombre.split()
        primer_nombre = partes[0]
        primer_apellido = partes[-1] if len(partes) > 1 else ""
        segundo_nombre = ' '.join(partes[1:-1]) if len(partes) > 2 else None
        segundo_apellido = None
        
        # Hashear contraseña
        password_hash = bcrypt.hash(password)
        
        # Iniciar transacción
        conn.start_transaction()
        
        # Crear persona
        cursor.execute("""
            INSERT INTO personas (
                id_rol, primer_nombre, segundo_nombre, 
                primer_apellido, segundo_apellido, email, tenant_id, fecha_creacion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (rol_id, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, email, None))
        
        persona_id = cursor.lastrowid
        
        # Crear usuario
        cursor.execute("""
            INSERT INTO usuarios (
                id_persona, id_rol, contrasena, estado, tenant_id
            ) VALUES (%s, %s, %s, %s, %s)
        """, (persona_id, rol_id, password_hash, 'activo', None))
        
        conn.commit()
        
        return True, f"Super admin creado exitosamente: {email}"
        
    except Exception as e:
        conn.rollback()
        return False, f"Error al crear super admin: {str(e)}"
    finally:
        cursor.close()
        conn.close()


def inicializar_super_admin() -> bool:
    """
    Inicializa el super_admin si no existe.
    Se ejecuta automáticamente al iniciar la aplicación.
    """
    try:
        exito, mensaje = crear_super_admin_desde_env()
        if exito:
            print(f"✅ {mensaje}")
        else:
            print(f"⚠️  {mensaje}")
        return exito
    except Exception as e:
        print(f"❌ Error al inicializar super admin: {e}")
        return False

