<template>
  <div class="user-layout">
    <!-- Header -->
    <nav class="navbar navbar-dark bg-success">
      <div class="container-fluid">
        <div class="d-flex align-items-center w-100">
          <button
            class="btn btn-outline-light d-md-none me-2"
            type="button"
            data-bs-toggle="offcanvas"
            data-bs-target="#userSidebar"
            aria-controls="userSidebar"
          >
            <i class="fas fa-bars"></i>
          </button>
          <i class="fas fa-user fa-lg me-2"></i>
          <span class="fw-bold">{{ userName }}</span>
          <span class="badge bg-info ms-2">Usuario</span>
          <router-link class="navbar-brand mx-auto d-flex align-items-center" to="/user/dashboard">
            <span class="fw-bold fs-2">QR FARM</span>
            <i class="fas fa-cow ms-2 logo-icon"></i>
          </router-link>
          <button class="btn btn-outline-light" @click="logout">
            <i class="fas fa-sign-out-alt me-1"></i>Salir
          </button>
        </div>
      </div>
    </nav>

    <!-- Sidebar -->
    <div class="d-none d-md-block user-sidebar">
      <nav class="nav flex-column">
        <router-link class="nav-link" to="/user/dashboard">
          <i class="fas fa-home me-2"></i>Inicio
        </router-link>
        <router-link class="nav-link" to="/user/mi-ganado">
          <i class="fas fa-cow me-2"></i>Mi Ganado
        </router-link>
        <router-link class="nav-link" to="/user/vacunacion">
          <i class="fas fa-syringe me-2"></i>Vacunación
        </router-link>
        <router-link class="nav-link active" to="/user/perfil">
          <i class="fas fa-user-edit me-2"></i>Mi Perfil
        </router-link>
        <router-link class="nav-link" to="/user/inventario">
          <i class="fas fa-boxes me-2"></i>Inventario
        </router-link>
        <router-link class="nav-link" to="/user/escanear-qr">
          <i class="fas fa-qrcode me-2"></i>Escanear QR
        </router-link>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="user-main-content">
      <div class="container-fluid py-4">
        <div class="row">
          <div class="col-12">
            <h2 class="mb-4">Mi Perfil</h2>

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
.user-layout {
  min-height: 100vh;
}

.user-sidebar {
  position: fixed;
  top: 70px;
  left: 0;
  width: 250px;
  height: calc(100vh - 70px);
  background-color: #28a745;
  padding: 1rem;
  overflow-y: auto;
}

.user-sidebar .nav-link {
  color: rgba(255, 255, 255, 0.9);
  padding: 0.75rem 1rem;
  margin-bottom: 0.25rem;
  border-radius: 0.375rem;
  transition: all 0.3s ease;
}

.user-sidebar .nav-link:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.2);
}

.user-sidebar .nav-link.active {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.3);
  font-weight: bold;
}

.user-main-content {
  margin-left: 250px;
  padding-top: 2rem;
}

@media (max-width: 767px) {
  .user-sidebar {
    display: none !important;
  }

  .user-main-content {
    margin-left: 0 !important;
  }
}
</style>