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
        <router-link class="nav-link" to="/admin/perfil">
          <i class="fas fa-user-edit me-2"></i>Perfil
        </router-link>
        <router-link class="nav-link" to="/admin/escanear-qr">
          <i class="fas fa-qrcode me-2"></i>Escanear QR
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.navbar {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%) !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border: none;
}

.navbar-brand {
  font-weight: 700;
  font-size: 1.5rem;
  color: white !important;
}

.logo-icon {
  color: #ffc107;
}

.admin-sidebar {
  position: fixed;
  top: 70px;
  left: 0;
  width: 280px;
  height: calc(100vh - 70px);
  background: linear-gradient(180deg, #343a40 0%, #495057 100%);
  padding: 1.5rem 1rem;
  overflow-y: auto;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.admin-sidebar .nav-link {
  color: rgba(255, 255, 255, 0.9);
  padding: 0.875rem 1.25rem;
  margin-bottom: 0.5rem;
  border-radius: var(--border-radius);
  transition: var(--transition);
  font-weight: 500;
  position: relative;
}

.admin-sidebar .nav-link:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.15);
  transform: translateX(5px);
}

.admin-sidebar .nav-link.active {
  color: #fff;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
}

.admin-sidebar .nav-link i {
  width: 20px;
  margin-right: 0.75rem;
}

.admin-main-content {
  margin-left: 280px;
  padding-top: 2rem;
  background-color: #f8f9fa;
  min-height: calc(100vh - 70px);
}

.stats-card {
  border: none !important;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow);
  transition: var(--transition);
  background: white;
}

.stats-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
}

.stats-card .card-body {
  padding: 2rem 1.5rem;
}

.stats-card i {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.stats-card h4 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.stats-card p {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6c757d;
}

.btn-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  border: none;
  font-weight: 600;
}

.btn-success {
  background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
  border: none;
  font-weight: 600;
}

.btn-info {
  background: linear-gradient(135deg, #17a2b8 0%, #117a8b 100%);
  border: none;
  font-weight: 600;
}

.card {
  border: none;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow);
}

.card-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #dee2e6;
  font-weight: 600;
  color: #495057;
}

h2 {
  color: #343a40;
  font-weight: 700;
  margin-bottom: 2rem;
}

.alert-info {
  background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
  border: 1px solid #b3d9ff;
  border-radius: var(--border-radius);
}

@media (max-width: 768px) {
  .admin-sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .admin-sidebar.show {
    transform: translateX(0);
  }

  .admin-main-content {
    margin-left: 0 !important;
  }

  .stats-card .card-body {
    padding: 1.5rem 1rem;
  }

  .stats-card h4 {
    font-size: 1.5rem;
  }

  .navbar-brand {
    font-size: 1.25rem;
  }
}

@media (max-width: 576px) {
  .container-fluid {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }

  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }

  .card-body .row .col-md-4 {
    margin-bottom: 1rem;
  }
}
</style>