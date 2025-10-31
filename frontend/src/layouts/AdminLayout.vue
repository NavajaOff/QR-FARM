<template>
  <div class="admin-layout">
    <!-- Header -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-gradient-primary shadow-sm">
      <div class="container-fluid px-4">
        <div class="d-flex align-items-center w-100">
          <button
            class="btn btn-outline-light d-md-none me-3"
            type="button"
            data-bs-toggle="offcanvas"
            data-bs-target="#adminSidebar"
            aria-controls="adminSidebar"
          >
            <i class="fas fa-bars"></i>
          </button>

          <!-- Logo y título -->
          <router-link class="navbar-brand d-flex align-items-center me-4" to="/admin/dashboard">
            <i class="fas fa-tractor text-warning me-2 fa-lg"></i>
            <span class="fw-bold fs-3 text-white">QR FARM</span>
            <i class="fas fa-cow ms-2 text-light"></i>
          </router-link>

          <!-- Espaciador -->
          <div class="flex-grow-1"></div>

          <!-- Información del usuario -->
          <div class="d-flex align-items-center me-3">
            <div class="d-flex align-items-center text-white">
              <i class="fas fa-user-shield me-2"></i>
              <div class="d-none d-sm-block">
                <div class="fw-semibold small">{{ userName }}</div>
                <div class="badge bg-light text-primary small">Administrador</div>
              </div>
            </div>
          </div>

          <!-- Botón salir -->
          <button class="btn btn-outline-light btn-sm" @click="logout" title="Cerrar sesión">
            <i class="fas fa-sign-out-alt me-1"></i>
            <span class="d-none d-sm-inline">Salir</span>
          </button>
        </div>
      </div>
    </nav>

    <!-- Sidebar -->
    <div class="d-none d-md-block admin-sidebar">
      <nav class="nav flex-column py-3">
        <!-- Dashboard -->
        <router-link class="nav-link mb-2" to="/admin/dashboard">
          <div class="d-flex align-items-center">
            <i class="fas fa-tachometer-alt me-3 fa-lg"></i>
            <span class="fw-medium">Dashboard</span>
          </div>
        </router-link>

        <!-- Gestión (Collapsible) -->
        <div class="nav-item">
          <a class="nav-link mb-2 d-flex align-items-center justify-content-between"
             data-bs-toggle="collapse"
             href="#gestionMenu"
             role="button"
             aria-expanded="false"
             aria-controls="gestionMenu">
            <div class="d-flex align-items-center">
              <i class="fas fa-tasks me-3 fa-lg"></i>
              <span class="fw-medium">Gestión</span>
            </div>
            <i class="fas fa-chevron-down transition-all"></i>
          </a>
          <div class="collapse ps-4" id="gestionMenu">
            <router-link class="nav-link mb-1 small" to="/admin/gestionar-usuarios">
              <i class="fas fa-users me-2"></i>Usuarios
            </router-link>
            <router-link class="nav-link mb-1 small" to="/admin/gestionar-animales">
              <i class="fas fa-cow me-2"></i>Ganado
            </router-link>
            <router-link class="nav-link mb-1 small" to="/admin/gestionar-potreros">
              <i class="fas fa-map-marked-alt me-2"></i>Potreros
            </router-link>
            <router-link class="nav-link mb-1 small" to="/admin/vacunacion">
              <i class="fas fa-syringe me-2"></i>Vacunación
            </router-link>
          </div>
        </div>

        <!-- Inventario -->
        <router-link class="nav-link mb-2" to="/admin/inventario">
          <div class="d-flex align-items-center">
            <i class="fas fa-boxes me-3 fa-lg"></i>
            <span class="fw-medium">Inventario</span>
          </div>
        </router-link>

        <!-- Escanear QR -->
        <router-link class="nav-link mb-2" to="/admin/escanear-qr">
          <div class="d-flex align-items-center">
            <i class="fas fa-qrcode me-3 fa-lg"></i>
            <span class="fw-medium">Escanear QR</span>
          </div>
        </router-link>

        <!-- Espaciador para empujar elementos abajo -->
        <div class="flex-grow-1"></div>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="admin-main-content">
      <router-view />
    </div>
  </div>
</template>

<script>
import authService from '../services/authService.js';

export default {
  name: 'AdminLayout',
  data() {
    return {
      userName: ''
    };
  },
  mounted() {
    console.log("Componente AdminLayout montado");

    try {
      // Verificar autenticación y rol
      const isAuth = authService.isAuthenticated();
      const isAdmin = authService.isAdmin();
      const token = authService.getToken();
      const role = authService.getRole();

      console.log("Verificación en AdminLayout:");
      console.log("- isAuthenticated:", isAuth);
      console.log("- isAdmin:", isAdmin);
      console.log("- Token presente:", !!token);
      console.log("- Rol actual:", role);

      if (!isAuth || !isAdmin) {
        console.log("Usuario no autenticado o no es admin, redirigiendo a login");
        this.$router.push('/login');
        return;
      }

      const user = authService.getUser();
      console.log('Usuario en AdminLayout:', user);
      this.userName = user?.persona?.primer_nombre || user?.primer_nombre || 'Administrador';
      console.log("AdminLayout inicializado correctamente para:", this.userName);
    } catch (error) {
      console.error('Error en AdminLayout mounted:', error);
      this.$router.push('/login');
    }
  },
  methods: {
    logout() {
      authService.logout();
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

/* Header con gradiente profesional */
.navbar {
  background: linear-gradient(135deg, #2c3e50 0%, #3498db 50%, #2980b9 100%) !important;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
  font-weight: 700 !important;
  letter-spacing: 0.5px;
}

.navbar-brand:hover {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}

/* Sidebar moderna */
.admin-sidebar {
  position: fixed;
  top: 76px;
  left: 0;
  width: 280px;
  height: calc(100vh - 76px);
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  overflow-x: hidden;
}

.admin-sidebar::-webkit-scrollbar {
  width: 6px;
}

.admin-sidebar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.admin-sidebar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.admin-sidebar .nav-link {
  color: rgba(255, 255, 255, 0.85);
  padding: 0.875rem 1.25rem;
  margin: 0.125rem 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  position: relative;
  overflow: hidden;
}

.admin-sidebar .nav-link::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s;
}

.admin-sidebar .nav-link:hover::before {
  left: 100%;
}

.admin-sidebar .nav-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(5px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.admin-sidebar .nav-link.router-link-active {
  color: #fff;
  background: linear-gradient(135deg, #3498db, #2980b9);
  box-shadow: 0 4px 20px rgba(52, 152, 219, 0.4);
  transform: translateX(8px);
}

.admin-sidebar .nav-link.router-link-active::after {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background: #fff;
  border-radius: 0 2px 2px 0;
}

/* Submenú */
.admin-sidebar .collapse .nav-link {
  padding: 0.5rem 1rem 0.5rem 2rem;
  margin: 0.125rem 0.5rem;
  font-size: 0.875rem;
  background: rgba(255, 255, 255, 0.05);
  border-left: 2px solid rgba(255, 255, 255, 0.2);
}

.admin-sidebar .collapse .nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  border-left-color: rgba(255, 255, 255, 0.4);
}

.admin-sidebar .collapse .nav-link.router-link-active {
  background: rgba(52, 152, 219, 0.3);
  border-left-color: #3498db;
}

/* Separador */
.admin-sidebar hr {
  border-color: rgba(255, 255, 255, 0.2);
  margin: 1rem 1rem;
}

/* Sección de reportes */
.admin-sidebar .text-muted {
  color: rgba(255, 255, 255, 0.6) !important;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

/* Botón logout */
.admin-sidebar .text-danger {
  color: #e74c3c !important;
}

.admin-sidebar .text-danger:hover {
  background: rgba(231, 76, 60, 0.1) !important;
  color: #ff6b6b !important;
}

/* Contenido principal */
.admin-main-content {
  margin-left: 280px;
  padding: 2rem;
  min-height: calc(100vh - 76px);
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding-top: 2rem;
}

/* Animaciones */
.transition-all {
  transition: all 0.3s ease;
}

/* Responsive */
@media (max-width: 991px) {
  .admin-sidebar {
    width: 260px;
  }

  .admin-main-content {
    margin-left: 260px;
  }
}

@media (max-width: 767px) {
  .admin-sidebar {
    display: none !important;
  }

  .admin-main-content {
    margin-left: 0 !important;
    padding: 1rem;
  }

  .navbar-brand span {
    display: none;
  }

  .navbar-brand i.fa-tractor {
    margin-right: 0.5rem !important;
  }
}

/* Efectos adicionales */
.admin-sidebar .nav-link i {
  width: 20px;
  text-align: center;
}


/* Gradiente para el fondo */
.admin-layout::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 20% 80%, rgba(52, 152, 219, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(155, 89, 182, 0.1) 0%, transparent 50%);
  pointer-events: none;
  z-index: -1;
}
</style>