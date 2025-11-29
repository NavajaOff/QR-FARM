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
export { default } from '../../assets/js/perfil-usuario.js';
</script>

<style scoped>
@import '../../assets/css/perfil-usuario.css';
</style>