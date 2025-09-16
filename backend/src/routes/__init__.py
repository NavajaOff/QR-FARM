from flask import Flask

def create_app():
    app = Flask(__name__)
    # Aquí se registrarán las rutas
    return app
