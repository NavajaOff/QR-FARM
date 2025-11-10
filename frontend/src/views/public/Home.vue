<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-dark bg-success" aria-label="Navegación principal del sitio público">
      <div class="container-fluid py-2 py-md-3 px-3 px-md-4">
        <router-link class="navbar-brand d-flex align-items-center" to="/">
          <i class="fas fa-cow me-2 logo-icon"></i>
          <span class="fw-bold fs-2">QR FARM</span>
        </router-link>
        
        <div class="d-flex align-items-center">
          <router-link class="btn btn-outline-light me-2" to="/contacto" role="button">
            <i class="fas fa-phone me-1"></i>Contacto
          </router-link>
          <router-link class="btn btn-light" to="/login" role="button">
            <i class="fas fa-user me-1"></i>Iniciar Sesión
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section bg-light py-4 py-md-5">
      <div class="container-fluid">
        <div class="row align-items-center min-vh-100 g-4">
          <div class="col-12 col-lg-10 col-xl-8 mx-auto">
            <div class="row align-items-center g-4">
              <!-- Image Column -->
              <div class="col-12 col-md-6">
                <div class="text-center p-3 p-md-4">
                  <img src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-C7VwFKE2Ge08TsJBkbkKkXUqUGwMMu.png" 
                       alt="Ganado en pastizales verdes - QR Farm" 
                       class="img-fluid rounded-4 shadow-lg">
                </div>
              </div>
              <!-- Content Column -->
              <div class="col-12 col-md-6">
                <div class="text-center text-md-start p-3 p-md-4">
                  <h1 class="display-4 fw-bold text-dark mb-3 mb-md-4">
                    Tu aliado inteligente en la gestión ganadera
                  </h1>
                  <p class="lead text-muted mb-3 mb-md-4">
                    Simplifica el control de tu ganado, mejora la trazabilidad y optimiza tus procesos con tecnología QR.
                    <br><strong>¡Transforma tu finca hoy!</strong>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: "Home",
};
</script>

<style scoped>
.hero-section {
  min-height: 100vh;
}

.logo-icon {
  font-size: 1.5rem;
}
</style>