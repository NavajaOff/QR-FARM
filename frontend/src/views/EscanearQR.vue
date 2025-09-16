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

    <!-- Layout -->
    <div class="d-flex">
      <!-- Sidebar -->
      <div class="sidebar">
        <nav class="nav flex-column py-3">
          <router-link class="nav-link" to="/inventario">
            <i class="fas fa-boxes me-2"></i>Inventario
          </router-link>

          <a
            class="nav-link d-flex justify-content-between align-items-center"
            data-bs-toggle="collapse"
            href="#gestionMenu"
            role="button"
            aria-expanded="false"
            aria-controls="gestionMenu"
          >
            <span><i class="fas fa-tasks me-2"></i>Gestión</span>
            <i class="fas fa-chevron-down"></i>
          </a>
          <div class="collapse ps-3" id="gestionMenu">
            <router-link class="nav-link" to="/gestionar_animales">
              <i class="fas fa-cow me-2"></i>Animales
            </router-link>
            <router-link class="nav-link" to="/gestionar_potreros">
              <i class="fas fa-map-marked-alt me-2"></i>Potreros
            </router-link>
            <router-link class="nav-link" to="/registro_vacunacion">
              <i class="fas fa-syringe me-2"></i>Vacunación
            </router-link>
          </div>

          <router-link class="nav-link active" to="/escanear_qr">
            <i class="fas fa-qrcode me-2"></i>Escanear QR
          </router-link>
          <router-link class="nav-link" to="/login">
            <i class="fas fa-sign-out-alt me-2"></i>Salir
          </router-link>
        </nav>
      </div>

      <!-- Main Content -->
      <div class="main-content">
        <div class="container-fluid py-4 py-md-5">
          <div class="row justify-content-center g-4">
            <div class="col-12 col-lg-10 col-xl-8">

              <!-- Scanner Section -->
              <div class="card border-0 shadow-lg mb-4">
                <div class="card-body p-3 p-sm-4 p-lg-5">
                  <div class="scanner-area mb-4">
                    <div class="d-flex flex-column align-items-center justify-content-center" style="min-height: 300px;">
                      <div style="position: relative; width: 200px; height: 200px; margin: 20px 0;">
                        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 3px solid #007bff; border-radius: 10px;"></div>
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                          <i class="fas fa-camera fa-3x text-muted"></i>
                        </div>
                      </div>
                      <div class="text-center mt-3">
                        <h5 class="text-muted mb-2">Área de escaneo</h5>
                        <p class="text-muted mb-0">Coloca el código QR dentro del marco</p>
                      </div>
                    </div>
                  </div>

                  <!-- Botones -->
                  <div class="d-flex justify-content-center gap-3 mb-4">
                    <button class="btn btn-primary btn-lg" @click="iniciarEscaneo">
                      <i class="fas fa-play me-2"></i>Iniciar Escaneo
                    </button>
                    <button class="btn btn-outline-secondary btn-lg" @click="subirImagen">
                      <i class="fas fa-upload me-2"></i>Subir Imagen
                    </button>
                  </div>

                  <!-- Instrucciones -->
                  <div class="alert alert-info">
                    <h6><i class="fas fa-info-circle me-2"></i>Instrucciones:</h6>
                    <ul class="text-start mb-0">
                      <li>Asegúrate de tener buena iluminación</li>
                      <li>Mantén el código QR dentro del marco</li>
                      <li>Espera a que el sistema reconozca el código</li>
                      <li>La información del animal aparecerá automáticamente</li>
                    </ul>
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
  name: "EscanearQR",
  methods: {
    iniciarEscaneo() {
      Swal.fire('Iniciar Escaneo', 'Aquí se activaría la cámara', 'info');
    },
    subirImagen() {
      Swal.fire('Subir Imagen', 'Aquí se subiría una imagen con código QR', 'info');
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
.main-content { margin-left: 250px; margin-top: 0; }
@media (max-width: 767px) { .sidebar { display: none !important; } .main-content { margin-left: 0 !important; } }
.scanner-area { background: #f8f9fa; border: 3px dashed #dee2e6; border-radius: 15px; padding: 60px; position: relative; }
</style>
