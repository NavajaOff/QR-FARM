<template>
  <div>
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
          <h2 class="mb-0">Gestión de Usuarios</h2>
          <button class="btn btn-primary" @click="openAddModal">
            <i class="fas fa-user-plus me-2"></i>Agregar usuario
          </button>
        </div>

        <!-- Tabla de usuarios -->
        <div class="card">
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-striped">
                <caption class="visually-hidden">Tabla de gestión de usuarios mostrando ID, nombre, email, rol, estado y acciones disponibles</caption>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Email</th>
                    <th>Rol</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="usuario in usuarios" :key="usuario.id">
                    <td>{{ usuario.id }}</td>
                    <td>{{ usuario.nombre }}</td>
                    <td>{{ usuario.email }}</td>
                    <td>
                      <span class="badge" :class="usuario.rol === 'admin' ? 'bg-danger' : 'bg-primary'">
                        {{ usuario.rol }}
                      </span>
                    </td>
                    <td>
                      <span class="badge" :class="usuario.estado === 'activo' ? 'bg-success' : 'bg-secondary'">
                        {{ usuario.estado }}
                      </span>
                    </td>
                    <td>
                      <button class="btn btn-sm btn-outline-primary me-2" @click="editUser(usuario)">
                        <i class="fas fa-edit"></i>
                      </button>
                      <button
                        v-if="isCurrentUserAdmin"
                        class="btn btn-sm"
                        :class="usuario.estado === 'activo' ? 'btn-outline-warning' : 'btn-outline-success'"
                        @click="toggleUserStatus(usuario)"
                        :title="usuario.estado === 'activo' ? 'Desactivar usuario' : 'Activar usuario'"
                      >
                        <i class="fas" :class="usuario.estado === 'activo' ? 'fa-ban' : 'fa-check'"></i>
                        {{ usuario.estado === 'activo' ? 'Desactivar' : 'Activar' }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de creación de usuario -->
    <div class="modal fade" :class="{ 'show d-block': showAddUserModal }" tabindex="-1" aria-modal="true" aria-labelledby="addUserModalLabel">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Agregar Usuario</h5>
            <button type="button" class="btn-close" @click="closeAddModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createUser">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="add_primer_nombre" class="form-label">Primer Nombre *</label>
                  <input
                    type="text"
                    class="form-control"
                    id="add_primer_nombre"
                    v-model="addForm.primer_nombre"
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="add_segundo_nombre" class="form-label">Segundo Nombre</label>
                  <input
                    type="text"
                    class="form-control"
                    id="add_segundo_nombre"
                    v-model="addForm.segundo_nombre"
                  >
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="add_primer_apellido" class="form-label">Primer Apellido *</label>
                  <input
                    type="text"
                    class="form-control"
                    id="add_primer_apellido"
                    v-model="addForm.primer_apellido"
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="add_segundo_apellido" class="form-label">Segundo Apellido</label>
                  <input
                    type="text"
                    class="form-control"
                    id="add_segundo_apellido"
                    v-model="addForm.segundo_apellido"
                  >
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="add_email" class="form-label">Email *</label>
                  <input
                    type="email"
                    class="form-control"
                    id="add_email"
                    v-model="addForm.email"
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="add_telefono" class="form-label">Teléfono</label>
                  <input
                    type="tel"
                    class="form-control"
                    id="add_telefono"
                    v-model="addForm.telefono"
                  >
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="add_password" class="form-label">Contraseña *</label>
                  <input
                    type="password"
                    class="form-control"
                    id="add_password"
                    v-model="addForm.password"
                    required
                  >
                  <div class="form-text">Mínimo 6 caracteres</div>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="add_confirm_password" class="form-label">Confirmar Contraseña *</label>
                  <input
                    type="password"
                    class="form-control"
                    id="add_confirm_password"
                    v-model="addForm.confirm_password"
                    required
                  >
                </div>
              </div>
              <!-- Campos adicionales para super admin -->
              <div v-if="isSuperAdmin" class="row">
                <div class="col-md-6 mb-3">
                  <label for="add_id_rol" class="form-label">Rol</label>
                  <select class="form-select" id="add_id_rol" v-model.number="addForm.id_rol">
                    <option :value="1">Administrador</option>
                    <option :value="2">Usuario</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="add_tenant_id" class="form-label">Tenant (Opcional)</label>
                  <select class="form-select" id="add_tenant_id" v-model.number="addForm.tenant_id">
                    <option :value="null">-- Sin asignar --</option>
                    <option
                      v-for="tenant in tenants"
                      :key="tenant.id"
                      :value="tenant.id"
                    >
                      {{ tenant.nombre }} ({{ tenant.codigo_tenant }})
                    </option>
                  </select>
                  <div class="form-text">Asignar tenant al usuario (solo super admin)</div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeAddModal">Cancelar</button>
            <button type="button" class="btn btn-primary" @click="createUser" :disabled="creatingUser">
              <span v-if="creatingUser" class="spinner-border spinner-border-sm me-2"></span>
              Guardar usuario
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAddUserModal" class="modal-backdrop fade show" @click="closeAddModal"></div>

    <!-- Modal de edición de usuario -->
    <div class="modal fade" :class="{ 'show d-block': showEditModal }" tabindex="-1" aria-modal="true" aria-labelledby="editUserModalLabel">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Editar Usuario</h5>
            <button type="button" class="btn-close" @click="closeEditModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateUser">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="primer_nombre" class="form-label">Primer Nombre</label>
                  <input
                    type="text"
                    class="form-control"
                    id="primer_nombre"
                    v-model="editForm.primer_nombre"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="segundo_nombre" class="form-label">Segundo Nombre</label>
                  <input
                    type="text"
                    class="form-control"
                    id="segundo_nombre"
                    v-model="editForm.segundo_nombre"
                  >
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="primer_apellido" class="form-label">Primer Apellido</label>
                  <input
                    type="text"
                    class="form-control"
                    id="primer_apellido"
                    v-model="editForm.primer_apellido"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="segundo_apellido" class="form-label">Segundo Apellido</label>
                  <input
                    type="text"
                    class="form-control"
                    id="segundo_apellido"
                    v-model="editForm.segundo_apellido"
                  >
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="email" class="form-label">Email</label>
                  <input
                    type="email"
                    class="form-control"
                    id="email"
                    v-model="editForm.email"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="telefono" class="form-label">Teléfono</label>
                  <input
                    type="tel"
                    class="form-control"
                    id="telefono"
                    v-model="editForm.telefono"
                  >
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="password" class="form-label">Nueva Contraseña (opcional)</label>
                  <input
                    type="password"
                    class="form-control"
                    id="password"
                    v-model="editForm.password"
                    placeholder="Dejar vacío para mantener la actual"
                  >
                  <div class="form-text">Mínimo 6 caracteres</div>
                </div>
              </div>
              <!-- Campo de rol solo visible para administradores -->
              <div v-if="isCurrentUserAdmin" class="row">
                <div class="col-md-6 mb-3">
                  <label for="id_rol" class="form-label">Rol</label>
                  <select class="form-select" id="id_rol" v-model.number="editForm.id_rol">
                    <option :value="1">Administrador</option>
                    <option :value="2">Usuario</option>
                  </select>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeEditModal">Cancelar</button>
            <button type="button" class="btn btn-primary" @click="updateUser" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Guardar Cambios
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Backdrop del modal -->
    <div v-if="showEditModal" class="modal-backdrop fade show" @click="closeEditModal"></div>
  </div>
</template>

<script>
export { default } from '../../assets/js/gestionar-usuarios.js';
</script>

<style scoped>
/* Estilos específicos para GestionarUsuarios admin pendientes de definir */
</style>