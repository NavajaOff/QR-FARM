import threading
import subprocess
from app import app

def run_backend():
    """Ejecuta el backend Flask en modo no debug."""
    app.run(debug=False, host="0.0.0.0", port=5000)

def run_frontend():
    """Ejecuta el servidor del frontend Vue."""
    subprocess.run(["npm.cmd", "run", "dev"], cwd="../frontend")

if __name__ == "__main__":
    print("Iniciando backend y frontend...")
    thread_backend = threading.Thread(target=run_backend)
    thread_frontend = threading.Thread(target=run_frontend)

    thread_backend.start()
    thread_frontend.start()

    thread_backend.join()
    thread_frontend.join()