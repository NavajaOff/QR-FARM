// src/socket.js
import { io } from "socket.io-client";

// Obtener URL del backend desde variables de entorno (obligatorio)
const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.VUE_APP_API_BASE_URL?.replace(/\/api\/?$/, '');

if (!backendUrl) {
  throw new Error(
    'VITE_BACKEND_URL o VUE_APP_API_BASE_URL debe estar configurado. ' +
    'Configure la variable de entorno antes de ejecutar la aplicación.'
  );
}

export const socket = io(backendUrl, {
  transports: ["websocket"],
  reconnectionAttempts: 5,
  reconnectionDelay: 3000,
});