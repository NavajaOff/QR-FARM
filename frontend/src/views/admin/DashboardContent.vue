<template>
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
</template>

<script>
import dashboardContent from '../../assets/js/dashboard-content.js';

export default dashboardContent;
</script>

<style scoped>
@import '../../assets/css/dashboard-content.css';
</style>