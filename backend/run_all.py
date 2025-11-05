import threading
import subprocess
import socket
from app import app

def find_free_port(start_port=5173):
    """Encuentra un puerto libre empezando desde start_port."""
    port = start_port
    while port < 6000:  # Límite superior razonable
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            port += 1
    raise RuntimeError("No se pudo encontrar un puerto libre")

def run_backend():
    """Ejecuta el backend Flask en modo no debug."""
    app.run(debug=False, host="0.0.0.0", port=5000)

def run_frontend():
    """Ejecuta el servidor del frontend Vue."""
    import time
    import os
    time.sleep(2)  # Esperar 2 segundos para asegurar que el backend esté listo

    # Encontrar un puerto libre
    free_port = find_free_port()
    print(f"Usando puerto {free_port} para el frontend")

    # Ejecutar con el puerto específico
    env = os.environ.copy()
    env['PORT'] = str(free_port)
    subprocess.run(["npm.cmd", "run", "dev", "--", "--port", str(free_port)], cwd="../frontend", env=env)

if __name__ == "__main__":
    print("Iniciando backend y frontend...")
    thread_backend = threading.Thread(target=run_backend)
    thread_frontend = threading.Thread(target=run_frontend)

    thread_backend.start()
    thread_frontend.start()

    thread_backend.join()
    thread_frontend.join()