// src/socket.js
import { io } from "socket.io-client";

// Obtener URL del backend desde variables de entorno o fallback a window.config
// Prioridad: VITE_BACKEND_URL > VUE_APP_API_BASE_URL > window.config.API_BASE_URL
let backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.VUE_APP_API_BASE_URL?.replace(/\/api\/?$/, '');

// Fallback a window.config si está disponible (config.js se carga antes)
if (!backendUrl && typeof window !== 'undefined' && window.config?.API_BASE_URL) {
  // Extraer la URL base del API_BASE_URL (remover /api si existe)
  backendUrl = window.config.API_BASE_URL.replace(/\/api\/?$/, '');
}

if (!backendUrl) {
  throw new Error(
    'VITE_BACKEND_URL o VUE_APP_API_BASE_URL debe estar configurado. ' +
    'Configure la variable de entorno antes de ejecutar la aplicación. ' +
    'En Docker, configure VITE_BACKEND_URL en .env y pase como build arg.'
  );
}

export const socket = io(backendUrl, {
  transports: ["websocket"],
  reconnectionAttempts: 5,
  reconnectionDelay: 3000,
});