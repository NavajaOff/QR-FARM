// Configuración global para desarrollo
// Este archivo se puede modificar según el entorno
// ⚠️  IMPORTANTE: Este archivo se carga ANTES que Vue.js
window.config = {
  // URL base del backend
  API_BASE_URL: 'http://localhost:5000/api',

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