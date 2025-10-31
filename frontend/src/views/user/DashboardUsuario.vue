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
          <span class="badge bg-info ms-2">Usuario</span>
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
}

.user-sidebar {
  position: fixed;
  top: 70px;
  left: 0;
  width: 250px;
  height: calc(100vh - 70px);
  background-color: #28a745;
  padding: 1rem;
  overflow-y: auto;
}

.user-sidebar .nav-link {
  color: rgba(255, 255, 255, 0.9);
  padding: 0.75rem 1rem;
  margin-bottom: 0.25rem;
  border-radius: 0.375rem;
  transition: all 0.3s ease;
}

.user-sidebar .nav-link:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.2);
}

.user-sidebar .nav-link.active {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.3);
  font-weight: bold;
}

.user-main-content {
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
  .user-sidebar {
    display: none !important;
  }

  .user-main-content {
    margin-left: 0 !important;
  }
}
</style>