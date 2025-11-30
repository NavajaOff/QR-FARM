<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <h2 class="mb-4">Inicio</h2>

        <!-- Estadísticas del usuario -->
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
                <i class="fas fa-map-marked-alt fa-2x text-info mb-2"></i>
                <h4 class="card-title">{{ estadisticas.potreros }}</h4>
                <p class="card-text text-muted">Potreros</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card stats-card border-warning">
              <div class="card-body text-center">
                <i class="fas fa-syringe fa-2x text-warning mb-2"></i>
                <h4 class="card-title">{{ estadisticas.vacunaciones }}</h4>
                <p class="card-text text-muted">Vacunaciones Registradas</p>
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
              <div class="col-md-4 col-lg-3">
                <router-link class="btn btn-success w-100" to="/user/ganado">
                  <i class="fas fa-plus-circle me-2"></i>Agregar Ganado
                </router-link>
              </div>
              <div class="col-md-4 col-lg-3">
                <router-link class="btn btn-info w-100" to="/user/potreros">
                  <i class="fas fa-map-marked-alt me-2"></i>Ver Potreros
                </router-link>
              </div>
              <div class="col-md-4 col-lg-3">
                <router-link class="btn btn-warning w-100" to="/user/qr">
                  <i class="fas fa-qrcode me-2"></i>Escanear QR
                </router-link>
              </div>
              <div class="col-md-4 col-lg-3">
                <router-link class="btn btn-outline-primary w-100" to="/user/reportes">
                  <i class="fas fa-chart-line me-2"></i>Ver Reportes
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Información del usuario -->
        <div class="card mt-4">
          <div class="card-header">
            <h5 class="mb-0">Mi Información</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <p><strong>Nombre:</strong> {{ userInfo.nombre }}</p>
                <p><strong>Email:</strong> {{ userInfo.email }}</p>
              </div>
              <div class="col-md-6">
                <p><strong>Rol:</strong> Usuario</p>
                <p><strong>Estado:</strong> <span class="badge bg-success">Activo</span></p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export { default } from '../../assets/js/dashboard-content-usuario.js';
</script>

<style scoped>
@import '../../assets/css/dashboard-content-usuario.css';
</style>