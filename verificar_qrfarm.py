#!/usr/bin/env python3
"""
Script para verificar que el backend QR Farm esté funcionando correctamente
Hace pruebas de conectividad y login
"""

import requests
import json
import sys

def test_health():
    """Prueba el endpoint de health check"""
    try:
        print("Probando health check...")
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Health check OK: {data['message']}")
            return True
        else:
            print(f"Health check fallo: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error conectando al health check: {e}")
        return False

def test_login():
    """Prueba el endpoint de login"""
    try:
        print("Probando login...")

        # Intentar login con credenciales de prueba
        payload = {
            'email': 'admin@qrfarm.com',
            'password': 'admin123'
        }

        response = requests.post('http://localhost:5000/api/usuarios/login',
                               json=payload,
                               timeout=10)

        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Respuesta: {json.dumps(data, indent=2)}")

            if data.get('status') == 'success':
                print("Login exitoso - Token recibido")
                return True
            else:
                print(f"Login fallo: {data.get('message', 'Sin mensaje')}")
                return False
        elif response.status_code == 401:
            data = response.json()
            print(f"Credenciales invalidas: {data.get('message', 'Sin mensaje')}")
            return False
        else:
            print(f"Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error conectando al login: {e}")
        return False

def test_cors():
    """Prueba CORS con una petición OPTIONS"""
    try:
        print("Probando CORS...")

        headers = {
            'Origin': 'http://localhost:5174',
            'Access-Control-Request-Method': 'POST'
        }

        response = requests.options('http://localhost:5000/api/usuarios/login',
                                  headers=headers,
                                  timeout=5)

        cors_headers = {
            'access-control-allow-origin': response.headers.get('Access-Control-Allow-Origin'),
            'access-control-allow-credentials': response.headers.get('Access-Control-Allow-Credentials')
        }

        print(f"CORS headers: {cors_headers}")

        if cors_headers['access-control-allow-origin']:
            print("CORS configurado correctamente")
            return True
        else:
            print("CORS podria no estar configurado")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error probando CORS: {e}")
        return False

def main():
    print("Verificando QR Farm Backend")
    print("=" * 40)

    tests = [
        ("Health Check", test_health),
        ("CORS", test_cors),
        ("Login", test_login)
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        result = test_func()
        results.append(result)
        print()

    print("=" * 40)
    print("Resumen:")

    passed = sum(results)
    total = len(results)

    for i, (name, _) in enumerate(tests):
        status = "PASO" if results[i] else "FALLO"
        print(f"  {name}: {status}")

    print(f"\nResultado final: {passed}/{total} pruebas pasaron")

    if passed == total:
        print("Todo esta funcionando correctamente!")
        return 0
    else:
        print("Hay problemas que necesitan atencion")
        return 1

if __name__ == "__main__":
    sys.exit(main())