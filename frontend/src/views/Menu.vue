<template>
  <div>
    <!-- Header -->
    <nav class="navbar navbar-dark bg-success">
      <div class="container-fluid">
        <div class="d-flex align-items-center">
          <i class="fas fa-user-circle fa-lg me-2"></i>
          <span class="fw-bold">Usuario</span>
        </div>
        <router-link class="navbar-brand mx-auto d-flex align-items-center" to="/">
          <span class="fw-bold fs-2">QR FARM</span>
          <i class="fas fa-cow ms-2 logo-icon"></i>
        </router-link>
        <div class="navbar-brand">
          <i class="fas fa-cow fa-2x"></i>
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
    <div class="d-flex">
      <!-- Sidebar -->
      <div class="sidebar">
        <nav class="nav flex-column">
          <router-link class="nav-link active" to="/inventario">
            <i class="fas fa-boxes me-2"></i>Inventario
          </router-link>
          <router-link class="nav-link" to="/gestionar_animales">
            <i class="fas fa-cow me-2"></i>Gestionar animales
          </router-link>
          <router-link class="nav-link" to="/gestionar_potreros">
            <i class="fas fa-map-marked-alt me-2"></i>Gestionar potreros
          </router-link>
          <router-link class="nav-link" to="/escanear_qr">
            <i class="fas fa-qrcode me-2"></i>Escanear QR
          </router-link>
          <router-link class="nav-link" to="/registro_vacunacion">
            <i class="fas fa-syringe me-2"></i>Registro Vacunación
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
              <!-- Título principal -->
              <div class="text-center mb-4 mb-md-5">
                <h2 class="fw-bold text-dark mb-2 mb-md-3">
                  ¡Bienvenido, <span id="nombreUsuario">Nombre del usuario</span>!
                </h2>
                <p class="lead text-muted">
                  Gestiona tu finca de manera inteligente con QR Farm
                </p>
              </div>
              <!-- Card principal -->
              <div class="card border-0 shadow-lg">
                <div class="card-body p-3 p-sm-4 p-lg-5">
                  <!-- Imagen -->
                  <div class="text-center mb-4">
                    <img src="/src/assets/images/vascas-holstein.jpg" 
                         alt="Vacas Holstein - QR Farm" 
                         class="img-fluid rounded-4 shadow-sm"
                         style="max-height: 350px; width: 100%; object-fit: cover;">
                  </div>
                  <!-- Estadísticas -->
                  <div class="row justify-content-center g-3 mb-4">
                    <div class="col-12 col-md-4 d-flex justify-content-center">
                      <div class="p-3 bg-light rounded-4 text-center h-100 w-100">
                        <i class="fas fa-cow fa-2x text-success mb-2"></i>
                        <h5 class="fw-bold mb-1">125</h5>
                        <small class="text-muted">Animales</small>
                      </div>
                    </div>
                    <div class="col-12 col-md-4 d-flex justify-content-center">
                      <div class="p-3 bg-light rounded-4 text-center h-100 w-100">
                        <i class="fas fa-qrcode fa-2x text-primary mb-2"></i>
                        <h5 class="fw-bold mb-1">125</h5>
                        <small class="text-muted">Códigos QR</small>
                      </div>
                    </div>
                    <div class="col-12 col-md-4 d-flex justify-content-center">
                      <div class="p-3 bg-light rounded-4 text-center h-100 w-100">
                        <i class="fas fa-chart-line fa-2x text-warning mb-2"></i>
                        <h5 class="fw-bold mb-1">98%</h5>
                        <small class="text-muted">Salud</small>
                      </div>
                    </div>
                  </div>
                  <!-- Acciones Rápidas -->
                  <div class="text-center px-2 px-sm-3 px-md-4">
                    <h5 class="fw-bold mb-3 text-success">Acciones Rápidas</h5>
                    <div class="d-flex justify-content-center gap-2 gap-md-3 flex-wrap">
                      <router-link class="btn btn-success" to="/escanear_qr" style="min-width: 130px;">
                        <i class="fas fa-qrcode me-1"></i>Escanear QR
                      </router-link>
                      <router-link class="btn btn-primary" to="/gestionar_animales" style="min-width: 130px;">
                        <i class="fas fa-plus-circle me-1"></i>Registrar Animal
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
  </div>
</template>

<script>
export default {
  name: 'Menu',
};
</script>

<style scoped>
/* Puedes agregar estilos específicos aquí */
</style>
