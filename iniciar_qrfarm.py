#!/usr/bin/env python3
"""
Script principal para iniciar el proyecto QR Farm
Inicia automáticamente el backend Flask y el frontend Vue.js

Uso:
    python iniciar_qrfarm.py

O hacer el archivo ejecutable:
    chmod +x iniciar_qrfarm.py
    ./iniciar_qrfarm.py
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

# Configuración de colores para output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_banner():
    """Imprime el banner del proyecto"""
    banner = f"""
{Colors.BOLD}{Colors.GREEN}
================================================================
                     QR FARM - Sistema de Gestion Ganadera
================================================================
{Colors.END}
"""
    print(banner)

def check_requirements():
    """Verifica que las dependencias necesarias estén instaladas"""
    print(f"{Colors.BLUE}[INFO] Verificando dependencias...{Colors.END}")

    # Verificar Python
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"{Colors.RED}[ERROR] Se requiere Python 3.8 o superior{Colors.END}")
        return False
    print(f"{Colors.GREEN}[OK] Python {python_version.major}.{python_version.minor}.{python_version.micro}{Colors.END}")

    # Verificar Node.js y npm
    try:
        # Intentar diferentes formas de ejecutar node
        node_commands = [['node', '--version'], ['node.exe', '--version']]
        npm_commands = [['npm', '--version'], ['npm.cmd', '--version']]

        node_result = None
        npm_result = None

        for cmd in node_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    node_result = result
                    break
            except:
                continue

        for cmd in npm_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    npm_result = result
                    break
            except:
                continue

        if node_result and npm_result:
            print(f"{Colors.GREEN}[OK] Node.js {node_result.stdout.strip()} | npm {npm_result.stdout.strip()}{Colors.END}")
        else:
            print(f"{Colors.RED}[ERROR] Node.js o npm no están disponibles{Colors.END}")
            print(f"{Colors.YELLOW}[INFO] Verificando instalación manual...{Colors.END}")
            # Verificar si están en el sistema
            try:
                import shutil
                node_path = shutil.which('node')
                npm_path = shutil.which('npm')
                if node_path and npm_path:
                    print(f"{Colors.GREEN}[OK] Node.js encontrado en: {node_path}{Colors.END}")
                    print(f"{Colors.GREEN}[OK] npm encontrado en: {npm_path}{Colors.END}")
                    return True
                else:
                    print(f"{Colors.RED}[ERROR] Node.js/npm no encontrados en PATH del sistema{Colors.END}")
            except:
                pass
            return False
    except Exception as e:
        print(f"{Colors.RED}[ERROR] Error verificando Node.js: {e}{Colors.END}")
        return False

    return True

def setup_environment():
    """Configura las variables de entorno necesarias"""
    print(f"{Colors.BLUE}[INFO] Configurando entorno...{Colors.END}")

    # Crear .env para backend si no existe
    backend_env = Path("backend/.env")
    if not backend_env.exists():
        print(f"{Colors.YELLOW}[WARN] Creando archivo backend/.env...{Colors.END}")
        env_content = """# Configuración de la base de datos
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=gestion_ganadera

# Clave secreta para JWT (cambiar en producción)
SECRET_KEY=dev-secret-key-change-in-production

# Configuración del servidor
HOST=0.0.0.0
PORT=5000
DEBUG=True

# Configuración de CORS
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
"""
        backend_env.parent.mkdir(parents=True, exist_ok=True)
        backend_env.write_text(env_content)
        print(f"{Colors.GREEN}[OK] Archivo backend/.env creado{Colors.END}")

    # Crear .env para frontend si no existe
    frontend_env = Path("frontend/.env")
    if not frontend_env.exists():
        print(f"{Colors.YELLOW}[WARN] Creando archivo frontend/.env...{Colors.END}")
        env_content = """# Configuración de desarrollo
VUE_APP_API_BASE_URL=http://localhost:5000/api
VUE_APP_APP_NAME=QR Farm
VUE_APP_DEBUG=true

# Para producción, cambiar a:
# VUE_APP_API_BASE_URL=https://tu-dominio.com/api
# VUE_APP_APP_NAME=QR Farm
# VUE_APP_DEBUG=false
"""
        frontend_env.parent.mkdir(parents=True, exist_ok=True)
        frontend_env.write_text(env_content)
        print(f"{Colors.GREEN}[OK] Archivo frontend/.env creado{Colors.END}")

    # Crear config.js si no existe
    config_js = Path("frontend/public/config.js")
    if not config_js.exists():
        print(f"{Colors.YELLOW}[WARN] Creando archivo frontend/public/config.js...{Colors.END}")
        config_content = """// Configuración global para desarrollo
window.config = {
  API_BASE_URL: 'http://localhost:5000/api',
  APP_NAME: 'QR Farm',
  VERSION: '1.0.0',
  DEBUG: true,
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000
};
"""
        config_js.parent.mkdir(parents=True, exist_ok=True)
        config_js.write_text(config_content)
        print(f"{Colors.GREEN}[OK] Archivo frontend/public/config.js creado{Colors.END}")

def install_dependencies():
    """Instala las dependencias del proyecto"""
    print(f"{Colors.BLUE}[INFO] Instalando dependencias...{Colors.END}")

    # Instalar dependencias del backend
    print(f"{Colors.YELLOW}[INFO] Instalando dependencias del backend...{Colors.END}")
    backend_result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'],
                                  cwd=os.getcwd(), capture_output=True, text=True)

    if backend_result.returncode == 0:
        print(f"{Colors.GREEN}[OK] Dependencias del backend instaladas{Colors.END}")
    else:
        print(f"{Colors.RED}[ERROR] Error instalando dependencias del backend:{Colors.END}")
        print(backend_result.stderr)
        return False

    # Instalar dependencias del frontend
    print(f"{Colors.YELLOW}[INFO] Instalando dependencias del frontend...{Colors.END}")

    # Intentar diferentes comandos de npm para Windows
    npm_commands = [['npm', 'install'], ['npm.cmd', 'install']]

    frontend_result = None
    for cmd in npm_commands:
        try:
            result = subprocess.run(cmd, cwd='frontend', capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                frontend_result = result
                break
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}[WARN] Timeout en comando npm, intentando siguiente...{Colors.END}")
            continue
        except Exception as e:
            print(f"{Colors.YELLOW}[WARN] Error con comando {cmd[0]}: {e}, intentando siguiente...{Colors.END}")
            continue

    if frontend_result and frontend_result.returncode == 0:
        print(f"{Colors.GREEN}[OK] Dependencias del frontend instaladas{Colors.END}")
    else:
        print(f"{Colors.RED}[ERROR] Error instalando dependencias del frontend{Colors.END}")
        if frontend_result:
            print(f"stdout: {frontend_result.stdout}")
            print(f"stderr: {frontend_result.stderr}")
        return False

    return True

def start_backend():
    """Inicia el servidor backend"""
    print(f"{Colors.BLUE}[INFO] Iniciando backend Flask...{Colors.END}")

    try:
        # Cambiar al directorio backend
        os.chdir('backend')

        # Iniciar el servidor Flask
        process = subprocess.Popen([sys.executable, 'app.py'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 text=True,
                                 bufsize=1,
                                 universal_newlines=True)

        # Esperar a que el servidor esté listo
        time.sleep(3)

        # Verificar si el proceso sigue vivo
        if process.poll() is None:
            print(f"{Colors.GREEN}[OK] Backend iniciado correctamente en http://localhost:5000{Colors.END}")
            return process
        else:
            print(f"{Colors.RED}[ERROR] Error iniciando backend{Colors.END}")
            return None

    except Exception as e:
        print(f"{Colors.RED}[ERROR] Error iniciando backend: {e}{Colors.END}")
        return None
    finally:
        # Volver al directorio raíz
        os.chdir('..')

def start_frontend():
    """Inicia el servidor frontend"""
    print(f"{Colors.BLUE}[INFO] Iniciando frontend Vue.js...{Colors.END}")

    try:
        # Intentar diferentes comandos para npm en Windows
        npm_commands = [['npm', 'run', 'dev'], ['npm.cmd', 'run', 'dev']]

        process = None
        for cmd in npm_commands:
            try:
                process = subprocess.Popen(cmd,
                                         cwd='frontend',
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT,
                                         text=True,
                                         bufsize=1,
                                         universal_newlines=True)
                break
            except Exception as e:
                print(f"{Colors.YELLOW}[WARN] Error con comando {cmd[0]}: {e}, intentando siguiente...{Colors.END}")
                continue

        if not process:
            print(f"{Colors.RED}[ERROR] No se pudo ejecutar npm{Colors.END}")
            return None

        # Esperar a que el servidor esté listo (Vite tarda un poco más)
        time.sleep(8)

        # Verificar si el proceso sigue vivo
        if process.poll() is None:
            print(f"{Colors.GREEN}[OK] Frontend iniciado correctamente en http://localhost:5173{Colors.END}")
            return process
        else:
            print(f"{Colors.RED}[ERROR] Error iniciando frontend{Colors.END}")
            return None

    except Exception as e:
        print(f"{Colors.RED}[ERROR] Error iniciando frontend: {e}{Colors.END}")
        return None

def monitor_processes(backend_process, frontend_process):
    """Monitorea los procesos y maneja señales de terminación"""
    def signal_handler(signum, frame):
        print(f"\n{Colors.YELLOW}🛑 Recibida señal de terminación...{Colors.END}")

        # Terminar procesos hijos
        if backend_process and backend_process.poll() is None:
            print(f"{Colors.BLUE}Deteniendo backend...{Colors.END}")
            backend_process.terminate()
            backend_process.wait()

        if frontend_process and frontend_process.poll() is None:
            print(f"{Colors.BLUE}Deteniendo frontend...{Colors.END}")
            frontend_process.terminate()
            frontend_process.wait()

        print(f"{Colors.GREEN}👋 ¡Hasta luego!{Colors.END}")
        sys.exit(0)

    # Registrar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"\n{Colors.BOLD}{Colors.GREEN}[SUCCESS] Proyecto QR Farm iniciado exitosamente!{Colors.END}")
    print(f"{Colors.BLUE}[URL] Frontend: http://localhost:5173{Colors.END}")
    print(f"{Colors.BLUE}[URL] Backend:  http://localhost:5000{Colors.END}")
    print(f"{Colors.BLUE}[URL] API Docs:  http://localhost:5000/api{Colors.END}")
    print(f"{Colors.YELLOW}[INFO] Presiona Ctrl+C para detener todos los servicios{Colors.END}")

    # Mantener el script vivo
    try:
        while True:
            time.sleep(1)

            # Verificar si algún proceso murió
            if backend_process and backend_process.poll() is not None:
                print(f"{Colors.RED}❌ El backend se detuvo inesperadamente{Colors.END}")
                break

            if frontend_process and frontend_process.poll() is not None:
                print(f"{Colors.RED}❌ El frontend se detuvo inesperadamente{Colors.END}")
                break

    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

def main():
    """Función principal"""
    print_banner()

    # Verificar requisitos
    if not check_requirements():
        sys.exit(1)

    # Configurar entorno
    setup_environment()

    # Instalar dependencias
    if not install_dependencies():
        sys.exit(1)

    # Iniciar servicios
    backend_process = start_backend()
    if not backend_process:
        print(f"{Colors.RED}❌ No se pudo iniciar el backend. Abortando.{Colors.END}")
        sys.exit(1)

    frontend_process = start_frontend()
    if not frontend_process:
        print(f"{Colors.RED}❌ No se pudo iniciar el frontend. Abortando.{Colors.END}")
        if backend_process:
            backend_process.terminate()
        sys.exit(1)

    # Monitorear procesos
    monitor_processes(backend_process, frontend_process)

if __name__ == "__main__":
    main()