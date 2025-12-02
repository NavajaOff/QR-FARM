// Centralized configuration utility
// This file provides a consistent way to access backend URL across the application

/**
 * Get the backend base URL from environment variables or configuration
 * @returns {string} Backend base URL (e.g., 'http://localhost:5000')
 */
export const getBackendUrl = () => {
  // Priority 1: Vite environment variable
  try {
    // Try direct access to import.meta (works in Vite/ESM environments)
    // eslint-disable-next-line no-undef
    if (import.meta && import.meta.env && import.meta.env.VITE_BACKEND_URL) {
      // eslint-disable-next-line no-undef
      return import.meta.env.VITE_BACKEND_URL;
    }
  } catch (e) {
    // import.meta not available (e.g., in tests or non-ESM environments)
  }
  
  // Priority 2: Vue environment variable (for compatibility)
  try {
    // eslint-disable-next-line no-undef
    if (import.meta && import.meta.env && import.meta.env.VUE_APP_API_BASE_URL) {
      // eslint-disable-next-line no-undef
      const url = import.meta.env.VUE_APP_API_BASE_URL;
      return url.replace(/\/api\/?$/, '');
    }
  } catch (e) {
    // import.meta not available (e.g., in tests or non-ESM environments)
  }
  
  // Priority 3: Window config (from config.js)
  if (globalThis.window?.config?.API_BASE_URL) {
    const url = globalThis.window.config.API_BASE_URL;
    return url.replace(/\/api\/?$/, '');
  }
  
  // Priority 4: Fallback to localhost (development only)
  return 'http://localhost:5000';
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

