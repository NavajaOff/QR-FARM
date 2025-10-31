import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import './style.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

// Configuración global usando variables de entorno (tiene prioridad sobre config.js)
const config = {
  API_BASE_URL: import.meta.env.VUE_APP_API_BASE_URL || window.config?.API_BASE_URL || 'http://localhost:5000/api',
  APP_NAME: import.meta.env.VUE_APP_APP_NAME || window.config?.APP_NAME || 'QR Farm',
  DEBUG: import.meta.env.VUE_APP_DEBUG === 'true' || window.config?.DEBUG || false,
  TIMEOUT: window.config?.TIMEOUT || 10000,
  RETRY_ATTEMPTS: window.config?.RETRY_ATTEMPTS || 3,
  RETRY_DELAY: window.config?.RETRY_DELAY || 1000,
};

// Mezclar con configuración global si existe (config.js tiene prioridad para algunas cosas)
if (window.config) {
  window.config = { ...window.config, ...config };
} else {
  window.config = config;
}

// Log de configuración para debug
if (window.config.DEBUG) {
  console.log('🔧 Configuración cargada:', window.config);
}

createApp(App).use(router).mount('#app')
