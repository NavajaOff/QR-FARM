<template>
  <div class="admin-layout">
    <!-- Header -->
    <nav class="navbar navbar-dark bg-primary" aria-label="Navegación principal de administrador">
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
      <nav class="nav flex-column" aria-label="Menú de navegación de administrador">
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
        <router-link class="nav-link" to="/admin/scan-qr">
          <i class="fas fa-qrcode me-2"></i>Escanear QR
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
                    <router-link class="btn btn-info w-100" to="/admin/reportes">
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
import dashboardAdmin from '../../assets/js/dashboard-admin.js';

export default dashboardAdmin;
</script>

<style scoped>
@import '../../assets/css/dashboard-admin.css';
</style>