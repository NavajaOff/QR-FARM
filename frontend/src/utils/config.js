// Centralized configuration utility
// This file provides a consistent way to access backend URL across the application

/**
 * Get the backend base URL from environment variables or configuration
 * @returns {string} Backend base URL
 * @throws {Error} If no backend URL is configured
 */
export const getBackendUrl = () => {
  // Priority 1: Vite environment variable
  // Use optional chaining to safely access import.meta (works in Vite/ESM environments)
  // eslint-disable-next-line no-undef
  if (import.meta?.env?.VITE_BACKEND_URL) {
    // eslint-disable-next-line no-undef
    return import.meta.env.VITE_BACKEND_URL;
  }
  
  // Priority 2: Vue environment variable (for compatibility)
  // eslint-disable-next-line no-undef
  if (import.meta?.env?.VUE_APP_API_BASE_URL) {
    // eslint-disable-next-line no-undef
    const url = import.meta.env.VUE_APP_API_BASE_URL;
    return url.replace(/\/api\/?$/, '');
  }
  
  // Priority 3: Window config (from config.js)
  if (globalThis.window?.config?.API_BASE_URL) {
    const url = globalThis.window.config.API_BASE_URL;
    return url.replace(/\/api\/?$/, '');
  }
  
  // No fallback - must be configured via environment variables
  throw new Error(
    'VITE_BACKEND_URL o VUE_APP_API_BASE_URL debe estar configurado. ' +
    'Configure la variable de entorno antes de ejecutar la aplicación.'
  );
};

/**
 * Get the API base URL (backend URL + /api)
 * @returns {string} API base URL (e.g., 'http://localhost:5000/api')
 */
export const getApiBaseUrl = () => {
  const backendUrl = getBackendUrl();
  return `${backendUrl}/api`;
};

/**
 * Get the full API URL for a specific endpoint
 * @param {string} endpoint - API endpoint (e.g., '/animales' or 'animales')
 * @returns {string} Full API URL
 */
export const getApiUrl = (endpoint) => {
  const apiBase = getApiBaseUrl();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${apiBase}${cleanEndpoint}`;
};

