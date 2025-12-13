#!/usr/bin/env python3
"""
Backend Flask para QR Farm
Servidor REST API con autenticación JWT
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_migrate import Migrate
from flask_socketio import SocketIO
import jwt
import datetime
import os
from dotenv import load_dotenv
from passlib.hash import bcrypt
from src.database.db import get_connection
from src.services.usuario_service import UsuarioService
from src.services.animal_service import GanadoService
from src.services.potrero_service import PotreroService
from src.services.vacunacion_service import VacunacionService
from src.cli.secure_seed import COMMANDS as SECURE_SEED_COMMANDS
from src.routes.potrero_routes import potrero_bp
from src.routes.usuario_routes import usuario_bp
from src.routes.animal_routes import animal_bp
from src.routes.vacunacion_routes import vacunacion_bp
from src.routes.reporte_routes import reporte_bp
from src.routes.tenant_routes import tenant_bp
from src.routes.notification_routes import notification_bp
from src.utils.init_super_admin import inicializar_super_admin
from src.utils.auth import token_required
from src.utils.tenant import get_current_tenant_id, _es_super_admin_usuario
from flask import g
# Constantes para mensajes de error
INTERNAL_SERVER_ERROR_MSG = "Error interno del servidor"

# Cargar variables de entorno desde la raíz del proyecto
import os
from pathlib import Path

# Buscar el archivo .env en la raíz del proyecto
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


def _require_env(nombre_variable: str) -> str:
    """Obtiene una variable de entorno obligatoria."""
    valor = os.getenv(nombre_variable)
    if valor is None:
        raise RuntimeError(f"Variable de entorno obligatoria no configurada: {nombre_variable}")
    return valor


def _build_sqlalchemy_uri() -> str:
    """Construye la URI de SQLAlchemy a partir de variables de entorno."""
    existing_url = os.getenv('DATABASE_URL')
    if existing_url:
        return existing_url
    db_user = _require_env('DB_USER')
    db_password = _require_env('DB_PASSWORD')
    db_host = _require_env('DB_HOST')
    db_port = _require_env('DB_PORT')
    db_name = _require_env('DB_NAME')
    return (
        f"mysql+mysqlconnector://{db_user}:{db_password}@"
        f"{db_host}:{db_port}/{db_name}"
    )


# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = _require_env('SECRET_KEY')
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV')
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'

# Configuración de Flask-Migrate
from src.database.db import ConexionBaseDatos
# Para Flask-Migrate necesitamos SQLAlchemy, pero como usamos MySQL Connector,
# crearemos una configuración básica
app.config['SQLALCHEMY_DATABASE_URI'] = _build_sqlalchemy_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar Flask-Migrate (aunque no usaremos SQLAlchemy directamente)
migrate = Migrate(app, directory='src/database/migrations')

# Inicializar SocketIO para actualizaciones en tiempo real
# CORS origins desde variables de entorno (obligatorio para producción)
_cors_origins_env = os.getenv('CORS_ORIGINS', '')
_flask_env = os.getenv('FLASK_ENV', 'production')

if _cors_origins_env:
    # Si hay variable de entorno, usar esos valores (separados por coma)
    ALLOWED_CORS_ORIGINS = [origin.strip() for origin in _cors_origins_env.split(',')]
elif _flask_env == 'development':
    # Solo en desarrollo: valores por defecto para facilitar desarrollo local
    # En producción debe configurarse explícitamente
    ALLOWED_CORS_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:80",
        "http://127.0.0.1:80",
        "http://localhost",
        "http://127.0.0.1"
    ]
    print("⚠️  ADVERTENCIA: Usando valores por defecto de CORS para desarrollo. "
          "Configure CORS_ORIGINS en producción.")
else:
    # En producción: sin valores por defecto - debe configurarse explícitamente
    raise RuntimeError(
        "CORS_ORIGINS debe estar configurado en variables de entorno para producción. "
        "Ejemplo: CORS_ORIGINS=http://localhost:5174,http://localhost:5173"
    )

socketio = SocketIO(app, cors_allowed_origins=ALLOWED_CORS_ORIGINS)

# Importar comandos de Flask-Migrate para que estén disponibles en la CLI
from flask_migrate import init, migrate, upgrade, revision

# Configuración CORS completa para permitir peticiones desde el frontend
# Aplicar CORS a todas las rutas, no solo /api/*
CORS(app, 
    resources={
        r"/*": {
            "origins": ALLOWED_CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "Authorization"]
        }
    },
    supports_credentials=True
)


@app.route('/api/ganado/<identifier>', methods=['GET', 'OPTIONS'])
@token_required
def obtener_ganado_detallado(identifier: str):
    """
    Devuelve la ficha detallada de un ganado, incluida la información relacionada.
    
    Super admin puede acceder sin tenant (ver todos).
    Usuarios normales requieren tenant asignado.
    """
    if request.method == 'OPTIONS':
        return ('', 204)

    try:
        # Obtener tenant_id (puede ser None para super admin)
        is_super_admin = _es_super_admin_usuario()
        tenant_id = get_current_tenant_id(require_tenant=False)
        
        # Si no es super admin y no tiene tenant, denegar acceso
        if not is_super_admin and tenant_id is None:
            return jsonify({
                "success": False,
                "message": "Usuario sin tenant asignado. Acceso denegado."
            }), 403

        # Obtener detalle del ganado con filtro de tenant (None para super admin = ver todos)
        detalle = GanadoService.obtener_ganado_detallado(identifier, tenant_id_override=tenant_id)
        if not detalle:
            return jsonify({
                "success": False,
                "message": "Este QR no está registrado en la base de datos."
            }), 404

        return jsonify({
            "success": True,
            "data": detalle
        }), 200
    except Exception as error:
        print(f"Error obteniendo detalle de ganado {identifier}: {error}")
        return jsonify({
            "status": "error",
            "message": "Error interno del servidor"
        }), 500

# Middleware para logging de peticiones
@app.before_request
def log_request_info():
    print(f"PETICION: {request.method} {request.url}")

# Middleware para asegurar headers CORS en todas las respuestas
# Se ejecuta después de Flask-CORS para asegurar que los headers estén presentes
@app.after_request
def after_request(response):
    """Agregar headers CORS a todas las respuestas si no están ya presentes."""
    origin = request.headers.get('Origin')
    
    # Solo agregar headers si no están ya presentes (Flask-CORS puede haberlos agregado)
    if 'Access-Control-Allow-Origin' not in response.headers:
        if origin and origin in ALLOWED_CORS_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = origin
        elif origin:
            # En desarrollo, permitir cualquier origin
            response.headers['Access-Control-Allow-Origin'] = origin
        elif ALLOWED_CORS_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = ALLOWED_CORS_ORIGINS[0]
    
    # Asegurar otros headers importantes
    if 'Access-Control-Allow-Credentials' not in response.headers:
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    if 'Access-Control-Allow-Methods' not in response.headers:
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
    
    if 'Access-Control-Allow-Headers' not in response.headers:
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
    
    return response

def generate_token(user_id, email, role, tenant_id=None):
    """Genera un token JWT para el usuario"""
    import datetime
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    if tenant_id:
        payload['tenant_id'] = tenant_id
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def _validate_login_data(data):
    """Valida los datos de login"""
    if not data:
        return None, _create_error_response("Se requieren datos JSON"), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return None, _create_error_response("Email y contraseña son requeridos"), 400

    return {'email': email, 'password': password}, None, None

def _create_error_response(message):
    """Crea una respuesta de error estándar"""
    return jsonify({
        "status": "error",
        "message": message
    })

def _verify_password(stored_password, password):
    """Verifica la contraseña con diferentes métodos de hash"""
    try:
        if stored_password and stored_password.startswith('$2b$'):
            try:
                return bcrypt.verify(password, stored_password)
            except (AttributeError, Exception) as bcrypt_error:
                # Manejar error de bcrypt (versión incompatible)
                print(f"Advertencia al verificar hash bcrypt: {bcrypt_error}")
                # Fallback a comparación directa solo si no es hash bcrypt válido
                return stored_password == password
        else:
            # Para contraseñas sin hash (compatibilidad)
            return stored_password == password
    except Exception as hash_error:
        print(f"Error verificando hash: {hash_error}")
        # Fallback a comparación directa
        return stored_password == password

def _create_success_response(token, user_data):
    """Crea una respuesta de login exitoso"""
    return jsonify({
        "status": "success",
        "message": "Inicio de sesión exitoso",
        "token": token,
        "user": user_data
    }), 200

def _create_invalid_credentials_response():
    """Crea una respuesta de credenciales inválidas"""
    return jsonify({
        "status": "error",
        "message": "Credenciales inválidas"
    }), 401

def _create_db_error_response():
    """Crea una respuesta de error de base de datos"""
    return jsonify({
        "status": "error",
        "message": "Error de conexión a la base de datos"
    }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificación de salud del servidor"""
    return jsonify({
        "status": "ok",
        "message": "Servidor activo"
    }), 200

# Endpoint eliminado: usar el blueprint usuario_routes.py que tiene la lógica completa de tenant
# El endpoint correcto está en: usuario_bp.route('/', methods=['GET'])(token_required(UsuarioController.obtener_todos_usuarios))



def _query_user_by_email(email):
    """Consulta usuario por email en la base de datos"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            u.id as usuario_id,
            u.contrasena,
            u.estado,
            p.tenant_id,
            p.email,
            r.rol AS rol
        FROM usuarios u
        INNER JOIN personas p ON u.id_persona = p.id
        INNER JOIN roles r ON u.id_rol = r.id
        WHERE p.email = %s AND u.estado = 'activo'
    """

    cursor.execute(query, (email,))
    result = cursor.fetchone()

    cursor.close()
    if conn and hasattr(conn, 'is_connected') and conn.is_connected():
        conn.close()

    return result

def _process_login_success(result):
    """Procesa un login exitoso y retorna la respuesta"""
    print(f"Usuario encontrado: {result['email']} - Rol: {result['rol']}")

    tenant_id = result.get('tenant_id')
    token = generate_token(result['usuario_id'], result['email'], result['rol'], tenant_id)
    print("Login exitoso - Token generado")

    user_data = {
        "id": result['usuario_id'],
        "email": result['email'],
        "rol": result['rol']
    }
    if tenant_id:
        user_data['tenant_id'] = tenant_id

    return _create_success_response(token, user_data)

@app.route('/api/usuarios/login', methods=['POST'])
def usuarios_login():
    """Endpoint de autenticación de usuarios"""
    try:
        print("Procesando login...")

        # Validar datos del request
        login_data, error_response, status_code = _validate_login_data(request.get_json())
        if error_response:
            return error_response, status_code

        email = login_data['email']
        password = login_data['password']
        print(f"Datos recibidos - Email: {email}")

        # Consultar usuario en la base de datos
        try:
            result = _query_user_by_email(email)

            # Verificar credenciales
            if result and _verify_password(result['contrasena'], password):
                return _process_login_success(result)
            else:
                print("Credenciales invalidas")
                return _create_invalid_credentials_response()

        except Exception as db_error:
            print(f"Error de base de datos: {str(db_error)}")
            import traceback
            traceback.print_exc()
            return _create_db_error_response()

    except Exception as e:
        print(f"Error en login: {str(e)}")
        import traceback
        traceback.print_exc()
        return _create_error_response(INTERNAL_SERVER_ERROR_MSG), 500

# Endpoint para servir imágenes QR
@app.route('/api/qr/<filename>', methods=['GET'])
def get_qr_image(filename):
    """Endpoint para servir imágenes QR"""
    try:
        # Ruta relativa al directorio del script (backend)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        qr_path = os.path.join(script_dir, 'qr', filename)

        print(f"Buscando imagen QR en: {qr_path}")
        print(f"¿Existe el archivo?: {os.path.exists(qr_path)}")

        if os.path.exists(qr_path):
            return send_file(qr_path, mimetype='image/png')
        else:
            print(f"Imagen QR no encontrada: {qr_path}")
            return jsonify({"error": "Imagen QR no encontrada"}), 404
    except Exception as e:
        print(f"Error sirviendo imagen QR: {e}")
        return jsonify({"error": INTERNAL_SERVER_ERROR_MSG}), 500

# Registrar blueprints
app.register_blueprint(potrero_bp, url_prefix='/api/potreros')
app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')
app.register_blueprint(animal_bp, url_prefix='/api/animales')
app.register_blueprint(vacunacion_bp, url_prefix='/api/vacunaciones')
app.register_blueprint(reporte_bp, url_prefix='/api/reportes')
app.register_blueprint(tenant_bp, url_prefix='/api/tenants')
app.register_blueprint(notification_bp, url_prefix='/api/notificaciones')

# Inicializar super_admin desde variables de entorno (solo si la BD está disponible)
print("🔐 Inicializando super_admin desde variables de entorno...")
try:
    # Verificar que la BD esté disponible antes de inicializar
    test_conn = get_connection()
    if test_conn:
        test_conn.close()
        inicializar_super_admin()
    else:
        print("⚠️  Base de datos no disponible. El super_admin se creará cuando la BD esté disponible.")
except Exception as e:
    print(f"⚠️  No se pudo inicializar super_admin: {e}")

# Eventos SocketIO para actualizaciones en tiempo real
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado para actualizaciones en tiempo real')

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

# Función para emitir actualizaciones a todos los clientes conectados
def emit_update(event_type, data):
    """Emite actualizaciones en tiempo real a todos los clientes conectados."""
    socketio.emit(event_type, data)
    print(f"Actualización emitida: {event_type}")

# Nota: La creación de usuarios admin (tenant_admin) se realiza cuando el super_admin
# crea un nuevo tenant. Solo se crea automáticamente el super_admin desde variables
# de entorno mediante inicializar_super_admin()

import click
from flask.cli import with_appcontext
import secrets

@app.cli.command("generate-secret-key")
@with_appcontext
def generate_secret_key():
    """Genera una SECRET_KEY aleatoria y la guarda en el archivo .env"""
    key = secrets.token_hex(32)
    env_file = Path(__file__).parent.parent / '.env'

    if not env_file.exists():
        print("[ERROR] No se encontró el archivo .env")
        return

    # Leer contenido actual del .env
    with open(env_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Reemplazar o agregar la línea de SECRET_KEY
    new_lines = []
    found = False
    for line in lines:
        if line.strip().startswith("SECRET_KEY="):
            new_lines.append(f"SECRET_KEY={key}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"\nSECRET_KEY={key}\n")

    # Escribir los cambios
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"[OK] Nueva SECRET_KEY generada y guardada en .env:")
    print(key)


for command in SECURE_SEED_COMMANDS:
    app.cli.add_command(command)



if __name__ == '__main__':
    print("=" * 60)
    print("INICIANDO SERVIDOR QR FARM BACKEND CON WEBSOCKETS...")
    print("=" * 60)
    
    # Verificar archivo .env
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        print(f"[OK] Archivo .env encontrado en: {env_file}")
    else:
        print(f"[ADVERTENCIA] No se encontro archivo .env en: {env_file}")
        print("              Configura las variables de entorno requeridas antes de iniciar el servicio")
    
    # Nota: El super_admin se crea automáticamente mediante inicializar_super_admin()
    # que se ejecuta al cargar la aplicación (línea 365)
    
    # Obtener host y puerto desde variables de entorno o usar valores por defecto
    backend_host = os.getenv('BACKEND_HOST', '0.0.0.0')
    backend_port = os.getenv('BACKEND_PORT', '5000')
    backend_url = f"http://{backend_host}:{backend_port}" if backend_host != '0.0.0.0' else f"http://localhost:{backend_port}"
    
    print("\nURLs disponibles:")
    print(f"  - URL: {backend_url}")
    print(f"  - Health check: {backend_url}/api/health")
    print(f"  - Login: {backend_url}/api/usuarios/login")
    print(f"  - WebSocket: ws://{backend_host}:{backend_port}/socket.io")
    print("\nPresiona Ctrl+C para detener")
    print("=" * 60)

    # Iniciar el servidor Flask con SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=app.config['DEBUG'], allow_unsafe_werkzeug=True)
