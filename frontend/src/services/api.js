import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.code === 'ERR_NETWORK') {
      alert('⚠️ No se pudo conectar al servidor Flask. Verifica que esté corriendo en el puerto 5000.');
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

export const userAPI = {
  getAll: () => api.get('/usuarios/'),
  getById: (id) => api.get(`/usuarios/${id}`),
  update: (id, data) => api.put(`/usuarios/${id}`, data),
  delete: (id) => api.delete(`/usuarios/${id}`),
  changeStatus: (id, status) => api.put(`/usuarios/${id}/estado`, { estado: status }),
};

export const ganadoAPI = {
  getAll: () => api.get('/ganados/'),
  getById: (id) => api.get(`/ganados/${id}`),
  create: (data) => api.post('/ganados/', data),
  update: (id, data) => api.put(`/ganados/${id}`, data),
  delete: (id) => api.delete(`/ganados/${id}`),
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

// Exportar instancia por defecto para uso general
export default api;