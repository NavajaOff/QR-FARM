import api from './api.js';

class AuthService {
  constructor() {
    this.user = null;
    this.token = null;
    this.role = null;
  }

  // Verificar si el usuario está autenticado
  isAuthenticated() {
    const token = this.getToken();
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp > currentTime;
    } catch (error) {
      return false;
    }
  }

  // Obtener token del localStorage
  getToken() {
    if (!this.token) {
      this.token = localStorage.getItem('token');
    }
    return this.token;
  }

  // Obtener datos del usuario
  getUser() {
    if (!this.user) {
      const userData = localStorage.getItem('user');
      if (userData && userData !== 'undefined' && userData !== 'null' && userData.trim() !== '') {
        try {
          this.user = JSON.parse(userData);
        } catch (error) {
          console.error('Error parsing user data from localStorage:', error);
          console.log('Raw userData:', userData);
          this.user = null;
          // Limpiar datos corruptos
          localStorage.removeItem('user');
        }
      } else {
        this.user = null;
      }
    }
    return this.user;
  }

  // Obtener rol del usuario
  getRole() {
    if (!this.role) {
      this.role = localStorage.getItem('userRole');
    }
    return this.role;
  }

  // Verificar si es administrador
  isAdmin() {
    const role = this.getRole();
    console.log("Verificando si es admin - Rol actual:", role);
    return role === 'admin' || role === 'administrador';
  }

  // Verificar si es usuario normal
  isUser() {
    const role = this.getRole();
    console.log("Verificando si es user - Rol actual:", role);
    return role === 'user' || role === 'usuario';
  }

  // Guardar email para renovación de token
  saveCredentialsForRenewal(email) {
    if (email && typeof email === 'string') {
      sessionStorage.setItem('lastLoginEmail', email);
    }
  }

  // Iniciar sesión
  async login(credentials) {
    try {
      const response = await api.post('/usuarios/login', credentials);

      if (response.data.status === 'success') {
        const { token, user } = response.data;

        // Decodificar token para obtener rol
        const payload = JSON.parse(atob(token.split('.')[1]));
        console.log('Token payload:', payload);
        console.log('User data:', user);

        // Guardar en localStorage
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
        localStorage.setItem('userRole', payload.role);

        // Guardar email para renovación de token
        if (credentials.email) {
          this.saveCredentialsForRenewal(credentials.email);
        }

        // Actualizar estado interno
        this.token = token;
        this.user = user;
        this.role = payload.role;

        console.log('Login successful - Role:', payload.role);
        return { success: true, user, role: payload.role };
      } else {
        return { success: false, message: response.data.message };
      }
    } catch (error) {
      const message = error.response?.data?.message || 'Error al iniciar sesión';
      return { success: false, message };
    }
  }

  // Cerrar sesión
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('userRole');
    sessionStorage.removeItem('lastLoginEmail');

    this.token = null;
    this.user = null;
    this.role = null;
  }

  // Verificar permisos para una ruta
  hasPermission(requiredRole) {
    if (!this.isAuthenticated()) return false;

    const userRole = this.getRole();

    if (requiredRole === 'admin') {
      return userRole === 'admin' || userRole === 'administrador';
    } else if (requiredRole === 'user') {
      return userRole === 'user' || userRole === 'usuario' || userRole === 'admin' || userRole === 'administrador';
    }

    return false;
  }

  // Redirigir según rol después del login
  getRedirectPath() {
    if (this.isAdmin()) {
      return '/admin/dashboard';
    } else if (this.isUser()) {
      return '/user/inicio';
    }
    return '/login';
  }
}

// Crear instancia singleton
const authService = new AuthService();

export default authService;