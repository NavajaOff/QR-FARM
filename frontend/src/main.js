import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import './style.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

// Configuración global usando variables de entorno (tiene prioridad sobre config.js)
const config = {
  API_BASE_URL: import.meta.env.VUE_APP_API_BASE_URL || globalThis.window?.config?.API_BASE_URL || 'http://localhost:5000/api',
  APP_NAME: import.meta.env.VUE_APP_APP_NAME || globalThis.window?.config?.APP_NAME || 'QR Farm',
  DEBUG: import.meta.env.VUE_APP_DEBUG === 'true' || globalThis.window?.config?.DEBUG || false,
  TIMEOUT: globalThis.window?.config?.TIMEOUT || 10000,
  RETRY_ATTEMPTS: globalThis.window?.config?.RETRY_ATTEMPTS || 3,
  RETRY_DELAY: globalThis.window?.config?.RETRY_DELAY || 1000,
};

// Mezclar con configuración global si existe (config.js tiene prioridad para algunas cosas)
if (globalThis.window?.config) {
  globalThis.window.config = { ...globalThis.window.config, ...config };
} else {
  globalThis.window = globalThis.window || {};
  globalThis.window.config = config;
}

// Log de configuración para debug
if (globalThis.window?.config?.DEBUG) {
  console.log('🔧 Configuración cargada:', globalThis.window.config);
}

createApp(App).use(router).mount('#app')
