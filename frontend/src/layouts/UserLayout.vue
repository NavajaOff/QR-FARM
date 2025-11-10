<template>
  <div class="user-layout">
    <!-- Barra superior de navegación -->
    <nav class="navbar navbar-dark bg-success" aria-label="Barra principal del usuario">
      <div class="container-fluid">
        <div class="d-flex align-items-center w-100">
          <button
            class="btn btn-outline-light d-md-none me-2"
            type="button"
            data-bs-toggle="offcanvas"
            data-bs-target="#userSidebar"
            aria-controls="userSidebar"
          >
            <i class="fas fa-bars"></i>
          </button>
          <i class="fas fa-user fa-lg me-2"></i>
          <span class="fw-bold">{{ userName }}</span>
          <span class="badge bg-info ms-2">Usuario</span>
          <router-link class="navbar-brand mx-auto d-flex align-items-center" to="/user/inicio">
            <span class="fw-bold fs-2">QR FARM</span>
            <i class="fas fa-cow ms-2 logo-icon"></i>
          </router-link>
          <button class="btn btn-outline-light" @click="logout">
            <i class="fas fa-sign-out-alt me-1"></i>Salir
          </button>
        </div>
      </div>
    </nav>

    <!-- Menú lateral fijo -->
    <div class="d-none d-md-block user-sidebar">
      <nav class="nav flex-column" aria-label="Menú lateral del usuario">
        <router-link class="nav-link" to="/user/inicio">
          <i class="fas fa-home me-2"></i>Inicio
        </router-link>
        <router-link class="nav-link" to="/user/ganado">
          <i class="fas fa-cow me-2"></i>Mi Ganado
        </router-link>
        <router-link class="nav-link" to="/user/potreros">
          <i class="fas fa-map-marked-alt me-2"></i>Potreros
        </router-link>
        <router-link class="nav-link" to="/user/reportes">
          <i class="fas fa-chart-line me-2"></i>Reportes
        </router-link>
        <router-link class="nav-link" to="/user/registro-vacunacion">
          <i class="fas fa-syringe me-2"></i>Vacunación
        </router-link>
        <router-link class="nav-link" to="/user/perfil">
          <i class="fas fa-user-edit me-2"></i>Perfil
        </router-link>
        <router-link class="nav-link" to="/user/qr">
          <i class="fas fa-qrcode me-2"></i>Escanear QR
        </router-link>
      </nav>
    </div>

    <!-- Contenido principal -->
    <div class="user-main-content">
      <router-view />
    </div>
  </div>
</template>

<script>
import authService from '../services/authService.js';

export default {
  name: 'UserLayout',
  data() {
    return {
      userName: ''
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isUser()) {
      this.$router.push('/login');
      return;
    }

    const user = authService.getUser();
    this.userName = user?.persona?.primer_nombre || 'Usuario';
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
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1030;
  background: #1f5c38 !important;
}

.user-layout {
  min-height: 100vh;
  padding-top: 76px;
}

.user-sidebar {
  position: fixed;
  top: 76px;
  left: 0;
  width: 250px;
  height: calc(100vh - 76px);
  background-color: #343a40;
  padding: 1rem;
  overflow-y: auto;
  margin-top: -1px;
}

.user-sidebar .nav-link {
  color: rgba(255, 255, 255, 0.8);
  padding: 0.75rem 1rem;
  margin-bottom: 0.25rem;
  border-radius: 0.375rem;
  transition: all 0.3s ease;
}

.user-sidebar .nav-link:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.1);
}

.user-sidebar .nav-link.router-link-active {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

.user-main-content {
  margin-left: 0;
  padding-top: 1.5rem;
}

@media (min-width: 768px) {
  .user-main-content {
    margin-left: 250px;
  }
}

@media (max-width: 767px) {
  .user-sidebar {
    display: none !important;
  }

  .user-main-content {
    margin-left: 0 !important;
  }
}
</style>