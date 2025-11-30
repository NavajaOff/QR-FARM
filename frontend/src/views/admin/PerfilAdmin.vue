<template>
  <div>
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">
            <i class="fas fa-user-edit me-2 text-primary"></i>Mi Perfil
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
                      <label class="form-label" for="admin-primer-nombre">Primer Nombre</label>
                      <input type="text" id="admin-primer-nombre" class="form-control" v-model="profile.primerNombre" required>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label" for="admin-segundo-nombre">Segundo Nombre</label>
                      <input type="text" id="admin-segundo-nombre" class="form-control" v-model="profile.segundoNombre">
                    </div>
                    <div class="col-md-6">
                      <label class="form-label" for="admin-primer-apellido">Primer Apellido</label>
                      <input type="text" id="admin-primer-apellido" class="form-control" v-model="profile.primerApellido" required>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label" for="admin-segundo-apellido">Segundo Apellido</label>
                      <input type="text" id="admin-segundo-apellido" class="form-control" v-model="profile.segundoApellido">
                    </div>
                    <div class="col-md-6">
                      <label class="form-label" for="admin-email">Email</label>
                      <input type="email" id="admin-email" class="form-control" v-model="profile.email" required readonly>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label" for="admin-telefono">Teléfono</label>
                      <input type="tel" id="admin-telefono" class="form-control" v-model="profile.telefono">
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
                  <span class="badge bg-primary ms-2">{{ userRole }}</span>
                </div>
                <div class="mb-3">
                  <strong>Estado:</strong>
                  <span class="badge bg-success ms-2">Activo</span>
                </div>
                <div class="mb-3">
                  <strong>Fecha de Registro:</strong>
                  <span class="text-muted">{{ formatDate(user?.persona?.fecha_creacion) }}</span>
                </div>
                <div class="mb-3">
                  <strong>Permisos:</strong>
                  <span class="text-muted">Acceso completo al sistema</span>
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
                    <label class="form-label" for="admin-password-current">Contraseña Actual</label>
                    <input type="password" id="admin-password-current" class="form-control" v-model="passwordData.current" required>
                  </div>
                  <div class="mb-3">
                    <label class="form-label" for="admin-password-new">Nueva Contraseña</label>
                    <input type="password" id="admin-password-new" class="form-control" v-model="passwordData.new" required>
                  </div>
                  <div class="mb-3">
                    <label class="form-label" for="admin-password-confirm">Confirmar Nueva Contraseña</label>
                    <input type="password" id="admin-password-confirm" class="form-control" v-model="passwordData.confirm" required>
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
export { default } from '../../assets/js/perfil-admin.js';
</script>

<style scoped>
@import '../../assets/css/perfil-admin.css';
</style>