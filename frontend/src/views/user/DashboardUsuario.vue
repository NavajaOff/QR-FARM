<template>
  <div class="user-layout">
    <!-- Header -->
    <nav class="navbar navbar-dark bg-success" aria-label="Navegación principal de usuario">
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
      <nav class="nav flex-column" aria-label="Menú de navegación de usuario">
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
                    <router-link class="btn btn-info w-100" to="/user/reportes">
                      <i class="fas fa-chart-bar me-2"></i>Ver Reportes
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
                  <p class="mb-0">Como usuario, tienes acceso a gestionar tu propio ganado y registrar vacunaciones.</p>
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
import dashboardUsuario from '../../assets/js/dashboard-usuario.js';

export default dashboardUsuario;
</script>

<style scoped>
@import '../../assets/css/dashboard-usuario.css';
</style>