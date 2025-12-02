// Configuración global para desarrollo
// Este archivo se puede modificar según el entorno
// ⚠️  IMPORTANTE: Este archivo se carga ANTES que Vue.js
// Para producción, configura VITE_BACKEND_URL en las variables de entorno
// o modifica este archivo directamente
(function() {
  // Determinar la URL del backend basándose en el hostname actual
  // En desarrollo local: usar localhost:5000
  // En producción: usar el mismo origin o configurar manualmente
  let backendUrl = 'http://localhost:5000';
  
  // Si no estamos en localhost, intentar usar el mismo origin
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    // En producción, asumir que el backend está en el mismo dominio pero puerto 5000
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