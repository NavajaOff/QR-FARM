<template>
  <nav class="navbar navbar-dark bg-success">
    <div class="container-fluid py-2 py-md-3 px-3 px-md-4">
      <!-- Link usando Vue Router -->
      <router-link class="navbar-brand" to="/">
        <i class="fas fa-home me-2"></i>Inicio
      </router-link>

      <router-link class="navbar-brand mx-auto d-flex align-items-center" to="/">
        <span class="fw-bold fs-2">QR FARM</span>
        <i class="fas fa-cow ms-2 logo-icon"></i>
      </router-link>

      <div class="navbar-brand">
        <i class="fas fa-cow fa-2x"></i>
      </div>
    </div>
  </nav>

  <!-- Main Content -->
  <div class="container-fluid min-vh-100 bg-light-custom">
    <div class="row min-vh-100 align-items-center py-4 py-md-5">
      <div class="col-12 col-lg-10 col-xl-8 mx-auto">
        <div class="row g-0 bg-white rounded-4 shadow-lg overflow-hidden">
          
          <!-- Left Side - Image -->
          <div class="col-12 col-md-6">
            <div class="p-3 p-sm-4 p-lg-5 h-100 d-flex flex-column justify-content-center">
              <div class="text-center">
                <img 
                src="/src/assets/images/crear_cuenta.jpg" alt="Vacas Holstein - QR Farm" 
                class="img-fluid rounded-4 shadow-sm register-image"
              />
              </div>
            </div>
          </div>

          <!-- Right Side - Registration Form -->
          <div class="col-12 col-md-6">
            <div class="p-3 p-sm-4 p-lg-5 h-100 d-flex align-items-center bg-form-register">
              <div class="w-100">
                <div class="text-center mb-4">
                  <h3 class="text-white fw-bold">Crear una cuenta</h3>
                  <p class="text-white-50">Es rápido y fácil</p>
                </div>

                <form id="registerForm" class="px-0 px-sm-2 px-md-3">
                  <!-- Campos del formulario -->
                  ...
                  <div class="text-center mt-3">
                    <p class="text-white">
                      ¿Ya tienes una cuenta?
                      <router-link to="/iniciar-sesion" class="text-info fw-bold">
                        Iniciar Sesión
                      </router-link>
                    </p>
                  </div>
                </form>

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
  name: 'CrearCuenta',
};
</script>

<style scoped>
/* Tus estilos */
</style>
