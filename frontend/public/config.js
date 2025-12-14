// Configuración global para desarrollo
// Este archivo se puede modificar según el entorno
// ⚠️  IMPORTANTE: Este archivo se carga ANTES que Vue.js
// Para producción, configura VITE_BACKEND_URL en las variables de entorno
// o modifica este archivo directamente
(function() {
  // Determinar la URL del backend basándose en el entorno
  // Docker: puerto 5174 → backend en 5010
  // Local: puerto 5173 o sin puerto → backend en 5000
  // Producción: usar configuración explícita o mismo dominio
  let backendUrl = 'http://localhost:5000'; // Valor por defecto para desarrollo local
  
  const currentPort = window.location.port;
  const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  
  // Detectar si estamos en Docker (puerto 5174 es el puerto externo del frontend en Docker)
  if (isLocalhost && currentPort === '5174') {
    // Docker: frontend en 5174 → backend en 5010
    backendUrl = 'http://localhost:5010';
  } else if (isLocalhost && (currentPort === '5173' || !currentPort)) {
    // Desarrollo local: frontend en 5173 o sin puerto → backend en 5000
    backendUrl = 'http://localhost:5000';
  } else if (!isLocalhost) {
    // Producción: asumir que el backend está en el mismo dominio pero puerto 5000
    // O usar el mismo origin si el backend está en el mismo servidor
    backendUrl = window.location.origin.replace(/:\d+$/, ':5000');
  }

  window.config = {
    // URL base del backend
    // Se puede sobrescribir con VITE_BACKEND_URL en variables de entorno
    // o con window.config.API_BASE_URL después de cargar este archivo
    API_BASE_URL: `${backendUrl}/api`,

    // Otras configuraciones globales
    APP_NAME: 'QR Farm',
    VERSION: '1.0.0',
    DEBUG: true,

    // Configuración de timeouts
    TIMEOUT: 10000,

    // Configuración de reintentos
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000
  };
})();