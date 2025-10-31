"""Routes module."""
from flask import Flask
from src.database.db import init_db
from src.routes.potrero_routes import potrero_bp
from src.routes.usuario_routes import usuario_bp
from src.routes.animal_routes import animal_bp
from flask_cors import CORS

def create_app(config_class=None):
    """Create Flask application."""
    app = Flask(__name__)

    # Load config
    if config_class is None:
        # Load default config
        app.config.from_object('src.config.Config')
    else:
        # Load provided config
        app.config.from_object(config_class)

    # Initialize database
    init_db()

    # Enable CORS con configuración específica para desarrollo
    from flask_cors import CORS

    CORS(app, resources={r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:5174"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5174')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response

    # Register blueprints
    app.register_blueprint(potrero_bp, url_prefix='/api/potreros')
    app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')
    app.register_blueprint(animal_bp, url_prefix='/api/animales', name='animal_compat')

    app.register_blueprint(animal_bp, url_prefix='/api/animales')

    # Add favicon route to prevent 404 errors
    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        print("INFO: Health check solicitado")
        from datetime import datetime
        from flask import jsonify
        return jsonify({
            'status': 'ok',
            'message': 'Backend QR Farm funcionando correctamente',
            'timestamp': datetime.now().isoformat()
        }), 200

    return app
