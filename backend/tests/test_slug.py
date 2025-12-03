"""Tests para utilidades de slug."""
import pytest
from unittest.mock import Mock, patch
from src.utils.slug import (
    normalizar_texto,
    generar_slug,
    verificar_codigo_tenant_existe,
    generar_codigo_tenant_unico
)


class TestNormalizarTexto:
    """Tests para normalizar_texto."""
    
    def test_normalizar_texto_sin_acentos(self):
        """Test normalizar texto sin acentos."""
        assert normalizar_texto("finca") == "finca"
        assert normalizar_texto("Finca") == "Finca"
    
    def test_normalizar_texto_con_acentos(self):
        """Test normalizar texto con acentos."""
        assert normalizar_texto("José") == "Jose"
        assert normalizar_texto("María") == "Maria"
        assert normalizar_texto("niño") == "nino"
        assert normalizar_texto("áéíóú") == "aeiou"
        assert normalizar_texto("ÁÉÍÓÚ") == "AEIOU"
    
    def test_normalizar_texto_con_enie(self):
        """Test normalizar texto con ñ."""
        assert normalizar_texto("niño") == "nino"
        assert normalizar_texto("Ñoño") == "Nono"
        assert normalizar_texto("España") == "Espana"
    
    def test_normalizar_texto_vacio(self):
        """Test normalizar texto vacío."""
        assert normalizar_texto("") == ""
        assert normalizar_texto(None) == ""


class TestGenerarSlug:
    """Tests para generar_slug."""
    
    def test_generar_slug_basico(self):
        """Test generar slug básico."""
        assert generar_slug("Finca San Jose") == "finca-san-jose"
        assert generar_slug("Mi Finca") == "mi-finca"
    
    def test_generar_slug_con_acentos(self):
        """Test generar slug con acentos."""
        assert generar_slug("Finca San José") == "finca-san-jose"
        assert generar_slug("María García") == "maria-garcia"
        assert generar_slug("Niño Feliz") == "nino-feliz"
    
    def test_generar_slug_minusculas(self):
        """Test que el slug siempre esté en minúsculas."""
        assert generar_slug("FINCA SAN JOSE") == "finca-san-jose"
        assert generar_slug("Mi FiNcA") == "mi-finca"
    
    def test_generar_slug_espacios_por_guiones(self):
        """Test que los espacios se conviertan en guiones."""
        assert generar_slug("Finca San Jose") == "finca-san-jose"
        assert generar_slug("Mi  Finca") == "mi-finca"  # Espacios múltiples
    
    def test_generar_slug_caracteres_especiales(self):
        """Test que los caracteres especiales se remuevan."""
        assert generar_slug("Finca #1") == "finca-1"
        assert generar_slug("Mi@Finca!") == "mi-finca"
        assert generar_slug("Finca (San Jose)") == "finca-san-jose"
    
    def test_generar_slug_guiones_multiples(self):
        """Test que los guiones múltiples se conviertan en uno solo."""
        assert generar_slug("Finca--San--Jose") == "finca-san-jose"
        assert generar_slug("Mi---Finca") == "mi-finca"
    
    def test_generar_slug_guiones_inicio_fin(self):
        """Test que se remuevan guiones al inicio y final."""
        assert generar_slug("-Finca San Jose-") == "finca-san-jose"
        assert generar_slug("--Finca--") == "finca"
    
    def test_generar_slug_vacio(self):
        """Test generar slug de texto vacío."""
        assert generar_slug("") == ""
        assert generar_slug("   ") == ""


class TestVerificarCodigoTenantExiste:
    """Tests para verificar_codigo_tenant_existe."""
    
    @patch('src.utils.slug.get_connection')
    def test_verificar_codigo_tenant_existe_true(self, mock_get_conn):
        """Test verificar código que existe."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'count': 1}
        
        result = verificar_codigo_tenant_existe('finca-san-jose')
        
        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('src.utils.slug.get_connection')
    def test_verificar_codigo_tenant_existe_false(self, mock_get_conn):
        """Test verificar código que no existe."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'count': 0}
        
        result = verificar_codigo_tenant_existe('finca-nueva')
        
        assert result is False
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('src.utils.slug.get_connection')
    def test_verificar_codigo_tenant_existe_exception(self, mock_get_conn):
        """Test verificar código con excepción."""
        mock_get_conn.side_effect = Exception("DB Error")
        
        result = verificar_codigo_tenant_existe('finca-test')
        
        assert result is False


class TestGenerarCodigoTenantUnico:
    """Tests para generar_codigo_tenant_unico."""
    
    @patch('src.utils.slug.verificar_codigo_tenant_existe')
    @patch('src.utils.slug.generar_slug')
    def test_generar_codigo_tenant_unico_disponible(self, mock_generar_slug, mock_verificar):
        """Test generar código cuando el slug base está disponible."""
        mock_generar_slug.return_value = 'finca-san-jose'
        mock_verificar.return_value = False
        
        result = generar_codigo_tenant_unico('Finca San José')
        
        assert result == 'finca-san-jose'
        mock_generar_slug.assert_called_once_with('Finca San José')
        mock_verificar.assert_called_once_with('finca-san-jose')
    
    @patch('src.utils.slug.verificar_codigo_tenant_existe')
    @patch('src.utils.slug.generar_slug')
    def test_generar_codigo_tenant_unico_con_sufijo(self, mock_generar_slug, mock_verificar):
        """Test generar código cuando el slug base existe, agregando sufijo."""
        mock_generar_slug.return_value = 'finca-san-jose'
        # Primera llamada: existe, segunda: no existe (disponible)
        mock_verificar.side_effect = [True, False]
        
        result = generar_codigo_tenant_unico('Finca San José')
        
        assert result == 'finca-san-jose-1'
        assert mock_verificar.call_count == 2
    
    @patch('src.utils.slug.verificar_codigo_tenant_existe')
    @patch('src.utils.slug.generar_slug')
    def test_generar_codigo_tenant_unico_multiples_sufijos(self, mock_generar_slug, mock_verificar):
        """Test generar código con múltiples sufijos incrementales."""
        mock_generar_slug.return_value = 'finca-san-jose'
        # Existen 1 y 2, pero 3 está disponible
        mock_verificar.side_effect = [True, True, True, False]
        
        result = generar_codigo_tenant_unico('Finca San José')
        
        assert result == 'finca-san-jose-3'
        assert mock_verificar.call_count == 4
    
    def test_generar_codigo_tenant_unico_nombre_vacio(self):
        """Test generar código con nombre vacío."""
        with pytest.raises(ValueError, match="El nombre del tenant no puede estar vacío"):
            generar_codigo_tenant_unico("")
        
        with pytest.raises(ValueError, match="No se pudo generar un código válido"):
            generar_codigo_tenant_unico("   ")

