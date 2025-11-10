<template>
  <nav class="navbar navbar-dark bg-success" aria-label="Barra principal para creación de cuentas">
    <div class="container-fluid py-2 py-md-3 px-3 px-md-4">
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
                    <!-- Registration Form - Full Width -->
                    <div class="col-12">
                        <div class="p-4 p-md-5 bg-form-register">
                            <div class="w-100">
                                <div class="text-center mb-4">
                                    <h3 class="text-white fw-bold">Crear una cuenta</h3>
                                    <p class="text-white-50">Regístrate para gestionar tu finca ganadera</p>
                                </div>

                                <form id="registerForm" class="px-0 px-sm-2 px-md-3" @submit.prevent="handleSubmit">
                                    <div class="row g-3 mb-3">
                                        <div class="col-6">
                                            <input type="text" class="form-control" id="primerNombre" v-model="form.primerNombre" placeholder="Primer Nombre" required>
                                        </div>
                                        <div class="col-6">
                                            <input type="text" class="form-control" id="segundoNombre" v-model="form.segundoNombre" placeholder="Segundo Nombre">
                                        </div>
                                    </div>

                                    <div class="row g-3 mb-3">
                                        <div class="col-6">
                                            <input type="text" class="form-control" id="primerApellido" v-model="form.primerApellido" placeholder="Primer Apellido" required>
                                        </div>
                                        <div class="col-6">
                                            <input type="text" class="form-control" id="segundoApellido" v-model="form.segundoApellido" placeholder="Segundo Apellido">
                                        </div>
                                    </div>

                                    <div class="row g-3 mb-3">
                                        <div class="col-12">
                                            <input type="tel" class="form-control" id="telefono" v-model="form.telefono" placeholder="Número de teléfono" required>
                                        </div>
                                    </div>

                                    <div class="row g-3 mb-3">
                                        <div class="col-6">
                                            <input type="email" class="form-control" id="email" v-model="form.email" placeholder="Email" required>
                                        </div>
                                        <div class="col-6">
                                            <input type="password" class="form-control" id="password" v-model="form.password" placeholder="Contraseña" required>
                                        </div>
                                    </div>


                                    <div class="mb-3 form-check">
                                        <input type="checkbox" class="form-check-input" id="terminos" v-model="form.terminos" required>
                                        <label class="form-check-label text-white" for="terminos">
                                            Acepto los <a href="#" class="text-info">términos y condiciones</a> y la <a href="#" class="text-info">política de privacidad</a>
                                        </label>
                                    </div>

                                    <div class="d-grid">
                                        <button type="submit" class="btn btn-success btn-lg fw-bold" :disabled="loading">
                                            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                                            {{ loading ? 'Creando cuenta...' : 'Crear Cuenta' }}
                                        </button>
                                    </div>

                                    <!-- Mensajes de error y éxito -->
                                    <div v-if="error" class="alert alert-danger mt-3" role="alert">
                                        {{ error }}
                                    </div>
                                    <div v-if="success" class="alert alert-success mt-3" role="alert">
                                        {{ success }}
                                    </div>

                                    <div class="text-center mt-3">
                                        <p class="text-white">¿Ya tienes una cuenta?
                                            <router-link to="/login">Iniciar Sesión</router-link>
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
import { authAPI } from '../../services/api.js';

export default {
  name: 'CrearCuenta',
  data() {
    return {
      form: {
        primerNombre: '',
        segundoNombre: '',
        primerApellido: '',
        segundoApellido: '',
        telefono: '',
        email: '',
        password: '',
        terminos: false
      },
      loading: false,
      error: null,
      success: null
    };
  },
  methods: {
    async handleSubmit() {
      this.loading = true;
      this.error = null;
      this.success = null;

      try {
        // Validar campos requeridos
        if (!this.form.primerNombre || !this.form.primerApellido || !this.form.email ||
            !this.form.password || !this.form.terminos) {
          throw new Error('Por favor complete todos los campos requeridos');
        }

        // Preparar datos para enviar
        const userData = {
          primer_nombre: this.form.primerNombre,
          segundo_nombre: this.form.segundoNombre || null,
          primer_apellido: this.form.primerApellido,
          segundo_apellido: this.form.segundoApellido || null,
          email: this.form.email,
          telefono: this.form.telefono || null,
          password: this.form.password
        };

        // Usar el servicio de API centralizado
        const response = await authAPI.register(userData);

        if (response.data.status === 'success') {
          this.success = 'Cuenta creada exitosamente. Redirigiendo al login...';
          setTimeout(() => {
            this.$router.push('/login');
          }, 2000);
        } else {
          throw new Error(response.data.message || 'Error al crear la cuenta');
        }
      } catch (error) {
        let errorMessage = 'Error al crear la cuenta';

        if (error.response?.data?.message) {
          errorMessage = error.response.data.message;
        } else if (error.message) {
          errorMessage = error.message;
        }

        this.error = errorMessage;
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.bg-form-register {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
}
</style>
