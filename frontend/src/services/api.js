import axios from 'axios';

const api = axios.create({
  baseURL: `${import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'}/api`,
  timeout: 10000,
});

api.interceptors.request.use(config => {
  // Crear headers object si no existe
  if (!config.headers) {
    config.headers = {};
  }
  
  // Agregar token de autenticación
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log('[API] Token agregado a petición:', config.url);
  } else {
    console.warn('[API] No hay token disponible para petición:', config.url);
  }
  
  // Agregar tenant_id a query params si está seleccionado (para super admin)
  try {
    const selectedTenantId = localStorage.getItem('qr_farm_selected_tenant_id');
    if (selectedTenantId) {
      const tenantId = Number.parseInt(selectedTenantId, 10);
      if (!Number.isNaN(tenantId)) {
        // Solo agregar tenant_id a rutas que no sean de tenants
        const url = config.url || '';
        if (!url.includes('/tenants') && !url.includes('/usuarios/login') && !url.includes('/usuarios/register')) {
          config.params = config.params || {};
          config.params.tenant_id = tenantId;
          console.log('[API] Tenant ID agregado a petición:', config.url, 'tenant_id:', tenantId);
        }
      }
    }
  } catch (error) {
    console.error('[API] Error agregando tenant_id a query params:', error);
  }
  
  console.log('[API] Petición configurada:', {
    url: config.url,
    method: config.method,
    hasToken: !!token,
    headers: config.headers
  });
  
  return config;
}, error => {
  console.error('[API] Error en interceptor de request:', error);
  return Promise.reject(error);
});

api.interceptors.response.use(
  response => {
    console.log('[API] Respuesta exitosa:', {
      url: response.config.url,
      status: response.status,
      statusText: response.statusText
    });
    return response;
  },
  error => {
    console.error('[API] Error en respuesta:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      message: error.message,
      code: error.code,
      data: error.response?.data
    });
    
    if (error.code === 'ERR_NETWORK') {
      console.error('[API] Error de red - No se pudo conectar al servidor');
      alert('⚠️ No se pudo conectar al servidor Flask. Verifica que esté corriendo en el puerto 5000.');
    } else if (error.response?.status === 401) {
      console.warn('[API] Error 401 - No autorizado, posible token expirado o inválido');
    } else if (error.response?.status === 403) {
      console.warn('[API] Error 403 - Acceso prohibido');
    } else if (error.response?.status >= 500) {
      console.error('[API] Error del servidor:', error.response?.status);
    }
    
    return Promise.reject(error);
  }
);

// Funciones de API organizadas por módulo
export const authAPI = {
  register: (userData) => api.post('/usuarios/register', userData),
  login: (credentials) => api.post('/usuarios/login', credentials),
  getProfile: () => api.get('/usuarios/profile'),
  updateProfile: (data) => api.put('/usuarios/profile', data),
};

export const recoveryAPI = {
  request: (email) => api.post('/usuarios/recovery/request', { email }),
  confirm: (payload) => api.post('/usuarios/recovery/confirm', payload),
  listRequests: () => api.get('/usuarios/recovery/requests'),
  approve: (recoveryId) => api.post(`/usuarios/recovery/${recoveryId}/approve`),
  reject: (recoveryId) => api.post(`/usuarios/recovery/${recoveryId}/reject`),
};
 
export const userAPI = {
  getAll: () => api.get('/usuarios/'),
  getById: (id) => api.get(`/usuarios/${id}`),
  update: (id, data) => api.put(`/usuarios/${id}`, data),
  delete: (id) => api.delete(`/usuarios/${id}`),
  changeStatus: (id, status) => api.put(`/usuarios/${id}/estado`, { estado: status }),
};

export const ganadoAPI = {
  getAll: () => api.get('/animales/'),
  getById: (id) => api.get(`/animales/${id}`),
  create: (data) => api.post('/animales/', data),
  update: (id, data) => api.put(`/animales/${id}`, data),
  delete: (id) => api.delete(`/animales/${id}`),
};

export const potreroAPI = {
  getAll: () => api.get('/potreros/'),
  getById: (id) => api.get(`/potreros/${id}`),
  create: (data) => api.post('/potreros/', data),
  update: (id, data) => api.put(`/potreros/${id}`, data),
  delete: (id) => api.delete(`/potreros/${id}`),
};

export const vacunacionAPI = {
  getAll: () => api.get('/vacunaciones/'),
  getById: (id) => api.get(`/vacunaciones/${id}`),
  create: (data) => api.post('/vacunaciones/', data),
  update: (id, data) => api.put(`/vacunaciones/${id}`, data),
  delete: (id) => api.delete(`/vacunaciones/${id}`),
};

export const reportAPI = {
  getSummary: () => api.get('/reportes/resumen'),
  downloadSummaryPdf: () => api.get('/reportes/resumen/pdf', { responseType: 'blob' }),
};

export const tenantAPI = {
  getAll: (activosOnly = true) => {
    // Asegurar que el parámetro sea un booleano convertido a string 'true' o 'false'
    const activosOnlyStr = (activosOnly === true || String(activosOnly) === 'true') ? 'true' : 'false'
    console.log('[tenantAPI] getAll - activosOnly:', activosOnly, 'convertido a:', activosOnlyStr)
    return api.get(`/tenants?activos_only=${activosOnlyStr}`)
  },
  getById: (id) => api.get(`/tenants/${id}`),
  getCurrent: () => api.get('/tenants/actual'),
  create: (data) => api.post('/tenants', data),
  update: (id, data) => api.put(`/tenants/${id}`, data),
};

export const notificationAPI = {
  getUpcoming: () => api.get('/notificaciones/proximas'),
};

// Exportar instancia por defecto para uso general
export default api;