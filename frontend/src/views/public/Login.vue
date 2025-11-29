<template>
  <!-- Barra superior pública -->
  <nav class="navbar navbar-dark bg-success" aria-label="Barra principal del acceso público">
    <div class="container-fluid py-2 py-md-3 px-3 px-md-4">
      <router-link class="navbar-brand" to="/login">
        <i class="fas fa-home me-2"></i>Inicio
      </router-link>

      <router-link class="navbar-brand mx-auto d-flex align-items-center" to="/login">
        <span class="fw-bold fs-2">QR FARM</span>
        <i class="fas fa-cow ms-2 logo-icon"></i>
      </router-link>

      <div class="navbar-brand d-none d-md-block">
        <i class="fas fa-cow fa-2x"></i>
      </div>
    </div>
  </nav>

  <!-- Main Content -->
  <div class="container-fluid bg-light min-vh-100">
    <div class="row min-vh-100 align-items-center py-4 py-md-5">
      <div class="col-12 col-lg-10 col-xl-8 mx-auto">
        <div class="row g-0 bg-white rounded-4 shadow-lg overflow-hidden">

          <!-- Left Image -->
          <div class="col-12 col-md-6">
            <div class="p-3 p-sm-4 p-lg-5 h-100 d-flex flex-column justify-content-center bg-white">
              <div class="text-center mb-4">
                <img src="../../assets/images/vacas-grupo.jpg" alt="Grupo de vacas" class="img-fluid" />
              </div>
              <div class="text-center px-2 px-sm-3 px-md-4">
                <p class="text-muted mb-2">Tu aliado inteligente en la gestión ganadera.</p>
                <p class="text-muted mb-2">Simplifica el control de tu ganado, mejora la trazabilidad</p>
                <p class="text-muted mb-2">y optimiza tus procesos con tecnología QR.</p>
                <p class="text-muted fw-bold mb-0">¡Transforma tu finca hoy!</p>
              </div>
            </div>
          </div>

          <!-- Right Form -->
          <div class="col-12 col-md-6">
            <div class="p-3 p-sm-4 p-lg-5 h-100 d-flex align-items-center bg-secondary">
              <div class="w-100">
                <div class="text-center mb-4">
                  <i class="fas fa-user-circle fa-3x text-white mb-3"></i>
                  <h4 class="text-white fw-bold">Inicio de Sesión</h4>
                </div>

                <!-- Formulario Vue -->
                <form @submit.prevent="login" class="px-0 px-sm-2 px-md-3">
                  <div v-if="error" class="alert alert-danger text-center mb-3">
                    {{ error }}
                  </div>

                  <div class="form-group mb-3">
                    <input v-model="email" type="email" class="form-control form-control-lg"
                      placeholder="Email" required />
                  </div>

                  <div class="form-group mb-4">
                    <input v-model="password" type="password" class="form-control form-control-lg"
                      placeholder="Contraseña" required />
                  </div>

                  <div class="d-grid gap-2 mb-3">
                    <button type="submit" class="btn btn-success btn-lg fw-bold" :disabled="loading">
                      <span v-if="loading" class="spinner-border spinner-border-sm me-2" aria-hidden="true" aria-label="Cargando"></span>
                      {{ loading ? 'Iniciando...' : 'Iniciar Sesión' }}
                    </button>
                  </div>

                  <div class="text-center">
                    <p class="text-white mb-0">
                      ¿No tienes cuenta?
                      <router-link to="/crear_cuenta" class="text-info fw-bold">
                        Crear cuenta
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

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import Swal from 'sweetalert2';
import authService from '../../services/authService.js';

const email = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);
const router = useRouter();

function validateInput() {
  if (email.value === '' || password.value === '') {
    error.value = 'Por favor completa todos los campos';
    return false;
  }
  return true;
}

async function handleLoginSuccess() {
  await Swal.fire({
    icon: 'success',
    title: '¡Bienvenido!',
    text: 'Inicio de sesión exitoso',
    timer: 1500,
    showConfirmButton: false
  });

  try {
    sessionStorage.setItem('lastLoginEmail', email.value);
    sessionStorage.setItem('lastLoginPassword', password.value);
  } catch (storageError) {
    console.warn('No se pudieron guardar las credenciales en sessionStorage', storageError);
  }

  const redirectPath = authService.getRedirectPath();
  console.log('[LOGIN] Redirigiendo a:', redirectPath);
  console.log('[LOGIN] Rol del usuario:', authService.getRole());
  router.push(redirectPath).catch(err => {
    console.error('[LOGIN] Error en redirección:', err);
    // Si hay error, intentar redirigir al dashboard de admin por defecto para super_admin
    if (authService.isAdmin() || authService.getRole() === 'super_admin') {
      router.push('/admin/dashboard');
    } else {
      router.push('/user/inicio');
    }
  });
}

async function handleLoginError(result) {
  await Swal.fire({
    icon: 'error',
    title: 'Error de autenticación',
    text: result.message,
    confirmButtonText: 'Intentar de nuevo'
  });
  error.value = result.message;
}

function getErrorMessage(err) {
  if (err.response) {
    if (err.response.status === 401) {
      return 'Credenciales incorrectas';
    } else if (err.response.status === 500) {
      return 'Error interno del servidor';
    } else {
      return err.response.data?.message || 'Error desconocido del servidor';
    }
  } else if (err.request) {
    return 'No se pudo conectar al servidor. Verifica tu conexión a internet.';
  }
  return 'Error al conectar con el servidor';
}

async function handleConnectionError(err) {
  console.error('Error en login:', err);
  const errorMessage = getErrorMessage(err);

  await Swal.fire({
    icon: 'error',
    title: 'Error de conexión',
    text: errorMessage,
    confirmButtonText: 'Aceptar'
  });

  error.value = errorMessage;
}

async function login() {
  if (!validateInput()) return;

  loading.value = true;
  error.value = '';

  try {
    const result = await authService.login({
      email: email.value,
      password: password.value
    });

    if (result.success) {
      await handleLoginSuccess();
    } else {
      await handleLoginError(result);
    }
  } catch (err) {
    await handleConnectionError(err);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.bg-secondary {
  background-color: #5c636a !important;
}
</style>