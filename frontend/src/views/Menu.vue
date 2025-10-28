<template>
  <div>
    <!-- Header -->
    <nav class="navbar navbar-dark bg-success">
      <div class="container-fluid">
        <div class="d-flex align-items-center w-100">
          <button
            class="btn btn-outline-light d-md-none me-2"
            type="button"
            data-bs-toggle="offcanvas"
            data-bs-target="#sidebarMenu"
            aria-controls="sidebarMenu"
          >
            <i class="fas fa-bars"></i>
          </button>
          <i class="fas fa-user-circle fa-lg me-2"></i>
          <span class="fw-bold">Usuario</span>
          <router-link class="navbar-brand mx-auto d-flex align-items-center" to="/menu">
            <span class="fw-bold fs-2">QR FARM</span>
            <i class="fas fa-cow ms-2 logo-icon"></i>
          </router-link>
          <div class="navbar-brand ms-auto">
            <i class="fas fa-cow fa-2x"></i>
          </div>
        </div>
      </div>
    </nav>

    <!-- Notification Icon -->
    <div class="notification-icon" style="position: fixed; top: 70px; right: 20px; z-index: 1000;">
      <button class="btn btn-light rounded-circle shadow">
        <i class="fas fa-bell fa-lg"></i>
        <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">3</span>
      </button>
    </div>

    <!-- Offcanvas Sidebar (móvil) -->
    <div class="offcanvas offcanvas-start d-md-none" tabindex="-1" id="sidebarMenu">
      <div class="offcanvas-header">
        <h5 class="offcanvas-title">Menú</h5>
        <button type="button" class="btn-close text-reset" data-bs-dismiss="offcanvas"></button>
      </div>
      <div class="offcanvas-body">
        <nav class="nav flex-column">
          <router-link class="nav-link" to="/inventario">
            <i class="fas fa-boxes me-2"></i>Inventario
          </router-link>
          <a class="nav-link d-flex justify-content-between align-items-center" data-bs-toggle="collapse" href="#gestionMenuMobile">
            <span><i class="fas fa-tasks me-2"></i>Gestión</span>
            <i class="fas fa-chevron-down"></i>
          </a>
          <div class="collapse ps-3" id="gestionMenuMobile">
            <router-link class="nav-link" to="/gestionar_animales">
              <i class="fas fa-cow me-2"></i>Ganado
            </router-link>
            <router-link class="nav-link" to="/gestionar_potreros">
              <i class="fas fa-map-marked-alt me-2"></i>Potreros
            </router-link>
            <router-link class="nav-link" to="/registro_vacunacion">
              <i class="fas fa-syringe me-2"></i>Vacunación
            </router-link>
          </div>
          <router-link class="nav-link" to="/escanear_qr">
            <i class="fas fa-qrcode me-2"></i>Escanear QR
          </router-link>
          <router-link class="nav-link" to="/login">
            <i class="fas fa-sign-out-alt me-2"></i>Salir
          </router-link>
        </nav>
      </div>
    </div>

    <!-- Sidebar fijo desktop -->
    <div class="d-none d-md-block sidebar">
      <nav class="nav flex-column">
        <router-link class="nav-link active" to="/inventario">
          <i class="fas fa-boxes me-2"></i>Inventario
        </router-link>
        <a class="nav-link d-flex justify-content-between align-items-center" data-bs-toggle="collapse" href="#gestionMenuDesktop">
          <span><i class="fas fa-tasks me-2"></i>Gestión</span>
          <i class="fas fa-chevron-down"></i>
        </a>
        <div class="collapse ps-3" id="gestionMenuDesktop">
          <router-link class="nav-link" to="/gestionar_animales">
            <i class="fas fa-cow me-2"></i>Ganado
          </router-link>
          <router-link class="nav-link" to="/gestionar_potreros">
            <i class="fas fa-map-marked-alt me-2"></i>Potreros
          </router-link>
          <router-link class="nav-link" to="/registro_vacunacion">
            <i class="fas fa-syringe me-2"></i>Vacunación
          </router-link>
        </div>
        <router-link class="nav-link" to="/escanear_qr">
          <i class="fas fa-qrcode me-2"></i>Escanear QR
        </router-link>
        <router-link class="nav-link" to="/login">
          <i class="fas fa-sign-out-alt me-2"></i>Salir
        </router-link>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="main-content d-flex align-items-center justify-content-center">
      <div class="container-fluid py-4 py-md-5">
        <div class="row justify-content-center g-4">
          <div class="col-12 col-lg-10 col-xl-8">
            <div class="text-center mb-4 mb-md-5">
              <h2 class="fw-bold text-dark mb-2 mb-md-3">
                ¡Bienvenido a QR Farm!
              </h2>
              <p class="lead text-muted">Gestiona tu finca ganadera de manera inteligente</p>
            </div>
            <div class="card border-0 shadow-lg">
              <div class="card-body p-3 p-sm-4 p-lg-5">
                <div class="text-center mb-4">
                  <img src="../assets/images/vascas-holstein.jpg" alt="Vacas Holstein" class="img-fluid rounded-4 shadow-sm" style="max-height: 350px; width: 100%; object-fit: cover;">
                </div>
                <div class="row justify-content-center g-3 mb-4">
                  <div class="col-12 col-md-4 d-flex justify-content-center">
                    <div class="p-3 bg-light rounded-4 text-center h-100 w-100">
                      <i class="fas fa-cow fa-2x text-success mb-2"></i>
                      <h5 class="fw-bold mb-1">{{ estadisticas.animales }}</h5>
                      <small class="text-muted">Ganado</small>
                    </div>
                  </div>
                  <div class="col-12 col-md-4 d-flex justify-content-center">
                    <div class="p-3 bg-light rounded-4 text-center h-100 w-100">
                      <i class="fas fa-map-marked-alt fa-2x text-primary mb-2"></i>
                      <h5 class="fw-bold mb-1">{{ estadisticas.potreros }}</h5>
                      <small class="text-muted">Potreros</small>
                    </div>
                  </div>
                  <div class="col-12 col-md-4 d-flex justify-content-center">
                    <div class="p-3 bg-light rounded-4 text-center h-100 w-100">
                      <i class="fas fa-chart-line fa-2x text-warning mb-2"></i>
                      <h5 class="fw-bold mb-1">{{ estadisticas.salud }}%</h5>
                      <small class="text-muted">Salud Promedio</small>
                    </div>
                  </div>
                </div>
                <div class="text-center px-2 px-sm-3 px-md-4">
                  <h5 class="fw-bold mb-3 text-success">Acciones Rápidas</h5>
                  <div class="d-flex justify-content-center gap-2 gap-md-3 flex-wrap">
                    <router-link class="btn btn-success" to="/escanear_qr" style="min-width: 130px;">
                      <i class="fas fa-qrcode me-1"></i>Escanear QR
                    </router-link>
                    <router-link class="btn btn-primary" to="/gestionar_animales" style="min-width: 130px;">
                      <i class="fas fa-plus-circle me-1"></i>Registrar Ganado
                    </router-link>
                    <router-link class="btn btn-info" to="/inventario" style="min-width: 130px;">
                      <i class="fas fa-chart-bar me-1"></i>Ver Reportes
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
import axios from 'axios';

export default {
  name: "Menu",
  data() {
    return {
      estadisticas: {
        animales: 0,
        potreros: 0,
        salud: 0
      }
    };
  },
  mounted() {
    this.cargarEstadisticas();
  },
  methods: {
    async cargarEstadisticas() {
      try {
        // Cargar estadísticas de ganado
        const ganadoResponse = await axios.get('http://localhost:5000/api/ganados/');
        this.estadisticas.animales = ganadoResponse.data.data ? ganadoResponse.data.data.length : 0;

        // Cargar estadísticas de potreros
        const potrerosResponse = await axios.get('http://localhost:5000/api/potreros/');
        this.estadisticas.potreros = potrerosResponse.data.data ? potrerosResponse.data.data.length : 0;

        // Calcular salud promedio (simulado por ahora)
        this.estadisticas.salud = this.calcularSaludPromedio();

      } catch (error) {
        console.error('Error cargando estadísticas:', error);
        // Valores por defecto
        this.estadisticas = {
          animales: 0,
          potreros: 0,
          salud: 0
        };
      }
    },
    calcularSaludPromedio() {
      // Lógica para calcular salud promedio basada en datos reales
      // Por ahora retornamos un valor simulado
      return Math.floor(Math.random() * 20) + 80; // Entre 80-99%
    }
  }
};
</script>

<style scoped>
.sidebar {
  min-width: 250px;
  max-width: 250px;
  position: fixed;
  top: 80px;
  left: 0;
  height: calc(100vh - 80px);
  background-color: #6c757d;
  z-index: 1020;
  padding: 1rem;
  overflow-y: auto;
}
@media (max-width: 767px) {
  .sidebar {
    display: none !important;
  }
}
.main-content {
  margin-left: 250px;
}
@media (max-width: 767px) {
  .main-content {
    margin-left: 0 !important;
  }
}
</style>