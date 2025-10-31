// Utilidades de autenticación y roles
export const auth = {
  // Verificar si el usuario está autenticado
  isAuthenticated() {
    return !!localStorage.getItem('token');
  },

  // Obtener el rol del usuario
  getUserRole() {
    return localStorage.getItem('userRole') || 'usuario';
  },

  // Verificar si el usuario es administrador
  isAdmin() {
    return this.getUserRole() === 'administrador';
  },

  // Verificar si el usuario es usuario normal
  isUser() {
    return this.getUserRole() === 'usuario';
  },

  // Limpiar datos de autenticación
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('userRole');
  },

  // Obtener token
  getToken() {
    return localStorage.getItem('token');
  },

  // Obtener datos del usuario
  getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }
};

// Guard de navegación para rutas protegidas
export const requireAuth = (to, from, next) => {
  if (!auth.isAuthenticated()) {
    next('/login');
  } else {
    next();
  }
};

// Guard para rutas de administrador
export const requireAdmin = (to, from, next) => {
  if (!auth.isAuthenticated()) {
    next('/login');
  } else if (!auth.isAdmin()) {
    next('/menu'); // Redirigir al menú si no es admin
  } else {
    next();
  }
};