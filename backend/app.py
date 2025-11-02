#!/usr/bin/env python3
"""
Backend Flask para QR Farm
Servidor REST API con autenticación JWT
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import jwt
import datetime
import os
from src.database.db import get_connection
from src.services.usuario_service import UsuarioService
from src.services.animal_service import GanadoService
from src.services.potrero_service import PotreroService
from src.routes.potrero_routes import potrero_bp
from src.routes.usuario_routes import usuario_bp
from src.routes.animal_routes import animal_bp

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'qr-farm-secret-key-2024'

# Configuración CORS completa para permitir peticiones desde el frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"],
        "allow_credentials": True
    }
})

# Middleware para logging de peticiones
@app.before_request
def log_request_info():
    print(f"PETICION: {request.method} {request.url}")

def generate_token(email, role):
    """Genera un token JWT para el usuario"""
    import datetime
    payload = {
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

        usuarios = UsuarioService.obtener_todos_usuarios()

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

@app.route('/api/ganados/', methods=['GET'])
def obtener_ganados():
    """Endpoint para obtener lista de ganado desde la base de datos"""
    try:
        print("Obteniendo lista de ganado desde la base de datos...")

        ganados = GanadoService.obtener_todos_ganados()

        # Convertir a formato compatible con el frontend
        ganados_data = []
        for ganado in ganados:
            # Calcular edad aproximada si hay fecha de nacimiento
            edad = None
            if ganado.fecha_nacimiento:
                from datetime import date
                today = date.today()
                edad = today.year - ganado.fecha_nacimiento.year - ((today.month, today.day) < (ganado.fecha_nacimiento.month, ganado.fecha_nacimiento.day))

            # Obtener estado desde la tabla estado_ganado
            estado_tipo = getattr(ganado, 'estado_tipo', None)
            if not estado_tipo and ganado.id_estado:
                # Buscar el estado en la tabla estado_ganado si no está en el objeto
                try:
                    conn_temp = get_connection()
                    cursor_temp = conn_temp.cursor(dictionary=True)
                    cursor_temp.execute("SELECT tipo_estado FROM estado_ganado WHERE id = %s", (ganado.id_estado,))
                    estado_result = cursor_temp.fetchone()
                    if estado_result:
                        estado_tipo = estado_result['tipo_estado']
                    cursor_temp.close()
                    conn_temp.close()
                except Exception as e:
                    print(f"Error obteniendo estado del ganado: {e}")

            ganados_data.append({
                "id": ganado.id,
                "nombre": ganado.nombre,
                "raza": ganado.raza,
                "edad": edad,
                "peso": float(ganado.peso) if ganado.peso else None,
                "estado": estado_tipo or ganado.estado.value if hasattr(ganado.estado, 'value') else str(ganado.estado),
                "estado_tipo": estado_tipo,
                "id_estado": getattr(ganado, 'id_estado', None) or ganado.id_estado if hasattr(ganado, 'id_estado') else None,
                "id_potrero": ganado.id_potrero,
                "id_persona": ganado.id_persona,
                "codigo_qr": ganado.codigo_qr,
                "fecha_nacimiento": ganado.fecha_nacimiento.isoformat() if ganado.fecha_nacimiento else None,
                "sexo": ganado.sexo.value if hasattr(ganado.sexo, 'value') else str(ganado.sexo)
            })

        print(f"Enviando {len(ganados_data)} animales desde la base de datos")

        return jsonify({
            "status": "success",
            "message": "Ganado obtenido exitosamente",
            "data": ganados_data
        }), 200

    except Exception as e:
        print(f"Error al obtener ganado: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": "Error interno del servidor"
        }), 500

@app.route('/api/potreros/', methods=['GET'])
def obtener_potreros():
    """Endpoint para obtener lista de potreros desde la base de datos"""
    try:
        print("Obteniendo lista de potreros desde la base de datos...")

        # Realizar consulta directa a la base de datos
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Consulta para obtener potreros con información del responsable
        query = """
            SELECT
                p.id,
                p.nombre,
                p.area,
                p.capacidad,
                p.ocupacion,
                p.hectareas,
                p.estado,
                p.fecha_ultimo_uso,
                p.ultima_limpieza,
                p.proxima_limpieza,
                p.descripcion,
                p.id_tipo_pasto,
                p.responsable_persona_id,
                tp.tipo_pasto,
                CONCAT(per.primer_nombre, ' ', COALESCE(per.segundo_nombre, ''), ' ', per.primer_apellido, ' ', COALESCE(per.segundo_apellido, '')) as responsable
            FROM potrero p
            LEFT JOIN tipo_pasto tp ON p.id_tipo_pasto = tp.id
            LEFT JOIN personas per ON p.responsable_persona_id = per.id
            ORDER BY p.id DESC
        """

        cursor.execute(query)
        potreros = cursor.fetchall()

        print(f"Enviando {len(potreros)} potreros desde la base de datos")

        return jsonify({
            "message": "Potreros obtenidos exitosamente",
            "data": potreros
        }), 200

    except Exception as e:
        print(f"Error al obtener potreros: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Error interno del servidor"
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

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

            if result and result['contrasena'] == password:
                print(f"Usuario encontrado: {result['email']} - Rol: {result['rol']}")

                # Generar token JWT
                token = generate_token(result['email'], result['rol'])

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

# Endpoint adicional para estados de ganado
@app.route('/api/animales/estados-ganado', methods=['GET'])
def obtener_estados_ganado():
    """Endpoint para obtener estados de ganado"""
    try:
        from src.services.animal_service import GanadoService
        estados = GanadoService.obtener_estados_ganado()
        return jsonify({
            "success": True,
            "data": estados
        }), 200
    except Exception as e:
        print(f"Error obteniendo estados de ganado: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500

if __name__ == '__main__':
    print("Iniciando servidor QR Farm Backend...")
    print("URL: http://localhost:5000")
    print("Health check: http://localhost:5000/api/health")
    print("Login: http://localhost:5000/api/login")
    print("Presiona Ctrl+C para detener")

    # Ejecutar verificación automática después de iniciar el servidor
    print("\nVerificacion automatica se ejecutara despues de iniciar el servidor\n")

    # Iniciar el servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=True)
