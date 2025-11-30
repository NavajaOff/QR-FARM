import api from './api.js';

class AuthService {
  user = null;
  token = null;
  role = null;

  // Verificar si el usuario está autenticado
  isAuthenticated() {
    const token = this.getToken();
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp > currentTime;
    } catch (error) {
      console.error('Error validating token:', error);
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

  // Obtener rol del usuario (siempre obtener del localStorage para asegurar valor actualizado)
  getRole() {
    const roleFromStorage = localStorage.getItem('userRole');
    // Actualizar estado interno si cambió
    if (roleFromStorage !== this.role) {
      this.role = roleFromStorage;
      console.log('[AuthService] Rol actualizado desde localStorage:', this.role);
    }
    return this.role;
  }

  // Verificar si es administrador
  isAdmin() {
    const role = this.getRole();
    const isAdminResult = role == 'admin' || role == 'administrador' || role == 'super_admin';
    console.log('[AuthService] isAdmin() - Rol:', role, 'Resultado:', isAdminResult);
    return isAdminResult;
  }

  // Verificar si es super admin
  isSuperAdmin() {
    const role = this.getRole();
    return role == 'super_admin';
  }

  // Verificar si es usuario normal
  isUser() {
    const role = this.getRole();
    console.log("Verificando si es user - Rol actual:", role);
    return role == 'user' || role == 'usuario';
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
    console.log('[AuthService] Iniciando logout...');
    
    // Limpiar localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('userRole');
    localStorage.removeItem('qr_farm_selected_tenant_id'); // Limpiar tenant seleccionado
    
    // Limpiar sessionStorage
    sessionStorage.removeItem('lastLoginEmail');

    // Limpiar estado interno
    this.token = null;
    this.user = null;
    this.role = null;
    
    console.log('[AuthService] Logout completado - Estado limpiado');
  }

  // Verificar permisos para una ruta
  hasPermission(requiredRole) {
    if (!this.isAuthenticated()) return false;

    const userRole = this.getRole();

    // Super admin tiene todos los permisos
    if (userRole == 'super_admin') {
      return true;
    }

    if (requiredRole == 'admin') {
      return userRole == 'admin' || userRole == 'administrador';
    } else if (requiredRole == 'user') {
      return userRole == 'user' || userRole == 'usuario' || userRole == 'admin' || userRole == 'administrador';
    }

    return false;
  }

  // Redirigir según rol después del login
  getRedirectPath() {
    const role = this.getRole();
    
    // Super admin puede acceder a admin dashboard
    if (role == 'super_admin' || this.isAdmin()) {
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