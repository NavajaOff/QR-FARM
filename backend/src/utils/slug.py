"""Utilidades para generación de slugs."""
import re
from typing import Optional
from src.database.db import get_connection


def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto español removiendo tildes y caracteres especiales.
    
    Args:
        texto: Texto a normalizar
        
    Returns:
        Texto normalizado sin tildes ni caracteres especiales
    """
    if not texto:
        return ""
    
    # Mapeo de caracteres especiales a sus equivalentes sin tilde
    reemplazos = {
        'á': 'a', 'à': 'a', 'ä': 'a', 'â': 'a',
        'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e',
        'í': 'i', 'ì': 'i', 'ï': 'i', 'î': 'i',
        'ó': 'o', 'ò': 'o', 'ö': 'o', 'ô': 'o',
        'ú': 'u', 'ù': 'u', 'ü': 'u', 'û': 'u',
        'ñ': 'n',
        'Á': 'A', 'À': 'A', 'Ä': 'A', 'Â': 'A',
        'É': 'E', 'È': 'E', 'Ë': 'E', 'Ê': 'E',
        'Í': 'I', 'Ì': 'I', 'Ï': 'I', 'Î': 'I',
        'Ó': 'O', 'Ò': 'O', 'Ö': 'O', 'Ô': 'O',
        'Ú': 'U', 'Ù': 'U', 'Ü': 'U', 'Û': 'U',
        'Ñ': 'N'
    }
    
    texto_normalizado = texto
    for caracter, reemplazo in reemplazos.items():
        texto_normalizado = texto_normalizado.replace(caracter, reemplazo)
    
    return texto_normalizado


def generar_slug(nombre: str) -> str:
    """
    Genera un slug a partir de un nombre.
    
    Convierte el nombre a minúsculas, reemplaza espacios por guiones,
    remueve tildes, ñ y caracteres especiales.
    
    Args:
        nombre: Nombre a convertir en slug
        
    Returns:
        Slug generado
    """
    if not nombre:
        return ""
    
    # Normalizar texto (remover tildes y ñ)
    texto_normalizado = normalizar_texto(nombre.strip())
    
    # Convertir a minúsculas
    texto_normalizado = texto_normalizado.lower()
    
    # Reemplazar espacios y caracteres no alfanuméricos por guiones
    texto_normalizado = re.sub(r'[^a-z0-9]+', '-', texto_normalizado)
    
    # Remover guiones al inicio y final
    texto_normalizado = texto_normalizado.strip('-')
    
    # Remover guiones múltiples consecutivos
    texto_normalizado = re.sub(r'-+', '-', texto_normalizado)
    
    return texto_normalizado


def verificar_codigo_tenant_existe(codigo_tenant: str) -> bool:
    """
    Verifica si un código de tenant ya existe en la base de datos.
    
    Args:
        codigo_tenant: Código a verificar
        
    Returns:
        True si existe, False si no existe
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM tenants WHERE codigo_tenant = %s
        """, (codigo_tenant,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result['count'] > 0 if result else False
    except Exception:
        return False


def generar_codigo_tenant_unico(nombre: str) -> str:
    """
    Genera un código de tenant único a partir del nombre.
    
    Si el slug generado ya existe, agrega un sufijo incremental
    hasta encontrar uno que no exista.
    
    Args:
        nombre: Nombre del tenant
        
    Returns:
        Código de tenant único
    """
    if not nombre:
        raise ValueError("El nombre del tenant no puede estar vacío")
    
    # Generar slug base
    codigo_base = generar_slug(nombre)
    
    if not codigo_base:
        raise ValueError("No se pudo generar un código válido a partir del nombre")
    
    # Verificar si el código base ya existe
    if not verificar_codigo_tenant_existe(codigo_base):
        return codigo_base
    
    # Si existe, agregar sufijo incremental
    contador = 1
    while True:
        codigo_candidato = f"{codigo_base}-{contador}"
        if not verificar_codigo_tenant_existe(codigo_candidato):
            return codigo_candidato
        contador += 1
        
        # Límite de seguridad para evitar loops infinitos
        if contador > 1000:
            raise ValueError("No se pudo generar un código único después de 1000 intentos")

