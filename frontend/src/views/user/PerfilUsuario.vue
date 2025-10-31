<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">
            <i class="fas fa-user-edit me-2 text-success"></i>Mi Perfil
          </h2>
        </div>

       <div class="row">
         <div class="col-md-8">
                <div class="card">
                  <div class="card-header">
                    <h5 class="mb-0">Información Personal</h5>
                  </div>
                  <div class="card-body">
                    <form @submit.prevent="updateProfile">
                      <div class="row g-3">
                        <div class="col-md-6">
                          <label class="form-label">Primer Nombre</label>
                          <input type="text" class="form-control" v-model="profile.primerNombre" required>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label">Segundo Nombre</label>
                          <input type="text" class="form-control" v-model="profile.segundoNombre">
                        </div>
                        <div class="col-md-6">
                          <label class="form-label">Primer Apellido</label>
                          <input type="text" class="form-control" v-model="profile.primerApellido" required>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label">Segundo Apellido</label>
                          <input type="text" class="form-control" v-model="profile.segundoApellido">
                        </div>
                        <div class="col-md-6">
                          <label class="form-label">Email</label>
                          <input type="email" class="form-control" v-model="profile.email" required readonly>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label">Teléfono</label>
                          <input type="tel" class="form-control" v-model="profile.telefono">
                        </div>
                      </div>

                      <div class="mt-4">
                        <button type="submit" class="btn btn-primary" :disabled="loading">
                          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                          Actualizar Perfil
                        </button>
                      </div>

                      <div v-if="message" class="alert mt-3" :class="messageType === 'success' ? 'alert-success' : 'alert-danger'">
                        {{ message }}
                      </div>
                    </form>
                  </div>
                </div>
              </div>

              <div class="col-md-4">
                <div class="card">
                  <div class="card-header">
                    <h5 class="mb-0">Información de la Cuenta</h5>
                  </div>
                  <div class="card-body">
                    <div class="mb-3">
                      <strong>Rol:</strong>
                      <span class="badge bg-info ms-2">{{ userRole }}</span>
                    </div>
                    <div class="mb-3">
                      <strong>Estado:</strong>
                      <span class="badge bg-success ms-2">Activo</span>
                    </div>
                    <div class="mb-3">
                      <strong>Fecha de Registro:</strong>
                      <span class="text-muted">{{ formatDate(user?.persona?.fecha_creacion) }}</span>
                    </div>
                  </div>
                </div>

                <div class="card mt-3">
                  <div class="card-header">
                    <h5 class="mb-0">Cambiar Contraseña</h5>
                  </div>
                  <div class="card-body">
                    <form @submit.prevent="changePassword">
                      <div class="mb-3">
                        <label class="form-label">Contraseña Actual</label>
                        <input type="password" class="form-control" v-model="passwordData.current" required>
                      </div>
                      <div class="mb-3">
                        <label class="form-label">Nueva Contraseña</label>
                        <input type="password" class="form-control" v-model="passwordData.new" required>
                      </div>
                      <div class="mb-3">
                        <label class="form-label">Confirmar Nueva Contraseña</label>
                        <input type="password" class="form-control" v-model="passwordData.confirm" required>
                      </div>
                      <button type="submit" class="btn btn-warning w-100" :disabled="passwordLoading">
                        <span v-if="passwordLoading" class="spinner-border spinner-border-sm me-2"></span>
                        Cambiar Contraseña
                      </button>
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
import authService from '../../services/authService.js';

export default {
  name: 'PerfilUsuario',
  data() {
    return {
      userName: '',
      user: null,
      userRole: '',
      loading: false,
      passwordLoading: false,
      message: '',
      messageType: '',
      profile: {
        primerNombre: '',
        segundoNombre: '',
        primerApellido: '',
        segundoApellido: '',
        email: '',
        telefono: ''
      },
      passwordData: {
        current: '',
        new: '',
        confirm: ''
      }
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isUser()) {
      this.$router.push('/login');
      return;
    }

    this.user = authService.getUser();
    this.userRole = authService.getRole();
    this.userName = this.user?.persona?.primer_nombre || 'Usuario';

    this.loadProfile();
  },

  watch: {
    '$route'(to, from) {
      // Forzar recarga cuando se navega a esta ruta
      if (to.name === 'PerfilUsuario') {
        this.loadProfile();
      }
    }
  },
  methods: {
    loadProfile() {
      if (this.user?.persona) {
        this.profile = {
          primerNombre: this.user.persona.primer_nombre || '',
          segundoNombre: this.user.persona.segundo_nombre || '',
          primerApellido: this.user.persona.primer_apellido || '',
          segundoApellido: this.user.persona.segundo_apellido || '',
          email: this.user.persona.email || '',
          telefono: this.user.persona.telefono || ''
        };
      }
    },

    async updateProfile() {
      this.loading = true;
      this.message = '';

      try {
        // Aquí iría la llamada a la API para actualizar el perfil
        // Por ahora solo simulamos
        await new Promise(resolve => setTimeout(resolve, 1000));

        this.message = 'Perfil actualizado exitosamente';
        this.messageType = 'success';
      } catch (error) {
        this.message = 'Error al actualizar el perfil';
        this.messageType = 'error';
      } finally {
        this.loading = false;
      }
    },

    async changePassword() {
      if (this.passwordData.new !== this.passwordData.confirm) {
        this.message = 'Las contraseñas no coinciden';
        this.messageType = 'error';
        return;
      }

      this.passwordLoading = true;
      this.message = '';

      try {
        // Aquí iría la llamada a la API para cambiar contraseña
        await new Promise(resolve => setTimeout(resolve, 1000));

        this.message = 'Contraseña cambiada exitosamente';
        this.messageType = 'success';
        this.passwordData = { current: '', new: '', confirm: '' };
      } catch (error) {
        this.message = 'Error al cambiar la contraseña';
        this.messageType = 'error';
      } finally {
        this.passwordLoading = false;
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleDateString();
    },

    logout() {
      authService.logout();
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.card {
  border: none;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow);
  background: white;
}

.card-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #dee2e6;
  font-weight: 600;
  color: #495057;
  border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0 !important;
}

.form-label {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
}

.form-control {
  border: 2px solid #e9ecef;
  border-radius: var(--border-radius);
  padding: 0.75rem;
  transition: var(--transition);
}

.form-control:focus {
  border-color: #28a745;
  box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
}

.btn-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  border: none;
  font-weight: 600;
}

.btn-warning {
  background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%);
  border: none;
  font-weight: 600;
}

.badge {
  font-size: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius-sm);
  font-weight: 600;
}

.alert {
  border: none;
  border-radius: var(--border-radius);
  font-weight: 500;
}

.spinner-border {
  width: 1rem;
  height: 1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .col-md-8, .col-md-4 {
    margin-bottom: 1.5rem;
  }

  .card-body {
    padding: 1.5rem;
  }

  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }
}
</style>