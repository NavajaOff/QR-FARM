#!/usr/bin/env python3
"""
Backend Flask para QR Farm
Servidor REST API con autenticación JWT
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
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

# Cargar variables de entorno desde la raíz del proyecto
import os
from pathlib import Path

# Buscar el archivo .env en la raíz del proyecto
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'qr-farm-secret-key-2024')
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'

# Configuración de Flask-Migrate
from src.database.db import ConexionBaseDatos
# Para Flask-Migrate necesitamos SQLAlchemy, pero como usamos MySQL Connector,
# crearemos una configuración básica
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL',
    f"mysql+mysqlconnector://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'gestion_ganadera')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar Flask-Migrate (aunque no usaremos SQLAlchemy directamente)
migrate = Migrate(app, directory='src/database/migrations')

# Inicializar SocketIO para actualizaciones en tiempo real
ALLOWED_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

socketio = SocketIO(app, cors_allowed_origins=ALLOWED_CORS_ORIGINS)

# Importar comandos de Flask-Migrate para que estén disponibles en la CLI
from flask_migrate import init, migrate, upgrade, revision

# Configuración CORS completa para permitir peticiones desde el frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_CORS_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"]
    }
})

# Middleware para logging de peticiones
@app.before_request
def log_request_info():
    print(f"PETICION: {request.method} {request.url}")

def generate_token(user_id, email, role):
    """Genera un token JWT para el usuario"""
    import datetime
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificación de salud del servidor"""
    return jsonify({
        "status": "ok",
        "message": "Servidor activo"
    }), 200

@app.route('/api/usuarios/', methods=['GET'])
def obtener_usuarios():
    """Endpoint para obtener lista de usuarios desde la base de datos"""
    try:
        print("Obteniendo lista de usuarios desde la base de datos...")

        usuarios = UsuarioService.obtener_todos_usuarios(incluir_inactivos=True)

        # Convertir a formato compatible con el frontend
        usuarios_data = []
        for usuario in usuarios:
            usuarios_data.append({
                "id": usuario.id,
                "nombre": f"{usuario.persona.primer_nombre} {usuario.persona.primer_apellido}",
                "email": usuario.persona.email,
                "rol": usuario.rol.rol if usuario.rol else "user",
                "estado": usuario.estado.value if hasattr(usuario.estado, 'value') else str(usuario.estado)
            })

        print(f"Enviando {len(usuarios_data)} usuarios desde la base de datos")

        return jsonify({
            "status": "success",
            "message": "Usuarios obtenidos exitosamente",
            "data": usuarios_data
        }), 200

    except Exception as e:
        print(f"Error al obtener usuarios: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Error interno del servidor"
        }), 500



@app.route('/api/usuarios/login', methods=['POST'])
def usuarios_login():
    """Endpoint de autenticación de usuarios"""
    try:
        print("Procesando login...")

        # Obtener datos JSON del request
        data = request.get_json()

        if not data:
            print("ERROR: No se recibieron datos JSON")
            return jsonify({
                "status": "error",
                "message": "Se requieren datos JSON"
            }), 400

        email = data.get('email')
        password = data.get('password')

        print(f"Datos recibidos - Email: {email}")

        # Validar que se proporcionaron email y password
        if not email or not password:
            print("ERROR: Email o password faltantes")
            return jsonify({
                "status": "error",
                "message": "Email y contraseña son requeridos"
            }), 400

        # Consultar usuario en la base de datos real
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # Consulta que une las tres tablas: usuarios, personas y roles
            query = """
                SELECT
                    u.id as usuario_id,
                    u.contrasena,
                    u.estado,
                    p.email,
                    r.rol AS rol
                FROM usuarios u
                INNER JOIN personas p ON u.id_persona = p.id
                INNER JOIN roles r ON u.id_rol = r.id
                WHERE p.email = %s AND u.estado = 'activo'
            """

            cursor.execute(query, (email,))
            result = cursor.fetchone()

            # Verificar contraseña con hash o sin hash (para compatibilidad)
            password_valid = False
            if result:
                # Primero intentar verificar como hash
                try:
                    password_valid = bcrypt.verify(password, result['contrasena'])
                except:
                    # Si falla, comparar directamente (para usuarios antiguos)
                    password_valid = (result['contrasena'] == password)

            if result and password_valid:
                print(f"Usuario encontrado: {result['email']} - Rol: {result['rol']}")

                # Generar token JWT
                token = generate_token(result['usuario_id'], result['email'], result['rol'])

                print("Login exitoso - Token generado")

                return jsonify({
                    "status": "success",
                    "message": "Inicio de sesión exitoso",
                    "token": token,
                    "rol": result['rol']
                }), 200
            else:
                print("Credenciales invalidas")
                return jsonify({
                    "status": "error",
                    "message": "Credenciales inválidas"
                }), 401

        except Exception as db_error:
            print(f"Error de base de datos: {str(db_error)}")
            return jsonify({
                "status": "error",
                "message": "Error de conexión a la base de datos"
            }), 500
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    except Exception as e:
        print(f"Error en login: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Error interno del servidor"
        }), 500

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
        return jsonify({"error": "Error interno del servidor"}), 500

# Registrar blueprints
app.register_blueprint(potrero_bp, url_prefix='/api/potreros')
app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')
app.register_blueprint(animal_bp, url_prefix='/api/animales')
app.register_blueprint(vacunacion_bp, url_prefix='/api/vacunaciones')
app.register_blueprint(reporte_bp, url_prefix='/api/reportes')


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

def crear_usuario_admin(app):
    """Crea el usuario administrador desde las variables de entorno"""
    with app.app_context():
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if not admin_email or not admin_password:
            print("ADVERTENCIA: Faltan ADMIN_EMAIL o ADMIN_PASSWORD en .env")
            return

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # Verificar si ya existe un usuario admin
            query_check = """
                SELECT p.id, p.email
                FROM personas p
                INNER JOIN usuarios u ON u.id_persona = p.id
                WHERE u.id_rol = 1
                LIMIT 1
            """
            cursor.execute(query_check)
            admin_existente = cursor.fetchone()

            if not admin_existente:
                # Crear persona para el admin
                insert_persona = """
                    INSERT INTO personas (id_rol, primer_nombre, primer_apellido, email, fecha_creacion)
                    VALUES (1, 'Administrador', 'Sistema', %s, NOW())
                """
                cursor.execute(insert_persona, (admin_email,))
                persona_id = cursor.lastrowid

                # Crear usuario admin con contraseña hasheada
                password_hash = bcrypt.hash(admin_password)
                insert_usuario = """
                    INSERT INTO usuarios (id_persona, id_rol, contrasena, estado)
                    VALUES (%s, 1, %s, 'activo')
                """
                cursor.execute(insert_usuario, (persona_id, password_hash))
                
                conn.commit()
                print(f"[OK] Usuario admin creado correctamente: {admin_email}")
                print(f"     Contrasena: {admin_password} (desde .env)")
            else:
                print(f"[INFO] Usuario admin ya existe: {admin_existente['email']}")

        except Exception as e:
            print(f"[ERROR] Error al crear usuario admin: {str(e)}")
            if conn:
                conn.rollback()
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

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
        print("              Usando valores por defecto")
    
    # Crear usuario admin si no existe
    crear_usuario_admin(app)
    
    print("\nURLs disponibles:")
    print("  - URL: http://localhost:5000")
    print("  - Health check: http://localhost:5000/api/health")
    print("  - Login: http://localhost:5000/api/usuarios/login")
    print("  - WebSocket: ws://localhost:5000/socket.io")
    print("\nPresiona Ctrl+C para detener")
    print("=" * 60)

    # Iniciar el servidor Flask con SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
