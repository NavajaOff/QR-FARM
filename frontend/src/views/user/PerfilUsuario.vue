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
                  <div class="card-body" v-if="!mostrarResumen">
                    <form @submit.prevent="updateProfile">
                      <div class="row g-3">
                        <div class="col-md-6">
                          <input type="text" class="form-control" v-model="profile.nombreCompleto" placeholder="Nombre completo" required>
                        </div>
                        <div class="col-md-6">
                          <input type="email" class="form-control" v-model="profile.email" placeholder="Email" required>
                        </div>
                        <div class="col-md-6">
                          <input type="tel" class="form-control" v-model="profile.telefono" placeholder="Teléfono">
                        </div>
                        <div class="col-md-6">
                          <input type="text" class="form-control" :value="formatDate(profile.fechaCreacion)" readonly>
                        </div>
                      </div>

                      <div class="mt-4 d-flex gap-2">
                        <button type="submit" class="btn btn-primary" :disabled="loading">
                          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                          Guardar cambios
                        </button>
                        <button type="button" class="btn btn-outline-secondary" @click="cancelarEdicion" :disabled="loading">
                          Cancelar
                        </button>
                      </div>

                      <div v-if="message" class="alert mt-3" :class="messageType === 'success' ? 'alert-success' : 'alert-danger'">
                        {{ message }}
                      </div>
                    </form>
                  </div>
                  <div class="card-body" v-else>
                    <div class="row g-3">
                      <div class="col-md-6">
                        <strong>Nombre completo</strong>
                        <p class="mb-0">{{ profile.nombreCompleto || 'Sin información' }}</p>
                      </div>
                      <div class="col-md-6">
                        <strong>Email</strong>
                        <p class="mb-0">{{ profile.email || 'Sin información' }}</p>
                      </div>
                      <div class="col-md-6">
                        <strong>Teléfono</strong>
                        <p class="mb-0">{{ profile.telefono || 'Sin información' }}</p>
                      </div>
                      <div class="col-md-6">
                        <strong>Fecha de creación</strong>
                        <p class="mb-0">{{ formatDate(profile.fechaCreacion) }}</p>
                      </div>
                    </div>
                    <div class="mt-4">
                      <button class="btn btn-primary" @click="mostrarResumen = false">Actualizar perfil</button>
                    </div>
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
                      <strong>Fecha de creación:</strong>
                      <span class="text-muted">{{ formatDate(profile.fechaCreacion) }}</span>
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
import authService from '../../services/authService.js';
import { authAPI } from '../../services/api.js';

export default {
  name: 'PerfilUsuario',
  data() {
    return {
      userName: '',
      userRole: '',
      loading: false,
      message: '',
      messageType: '',
      mostrarResumen: true,
      profile: {
        nombreCompleto: '',
        email: '',
        telefono: '',
        fechaCreacion: ''
      }
    };
  },
  mounted() {
    if (!authService.isAuthenticated() || !authService.isUser()) {
      this.$router.push('/login');
      return;
    }

    this.userRole = authService.getRole();
    this.userName = authService.getUser()?.persona?.primer_nombre || 'Usuario';

    this.fetchProfile();
  },

  watch: {
    '$route'(to) {
      if (to.name === 'PerfilUsuario') {
        this.fetchProfile();
      }
    }
  },
  methods: {
    async fetchProfile() {
      try {
        const response = await authAPI.getProfile();
        if (response.data?.status === 'success') {
          const data = response.data.data;
          this.profile = {
            nombreCompleto: data.nombre_completo || '',
            email: data.email || '',
            telefono: data.telefono || '',
            fechaCreacion: data.fecha_creacion || ''
          };
          this.mostrarResumen = true; // Mostrar el resumen por defecto
        } else {
          throw new Error(response.data?.message || 'No se pudo cargar el perfil');
        }
      } catch (error) {
        this.message = error.message || 'Error al cargar el perfil';
        this.messageType = 'error';
      }
    },

    async updateProfile() {
      this.loading = true;
      this.message = '';

      try {
        const payload = {
          nombre_completo: this.profile.nombreCompleto,
          email: this.profile.email,
          telefono: this.profile.telefono
        };

        const response = await authAPI.updateProfile(payload);
        if (response.data?.status === 'success') {
          this.message = response.data?.message || 'Perfil actualizado exitosamente';
          this.messageType = 'success';
          await this.fetchProfile();
          this.mostrarResumen = true; // Volver a mostrar el resumen después de la actualización
        } else {
          throw new Error(response.data?.message || 'No se pudo actualizar el perfil');
        }
      } catch (error) {
        this.message = error.message || 'Error al actualizar el perfil';
        this.messageType = 'error';
      } finally {
        this.loading = false;
      }
    },

    cancelarEdicion() {
      this.mostrarResumen = true;
      this.fetchProfile(); // Recargar los datos para mostrar el resumen actualizado
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleDateString();
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