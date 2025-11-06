import threading
import subprocess
import socket
import os
from pathlib import Path
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
    print("[BACKEND] Iniciando servidor Flask en http://localhost:5000")
    app.run(debug=False, host="0.0.0.0", port=5000)

def run_frontend():
    """Ejecuta el servidor del frontend Vue."""
    import time
    time.sleep(2)  # Esperar 2 segundos para asegurar que el backend esté listo

    # Encontrar la ruta correcta del frontend
    backend_dir = Path(__file__).parent
    frontend_dir = backend_dir.parent / "frontend"
    
    if not frontend_dir.exists():
        print(f"[ERROR] No se encontró el directorio frontend en: {frontend_dir}")
        return
    
    # Encontrar un puerto libre
    free_port = find_free_port()
    print(f"[FRONTEND] Usando puerto {free_port} para el frontend")
    print(f"[FRONTEND] Directorio: {frontend_dir}")

    # Ejecutar con el puerto específico
    env = os.environ.copy()
    env['PORT'] = str(free_port)
    
    try:
        # En Windows usar npm.cmd, en otros sistemas usar npm
        npm_command = "npm.cmd" if os.name == 'nt' else "npm"
        subprocess.run([npm_command, "run", "dev", "--", "--port", str(free_port)],
                      cwd=str(frontend_dir),
                      env=env,
                      check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error al ejecutar el frontend: {e}")
    except FileNotFoundError:
        print("[ERROR] npm no está instalado o no está en el PATH")

if __name__ == "__main__":
    print("=" * 60)
    print("INICIANDO SISTEMA QR-FARM COMPLETO")
    print("=" * 60)
    print("[INFO] Iniciando backend y frontend...")
    
    thread_backend = threading.Thread(target=run_backend)
    thread_frontend = threading.Thread(target=run_frontend)

    thread_backend.start()
    thread_frontend.start()

    try:
        thread_backend.join()
        thread_frontend.join()
    except KeyboardInterrupt:
        print("\n[INFO] Deteniendo servidores...")
        print("=" * 60)