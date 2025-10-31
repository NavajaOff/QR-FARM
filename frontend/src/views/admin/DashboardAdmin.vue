<template>
  <div class="admin-layout">
    <!-- Header -->
    <nav class="navbar navbar-dark bg-primary">
      <div class="container-fluid">
        <div class="d-flex align-items-center w-100">
          <button
            class="btn btn-outline-light d-md-none me-2"
            type="button"
            data-bs-toggle="offcanvas"
            data-bs-target="#adminSidebar"
            aria-controls="adminSidebar"
          >
            <i class="fas fa-bars"></i>
          </button>
          <i class="fas fa-user-shield fa-lg me-2"></i>
          <span class="fw-bold">{{ userName }}</span>
          <span class="badge bg-danger ms-2">Administrador</span>
          <router-link class="navbar-brand mx-auto d-flex align-items-center" to="/admin/dashboard">
            <span class="fw-bold fs-2">QR FARM</span>
            <i class="fas fa-cow ms-2 logo-icon"></i>
          </router-link>
          <button class="btn btn-outline-light" @click="logout">
            <i class="fas fa-sign-out-alt me-1"></i>Salir
          </button>
        </div>
      </div>
    </nav>

    <!-- Sidebar -->
    <div class="d-none d-md-block admin-sidebar">
      <nav class="nav flex-column">
        <router-link class="nav-link active" to="/admin/dashboard">
          <i class="fas fa-tachometer-alt me-2"></i>Dashboard
        </router-link>
        <router-link class="nav-link" to="/admin/gestionar-usuarios">
          <i class="fas fa-users me-2"></i>Usuarios
        </router-link>
        <router-link class="nav-link" to="/admin/gestionar-ganado">
          <i class="fas fa-cow me-2"></i>Ganado
        </router-link>
        <router-link class="nav-link" to="/admin/gestionar-potreros">
          <i class="fas fa-map-marked-alt me-2"></i>Potreros
        </router-link>
        <router-link class="nav-link" to="/admin/inventario">
          <i class="fas fa-boxes me-2"></i>Inventario
        </router-link>
        <router-link class="nav-link" to="/admin/vacunacion">
          <i class="fas fa-syringe me-2"></i>Vacunación
        </router-link>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="admin-main-content">
      <div class="container-fluid py-4">
        <div class="row">
          <div class="col-12">
            <h2 class="mb-4">Panel de Administración</h2>

            <!-- Estadísticas -->
            <div class="row g-4 mb-4">
              <div class="col-md-3">
                <div class="card stats-card border-primary">
                  <div class="card-body text-center">
                    <i class="fas fa-users fa-2x text-primary mb-2"></i>
                    <h4 class="card-title">{{ estadisticas.usuarios }}</h4>
                    <p class="card-text text-muted">Usuarios Registrados</p>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card stats-card border-success">
                  <div class="card-body text-center">
                    <i class="fas fa-cow fa-2x text-success mb-2"></i>
                    <h4 class="card-title">{{ estadisticas.ganado }}</h4>
                    <p class="card-text text-muted">Total Ganado</p>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card stats-card border-info">
                  <div class="card-body text-center">
                    <i class="fas fa-map-marked-alt fa-2x text-info mb-2"></i>
                    <h4 class="card-title">{{ estadisticas.potreros }}</h4>
                    <p class="card-text text-muted">Potreros</p>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card stats-card border-warning">
                  <div class="card-body text-center">
                    <i class="fas fa-chart-line fa-2x text-warning mb-2"></i>
                    <h4 class="card-title">{{ estadisticas.salud }}%</h4>
                    <p class="card-text text-muted">Salud Promedio</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Acciones Rápidas -->
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Acciones Rápidas</h5>
              </div>
              <div class="card-body">
                <div class="row g-3">
                  <div class="col-md-4">
                    <router-link class="btn btn-primary w-100" to="/admin/gestionar-usuarios">
                      <i class="fas fa-user-plus me-2"></i>Agregar Usuario
                    </router-link>
                  </div>
                  <div class="col-md-4">
                    <router-link class="btn btn-success w-100" to="/admin/gestionar-ganado">
                      <i class="fas fa-plus-circle me-2"></i>Registrar Ganado
                    </router-link>
                  </div>
                  <div class="col-md-4">
                    <router-link class="btn btn-info w-100" to="/admin/inventario">
                      <i class="fas fa-chart-bar me-2"></i>Ver Reportes
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import authService from '../../services/authService.js';
import { ganadoAPI, potreroAPI, userAPI } from '../../services/api.js';

export default {
  name: 'DashboardAdmin',
  data() {
    return {
      userName: '',
      estadisticas: {
        usuarios: 0,
        ganado: 0,
        potreros: 0,
        salud: 0
      }
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isAdmin()) {
      this.$router.push('/login');
      return;
    }

    const user = authService.getUser();
    this.userName = user?.persona?.primer_nombre || 'Administrador';

    this.cargarEstadisticas();
  },
  methods: {
    async cargarEstadisticas() {
      try {
        // Cargar estadísticas de usuarios
        const usuariosResponse = await userAPI.getAll();
        this.estadisticas.usuarios = usuariosResponse.data?.data?.length || 0;

        // Cargar estadísticas de ganado
        const ganadoResponse = await ganadoAPI.getAll();
        this.estadisticas.ganado = ganadoResponse.data?.data?.length || 0;

        // Cargar estadísticas de potreros
        const potrerosResponse = await potreroAPI.getAll();
        this.estadisticas.potreros = potrerosResponse.data?.data?.length || 0;

        // Salud promedio simulada
        this.estadisticas.salud = Math.floor(Math.random() * 20) + 80;
      } catch (error) {
        console.error('Error cargando estadísticas:', error);
      }
    },

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
}

.admin-sidebar {
  position: fixed;
  top: 70px;
  left: 0;
  width: 250px;
  height: calc(100vh - 70px);
  background-color: #343a40;
  padding: 1rem;
  overflow-y: auto;
}

.admin-sidebar .nav-link {
  color: rgba(255, 255, 255, 0.8);
  padding: 0.75rem 1rem;
  margin-bottom: 0.25rem;
  border-radius: 0.375rem;
  transition: all 0.3s ease;
}

.admin-sidebar .nav-link:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.1);
}

.admin-sidebar .nav-link.active {
  color: #fff;
  background-color: #007bff;
}

.admin-main-content {
  margin-left: 250px;
  padding-top: 2rem;
}

.stats-card {
  transition: transform 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-5px);
}

@media (max-width: 767px) {
  .admin-sidebar {
    display: none !important;
  }

  .admin-main-content {
    margin-left: 0 !important;
  }
}
</style>