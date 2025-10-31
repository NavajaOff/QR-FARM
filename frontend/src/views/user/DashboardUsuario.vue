<template>
  <div class="user-layout">
    <!-- Header -->
    <nav class="navbar navbar-dark bg-success">
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
          <span class="badge bg-info ms-2">{{ userRole }}</span>
          <router-link class="navbar-brand mx-auto d-flex align-items-center" to="/user/dashboard">
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
    <div class="d-none d-md-block user-sidebar">
      <nav class="nav flex-column">
        <router-link class="nav-link active" to="/user/dashboard">
          <i class="fas fa-home me-2"></i>Inicio
        </router-link>
        <router-link class="nav-link" to="/user/mi-ganado">
          <i class="fas fa-cow me-2"></i>Mi Ganado
        </router-link>
        <router-link class="nav-link" to="/user/vacunacion">
          <i class="fas fa-syringe me-2"></i>Vacunación
        </router-link>
        <router-link class="nav-link" to="/user/perfil">
          <i class="fas fa-user-edit me-2"></i>Mi Perfil
        </router-link>
        <router-link class="nav-link" to="/user/inventario">
          <i class="fas fa-boxes me-2"></i>Inventario
        </router-link>
        <router-link class="nav-link" to="/user/escanear-qr">
          <i class="fas fa-qrcode me-2"></i>Escanear QR
        </router-link>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="user-main-content">
      <div class="container-fluid py-4">
        <div class="row">
          <div class="col-12">
            <h2 class="mb-4">Bienvenido a QR Farm</h2>
            <p class="lead text-muted mb-4">Gestiona tu ganado de manera eficiente y segura.</p>

            <!-- Estadísticas Personales -->
            <div class="row g-4 mb-4">
              <div class="col-md-4">
                <div class="card stats-card border-success">
                  <div class="card-body text-center">
                    <i class="fas fa-cow fa-2x text-success mb-2"></i>
                    <h4 class="card-title">{{ estadisticas.ganado }}</h4>
                    <p class="card-text text-muted">Mi Ganado</p>
                  </div>
                </div>
              </div>
              <div class="col-md-4">
                <div class="card stats-card border-info">
                  <div class="card-body text-center">
                    <i class="fas fa-syringe fa-2x text-info mb-2"></i>
                    <h4 class="card-title">{{ estadisticas.vacunas }}</h4>
                    <p class="card-text text-muted">Vacunas Aplicadas</p>
                  </div>
                </div>
              </div>
              <div class="col-md-4">
                <div class="card stats-card border-warning">
                  <div class="card-body text-center">
                    <i class="fas fa-heartbeat fa-2x text-warning mb-2"></i>
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
                    <router-link class="btn btn-success w-100" to="/user/escanear-qr">
                      <i class="fas fa-qrcode me-2"></i>Escanear QR
                    </router-link>
                  </div>
                  <div class="col-md-4">
                    <router-link class="btn btn-primary w-100" to="/user/vacunacion">
                      <i class="fas fa-syringe me-2"></i>Registrar Vacuna
                    </router-link>
                  </div>
                  <div class="col-md-4">
                    <router-link class="btn btn-info w-100" to="/user/inventario">
                      <i class="fas fa-chart-bar me-2"></i>Ver Inventario
                    </router-link>
                  </div>
                </div>
              </div>
            </div>

            <!-- Información del Sistema -->
            <div class="row mt-4">
              <div class="col-12">
                <div class="alert alert-info">
                  <h6><i class="fas fa-info-circle me-2"></i>Información del Sistema</h6>
                  <p class="mb-0">Como usuario, tienes acceso a gestionar tu propio ganado, registrar vacunaciones y consultar el inventario general.</p>
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
import { ganadoAPI, vacunacionAPI } from '../../services/api.js';

export default {
  name: 'DashboardUsuario',
  data() {
    return {
      userName: '',
      userRole: 'Usuario',
      estadisticas: {
        ganado: 0,
        vacunas: 0,
        salud: 0
      }
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isUser()) {
      this.$router.push('/login');
      return;
    }

    const user = authService.getUser();
    this.userName = user?.persona?.primer_nombre || 'Usuario';
    this.userRole = user?.rol?.rol || 'Usuario';

    this.cargarEstadisticas();
  },
  methods: {
    async cargarEstadisticas() {
      try {
        const user = authService.getUser();
        const userId = user?.id;

        // Cargar ganado del usuario
        const ganadoResponse = await ganadoAPI.getAll();
        const ganadoUsuario = ganadoResponse.data?.data?.filter(g => g.id_persona === userId) || [];
        this.estadisticas.ganado = ganadoUsuario.length;

        // Cargar vacunas aplicadas
        const vacunasResponse = await vacunacionAPI.getAll();
        this.estadisticas.vacunas = vacunasResponse.data?.data?.length || 0;

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
.user-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.navbar {
  background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%) !important;
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

.user-sidebar {
  position: fixed;
  top: 70px;
  left: 0;
  width: 280px;
  height: calc(100vh - 70px);
  background: linear-gradient(180deg, #28a745 0%, #20c997 100%);
  padding: 1.5rem 1rem;
  overflow-y: auto;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.user-sidebar .nav-link {
  color: rgba(255, 255, 255, 0.95);
  padding: 0.875rem 1.25rem;
  margin-bottom: 0.5rem;
  border-radius: var(--border-radius);
  transition: var(--transition);
  font-weight: 500;
  position: relative;
}

.user-sidebar .nav-link:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.2);
  transform: translateX(5px);
}

.user-sidebar .nav-link.active {
  color: #fff;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.1) 100%);
  box-shadow: 0 4px 8px rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

.user-sidebar .nav-link i {
  width: 20px;
  margin-right: 0.75rem;
}

.user-main-content {
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

.btn-success {
  background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
  border: none;
  font-weight: 600;
}

.btn-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
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
  margin-bottom: 1rem;
}

.lead {
  color: #6c757d;
  font-size: 1.1rem;
  font-weight: 400;
  margin-bottom: 2rem;
}

.alert-info {
  background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
  border: 1px solid #b3d9ff;
  border-radius: var(--border-radius);
  color: #0c5460;
}

.alert-info h6 {
  color: #0c5460;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

@media (max-width: 768px) {
  .user-sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .user-sidebar.show {
    transform: translateX(0);
  }

  .user-main-content {
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